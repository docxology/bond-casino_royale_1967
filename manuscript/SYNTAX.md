# Manuscript Syntax Reference (FIVE 00s)

Pandoc / pandoc-crossref conventions for the **Casino Royale (1967) · FIVE
00s** manuscript. Figures, tokens, and tables are the authoritative registry
for this package.

## `{{TOKEN}}` protocol

Numeric result claims **must** use `{{TOKEN}}` syntax — never hard-coded
numbers in prose. Tokens are computed live by
`src/casino_royale_1967/manuscript_variables.py` from
`manuscript/config.yaml` + the deterministic domain core, and hydrated by
`scripts/z_generate_manuscript_variables.py` (strict: any unresolved token
fails).

To add a token: add it to `generate_variables()`, reference it with
`{{TOKEN}}` in a `manuscript/[0-9]*.md` section, and let the live
cross-reference test (`test_manuscript_variables.py`) verify it.

## Figure references

```markdown
![Per-task agent load; bars above the dashed line are overlaps.](../output/figures/coordination_farce.png){#fig:coordination}
```

Reference in prose with `[@fig:label]`. Images must exist under
`output/figures/` at render time.

### Figure label registry

| Label | PNG filename | Generator |
|---|---|---|
| `{#fig:coordination}` | `output/figures/coordination_farce.png` | `render_coordination_figure()` in `src/casino_royale_1967/figures/plots.py` |
| `{#fig:dispatch}` | `output/figures/dispatch_chaos.png` | `render_dispatch_figure()` |
| `{#fig:spoof}` | `output/figures/spoof_analyzer.png` | `render_spoof_figure()` |
| `{#fig:identity}` | `output/figures/identity_confusion.png` | `render_identity_figure()` |
| `{#fig:baccarat}` | `output/figures/baccarat_odds.png` | `render_baccarat_figure()` |
| `{#fig:escalation}` | `output/figures/escalation_ladder.png` | `render_escalation_figure()` |

## Section labels

Every H1 carries `{#sec:<name>}`: `00_abstract.md` → `{#sec:abstract}`,
`01_introduction.md` → `{#sec:introduction}`, `02_methodology.md` →
`{#sec:methodology}`, `03_results.md` → `{#sec:results}`,
`04_conclusion.md` → `{#sec:conclusion}`, `05_experimental_setup.md` →
`{#sec:experimental_setup}`, `06_reproducibility.md` → `{#sec:reproducibility}`,
`07_scope_and_related_work.md` → `{#sec:scope}`, `99_references.md` →
`{#sec:references}`.

## Citations

`[@key]` / `@key` narrative form; keys must exist in `references.bib`.
Never write raw `\cite{}`.

## Prose conventions

- No "In summary" / "In conclusion" at section ends.
- Use explicit file paths when referencing code (`src/casino_royale_1967/coordination_farce.py`, not "the model").
- Keep paragraphs focused; one idea per paragraph.

## See also

- [`AGENTS.md`](AGENTS.md) — manuscript editing rules and token protocol.
- [`README.md`](README.md) — quick orientation.
- [`preamble.md`](preamble.md) — LaTeX preamble.
