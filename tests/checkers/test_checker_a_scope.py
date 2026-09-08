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


@pytest.mark.checker_a
def test_no_prohibited_legacy_metrics():
    """
    Scan findings and manuscript docs for uncontextualized occurrences of
    legacy metrics (342, 207 routes, 39% reduction, 95.7% coverage, 1,009 fleet, SMC).
    """
    targets = [
        PAPER_DIR / "FINDINGS.md",
        REPO_ROOT / "README.md",
    ]
    # Also scan any draft markdown files under paper/
    targets.extend(PAPER_DIR.glob("**/*.md"))
    
    all_violations = []
    for target in set(targets):
        if target.exists():
            text = target.read_text(encoding="utf-8", errors="ignore")
            violations = check_no_legacy_strings(text, context=str(target.relative_to(REPO_ROOT)))
            all_violations.extend(violations)
            
    assert not all_violations, "Found prohibited legacy metric mentions:\n" + "\n".join(all_violations)


@pytest.mark.checker_a
@pytest.mark.quick
def test_raw_data_manifest_and_staged_inputs():
    """Verify all critical raw staged files exist under data/raw."""
    critical_files = [
        RAW_DIR / "Rationalised_Routes_Kashmir_v3.csv",
        RAW_DIR / "Rationalised_Routes_Kashmir_v3.geojson",
        RAW_DIR / "existing-routes.csv",
        RAW_DIR / "pois.csv",
        RAW_DIR / "kashmir_worldpop.tif",
        RAW_DIR / "kashmir_districts_osm.geojson",
        RAW_DIR / "kashmir_tehsils_osm.geojson",
        RAW_DIR / "Kashmir_Stops_Master_v4.csv",
        RAW_DIR / "Hourly_Passenger_Count.csv",
        RAW_DIR / "chalo_ridership.csv",
        RAW_DIR / "chalo_deployed_buses.csv",
        RAW_DIR / "census2011_kashmir_districts.csv",
        RAW_DIR / "gps" / "reality_check.csv",
        RAW_DIR / "gps" / "corridor_profiles.csv",
        RAW_DIR / "gps" / "route_evidence.csv",
        RAW_DIR / "gps" / "permit_observed.csv",
    ]
    for f in critical_files:
        assert f.exists(), f"Missing required staged input: {f}"
        assert f.stat().st_size > 0, f"Raw input is empty: {f}"
