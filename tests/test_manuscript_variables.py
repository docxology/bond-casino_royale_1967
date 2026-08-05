"""Tests for manuscript variable generation and the live token cross-reference.

The live cross-reference test scans the numbered prose sections in
``manuscript/[0-9]*.md`` and asserts every ``{{TOKEN}}`` there exists in the
token map produced by ``generate_variables`` — the same strict gate the
manuscript renderer enforces.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from casino_royale_1967.manuscript_variables import (
    TOKEN_PATTERN,
    generate_variables,
    load_mission_config,
    save_variables,
    write_resolved_manuscript_tree,
)

_ROOT = Path(__file__).resolve().parent.parent
_MANUSCRIPT = _ROOT / "manuscript"
_FIXED_NOW = datetime(2026, 8, 4, 9, 0, 0)


class TestTokenMap:
    """The token map is populated from live, deterministic computation."""

    def test_core_identity_tokens(self) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert variables["BOND_IDENTITY"] == "Casino Royale (1967)"
        assert variables["BOND_CODENAME"] == "FIVE 00s"
        assert variables["BOND_VERSION"] == "0.1.0"

    def test_configuration_tokens(self) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert variables["CONFIG_NUM_AGENTS"] == "5"
        assert variables["CONFIG_NUM_TASKS"] == "6"
        assert variables["CONFIG_OVERLAP_WEIGHT"] == "2"
        assert variables["CONFIG_CONFLICT_WEIGHT"] == "3"
        assert variables["CONFIG_MAX_TICKS"] == "100"

    def test_live_result_tokens(self) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert variables["RESULT_OVERLAP_COUNT"] == "3"
        assert variables["RESULT_CONFLICT_COUNT"] == "3"
        assert variables["RESULT_COORDINATION_LOSS"] == "15"
        assert variables["RESULT_CLEARANCE_VIOLATIONS"] == "1"
        assert variables["RESULT_ORDERS"] == "13"
        assert variables["RESULT_DISPATCHED"] == "5"
        assert variables["RESULT_REJECTED"] == "8"
        assert variables["RESULT_VIOLATIONS"] == "8"
        assert variables["RESULT_CHAOS_INDEX"] == "0.62"
        assert variables["RESULT_SUCCESS_RATIO"] == "0.38"
        assert variables["RESULT_SPOOF_INDEX"] == "45.0"

    def test_phase4_result_tokens(self) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        # Identity confusion
        assert variables["RESULT_IDENTITY_NMI"] == "0.075"
        assert variables["RESULT_IDENTITY_RESOLUTION"] == "bond_cooper"
        assert variables["CONFIG_TABLE_BONDS"] == "5"
        # Baccarat odds (canonical infinite-deck values)
        assert variables["RESULT_BACCARAT_PLAYER"] == "0.4461"
        assert variables["RESULT_BACCARAT_BANKER"] == "0.4584"
        assert variables["RESULT_TABLE_COLLISION"] == "0.704"
        # Escalation ladder
        assert variables["RESULT_ESCALATION_SPOOF"] == "4.0"
        assert variables["RESULT_ESCALATION_SANCTIONED"] == "56.0"
        assert variables["RESULT_ESCALATION_ACCELERATION"] == "14.0"

    def test_deterministic_with_fixed_now(self) -> None:
        a = generate_variables(_ROOT, now=_FIXED_NOW)
        b = generate_variables(_ROOT, now=_FIXED_NOW)
        assert a == b

    def test_all_values_are_strings(self) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert all(isinstance(value, str) for value in variables.values())


class TestConfigLoading:
    """manuscript/config.yaml drives the identity and experiment tokens."""

    def test_loads_mission_config(self) -> None:
        config = load_mission_config(_ROOT)
        assert config["mission"]["identity"] == "Casino Royale (1967)"
        assert config["mission"]["codename"] == "FIVE 00s"

    def test_config_has_experiment_block(self) -> None:
        config = load_mission_config(_ROOT)
        assert config["experiment"]["overlap_weight"] == 2.0
        assert config["experiment"]["conflict_weight"] == 3.0


class TestLiveCrossReference:
    """Every prose token in the manuscript is generated — the render gate."""

    def test_all_manuscript_tokens_are_generated(self) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert _MANUSCRIPT.exists(), "manuscript/ must exist to run the live gate"
        sections = sorted(_MANUSCRIPT.glob("[0-9]*.md"))
        assert sections, "no numbered manuscript sections found"
        used: set[str] = set()
        for section in sections:
            used.update(TOKEN_PATTERN.findall(section.read_text(encoding="utf-8")))
        missing = sorted(token for token in used if token not in variables)
        assert not missing, f"tokens used in manuscript but not generated: {missing}"

    def test_manuscript_uses_at_least_one_result_token(self) -> None:
        # Guards against a manuscript that hand-authors metrics in prose.
        sections = sorted(_MANUSCRIPT.glob("[0-9]*.md"))
        texts = "\n".join(s.read_text(encoding="utf-8") for s in sections)
        assert "{{RESULT_" in texts


class TestWriteResolvedTree:
    """Strict token substitution into output/manuscript/."""

    def _make_scaffold(self, tmp_path: Path) -> Path:
        manuscript = tmp_path / "manuscript"
        manuscript.mkdir()
        (manuscript / "00_test.md").write_text(
            "codename {{BOND_CODENAME}} agents {{CONFIG_NUM_AGENTS}}",
            encoding="utf-8",
        )
        return tmp_path

    def test_resolves_tokens(self, tmp_path: Path) -> None:
        project = self._make_scaffold(tmp_path)
        variables = {"BOND_CODENAME": "FIVE 00s", "CONFIG_NUM_AGENTS": "5"}
        out_dir = write_resolved_manuscript_tree(project, variables)
        resolved = (out_dir / "00_test.md").read_text(encoding="utf-8")
        assert resolved == "codename FIVE 00s agents 5"

    def test_unresolved_token_raises(self, tmp_path: Path) -> None:
        project = self._make_scaffold(tmp_path)
        with pytest.raises(ValueError, match="BOND_CODENAME"):
            write_resolved_manuscript_tree(project, {"CONFIG_NUM_AGENTS": "5"})

    def test_injected_token_in_value_is_caught(self, tmp_path: Path) -> None:
        """A token value carrying its own {{...}} is detected by the guard."""
        project = self._make_scaffold(tmp_path)
        with pytest.raises(ValueError, match="INJECTED"):
            write_resolved_manuscript_tree(
                project,
                {"BOND_CODENAME": "FIVE {{INJECTED}} 00s", "CONFIG_NUM_AGENTS": "5"},
            )

    def test_bad_config_yaml_raises(self, tmp_path: Path) -> None:
        manuscript = tmp_path / "manuscript"
        manuscript.mkdir()
        (manuscript / "config.yaml").write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(ValueError, match="YAML mapping"):
            load_mission_config(tmp_path)


class TestSaveVariables:
    """save_variables writes deterministic, sorted JSON."""

    def test_round_trip(self, tmp_path: Path) -> None:
        out = tmp_path / "nested" / "data" / "vars.json"
        variables = {"B": "2", "A": "1"}
        saved = save_variables(variables, out)
        assert saved == out
        assert out.exists()
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert loaded == variables

    def test_live_json_artifact_matches_generate(self, tmp_path: Path) -> None:
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        out = tmp_path / "vars.json"
        save_variables(variables, out)
        assert json.loads(out.read_text(encoding="utf-8")) == variables
