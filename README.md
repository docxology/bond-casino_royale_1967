# Casino Royale (1967) — FIVE 00s · Special-Agent Mission Software

A **PROJECT BOND** film package. The 1967 *Casino Royale* is the spy farce
in which five operatives all answer to the codename *James Bond* — a
coordiation catastrophe in the shape of a blockbuster. **FIVE 00s** models
that farce rigorously and deterministically, then exposes it through the
frozen `bond_api` mission protocol.

Local-only working tree inside the BOND suite
(`projects/working/bond/casino_royale_1967`): no remote, never pushed.

## Concepts

| Module | Concept |
|---|---|
| `src/casino_royale_1967/coordination_farce.py` | Five-Bond **coordination-failure model**: overlap + conflict detection, clearance violations, weighted loss, single-agent deduplication |
| `src/casino_royale_1967/dispatch_chaos.py` | **Dispatch chaos simulation**: tick-based dispatch centre enforcing five protocol rules (exclusive tasks, clearance, double-booking, duplicate orders, duplicate codenames) |
| `src/casino_royale_1967/spoof_analyzer.py` | **Spoof protocol analyzer**: lexical scoring of satirical ops doctrine against a sane protocol, with a normalised spoof index |
| `src/casino_royale_1967/mission.py` | Thin `bond_api` `MissionProvider` adapter (slug `casino_royale_1967`, codename **FIVE 00s**) + gadget registry |

All three domain modules are pure (stdlib + numpy only) and importable even
if the `bond-api` path dependency fails; `mission.py` is the only module that
constructs `bond_api` protocol types.

## Quick start

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format src/ scripts/
uv run mypy src/ scripts/
```

## Mission phases (thin CLIs)

```bash
uv run python scripts/mission.py brief     # mission brief (deterministic JSON)
uv run python scripts/mission.py recon     # reconnaissance findings
uv run python scripts/mission.py plan      # three-step plan
uv run python scripts/mission.py execute   # mission outcome + provenance
uv run python scripts/mission.py debrief   # lessons learned
uv run python scripts/mission.py figures   # render the three concept figures
uv run python scripts/z_generate_manuscript_variables.py  # tokens + resolved manuscript
```

## Determinism & quality

- Fixed seed 7; the dispatch simulation makes no random draws at all.
- Zero mocks — every test exercises real computation.
- ≥90% line+branch coverage on `src/` (canonical gate).
- Manuscript metrics are injected live from `manuscript/config.yaml` +
  `src/casino_royale_1967/manuscript_variables.py` — never hand-authored.

## Layout

- `src/casino_royale_1967/` — pure domain core + `mission.py` adapter + figures
- `scripts/` — thin mission-phase orchestrators
- `tests/` — per-module real-data tests + protocol/smoke/figure tests
- `manuscript/` — the FIVE 00s manuscript (tokens + figures)
- `data/` — claim ledger (see `data/claim_ledger.yaml`)
- `output/` — regenerable artifacts (git-ignored)

See [AGENTS.md](AGENTS.md) for the full package spec and
[TODO.md](TODO.md) for build state and integration points.
