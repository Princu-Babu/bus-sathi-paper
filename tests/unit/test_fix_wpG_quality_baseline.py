"""
Phase-1 fix tests for work package G: data-quality join check, WorldPop-vs-Census
district table, V2 benchmark under both readings of "Trip Count", V1 layer
history, and the fleet baseline. Values are recomputed from the raw inputs or
from synthetic fixtures, not compared with a module's own output.
"""
import json
import re
import sys

import pandas as pd
import pytest

from tests.conftest import ANALYSIS_DIR, DERIVED_DIR, RAW_DIR

sys.path.insert(0, str(ANALYSIS_DIR))

import common as C  # noqa: E402
import q02_fleet_baseline as Q2  # noqa: E402
import v02_benchmark as V2  # noqa: E402

SUMMARY = RAW_DIR / "permit_register_summary.csv"


def _j(name):
    return json.loads((DERIVED_DIR / f"{name}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- summary CSV privacy
def test_summary_csv_has_no_identifier_column_or_registration_number():
    text = SUMMARY.read_text(encoding="utf-8")
    assert not re.search(r"JK\d{2}", text)
    cols = set(pd.read_csv(SUMMARY, nrows=1).columns)
    assert cols == {"block", "in_kashmir_division", "office", "vehicle_class", "vehicle_category",
                    "validity_status", "validity_years_rounded", "route_recorded",
                    "n_permit_rows", "n_vehicles"}
    assert not any(re.search(r"reg|owner|name_of|driver|vehicle_no", c) for c in cols)
    d = pd.read_csv(SUMMARY, keep_default_na=False)
    assert d["n_vehicles"].dtype.kind == "i" and d["n_permit_rows"].dtype.kind == "i"
    assert (d["n_vehicles"] <= d["n_permit_rows"]).all()
    assert (d["n_permit_rows"] > 0).all()


# ---------------------------------------------------------------- fleet baseline
def test_baseline_arithmetic_on_synthetic_summary():
    rows = []
    for cls, st, n in (("Bus", "valid", 10), ("Bus", "expired", 30), ("Bus", "placeholder", 5),
                       ("Omni Bus", "valid", 4), ("Omni Bus", "expired", 1),
                       ("Maxi Cab", "valid", 99)):
        rows.append(dict(block="stock", in_kashmir_division="yes", office="X ARTO",
                         vehicle_class=cls, vehicle_category="HPV", validity_status=st,
                         validity_years_rounded="ALL", route_recorded="ALL",
                         n_permit_rows=n, n_vehicles=n))
    rows.append(dict(rows[0], in_kashmir_division="no", n_vehicles=1000, n_permit_rows=1000))
    res = Q2.compute(pd.DataFrame(rows), n_ebuses=6, plan_fleet=50)
    assert res["valid_private_buses"] == 14           # Maxi Cab and the other division excluded
    assert res["baseline_valid_private_plus_ebuses"] == 20
    assert res["uplift_vs_baseline"]["uplift_fraction"] == pytest.approx(50 / 20 - 1)
    assert res["uplift_vs_valid_private_only"]["additional_buses"] == 36
    assert res["share_expired_on_paper"]["share_expired"] == pytest.approx(31 / 50)


def test_baseline_output_recomputes_from_inputs():
    out = _j("q02_fleet_baseline")
    s = pd.read_csv(SUMMARY, keep_default_na=False)
    k = s[(s.block == "stock") & (s.in_kashmir_division == "yes")
          & s.vehicle_class.isin(["Bus", "Omni Bus"])]
    valid = int(k[k.validity_status == "valid"].n_vehicles.sum())
    d = pd.read_csv(C.CHALO_DEPLOYED_CSV)
    ebus = int(pd.to_numeric(d["New Deployement"], errors="coerce").sum()
               - (pd.to_numeric(d.loc[d["PROPSED ROUTE NO"].astype(str) == "TOTAL", "New Deployement"],
                                errors="coerce").sum()))
    plan = int(C.load_active()["Fleet_Required"].sum())
    assert out["valid_private_buses"] == valid
    assert out["ebuses"]["n_ebuses"] == ebus
    assert out["baseline_valid_private_plus_ebuses"] == valid + ebus
    assert out["plan_fleet"] == plan
    assert out["uplift_vs_baseline"]["uplift_fraction"] == pytest.approx(plan / (valid + ebus) - 1)
    assert out["uplift_vs_valid_private_only"]["uplift_fraction"] == pytest.approx(plan / valid - 1)
    assert out["n_kashmir_division_offices"] == 10
    assert out["jkrtc"]["status"] == "excluded_by_decision"
    assert "not proof that the bus operates" in out["caveat"]
    st = out["bus_class_vehicles"]
    assert sum(st["by_status"].values()) == st["total"]
    assert 0 < out["share_expired_on_paper"]["share_expired"] < 1


# ---------------------------------------------------------------- q01 join match
def _flags(names, origins, dests, min_len):
    out = []
    for nm, o, d in zip(names, origins, dests):
        name = str(nm).upper()
        out.append(any(t[:4] in name for t in str(o).upper().split() if len(t) >= min_len)
                   and any(t[:4] in name for t in str(d).upper().split() if len(t) >= min_len))
    return out


def test_join_match_recomputes_and_old_filter_artefact_is_explained():
    permits = pd.read_csv(C.PERMITS_CSV).reset_index(drop=True)
    permits["Route_ID"] = [f"R{i + 1:04d}" for i in range(len(permits))]
    m = C.load_plan()[["Route_ID", "Route_Name"]].merge(
        permits[["Route_ID", "Origin", "Destination"]], on="Route_ID", how="left")
    m = m[m["Origin"].notna()]
    new = _flags(m.Route_Name, m.Origin, m.Destination, 2)
    old = _flags(m.Route_Name, m.Origin, m.Destination, 3)
    jc = _j("q01_data_quality")["D1_register_hygiene"]["join_check"]
    assert sum(new) / len(new) > 0.99
    assert abs(sum(old) / len(old) - 0.8046) < 0.001          # the old (wrong) rate reproduces
    assert jc["n_checked"] == len(m) and jc["n_match"] == sum(new)
    assert jc["n_mismatch"] == len(m) - sum(new) == len(jc["genuine_mismatches"])
    assert jc["match_rate"] == pytest.approx(sum(new) / len(new))
    # 'LD' is what the old filter dropped
    assert jc["n_old_failures_cleared_by_counting_two_letter_tokens"] >= 100
    assert jc["two_letter_tokens_in_old_failures"].get("LD", 0) >= 100
    # the positional alignment is real: a shifted join is at chance
    off = jc["offset_test_match_rate_by_row_shift"]
    assert off["0"] > 0.99 and max(off["-1"], off["1"], off["-2"], off["2"]) < 0.3
    assert _j("q01_data_quality")["D1_register_hygiene"]["join_match_rate"] == pytest.approx(
        jc["match_rate"])


# ---------------------------------------------------------------- q01 WorldPop vs Census
def test_worldpop_census_district_table_and_band_counts():
    d4 = _j("q01_data_quality")["D4_worldpop"]
    rows = d4["district_ratios"]
    lo, hi = d4["cagr_band_per_year"]
    assert len(rows) == d4["n_districts_total"] == 10
    for r in rows:
        assert r["ratio_wp_to_census"] == pytest.approx(r["worldpop_2026"] / r["census_2011"])
        assert r["within_declared_band"] == (lo <= r["implied_cagr_per_year"] <= hi)
        assert r["implied_cagr_per_year"] == pytest.approx(
            (r["worldpop_2026"] / r["census_2011"]) ** (1 / 15) - 1)      # 2011 -> 2026
    assert d4["n_districts_within_declared_band"] == sum(r["within_declared_band"] for r in rows)
    assert d4["n_districts_within_declared_band"] + d4["n_districts_outside_declared_band"] == 10
    assert d4["ratio_min"]["ratio"] == pytest.approx(min(r["ratio_wp_to_census"] for r in rows))
    assert d4["ratio_max"]["ratio"] == pytest.approx(max(r["ratio_wp_to_census"] for r in rows))
    assert d4["ratio_min"]["district"] == "Kupwara" and d4["ratio_min"]["ratio"] < 0.75
    assert d4["ratio_max"]["ratio"] > 1.15       # hidden behind the 0.956 total
    assert d4["census_anchored"] is True and d4["independent_of_census_frame"] is False
    assert "validated" not in d4["statement"].lower()
    assert "conservatism" not in d4["note"].lower()
    assert "direction of the bias is not established" in d4["note"]
    assert d4["worldpop_variant"] == "not recorded in metadata"
    tab = pd.read_csv(C.TABLES / "table02d_worldpop_vs_census.csv")
    assert int(tab["within_declared_band"].sum()) == d4["n_districts_within_declared_band"]


# ---------------------------------------------------------------- V2 both readings
def test_v02_verdict_from_ratios_follows_band():
    assert V2.verdict_from_ratios([1.0, 1.1], 0.15)["verdict"] == "pass"
    assert V2.verdict_from_ratios([1.0, 1.4], 0.15)["verdict"] == "mixed"
    assert V2.verdict_from_ratios([1.4, 1.6], 0.15)["verdict"] == "fail"
    v = V2.verdict_from_ratios([0.7, 0.8], 0.25)
    assert v["verdict"] == "mixed" and V2.verdict_from_ratios([0.6, 0.7], 0.25)["direction"] == \
        "plan_below_scaled_reference"


def test_v02_both_readings_present_and_consistent():
    out = _j("v02_benchmark")
    assert set(out["readings"]) == {"A_departure", "B_one_way_run"}
    assert out["needs_data_owner_confirmation"] is True
    assert out["trip_count_definition"]["needs_data_owner_confirmation"] is True
    a, b = out["readings"]["A_departure"], out["readings"]["B_one_way_run"]
    assert a["departures_per_route_direction_per_day"] == pytest.approx(
        2 * b["departures_per_route_direction_per_day"])
    for r in (a, b):
        ratios = [s["ratio"] for s in r["sweep"]]
        assert r["verdict_declared_band"] == V2.verdict_from_ratios(ratios, V2.TOLERANCE)
        for s in r["sweep"]:
            assert s["ratio"] == pytest.approx(s["plan_fleet"] / s["chalo_scaled_fleet"], abs=0.002)
            assert s["within_tolerance"] == (abs(s["ratio"] - 1) <= V2.TOLERANCE)
    # the two readings sit on opposite sides of 1 and move the answer by a factor of about 2
    assert min(s["ratio"] for s in a["sweep"]) > 1 > max(s["ratio"] for s in b["sweep"])
    for sa, sb in zip(a["sweep"], b["sweep"]):
        assert sa["ratio"] / sb["ratio"] == pytest.approx(2.0, rel=0.01)
    # naming and wording
    assert out["operator_deployed_buses"] == 98 and out["plan_backbone_fleet"] == 283
    assert out["band"]["pre_registered"] is False and out["band"]["registered_anywhere"] is False
    assert out["band"]["engine_cross_check_band"] == 0.25
    ev = out["trip_count_definition"]["evidence"]
    rid = pd.read_csv(C.CHALO_RIDERSHIP_CSV)
    rid = rid[rid["Month"].notna() & rid["Trip Count"].notna()]
    km_per_trip = rid["Operated KM"].map(V2.num).sum() / rid["Trip Count"].map(V2.num).sum()
    assert ev["operated_km_per_counted_trip_overall"] == pytest.approx(km_per_trip)
    one_way = ev["plan_backbone_one_way_route_km"]["mean"]
    nearer_one_way = abs(km_per_trip - one_way) < abs(km_per_trip - 2 * one_way)
    assert ev["evidence_favours"] == ("B_one_way_run" if nearer_one_way else "A_departure")
    assert ev["evidence_favours"] in {"A_departure", "B_one_way_run"}


# ---------------------------------------------------------------- V1 history
def test_v01_sequence_reports_declared_layer_failure_and_later_layer():
    v = _j("v01_spatial_crossval")
    s = v["sequence"]
    assert s["declared_first"]["layer"] == "osm" and s["added_later"]["layer"] == "microsoft"
    assert s["primary_is_declared_layer"] is False
    thr = s["threshold"]
    osm, ms = s["results_by_layer"]["osm"], s["results_by_layer"]["microsoft"]
    assert osm["passes_declared_criterion"] == (
        osm["route_scale_rho_area"] > thr and osm["grid_populated_cells_rho"] > thr)
    assert ms["passes_declared_criterion"] == (
        ms["route_scale_rho_area"] > thr and ms["grid_populated_cells_rho"] > thr)
    assert osm["passes_declared_criterion"] is False and ms["passes_declared_criterion"] is True
    assert v["verdict_pass_declared_layer"] is False
    assert v["worldpop_variant"] == "not recorded in metadata"
    assert "pre-registered" not in json.dumps(v["sequence"]).lower().replace("not pre-registered", "")
