# Rubric (100 points)

Start every category at its maximum and subtract. Each deduction needs evidence in the report. Floor at 0.
Pass = total at least 85 and zero hard blockers (see SKILL.md).

## 1. Color and contrast (15)
| Deduction | When |
|---|---|
| -3 each, cap -9 | Distinct failing text pair (fg/bg) in `contrast.failing` |
| -3 | Lint `accent` finding (more than one chromatic hue group) |
| -3 | Lint `tokens` blocker (more than 5 literals outside `:root`) |
| -1 | Lint `tokens` warn (1-5 literals outside `:root`) |
| -2 | Text over image/canvas/video with no scrim and visibly weak legibility (judged from screenshot) |

## 2. Typography and hierarchy (15)
| Deduction | When |
|---|---|
| -5 | Lint/runtime fonts: more than 2 non-mono families |
| -3 | Fewer than 4 or more than 9 distinct font sizes (`typeScale`) |
| -3 | `h1` count is not exactly 1 |
| -2 | Body text (most characters) under 16px at 1440 |
| -2 | Largest size is less than 2.5x the body size (weak hierarchy) |

## 3. Responsive (15)
| Deduction | When |
|---|---|
| -5 each viewport | Horizontal overflow (375, 768, 1440; max -15) |
| -3 | Small touch targets at 375 or 768 |
| -2 | Body text under 14px at 375 |
| -0 to -5 | Layout does not hold at a viewport in the screenshots (collapsed columns, clipped content, unreadable); state which viewport and what |

## 4. Accessibility (15)
| Deduction | When |
|---|---|
| -5 | Any control without a focus indicator |
| -5 | Motion still running under reduced motion, or no `prefers-reduced-motion` handling |
| -2 | `<html lang>` missing |
| -2 | Images without `alt` |
| -2 | Native cursor hidden globally or text selection disabled globally |
| -1 each, cap -3 | Other issues seen (empty links, heading order skipped, color as only signal) |

## 5. Motion (10)
Read the CSS/JS to judge.
| Deduction | When |
|---|---|
| -3 | More than 3 distinct easing curves in use |
| -3 | Durations outside 150-1200 ms for non-ambient motion |
| -2 | `transition: all` |
| -2 | No hover/focus feedback on interactive elements, or entrance sequence longer than 2 s |

## 6. Performance (10)
| Deduction | When |
|---|---|
| -5 / -10 | LCP 2.5-4 s / over 4 s |
| -5 | Any console error (also a blocker) |
| -3 / -5 | CLS above 0.1 / above 0.25 |

## 7. Spacing and layout (10)
Judged from screenshots plus CSS.
| Deduction | When |
|---|---|
| -3 | Fewer than about 80% of spacing values on a 4/8px grid |
| -3 | Inconsistent container width or gutters between sections |
| -4 | Weak vertical rhythm or misalignment (name the sections) |

## 8. Content (5)
| Deduction | When |
|---|---|
| -2 | Placeholder copy (lorem ipsum, TBD, TODO) |
| -2 | No clear primary call to action above the fold |
| -1 | Generic filler copy |

## 9. Signature moment (5)
| Deduction | When |
|---|---|
| -3 | No identifiable signature moment, or it does not execute |
| -2 | WebGL/3D tier with no fallback when WebGL fails or reduced motion is on |

## Thresholds that need a source before they become standards
The 2.5 s LCP and 0.1 CLS values are project rules taken from commonly cited Core Web Vitals "good" ranges;
they have not been verified against the primary source in this knowledge base. The 44px touch target is a
project rule, stricter than the WCAG 2.2 target-size minimum (verify SC 2.5.8 before citing a number).
