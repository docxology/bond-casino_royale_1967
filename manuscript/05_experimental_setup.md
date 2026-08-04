# Experimental Setup

## Configuration

All identity and experiment parameters are declared in
`manuscript/config.yaml` and injected as tokens by
`src/casino_royale_1967/manuscript_variables.py` — never hard-coded in prose.

| Parameter | Value |
|---|---|
| Mission identity | {{BOND_IDENTITY}} |
| Mission codename | {{BOND_CODENAME}} |
| Package version | {{BOND_VERSION}} |
| Number of agents | {{CONFIG_NUM_AGENTS}} |
| Number of tasks | {{CONFIG_NUM_TASKS}} |
| Overlap loss weight | {{CONFIG_OVERLAP_WEIGHT}} |
| Conflict loss weight | {{CONFIG_CONFLICT_WEIGHT}} |
| Dispatch horizon (ticks) | {{CONFIG_MAX_TICKS}} |

## Software environment

- Python {{PYTHON_VERSION}}
- numpy and matplotlib for computation and rendering
- `bond-api` (frozen `MissionProvider` protocol, local path dependency)
- Deterministic seed 7; no random draws, no wall clock in artifacts.

## Artifact regeneration

Every artifact is regenerable from `scripts/`:

```bash
uv run python scripts/mission.py execute   # mission outcome (deterministic JSON)
uv run python scripts/mission.py figures   # the three concept figures
uv run python scripts/z_generate_manuscript_variables.py  # tokens + resolved tree
```
