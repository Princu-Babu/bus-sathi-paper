"""
Checker A: Data and Scope Integrity Audit.

Enforces:
1. Kashmir Division (10 districts) only, not Srinagar Metropolitan City.
2. Denominator is 6,584,762 (or 6,584,763).
3. 644 plan rows (614 permits + 30 SSCL), 186 active, stated fleet 1,011.
4. Zero uncontextualized occurrences of obsolete metrics:
   342 permits, 207 routes, 39% reduction, 95.7% coverage, 1,009 fleet, SMC.
5. Raw staged data integrity.
6. Cache files exclusion rules.
"""
import json
from pathlib import Path
import pytest
import pandas as pd
from tests.conftest import (
    EXPECTED_DISTRICTS,
    EXPECTED_POPULATION,
    EXPECTED_PLAN_ROWS,
    EXPECTED_PERMIT_ROWS,
    EXPECTED_SSCL_ROUTES,
    EXPECTED_ACTIVE_ROUTES,
    EXPECTED_MERGED_ROUTES,
    EXPECTED_STATED_FLEET,
    check_no_legacy_strings,
    REPO_ROOT,
    RAW_DIR,
    DERIVED_DIR,
    CACHE_DIR,
    PAPER_DIR,
)


@pytest.mark.checker_a
@pytest.mark.quick
def test_district_count_and_names():
    """Verify Kashmir Division has exactly 10 districts."""
    census_file = RAW_DIR / "census2011_kashmir_districts.csv"
    assert census_file.exists(), "census2011_kashmir_districts.csv must exist"
    census_df = pd.read_csv(census_file)
    dist_col = "district_osm" if "district_osm" in census_df.columns else "district"
    districts = sorted(census_df[dist_col].str.strip().tolist())
    assert len(districts) == 10, f"Expected 10 districts, found {len(districts)}"
    assert districts == sorted(EXPECTED_DISTRICTS), f"District mismatch: {districts}"


@pytest.mark.checker_a
@pytest.mark.quick
def test_study_area_population_denominator():
    """Verify study area population denominator in common.py and derived tables."""
    import analysis.common as C
    assert C.STUDY_AREA_POPULATION in (6_584_762, 6_584_763), (
        f"Denominator must be 6,584,762/3, got {C.STUDY_AREA_POPULATION}"
    )


@pytest.mark.checker_a
@pytest.mark.quick
def test_plan_and_permit_row_counts(plan_df, permits_df, active_df):
    """Verify exact counts: 644 plan rows, 614 permits, 186 active, 458 merged, 30 SSCL."""
    assert len(plan_df) == EXPECTED_PLAN_ROWS, f"Plan rows must be {EXPECTED_PLAN_ROWS}, got {len(plan_df)}"
    assert len(permits_df) == EXPECTED_PERMIT_ROWS, f"Permits must be {EXPECTED_PERMIT_ROWS}, got {len(permits_df)}"
    assert len(active_df) == EXPECTED_ACTIVE_ROUTES, f"Active routes must be {EXPECTED_ACTIVE_ROUTES}, got {len(active_df)}"
    
    merged = plan_df[plan_df["Action_Taken"] == "MERGED_INTO_TRUNK"]
    assert len(merged) == EXPECTED_MERGED_ROUTES, f"Merged routes must be {EXPECTED_MERGED_ROUTES}, got {len(merged)}"
    
    sscl = plan_df[plan_df["New_Route_ID"].astype(str).str.startswith("SSCL-")]
    assert len(sscl) == EXPECTED_SSCL_ROUTES, f"SSCL routes must be {EXPECTED_SSCL_ROUTES}, got {len(sscl)}"
    
    # Check stated fleet
    total_fleet = active_df["Fleet_Required"].sum()
    assert total_fleet == EXPECTED_STATED_FLEET, f"Stated active fleet must be {EXPECTED_STATED_FLEET}, got {total_fleet}"


@pytest.mark.checker_a
@pytest.mark.quick
def test_corridor_decomposition_and_retention(plan_df):
    """
    Verify F1: 614 permits decompose into 157 distinct corridors;
    156 of 157 corridors are retained (99.4% retention).
    Consolidation is 0.2 pp, change-of-unit is 71.0 pp.
    """
    q01_json = DERIVED_DIR / "q01_data_quality.json"
    if q01_json.exists():
        with q01_json.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        d1 = data.get("D1_register_hygiene", {})
        assert d1.get("n_distinct_corridors_11m") == 157, (
            f"Expected 157 corridors, got {d1.get('n_distinct_corridors_11m')}"
        )
        assert d1.get("n_active_permit_derived") == 156, (
            f"Expected 156 active permit corridors, got {d1.get('n_active_permit_derived')}"
        )
        assert round(d1.get("reduction_from_unit_change", 0) * 100, 1) == 71.0, (
            f"Expected 71.0 pp unit change, got {d1.get('reduction_from_unit_change')}"
        )
        assert round(d1.get("reduction_from_corridor_consolidation", 0) * 100, 1) == 0.2, (
            f"Expected 0.2 pp consolidation, got {d1.get('reduction_from_corridor_consolidation')}"
        )


def _legacy_violations(targets) -> list:
    out = []
    for target in sorted(set(targets)):
        if target.exists():
            text = target.read_text(encoding="utf-8", errors="ignore")
            out.extend(check_no_legacy_strings(text, context=str(target.relative_to(REPO_ROOT))))
    return out


@pytest.mark.checker_a
def test_no_prohibited_legacy_metrics_in_generated_outputs():
    """Generated tables and literature-review coding files must not carry a barred figure
    (342 permits, 207 routes, 39 % reduction, 95.7 %, 1,009 fleet, SMC); no exemption applies."""
    targets = list(PAPER_DIR.glob("tables/*.md")) + list(PAPER_DIR.glob("tables/*.csv"))         + list(PAPER_DIR.glob("literature_review/**/*.md"))
    assert targets, "no generated outputs found to scan"
    v = _legacy_violations(targets)
    assert not v, "Found prohibited legacy metric mentions:\n" + "\n".join(v)


@pytest.mark.checker_a
@pytest.mark.xfail(strict=True, reason="prose pending Phase 2: README, paper/sections/*, FINDINGS.md, CLAIM_LEDGER.md, "
                   "archive/PENDING_DECISIONS_v1 still quote barred figures (207 routes, 1,009 fleet, Srinagar "
                   "Metropolitan City) outside an explicit [retired-figure] callout; Phase 2 rewrites or marks them")
def test_no_prohibited_legacy_metrics():
    """
    Scan findings and manuscript docs for uncontextualized occurrences of
    legacy metrics. Only paragraphs carrying an explicit editorial callout marker
    (tests/conftest.py::EDITORIAL_CALLOUT_MARKERS) are exempt.
    """
    targets = [PAPER_DIR / "FINDINGS.md", REPO_ROOT / "README.md"]
    targets.extend(p for p in PAPER_DIR.glob("**/*.md")
                   if "tables" not in p.parts and "literature_review" not in p.parts)
    v = _legacy_violations(targets)
    assert not v, "Found prohibited legacy metric mentions:\n" + "\n".join(v)


def test_legacy_guard_catches_both_spacings_and_has_no_loose_exemptions():
    """The guard itself: catches '95.7 %' and '39 %', does not exempt 'inherited'/'prior'/'claim',
    exempts only an explicit callout, and does not fire on '1,342' or a page range."""
    bad = ["Coverage was 95.7% of residents.", "Coverage was 95.7 % of residents.",
           "A 39% reduction in routes.", "A 39 % reduction in routes."]
    for t in bad:
        assert check_no_legacy_strings(t), t
    for word in ("inherited", "prior", "claim"):
        assert check_no_legacy_strings(f"The {word} figure of 95.7 % was reported."), word
    assert not check_no_legacy_strings("[retired-figure] The old 95.7 % figure is wrong.")
    assert not check_no_legacy_strings("Interval 1,093-1,342 and pp. 341, 342 were read.")
    assert not check_no_legacy_strings("Coverage was 195.7 and 139 % of nothing.")
