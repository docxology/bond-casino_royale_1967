"""Manuscript variables for the FIVE 00s manuscript.

Hydrates ``{{TOKEN}}`` markers in ``manuscript/[0-9]*.md`` from two sources,
never from hand-authored prose:

* identity/experiment parameters from ``manuscript/config.yaml``
  (``mission:`` and ``experiment:`` blocks);
* live metrics computed deterministically from the domain core — the
  coordination report, dispatch report, and doctrine report.

:func:`write_resolved_manuscript_tree` performs strict substitution into
``output/manuscript/``: any unresolved ``{{TOKEN}}`` left behind raises
``ValueError`` (draft mode is not offered — every token is computable).

``now=`` is accepted for deterministic tests; production defaults to the
current UTC timestamp (the one wall-clock value in the token map, per the
template's ``GENERATION_TIMESTAMP`` convention).
"""

from __future__ import annotations

import json
import platform
import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from casino_royale_1967.baccarat_table import (
    CANONICAL_TABLE_BONDS,
    deal_outcome_probabilities,
    hand_collision_probability,
)
from casino_royale_1967.coordination_farce import (
    AGENT_BY_ID,
    AGENT_ROSTER,
    DEFAULT_ASSIGNMENTS,
    TASK_BY_ID,
    TASK_CATALOG,
    analyze_assignments,
    deduplicate_assignments,
)
from casino_royale_1967.dispatch_chaos import PROTOCOL_RULES, DispatchViolation, simulate_dispatch
from casino_royale_1967.escalation_ladder import LADDER_STATES, compare_doctrines
from casino_royale_1967.figures.plots import FIGURE_FILENAMES
from casino_royale_1967.identity_confusion import analyze_identity
from casino_royale_1967.mission import CODENAME, IDENTITY, PACKAGE_VERSION
from casino_royale_1967.spoof_analyzer import REAL_OPS_RULES, analyze_doctrine

__all__ = [
    "TOKEN_PATTERN",
    "generate_variables",
    "load_mission_config",
    "save_variables",
    "write_resolved_manuscript_tree",
]

TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

_CONFIG_DEFAULTS: dict[str, object] = {
    "mission": {"identity": IDENTITY, "codename": CODENAME},
    "experiment": {
        "overlap_weight": 2.0,
        "conflict_weight": 3.0,
        "max_ticks": 100,
    },
}


def load_mission_config(project_root: Path) -> dict[str, object]:
    """Load ``manuscript/config.yaml`` merged over safe defaults.

    Args:
        project_root: the package root (contains ``manuscript/config.yaml``).

    Returns:
        The parsed config mapping (never ``None`` for a valid file).
    """
    path = project_root / "manuscript" / "config.yaml"
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    merged: dict[str, object] = dict(_CONFIG_DEFAULTS)
    for section, values in loaded.items():
        if isinstance(values, dict):
            base = merged.get(section)
            if isinstance(base, dict):
                base.update(values)
            else:
                merged[section] = values
        else:
            merged[str(section)] = values
    return merged


def _section(config: dict[str, object], name: str) -> dict[str, object]:
    value = config.get(name, {})
    return value if isinstance(value, dict) else {}


def _rule_counts(violations: tuple[DispatchViolation, ...]) -> dict[str, int]:
    """Violations per protocol rule, with every declared rule present.

    Rules that never fired are reported as ``0`` rather than omitted, so a
    manuscript token can never silently vanish when the scenario changes.

    Args:
        violations: the violations recorded by the dispatch simulation.

    Returns:
        Mapping ``rule -> count`` covering all of ``PROTOCOL_RULES``.
    """
    counts = dict.fromkeys(PROTOCOL_RULES, 0)
    for violation in violations:
        counts[violation.rule] = counts.get(violation.rule, 0) + 1
    return counts


def generate_variables(project_root: Path, *, now: datetime | None = None) -> dict[str, str]:
    """Compute the full ``{{TOKEN}}`` map for the FIVE 00s manuscript.

    Metrics are recomputed live from the deterministic domain core — the same
    analyses the mission executes — so tokens can never drift from code.

    Args:
        project_root: the package root.
        now: timestamp override (deterministic tests); defaults to UTC now.

    Returns:
        Mapping of token name -> rendered string value.
    """
    config = load_mission_config(project_root)
    mission = _section(config, "mission")
    experiment = _section(config, "experiment")

    overlap_weight = float(str(experiment.get("overlap_weight", 2.0)))
    conflict_weight = float(str(experiment.get("conflict_weight", 3.0)))
    max_ticks = int(str(experiment.get("max_ticks", 100)))

    coordination = analyze_assignments(
        DEFAULT_ASSIGNMENTS,
        overlap_weight=overlap_weight,
        conflict_weight=conflict_weight,
    )
    dedup = deduplicate_assignments(DEFAULT_ASSIGNMENTS)
    dispatch = simulate_dispatch(max_ticks=max_ticks)
    doctrine = analyze_doctrine()
    identity = analyze_identity()
    odds = deal_outcome_probabilities()
    collision = hand_collision_probability(CANONICAL_TABLE_BONDS)
    escalation = compare_doctrines()

    stamp = (now or datetime.now(UTC)).isoformat(timespec="seconds")

    rule_counts = _rule_counts(dispatch.violations)
    rules_fired = sum(1 for count in rule_counts.values() if count > 0)

    # First clearance failure of the canonical assignment set, described from
    # the roster/catalog rather than restated in prose.
    first_breach = coordination.clearance_violations[0]
    breach_agent = AGENT_BY_ID[first_breach.agent_id]
    breach_task = TASK_BY_ID[first_breach.task_id]

    return {
        # Identity
        "BOND_IDENTITY": str(mission.get("identity", IDENTITY)),
        "BOND_CODENAME": str(mission.get("codename", CODENAME)),
        "BOND_VERSION": PACKAGE_VERSION,
        # Configuration
        "CONFIG_NUM_AGENTS": str(len(AGENT_ROSTER)),
        "CONFIG_NUM_TASKS": str(len(TASK_CATALOG)),
        "CONFIG_OVERLAP_WEIGHT": f"{overlap_weight:g}",
        "CONFIG_CONFLICT_WEIGHT": f"{conflict_weight:g}",
        "CONFIG_MAX_TICKS": str(max_ticks),
        "CONFIG_TABLE_BONDS": str(CANONICAL_TABLE_BONDS),
        "CONFIG_PROTOCOL_RULES": str(len(PROTOCOL_RULES)),
        "CONFIG_DOCTRINE_RULES": str(len(REAL_OPS_RULES)),
        "CONFIG_LADDER_STATES": str(len(LADDER_STATES)),
        "CONFIG_NUM_FIGURES": str(len(FIGURE_FILENAMES)),
        # Coordination-farce results
        "RESULT_ASSIGNMENTS": str(coordination.total_assignments),
        "RESULT_OVERLAP_COUNT": str(coordination.overlap_count),
        "RESULT_CONFLICT_COUNT": str(coordination.conflict_count),
        "RESULT_COORDINATION_LOSS": f"{coordination.loss:g}",
        "RESULT_CLEARANCE_VIOLATIONS": str(len(coordination.clearance_violations)),
        "RESULT_CLEARANCE_AGENT": breach_agent.agent_id,
        "RESULT_CLEARANCE_ALIAS": breach_agent.alias,
        "RESULT_CLEARANCE_LEVEL": str(breach_agent.clearance),
        "RESULT_CLEARANCE_REQUIRED": str(breach_task.required_clearance),
        "RESULT_CLEARANCE_TASK": breach_task.description,
        "RESULT_DEDUP_KEPT": str(len(dedup.kept)),
        "RESULT_DEDUP_DROPPED": str(len(dedup.dropped)),
        # Dispatch-chaos results
        "RESULT_ORDERS": str(dispatch.total_orders),
        "RESULT_DISPATCHED": str(dispatch.dispatched),
        "RESULT_REJECTED": str(dispatch.rejected),
        "RESULT_VIOLATIONS": str(len(dispatch.violations)),
        "RESULT_CHAOS_INDEX": f"{dispatch.chaos_index:.2f}",
        "RESULT_SUCCESS_RATIO": f"{dispatch.success_ratio:.2f}",
        # Per-rule dispatch violation counts (never hand-authored in prose)
        "RESULT_RULES_FIRED": str(rules_fired),
        "RESULT_RULE_EXCLUSIVE_TASK": str(rule_counts["exclusive_task"]),
        "RESULT_RULE_CLEARANCE": str(rule_counts["clearance"]),
        "RESULT_RULE_DOUBLE_BOOKING": str(rule_counts["double_booking"]),
        "RESULT_RULE_DUPLICATE_ORDER": str(rule_counts["duplicate_order"]),
        "RESULT_RULE_DUPLICATE_CODENAME": str(rule_counts["duplicate_codename"]),
        # Spoof-analyzer results
        "RESULT_DIRECTIVES": str(doctrine.directive_count),
        "RESULT_MEAN_SPOOF_SCORE": f"{doctrine.mean_score:.2f}",
        "RESULT_SPOOF_INDEX": f"{doctrine.spoof_index:.1f}",
        "RESULT_WORST_DIRECTIVE": doctrine.worst_directive,
        "RESULT_DOCTRINE_RULES_HIT": str(len(doctrine.rule_violation_counts)),
        # Identity-confusion results
        "RESULT_IDENTITY_NMI": f"{identity.normalized_mutual_information:.3f}",
        "RESULT_IDENTITY_MI": f"{identity.mutual_information:.3f}",
        # Every entropy in bits at three decimals, so the two subtractions the
        # manuscript states — H(routed) - I and H(intended) - I — reconcile
        # exactly at the printed precision instead of only approximately.
        "RESULT_IDENTITY_PRIOR_ENTROPY": f"{identity.prior_entropy:.3f}",
        "RESULT_IDENTITY_ROUTING_ENTROPY": f"{identity.routing_entropy:.3f}",
        "RESULT_IDENTITY_AMBIGUITY": f"{identity.conditional_entropy:.3f}",
        "RESULT_IDENTITY_RESIDUAL": f"{identity.residual_identity_entropy:.3f}",
        "RESULT_IDENTITY_RESOLUTION": identity.resolution.resolution,
        "RESULT_IDENTITY_CONFIDENCE": f"{identity.resolution.confidence:.3f}",
        # Baccarat-table results
        "RESULT_BACCARAT_PLAYER": f"{odds.player_probability:.4f}",
        "RESULT_BACCARAT_BANKER": f"{odds.banker_probability:.4f}",
        "RESULT_BACCARAT_TIE": f"{odds.tie_probability:.4f}",
        "RESULT_TABLE_COLLISION": f"{collision:.3f}",
        "RESULT_BANKER_ADVANTAGE": f"{odds.banker_probability - odds.player_probability:+.4f}",
        # Escalation results
        "RESULT_ESCALATION_SPOOF": f"{escalation.spoof_index:.1f}",
        "RESULT_ESCALATION_SANCTIONED": f"{escalation.sanctioned_index:.1f}",
        "RESULT_ESCALATION_ACCELERATION": f"{escalation.acceleration_factor:.1f}",
        "RESULT_ESCALATION_SPECTRAL": f"{escalation.spoof_report.spectral_radius_q:.3f}",
        "RESULT_ESCALATION_ABSORPTION": f"{escalation.spoof_report.absorption_probability:.3f}",
        "RESULT_ESCALATION_ABSORBING_STATE": escalation.spoof_report.absorbing_state,
        # Figures
        "FIGURE_COORDINATION": FIGURE_FILENAMES["coordination"],
        "FIGURE_DISPATCH": FIGURE_FILENAMES["dispatch"],
        "FIGURE_SPOOF": FIGURE_FILENAMES["spoof"],
        "FIGURE_IDENTITY": FIGURE_FILENAMES["identity"],
        "FIGURE_BACCARAT": FIGURE_FILENAMES["baccarat"],
        "FIGURE_ESCALATION": FIGURE_FILENAMES["escalation"],
        # Environment
        "PYTHON_VERSION": platform.python_version(),
        "GENERATION_TIMESTAMP": stamp,
    }


def save_variables(variables: dict[str, str], out_path: Path) -> Path:
    """Write the token map as sorted, indented JSON.

    Args:
        variables: the token map from :func:`generate_variables`.
        out_path: destination file (parent directories are created).

    Returns:
        The path written.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(variables, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return out_path


def write_resolved_manuscript_tree(project_root: Path, variables: dict[str, str]) -> Path:
    """Copy numbered manuscript sections to ``output/manuscript/``, tokens resolved.

    Strict mode: any ``{{TOKEN}}`` left after substitution (unknown token or
    missing key) raises ``ValueError`` naming the section and token.

    Args:
        project_root: the package root.
        variables: the token map from :func:`generate_variables`.

    Returns:
        The output manuscript directory.
    """
    source_dir = project_root / "manuscript"
    out_dir = project_root / "output" / "manuscript"
    out_dir.mkdir(parents=True, exist_ok=True)

    sections = sorted(source_dir.glob("[0-9]*.md"))
    for section in sections:
        text = section.read_text(encoding="utf-8")

        def _substitute(match: re.Match[str]) -> str:
            token = match.group(1)
            if token not in variables:
                raise ValueError(f"unresolved token {{{{{token}}}}} in {section.name}")
            return variables[token]

        resolved = TOKEN_PATTERN.sub(_substitute, text)
        (out_dir / section.name).write_text(resolved, encoding="utf-8")

    remaining = TOKEN_PATTERN.findall(
        "\n".join(section.read_text(encoding="utf-8") for section in sorted(out_dir.glob("[0-9]*.md")))
    )
    if remaining:
        raise ValueError(f"unresolved tokens remain: {sorted(set(remaining))}")
    return out_dir
