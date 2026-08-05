# Reproducibility

## Determinism guarantees

Every artifact in this project is deterministic by construction:

- **Fixed seed.** The mission uses seed 7; the dispatch simulation makes no
  random draws at all — order processing is a pure function of the input
  order stream.
- **No wall clock in any persisted artifact.** Coordination, dispatch, and
  doctrine reports carry no timestamps; `Provenance.wall_time_s` is `0.0`; and
  the manuscript token map reads no clock at all — `generate_variables` takes
  no `now=` parameter, because an injectable clock with a wall-clock default is
  still a wall clock. This manuscript's date, {{MANUSCRIPT_DATE}}, is the
  committed `paper.date` in `manuscript/config.yaml`; edit that file to change
  it, and it is otherwise fixed.
- **No interpreter state either.** The declared Python range is
  `{{PYTHON_REQUIRES}}` — the committed `paper.python_requires`, held equal to
  `requires-python` in `pyproject.toml` by test. The token map introspects
  nothing about the machine that ran it.
- **Live computation.** Manuscript metrics are recomputed from the domain core
  at hydration time, so prose can never drift from code.

Because the token map is a pure function of committed files, regenerating with
`scripts/z_generate_manuscript_variables.py` reproduces
`output/data/manuscript_variables.json`, `output/manuscript/*.md`, and
`output/figures/*.png` **byte for byte**. That is not an aspiration:
`tests/test_regeneration_determinism.py` runs the generator twice in
succession, hashes every artifact under `output/`, and fails on any difference.

## Canonical metric snapshot

| Metric | Value |
|---|---|
| Assignments | {{RESULT_ASSIGNMENTS}} |
| Overlaps | {{RESULT_OVERLAP_COUNT}} |
| Conflicts | {{RESULT_CONFLICT_COUNT}} |
| Coordination loss | {{RESULT_COORDINATION_LOSS}} |
| Clearance violations | {{RESULT_CLEARANCE_VIOLATIONS}} |
| Single-agent deduplication of assignments (kept / dropped) | {{RESULT_DEDUP_KEPT}} / {{RESULT_DEDUP_DROPPED}} |
| Dispatch orders | {{RESULT_ORDERS}} |
| Dispatched / rejected orders | {{RESULT_DISPATCHED}} / {{RESULT_REJECTED}} |
| Protocol violations | {{RESULT_VIOLATIONS}} |
| Chaos index | {{RESULT_CHAOS_INDEX}} |
| Success ratio | {{RESULT_SUCCESS_RATIO}} |
| Spoof index | {{RESULT_SPOOF_INDEX}} / 100 |
| Identity NMI | {{RESULT_IDENTITY_NMI}} |
| Dispatch ambiguity `H(routed \| intended)` (bits) | {{RESULT_IDENTITY_AMBIGUITY}} |
| Residual identity `H(intended \| routed)` (bits) | {{RESULT_IDENTITY_RESIDUAL}} |
| Baccarat player / banker | {{RESULT_BACCARAT_PLAYER}} / {{RESULT_BACCARAT_BANKER}} |
| Table collision ({{CONFIG_TABLE_BONDS}} Bonds, i.i.d.-across-hands approximation) | {{RESULT_TABLE_COLLISION}} |
| Escalation (spoof / sanctioned steps) | {{RESULT_ESCALATION_SPOOF}} / {{RESULT_ESCALATION_SANCTIONED}} |
| Acceleration factor | {{RESULT_ESCALATION_ACCELERATION}}× |

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

The gate enforces ≥90% line+branch coverage on `src/`, zero mocks, and a clean
git tree after regeneration. Figures and the resolved manuscript tree live
under `output/`, which is git-ignored and regenerable.
