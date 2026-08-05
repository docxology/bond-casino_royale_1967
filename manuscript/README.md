# Casino Royale (1967) · FIVE 00s — Manuscript

The FIVE 00s manuscript documents six deterministic concepts built from the
five-Bond farce of the 1967 *Casino Royale*:

1. **Coordination-farce model** — overlap/conflict/clearance detection and a
   weighted coordination loss over a five-agent duplicate-identity roster.
2. **Dispatch-chaos simulation** — a tick-based dispatch centre enforcing five
   protocol rules, with a chaos index.
3. **Spoof protocol analyzer** — lexical scoring of satirical ops doctrine
   against a sane protocol, with a normalised spoof index.
4. **Identity-confusion model** — a routing confusion matrix with entropy,
   mutual information and NMI, plus Bayesian resolution of a sighting.
5. **Baccarat table model** — exact chemin de fer deal odds by enumeration and
   the birthday-bound hand-collision probability across the seated Bonds.
6. **Escalation-ladder model** — doctrine as an absorbing Markov chain,
   compared against a disciplined doctrine.

## Sections

| File | Content |
|---|---|
| `00_abstract.md` | Abstract with the canonical result tokens for all six concepts |
| `01_introduction.md` | The five-Bond premise, the six concepts, and the reader's guide |
| `02_methodology.md` | The six algorithms, one section each |
| `03_results.md` | Canonical metrics, the per-rule violation table, and all six figures |
| `04_conclusion.md` | Summary across the six concepts |
| `05_experimental_setup.md` | Configuration parameters + software environment |
| `06_reproducibility.md` | Determinism guarantees + the full metric snapshot |
| `07_scope_and_related_work.md` | What the models do not claim + related threads |
| `99_references.md` | References (mirrors `references.bib`) |

Supporting files: `config.yaml` (identity + experiment parameters),
`preamble.md` (LaTeX preamble), `references.bib` (bibliography),
`layer_contract.yaml` (declared import boundaries), [`SYNTAX.md`](SYNTAX.md)
(markup conventions) and [`AGENTS.md`](AGENTS.md) (editing protocol).

## The rule that matters

Every measured number is injected as a `{{TOKEN}}` from `config.yaml` +
`src/casino_royale_1967/manuscript_variables.py`. Never hand-author a metric.
Three gates in `tests/test_manuscript_variables.py` enforce this:

1. a token used in a numbered section but not generated fails;
2. a token generated but never referenced fails;
3. a bare numeral in `03_results.md` or `04_conclusion.md` fails.

Figures are referenced through `FIGURE_*` tokens too, so renaming a PNG in
`FIGURE_FILENAMES` cannot silently break an image link.
