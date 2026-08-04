"""Casino Royale (1967) — FIVE 00s mission software.

Public API surface: the three pure domain modules, the mission adapter, and
the manuscript-variable generator.
"""

from __future__ import annotations

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
from casino_royale_1967.mission import (
    CODENAME,
    FILM,
    GADGET_REGISTRY,
    IDENTITY,
    MissionProvider,
    PACKAGE_VERSION,
)
from casino_royale_1967.spoof_analyzer import (
    CANONICAL_SPOOF_DOCTRINE,
    analyze_doctrine,
)

__all__ = [
    # Identity
    "FILM",
    "CODENAME",
    "IDENTITY",
    "PACKAGE_VERSION",
    # Domain core
    "AGENT_ROSTER",
    "TASK_CATALOG",
    "analyze_assignments",
    "deduplicate_assignments",
    "CHAOS_ORDERS",
    "simulate_dispatch",
    "CANONICAL_SPOOF_DOCTRINE",
    "analyze_doctrine",
    # Protocol adapter
    "MissionProvider",
    "GADGET_REGISTRY",
]
