"""
Phase-1 fix tests for work package D (a14 cost/emissions, a15 scenarios and funding
sequence, a16 peer regression and per-population ratios).

Quantities are recomputed from the published plan CSV, the peer-city input file and
the upstream module outputs, then compared with what the modules emitted.
"""
import json
import sys

import numpy as np
import pandas as pd
import pytest

from tests.conftest import ANALYSIS_DIR, DERIVED_DIR, RAW_DIR, TABLES_DIR

sys.path.insert(0, str(ANALYSIS_DIR))

import common as C  # noqa: E402


def _j(name):
    return json.loads((DERIVED_DIR / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def a14():
    return _j("a14_cost_emissions")


@pytest.fixture(scope="module")
def a15():
    return _j("a15_scenarios")


@pytest.fixture(scope="module")
def a16():
    return _j("a16_peer_regression")


@pytest.fixture(scope="module")
def plan():
    return C.load_active()


# ── a14 ─────────────────────────────────────────────────────────────────────────
def test_a14_class_counts_match_plan(a14, plan):
    for cls, col in (("HPV", "HPV_Count"), ("MPV", "MPV_Count"), ("LPV", "LPV_Count")):
        assert a14["vehicle_classes"][cls]["n_buses"] == int(plan[col].sum())
        assert a14["bases"]["PLAN"]["by_class"][cls]["n_buses"] == int(plan[col].sum())
    assert sum(v["n_buses"] for v in a14["vehicle_classes"].values()) == int(plan["Fleet_Required"].sum())


@pytest.mark.parametrize("basis", ["PLAN", "OBSERVED", "PLAN_TRIPS_X_LENGTH"])
def test_a14_class_costs_sum_to_total(a14, basis):
    b = a14["bases"][basis]
    lo = hi = km = co2lo = co2hi = 0.0
    for cls, r in b["by_class"].items():
        rate_lo, rate_hi = r["cost_rate_inr_per_km"]
        # each class cost is its own km times its own rate (low with low, high with high)
        assert r["cost_inr_per_year"][0] == pytest.approx(r["vehicle_km_per_year"] * rate_lo, rel=1e-9)
        assert r["cost_inr_per_year"][1] == pytest.approx(r["vehicle_km_per_year"] * rate_hi, rel=1e-9)
        lo += r["cost_inr_per_year"][0]
        hi += r["cost_inr_per_year"][1]
        km += r["vehicle_km_per_year"]
        co2lo += r["co2_t_per_year"][0]
        co2hi += r["co2_t_per_year"][1]
    assert b["cost_inr_per_year"][0] == pytest.approx(lo, rel=1e-9)
    assert b["cost_inr_per_year"][1] == pytest.approx(hi, rel=1e-9)
    assert b["vehicle_km_per_year"] == pytest.approx(km, rel=1e-9)
    assert b["co2_t_per_year"] == [pytest.approx(co2lo, rel=1e-9), pytest.approx(co2hi, rel=1e-9)]
    assert b["cost_inr_per_year"][0] < b["cost_inr_per_year"][1]


def test_a14_mpv_not_priced_as_full_size(a14):
    b = a14["bases"]["PLAN"]
    hpv_rate = b["by_class"]["HPV"]["cost_rate_inr_per_km"]
    lpv_rate = b["by_class"]["LPV"]["cost_rate_inr_per_km"]
    mpv_rate = b["by_class"]["MPV"]["cost_rate_inr_per_km"]
    assert mpv_rate == [pytest.approx((hpv_rate[0] + lpv_rate[0]) / 2),
                        pytest.approx((hpv_rate[1] + lpv_rate[1]) / 2)]
    assert mpv_rate != hpv_rate
    sens = b["mpv_pricing_sensitivity"]
    # ordering of the bracket: MPV as LPV < midpoint < MPV as HPV
    assert (sens["mpv_priced_as_lpv"]["cost_inr_per_year"][1]
            < b["cost_inr_per_year"][1] < sens["mpv_priced_as_hpv"]["cost_inr_per_year"][1])


def test_a14_every_constant_has_verified_flag_and_assumptions_are_labelled(a14):
    assert len(a14["constants_table"]) >= 8
    for row in a14["constants_table"]:
        assert row.get("verified") in (True, False, "press"), row["constant"]
        assert row["source"], row["constant"]
        assert "unit" in row and "low" in row and "high" in row
        if row["source"] == "assumption":
            assert row["verified"] is False
            assert row["source_status"] == "assumption"
    for k, v in a14["constants"].items():
        if isinstance(v, dict):
            assert v.get("verified") in (True, False, "press"), k
    names = {r["constant"] for r in a14["constants_table"]}
    assert {"diesel_kmpl_mpv", "cost_inr_per_km_mpv"} <= names


def test_a14_exclusions_and_daily_km_basis_stated(a14, plan):
    ex = " ".join(a14["exclusions"]).lower()
    for word in ("crew", "capital", "depot", "charging"):
        assert word in ex
    d = a14["daily_km_assumption"]
    # recompute the plan's own trips x length against Daily_KM
    trips_x_len = float((plan["Daily_Trips"] * plan["Route_KM"]).sum())
    assert d["plan_trips_x_route_km_total"] == pytest.approx(trips_x_len, rel=1e-6)
    assert d["plan_daily_km_total"] == pytest.approx(float(plan["Daily_KM"].sum()), rel=1e-6)
    assert d["plan_over_trips_x_length_ratio"] == pytest.approx(
        d["plan_daily_km_total"] / d["plan_trips_x_route_km_total"], rel=1e-6)
    assert d["plan_km_per_bus_day"]["network_mean"] == pytest.approx(
        d["plan_daily_km_total"] / int(plan["Fleet_Required"].sum()), rel=1e-6)


def test_a14_emission_ratio_computed_not_typed(a14):
    e = a14["engine_emission_factor_check"]
    lo, hi = e["understatement_factor_range"]
    assert lo < e["understatement_factor"] < hi
    # factor = module's e-bus-equivalent g/km (mid-range) over the engine's 30 g/km
    eng = e["engine_ebus_gco2_per_km"]
    assert e["understatement_factor"] == pytest.approx(e["midrange_ebus_gco2_per_km"] / eng, rel=1e-9)
    assert [lo, hi] == [pytest.approx(v / eng) for v in e["ebus_gco2_per_km_range"]]
    src = (ANALYSIS_DIR / "a14_cost_emissions.py").read_text(encoding="utf-8")
    assert "roughly 25x" not in src and "25x" not in src.split('"""')[1]


# ── a15 ─────────────────────────────────────────────────────────────────────────
def test_a15_s4_flagged_upper_bound_with_reason(a15):
    s = {r["scenario"]: r for r in a15["scenarios"]}
    assert s["S4"]["interpretation"] == "upper bound on consolidation"
    assert len(s["S4"]["interpretation_why"]) >= 2
    assert s["S4"]["fleet_method"].startswith("NOT recomputed")
    for k in ("S0", "S1", "S2", "S3", "S5"):
        assert s[k]["fleet_method"].startswith("recomputed")
        assert s[k].get("interpretation") != "upper bound on consolidation"
    csv = pd.read_csv(TABLES_DIR / "table08_scenarios.csv")
    assert any("upper bound" in str(x).lower() for x in csv["Reading"])
    # diagnostics are internally consistent
    dg = s["S4"]["consolidation_diagnostics"]
    assert dg["n_removed_with_no_direct_qualifying_pair_to_their_survivor"] <= dg["n_routes_removed"]


def test_a15_funding_budget_vs_allocation(a15):
    f = a15["funding_sequence"]
    seq = pd.read_csv(DERIVED_DIR / "a15_funding_sequence.csv")
    funded = seq[seq["within_budget"]]
    assert f["buses_allocated"] <= f["buses_budgeted"]
    assert f["buses_allocated"] == int(funded["cum_buses"].max()) == int(funded["fleet"].sum())
    assert f["buses_unspent"] == f["buses_budgeted"] - f["buses_allocated"]
    assert f["routes_funded"] == len(funded)
    assert f["coverage_reached_at_allocated_buses"] == pytest.approx(float(funded["cum_coverage"].iloc[-1]))
    assert f["ordering_method"] == "greedy by marginal coverage per bus; order-dependent; not an optimum"
    # legacy keys still agree with the new ones
    assert f["budget_buses"] == f["buses_budgeted"] and f["buses_used"] == f["buses_allocated"]
    v = f["variant_fill_remaining_budget"]
    assert v["buses_allocated"] <= f["buses_budgeted"]
    assert v["n_extra_routes"] >= 0 and v["coverage"] >= f["coverage_reached_at_allocated_buses"]


# ── a16 ─────────────────────────────────────────────────────────────────────────
def test_a16_prediction_interval_contains_point_and_is_in_buses(a16):
    kpop = a16["kashmir"]["population_denominators"]["total"]["value"]
    for s in a16["model_summary"]:
        lo, hi = s["pred_interval_buses_per_1000"]
        assert lo < s["point_buses_per_1000"] < hi
        blo, bhi = s["pred_interval_buses"]
        assert blo == pytest.approx(lo * kpop / 1000.0)
        assert bhi == pytest.approx(hi * kpop / 1000.0)
        assert blo < s["point_buses"] < bhi
        assert s["pred_interval_lower_is_impossible"] == (blo < 0)
        assert 0.0 <= s["r_squared"] <= 1.0 and s["adj_r_squared"] <= s["r_squared"]
        assert s["plan_within_pred_interval"] == (blo <= s["plan_fleet"] <= bhi)
    assert a16["n"] == 36
    assert set(a16["r_squared"]) == {s["model"] for s in a16["model_summary"]}


def test_a16_r2_and_pvalues_recompute_from_peer_file(a16):
    import statsmodels.api as sm
    p = pd.read_csv(RAW_DIR / "peer_cities.csv")
    p = p[p["use_in_fit"]]
    y = (p["buses"] / p["population"] * 1000.0).to_numpy()
    X = sm.add_constant(np.log10(p["population"].to_numpy()))
    r = sm.OLS(y, X).fit()
    assert a16["r_squared"]["M1_pop_only"] == pytest.approx(r.rsquared, abs=1e-4)
    assert a16["coefficient_p_values"]["M1_pop_only"]["log10_pop"] == pytest.approx(r.pvalues[1], rel=1e-6)
    assert a16["r_squared"]["M1_pop_only"] < 0.2   # weak fit; must be surfaced
    assert "R^2" in a16["headline"] and "cannot" in a16["headline"]


def test_a16_extrapolation_flag_matches_density_range(a16):
    ex = a16["extrapolation"]
    lo, hi = ex["fitted_density_range"]
    assert ex["density_outside_fitted_range"] == (not (lo <= ex["kashmir_density"] <= hi))
    flagged = {s["model"] for s in a16["model_summary"] if s["extrapolation"]}
    assert ex["models_flagged"] and set(ex["models_flagged"]) == flagged
    for s in a16["model_summary"]:
        uses_density = s["kashmir_design"]["density"] is not None
        assert s["extrapolation"] == (uses_density and ex["density_outside_fitted_range"])


def test_a16_engine_self_report_not_used_as_denominator(a16):
    assert 2_317_958 not in [r["population"] for r in a16["per_population_ratios"]["rows"]]
    assert "served_engine" not in a16["kashmir"]["population_denominators"]
    assert not any("served_engine" in k for k in a16["placement"])
    assert a16["legacy_engine_self_report"]["status"].startswith("superseded")
    tbl = pd.read_csv(TABLES_DIR / "table05j_peer_prediction.csv")
    assert not tbl["basis"].str.contains("engine", case=False).any()


def test_a16_per_population_ratios_recompute(a16, plan):
    from decimal import Decimal, ROUND_HALF_UP
    fleet = int(plan["Fleet_Required"].sum())
    a02 = _j("a02_network_catchments")
    a11 = _j("a11_coverage_accessibility")
    expected = {
        "total": a11["morans"]["study_area_worldpop_in_union"],
        "euclid_400m": a02["pop_euclid_union"],
        "network_400m": a02["pop_net_union"],
    }
    rows = a16["per_population_ratios"]["rows"]
    assert a16["per_population_ratios"]["numerator_buses"] == fleet == 1011
    assert len(rows) == 3
    for r, (k, pop) in zip(rows, expected.items()):
        assert r["population"] == int(round(pop))
        want = float(Decimal(repr(fleet / pop * 1e5)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
        assert r["buses_per_100000"] == want
        assert r["buses_per_1000"] == pytest.approx(fleet / pop * 1000, abs=0.005)
        assert k in r["source"] or "pop_" in r["source"] or "study_area" in r["source"]
    # denominators are traced inside the repo, not to a README/CLAUDE.md
    assert all(r["source"].startswith("data/derived/") for r in rows)
    assert a16["denominators"]["total"]["equals_common_STUDY_AREA_POPULATION"] is True
    assert a16["denominators"]["network_400m"]["equals_a11_any_service_population"] is True
    assert a16["per_population_ratios"]["benchmark"]["defined_on"].startswith("a city")
    # file on disk matches
    t = pd.read_csv(TABLES_DIR / "table05j_per_population_ratios.csv")
    assert t["buses_per_100000"].tolist() == [r["buses_per_100000"] for r in rows]


def test_a16_rounding_is_half_up_not_truncation():
    import a16_peer_regression as A
    assert A.round_half_up(43.65, 1) == 43.7
    assert A.round_half_up(43.6, 1) == 43.6
    assert A.round_half_up(2.25, 1) == 2.3        # banker's rounding would give 2.2


def test_a14_sourced_constants_carry_url_and_three_bases(a14):
    ver = {r["constant"]: r for r in a14["constants_table"]}
    for name in ("grid_kgco2_per_kwh", "ebus_kwh_per_km", "srtu_km_per_bus_day"):
        assert ver[name]["verified"] is True
        assert ver[name]["source_status"] == "primary_source_url"
    assert a14["constants"]["grid_kgco2_per_kwh"]["low"] == pytest.approx(0.675)
    assert a14["constants"]["srtu_km_per_bus_day"]["high"] == pytest.approx(218.2)
    assert a14["constants"]["ebus_kwh_per_km"]["low"] == pytest.approx(0.98)
    for name in ("gcc_inr_per_km_ebus_12m", "gcc_inr_per_km_ebus_9m"):
        assert ver[name]["verified"] == "press"
    # unsourced items stay unverified
    for name in ("diesel_kmpl_mpv", "ebus_kwh_per_km_mpv", "cost_inr_per_km_mpv", "diesel_kmpl_full_size"):
        assert ver[name]["verified"] is False
    assert set(a14["bases"]) == {"PLAN", "PLAN_TRIPS_X_LENGTH", "TIMETABLE_DAY", "OBSERVED", "SRTU_MORTH"}
    tt, pl = a14["bases"]["TIMETABLE_DAY"], a14["bases"]["PLAN_TRIPS_X_LENGTH"]
    assert a14["central"]["basis"] == "TIMETABLE_DAY"
    assert 11 / 16 < tt["vehicle_km_per_year"] / pl["vehicle_km_per_year"] < 13 / 16 + 0.05
    fleet = a14["bases"]["PLAN"]["by_class"]
    n = sum(fleet[c]["n_buses"] for c in fleet)
    srtu = a14["bases"]["SRTU_MORTH"]["vehicle_km_per_year"]
    assert srtu == pytest.approx(218.2 * n * 365, rel=1e-9)
