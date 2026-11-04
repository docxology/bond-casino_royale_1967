# AGENTS.md — Casino Royale (1967) · FIVE 00s

**This is an active PROJECT BOND film package**, drafted in the BOND suite as
`projects/working/bond/casino_royale_1967` and tracked at
`github.com/docxology/bond-casino_royale_1967`. It is built under the shared
Bond guardrail preamble and models the coordination
farce of the 1967 *Casino Royale* — five operatives, one codename — as
deterministic mission software, exposed through the FROZEN `bond_api`
`MissionProvider` protocol.

## Scope and hard constraints

- **Scope is exactly this package directory** (`src/casino_royale_1967/`,
  `scripts/`, `tests/`, `manuscript/`, docs, metadata). Never touch sibling
  packages, bond root files, or the template repo.
- **Repo-scoped commits.** The tree is tracked at
  `github.com/docxology/bond-casino_royale_1967`; commit inside this repo only
  (`git add -A` here).
- **Zero mocks.** Real computation + real protocol types only — no
  `MagicMock` / `mocker.patch` / `unittest.mock`.
- **≥90% line+branch coverage on `src/`** (`uv run pytest tests/
  --cov=src --cov-fail-under=90`).
- **Deterministic:** fixed seed 7, no untracked random reliance, and no wall
  clock or interpreter introspection in *any* persisted artifact — the
  manuscript token map is a pure function of committed files, so regenerating
  reproduces `output/` byte for byte (`tests/test_regeneration_determinism.py`
  proves it by regenerating twice and diffing). Never add a `now=` parameter
  with a wall-clock default.
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
| Package init | `src/casino_royale_1967/__init__.py` | eager domain re-exports; adapter symbols resolved **lazily** via PEP 562 `__getattr__` so the core imports without `bond_api` |
| Protocol adapter | `src/casino_royale_1967/mission.py` | the single module constructing FROZEN `bond_api` types |
| Manuscript | `src/casino_royale_1967/manuscript_variables.py` | token hydration, strict resolved-tree writer |
| Scripts | `scripts/mission.py`, `scripts/z_generate_manuscript_variables.py` | thin CLI wrappers (sys.path bootstrap + argv forwarding), `# noqa: E402` on bootstrap lines |

`mission.py` and the pure core communicate through plain dicts/dataclasses;
nothing in `src` imports `infrastructure.*` at all
(`manuscript/layer_contract.yaml` declares `allow_infrastructure_imports: []`).

The layer contract is **executed, not asserted**: `tests/test_layer_contract.py`
imports the whole domain core in a subprocess with `bond_api` blocked at the
meta-path level, and carries a positive control proving `mission.py` fails
under the same conditions — so the check cannot pass vacuously.

## Protocol binding (FROZEN bond-api)

- `pyproject.toml` binds `bond-api` as a local path dependency, vendored at
  `vendor/bond-api`:
  ```toml
  [tool.uv.sources]
  bond-api = { path = "vendor/bond-api" }
  ```
  with `"bond-api"` in `[project] dependencies`; run `uv sync --extra dev`
  before pytest.
- `src/casino_royale_1967/mission.py` exports `MissionProvider` at module top
  level with `film = "casino_royale_1967"`, implementing `brief()` /
  `recon()` / `plan()` / `execute()` / `debrief()` against the frozen
  `bond_api` dataclasses, and registers seven gadgets (`roster`,
  `coordination`, `dispatch`, `doctrine`, `identity`, `baccarat`,
  `escalation`) on the module-level `GADGET_REGISTRY`, alongside the
  `GADGETS` map and the `register_gadgets(registry=None)` hook.

**This surface is FROZEN.** `bond-cli`, the coordinator's reconcile and the
orchestrator consume these symbols across all 33 BOND packages. Deepen inside
the stages — richer payloads, more findings, more plan steps, new gadget
entries — never change a signature, the class name, or a registry symbol.

## Testing requirements

- **Per concept module** a real-data test file: `test_coordination_farce.py`,
  `test_dispatch_chaos.py`, `test_spoof_analyzer.py`,
  `test_identity_confusion.py`, `test_baccarat_table.py`,
  `test_escalation_ladder.py`.
- `test_mission.py` — protocol conformance, deterministic outcome + registry
  + serialization round-trips + slug discovery against the real `bond_api`.
- `test_layer_contract.py` — subprocess import of the domain core with
  `bond_api` blocked, its positive control against `mission.py`, a source scan
  for forbidden imports, and the lazy adapter exports. A new domain module must
  be added to its `DOMAIN_MODULES` tuple or the completeness check fails.
- `test_manuscript_variables.py` — token map plus **three manuscript gates**
  over `manuscript/[0-9]*.md` (numbered prose only; guide files use
  `{{TOKEN}}` syntax legitimately): unknown tokens fail, generated-but-unused
  tokens fail, and bare numerals in `03_results.md` / `04_conclusion.md` fail.
- `test_scripts_smoke.py` — subprocess runs of the thin CLIs via
  `sys.executable` with `cwd=project_root`.
- `test_figures.py` — deterministic PNG render + byte-idempotence.
- `test_regeneration_determinism.py` — the byte-for-byte claim, executed: the
  production generator is run twice in sequence (no injected values) and every
  artifact it writes is hashed and diffed, plus a scan rejecting any
  clock-shaped token value.

**Positive controls are mandatory for new gates.** Every contract check here
ships with an input that must break it (see `docs/testing_philosophy.md`); a
check that cannot fail reports safety it does not provide.

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
