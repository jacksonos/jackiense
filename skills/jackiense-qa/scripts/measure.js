async () => {
  // jackiense-qa: in-page measurements. Pass this whole function to evaluate_script, once per viewport.
  // Returns plain JSON. "indeterminate" means the browser cannot measure it reliably: check a screenshot.
  const W = document.documentElement.clientWidth, H = window.innerHeight;
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgba = (c) => { cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], d[3] / 255]; };
  const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const lum = (c) => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (a, b) => { const [hi, lo] = lum(a) > lum(b) ? [lum(a), lum(b)] : [lum(b), lum(a)]; return (hi + 0.05) / (lo + 0.05); };
  const over = (f, b) => [0, 1, 2].map(i => f[i] * f[3] + b[i] * (1 - f[3]));
  const cs = (e) => getComputedStyle(e);
  const visible = (e) => { const r = e.getBoundingClientRect(), s = cs(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const name = (e) => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
    (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const clipsX = (e) => { for (let p = e.parentElement; p; p = p.parentElement) {
    const o = cs(p).overflowX; if (o !== 'visible') return true; } return false; };

  // 1. horizontal overflow
  const overflowPx = document.documentElement.scrollWidth - W;
  const offenders = [];
  if (overflowPx > 1) for (const e of document.body.querySelectorAll('*')) {
    const r = e.getBoundingClientRect();
    if (r.width && r.right > W + 1 && cs(e).position !== 'fixed' && !clipsX(e)) offenders.push({ el: name(e), right: Math.round(r.right) });
    if (offenders.length >= 8) break;
  }

  // 2. text contrast
  const media = [...document.querySelectorAll('canvas,video')].filter(visible);
  const seen = new Set(), failing = [], stats = { measured: 0, indeterminate: 0 }, sizes = {}, fams = {};
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = tw.nextNode());) {
    const t = n.textContent.trim(); const e = n.parentElement;
    if (!t || !e || seen.has(e) || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(e.tagName) || !visible(e)) continue;
    seen.add(e);
    const s = cs(e), px = parseFloat(s.fontSize), bold = parseInt(s.fontWeight) >= 700;
    sizes[Math.round(px * 2) / 2] = (sizes[Math.round(px * 2) / 2] || 0) + t.length;
    const fam = s.fontFamily.split(',')[0].trim().replace(/["']/g, ''); fams[fam] = (fams[fam] || 0) + t.length;
    let op = 1, bg = [255, 255, 255, 1], indeterminate = false; const chain = [];
    for (let p = e; p; p = p.parentElement) chain.unshift(p);
    for (const p of chain) { const ps = cs(p); op *= parseFloat(ps.opacity);
      if (ps.backgroundImage !== 'none') indeterminate = true;
      const b = rgba(ps.backgroundColor); if (b[3] > 0) bg = [...over(b, bg), 1]; }
    const r = e.getBoundingClientRect();
    if (media.some(m => !m.contains(e) && m.getBoundingClientRect().right > r.left && m.getBoundingClientRect().left < r.right &&
      m.getBoundingClientRect().bottom > r.top && m.getBoundingClientRect().top < r.bottom)) indeterminate = true;
    if (indeterminate) { stats.indeterminate++; continue; }
    const fg = rgba(s.color); fg[3] *= op; const c = ratio(over(fg, bg), bg);
    const need = (px >= 24 || (bold && px >= 18.66)) ? 3 : 4.5; stats.measured++;
    if (c < need) failing.push({ el: name(e), text: t.slice(0, 40), ratio: +c.toFixed(2), needed: need, px, fg: s.color, bg: `rgb(${bg.slice(0, 3).map(Math.round)})` });
  }
  failing.sort((a, b) => a.ratio - b.ratio);

  // 3. touch targets (interactive elements, inline links inside prose are exempt)
  const sel = 'a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=link],[tabindex]:not([tabindex="-1"])';
  const ctl = [...document.querySelectorAll(sel)].filter(visible);
  const PROSE = ['P', 'LI', 'SPAN', 'TD', 'DD', 'BLOCKQUOTE', 'FIGCAPTION', 'LABEL'];
  const inProse = (e) => e.tagName === 'A' && cs(e).display === 'inline' && PROSE.includes(e.parentElement.tagName) &&
    e.parentElement.textContent.trim().length > e.textContent.trim().length + 10;
  const small = ctl.filter(e => !inProse(e)).map(e => { const r = e.getBoundingClientRect(); return { el: name(e), w: Math.round(r.width), h: Math.round(r.height) }; })
    .filter(x => x.w < 44 || x.h < 44);

  // 4. focus indicator
  const props = ['outlineStyle', 'outlineWidth', 'boxShadow', 'borderColor', 'backgroundColor', 'color', 'textDecorationLine'];
  const noFocus = [];
  for (const e of ctl.slice(0, 40)) {
    const before = props.map(p => cs(e)[p]).join('|'); e.focus({ focusVisible: true });
    const after = props.map(p => cs(e)[p]).join('|'); const ok = before !== after || e.matches(':focus-visible') && cs(e).outlineStyle !== 'none';
    if (!ok) noFocus.push(name(e)); e.blur();
  }

  // 5. animations, meta, perf
  const anims = document.getAnimations();
  const infinite = anims.filter(a => a.effect && a.effect.getComputedTiming().iterations === Infinity).length;
  const perf = await new Promise(res => { let lcp = null, cls = 0;
    try { new PerformanceObserver(l => { for (const x of l.getEntries()) lcp = x.startTime; }).observe({ type: 'largest-contentful-paint', buffered: true });
      new PerformanceObserver(l => { for (const x of l.getEntries()) if (!x.hadRecentInput) cls += x.value; }).observe({ type: 'layout-shift', buffered: true }); } catch (e) {}
    setTimeout(() => res({ lcpMs: lcp && Math.round(lcp), cls: +cls.toFixed(3) }), 300); });
  return {
    viewport: { w: W, h: H, dpr: devicePixelRatio },
    overflow: { px: overflowPx, offenders },
    contrast: { ...stats, failingCount: failing.length, failing: failing.slice(0, 15) },
    targets: { total: ctl.length, smallCount: small.length, small: small.slice(0, 15) },
    focus: { checked: Math.min(ctl.length, 40), withoutIndicator: noFocus },
    fonts: { families: fams, loaded: [...document.fonts].map(f => f.family + ':' + f.status) },
    typeScale: Object.entries(sizes).map(([px, chars]) => ({ px: +px, chars })).sort((a, b) => a.px - b.px),
    animations: { running: anims.length, infinite },
    meta: { lang: document.documentElement.lang, title: document.title, h1: document.querySelectorAll('h1').length,
      imgsNoAlt: document.querySelectorAll('img:not([alt])').length, viewportMeta: !!document.querySelector('meta[name=viewport]') },
    perf,
  };
}
