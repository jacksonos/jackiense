# Corpus: measured patterns from 10 site specs

Tag: `[corpus]`. Observations, not standards. Sample is small (10) and 9 of the 10 come from the same
generator, so treat counters as indicative. Rule = seen in 3 or more; below that = style.

## The sample

7 of 10 are WebGL/3D/video-led, 3 are editorial.

| Id | Type | Signature moment | Fonts | Accent / palette character |
|---|---|---|---|---|
| kimi | Racing driver, WebGL helmet | 3D hero + sticky section stack | (see source) | Racing palette |
| gravity | Studio, WebGL spheres | ~96 spheres driven by scroll progress | Raleway + mono | Cobalt on white-slate, morphs to lime then pink |
| ascend | SaaS, WebGL planet | Planet zoom/swing with bloom pass | Inter | Mint on near-black navy |
| vane | Founder portfolio | Giant name behind a cut-out portrait | Anton + Onest | Red on near-black |
| baseline | Tennis club | Loader curtain, parallax hero, ghost words | Onest | Navy / royal blue on white |
| loopstack | Single-screen hero | Looping video + giant wordmark + custom cursor | Playfair + Outfit + General Sans | Neon green on black |
| flowstate | Waitlist hero | Fluid simulation with auto-driven cursor | Onest | Cyan-to-magenta ink on near-black |
| laocoon | Scroll-driven 3D | Camera orbit around a statue, shader background | Italiana + Outfit | Bronze to sapphire |
| soda | Product hero | 3D can tilting to cursor, flavor-switch choreography | Galada + Inter + Manrope | Teal / blue with pink accent |
| kai | Artist portfolio | Monochrome editorial, dashed hairlines | Playfair + Satoshi | No accent (strict monochrome) |

## Prompt structure of the sources

Title, then "what it is" (concept plus motion arc), shell and libraries with pinned versions, layout per
section with verbatim copy, motion, loader, **fixed parameters** (numbers repeated as a checksum), assets.
Literal code is used only for what prose cannot carry (shaders, physics, fluid engine); everything else is
prose plus numbers. For large effects, separate the **engine** (literal) from a small **knob table**
(the values that define the look).

## Color

- One accent plus tinted neutrals (9 of 10; the tenth is strict monochrome). Dark grounds are near-black
  with a slight hue (`#08080a`, `#04060f`, `#04050c`, `#191917`), not pure `#000`. Light ink is warm or cool
  off-white (`#f3f1ea`, `#f3f6ff`, `#eef0f6`, `#fff6ed`).
- Muted text sits around 55-60% of the ink (about `#807f78` to `#b9becf` on dark; `rgba(25,25,23,.6)` on light).
- Hairlines: white or ink at 10-22% alpha; 1px.
- Glass surfaces: white at 5-25% (or `rgba(12,18,38,.55)` dark), 1px border at 10-20% white, blur 10-20px.
- Text over a live canvas needs a scrim: radial `rgba(base, .68)` center to `.12` edge, or top-weighted
  `.82` to `.28`, or a wide soft text-shadow (`0 2px 40-50px rgba(0,0,0,.55)`).

## Typography

- Display plus sans; mono only in 1 of 10. Onest is the generator's default sans (3 of 10).
- Display tracking -0.01 to -0.03em; display line-height 0.78-1.12; body line-height 1.45-1.65.
- Eyebrow/label: 11-13px, uppercase, tracking 0.16-0.28em.
- Oversized wordmark as a footer or closing device (3 of 10): 18vw, 21.9vw, 8.2vw ghost words.
- Measured scale from one source (px): 13, 17, 22, 28 (ratio about 1.28, reading range), then 52, 80, 120,
  208, 448 (ratios 1.5-2.15, poster range). Two regimes: reading scale and poster scale.

## Spacing and layout

- 4/8px base. Gutter 40-48px; section padding 96-144px; container up to 120rem.
- Radii: pill 9999px; cards 18-32px.
- Adaptive rem grid, identical in 4 of 10: root font-size by viewport width, `max-width` 1920 / 1440 / 1024 / 640 →
  `0.833333vw / 1.111111vw / 1.5625vw / 4.444444vw`; plus a JS scale-up above 1920.
- Editorial 12-column grid with asymmetric zig-zag (items span 7 columns, start at col 1 or 6, odd items offset
  down 6rem); alternating white / light-grey / dark sections; dashed 1px hairlines as a signature.
- z-index ladder: canvas 0, content 10, header 30, modal 60-90, loader 100-200, custom cursor 9998-9999.

## Motion

- Dominant easing `cubic-bezier(.16,1,.3,1)` (easeOutExpo). Others seen: `(.22,.7,.2,1)`, `(.05,.9,.1,1)`,
  `(.25,1,.5,1)`, `(.2,0,0,1)`, easeOutQuart `(.165,.84,.44,1)`, easeOutCubic; easeInOutCubic for loaders/curtains.
- Reveal: once, via IntersectionObserver; rise 24-60px plus opacity (plus blur 8-20px in 3 of 10); 0.5-1.5s.
- Stagger: siblings 80-140ms; letters 35-90ms; title words 85-140ms; body words 10-30ms; lines 90-140ms.
- Text mask: `overflow:hidden` wrapper, inner `translateY(105-115%)`, bottom padding 0.12-0.15em for descenders.
- Spring-to-time mapping (from react-spring configs): entrances 520-720ms; hover color about 340ms; panels about 600ms;
  CTA arrow about 400ms.
- Entrance with no loader: nav 150 → badge 320 → title 480 → subtitle 1150 → form 1450 → footer 1650 ms (top to bottom, under 1.7s).
  With a loader: hero starts 2500-3400ms.
- Three motion layers in every hero: **ambient** (always on), **pointer** (lerp 0.05-0.2), **scroll or intro**
  (lerp 0.025-0.09). In 3 of 10 (gravity, ascend, laocoon) a single scroll scalar (0-1 or scrollY/vh) drives
  camera, shader, section state and palette.
- Parallax depth planes with opposite signs (+60 / -30 / -15 px); hero plate 0 → 12%; plates scrub +/-2.5rem.
- Hide a state change at the peak of a motion (spin plus blur, swap texture mid-spin).
- Smooth scroll: Lenis in 6 of 10; custom lerp (0.025-0.09) in 2; none in 2.
- Hover: lift 2-12px, scale 1.03-1.06, arrow nudge 5-8px. Header with `mix-blend-mode: difference` in 1.

## 3D / WebGL

- Lighting: studio-light (hemi 1.6, key 1.4, exposure 1.15) vs chiaroscuro (ambient .1, key 18, rim 10, fill .8, exposure 2.2).
- Perpetual ambient motion keeps the scene alive: orbiting virtual cursor, floating sparks, spinning planet.

## Weaknesses of the sample (must be fixed by the skill, not inherited)

| Issue | Evidence |
|---|---|
| Reduced-motion handled in only 5 of 10 | Present: kimi, ascend, vane, baseline, kai. Missing: gravity, loopstack, flowstate, laocoon, soda. |
| Hover disabled at <=768px in only 3 of 10 | vane, baseline, kai. |
| Desktop-only de facto | laocoon, soda, loopstack. Soda applies a grid to a flex container (no effect). |
| Hostile accessibility | laocoon hides the native cursor everywhere and disables text selection. |
| Content bug carried by a spec | kai: title says "Four rules", list has 3. Never copy content bugs. |

## Gaps (not covered by this corpus)

Real mobile layouts for WebGL sites, numeric accessibility, UX architecture (IA, flows, heuristics), product UI
(dashboards, forms, states), copywriting, performance budgets and no-WebGL fallbacks. These come from `L1`
and from the skills themselves.
