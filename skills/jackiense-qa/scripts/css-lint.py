#!/usr/bin/env python3
"""Static lint for a generated single-file site (jackiense-qa).

  python -I css-lint.py FILE.html [--json]

Reads inline <style>, local <link rel=stylesheet>, style="" attributes and <script> text.
Does not parse native CSS nesting. Exit code 1 if any blocker is found.
Finding severities: blocker (fails the gate), warn (deduct points), info.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contrast import parse_color, rgb_to_oklch  # noqa: E402

GENERIC = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif", "ui-serif",
           "ui-monospace", "ui-rounded", "emoji", "math", "fangsong", "inherit", "initial", "unset", "-apple-system",
           "blinkmacsystemfont", "segoe ui", "roboto", "helvetica neue", "arial", "helvetica", "georgia"}
MONO = re.compile(r"mono|code|courier|consolas|menlo", re.I)
COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\([^)]*\)")
VAR = re.compile(r"var\((?:[^()]|\([^()]*\))*\)")
STATUS = re.compile(r"success|warn|danger|error|info|status|positive|negative", re.I)


def strip_comments(s):
    return re.sub(r"/\*.*?\*/", "", s, flags=re.S)


def split_decls(body):
    out, depth, cur = [], 0, ""
    for ch in body:
        depth += (ch == "(") - (ch == ")")
        if ch == ";" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [tuple(x.strip() for x in d.split(":", 1)) for d in out if ":" in d]


def parse(css):
    """Yield (selector, prop, value). Recurses into @media/@supports/@keyframes."""
    pos, n = 0, len(css)
    while pos < n:
        i = css.find("{", pos)
        if i < 0:
            return
        sel, depth, j = css[pos:i].strip(), 0, i
        while j < n:
            depth += (css[j] == "{") - (css[j] == "}")
            if depth == 0:
                break
            j += 1
        body = css[i + 1:j]
        if sel.startswith("@") and not sel.startswith("@font-face"):
            yield from parse(body)
        else:
            for prop, val in split_decls(body):
                yield sel, prop.lower(), val
        pos = j + 1


def is_neutral_overlay(c):
    try:
        r, g, b, a = parse_color(c)
    except ValueError:
        return False
    return a < 1 and ((r, g, b) == (0, 0, 0) or (round(r), round(g), round(b)) == (255, 255, 255))


def main(path, as_json):
    html = open(path, encoding="utf-8", errors="replace").read()
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I))
    for href in re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)[\"']", html, re.I):
        p = os.path.join(os.path.dirname(os.path.abspath(path)), href)
        if not href.startswith(("http", "//")) and os.path.exists(p):
            css += "\n" + open(p, encoding="utf-8", errors="replace").read()
    js = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", html, re.S | re.I))
    css = strip_comments(css)
    findings = []

    def add(id_, sev, msg, evidence=None):
        findings.append({"id": id_, "severity": sev, "message": msg, "evidence": evidence or []})

    decls = list(parse(css))
    for style in re.findall(r"style=\"([^\"]*)\"", html):
        decls += [("inline", p.lower(), v) for p, v in split_decls(style)]

    tokens, literals, tolerated, families = {}, [], 0, set()
    for sel, prop, val in decls:
        in_scope = ":root" in sel or "[data-theme" in sel
        if in_scope and prop.startswith("--"):
            tokens[prop] = val
        if prop.startswith("--font") or prop == "font-family":
            for fam in val.split(","):
                fam = fam.strip().strip("\"'")
                if fam and not fam.startswith("var(") and fam.lower() not in GENERIC and not fam.startswith("--"):
                    families.add(fam)
        if in_scope or "url(" in val:
            continue
        for c in COLOR.findall(VAR.sub("", val)):
            if is_neutral_overlay(c):
                tolerated += 1
            else:
                literals.append(f"{sel} {{ {prop}: {c} }}")

    for href in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"')\s]+)", html):
        for fam in re.findall(r"family=([^:&;]+)", href):
            families.add(fam.replace("+", " "))

    # fonts: at most 2 non-mono families (+ mono)
    prose = sorted(f for f in families if not MONO.search(f))
    if len(prose) > 2:
        add("fonts", "blocker", f"{len(prose)} non-mono font families (max 2 + mono)", prose)
    # colors outside :root
    if literals:
        add("tokens", "blocker" if len(literals) > 5 else "warn",
            f"{len(literals)} color literals outside :root (+{tolerated} tolerated black/white alpha overlays)",
            literals[:10])
    # accent count: chromatic hue clusters among :root tokens, status colors excluded
    hues = []
    for name, val in tokens.items():
        m = COLOR.findall(VAR.sub("", val))
        if len(m) == 1 and not STATUS.search(name) and "gradient" not in val:
            try:
                r, g, b, _ = parse_color(m[0])
            except ValueError:
                continue
            L, C, H = rgb_to_oklch(r, g, b)
            if C > 0.06 and 0.1 < L < 0.97:
                hues.append((H, name))
    hues.sort()
    clusters = []
    for H, name in hues:
        if clusters and H - clusters[-1][-1][0] <= 30:
            clusters[-1].append((H, name))
        else:
            clusters.append([(H, name)])
    if len(clusters) > 1 and (clusters[0][0][0] + 360 - clusters[-1][-1][0]) <= 30:
        clusters[0] = clusters.pop() + clusters[0]  # hue wraps around 0/360
    if len(clusters) > 1:
        add("accent", "blocker", f"{len(clusters)} chromatic hue groups in :root tokens (max 1 accent)",
            [", ".join(f"{n}@{round(h)}deg" for h, n in c) for c in clusters])
    # reduced motion
    has_motion = bool(re.search(r"@keyframes|animation\s*:|transition\s*:|requestAnimationFrame|gsap|WebGL", css + js))
    if has_motion and "prefers-reduced-motion" not in css + js:
        add("reduced-motion", "blocker", "motion present but no prefers-reduced-motion handling")
    # focus
    if re.search(r"outline\s*:\s*(none|0)\b", css) and ":focus-visible" not in css:
        add("focus", "blocker", "outline removed and no :focus-visible replacement")
    # structure and hygiene
    if not re.search(r"<html[^>]*\blang=", html, re.I):
        add("lang", "warn", "<html> has no lang attribute")
    if not re.search(r"<meta[^>]+name=[\"']viewport", html, re.I):
        add("viewport", "blocker", "missing viewport meta")
    missing_alt = re.findall(r"<img(?![^>]*\balt=)[^>]*>", html, re.I)
    if missing_alt:
        add("alt", "warn", f"{len(missing_alt)} <img> without alt", missing_alt[:5])
    h1s = len(re.findall(r"<h1\b", html, re.I))
    if h1s != 1:
        add("h1", "warn", f"expected exactly one <h1>, found {h1s}")
    if any(sel in ("*", "body", "html") and p == "cursor" and v.startswith("none") for sel, p, v in decls):
        add("cursor", "warn", "native cursor hidden globally")
    if any(sel in ("*", "body", "html") and p == "user-select" and v == "none" for sel, p, v in decls):
        add("select", "warn", "text selection disabled globally")
    if re.search(r"transition\s*:\s*all\b", css):
        add("transition-all", "warn", "transition: all animates layout properties")
    if re.search(r"lorem ipsum|\bTBD\b|\bTODO\b", html, re.I):
        add("placeholder", "warn", "placeholder copy found (lorem ipsum / TBD / TODO)")

    blockers = [f for f in findings if f["severity"] == "blocker"]
    result = {"file": path, "families": sorted(families), "findings": findings, "blockers": len(blockers)}
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity'].upper()}] {f['id']}: {f['message']}")
            for e in f["evidence"]:
                print(f"    - {e}")
        print(f"\n{len(blockers)} blocker(s), {len(findings) - len(blockers)} other finding(s)")
    return 1 if blockers else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit("usage: css-lint.py FILE.html [--json]")
    sys.exit(main(args[0], "--json" in sys.argv))
