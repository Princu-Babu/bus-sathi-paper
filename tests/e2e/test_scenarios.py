"""
Tier 4 E2E Tests: Real-World Application Scenarios (Scenarios 1-5).
"""
import json
import math
from pathlib import Path
import pytest
import pandas as pd
from tests.conftest import (
    REPO_ROOT,
    RAW_DIR,
    DERIVED_DIR,
    EXPECTED_DISTRICTS,
    EXPECTED_PLAN_ROWS,
    EXPECTED_PERMIT_ROWS,
    EXPECTED_ACTIVE_ROUTES,
    EXPECTED_STATED_FLEET,
    EXPECTED_POPULATION,
)


@pytest.mark.tier4
def test_scenario_2_baseline_scope_invariants(plan_df, permits_df, active_df):
    """
    Scenario 2: Baseline Scope and Data Invariant Verification.
    Verifies that the entire network baseline satisfies the Kashmir Division research contract.
    """
    assert len(plan_df) == EXPECTED_PLAN_ROWS
    assert len(permits_df) == EXPECTED_PERMIT_ROWS
    assert len(active_df) == EXPECTED_ACTIVE_ROUTES
    assert active_df["Fleet_Required"].sum() == EXPECTED_STATED_FLEET
    
    # Verify population column exists and sums reasonably
    assert "Population_Served" in active_df.columns
    # Check that route types are correctly mapped
    valid_types = {"Urban", "Peri_Urban", "Regional_District"}
    assert set(active_df["Route_Type"].unique()).issubset(valid_types)


@pytest.mark.tier4
def test_scenario_3_supply_side_gps_and_fleet_reproduction(active_df, reality_check_df):
    """
    Scenario 3: Supply-Side Observational GPS & Fleet Sizing Validation.
    Verifies fleet reproduction across all eligible active routes and GPS corridor groupings.
    """
    non_sscl = active_df[~active_df["New_Route_ID"].astype(str).str.startswith("SSCL-")]
    assert len(non_sscl) == 156
    
    # 0 mismatches: the production fleet model (analysis/fleet_model.py), not a re-typed formula
    from analysis import fleet_model as fm
    arr = fm.load_arrays()
    calc = fm.fleet(arr)
    mismatches = int((calc[~arr.sscl] != arr.fleet_pub[~arr.sscl]).sum())
    assert int((~arr.sscl).sum()) == 156
    assert mismatches == 0, f"Expected 0 mismatches, found {mismatches}"
    
    # Verify GPS groupings
    assert len(reality_check_df[reality_check_df["klass"] == "matched"]) == 5
    assert len(reality_check_df[reality_check_df["klass"] == "partial"]) == 9


@pytest.mark.tier4
def test_scenario_4_spatial_accessibility_and_walkshed_f8():
    """
    Scenario 4: Spatial Accessibility & Walk Catchment Overstatement (F8).
    Verifies that Euclidean catchments overstate network walk catchments by approximately one-third.
    """
    f_json = DERIVED_DIR / "a02_network_catchments.json"
    if not f_json.exists():
        pytest.skip("a02_network_catchments.json not yet generated")
        
    with f_json.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
        
    # The module's figures must equal an independent recomputation from the per-route CSV and the
    # union populations it reports (a module bug cannot hide behind a wide tolerance band).
    csv = pd.read_csv(DERIVED_DIR / "a02_catchments.csv")
    assert data["n_routes"] == len(csv) == EXPECTED_ACTIVE_ROUTES
    assert data["overstatement_pct_median"] == pytest.approx(
        float(((csv["pop_euclid"] - csv["pop_net"]) / csv["pop_euclid"] * 100).median()), abs=1e-9)
    assert data["coverage_share_euclid"] == pytest.approx(data["pop_euclid_union"] / EXPECTED_POPULATION, rel=1e-6)
    assert data["coverage_share_net"] == pytest.approx(data["pop_net_union"] / EXPECTED_POPULATION, rel=1e-6)
    assert data["pop_euclid_union"] > data["pop_net_union"] > 0


@pytest.mark.tier4
def test_scenario_5_uncertainty_parameters_coverage():
    """
    Scenario 5: Multi-Channel Decision Robustness & Uncertainty Parameters.
    Verifies parameter coverage across the 10 predeclared parameter distributions.
    """
    import analysis.common as C
    params = C.PARAMETERS
    assert len(params) >= 10, f"Expected at least 10 predeclared parameters, found {len(params)}"
    for name, spec in params.items():
        assert "dist" in spec, f"Parameter {name} must have a declared sampling distribution"
        assert spec["dist"] in ("unif", "tri"), f"Unknown distribution {spec['dist']} for {name}"
