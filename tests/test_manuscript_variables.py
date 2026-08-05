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

    def test_per_rule_dispatch_tokens(self) -> None:
        """Per-rule rejection counts are tokens, not prose."""
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        per_rule = {
            "RESULT_RULE_EXCLUSIVE_TASK": "2",
            "RESULT_RULE_CLEARANCE": "2",
            "RESULT_RULE_DOUBLE_BOOKING": "2",
            "RESULT_RULE_DUPLICATE_ORDER": "1",
            "RESULT_RULE_DUPLICATE_CODENAME": "1",
        }
        for token, expected in per_rule.items():
            assert variables[token] == expected, token
        # The per-rule counts must reconcile with the total.
        assert sum(int(variables[token]) for token in per_rule) == int(variables["RESULT_VIOLATIONS"])
        assert variables["RESULT_RULES_FIRED"] == variables["CONFIG_PROTOCOL_RULES"] == "5"

    def test_clearance_breach_tokens_describe_the_real_assignment(self) -> None:
        """The clearance-breach narrative is derived from roster + catalog."""
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert variables["RESULT_CLEARANCE_AGENT"] == "bond_jimmy"
        assert variables["RESULT_CLEARANCE_ALIAS"] == "Woody Allen"
        assert variables["RESULT_CLEARANCE_TASK"] == "infiltrate SMERSH headquarters"
        # The breach must actually be a breach.
        assert int(variables["RESULT_CLEARANCE_LEVEL"]) < int(variables["RESULT_CLEARANCE_REQUIRED"])

    def test_structural_config_tokens_track_the_code(self) -> None:
        """Counts describing code structure are derived, never declared."""
        from casino_royale_1967.dispatch_chaos import PROTOCOL_RULES
        from casino_royale_1967.escalation_ladder import LADDER_STATES
        from casino_royale_1967.figures.plots import FIGURE_FILENAMES
        from casino_royale_1967.spoof_analyzer import REAL_OPS_RULES

        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert variables["CONFIG_PROTOCOL_RULES"] == str(len(PROTOCOL_RULES))
        assert variables["CONFIG_DOCTRINE_RULES"] == str(len(REAL_OPS_RULES))
        assert variables["CONFIG_LADDER_STATES"] == str(len(LADDER_STATES))
        assert variables["CONFIG_NUM_FIGURES"] == str(len(FIGURE_FILENAMES))

    def test_escalation_certainty_tokens(self) -> None:
        """Absorption is reported as a computed fact, not an assumption."""
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        assert float(variables["RESULT_ESCALATION_SPECTRAL"]) < 1.0
        assert float(variables["RESULT_ESCALATION_ABSORPTION"]) == pytest.approx(1.0, abs=1e-3)
        assert variables["RESULT_ESCALATION_ABSORBING_STATE"] == "catastrophe"

    def test_identity_information_tokens_are_consistent(self) -> None:
        """The tokens must satisfy the identities they are named after.

        ``I = H(routed) - H(routed | intended)`` — note the routing entropy,
        *not* the prior entropy, so ``ambiguity != prior - MI`` in general.
        """
        from casino_royale_1967.identity_confusion import analyze_identity

        report = analyze_identity()
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        prior = float(variables["RESULT_IDENTITY_PRIOR_ENTROPY"])
        mi = float(variables["RESULT_IDENTITY_MI"])
        nmi = float(variables["RESULT_IDENTITY_NMI"])
        ambiguity = float(variables["RESULT_IDENTITY_AMBIGUITY"])

        assert prior == pytest.approx(report.prior_entropy, abs=5e-3)
        assert mi == pytest.approx(report.mutual_information, abs=5e-3)
        # The defining identity of mutual information.
        assert ambiguity == pytest.approx(report.routing_entropy - mi, abs=5e-3)
        # NMI normalizes by the larger of the two marginal entropies.
        assert nmi == pytest.approx(mi / max(prior, report.routing_entropy), abs=5e-3)
        # A shared codename means routing recovers only a sliver of identity.
        assert 0.0 < mi < prior
        assert 0.0 < nmi < 0.2

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

    def test_every_generated_token_is_used(self) -> None:
        """No dead tokens: a generated token nobody references is drift.

        Six ``FIGURE_*`` tokens were generated but unreferenced while the
        manuscript hardcoded figure filenames, so a rename in
        ``FIGURE_FILENAMES`` would have silently broken every image link.
        """
        variables = generate_variables(_ROOT, now=_FIXED_NOW)
        sections = sorted(_MANUSCRIPT.glob("[0-9]*.md"))
        used: set[str] = set()
        for section in sections:
            used.update(TOKEN_PATTERN.findall(section.read_text(encoding="utf-8")))
        unused = sorted(set(variables) - used)
        assert not unused, f"generated but never referenced: {unused}"

    def test_figure_links_go_through_tokens(self) -> None:
        """Image paths must name a token, never a literal PNG filename."""
        from casino_royale_1967.figures.plots import FIGURE_FILENAMES

        results = (_MANUSCRIPT / "03_results.md").read_text(encoding="utf-8")
        for filename in FIGURE_FILENAMES.values():
            assert filename not in results, f"hardcoded figure filename {filename}"
        links = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", results)
        assert len(links) == len(FIGURE_FILENAMES), "one figure link per rendered figure"
        for link in links:
            assert TOKEN_PATTERN.search(link), f"figure link {link} does not use a token"


class TestNoHandAuthoredMetrics:
    """Measured quantities must arrive as tokens, never as literals in prose.

    Only the sections that *report measurements* are scanned. Methodology and
    setup legitimately state structural constants (card values, drawing rules,
    loss-weight definitions, the seed), and reproducibility/conclusion state
    the coverage gate itself rather than a measured coverage figure.
    """

    #: Sections whose numerals are all results and must therefore be tokens.
    MEASURED_SECTIONS: tuple[str, ...] = ("03_results.md", "04_conclusion.md")

    #: Numerals that are definitions or dates rather than measurements.
    ALLOWED: frozenset[str] = frozenset(
        {
            "100",  # the "/ 100" scale denominator of the spoof index
            "1967",  # the film's release year
            "90",  # the declared coverage gate, not a measured value
        }
    )

    #: A bare numeral: not part of a word, not part of a dotted version string,
    #: but *including* one that ends a sentence ("the loss is 15.").
    NUMERAL = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?!\.?\d)(?!\w)")

    #: Markdown ordered-list markers ("1." at the head of a line) are layout,
    #: not measurements, and are removed before the numeral scan.
    LIST_MARKER = re.compile(r"^\s*\d+\.\s", re.MULTILINE)

    def _offenders(self, text: str) -> list[str]:
        """Bare, non-allowlisted numerals left after token substitution."""
        stripped = self.LIST_MARKER.sub("", TOKEN_PATTERN.sub("", text))
        return sorted({n for n in self.NUMERAL.findall(stripped) if n not in self.ALLOWED})

    @pytest.mark.parametrize("section_name", MEASURED_SECTIONS)
    def test_no_bare_numerals_in_measured_prose(self, section_name: str) -> None:
        section = _MANUSCRIPT / section_name
        assert section.exists(), f"{section_name} must exist"
        offenders = self._offenders(section.read_text(encoding="utf-8"))
        assert not offenders, f"{section_name} hand-authors metrics: {offenders}"

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("The chaos index is 0.62 and the loss is 15.", ["0.62", "15"]),
            ("Rejected 8 of 13 orders", ["13", "8"]),
            ("A collision probability of 0.704.", ["0.704"]),
            ("Version 0.1.0 is not a metric", []),
            ("Token only: {{RESULT_CHAOS_INDEX}}", []),
            ("Words like COVID19 and h2o are not metrics", []),
        ],
    )
    def test_scan_is_not_vacuous(self, text: str, expected: list[str]) -> None:
        """Positive controls: the scan must reject injected literal metrics.

        The sentence-final case is the one that matters most — an earlier
        version of this regex excluded a trailing ``.``, so ``the loss is 15.``
        slipped through the gate entirely.
        """
        assert self._offenders(text) == expected

    def test_measured_sections_actually_carry_numbers(self) -> None:
        """Guard: the sections scanned must contain result tokens at all."""
        for name in self.MEASURED_SECTIONS:
            text = (_MANUSCRIPT / name).read_text(encoding="utf-8")
            assert text.count("{{RESULT_") >= 5, f"{name} reports too few tokens to be a results section"


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
