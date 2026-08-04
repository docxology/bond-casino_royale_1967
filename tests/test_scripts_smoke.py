"""Subprocess smoke tests for the thin mission-phase CLIs.

Each script is run as its own subprocess (``sys.executable``) with
``cwd=project_root``, asserting exit code 0 and the expected JSON/artifact
output. Figures and the manuscript-variables artifact land under ``output/``,
which is git-ignored, so these runs leave the tree clean.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _ROOT / "scripts"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_SCRIPTS / "mission.py"), *args],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class TestMissionCLI:
    """Each life-cycle phase subcommand exits 0 and prints parseable JSON."""

    def test_brief(self) -> None:
        result = _run("brief")
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["codename"] == "FIVE 00s"
        assert len(payload["objectives"]) == 3

    def test_recon(self) -> None:
        result = _run("recon")
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        labels = {f["label"] for f in payload["findings"]}
        assert "doctrine" in labels

    def test_plan(self) -> None:
        result = _run("plan")
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert len(payload["steps"]) == 3

    def test_execute(self) -> None:
        result = _run("execute")
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["success"] is True
        assert payload["provenance"]["input_hash"]
        assert payload["results"]["doctrine"]["spoof_index"] == 45.0

    def test_debrief(self) -> None:
        result = _run("debrief")
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["success"] is True
        assert len(payload["lessons"]) >= 3

    def test_figures(self) -> None:
        result = _run("figures")
        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert set(payload) == {"coordination", "dispatch", "spoof"}
        for name, path in payload.items():
            assert Path(path).exists(), f"missing {name} figure at {path}"

    def test_unknown_subcommand_exits_2(self) -> None:
        result = _run("not_a_phase")
        assert result.returncode == 2

    def test_no_args_exits_2(self) -> None:
        result = _run()
        assert result.returncode == 2


class TestManuscriptVariablesCLI:
    """z_generate_manuscript_variables.py writes + injects all artifacts."""

    def test_generates_variables_and_resolves_tree(self) -> None:
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS / "z_generate_manuscript_variables.py")],
            cwd=_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

        vars_path = _ROOT / "output" / "data" / "manuscript_variables.json"
        assert vars_path.exists()
        variables = json.loads(vars_path.read_text(encoding="utf-8"))
        assert variables["BOND_CODENAME"] == "FIVE 00s"
        assert variables["RESULT_SPOOF_INDEX"] == "45.0"

        # Resolved manuscript tree must carry no unresolved {{TOKEN}}s.
        resolved = _ROOT / "output" / "manuscript"
        for section in sorted(resolved.glob("[0-9]*.md")):
            text = section.read_text(encoding="utf-8")
            assert "{{" not in text, f"unresolved token in {section.name}"

        # Figures rendered as part of the pipeline.
        assert (_ROOT / "output" / "figures" / "coordination_farce.png").exists()
