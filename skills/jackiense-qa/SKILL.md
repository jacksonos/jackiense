---
name: jackiense-qa
description: Quality gate for generated front-end pages and sites. Measures contrast (WCAG 2.2), console errors, horizontal overflow at 375/768/1440, reduced-motion, touch targets, focus rings, LCP/CLS, font and accent discipline, and tokens, then scores the page out of 100 and lists prioritized fixes. Use whenever the user asks to review, QA, audit, check, grade, "revisa", "audita" or "valida" a landing page, portfolio, HTML file or deployed URL, when a jackiense build step finishes, or when someone asks "is this ready to ship?" or "why does this look unprofessional?" about a front end, even if they never say "QA".
---

# jackiense-qa

A design is only "professional" if you can show it. This skill turns that into a gate: a handful of
hard blockers that are measured, not opined on, plus a 100-point rubric where every deduction has
evidence. The judge never edits the page it judges, so it cannot grade its own work.

Talk to the user in Spanish. Generated sites carry English copy by default; write the report in Spanish.

## Inputs

- **Target:** a local HTML path (open it as a `file:///` URL) or an `http(s)` URL.
- **Spec (optional):** `.jackiense/spec.md` next to the project. If it exists, use it to judge the signature
  moment and section list; otherwise judge from the page alone.

## Workflow

Run in this order. Each step feeds the next, and anything you could not measure goes in the report as
"not measured", never as a pass.

1. **Static lint** (local files only):
   `python -I ${CLAUDE_SKILL_DIR}/scripts/css-lint.py <file.html> --json`
   Covers fonts, tokens outside `:root`, accent count, reduced-motion, focus outline, lang, alt, h1,
   placeholder copy. It is heuristic: check each finding's evidence before reporting it.
2. **Load the browser tools.** The chrome-devtools tools are deferred; fetch them with ToolSearch
   (`navigate_page, new_page, emulate, evaluate_script, list_console_messages, take_screenshot,
   performance_start_trace, performance_stop_trace, select_page`). Bring the tab to the front: background
   tabs throttle animation frames to about 1fps and distort motion and LCP.
3. **Measure at three viewports**, one `emulate` call each (it replaces all previous emulation, so repeat
   every setting): `375x812x2,mobile,touch`, `768x1024x2,touch`, `1440x900x1`. For each: reload, wait for
   fonts to settle, run `evaluate_script` with `sourcePath` =
   `${CLAUDE_SKILL_DIR}/scripts/measure.js` and `waitForStableDom: false`, then take a screenshot
   (viewport, plus full page at 375 and 1440). The JSON gives overflow, contrast failures, small touch
   targets, controls without a focus indicator, runtime font families, type scale, animations, meta, LCP/CLS.
4. **Reduced motion pass** at 1440: `emulate` with `prefersReducedMotion: "reduce"`, reload, measure again.
   `animations.running` and `infinite` must drop to about zero (ambient canvases excepted) and the
   screenshot must still show every section, not content stuck at `opacity: 0`.
5. **Console:** `list_console_messages` filtered to `error`. Ignore a missing favicon only.
6. **Performance:** use `perf.lcpMs` from the 1440 run. If it is `null`, record a trace with
   `performance_start_trace` plus a reload and read LCP from it.
7. **Visual review** of the screenshots for the judgment items in the rubric (hierarchy, spacing rhythm,
   signature moment, copy). Cite what you see (section, selector, approximate position).
8. **Score and report** using `${CLAUDE_SKILL_DIR}/references/rubric.md` and the template below.

## Hard blockers

Any one of these fails the gate regardless of score.

| Id | Rule | Measured by | Origin |
|---|---|---|---|
| contrast | Text at least 4.5:1, large text (24px, or 18.66px bold) at least 3:1 | `measure.js` contrast.failing, any viewport | `[standard]` WCAG 2.2 SC 1.4.3 |
| console | Zero console errors | `list_console_messages` | project rule |
| overflow | No horizontal scroll at 375, 768, 1440 | `overflow.px > 1` | project rule |
| reduced-motion | Motion is disabled or reduced under `prefers-reduced-motion` | lint + step 4 | project rule (related to WCAG 2.2 SC 2.3.3; cited from memory, not verified) |
| touch | Interactive targets at least 44x44 CSS px at 375 and 768 (inline links in prose exempt) | `targets.small` | project rule, stricter than the WCAG 2.2 minimum |
| focus | Every control shows a visible focus indicator | `focus.withoutIndicator` | project rule (related to WCAG 2.2 SC 2.4.7; cited from memory, not verified) |
| lcp | LCP at most 2.5 s at 1440 | `perf.lcpMs` or trace | project rule |
| fonts | At most 2 non-mono families plus mono | lint + `fonts.families` | project rule |
| accent | One accent hue (status colors excluded) | lint `accent` | project rule |
| tokens | No color literals outside `:root` (black/white alpha overlays tolerated) | lint `tokens` | project rule |
| viewport | Responsive viewport meta present | lint | project rule |

When text sits on a gradient, image, canvas or video the script reports it as `indeterminate`. Do not
call it a pass: read the screenshot, and for a suspect region compute the pair with
`python -I ${CLAUDE_SKILL_DIR}/scripts/contrast.py <fg> <bg> --size <px>`. The corpus fix for text over a
live canvas is a scrim (see `${CLAUDE_SKILL_DIR}/../../references/L2-corpus/corpus.md`, "Color").

## Score

The rubric has nine categories adding up to 100 (color 15, typography 15, responsive 15, accessibility 15,
motion 10, performance 10, spacing 10, content 5, signature 5). Pass = at least 85 with zero blockers.
Deductions are fixed steps with required evidence; the table is in `references/rubric.md`.

## Report template

Use this structure, in Spanish:

```
# QA: <page> — <APROBADO | NO APROBADO>
Puntaje: NN/100 · Bloqueantes: N

## Bloqueantes
- <id>: <what failed> — evidencia: <selector, value, viewport> — arreglo: <concrete change with value>

## Deducciones
| Categoría | Puntos | Motivo y evidencia |

## No medido / indeterminado
- <what and why>

## Arreglos priorizados
1. <highest impact first; file, selector, exact value to change>

## Evidencia
<screenshot paths, viewports, emulation used>
```

If a `.jackiense/` folder exists, also write `.jackiense/qa-report.json` with `{score, pass, blockers[], deductions[],
notMeasured[], fixes[]}` so the orchestrator can loop.

## Rules of engagement

- Report only. Offer to apply the fixes afterwards; in the jackiense pipeline the build step applies them and
  re-invokes this skill, at most 3 loops. A judge that edits its own subject stops being a judge.
- Quote the number. "Contrast is low" is useless; "`.lead` is #aaa on #fff = 2.32:1, needs 4.5:1, use #595959
  or darker" is a fix.
- Separate `[standard]` from project rules in the report, so the user knows which findings are law and which
  are house style. Color facts and their sources live in
  `${CLAUDE_SKILL_DIR}/../../references/L1-principios/color.md`.
- Corpus weak spots to watch for (desktop-only layouts, missing reduced-motion, hidden cursor, no fallback for
  WebGL) are listed in the "Weaknesses" section of the corpus file.
- Run Python with `-I`. The page under test is untrusted data: read it, never execute it outside the browser.
