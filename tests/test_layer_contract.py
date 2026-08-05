"""Layer-contract tests — the pure domain core must not need ``bond_api``.

``README.md``, ``AGENTS.md`` and ``docs/architecture.md`` all claim that the
six domain modules are pure (stdlib + numpy) and stay importable when the
``bond-api`` path dependency is unavailable. A claim that nothing executes is
just prose, so this module executes it:

* a **subprocess** import of every domain module with ``bond_api`` forced to
  fail (a real ``ModuleNotFoundError``, injected through a meta-path finder —
  no mocking framework);
* a **source scan** asserting no domain module contains a ``bond_api`` or
  ``infrastructure`` import at all;
* an assertion that the lazy package ``__getattr__`` still resolves the
  adapter exports and still rejects unknown names.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
_PACKAGE = _SRC / "casino_royale_1967"

#: The pure domain modules — everything in ``src/`` except the adapter,
#: the manuscript generator (which imports the adapter's identity) and
#: ``__init__``.
DOMAIN_MODULES: tuple[str, ...] = (
    "baccarat_table",
    "coordination_farce",
    "dispatch_chaos",
    "escalation_ladder",
    "figures.plots",
    "identity_confusion",
    "spoof_analyzer",
)

# Blocks bond_api at the meta-path level, then imports the whole domain core.
_PROBE = """
import sys


class _BlockBondApi:
    @staticmethod
    def find_module(fullname, path=None):  # pragma: no cover - legacy hook
        return None

    @staticmethod
    def find_spec(fullname, path=None, target=None):
        if fullname == "bond_api" or fullname.startswith("bond_api."):
            raise ModuleNotFoundError("No module named 'bond_api'", name=fullname)
        return None


sys.meta_path.insert(0, _BlockBondApi)
for name in {modules!r}:
    __import__("casino_royale_1967." + name)
print("DOMAIN_CORE_IMPORTED")
"""


class TestDomainCoreIsBondApiFree:
    """The domain core imports with ``bond_api`` unavailable."""

    def test_domain_modules_import_without_bond_api(self) -> None:
        """A real subprocess import with ``bond_api`` blocked must succeed."""
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [sys.executable, "-c", _PROBE.format(modules=list(DOMAIN_MODULES))],
            cwd=str(_ROOT),
            env={"PYTHONPATH": str(_SRC), "PATH": "/usr/bin:/bin", "MPLBACKEND": "Agg"},
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert result.returncode == 0, f"domain core failed to import: {result.stderr}"
        assert "DOMAIN_CORE_IMPORTED" in result.stdout

    def test_probe_is_not_vacuous(self) -> None:
        """Positive control: the same probe must fail for the adapter.

        Without this, a broken blocker would let the test above pass for the
        wrong reason.
        """
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [sys.executable, "-c", _PROBE.format(modules=["mission"])],
            cwd=str(_ROOT),
            env={"PYTHONPATH": str(_SRC), "PATH": "/usr/bin:/bin", "MPLBACKEND": "Agg"},
            capture_output=True,
            text=True,
            timeout=180,
        )
        assert result.returncode != 0, "mission.py must FAIL to import without bond_api"
        assert "bond_api" in result.stderr

    @pytest.mark.parametrize("module_name", DOMAIN_MODULES)
    def test_domain_source_has_no_forbidden_imports(self, module_name: str) -> None:
        """No domain module may import ``bond_api`` or ``infrastructure``."""
        path = _PACKAGE / (module_name.replace(".", "/") + ".py")
        source = path.read_text(encoding="utf-8")
        offenders = re.findall(r"^\s*(?:from|import)\s+(bond_api|infrastructure)\b", source, re.MULTILINE)
        assert not offenders, f"{path.name} imports {offenders}"

    def test_scan_set_is_complete(self) -> None:
        """Guard against the scan above silently covering nothing."""
        on_disk = {
            path.stem
            for path in _PACKAGE.glob("*.py")
            if path.stem not in {"__init__", "mission", "manuscript_variables"}
        }
        assert on_disk == {name for name in DOMAIN_MODULES if "." not in name}
        assert len(DOMAIN_MODULES) > 1


class TestLazyAdapterExports:
    """The lazy package ``__getattr__`` preserves the public surface."""

    def test_adapter_exports_resolve(self) -> None:
        import casino_royale_1967 as package

        assert package.FILM == "casino_royale_1967"
        assert package.CODENAME == "FIVE 00s"
        assert package.MissionProvider().film == "casino_royale_1967"
        assert "roster" in package.GADGETS

    def test_unknown_attribute_raises(self) -> None:
        import casino_royale_1967 as package

        with pytest.raises(AttributeError, match="no attribute 'q_branch_jetpack'"):
            _ = package.q_branch_jetpack

    def test_dir_lists_lazy_exports(self) -> None:
        import casino_royale_1967 as package

        listed = dir(package)
        assert "MissionProvider" in listed
        assert "analyze_assignments" in listed
