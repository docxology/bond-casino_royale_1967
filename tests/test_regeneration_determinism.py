"""The byte-for-byte regeneration claim, bound to an executable check.

The manuscript, ``README.md`` and ``AGENTS.md`` all state that regenerating
this package's artifacts reproduces them byte for byte. That claim was false
for the whole of this package's history: ``generate_variables`` defaulted its
``now=`` parameter to ``datetime.now(UTC)`` and rendered the result into the
manuscript prose and the token JSON, so every regeneration produced different
bytes. The test that was supposed to cover it passed a fixed ``now=`` to both
calls — it fixed the only value that varied, and so could never fail.

These tests do the thing the claim describes: run the production generator
twice, in sequence, with no injected values of any kind, and compare the
resulting bytes. A sleep separates the runs so a second-resolution clock would
tick between them, and a separate scan rejects any clock-shaped value in the
token map so a coarser-grained clock cannot hide inside one interval either.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent.parent
_GENERATOR = _ROOT / "scripts" / "z_generate_manuscript_variables.py"
_OUTPUT = _ROOT / "output"
_TOKEN_JSON = _OUTPUT / "data" / "manuscript_variables.json"

# Artifacts the byte-for-byte claim covers: the token map, the resolved
# manuscript tree, and the rendered figures — everything the generator writes.
_COVERED = (
    _OUTPUT / "data" / "manuscript_variables.json",
    _OUTPUT / "manuscript",
    _OUTPUT / "figures",
)

# A bare date (the committed paper.date) is legitimate; a date carrying a
# time of day is a clock reading and nothing else.
_DATETIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _run_generator() -> None:
    """Execute the production generator exactly as a user would."""
    result = subprocess.run(
        [sys.executable, str(_GENERATOR)],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"generator failed:\n{result.stdout}\n{result.stderr}"


def _covered_files() -> list[Path]:
    files: list[Path] = []
    for target in _COVERED:
        if target.is_dir():
            files.extend(p for p in target.rglob("*") if p.is_file())
        elif target.is_file():
            files.append(target)
    return sorted(files)


def _tree_digest() -> tuple[str, dict[str, str]]:
    """Hash every covered artifact, returning the roll-up and the per-file map.

    The per-file map is returned so a failure names the artifact that drifted
    instead of only reporting that two opaque hashes differ.
    """
    per_file: dict[str, str] = {}
    roll_up = hashlib.sha256()
    for path in _covered_files():
        rel = str(path.relative_to(_ROOT))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        per_file[rel] = digest
        roll_up.update(rel.encode("utf-8"))
        roll_up.update(digest.encode("utf-8"))
    return roll_up.hexdigest(), per_file


class TestRegenerationIsByteIdentical:
    """Regenerating twice produces identical bytes — the claim, executed."""

    def test_full_regeneration_is_byte_identical(self) -> None:
        _run_generator()
        first_hash, first_files = _tree_digest()
        assert first_files, "generator produced no covered artifacts"

        # Let the wall clock advance past one-second resolution, so a
        # reintroduced timestamp would differ between the two runs rather
        # than accidentally landing in the same tick.
        time.sleep(1.1)

        _run_generator()
        second_hash, second_files = _tree_digest()

        drifted = sorted(
            name for name in set(first_files) | set(second_files) if first_files.get(name) != second_files.get(name)
        )
        assert not drifted, (
            f"regeneration is not byte-identical; these artifacts changed between two consecutive runs: {drifted}"
        )
        assert first_hash == second_hash

    def test_token_map_carries_no_clock_reading(self) -> None:
        """No token is a timestamp, and every date is the committed one.

        This holds independently of how coarse a reintroduced clock would be:
        a run-to-run diff only catches clocks finer than the gap between runs,
        while a token that reads the date would still slip through until
        midnight. Pinning every date to ``paper.date`` closes that.
        """
        _run_generator()
        variables: dict[str, str] = json.loads(_TOKEN_JSON.read_text(encoding="utf-8"))

        committed_date = yaml.safe_load((_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))["paper"][
            "date"
        ]

        stamped = sorted(f"{token}={value}" for token, value in variables.items() if _DATETIME_RE.search(value))
        assert not stamped, f"token values contain a time of day: {stamped}"

        foreign_dates = sorted(
            f"{token}={value}"
            for token, value in variables.items()
            for match in _DATE_RE.findall(value)
            if match != committed_date
        )
        assert not foreign_dates, (
            f"token values contain a date other than committed paper.date ({committed_date}): {foreign_dates}"
        )


class TestCommittedBuildInputs:
    """The stamps the manuscript prints are committed, not discovered."""

    def test_python_requires_matches_pyproject(self) -> None:
        """``paper.python_requires`` must not drift from ``requires-python``."""
        config = yaml.safe_load((_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8"))
        declared = str(config["paper"]["python_requires"])

        pyproject = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'^requires-python\s*=\s*"([^"]+)"', pyproject, flags=re.MULTILINE)
        assert match is not None, "pyproject.toml declares no requires-python"
        assert declared == match.group(1)

    def test_generator_module_reads_no_clock(self) -> None:
        """A lexical backstop naming the exact APIs that caused the breach.

        Weaker than the byte comparison above and deliberately kept as a
        supplement, not a substitute: it fails fast and points at the line,
        where the byte comparison only reports that something moved.
        """
        source = (_ROOT / "src" / "casino_royale_1967" / "manuscript_variables.py").read_text(encoding="utf-8")
        banned = ("datetime.now", "time.time", "date.today", "platform.python_version")
        present = sorted(name for name in banned if name in source)
        assert not present, f"manuscript_variables.py reads runtime state: {present}"
