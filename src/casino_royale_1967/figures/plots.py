"""Deterministic matplotlib figures for the FIVE 00s mission.

Six publication-style figures, one per concept:

* ``coordination_farce.png`` — per-task agent load (overlap visible as bars
  taller than one);
* ``dispatch_chaos.png`` — tick-by-tick dispatch timeline: accepted orders vs
  protocol violations, stacked;
* ``spoof_analyzer.png`` — per-directive spoof score bar chart with the
  normalised spoof index in the title;
* ``identity_confusion.png`` — the 5x5 routing confusion matrix heatmap with
  the normalized mutual information in the title;
* ``baccarat_odds.png`` — player/banker/tie deal probabilities with the
  five-Bond hand-collision probability annotated;
* ``escalation_ladder.png`` — expected steps to catastrophe per transient
  state, grouped by doctrine (spoof vs sanctioned).

Every figure is generated from the canonical deterministic analyses (no RNG,
no wall clock) and rendered with a fixed DPI, so re-running reproduces
byte-identical PNGs.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from casino_royale_1967.baccarat_table import (
    CANONICAL_TABLE_BONDS,
    deal_outcome_probabilities,
    hand_collision_probability,
)
from casino_royale_1967.coordination_farce import (
    DEFAULT_ASSIGNMENTS,
    analyze_assignments,
)
from casino_royale_1967.dispatch_chaos import CHAOS_ORDERS, simulate_dispatch
from casino_royale_1967.escalation_ladder import compare_doctrines
from casino_royale_1967.identity_confusion import (
    analyze_identity,
    build_confusion_matrix,
)
from casino_royale_1967.spoof_analyzer import (
    CANONICAL_SPOOF_DOCTRINE,
    analyze_doctrine,
)

__all__ = [
    "FIGURE_FILENAMES",
    "render_all_figures",
    "render_baccarat_figure",
    "render_coordination_figure",
    "render_dispatch_figure",
    "render_escalation_figure",
    "render_identity_figure",
    "render_spoof_figure",
]

FIGURE_FILENAMES: dict[str, str] = {
    "coordination": "coordination_farce.png",
    "dispatch": "dispatch_chaos.png",
    "spoof": "spoof_analyzer.png",
    "identity": "identity_confusion.png",
    "baccarat": "baccarat_odds.png",
    "escalation": "escalation_ladder.png",
}


def _save(fig: plt.Figure, output_dir: Path, filename: str) -> Path:
    """Render a figure to ``output_dir`` at fixed DPI (Agg backend)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return path


def render_coordination_figure(output_dir: Path) -> Path:
    """Bar chart of per-task agent load; overlaps stand out as bars > 1."""
    report = analyze_assignments(DEFAULT_ASSIGNMENTS)
    tasks = sorted(report.per_task_load)
    loads = [report.per_task_load[task] for task in tasks]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = ["#b91c1c" if load > 1 else "#1e3a8a" for load in loads]
    ax.bar(tasks, loads, color=colors)
    ax.axhline(1.0, color="#334155", linestyle="--", linewidth=0.8)
    ax.set_ylabel("agents assigned")
    ax.set_title(
        f"Coordination farce: {report.overlap_count} overlaps, {report.conflict_count} conflicts (loss {report.loss:g})"
    )
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    return _save(fig, output_dir, FIGURE_FILENAMES["coordination"])


def render_dispatch_figure(output_dir: Path) -> Path:
    """Stacked per-tick bars: accepted dispatches vs protocol violations."""
    report = simulate_dispatch(CHAOS_ORDERS)
    ticks = sorted({event.tick for event in report.events})
    dispatched = [sum(1 for e in report.events if e.tick == t and e.event_type == "dispatch") for t in ticks]
    violations = [sum(1 for e in report.events if e.tick == t and e.event_type == "violation") for t in ticks]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(ticks, dispatched, label="dispatched", color="#1e3a8a")
    ax.bar(ticks, violations, bottom=dispatched, label="violations", color="#b91c1c")
    ax.set_xlabel("tick")
    ax.set_ylabel("orders")
    ax.set_title(
        f"Dispatch chaos: {report.dispatched}/{report.total_orders} dispatched, chaos index {report.chaos_index:.2f}"
    )
    ax.legend()
    fig.tight_layout()
    return _save(fig, output_dir, FIGURE_FILENAMES["dispatch"])


def render_spoof_figure(output_dir: Path) -> Path:
    """Per-directive spoof scores with the aggregate spoof index in the title."""
    report = analyze_doctrine(CANONICAL_SPOOF_DOCTRINE)
    labels = [f"#{i + 1}" for i in range(report.directive_count)]
    scores = [verdict.spoof_score for verdict in report.verdicts]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(labels, scores, color="#1e3a8a")
    ax.set_xlabel("doctrine directive")
    ax.set_ylabel("spoof score")
    ax.set_title(f"Spoof protocol analyzer: doctrine spoof index {report.spoof_index:.1f} / 100")
    fig.tight_layout()
    return _save(fig, output_dir, FIGURE_FILENAMES["spoof"])


def render_identity_figure(output_dir: Path) -> Path:
    """The 5x5 routing confusion-matrix heatmap (NMI in the title)."""
    confusion = build_confusion_matrix()
    report = analyze_identity()
    labels = [f"B{i + 1}" for i in range(confusion.shape[0])]

    fig, ax = plt.subplots(figsize=(7, 6))
    cmap = plt.get_cmap("RdYlBu_r")
    image = ax.imshow(confusion, cmap=cmap, vmin=0.0, vmax=confusion.max())
    ax.set_xticks(range(confusion.shape[0]))
    ax.set_yticks(range(confusion.shape[0]))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("routed to")
    ax.set_ylabel("intended agent")
    ax.set_title(
        f"Identity confusion: routing NMI {report.normalized_mutual_information:.3f}, "
        f"ambiguity {report.conditional_entropy:.2f} bits"
    )
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    return _save(fig, output_dir, FIGURE_FILENAMES["identity"])


def render_baccarat_figure(output_dir: Path) -> Path:
    """Player/banker/tie odds bar chart with the table-collision annotation."""
    odds = deal_outcome_probabilities()
    collision = hand_collision_probability(CANONICAL_TABLE_BONDS)
    categories = ["player", "banker", "tie"]
    values = [
        odds.player_probability,
        odds.banker_probability,
        odds.tie_probability,
    ]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(categories, values, color=["#1e3a8a", "#b91c1c", "#64748b"])
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.005,
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )
    ax.set_ylabel("probability")
    ax.set_ylim(0.0, 0.55)
    ax.set_title(f"Casino table odds: {CANONICAL_TABLE_BONDS}-Bond hand-collision probability {collision:.3f}")
    fig.tight_layout()
    return _save(fig, output_dir, FIGURE_FILENAMES["baccarat"])


def render_escalation_figure(output_dir: Path) -> Path:
    """Grouped bars: expected absorption time per state, spoof vs sanctioned."""
    comparison = compare_doctrines()
    states = comparison.spoof_report.states[:-1]  # transient states only
    spoof = list(comparison.spoof_report.expected_absorption)
    sanctioned = list(comparison.sanctioned_report.expected_absorption)
    x = list(range(len(states)))

    fig, ax = plt.subplots(figsize=(9, 4.5))
    width = 0.38
    ax.bar(x, spoof, width, label="spoof doctrine", color="#b91c1c")
    ax.bar(
        [i + width for i in x],
        sanctioned,
        width,
        label="sanctioned doctrine",
        color="#1e3a8a",
    )
    ax.set_xticks([i + width / 2 for i in x])
    ax.set_xticklabels(states)
    ax.set_ylabel("expected steps to catastrophe")
    ax.set_title(
        f"Doctrine escalation: spoof {comparison.spoof_index:.1f} steps vs "
        f"sanctioned {comparison.sanctioned_index:.1f} ({comparison.acceleration_factor:.1f}x faster)"
    )
    ax.legend()
    fig.tight_layout()
    return _save(fig, output_dir, FIGURE_FILENAMES["escalation"])


def render_all_figures(output_dir: Path | str) -> dict[str, Path]:
    """Render every FIVE 00s figure into ``output_dir``.

    Args:
        output_dir: target directory (created when missing).

    Returns:
        Mapping of concept name -> rendered PNG path.
    """
    target = Path(output_dir)
    return {
        "coordination": render_coordination_figure(target),
        "dispatch": render_dispatch_figure(target),
        "spoof": render_spoof_figure(target),
        "identity": render_identity_figure(target),
        "baccarat": render_baccarat_figure(target),
        "escalation": render_escalation_figure(target),
    }
