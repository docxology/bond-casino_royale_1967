# docs/ — Quick Navigation

**Casino Royale (1967) · FIVE 00s** — deterministic mission software for the
five-Bond farce, exposed through the FROZEN `bond_api` protocol.

- **New agent?** Start with [agent_instructions.md](agent_instructions.md).
- **Architecture?** See [architecture.md](architecture.md).
- **Testing?** See [testing_philosophy.md](testing_philosophy.md).

## Key entry points

| Path | Role |
|---|---|
| `src/casino_royale_1967/coordination_farce.py` | Five-Bond coordination-failure model |
| `src/casino_royale_1967/dispatch_chaos.py` | Dispatch chaos simulation |
| `src/casino_royale_1967/spoof_analyzer.py` | Spoof protocol analyzer |
| `src/casino_royale_1967/mission.py` | `bond_api` `MissionProvider` adapter |
| `src/casino_royale_1967/manuscript_variables.py` | Live `{{TOKEN}}` hydration |
| `scripts/mission.py` | brief/recon/plan/execute/debrief/figures CLIs |
| `scripts/z_generate_manuscript_variables.py` | tokens + resolved manuscript |
| `manuscript/` | the FIVE 00s manuscript |

## Quick start

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/mission.py execute
uv run python scripts/mission.py figures
uv run python scripts/z_generate_manuscript_variables.py
```
