"""Tests for the deterministic figure generators (Agg backend)."""

from __future__ import annotations

from pathlib import Path

from casino_royale_1967.figures.plots import (
    FIGURE_FILENAMES,
    render_all_figures,
    render_coordination_figure,
    render_dispatch_figure,
    render_spoof_figure,
)


class TestFigureRendering:
    """Each concept figure renders to a non-empty PNG at fixed DPI."""

    def test_coordination_figure(self, tmp_path: Path) -> None:
        path = render_coordination_figure(tmp_path)
        assert path == tmp_path / FIGURE_FILENAMES["coordination"]
        assert path.exists() and path.stat().st_size > 0

    def test_dispatch_figure(self, tmp_path: Path) -> None:
        path = render_dispatch_figure(tmp_path)
        assert path.exists() and path.stat().st_size > 0

    def test_spoof_figure(self, tmp_path: Path) -> None:
        path = render_spoof_figure(tmp_path)
        assert path.exists() and path.stat().st_size > 0

    def test_render_all_figures_returns_three_paths(self, tmp_path: Path) -> None:
        paths = render_all_figures(tmp_path)
        assert set(paths) == {"coordination", "dispatch", "spoof"}
        for name, path in paths.items():
            assert path == tmp_path / FIGURE_FILENAMES[name]
            assert path.exists() and path.stat().st_size > 0

    def test_render_all_accepts_str_dir(self, tmp_path: Path) -> None:
        target = str(tmp_path / "figs")
        paths = render_all_figures(target)
        assert all(Path(path).exists() for path in paths.values())

    def test_recreation_is_idempotent(self, tmp_path: Path) -> None:
        first = render_all_figures(tmp_path)
        second = render_all_figures(tmp_path)
        # Deterministic rendering: byte-identical PNGs across calls.
        for name in ("coordination", "dispatch", "spoof"):
            assert first[name].read_bytes() == second[name].read_bytes()
