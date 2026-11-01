# Decisions

Date of first set: 2026-11-01.

| # | Decision | Why |
|---|---|---|
| 1 | Plugin name `jackiense`; repo `jacksonos/jackiense`; the repo is its own marketplace. | Same layout as other self-marketplace plugins; versioned and publishable. |
| 2 | Default output: a single self-contained `index.html` (vanilla JS). Other stacks (React/Next) come later as adapters over the same stack-agnostic spec. | The spec (tokens, copy, sections, named motion configs) is portable; components, routing and state are not. Ship the reference adapter first. |
| 3 | WebGL is off by default. The "signature moment" has three tiers: 0 = CSS only, 1 = light JS, 2 = WebGL. Tier 2 requires a justified brief, a performance budget and a fallback. | Several sources in the corpus are desktop-only or lack fallbacks. |
| 4 | Generated copy defaults to English. Conversation with the user is in Spanish. | User preference. |
| 5 | Shared knowledge lives in `references/` at the plugin root and is read via `${CLAUDE_SKILL_DIR}/../../references/`. | Verified working pattern in an existing local plugin. |
| 6 | Hard quality gate = WCAG 2.2 ratios. APCA is advisory only. Palettes are generated in OKLCH and always verified by script. | WCAG 2.2 is a W3C Recommendation; APCA is still a WCAG 3 draft with beta licensing. OKLCH does not guarantee contrast by lightness difference alone. |

## Harness (8 steps, two human gates)

0 Intake (max 5 questions, all with defaults) → 1 Direction (**G1**: user picks 1 of 3) → 2 Spec
(**G2**: user approves a one-page summary; spec lint passes) → 3 Scaffold → 4 Sections one by one →
5 Signature moment → 6 Responsive and accessibility → 7 QA (100-point rubric, max 3 fix loops) → 8 Delivery.

Hard blockers: body-text contrast below 4.5:1 (3:1 large text), console errors, horizontal scroll at
375/768/1440, broken reduced-motion, touch targets under 44px, missing focus ring, LCP over 2.5s,
more than 2 font families (plus mono) or more than 1 accent, colors defined outside `:root`.
