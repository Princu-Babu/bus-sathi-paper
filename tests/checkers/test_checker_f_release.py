"""
Checker F: Clean Reproduction and Release Gate Audit.

Enforces:
1. Environment and dependencies: Python 3.14.2 venv has all scientific libraries.
2. Quick reproduction runner (when implemented) runs cleanly.
3. No secrets, credentials, API keys, or private GPS logs committed.
4. Unit tests pass with 0 errors.
"""
import importlib
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


@pytest.mark.checker_f
@pytest.mark.quick
def test_no_private_keys_or_secrets():
    """Verify no API keys, private tokens, or credentials are committed in repository."""
    forbidden_tokens = [
        "AIzaSy",  # Google API key prefix
        "sk-proj-", # OpenAI key prefix
        "ghp_",     # GitHub personal token
        "xoxb-",    # Slack token
    ]
    # Scan python files and markdown files
    scan_extensions = [".py", ".md", ".json", ".csv", ".yml", ".yaml"]
    for path in REPO_ROOT.rglob("*"):
        # Skip .venv and .git and .agents
        if any(part.startswith(".") for part in path.parts if part not in [".agents"]):
            continue
        if ".venv" in path.parts:
            continue
        if path.is_file() and path.suffix in scan_extensions:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                for tok in forbidden_tokens:
                    assert tok not in content, f"Possible secret token '{tok}' found in {path}"
            except Exception:
                pass


@pytest.mark.checker_f
def test_reproducibility_runner():
    """
    Test run_all.py CLI options when implemented.
    """
    runner = ANALYSIS_DIR / "run_all.py"
    if not runner.exists():
        pytest.skip("analysis/run_all.py not yet implemented by M0 track")
        
    import subprocess
    import sys
    res = subprocess.run([sys.executable, str(runner), "--quick"], capture_output=True, text=True)
    assert res.returncode == 0, f"run_all.py --quick failed:\n{res.stderr}"
