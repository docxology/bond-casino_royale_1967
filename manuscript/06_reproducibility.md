# Reproducibility

## Determinism guarantees

Every artifact in this project is deterministic by construction:

- **Fixed seed.** The mission uses seed 7; the dispatch simulation makes no
  random draws at all — order processing is a pure function of the input
  order stream.
- **No wall clock in domain artifacts.** Coordination, dispatch, and doctrine
  reports carry no timestamps; `Provenance.wall_time_s` is `0.0`. The only
  wall-clock value in the system is the `GENERATION_TIMESTAMP` manuscript
  token, injected at `{{GENERATION_TIMESTAMP}}` and overridable for
  deterministic tests.
- **Live computation.** Manuscript metrics are recomputed from the domain core
  at hydration time, so prose can never drift from code.

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
