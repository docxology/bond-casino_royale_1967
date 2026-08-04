"""FIVE 00s — the Casino Royale (1967) MissionProvider for BOND-API.

Thin adapter between the pure domain core (``coordination_farce``,
``dispatch_chaos``, ``spoof_analyzer``) and the FROZEN ``bond_api`` protocol.
Discovery contract: a top-level module named by slug exposing
``mission.MissionProvider`` (film slug ``casino_royale_1967``).

The three domain modules never import ``bond_api`` — they stay importable if
the path dependency fails; this module is the only place the protocol types
are constructed.

Gadgets (registered with :class:`bond_api.registry.GadgetRegistry`):

* ``roster`` — the five-Bond agent roster (JSON-safe dicts);
* ``coordination`` — the canonical coordination report;
* ``dispatch`` — the canonical dispatch report;
* ``doctrine`` — the canonical doctrine report.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from bond_api.protocol import (
    Asset,
    Constraint,
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    ReconRequest,
    Step,
)
from bond_api.registry import GadgetRegistry

from casino_royale_1967.coordination_farce import (
    AGENT_ROSTER,
    DEFAULT_ASSIGNMENTS,
    analyze_assignments,
    deduplicate_assignments,
)
from casino_royale_1967.dispatch_chaos import (
    CHAOS_ORDERS,
    DispatchViolation,
    simulate_dispatch,
)
from casino_royale_1967.spoof_analyzer import (
    CANONICAL_SPOOF_DOCTRINE,
    analyze_doctrine,
)

__all__ = [
    "GADGETS",
    "GADGET_REGISTRY",
    "MissionProvider",
    "PACKAGE_VERSION",
    "SEED",
    "register_gadgets",
]

PACKAGE_VERSION = "0.1.0"
SEED = 7
FILM = "casino_royale_1967"
CODENAME = "FIVE 00s"
IDENTITY = "Casino Royale (1967)"

_MISSION_OBJECTIVES: tuple[str, ...] = (
    "model coordination failure across the five overlapping Bonds",
    "simulate dispatch chaos and protocol violations deterministically",
    "analyze the spoof ops doctrine and quantify its deviation",
)


def _input_fingerprint() -> str:
    """Deterministic sha256 over the canonical mission inputs.

    Built from the default assignments, chaos orders, and spoof doctrine so
    outcome provenance can be audited without re-running the film.
    """
    payload = {
        "assignments": [(a.agent_id, a.task_id, a.priority) for a in DEFAULT_ASSIGNMENTS],
        "orders": [(o.order_id, o.agent_id, o.task_id, o.priority, o.issued_tick) for o in CHAOS_ORDERS],
        "doctrine": list(CANONICAL_SPOOF_DOCTRINE),
        "seed": SEED,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _coordination_payload() -> dict[str, Any]:
    """JSON-safe canonical coordination analysis (report + dedup)."""
    report = analyze_assignments(DEFAULT_ASSIGNMENTS)
    dedup = deduplicate_assignments(DEFAULT_ASSIGNMENTS)
    return {
        "total_assignments": report.total_assignments,
        "overlap_count": report.overlap_count,
        "conflict_count": report.conflict_count,
        "clearance_violations": [
            {
                "agent_id": a.agent_id,
                "task_id": a.task_id,
                "priority": a.priority,
            }
            for a in report.clearance_violations
        ],
        "loss": report.loss,
        "per_task_load": report.per_task_load,
        "overlap_victims": report.overlap_victims,
        "dedup_kept": [{"agent_id": a.agent_id, "task_id": a.task_id, "priority": a.priority} for a in dedup.kept],
        "dedup_dropped": [
            {"agent_id": a.agent_id, "task_id": a.task_id, "priority": a.priority} for a in dedup.dropped
        ],
    }


def _dispatch_payload() -> dict[str, Any]:
    """JSON-safe canonical dispatch-chaos analysis."""
    report = simulate_dispatch(CHAOS_ORDERS)
    return {
        "total_orders": report.total_orders,
        "dispatched": report.dispatched,
        "rejected": report.rejected,
        "violations": [
            {
                "tick": v.tick,
                "order_id": v.order_id,
                "agent_id": v.agent_id,
                "task_id": v.task_id,
                "rule": v.rule,
                "detail": v.detail,
            }
            for v in report.violations
        ],
        "duplicate_dispatches": report.duplicate_dispatches,
        "mean_delay": report.mean_delay,
        "success_ratio": report.success_ratio,
        "chaos_index": report.chaos_index,
        "rule_counts": _rule_counts(report.violations),
    }


def _rule_counts(
    violations: tuple[DispatchViolation, ...],
) -> dict[str, int]:
    """Count violations per protocol rule, in protocol order."""
    counts: dict[str, int] = {}
    for violation in violations:
        counts[violation.rule] = counts.get(violation.rule, 0) + 1
    return counts


def _doctrine_payload() -> dict[str, Any]:
    """JSON-safe canonical spoof-doctrine analysis."""
    report = analyze_doctrine(CANONICAL_SPOOF_DOCTRINE)
    return {
        "directive_count": report.directive_count,
        "total_score": report.total_score,
        "mean_score": report.mean_score,
        "spoof_index": report.spoof_index,
        "worst_directive": report.worst_directive,
        "rule_violation_counts": report.rule_violation_counts,
        "verdicts": [
            {
                "text": v.text,
                "spoof_score": v.spoof_score,
                "inverted_rules": list(v.inverted_rules),
                "oxymorons": [list(pair) for pair in v.oxymorons],
                "flags": list(v.flags),
            }
            for v in report.verdicts
        ],
    }


GADGETS: dict[str, Any] = {
    "roster": [
        {
            "agent_id": agent.agent_id,
            "alias": agent.alias,
            "codename": agent.codename,
            "clearance": agent.clearance,
            "jurisdiction": agent.jurisdiction,
        }
        for agent in AGENT_ROSTER
    ],
    "coordination": _coordination_payload(),
    "dispatch": _dispatch_payload(),
    "doctrine": _doctrine_payload(),
}


def register_gadgets(registry: GadgetRegistry | None = None) -> GadgetRegistry:
    """Register the film's gadgets with a :class:`GadgetRegistry`.

    Args:
        registry: the registry to populate (a fresh one when ``None``).

    Returns:
        The populated registry (same instance when one was passed).
    """
    target = registry if registry is not None else GadgetRegistry()
    target.register(FILM, GADGETS)
    return target


#: Module-level registry populated at import time — coordinators that only
#: ``load_provider`` still find the film's gadgets here.
GADGET_REGISTRY: GadgetRegistry = register_gadgets()


class MissionProvider:  # noqa: N801 — class name fixed by the discovery contract
    """Deterministic BOND-API mission provider for Casino Royale (1967).

    Every stage is pure: the analyses run on the canonical inputs with no RNG
    and no wall clock, so ``brief -> recon -> plan -> execute -> debrief`` is
    byte-reproducible.
    """

    film = FILM

    def brief(self) -> MissionBrief:
        """Declare the FIVE 00s mission: three objectives, two assets."""
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=_MISSION_OBJECTIVES,
            assets=(
                Asset(
                    kind="manifest",
                    name="five_bonds_roster",
                    payload={
                        "agents": len(AGENT_ROSTER),
                        "codename": "James Bond",
                    },
                ),
                Asset(
                    kind="doctrine",
                    name="spoof_ops_doctrine",
                    payload={
                        "directives": len(CANONICAL_SPOOF_DOCTRINE),
                        "source": "Casino Royale (1967) standing orders",
                    },
                ),
            ),
            constraints=(
                Constraint(
                    kind="determinism",
                    detail="fixed seed, no random draws, no wall clock in artifacts",
                ),
                Constraint(
                    kind="protocol",
                    detail="FROZEN bond_api surface; domain core stays bond_api-free",
                ),
            ),
        )

    def recon(self, request: ReconRequest) -> ReconReport:
        """Survey the goal and the three concept analyses."""
        coordination = analyze_assignments(DEFAULT_ASSIGNMENTS)
        dispatch = simulate_dispatch(CHAOS_ORDERS)
        doctrine = analyze_doctrine(CANONICAL_SPOOF_DOCTRINE)
        return ReconReport(
            findings=(
                Finding(label="goal", detail=request.goal),
                Finding(
                    label="overlap",
                    detail=f"{coordination.overlap_count} overlapping assignments",
                ),
                Finding(
                    label="conflict",
                    detail=f"{coordination.conflict_count} conflicting agent pairs",
                ),
                Finding(
                    label="dispatch",
                    detail=(f"{dispatch.rejected} of {dispatch.total_orders} orders rejected by protocol"),
                ),
                Finding(
                    label="doctrine",
                    detail=f"spoof index {doctrine.spoof_index:.1f} / 100",
                ),
            )
        )

    def plan(self, brief: MissionBrief) -> MissionPlan:
        """Plan the three deterministic steps, one per concept module."""
        return MissionPlan(
            steps=(
                Step(
                    name="coordination",
                    action="analyze_assignments",
                    params={"assignments": brief.assets[0].name},
                ),
                Step(
                    name="dispatch",
                    action="simulate_dispatch",
                    params={"orders": "canonical chaos scenario"},
                ),
                Step(
                    name="doctrine",
                    action="analyze_doctrine",
                    params={"directives": brief.assets[1].name},
                ),
            )
        )

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        """Run the plan's three analyses and return a deterministic outcome."""
        steps_completed = tuple(step.name for step in plan.steps)
        results: dict[str, Any] = {
            "steps_completed": steps_completed,
            "coordination": _coordination_payload(),
            "dispatch": _dispatch_payload(),
            "doctrine": _doctrine_payload(),
        }
        return MissionOutcome(
            success=True,
            results=results,
            provenance=Provenance(
                package_version=PACKAGE_VERSION,
                seed=SEED,
                input_hash=_input_fingerprint(),
                wall_time_s=0.0,
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        """Summarize the mission and record the farce's standing lessons."""
        coordination = outcome.results["coordination"]
        dispatch = outcome.results["dispatch"]
        doctrine = outcome.results["doctrine"]
        return Debrief(
            outcome=outcome,
            lessons=(
                "five agents sharing one codename guarantees overlap loss",
                f"coordination loss stays {coordination['loss']} until discipline",
                f"dispatch protocol rejected {dispatch['rejected']} of {dispatch['total_orders']} orders",
                "single-agent discipline removes every overlap",
                f"the spoof doctrine scores {doctrine['spoof_index']} / 100",
            ),
        )
