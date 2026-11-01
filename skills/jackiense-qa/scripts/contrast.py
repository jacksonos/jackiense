#!/usr/bin/env python3
"""WCAG 2.2 contrast checker (jackiense-qa).

  python -I contrast.py FG BG [--size PX] [--bold]
  python -I contrast.py --selftest

Colors: #rgb #rrggbb #rrggbbaa rgb() rgba() hsl() hsla() oklch(), white, black, transparent.
Alpha on FG is composited over BG. Relative luminance uses the WCAG 2.2 definition
(sRGB threshold 0.04045, exponent 2.4). Large text = >=24px, or bold and >=18.66px.
"""
import math
import re
import sys

NAMED = {"white": (255, 255, 255, 1.0), "black": (0, 0, 0, 1.0), "transparent": (0, 0, 0, 0.0)}


def _alpha(tok):
    return float(tok[:-1]) / 100 if tok.endswith("%") else float(tok)


def oklch_to_srgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )
    out = []
    for c in lin:
        c = max(0.0, min(1.0, c))
        out.append(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))
    return tuple(out)


def rgb_to_oklch(r, g, b):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = lin(r), lin(g), lin(b)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def parse_color(s):
    """Return (r, g, b, a) with r,g,b in 0-255 and a in 0-1."""
    s = s.strip().lower()
    if s in NAMED:
        return NAMED[s]
    m = re.fullmatch(r"#([0-9a-f]{3,8})", s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            raise ValueError(f"bad hex: {s}")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        return (r, g, b, int(h[6:8], 16) / 255 if len(h) == 8 else 1.0)
    m = re.fullmatch(r"(rgba?|hsla?|oklch)\((.*)\)", s)
    if not m:
        raise ValueError(f"unsupported color: {s}")
    fn, args = m.groups()
    parts = [p for p in re.split(r"[\s,/]+", args.strip()) if p]
    alpha = _alpha(parts[3]) if len(parts) == 4 else 1.0
    p = parts[:3]
    if fn.startswith("rgb"):
        ch = [float(x[:-1]) * 2.55 if x.endswith("%") else float(x) for x in p]
        return (*[max(0.0, min(255.0, c)) for c in ch], alpha)
    if fn.startswith("hsl"):
        h = float(p[0].replace("deg", "")) % 360
        sat, lig = float(p[1].rstrip("%")) / 100, float(p[2].rstrip("%")) / 100
        c = (1 - abs(2 * lig - 1)) * sat
        x = c * (1 - abs((h / 60) % 2 - 1))
        r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
        mm = lig - c / 2
        return ((r + mm) * 255, (g + mm) * 255, (b + mm) * 255, alpha)
    L = float(p[0][:-1]) / 100 if p[0].endswith("%") else float(p[0])
    C = float(p[1][:-1]) / 100 * 0.4 if p[1].endswith("%") else float(p[1])
    return (*oklch_to_srgb(L, C, float(p[2].replace("deg", ""))), alpha)


def luminance(rgb):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(v) for v in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def over(fg, bg):
    """Composite fg (r,g,b,a) over an opaque bg (r,g,b[,a])."""
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))


def ratio(fg, bg):
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def is_large(size_px, bold):
    return size_px >= 24 or (bold and size_px >= 18.66)


def check(fg, bg, size_px=16, bold=False):
    f, b = parse_color(fg), parse_color(bg)
    r = ratio(over(f, b), b[:3])
    need = 3.0 if is_large(size_px, bold) else 4.5
    return {"ratio": round(r, 2), "needed": need, "aa": r >= need, "aaa": r >= (4.5 if need == 3.0 else 7.0)}


def selftest():
    assert abs(ratio((0, 0, 0), (255, 255, 255)) - 21.0) < 0.01
    assert check("#767676", "#fff")["aa"] and not check("#777777", "#fff")["aa"]
    assert check("#777777", "#fff", 24)["aa"], "large text needs only 3:1"
    assert parse_color("hsl(0 0% 100%)")[:3] == (255.0, 255.0, 255.0)
    assert all(abs(v - 255) < 1.5 for v in parse_color("oklch(1 0 0)")[:3])
    r, g, b, _ = parse_color("oklch(45.2% 0.313 264.05)")  # sRGB blue per the CSS Color 4 example values
    assert r < 12 and g < 12 and b > 245, (r, g, b)
    L, C, H = rgb_to_oklch(255, 0, 0)
    assert 0.6 < L < 0.65 and C > 0.25 and 25 < H < 33, (L, C, H)
    print("contrast.py selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a == ["--selftest"]:
        selftest()
    else:
        size = float(a[a.index("--size") + 1]) if "--size" in a else 16
        print(check(a[0], a[1], size, "--bold" in a))
