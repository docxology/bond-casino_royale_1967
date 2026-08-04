# docs/ — Agent-Facing Documentation Hub (FIVE 00s)

Operational rulebook for AI agents and developers working inside the
**Casino Royale (1967) · FIVE 00s** package.

| File | Purpose |
|---|---|
| `README.md` | Quick navigation and entry points |
| `AGENTS.md` | This index |
| `agent_instructions.md` | Behavioral constraints (read-first priority) |
| `architecture.md` | Layer boundaries and how-to-add-concept |
| `testing_philosophy.md` | Zero-mock policy and coverage mechanics |

## Reading order

1. `agent_instructions.md` — the rules of the road before touching any file.
2. `architecture.md` — layer boundaries before modifying `src/` or `scripts/`.
3. `testing_philosophy.md` — before writing or editing any `pytest` file.

## Verification commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 -q
grep -r "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
grep -rnE "^(from|import) infrastructure" src/casino_royale_1967/ || echo Clean
```
