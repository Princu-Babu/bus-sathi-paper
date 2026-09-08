"""
Tier 2 Integration Tests: a02_catchments.csv -> a03_index_weights.py & a04_class_count.py.

Contract:
- Input: data/derived/a02_catchments.csv (186 rows: New_Route_ID, Route_Type, geom_km, pop_net, pop_euclid).
- Guarantees valid numeric inputs for CDI calculation and Jenks tiering.
"""
from pathlib import Path
import pytest
import pandas as pd
from tests.conftest import DERIVED_DIR, EXPECTED_ACTIVE_ROUTES


@pytest.mark.tier2
def test_catchment_to_index_weights_contract():
    """Verify a02_catchments.csv fulfills input contract for a03_index_weights.py."""
    catch_path = DERIVED_DIR / "a02_catchments.csv"
    if not catch_path.exists():
        pytest.skip("a02_catchments.csv not yet generated")
        
    df = pd.read_csv(catch_path)
    assert len(df) == EXPECTED_ACTIVE_ROUTES, f"Must have {EXPECTED_ACTIVE_ROUTES} rows"
    
    # Must have non-null, non-negative population
    assert (df["pop_net"] >= 0).all(), "Net population must be non-negative"
    assert (df["pop_net"].notna()).all(), "Net population must have no nulls"
    
    # Check unique route IDs
    assert df["New_Route_ID"].nunique() == EXPECTED_ACTIVE_ROUTES, "New_Route_ID must be unique"


@pytest.mark.tier2
def test_catchment_pop_served_comparison():
    """Verify pop_euclid > pop_net for almost all routes (F8)."""
    catch_path = DERIVED_DIR / "a02_catchments.csv"
    if not catch_path.exists():
        pytest.skip("a02_catchments.csv not yet generated")
        
    df = pd.read_csv(catch_path)
    if "pop_euclid" in df.columns and "pop_net" in df.columns:
        overstated = df[df["pop_euclid"] > df["pop_net"]]
        # At least 180 of 186 routes must show overstatement (F8 states 184/186)
        assert len(overstated) >= 180, (
            f"Expected almost all routes to have Euclidean > Network, got {len(overstated)}/186"
        )
