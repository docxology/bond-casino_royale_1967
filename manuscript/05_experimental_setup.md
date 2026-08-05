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
| Dispatch protocol rules enforced | {{CONFIG_PROTOCOL_RULES}} |
| Sane ops rules in the doctrine baseline | {{CONFIG_DOCTRINE_RULES}} |
| Escalation-ladder states | {{CONFIG_LADDER_STATES}} |
| Casino table (Bonds seated) | {{CONFIG_TABLE_BONDS}} |
| Figures rendered | {{CONFIG_NUM_FIGURES}} |

Values in this table are read from `manuscript/config.yaml` where the
parameter is a free choice (loss weights, dispatch horizon) and derived from
the domain modules where the parameter is structural (rule counts, ladder
size, figure count), so neither source can drift from the code.

## Software environment

- Python `{{PYTHON_REQUIRES}}` — the declared supported range. The artifacts do
  not record which interpreter within that range produced them, which is what
  keeps them byte-identical across it.
- numpy and matplotlib for computation and rendering
- `bond-api` (frozen `MissionProvider` protocol, local path dependency)
- Deterministic seed 7; no random draws, no wall clock in artifacts.

## Artifact regeneration

Every artifact is regenerable from `scripts/`:

```bash
uv run python scripts/mission.py execute   # mission outcome (deterministic JSON)
uv run python scripts/mission.py figures   # the concept figures
uv run python scripts/z_generate_manuscript_variables.py  # tokens + resolved tree
```

The last command is the authoritative one: it recomputes the token map,
re-renders every figure, and rewrites `output/manuscript/` with every token
marker resolved, failing loudly if any marker is unresolvable.
