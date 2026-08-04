"""Agent dispatch chaos simulation (Casino Royale, 1967).

The dispatch centre has five agents who all answer to *James Bond*, a task
catalog with exclusivity and clearance requirements, and a stream of orders.
Chaos ensues: duplicate agents pile onto the same exclusive task, agents are
double-booked across simultaneous orders, the under-cleared nephew is sent to
defuse the gamma-ray projector, and the same order id is issued twice.

This module simulates dispatch deterministically:

* :class:`DispatchOrder` — an order issued at a tick with a priority;
* :func:`simulate_dispatch` — a tick-based scheduler (no RNG, no wall clock)
  that applies five protocol rules per order:
  ``exclusive_task``, ``duplicate_codename``, ``clearance``,
  ``double_booking``, ``duplicate_order``;
* :class:`DispatchReport` — accepted/rejected counts, every violation with
  the rule that fired, per-order delay, success ratio, and a chaos index
  (violations per order, normalised to ``[0, 1]``), plus a tick-by-tick
  event timeline for visualisation.

Orders are processed in ``issued_tick`` order; within a tick, higher priority
first, ties broken by order id. A rejected order is *not* retried — the whole
point of the model is that a chaotic dispatch centre loses orders.

Pure domain logic: stdlib only, no ``infrastructure`` / ``bond_api`` imports.
"""

from __future__ import annotations

from dataclasses import dataclass

from casino_royale_1967.coordination_farce import AGENT_BY_ID, TASK_BY_ID

__all__ = [
    "CHAOS_ORDERS",
    "DispatchEvent",
    "DispatchOrder",
    "DispatchReport",
    "DispatchViolation",
    "PROTOCOL_RULES",
    "simulate_dispatch",
]

# The five protocol rules the dispatch centre is supposed to enforce.
PROTOCOL_RULES: tuple[str, ...] = (
    "exclusive_task",
    "duplicate_codename",
    "clearance",
    "double_booking",
    "duplicate_order",
)


@dataclass(frozen=True)
class DispatchOrder:
    """A single dispatch order issued at a tick."""

    order_id: str
    agent_id: str
    task_id: str
    priority: int = 1
    issued_tick: int = 0


@dataclass(frozen=True)
class DispatchViolation:
    """A protocol violation recorded while processing an order."""

    tick: int
    order_id: str
    agent_id: str
    task_id: str
    rule: str
    detail: str


@dataclass(frozen=True)
class DispatchEvent:
    """One entry of the deterministic event timeline (for figures/reports)."""

    tick: int
    event_type: str  # "dispatch" | "violation"
    order_id: str
    agent_id: str
    task_id: str
    rule: str = ""


@dataclass(frozen=True)
class DispatchReport:
    """Deterministic outcome of :func:`simulate_dispatch`."""

    total_orders: int
    dispatched: int
    rejected: int
    violations: tuple[DispatchViolation, ...]
    duplicate_dispatches: int  # orders rejected as duplicates of an earlier id
    mean_delay: float  # ticks between issue and dispatch (0 in the reject model)
    success_ratio: float  # dispatched / total_orders
    chaos_index: float  # violations / total_orders, in [0, 1]
    events: tuple[DispatchEvent, ...]


# The canonical chaos scenario: engineered to fire every protocol rule.
# 13 orders over ticks 0..4 across the five Bonds.
CHAOS_ORDERS: tuple[DispatchOrder, ...] = (
    DispatchOrder("o01", "bond_tremble", "baccarat", priority=3, issued_tick=0),
    DispatchOrder("o02", "bond_sir", "baccarat", priority=2, issued_tick=0),
    DispatchOrder("o03", "bond_vesper", "baccarat", priority=1, issued_tick=0),
    DispatchOrder("o04", "bond_cooper", "burn_baccarat", priority=2, issued_tick=1),
    DispatchOrder("o05", "bond_vesper", "smersh_hq", priority=2, issued_tick=1),
    DispatchOrder("o06", "bond_vesper", "mata_bond", priority=3, issued_tick=1),
    DispatchOrder("o07", "bond_jimmy", "gamma_ray", priority=1, issued_tick=2),
    DispatchOrder("o08", "bond_sir", "gamma_ray", priority=3, issued_tick=2),
    DispatchOrder("o09", "bond_sir", "mata_bond", priority=2, issued_tick=2),
    DispatchOrder("o01", "bond_tremble", "baccarat", priority=3, issued_tick=3),
    DispatchOrder("o11", "bond_cooper", "mata_bond", priority=1, issued_tick=3),
    DispatchOrder("o12", "bond_jimmy", "casino_vault", priority=1, issued_tick=3),
    DispatchOrder("o13", "bond_sir", "smersh_hq", priority=2, issued_tick=4),
)


def _order_sort_key(order: DispatchOrder) -> tuple[int, str]:
    """Deterministic dispatch order: priority desc, then order id asc."""
    return (-order.priority, order.order_id)


def simulate_dispatch(
    orders: tuple[DispatchOrder, ...] = CHAOS_ORDERS,
    *,
    max_ticks: int = 100,
) -> DispatchReport:
    """Run the tick-based dispatch simulation against the protocol rules.

    State per tick: agents already committed this tick (double-booking guard)
    and agents committed to each task so far (exclusive/codename guards).
    Orders issued at the same tick are processed by
    ``(priority desc, order_id asc)``; a rejected order is dropped, never
    requeued.

    Args:
        orders: the order stream (default: the canonical chaos scenario).
        max_ticks: simulation horizon; orders past it are ignored.

    Returns:
        A frozen :class:`DispatchReport`.

    Raises:
        ValueError: if any order references an unknown agent or task, or has a
            non-positive priority.
    """
    by_tick: dict[int, list[DispatchOrder]] = {}
    for order in orders:
        if order.agent_id not in AGENT_BY_ID:
            raise ValueError(f"unknown agent id {order.agent_id!r}")
        if order.task_id not in TASK_BY_ID:
            raise ValueError(f"unknown task id {order.task_id!r}")
        if order.priority <= 0:
            raise ValueError(f"order {order.order_id!r} priority must be > 0")
        if order.issued_tick < 0:
            raise ValueError(f"order {order.order_id!r} issued_tick must be >= 0")
        by_tick.setdefault(order.issued_tick, []).append(order)

    seen_order_ids: set[str] = set()
    # Agents committed to a task so far (persistent task occupancy).
    task_occupants: dict[str, set[str]] = {}
    # Agents committed to a task *this tick* (double-booking guard).
    tick_committed: set[str] = set()

    dispatched: int = 0
    rejected: int = 0
    duplicate_dispatches: int = 0
    violations: list[DispatchViolation] = []
    events: list[DispatchEvent] = []

    for tick in range(max_ticks + 1):
        tick_orders = sorted(by_tick.get(tick, ()), key=_order_sort_key)
        if not tick_orders:
            continue
        tick_committed = set()
        for order in tick_orders:
            agent = AGENT_BY_ID[order.agent_id]
            task = TASK_BY_ID[order.task_id]
            rule: str | None = None
            detail = ""

            if order.order_id in seen_order_ids:
                rule = "duplicate_order"
                detail = f"order id {order.order_id!r} issued twice"
                duplicate_dispatches += 1
            elif task.exclusive and order.task_id in task_occupants:
                rule = "exclusive_task"
                detail = f"task {order.task_id!r} is exclusive and already occupied"
            elif agent.clearance < task.required_clearance:
                rule = "clearance"
                detail = f"agent clearance {agent.clearance} < required {task.required_clearance}"
            elif order.agent_id in tick_committed:
                rule = "double_booking"
                detail = f"agent {order.agent_id!r} already committed this tick"
            elif (
                not task.exclusive
                and task_occupants.get(order.task_id)
                and any(AGENT_BY_ID[occupant].codename == agent.codename for occupant in task_occupants[order.task_id])
            ):
                rule = "duplicate_codename"
                detail = f"codename {agent.codename!r} already on task {order.task_id!r}"

            if rule is not None:
                rejected += 1
                violations.append(
                    DispatchViolation(
                        tick=tick,
                        order_id=order.order_id,
                        agent_id=order.agent_id,
                        task_id=order.task_id,
                        rule=rule,
                        detail=detail,
                    )
                )
                events.append(
                    DispatchEvent(
                        tick=tick,
                        event_type="violation",
                        order_id=order.order_id,
                        agent_id=order.agent_id,
                        task_id=order.task_id,
                        rule=rule,
                    )
                )
                continue

            dispatched += 1
            seen_order_ids.add(order.order_id)
            tick_committed.add(order.agent_id)
            task_occupants.setdefault(order.task_id, set()).add(order.agent_id)
            events.append(
                DispatchEvent(
                    tick=tick,
                    event_type="dispatch",
                    order_id=order.order_id,
                    agent_id=order.agent_id,
                    task_id=order.task_id,
                )
            )

    total = len(orders)
    success_ratio = dispatched / total if total else 0.0
    chaos_index = len(violations) / total if total else 0.0
    # Reject model: every accepted order dispatches in its issue tick.
    mean_delay = 0.0

    return DispatchReport(
        total_orders=total,
        dispatched=dispatched,
        rejected=rejected,
        violations=tuple(violations),
        duplicate_dispatches=duplicate_dispatches,
        mean_delay=mean_delay,
        success_ratio=success_ratio,
        chaos_index=chaos_index,
        events=tuple(events),
    )
