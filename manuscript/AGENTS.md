---
title: "Manuscript directory: casino_royale_1967 (FIVE 00s)"
type: "manuscript_guide"
version: "0.1.0"
---

# Manuscript (`manuscript/`)

Repository-wide behavioral rules live in [`../docs/agent_instructions.md`](../docs/agent_instructions.md).
This file covers **manuscript-specific** editing for the FIVE 00s package.

## {{TOKEN}} protocol

Numeric values from analysis outputs **must** use `{{VARIABLE_NAME}}` syntax.
Hardcoding a number that changes when `config.yaml` is edited or the analysis
is re-run is the primary cause of inaccurate manuscripts.

**The token pipeline:**

1. `scripts/z_generate_manuscript_variables.py` calls
   `src/casino_royale_1967/manuscript_variables.py::generate_variables()`, which
   reads `manuscript/config.yaml` (`mission:` / `experiment:` blocks) and
   recomputes every result metric live from the deterministic domain core.
2. The script writes the full `{TOKEN: value}` map to
   `output/data/manuscript_variables.json`.
3. It renders all six concept figures into `output/figures/`.
4. `write_resolved_manuscript_tree()` copies each `manuscript/[0-9]*.md`
   template to `output/manuscript/`, substituting every `{{TOKEN}}` — strict
   (any unresolved token raises).

**Adding a token:** add a key to `generate_variables()`, then reference it with
`{{TOKEN}}` in a numbered section. Do both — three gates in
`tests/test_manuscript_variables.py` enforce the pairing:

| Gate | Fails when |
|---|---|
| `test_all_manuscript_tokens_are_generated` | a section uses a token that `generate_variables()` does not produce |
| `test_every_generated_token_is_used` | `generate_variables()` produces a token no section references |
| `test_no_bare_numerals_in_measured_prose` | `03_results.md` or `04_conclusion.md` states a numeral outside a token (allowlist: the `/100` scale denominator, the film's year `1967`, and the declared coverage floor `90`) |

Methodology and setup sections are exempt from the numeral gate because their
numbers are *definitions* — card values, drawing rules, loss-weight formulas —
rather than measurements.

## Figure protocol

Figure *paths* in the manuscript go through `FIGURE_*` tokens, never literal
PNG filenames, so renaming an entry in `FIGURE_FILENAMES` cannot silently break
an image link — `test_figure_links_go_through_tokens` enforces it. Figure
*labels* use Pandoc-crossref `[@fig:label]`:

| Label | PNG | Generator |
|---|---|---|
| `{#fig:coordination}` | `output/figures/coordination_farce.png` | `render_coordination_figure()` |
| `{#fig:dispatch}` | `output/figures/dispatch_chaos.png` | `render_dispatch_figure()` |
| `{#fig:spoof}` | `output/figures/spoof_analyzer.png` | `render_spoof_figure()` |
| `{#fig:identity}` | `output/figures/identity_confusion.png` | `render_identity_figure()` |
| `{#fig:baccarat}` | `output/figures/baccarat_odds.png` | `render_baccarat_figure()` |
| `{#fig:escalation}` | `output/figures/escalation_ladder.png` | `render_escalation_figure()` |

## Authoritative token source

`src/casino_royale_1967/manuscript_variables.py::generate_variables()` is the
single source of truth; the live cross-reference test
`test_all_manuscript_tokens_are_generated` is what gates completeness.

## Section modification protocol

1. Update the domain core (`src/.../`) or `manuscript/config.yaml`.
2. Regenerate: `uv run python scripts/z_generate_manuscript_variables.py`.
3. If a token changed, update the `{{TOKEN}}` usage (or just re-run — tokens
   re-resolve automatically).
4. Re-run the test suite + live cross-reference.
