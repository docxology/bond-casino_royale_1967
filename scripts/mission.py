#!/usr/bin/env python3
"""FIVE 00s — mission phase CLIs (brief/recon/plan/execute/debrief/figures).

Each script is a thin orchestrator: it drives one stage of the FROZEN
``bond_api`` mission lifecycle through the package's ``MissionProvider`` and
prints the stage payload as deterministic JSON. Business logic lives in
``src/``; these wrappers only bind the adapter and format output.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))  # noqa: E402
sys.path.insert(0, str(_PROJECT_ROOT))  # noqa: E402

from casino_royale_1967.mission import MissionProvider  # noqa: E402

_PROVIDER = MissionProvider()


def _emit(payload: object) -> int:
    """Print a JSON-serialisable stage payload (deterministic ordering)."""
    print(json.dumps(payload, sort_keys=True, indent=2, default=str))
    return 0


def run_brief() -> int:
    brief = _PROVIDER.brief()
    return _emit(
        {
            "film": brief.film,
            "codename": brief.codename,
            "objectives": list(brief.objectives),
            "assets": [{"kind": a.kind, "name": a.name, "payload": a.payload} for a in brief.assets],
            "constraints": [{"kind": c.kind, "detail": c.detail} for c in brief.constraints],
        }
    )


def run_recon() -> int:
    from bond_api.protocol import ReconRequest

    report = _PROVIDER.recon(ReconRequest(goal="characterize the five-Bond farce"))
    return _emit(
        {
            "goal": "characterize the five-Bond farce",
            "findings": [{"label": f.label, "detail": f.detail} for f in report.findings],
        }
    )


def run_plan() -> int:
    plan = _PROVIDER.plan(_PROVIDER.brief())
    return _emit({"steps": [{"name": s.name, "action": s.action, "params": s.params} for s in plan.steps]})


def run_execute() -> int:
    outcome = _PROVIDER.execute(_PROVIDER.plan(_PROVIDER.brief()))
    return _emit(
        {
            "success": outcome.success,
            "provenance": {
                "package_version": outcome.provenance.package_version,
                "seed": outcome.provenance.seed,
                "input_hash": outcome.provenance.input_hash,
                "wall_time_s": outcome.provenance.wall_time_s,
            },
            "results": outcome.results,
        }
    )


def run_debrief() -> int:
    from bond_api.protocol import ReconRequest

    request = ReconRequest(goal="characterize the five-Bond farce")
    debrief = _PROVIDER.debrief(_PROVIDER.execute(_PROVIDER.plan(_PROVIDER.brief())))
    return _emit(
        {
            "success": debrief.outcome.success,
            "lessons": list(debrief.lessons),
            "recon_findings": [{"label": f.label, "detail": f.detail} for f in _PROVIDER.recon(request).findings],
        }
    )


def run_figures() -> int:
    from casino_royale_1967.figures.plots import render_all_figures

    paths = render_all_figures(_PROJECT_ROOT / "output" / "figures")
    return _emit({name: str(path) for name, path in paths.items()})


_COMMANDS: dict[str, object] = {
    "brief": run_brief,
    "recon": run_recon,
    "plan": run_plan,
    "execute": run_execute,
    "debrief": run_debrief,
    "figures": run_figures,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in _COMMANDS:
        print(f"usage: python {Path(sys.argv[0]).name} <{'|'.join(_COMMANDS)}>")
        return 2
    return int(_COMMANDS[sys.argv[1]]())  # type: ignore[operator]


if __name__ == "__main__":
    raise SystemExit(main())
