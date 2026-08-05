# docs/AGENTS.md — working inside FIVE 00s

How an agent should operate in the **Casino Royale (1967) · FIVE 00s** package.
This file is the hub; the rules themselves live in the documents it points to.

## Reading order

1. **[agent_instructions.md](agent_instructions.md)** — the ten hard rules.
   Read before touching any file; they override convenience.
2. **[architecture.md](architecture.md)** — layer boundaries, what each module
   computes, and the frozen `MissionProvider` contract. Read before modifying
   `src/` or `scripts/`.
3. **[testing_philosophy.md](testing_philosophy.md)** — the zero-mock doctrine,
   the three manuscript gates, and the positive-control discipline. Read before
   writing or editing any test.
4. **[README.md](README.md)** — the map of what lives where, if you need to
   find a module by what it computes.

## The five things most likely to trip you up

1. **`mission.py`'s public shape is frozen.** `MissionProvider`, the five
   stage methods, `GADGETS`, `GADGET_REGISTRY` and `register_gadgets` are
   consumed by `bond-cli`, the coordinator and the orchestrator across all 33
   BOND packages. Deepen inside the stages; never change their shape.
2. **Only `mission.py` may import `bond_api`.** The domain core must stay
   importable without it — enforced, with a positive control, by
   `tests/test_layer_contract.py`. Adding a domain module means adding it to
   that test's `DOMAIN_MODULES`.
3. **No number goes into the manuscript by hand.** Add the variable to
   `manuscript_variables.py`, then reference the token. Unused tokens and bare
   numerals in results prose both fail the suite.
4. **`output/` is disposable.** Regenerate it with
   `scripts/z_generate_manuscript_variables.py`; never hand-edit an artifact to
   make a gate pass.
5. **Don't quote a coverage number in prose.** Docs are not regenerated, so a
   pasted figure goes stale silently. Name the gate (≥90% line+branch on
   `src/`) and let anyone who wants the current number run it.

## The gate

```bash
uv sync --extra dev
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/ && uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

Supplementary contract checks:

```bash
# no mock framework anywhere in the suite
grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
# no forbidden imports in the domain core
grep -rnE "^(from|import) (infrastructure|bond_api)" \
  src/casino_royale_1967/*.py | grep -v "^src/casino_royale_1967/mission.py" \
  || echo Clean
# no exemplar lineage strings left in code
rg -n "template[_]code_project" . --glob '!uv.lock' --glob '!.git/**' || echo Clean
```

Under a restrictive sandbox `uv` cannot write its cache; a `Failed to
initialize cache` error is an environment restriction, not a package failure.
Re-run with the sandbox disabled.

## Scope boundary

This package is local-only and has no remote. Work stays inside
`projects/working/bond/casino_royale_1967/` — never a sibling BOND package,
never the bond root files, never the template repo. Commit here, push nowhere.
