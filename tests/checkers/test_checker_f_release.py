"""
Checker F: Clean Reproduction and Release Gate Audit.

Enforces:
1. Environment and dependencies: Python 3.14.2 venv has all scientific libraries.
2. Quick reproduction runner (when implemented) runs cleanly.
3. No secrets, credentials, API keys, or private GPS logs committed.
4. Unit tests pass with 0 errors.
"""
import importlib
import re
from pathlib import Path
import pytest
from tests.conftest import (
    REPO_ROOT,
    ANALYSIS_DIR,
)


@pytest.mark.checker_f
@pytest.mark.quick
def test_scientific_dependencies_installed():
    """Verify all critical scientific libraries are installed in the venv."""
    required_packages = [
        "geopandas",
        "rasterio",
        "shapely",
        "sklearn",
        "jenkspy",
        "statsmodels",
        "networkx",
        "SALib",
        "esda",
        "libpysal",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "rasterstats",
        "pytest",
    ]
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError as exc:
            pytest.fail(f"Required package '{pkg}' is not installed: {exc}")


def _forbidden_patterns() -> dict:
    return {
        "google": re.compile("AIza" + "Sy" + r"[0-9A-Za-z_-]{30,}"),
        "openai": re.compile("sk-" + "proj-" + r"[0-9A-Za-z_-]{20,}"),
        "github": re.compile("gh" + "p_" + r"[0-9A-Za-z]{30,}"),
        "slack": re.compile("xox" + "b-" + r"[0-9A-Za-z-]{10,}"),
    }


def _token_hits(content: str, patterns: dict) -> list:
    return [name for name, rx in patterns.items() if rx.search(content)]


@pytest.mark.checker_f
@pytest.mark.quick
def test_no_private_keys_or_secrets():
    """Verify no API keys, private tokens, or credentials are committed in repository."""
    # Patterns = key prefix + the characters a real key carries after it, so a report that merely
    # mentions a prefix does not trip the scan. Prefixes are built from halves so this file never
    # contains a live-looking key prefix itself.
    forbidden = _forbidden_patterns()
    n_scanned = 0
    hits = []
    scan_extensions = [".py", ".md", ".json", ".csv", ".yml", ".yaml", ".txt", ".toml", ".cfg", ".ini", ".html"]
    for path in REPO_ROOT.rglob("*"):
        rel = path.relative_to(REPO_ROOT).parts
        # skip dot-directories (.git, .venv, ...), the audit working folder and caches
        if any(part.startswith(".") for part in rel if part != ".agents"):
            continue
        if rel[0] in ("audit", "node_modules") or "__pycache__" in rel:
            continue
        if path.is_file() and path.suffix in scan_extensions:
            if path.resolve() == Path(__file__).resolve():
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")   # no blanket except: a read error must fail
            n_scanned += 1
            hits.extend(f"{name} in {path}" for name in _token_hits(content, forbidden))
    assert n_scanned > 50, f"secret scan looked at only {n_scanned} files; the walk is broken"
    assert not hits, "Possible secret tokens committed:" + chr(10) + chr(10).join(hits)


def test_secret_scan_can_fail():
    """The scanner's matching rule flags planted tokens and passes clean or prefix-only text."""
    forbidden = _forbidden_patterns()
    planted = {
        "google": "AIza" + "Sy" + "a" * 35,
        "openai": "sk-" + "proj-" + "b" * 30,
        "github": "gh" + "p_" + "c" * 36,
        "slack": "xox" + "b-" + "1234567890-abcdef",
    }
    for name, tok in planted.items():
        assert _token_hits(f"KEY = '{tok}'", forbidden) == [name], name
    assert _token_hits("the prefix " + "gh" + "p_ is mentioned in prose", forbidden) == []
    assert _token_hits("nothing secret here", forbidden) == []


@pytest.mark.checker_f
def test_reproducibility_runner():
    """
    Test run_all.py CLI options when implemented.
    """
    runner = ANALYSIS_DIR / "run_all.py"
    assert runner.exists(), "analysis/run_all.py is missing"
        
    import subprocess
    import sys
    # --dry-run only prints the plan: a real --quick run rewrites derived outputs and belongs to the
    # release procedure, not to the test suite (the suite must write nothing tracked).
    res = subprocess.run([sys.executable, str(runner), "--quick", "--dry-run"], capture_output=True, text=True)
    assert res.returncode == 0, f"run_all.py --quick --dry-run failed:\n{res.stderr}"
    order = [ln.split()[3] for ln in res.stdout.splitlines() if ln.strip()[:1].isdigit() and "Stage" in ln]
    for needed in ("q01_data_quality", "q02_fleet_baseline", "a02_summary", "a09_monte_carlo_sobol", "a04_class_count"):
        assert needed in order, f"{needed} missing from the --quick plan: {order}"
    assert order.index("q01_data_quality") < order.index("q02_fleet_baseline")
    assert order.index("a09_monte_carlo_sobol") < order.index("a04_class_count"), "a04 must re-run after a09"
    assert order.index("a02_summary") < order.index("a02b_faithfulness")
    assert "a02_network_catchments" not in order and "a08a_catchment_grid" not in order  # heavy builds excluded
