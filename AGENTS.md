# AGENTS.md — Casino Royale (1967) · FIVE 00s

**This is an active PROJECT BOND film package** in the BOND suite
(`projects/working/bond/casino_royale_1967`), built under the shared Bond
guardrail preamble. It models the coordination farce of the 1967 *Casino
Royale* — five operatives, one codename — as deterministic mission software,
exposed through the FROZEN `bond_api` `MissionProvider` protocol.

## Scope and hard constraints

- **Scope is exactly this package directory** (`src/casino_royale_1967/`,
  `scripts/`, `tests/`, `manuscript/`, docs, metadata). Never touch sibling
  packages, bond root files, or the template repo.
- **Local-only working tree.** No remote, never push. Path-scoped commits
  inside this repo only (`git add -A` here).
- **Zero mocks.** Real computation + real protocol types only — no
  `MagicMock` / `mocker.patch` / `unittest.mock`.
- **≥90% line+branch coverage on `src/`** (`uv run pytest tests/
  --cov=src --cov-fail-under=90`).
- **Deterministic:** fixed seed 7, no untracked random reliance, no wall
  clock in domain artifacts.
- **Thin orchestrators in `scripts/`; business logic in `src/`.**
- **No leftover `template[_]code_project` strings** (bracket-split any must-run
  grep in docs so the doc cannot trip its own gate).
- Manuscript metrics are injected from `manuscript/config.yaml` +
  `src/casino_royale_1967/manuscript_variables.py` — never hand-authored.
- Update `README.md`, `AGENTS.md`, `TODO.md` to reflect THIS package.

## Layer contract

| Layer | Files | Rule |
|---|---|---|
| Pure domain core | `src/casino_royale_1967/{coordination_farce,dispatch_chaos,spoof_analyzer,identity_confusion,baccarat_table,escalation_ladder}.py`, `src/casino_royale_1967/figures/` | stdlib + numpy/matplotlib only; **no** `infrastructure.*`, **no** `bond_api` imports; importable standalone |
| Protocol adapter | `src/casino_royale_1967/mission.py` | the single module constructing FROZEN `bond_api` types |
| Manuscript | `src/casino_royale_1967/manuscript_variables.py` | token hydration, strict resolved-tree writer |
| Scripts | `scripts/mission.py`, `scripts/z_generate_manuscript_variables.py` | thin CLI wrappers (sys.path bootstrap + argv forwarding), `# noqa: E402` on bootstrap lines |

`mission.py` and the pure core communicate through plain dicts/dataclasses;
nothing in `src` imports `infrastructure.*` at all
(`manuscript/layer_contract.yaml` declares `allow_infrastructure_imports: []`).

## Protocol binding (FROZEN bond-api)

- `pyproject.toml` binds `bond-api` as a local path dependency:
  ```toml
  [tool.uv.sources]
  bond-api = { path = "/Users/4d/Documents/GitHub/template/projects/working/bond/bond-api" }
  ```
  with `"bond-api"` in `[project] dependencies`; run `uv sync --extra dev`
  before pytest.
- `src/casino_royale_1967/mission.py` exports `MissionProvider` at module top
  level with `film = "casino_royale_1967"`, implementing `brief()` /
  `recon()` / `plan()` / `execute()` / `debrief()` against the frozen
  `bond_api` dataclasses, and registers gadgets (`roster`, `coordination`,
  `dispatch`, `doctrine`) on the module-level `GADGET_REGISTRY`.

## Testing requirements

- **Per concept module** a real-data test file: `test_coordination_farce.py`,
  `test_dispatch_chaos.py`, `test_spoof_analyzer.py`,
  `test_identity_confusion.py`, `test_baccarat_table.py`,
  `test_escalation_ladder.py`.
- `test_mission.py` — protocol conformance, deterministic outcome + registry
  + serialization round-trips + slug discovery against the real `bond_api`.
- `test_manuscript_variables.py` — token map plus the **live cross-reference
  gate** scanning `manuscript/[0-9]*.md` (numbered prose only; guide files
  url `{{TOKEN}}` syntax legitimately).
- `test_scripts_smoke.py` — subprocess runs of the thin CLIs via
  `sys.executable` with `cwd=project_root`.
- `test_figures.py` — deterministic PNG render + byte-idempotence.

## Verification before done

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
git status --short   # clean after commit
```

Report: modules + concepts built, coverage %, commit SHA.
