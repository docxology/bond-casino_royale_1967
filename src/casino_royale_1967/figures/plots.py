"""Deterministic matplotlib figures for the FIVE 00s mission.

Three publication-style figures, one per concept module:

* ``coordination_farce.png`` — per-task agent load (overlap visible as bars
  taller than one) with conflict pairs annotated;
* ``dispatch_chaos.png`` — tick-by-tick dispatch timeline: accepted orders vs
  protocol violations, stacked;
* ``spoof_analyzer.png`` — per-directive spoof score bar chart with the
  normalised spoof index in the title.

Every figure is generated from the canonical deterministic analyses (no RNG,
no wall clock) and rendered with a fixed DPI, so re-running reproduces
byte-identical PNGs.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from casino_royale_1967.coordination_farce import (
    DEFAULT_ASSIGNMENTS,
    analyze_assignments,
)
from casino_royale_1967.dispatch_chaos import CHAOS_ORDERS, simulate_dispatch
from casino_royale_1967.spoof_analyzer import (
    CANONICAL_SPOOF_DOCTRINE,
    analyze_doctrine,
)

__all__ = [
    "FIGURE_FILENAMES",
    "render_all_figures",
    "render_coordination_figure",
    "render_dispatch_figure",
    "render_spoof_figure",
]

FIGURE_FILENAMES: dict[str, str] = {
    "coordination": "coordination_farce.png",
    "dispatch": "dispatch_chaos.png",
    "spoof": "spoof_analyzer.png",
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
    bottom = [0] * len(ticks)
    ax.bar(ticks, dispatched, label="dispatched", color="#1e3a8a")
    bottom = dispatched
    ax.bar(ticks, violations, bottom=bottom, label="violations", color="#b91c1c")
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
    }
