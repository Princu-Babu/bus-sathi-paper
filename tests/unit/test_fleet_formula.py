"""
Tier 1 Unit Tests: Fleet Sizing Formula Contract.

Formula:
operating = max(1, ceil(cycle_min / max(1, headway_min)))
fleet = max(max(1, ceil(operating * 1.15)), 1 if route_type == 'Regional_District' else 2)
"""
import math
import pytest


def calc_fleet(cycle_min: float, headway_min: float, route_type: str) -> tuple[int, int]:
    operating = max(1, math.ceil(cycle_min / max(1.0, headway_min)))
    min_floor = 1 if route_type == "Regional_District" else 2
    fleet = max(max(1, math.ceil(operating * 1.15)), min_floor)
    return operating, fleet


@pytest.mark.tier1
@pytest.mark.quick
def test_fleet_formula_basic():
    """Verify basic operational calculation."""
    # cycle = 60 min, headway = 20 min -> operating = ceil(60/20) = 3
    # fleet = max(ceil(3 * 1.15), 2) = max(4, 2) = 4
    operating, fleet = calc_fleet(60.0, 20.0, "Urban")
    assert operating == 3
    assert fleet == 4


@pytest.mark.tier1
@pytest.mark.quick
def test_fleet_formula_urban_floor():
    """Urban routes must enforce minimum fleet floor of 2."""
    operating, fleet = calc_fleet(10.0, 35.0, "Urban")
    assert operating == 1
    assert fleet == 2


@pytest.mark.tier1
@pytest.mark.quick
def test_published_regional_fleet_counts(active_df):
    """Inspect actual non-SSCL published Regional_District routes."""
    reg = active_df[
        (active_df["Route_Type"] == "Regional_District") &
        (~active_df["New_Route_ID"].astype(str).str.startswith("SSCL-"))
    ]
    assert len(reg) > 0
    # Every published non-SSCL fleet count matches our formula exactly
    for _, r in reg.iterrows():
        cycle = float(r["Cycle_Time_Min"])
        headway = float(r["Headway_Min"])
        published = int(r["Fleet_Required"])
        _, calc = calc_fleet(cycle, headway, "Regional_District")
        assert calc == published, f"Mismatch on {r['New_Route_ID']}"


@pytest.mark.tier1
@pytest.mark.quick
def test_fleet_monotonicity_cycle():
    """Fleet must be non-decreasing with increasing cycle time."""
    headway = 20.0
    route_type = "Urban"
    prev_fleet = 0
    for cycle in range(10, 300, 10):
        _, fl = calc_fleet(float(cycle), headway, route_type)
        assert fl >= prev_fleet, f"Monotonicity violated at cycle={cycle}: {fl} < {prev_fleet}"
        prev_fleet = fl


@pytest.mark.tier1
@pytest.mark.quick
def test_fleet_monotonicity_headway():
    """Fleet must be non-increasing with increasing headway."""
    cycle = 120.0
    route_type = "Urban"
    prev_fleet = 999
    for headway in [5.0, 10.0, 15.0, 20.0, 30.0, 35.0, 50.0]:
        _, fl = calc_fleet(cycle, headway, route_type)
        assert fl <= prev_fleet, f"Monotonicity violated at headway={headway}: {fl} > {prev_fleet}"
        prev_fleet = fl
