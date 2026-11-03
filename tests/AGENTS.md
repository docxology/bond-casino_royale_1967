# tests/ — real data, no mocks, an executed layer contract

One test module per concept (`test_coordination_farce.py`, `test_dispatch_chaos.py`,
`test_spoof_analyzer.py`, `test_identity_confusion.py`, `test_baccarat_table.py`,
`test_escalation_ladder.py`), plus `test_figures.py`, `test_mission.py`,
`test_manuscript_variables.py`, `test_scripts_smoke.py`, `test_regeneration_determinism.py` and
`test_layer_contract.py`.

## Rules

- **Zero mocks.** No `MagicMock`, `mocker.patch` or `unittest.mock`: real computation against real
  protocol types. A mocked mission tests the mock.
- **The layer contract is executed, not asserted.** `test_layer_contract.py` imports the whole domain
  core in a subprocess with `bond_api` blocked at the meta-path level, and carries a positive control
  proving `mission.py` fails under the same conditions — so the check cannot pass vacuously. Keep the
  control.
- **Determinism is proven by regenerating**: `test_regeneration_determinism.py` runs the generator
  twice and diffs. A new persisted artifact joins that comparison or the claim is weakened.
- **Coverage floor 90% line and branch on `src/`.** Do not lower it to admit new code.
- **`test_scripts_smoke.py` covers the wrappers**; a new script needs its smoke path.
- **Assertions about absence are contracts too.** A test that refuses a DOI or a repository URL for a
  local-only package is protecting the rule that a fabricated identifier is worse than none — read it
  before changing wording it depends on.
