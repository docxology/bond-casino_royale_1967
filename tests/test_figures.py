"""Tests for the deterministic figure generators (Agg backend)."""

from __future__ import annotations

from pathlib import Path

from casino_royale_1967.figures.plots import (
    FIGURE_FILENAMES,
    render_all_figures,
    render_baccarat_figure,
    render_coordination_figure,
    render_dispatch_figure,
    render_escalation_figure,
    render_identity_figure,
    render_spoof_figure,
)

_ALL_NAMES = ("coordination", "dispatch", "spoof", "identity", "baccarat", "escalation")


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

    def test_identity_figure(self, tmp_path: Path) -> None:
        path = render_identity_figure(tmp_path)
        assert path == tmp_path / FIGURE_FILENAMES["identity"]
        assert path.exists() and path.stat().st_size > 0

    def test_baccarat_figure(self, tmp_path: Path) -> None:
        path = render_baccarat_figure(tmp_path)
        assert path == tmp_path / FIGURE_FILENAMES["baccarat"]
        assert path.exists() and path.stat().st_size > 0

    def test_escalation_figure(self, tmp_path: Path) -> None:
        path = render_escalation_figure(tmp_path)
        assert path == tmp_path / FIGURE_FILENAMES["escalation"]
        assert path.exists() and path.stat().st_size > 0

    def test_render_all_figures_returns_all_six(self, tmp_path: Path) -> None:
        paths = render_all_figures(tmp_path)
        assert set(paths) == set(_ALL_NAMES)
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
        for name in _ALL_NAMES:
            assert first[name].read_bytes() == second[name].read_bytes()
