"""Coordination-failure model for the five-Bond farce (Casino Royale, 1967).

The film's premise is an organizational failure: SMERSH has eliminated every
active double-0, so British Intelligence reactivates Sir James Bond and then
deploys *five* operatives who all answer to the codename *James Bond* —
overlapping identities, overlapping assignments, and contradictory orders.

This module models that farce deterministically:

* a roster of five agents (all codename ``James Bond``, with the actor who
  played them and a clearance level);
* a task catalog drawn from the film's plot (baccarat championship, SMERSH
  headquarters, the casino vault, Mata Bond, the gamma-ray projector);
* a conflict graph of mutually exclusive task pairs (e.g. *win the baccarat
  championship* vs. *burn the baccarat table*);
* :func:`analyze_assignments` — overlap detection (more than one agent on a
  task), conflict detection (agents on conflicting task pairs), clearance
  violations, and a weighted coordination loss;
* :func:`deduplicate_assignments` — the deterministic single-agent discipline:
  keep the highest-priority assignment per task, retire the overlap victims.

Pure domain logic: stdlib + no ``infrastructure`` imports, no ``bond_api``
imports. Deterministic by construction (no RNG, no wall clock).
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "AGENT_ROSTER",
    "AGENT_BY_ID",
    "Assignment",
    "CONFLICT_GRAPH",
    "DEFAULT_ASSIGNMENTS",
    "DedupResult",
    "TASK_CATALOG",
    "TASK_BY_ID",
    "Agent",
    "CoordinationReport",
    "Task",
    "analyze_assignments",
    "deduplicate_assignments",
]

# ---------------------------------------------------------------------------
# Domain data — the five Bonds of Casino Royale (1967)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Agent:
    """One operative on the FIVE 00s roster.

    Every member of the roster answers to the codename *James Bond* — that is
    the organizational failure being modelled: the dispatch centre cannot tell
    its agents apart.
    """

    agent_id: str
    alias: str  # the actor who played this Bond
    codename: str
    clearance: int  # 1 (untrained) .. 5 (Sir James himself)
    jurisdiction: str  # nominal speciality


@dataclass(frozen=True)
class Task:
    """A single operation from the film's plot."""

    task_id: str
    description: str
    required_clearance: int
    exclusive: bool  # True => exactly one agent may be assigned


@dataclass(frozen=True)
class Assignment:
    """An agent assigned to a task, with a priority (higher dispatches first)."""

    agent_id: str
    task_id: str
    priority: int = 1


# The five Bonds. All share codename "James Bond" — duplicates by design.
AGENT_ROSTER: tuple[Agent, ...] = (
    Agent(
        agent_id="bond_sir",
        alias="David Niven",
        codename="James Bond",
        clearance=5,
        jurisdiction="diplomacy",
    ),
    Agent(
        agent_id="bond_tremble",
        alias="Peter Sellers",
        codename="James Bond",
        clearance=3,
        jurisdiction="gambling",
    ),
    Agent(
        agent_id="bond_vesper",
        alias="Ursula Andress",
        codename="James Bond",
        clearance=4,
        jurisdiction="seduction",
    ),
    Agent(
        agent_id="bond_jimmy",
        alias="Woody Allen",
        codename="James Bond",
        clearance=2,
        jurisdiction="accounting",
    ),
    Agent(
        agent_id="bond_cooper",
        alias="Terence Cooper",
        codename="James Bond",
        clearance=4,
        jurisdiction="field ops",
    ),
)

TASK_CATALOG: tuple[Task, ...] = (
    Task(
        task_id="baccarat",
        description="win the baccarat championship",
        required_clearance=3,
        exclusive=True,
    ),
    Task(
        task_id="burn_baccarat",
        description="burn the baccarat table for the insurance claim",
        required_clearance=2,
        exclusive=True,
    ),
    Task(
        task_id="smersh_hq",
        description="infiltrate SMERSH headquarters",
        required_clearance=4,
        exclusive=False,
    ),
    Task(
        task_id="casino_vault",
        description="guard the casino vault",
        required_clearance=3,
        exclusive=False,
    ),
    Task(
        task_id="mata_bond",
        description="seduce Mata Bond for intelligence",
        required_clearance=3,
        exclusive=False,
    ),
    Task(
        task_id="gamma_ray",
        description="disable the gamma-ray projector",
        required_clearance=5,
        exclusive=False,
    ),
)

# Mutually exclusive task pairs: assigning agents to both is a conflict.
CONFLICT_GRAPH: frozenset[frozenset[str]] = frozenset((frozenset(("baccarat", "burn_baccarat")),))

AGENT_BY_ID: dict[str, Agent] = {agent.agent_id: agent for agent in AGENT_ROSTER}
TASK_BY_ID: dict[str, Task] = {task.task_id: task for task in TASK_CATALOG}

# The farcical default: Sir James and two more Bonds all at the baccarat
# table, Cooper burning the same table, Vesper and Jimmy both at SMERSH HQ,
# and Jimmy under-cleared for everything he touches.
DEFAULT_ASSIGNMENTS: tuple[Assignment, ...] = (
    Assignment("bond_tremble", "baccarat", priority=3),
    Assignment("bond_sir", "baccarat", priority=2),
    Assignment("bond_vesper", "baccarat", priority=1),
    Assignment("bond_cooper", "burn_baccarat", priority=2),
    Assignment("bond_vesper", "smersh_hq", priority=2),
    Assignment("bond_jimmy", "smersh_hq", priority=1),
    Assignment("bond_sir", "gamma_ray", priority=1),
    Assignment("bond_cooper", "mata_bond", priority=1),
)

# Default loss weights (documented in manuscript/config.yaml).
OVERLAP_WEIGHT = 2.0
CONFLICT_WEIGHT = 3.0


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CoordinationReport:
    """Deterministic outcome of :func:`analyze_assignments`."""

    total_assignments: int
    overlap_count: int
    conflict_count: int
    clearance_violations: tuple[Assignment, ...]
    loss: float
    per_task_load: dict[str, int]
    overlap_victims: dict[str, tuple[str, ...]]  # task_id -> extra agent ids


def _validate_known_ids(assignments: tuple[Assignment, ...]) -> None:
    """Raise ValueError on unknown agent/task ids (fail loud, never guess)."""
    for assignment in assignments:
        if assignment.agent_id not in AGENT_BY_ID:
            raise ValueError(f"unknown agent id {assignment.agent_id!r}")
        if assignment.task_id not in TASK_BY_ID:
            raise ValueError(f"unknown task id {assignment.task_id!r}")


def analyze_assignments(
    assignments: tuple[Assignment, ...],
    *,
    overlap_weight: float = OVERLAP_WEIGHT,
    conflict_weight: float = CONFLICT_WEIGHT,
    conflict_graph: frozenset[frozenset[str]] = CONFLICT_GRAPH,
) -> CoordinationReport:
    """Analyze an assignment set for overlap, conflict, and clearance failures.

    Overlap: every extra agent beyond the first on a task counts once
    (``n_agents - 1`` per task). Conflict: every unordered pair of *distinct*
    agents assigned to a conflicting task pair counts once. Clearance
    violations are reported but not double-counted in the loss.

    Args:
        assignments: the assignment set to analyze (deterministic order).
        overlap_weight: loss weight per overlapping extra agent.
        conflict_weight: loss weight per conflicting agent pair.
        conflict_graph: set of mutually exclusive task-id pairs.

    Returns:
        A frozen :class:`CoordinationReport`.

    Raises:
        ValueError: if any assignment references an unknown agent or task, or
            if a conflict-graph entry does not name exactly two tasks.
    """
    _validate_known_ids(assignments)

    per_task: dict[str, list[str]] = {}
    for assignment in assignments:
        per_task.setdefault(assignment.task_id, []).append(assignment.agent_id)

    overlap_count = 0
    overlap_victims: dict[str, tuple[str, ...]] = {}
    for task_id, agent_ids in sorted(per_task.items()):
        distinct = sorted(set(agent_ids))
        extras = len(distinct) - 1
        if extras > 0:
            overlap_count += extras
            # The victims: every agent beyond the first, in stable order.
            overlap_victims[task_id] = tuple(distinct[1:])

    conflict_count = 0
    for pair in sorted(tuple(sorted(p)) for p in conflict_graph):
        if len(pair) != 2:
            raise ValueError(f"conflict graph entry {pair!r} must name exactly two tasks")
        task_a, task_b = pair
        agents_a = set(per_task.get(task_a, ()))
        agents_b = set(per_task.get(task_b, ()))
        # Pairs of *distinct* agents across the two conflicting tasks. One
        # agent holding both sides of a conflict is a single-agent scheduling
        # problem, not an inter-agent conflict, so it must not be counted.
        conflict_count += sum(1 for a in agents_a for b in agents_b if a != b)

    clearance_violations = tuple(
        assignment
        for assignment in assignments
        if AGENT_BY_ID[assignment.agent_id].clearance < TASK_BY_ID[assignment.task_id].required_clearance
    )

    loss = overlap_weight * overlap_count + conflict_weight * conflict_count
    per_task_load = {task_id: len(agents) for task_id, agents in sorted(per_task.items())}

    return CoordinationReport(
        total_assignments=len(assignments),
        overlap_count=overlap_count,
        conflict_count=conflict_count,
        clearance_violations=clearance_violations,
        loss=loss,
        per_task_load=per_task_load,
        overlap_victims=overlap_victims,
    )


@dataclass(frozen=True)
class DedupResult:
    """Outcome of the deterministic single-agent discipline."""

    kept: tuple[Assignment, ...]
    dropped: tuple[Assignment, ...]
    dropped_by_task: dict[str, tuple[str, ...]]


def deduplicate_assignments(
    assignments: tuple[Assignment, ...],
) -> DedupResult:
    """Keep the highest-priority assignment per task; retire the rest.

    The farce's antidote: one agent per task, chosen by the lexicographic
    maximum of ``(priority, agent_id)`` — highest priority wins, and an exact
    tie is broken by the *greatest* agent id, which makes the choice a pure
    function of the input set regardless of assignment order. Retired
    assignments are the overlap victims — the Bonds who showed up to a party
    already attended.

    Args:
        assignments: the assignment set (unknown ids raise ``ValueError``).

    Returns:
        A frozen :class:`DedupResult` with kept and dropped assignments.

    Raises:
        ValueError: if any assignment references an unknown agent or task.
    """
    _validate_known_ids(assignments)

    best: dict[str, Assignment] = {}
    for assignment in assignments:
        prior = best.get(assignment.task_id)
        if prior is None or (assignment.priority, assignment.agent_id) > (
            prior.priority,
            prior.agent_id,
        ):
            best[assignment.task_id] = assignment

    kept = tuple(best[task_id] for task_id in sorted(best))
    kept_ids = {(a.task_id, a.agent_id) for a in kept}
    dropped = tuple(a for a in assignments if (a.task_id, a.agent_id) not in kept_ids)

    dropped_by_task: dict[str, tuple[str, ...]] = {}
    for task_id in sorted({a.task_id for a in dropped}):
        dropped_by_task[task_id] = tuple(sorted(a.agent_id for a in dropped if a.task_id == task_id))

    return DedupResult(kept=kept, dropped=dropped, dropped_by_task=dropped_by_task)
