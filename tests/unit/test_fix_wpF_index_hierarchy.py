"""
Phase-1 fix tests, work package F: index weights, class count / hierarchy,
time-of-day headways, deadhead, load factor.

Each test recomputes the quantity from the raw plan / tier files and compares it
with what the module published, or checks a structural property of the output.
"""
import json
import re
import sys

import numpy as np
import pandas as pd

from tests.conftest import ANALYSIS_DIR, DERIVED_DIR

sys.path.insert(0, str(ANALYSIS_DIR))

import common as C  # noqa: E402

TABLES = C.ROOT / "paper" / "tables"


def _j(name):
    return json.loads((DERIVED_DIR / name).read_text(encoding="utf-8"))


# ── a03 ──────────────────────────────────────────────────────────────────────
def test_a03_equal_and_pca_flagged_identical_and_truly_identical():
    a = _j("a03_index_weights.json")
    assert a["n_schemes_computed"] == 3
    assert a["n_distinct_weightings"] == 2
    flagged = {(r["variant"], tuple(r["schemes"])) for r in a["identical_by_construction"]}
    assert flagged == {("euclid", ("equal", "pca")), ("net", ("equal", "pca"))}
    for v, blk in a["by_variant"].items():
        w = blk["weights"]
        assert np.allclose(w["equal"], w["pca"]), v
        assert not np.allclose(w["equal"], w["entropy"]), v   # entropy is the distinct one


def test_a03_collinearity_statistic_recomputes_and_rule_reported():
    a = _j("a03_index_weights.json")
    idx = pd.read_csv(DERIVED_DIR / "a03_index.csv")
    for variant, (pop, poi) in {"euclid": ("pop_score_euclid", "poi_score_euclid"),
                                "net": ("pop_score_net", "poi_score_net")}.items():
        rec = a["collinearity_rule"]["by_variant"][variant]
        r = float(np.corrcoef(idx[pop], idx[poi])[0, 1])
        rho = float(idx[pop].rank().corr(idx[poi].rank()))
        assert abs(rec["pearson_r"] - r) < 1e-6
        assert abs(rec["spearman_rho"] - rho) < 1e-6
        assert rec["threshold"] == 0.85
        assert "assumption" in rec["threshold_source"]
        # the flag must follow the numbers, not be asserted
        assert rec["rule_fired"] == bool(max(r, rho) > rec["threshold"])
        assert rec["outcome_as_written"]


# ── a04: published vs objective, stability, class count ──────────────────────
def _objective_vs_plan():
    tiers = pd.read_csv(DERIVED_DIR / "a04_route_tiers.csv")
    plan = C.load_active()
    m = tiers.merge(plan[["New_Route_ID", "Priority_Band", "CMP_Trunk"]],
                    on="New_Route_ID", how="inner")
    pub = m["Priority_Band"].map({"HP": 1, "MP": 2, "LP": 3})
    return m, pub


def test_a04_agreement_recomputes_from_plan_and_tiers():
    m, pub = _objective_vs_plan()
    b = _j("a04_class_count.json")["published_vs_objective_agreement"]
    assert len(m) == b["n_routes"] == 186
    n_agree = int((m["tier_rank"] == pub).sum())
    assert b["n_agree"] == n_agree
    assert abs(b["agreement_pct"] - 100 * n_agree / len(m)) < 1e-6
    non = ~m["CMP_Trunk"].astype(bool)
    ex = b["excluding_sscl_backbone"]
    assert ex["n_routes"] == int(non.sum())
    assert ex["n_agree"] == int((m.loc[non, "tier_rank"] == pub[non]).sum())
    # the headline contrast the paper must now carry: published tiers disagree far more
    # than the Monte-Carlo stability share suggests
    assert b["agreement_pct"] < 75.0


def test_a04_high_priority_in_lowest_tier_listed_with_reasons():
    m, _ = _objective_vs_plan()
    sel = m[m["Priority_Band"].eq("HP") & m["tier_rank"].eq(3)]
    lst = _j("a04_class_count.json")["published_vs_objective_agreement"][
        "high_priority_in_lowest_objective_tier"]
    routes = lst["routes"] if isinstance(lst, dict) else lst
    assert sorted(r["New_Route_ID"] for r in routes) == sorted(sel["New_Route_ID"])
    assert all(r["reason_codes"] for r in routes)          # every route has a reason code
    if isinstance(lst, dict):
        assert lst["n"] == len(sel)


def test_a04_stability_is_a_separate_key_with_base():
    b = _j("a04_class_count.json")
    s = b["stability_under_uncertainty"]
    assert s is not b["published_vs_objective_agreement"]
    mc = json.dumps(s).lower()
    assert "n_draws" in mc and "5000" in mc          # base of the Monte-Carlo figure stated
    assert "186" in mc                               # conditional on the 186-route set
    assert s["monte_carlo"]["baseline_is_this_modules_objective_partition"] is True
    # stability must exceed published agreement: it is a different (self-referential) quantity
    pub = _j("a04_class_count.json")["published_vs_objective_agreement"]["agreement_pct"] / 100
    assert s["monte_carlo"]["tier_agreement_median"] > pub + 0.25


def test_a04_class_count_rules_state_thresholds_and_reach():
    b = _j("a04_class_count.json")
    for name, c in b["curves"].items():
        ra, rb = c["rule_a"], c["rule_b"]
        assert "assumption" in ra["threshold_source"], name
        assert 2 not in rb["admissible_k"] and 2 in rb["cannot_return_k"], name
        assert min(rb["admissible_k"]) == 3, name
        assert ra["can_return_k"] and 2 in ra["can_return_k"], name
    s = b["elbow_rules_summary"]
    assert s["independent_confirmation_of_k3"] is False
    assert s["mode_test_run"] is False
    gvf = b["gvf_by_k"]
    assert sorted(int(k) for k in gvf) == list(range(2, 8)) or \
        sorted(int(k) for k in next(iter(gvf.values()))) == list(range(2, 8))


def test_a04_no_preregistered_wording_in_owned_outputs():
    for name in ("a04_class_count.json", "a03_index_weights.json", "a05_headway_timeofday.json",
                 "a06_deadhead.json", "a07_load_factor.json"):
        assert "pre-regist" not in (DERIVED_DIR / name).read_text(encoding="utf-8").lower(), name
    for name in ("a03_index_weights.py", "a04_class_count.py", "a05_headway_timeofday.py",
                 "a06_deadhead.py", "a07_load_factor.py"):
        src = (ANALYSIS_DIR / name).read_text(encoding="utf-8").lower()
        assert "pre-regist" not in src or "no pre-regist" in src or "not pre-regist" in src, name


def test_a04_identity_confusion_labelled():
    b = _j("a04_class_count.json")
    cm = b["confusion_matrices"]
    kinds = {k: (v.get("kind") if isinstance(v, dict) else None) for k, v in cm.items()}
    ident = [k for k, v in kinds.items() if v and "identity" in v]
    assert ident, kinds              # Jenks vs k-means is flagged as an implementation check
    assert any("kmeans" in k and "jenks" in k for k in ident)
    assert cm["jenks__vs__kmeans"]["kind"] == "implementation_check_identity"
    tiers = pd.read_csv(DERIVED_DIR / "a04_route_tiers.csv")
    assert (tiers["tier_class"] == tiers["class_kmeans"]).all()   # the identity really holds on the data


def test_class_count_table_parses_with_consistent_columns():
    lines = [ln for ln in (TABLES / "table05_class_count.md").read_text(encoding="utf-8").splitlines()
             if ln.startswith("|")]
    assert len(lines) >= 3

    def cells(ln):
        return [c for c in ln.strip().strip("|").split("|")]

    ncol = len(cells(lines[0]))
    assert ncol >= 8
    for ln in lines:
        assert len(cells(ln)) == ncol, ln
    assert "nan" not in "\n".join(lines).lower().replace("nan%", "")
    csv = pd.read_csv(TABLES / "table05_class_count.csv")
    assert len(csv) == len(lines) - 2
    assert list(csv.columns[:1]) == ["k"] and len(csv.columns) == ncol


# ── a05 ──────────────────────────────────────────────────────────────────────
def test_a05_saving_range_present_ordered_and_matches_arms():
    a = _j("a05_headway_timeofday.json")
    s = a["saving_summary"]
    assert s["min_pct"] <= s["max_pct"]
    pa = {r["rule"]: r["bus_hour_saving_pct"] for r in a["fleet_consequence"]
          if r["anchor"] == "peak-anchored"}
    assert s["min_pct"] == min(pa.values()) and s["max_pct"] == max(pa.values())
    assert s["proportional_pct"] == pa["proportional"] and s["square_root_pct"] == pa["square-root"]
    assert s["square_root_pct"] < s["proportional_pct"]      # the paper must not quote only the larger
    assert a["analysis_scope"] == "paper_side_analysis_not_in_engine"


def test_a05_same_fleet_flagged_identity_only_where_peak_multiplier_is_one():
    a = _j("a05_headway_timeofday.json")
    peak = [b for b in a["bands"] if b["band"] == "Peak"][0]
    assert abs(peak["mult_proportional_peak_anchored"] - 1.0) < 1e-12
    for r in a["fleet_consequence"]:
        if r["anchor"] == "peak-anchored":
            assert r["peak_fleet_equals_plan_by_construction"] is True
            assert r["vehicles_to_purchase_delta"] == 0
        else:
            assert r["peak_fleet_equals_plan_by_construction"] is False
            assert r["vehicles_to_purchase_delta"] > 0
            assert r["bus_hour_saving_pct"] < 0               # bus-hours rise


def test_a05_service_window_sensitivity_covers_all_day_lengths():
    a = _j("a05_headway_timeofday.json")
    w = a["saving_summary"]["range_across_service_windows_pct"]
    assert {v["hours"] for v in w.values()} == {17, 16, 11}
    for v in w.values():
        assert v["min_pct"] <= v["max_pct"]
    # headline window reproduces the headline range
    assert w["observed_17h"]["min_pct"] == a["saving_summary"]["min_pct"]
    assert w["observed_17h"]["max_pct"] == a["saving_summary"]["max_pct"]


# ── a06 ──────────────────────────────────────────────────────────────────────
def test_a06_d1_below_literature_range_labelled():
    d = _j("a06_deadhead.json")
    share = d["network"]["deadhead_share_D1"]
    assert share < 0.05
    assert d["d1_inside_literature_range"] is False
    assert d["d1_position_vs_literature_range"] == "below"
    assert "none cited" in d["literature_range_source"]
    assert "Srinagar" in d["depot_assumptions_stated"]["observed_day_caveat"]
    assert d["n_routes"] == 186


# ── a07 ──────────────────────────────────────────────────────────────────────
def test_a07_both_direction_ratio_is_exactly_half_legacy_and_recomputes():
    r = pd.read_csv(DERIVED_DIR / "a07_route_load.csv")
    assert np.allclose(r["proxy_boarding_to_capacity_both_directions"] * 2.0,
                       r["proxy_boarding_to_capacity"])
    assert np.allclose(r["peak_hour_capacity_both_directions"], 2.0 * r["peak_hour_capacity"])
    # recompute from the plan, not from the module's own column
    a = C.load_active().set_index("New_Route_ID").loc[r["New_Route_ID"]]
    cap = C.VEHICLE_CAPACITY
    fleet = a["HPV_Count"] + a["MPV_Count"] + a["LPV_Count"]
    mean_cap = (a["HPV_Count"] * cap["HPV"] + a["MPV_Count"] * cap["MPV"]
                + a["LPV_Count"] * cap["LPV"]) / fleet
    phf = _j("a05_headway_timeofday.json")["peak_hour_factor_pct"] / 100.0
    expect = a["Daily_Demand_Pax"] * phf / (2.0 * 60.0 / a["Headway_Min"] * mean_cap)
    assert np.allclose(r["proxy_boarding_to_capacity_both_directions"].to_numpy(),
                       expect.to_numpy(), rtol=1e-9)


def test_a07_json_states_base_n_and_both_statistics():
    j = _j("a07_load_factor.json")
    assert j["direction_consistency"]["status"] == "verified_real"
    p = j["proxy_network_both_directions"]
    assert p["n_routes"] == 186 and p["in_sample"] is True
    assert abs(p["median"] * 2 - j["proxy_network"]["median"]) < 1e-9
    assert p["n_below_040"] >= j["proxy_network"]["n_below_040"]   # correction makes it worse, not better
    b = j["load_statistics"]["backbone_day_one"]
    assert b["n_routes"] == 30
    assert "May 2025" in b["base"]
    lo, hi = b["boardings_per_oneway_trip_today_range"]
    assert lo < hi
    assert 8.0 < b["boardings_per_oneway_trip_plan_day_one"] < 8.5
    assert b["trip_multiplier_range"][0] < b["trip_multiplier_range"][1]
    assert "note" in j["proxy_network"]                         # legacy key carries its note
