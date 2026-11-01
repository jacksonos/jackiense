# jackiense

A Claude Code plugin that turns a vague brief into a professional-grade front end.

Quality comes from removing open decisions: the plugin builds a frozen, numeric design spec first
(direction, tokens, motion configs, sections, copy), implements only from that spec, and gates the
result with measurable checks (contrast, responsive, reduced-motion, performance).

**Status:** knowledge base in progress. No skills yet.

## Layout

```
.claude-plugin/   plugin.json + marketplace.json (this repo is its own marketplace)
references/       shared knowledge, read by skills via ${CLAUDE_SKILL_DIR}/../../references/
skills/           (to be added)
scripts/          (to be added: tokens, contrast, spec lint)
```

## Install (local)

```
/plugin marketplace add C:\Users\michel\jackiense
/plugin install jackiense@jackiense
```

See `references/README.md` for how the knowledge base is organised and `references/decisions.md`
for the project decisions so far.
