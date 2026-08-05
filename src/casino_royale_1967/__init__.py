"""Casino Royale (1967) — FIVE 00s mission software.

Public API surface: the six pure domain modules, the mission adapter, and
the manuscript-variable generator.

**Layer contract.** The six domain modules import stdlib + numpy only. The
protocol adapter (:mod:`casino_royale_1967.mission`) is the single module that
imports ``bond_api``, and it is loaded **lazily** through the module-level
``__getattr__`` below. Importing the domain core therefore succeeds even when
the ``bond-api`` path dependency is unavailable — a claim enforced by
``tests/test_layer_contract.py``, which blocks ``bond_api`` in a subprocess and
imports every domain module.

Names resolved lazily (they pull in ``bond_api``): ``MissionProvider``,
``GADGETS``, ``GADGET_REGISTRY``, ``FILM``, ``CODENAME``, ``IDENTITY``,
``PACKAGE_VERSION``. The discovery contract used by bond-cli / the coordinator
/ the orchestrator is unchanged: ``casino_royale_1967.mission.MissionProvider``
resolves exactly as before, and ``from casino_royale_1967 import
MissionProvider`` continues to work.
"""

from __future__ import annotations

from typing import Any

from casino_royale_1967.baccarat_table import (
    deal_outcome_probabilities,
    hand_collision_probability,
)
from casino_royale_1967.coordination_farce import (
    AGENT_ROSTER,
    TASK_CATALOG,
    analyze_assignments,
    deduplicate_assignments,
)
from casino_royale_1967.dispatch_chaos import (
    CHAOS_ORDERS,
    simulate_dispatch,
)
from casino_royale_1967.escalation_ladder import (
    compare_doctrines,
    escalation_analysis,
)
from casino_royale_1967.identity_confusion import (
    analyze_identity,
    build_confusion_matrix,
)
from casino_royale_1967.spoof_analyzer import (
    CANONICAL_SPOOF_DOCTRINE,
    analyze_doctrine,
)

#: Names re-exported from the ``bond_api``-dependent protocol adapter. They are
#: resolved on first attribute access so the domain core stays importable
#: without ``bond_api`` installed.
_ADAPTER_EXPORTS: frozenset[str] = frozenset(
    {
        "CODENAME",
        "FILM",
        "GADGETS",
        "GADGET_REGISTRY",
        "IDENTITY",
        "MissionProvider",
        "PACKAGE_VERSION",
    }
)

__all__ = [
    # Identity (lazy — defined in mission.py)
    "FILM",
    "CODENAME",
    "IDENTITY",
    "PACKAGE_VERSION",
    # Domain core (eager — pure, bond_api-free)
    "AGENT_ROSTER",
    "TASK_CATALOG",
    "analyze_assignments",
    "deduplicate_assignments",
    "CHAOS_ORDERS",
    "simulate_dispatch",
    "CANONICAL_SPOOF_DOCTRINE",
    "analyze_doctrine",
    "analyze_identity",
    "build_confusion_matrix",
    "deal_outcome_probabilities",
    "hand_collision_probability",
    "escalation_analysis",
    "compare_doctrines",
    # Protocol adapter (lazy)
    "MissionProvider",
    "GADGETS",
    "GADGET_REGISTRY",
]


def __getattr__(name: str) -> Any:
    """Resolve the ``bond_api``-dependent adapter exports on first access.

    Args:
        name: the attribute requested from the package namespace.

    Returns:
        The attribute of the same name from
        :mod:`casino_royale_1967.mission`.

    Raises:
        AttributeError: for any name that is not an adapter export.
    """
    if name in _ADAPTER_EXPORTS:
        from casino_royale_1967 import mission

        return getattr(mission, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Include the lazily-resolved adapter exports in ``dir()``."""
    return sorted(set(globals()) | _ADAPTER_EXPORTS)
