"""
Tier 1 Unit Tests: Data Schemas and Table Column Integrity.
"""
from pathlib import Path
import pytest
import pandas as pd
from tests.conftest import (
    RAW_DIR,
    DERIVED_DIR,
)


@pytest.mark.tier1
@pytest.mark.quick
def test_plan_csv_schema(plan_df):
    """Verify Rationalised_Routes_Kashmir_v3.csv contains all mandatory planning fields."""
    mandatory_cols = [
        "Route_ID", "Route_Name", "Action_Taken", "New_Route_ID",
        "Route_KM", "Route_Type", "Cycle_Time_Min", "Headway_Min",
        "Fleet_Required", "Population_Served", "Final_CDI"
    ]
    for col in mandatory_cols:
        assert col in plan_df.columns, f"Mandatory column {col} missing from plan CSV"


@pytest.mark.tier1
@pytest.mark.quick
def test_permits_csv_schema(permits_df):
    """Verify existing-routes.csv schema."""
    mandatory_cols = [
        "Route_Name", "Origin", "Destination", "Vehicle_Category", "Service_Type"
    ]
    for col in mandatory_cols:
        assert col in permits_df.columns, f"Mandatory column {col} missing from permits CSV"


@pytest.mark.tier1
@pytest.mark.quick
def test_hourly_passenger_schema():
    """Verify Hourly_Passenger_Count.csv exists and contains standard operational columns."""
    pax_path = RAW_DIR / "Hourly_Passenger_Count.csv"
    assert pax_path.exists(), "Hourly_Passenger_Count.csv missing"
    
    # Header is on row 2 (skiprows=1)
    df = pd.read_csv(pax_path, skiprows=1)
    assert len(df) > 0, "Hourly_Passenger_Count.csv is empty"
    expected_cols = ["DATE", "Hours", "Passenger Count", "Total Collection"]
    for col in expected_cols:
        assert col in df.columns, f"Missing {col} in Hourly_Passenger_Count.csv"


@pytest.mark.tier1
@pytest.mark.quick
def test_derived_catchments_schema():
    """Verify a02_catchments.csv schema if generated."""
    p = DERIVED_DIR / "a02_catchments.csv"
    if not p.exists():
        pytest.skip("a02_catchments.csv not yet generated")
        
    df = pd.read_csv(p)
    assert len(df) == 186, f"Expected 186 active route rows in a02_catchments, got {len(df)}"
    mandatory_cols = [
        "New_Route_ID", "Route_Type", "pop_net", "pop_euclid"
    ]
    for col in mandatory_cols:
        assert col in df.columns, f"Missing {col} in a02_catchments.csv"


@pytest.mark.tier1
@pytest.mark.quick
def test_derived_corridor_comparison_schema():
    """Verify v04_corridor_comparison.csv schema if generated."""
    p = DERIVED_DIR / "v04_corridor_comparison.csv"
    if not p.exists():
        pytest.skip("v04_corridor_comparison.csv not yet generated")
        
    df = pd.read_csv(p)
    assert len(df) == 14, f"Expected 14 corridor rows, got {len(df)}"
    mandatory_cols = [
        "corridor", "route", "klass", "obs_km", "eng_km", "obs_oneway_min", "plan_oneway_min"
    ]
    for col in mandatory_cols:
        assert col in df.columns, f"Missing {col} in v04_corridor_comparison.csv"
