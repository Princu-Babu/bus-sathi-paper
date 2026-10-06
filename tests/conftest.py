r"""
Central pytest configuration, fixtures, and assertion helpers for E:\kash-paper.
"""
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import re
import pytest
import pandas as pd

# Directory paths
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CACHE_DIR = DATA_DIR / "cache"
DERIVED_DIR = DATA_DIR / "derived"
PAPER_DIR = REPO_ROOT / "paper"
TABLES_DIR = PAPER_DIR / "tables"
FIGURES_DIR = PAPER_DIR / "figures"
ANALYSIS_DIR = REPO_ROOT / "analysis"
LOGS_DIR = REPO_ROOT / "logs"

# Research contract constants
EXPECTED_DISTRICTS = [
    "Anantnag", "Bandipore", "Baramulla", "Budgam", "Ganderbal",
    "Kulgam", "Kupwara", "Pulwama", "Shopian", "Srinagar"
]
EXPECTED_POPULATION = 6_584_762  # WorldPop 2026 UN-adjusted (also accepts 6_584_763)
EXPECTED_PLAN_ROWS = 644
EXPECTED_PERMIT_ROWS = 614
EXPECTED_SSCL_ROUTES = 30
EXPECTED_ACTIVE_ROUTES = 186
EXPECTED_MERGED_ROUTES = 458
EXPECTED_STATED_FLEET = 1011
RANDOM_SEED = 20260823

# Prohibited legacy phrases / patterns (when uncontextualized)
PROHIBITED_PATTERNS = [
    r"(?<![\d,.])342\s+(?:permits?|routes?)",   # 342 permits (not 1,342 or a page range)
    r"207\s+routes",
    r"(?<![\d.])39\s*%\s*(?:route\s*)?reduction",   # "39% reduction" and "39 % reduction"
    r"(?<![\d.])95\.7\s*%\s*(?:coverage)?",         # "95.7%" and "95.7 %"
    r"1,?009\s*(?:bus(?:es)?|fleet)",
    r"Srinagar\s+Metropolitan\s+City",
    r"validated\s+against\s+ridership",
]

# A paragraph may mention a barred figure only if it is an explicit editorial callout, i.e. it carries
# one of these literal markers. Generic words such as "prior", "inherited" or "claim" no longer exempt
# a paragraph (they let uncontextualised uses through).
EDITORIAL_CALLOUT_MARKERS = [
    "[retired-figure]",
    "<!-- retired-figure -->",
    "retired figure:",
]
CONTEXT_EXCLUSION_WORDS = EDITORIAL_CALLOUT_MARKERS   # legacy name kept for importers


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "tier1: Tier 1 smoke and unit tests")
    config.addinivalue_line("markers", "tier2: Tier 2 component integration tests")
    config.addinivalue_line("markers", "tier3: Tier 3 system and pairwise tests")
    config.addinivalue_line("markers", "tier4: Tier 4 end-to-end real world scenarios")
    config.addinivalue_line("markers", "checker_a: Checker A Scope and Data Integrity audit")
    config.addinivalue_line("markers", "checker_b: Checker B Numerical Reproducibility audit")
    config.addinivalue_line("markers", "checker_c: Checker C GPS Validation audit")
    config.addinivalue_line("markers", "checker_d: Checker D Methodological Rigour audit")
    config.addinivalue_line("markers", "checker_e: Checker E Manuscript Claims audit")
    config.addinivalue_line("markers", "checker_f: Checker F Clean Release Gate audit")
    config.addinivalue_line("markers", "quick: Fast-running tests for CI/quick-run")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def data_raw() -> Path:
    return RAW_DIR


@pytest.fixture(scope="session")
def data_derived() -> Path:
    return DERIVED_DIR


@pytest.fixture(scope="session")
def data_cache() -> Path:
    return CACHE_DIR


@pytest.fixture(scope="session")
def paper_dir() -> Path:
    return PAPER_DIR


@pytest.fixture(scope="session")
def plan_df() -> pd.DataFrame:
    """Full published plan (644 rows)."""
    p = RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv"
    assert p.exists(), f"Missing plan CSV at {p}"
    return pd.read_csv(p)


@pytest.fixture(scope="session")
def active_df(plan_df: pd.DataFrame) -> pd.DataFrame:
    """186 active routes."""
    active = plan_df[plan_df["Action_Taken"].isin(["UPGRADED_TO_TRUNK", "RETAINED_AS_FEEDER"])].copy()
    active.reset_index(drop=True, inplace=True)
    return active


@pytest.fixture(scope="session")
def permits_df() -> pd.DataFrame:
    """614 baseline permits."""
    p = RAW_DIR / "existing-routes.csv"
    assert p.exists(), f"Missing permits CSV at {p}"
    return pd.read_csv(p)


@pytest.fixture(scope="session")
def reality_check_df() -> pd.DataFrame:
    """GPS reality check corridor dataset."""
    p = RAW_DIR / "gps" / "reality_check.csv"
    assert p.exists(), f"Missing reality check CSV at {p}"
    return pd.read_csv(p)


@pytest.fixture(scope="session")
def corridor_profiles_df() -> pd.DataFrame:
    """GPS corridor profiles dataset."""
    p = RAW_DIR / "gps" / "corridor_profiles.csv"
    assert p.exists(), f"Missing corridor profiles CSV at {p}"
    return pd.read_csv(p)


def check_no_legacy_strings(text: str, context: str = "") -> list[str]:
    """
    Search text for uncontextualized legacy metrics.
    Returns list of violations found.
    Allows matches only inside an explicit editorial callout (see EDITORIAL_CALLOUT_MARKERS).
    """
    violations = []
    paragraphs = text.split("\n\n")
    for p_num, p in enumerate(paragraphs, start=1):
        p_clean = p.strip()
        if not p_clean:
            continue
        p_lower = p_clean.lower()
        
        # If paragraph explicitly acknowledges obsolescence/negation/warning, permit it
        if any(w in p_lower for w in CONTEXT_EXCLUSION_WORDS):
            continue
            
        for pat in PROHIBITED_PATTERNS:
            if re.search(pat, p_clean, re.IGNORECASE):
                snippet = p_clean.replace("\n", " ")[:120]
                violations.append(f"{context} (para {p_num}): Pattern '{pat}' matched in: {snippet}")
    return violations
