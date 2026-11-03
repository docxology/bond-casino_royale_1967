# src/ — the domain core, the adapter and the manuscript tokens

`casino_royale_1967/`: `coordination_farce.py`, `dispatch_chaos.py`, `spoof_analyzer.py`,
`identity_confusion.py`, `baccarat_table.py`, `escalation_ladder.py`, `figures/`, plus
`mission.py`, `__init__.py` and `manuscript_variables.py`.

## Rules

- **Keep the layer contract.** The pure domain core and `figures/` use the standard library plus
  numpy/matplotlib only: no `infrastructure.*` and no `bond_api` imports, so the core imports
  standalone. `mission.py` is the **single** module that constructs frozen `bond_api` types, and
  `manuscript_variables.py` owns token hydration.
- **`__init__.py` re-exports the domain eagerly and adapter symbols lazily** through PEP 562
  `__getattr__`, which is what lets the core import without `bond_api` installed. Keep that split.
- **The `MissionProvider` surface is FROZEN.** `film`, `brief()`, `recon()`, `plan()`, `execute()`,
  `debrief()`, `register_gadgets()` and `GADGET_REGISTRY` are consumed by bond-cli, the coordinator
  and the orchestrator across the suite's packages. Deepen inside the stages; never change a
  signature, the class name or a registry symbol.
- **Determinism is a property of the artifact.** Fixed seed 7, no wall clock and no interpreter
  introspection on the persisted path, because the manuscript token map is a pure function of
  committed files. Never add a `now=` parameter with a wall-clock default.
- **Coverage floor: 90% line and branch on `src/`** (`uv run pytest tests/ --cov=src
  --cov-fail-under=90`).
- **`bond-api` path dependency: the sibling-relative form.** `pyproject.toml` declares
  `bond-api = { path = "../bond-api" }`, so `uv sync --extra dev` resolves from a checkout of the
  suite. It previously named an absolute path on the author's machine, which is why this package
  could not install anywhere else. `uv.lock` is generated from that declaration — never hand-edit it.
- **Publishing state as observed**: the tree is tracked at
  `github.com/docxology/bond-casino_royale_1967` on `main`; the BOND suite copy at
  `projects/working/bond/casino_royale_1967` has no remote of its own. Nothing in `src/` should claim
  the module repository lacks its own remote.
