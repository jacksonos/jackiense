# references

Shared knowledge for the jackiense skills. Skills read only the file they need.

| Path | Layer | Provenance tag | What it holds |
|---|---|---|---|
| `L1-principios/` | Design principles and standards | `[standard]` | Verified external sources (WCAG, color science, design systems). Each fact carries a URL and a verification date. |
| `L2-corpus/` | Measured observations | `[corpus]` | Ranges and patterns extracted from real, high-quality site specs, with a "seen in N of M" counter. |
| `decisions.md` | Project decisions | — | What was decided and why. |

(`L3-arquetipos/` and `L4-recetas/` will be added when the archetype and recipe skills are built.)

## Conventions

- **Provenance is mandatory.** Every rule is tagged `[standard]` (external, cited) or `[corpus]`
  (observed). Never present an observation as a standard.
- **Rule vs style.** A pattern seen in 3 or more sources of the corpus is a *rule*; fewer is *style*.
  Update the counter whenever a source is added.
- **Verified vs unverified.** Anything not checked against a primary source is listed under
  "Unverified" and must not be used as a hard gate.
- **No copied content.** The corpus stores numbers and patterns, not the original prompts or copy.
- Language: English (the generated sites default to English copy).
