# Color: verified sources and method

Tag: `[standard]`. Verified against primary sources on **2026-11-01**. Re-verify before changing a hard gate.

## Verified facts

| Source | Fact | URL |
|---|---|---|
| WCAG 2.2 (W3C Recommendation, page status "12 December 2024") | SC 1.4.3 (AA): text contrast at least 4.5:1; large-scale text (at least 18pt, or 14pt bold) at least 3:1. | https://www.w3.org/TR/WCAG22/ |
| WCAG 2.2 | SC 1.4.6 (AAA): 7:1; large-scale text 4.5:1. | https://www.w3.org/TR/WCAG22/ |
| WCAG 2.2 | SC 1.4.11 (AA): non-text UI components and graphical objects at least 3:1 against adjacent colors. | https://www.w3.org/TR/WCAG22/ |
| WCAG 2.2 | SC 1.4.1 (A): color is not the only visual means of conveying information. | https://www.w3.org/TR/WCAG22/ |
| Oklab (Bjorn Ottosson, 23 Dec 2020) | Perceptual color space with lightness, chroma, hue. Lightness error 0.20 (HSV: 11.59); hue error 0.49, better than CIELAB/CIELUV (JzAzBz is better at 0.43). The post compares against HSV, not HSL. Caveat from the author: test data was generated with CAM16, not human experiments. | https://bottosson.github.io/posts/oklab/ |
| CSS Color 4 | `oklab()` and `oklch()` are defined. The spec document is a Candidate Recommendation Draft (29 Oct 2026), not a final Recommendation. | https://www.w3.org/TR/css-color-4/ |
| MDN `oklch()` | Baseline "widely available" since May 2023. L 0-1 (0%-100%); C minimum 0, in practice at most about 0.5 (100% = 0.4); H 0-360. Red is near 29deg; 0deg is magenta-like. | https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch |
| Material Color Utilities (Google), `hct.ts` comment | "A difference of 40 in HCT tone guarantees a contrast ratio >= 3.0, and a difference of 50 guarantees a contrast ratio >= 4.5." Sufficient condition, not necessary. Source is a code comment; the m3.material.io page was not readable (client-rendered). | https://github.com/material-foundation/material-color-utilities |
| Radix Colors | 12-step scale. 1 app background; 2 subtle component background; 3 component background; 4 hover; 5 pressed/selected; 6 subtle border; 7 interactive border; 8 strong border and focus ring; 9 solid (highest chroma); 10 solid hover; 11 low-contrast text; 12 high-contrast text. Steps 11 and 12 are guaranteed Lc 60 and Lc 90 (APCA) on a step 2 background of the same scale. The page does not document pairing grays with accents. | https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale |
| APCA ("APCA in a Nutshell") | Candidate method for WCAG 3, still a draft. Lc 90 preferred / 75 minimum for body text; Lc 60 content text; Lc 45 headlines; non-text: Lc 45 fine icons, Lc 30 solid icons, Lc 15 absolute minimum for dividers. The repository shows a "Beta Non-Com" license badge: review terms before embedding code. | https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html , https://github.com/Myndex/SAPC-APCA |
| Adobe Leonardo | Generates scales from target contrast ratios; exports CSS custom properties and design tokens. The README does not name its color spaces or mention APCA or OKLCH: do not claim support. | https://leonardocolor.io/ , https://github.com/adobe/leonardo |
| WCAG 2.2 glossary (verified 2026-11-01) | Relative luminance `L = 0.2126*R + 0.7152*G + 0.0722*B`, with `R = Rs/12.92` if `Rs <= 0.04045`, else `((Rs+0.055)/1.055)^2.4`, `Rs = R8bit/255` (same for G, B). The page notes the threshold was 0.03928 before May 2021. Contrast ratio `(L1 + 0.05) / (L2 + 0.05)`, L1 the lighter; range 1:1 to 21:1. Implemented in `skills/jackiense-qa/scripts/contrast.py`. | https://www.w3.org/TR/WCAG22/ |

## Unverified (do not use as hard gates)

- WCAG 2.2 SC 2.3.3 (animation from interactions), 2.4.7 (focus visible) and 2.5.8 (target size minimum): cited from memory only.
- Core Web Vitals "good" thresholds (LCP 2.5 s, CLS 0.1): cited from memory only.

- Books and articles: Albers, *Interaction of Color*; Itten, *The Art of Color* (criticised as not perceptual); Wathan and Schoger, *Refactoring UI*; Ware, *Information Visualization*; ColorBrewer; Wong 2011 (color-blind-safe palettes); NN/g; Apple HIG.
- The "60-30-10" rule is a popular interior-design heuristic, not an empirical standard. Do not treat it as a rule.

## Method (draft, to be implemented in scripts)

1. **Intent:** the archetype fixes mood and the accent hue.
2. **Scale:** 12 steps in OKLCH, a fixed lightness curve per theme, chroma reduced at the extremes.
3. **Neutrals:** same hue as the accent at very low chroma (`[corpus]` observation, see L2).
4. **Roles:** background, surface, line, text, muted text, accent, on-accent, plus success/warning/danger, each bound to one step (Radix roles above).
5. **Contrast:** pick pairs from steps far enough apart, then **always verify** with WCAG 2.2 ratios in `contrast.py`. OKLCH lightness difference does not guarantee the ratio the way HCT tone does.
6. **Dark mode:** derived with its own curve, not inverted.
7. **Color vision deficiency:** simulate protanopia, deuteranopia and tritanopia for status colors; never rely on color alone (SC 1.4.1).
8. **Priors:** corpus defaults (see L2) as adjustable starting values.
