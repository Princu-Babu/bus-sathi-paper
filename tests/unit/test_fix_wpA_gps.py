"""
Phase-1 fix tests for the GPS validation module (v04_gps_validation).

Each test checks behaviour the audit found wrong: run counts that were route
incidences, headline statistics resting on five in-sample corridors, a fleet
rule that truncated, verdicts that did not follow the declared criteria. Values
are recomputed from the raw GPS files and the published plan, not read back from
the module's own output and compared with themselves.
"""
import json
import sys

import numpy as np
import pandas as pd
import pytest

from tests.conftest import ANALYSIS_DIR, DERIVED_DIR, RAW_DIR

sys.path.insert(0, str(ANALYSIS_DIR))

import common as C  # noqa: E402
import v04_gps_validation as V  # noqa: E402

GPS = RAW_DIR / "gps"
FIVE_IDS = ["FDR-050", "FDR-262", "FDR-270", "FDR-370", "FDR-575"]


@pytest.fixture(scope="module")
def out():
    p = DERIVED_DIR / "v04_gps_validation.json"
    assert p.exists(), "run python analysis/v04_gps_validation.py first"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def comp():
    return pd.read_csv(DERIVED_DIR / "v04_corridor_comparison.csv")


@pytest.fixture(scope="module")
def plan():
    return C.load_active().set_index("New_Route_ID")


def _all_comparison_rows(out):
    rows = list(out["runtime"]) + list(out["runtime_by_subset"]) + list(out["length_rows"])
    rows += list(out["moving_speed"]) + list(out["moving_speed_by_subset"])
    rows += [out["dwell"]["rate_comparison"]]
    rows += [d["rate_comparison"] for d in out["dwell_by_subset"].values()]
    return rows


# ── run counts ───────────────────────────────────────────────────────────────
def test_distinct_runs_recompute_and_never_exceed_route_incidences(out):
    dd = pd.read_csv(next(p for p in (GPS / "driver_days.csv", GPS / "driver_days_deidentified.csv")
                          if p.exists()))
    ev = pd.read_csv(GPS / "route_evidence.csv")
    c = out["corpus"]
    assert c["distinct_runs_total"]["value"] == int(dd["n_runs"].sum())
    assert c["route_incidences"]["value"] == int(ev["n_runs"].sum())
    assert c["distinct_runs_total"]["value"] < c["route_incidences"]["value"]
    assert c["distinct_runs_clean"]["value"] <= c["distinct_runs_total"]["value"]
    assert c["distinct_runs_total"]["derived"] is True
    assert c["distinct_runs_clean"]["derived"] is False          # README statement, not derivable
    assert "README" in c["distinct_runs_clean"]["source"]
    assert c["incidences_per_distinct_run"] > 1.0


def test_old_run_key_kept_but_labelled_as_incidences(out, ):
    rc = out["route_coverage"]
    assert rc["total_observed_runs"] == out["corpus"]["route_incidences"]["value"]
    assert "ROUTE-INCIDENCES" in rc["total_observed_runs_note"]
    assert rc["distinct_runs_total"] == out["corpus"]["distinct_runs_total"]["value"]
    assert "not a total" in rc["total_distinct_drivers_max_note"]
    # the corridor sample is a subset of the corpus
    assert out["scope"]["total_runs"] < out["corpus"]["distinct_runs_total"]["value"]


def test_driver_counts_consistent_and_within_derivable_bounds(out):
    dd = pd.read_csv(next(p for p in (GPS / "driver_days.csv", GPS / "driver_days_deidentified.csv")
                          if p.exists()))
    assert out["corpus"]["drivers_distinct"]["value"] == int(dd["driver"].nunique())
    assert "account" in out["corpus"]["drivers_distinct"]["unit"]
    private = out["corpus"]["private_one_off_check"]
    assert private["derived"] is False
    assert private["driver_accounts_total"] == out["corpus"]["drivers_distinct"]["value"]
    assert private["runs_total"] == out["corpus"]["distinct_runs_total"]["value"]
    # the documented distinct-driver counts must sit inside the bounds the shipped
    # per-corridor aggregates imply: max(n_drivers) <= distinct <= sum(n_drivers)
    by_subset = private["distinct_drivers_by_subset"]
    for r in out["runtime_by_subset"]:
        if r["comparison"].startswith("Pace") and r["plan_basis"] == V.PUB:
            lo, hi = r["distinct_drivers_bounds"]
            assert lo <= by_subset[r["subset"]] <= hi, (r["subset"], lo, by_subset[r["subset"]], hi)
    five = [r for r in out["runtime_by_subset"]
            if r["subset"] == "retimed_in_sample" and r["comparison"].startswith("Pace")][0]
    assert five["n_driver_corridor_pairs"] == 69          # sum of corridor-driver pairs ...
    assert by_subset["retimed_in_sample"] < 69            # ... is not a driver count


# ── membership ───────────────────────────────────────────────────────────────
def test_every_comparison_states_n_membership(out):
    for r in out["runtime_by_subset"] + out["moving_speed_by_subset"]:
        for k in ("n", "n_corridors", "corridors", "n_runs", "route_ids", "route_codes",
                  "n_driver_corridor_pairs", "distinct_drivers_bounds", "subset", "in_sample"):
            assert k in r, (r["comparison"], k)
        assert r["n_corridors"] == len(r["corridors"])
        assert r["n_routes"] == len(r["route_ids"]) == len(r["route_codes"])
    for r in out["runtime_by_subset"]:
        assert "plan_basis" in r


def test_subsets_partition_the_14_corridors(out, comp):
    st = out["in_sample"]["statuses"]
    assert sorted(st["retimed_in_sample"]) == ["C1", "C4", "C6", "C7", "C8"]
    assert st["same_route_as_retimed"] == ["C5"]
    assert len(st["out_of_sample"]) == 8
    assert sum(len(v) for v in st.values()) == len(comp) == 14
    # C5 is on a re-timed route, so it must not leak into the out-of-sample set
    assert "FDR-370" not in out["in_sample"]["out_of_sample_route_ids"]
    runs = {s: int(comp.loc[comp["sample_status"] == s, "n_runs"].sum()) for s in st}
    assert runs["retimed_in_sample"] == 470 and runs["out_of_sample"] == 263
    assert sum(runs.values()) == out["scope"]["total_runs"] == int(comp["n_runs"].sum())


def test_in_sample_set_equals_v345_correction_list(out):
    snap = pd.read_csv(DERIVED_DIR / "v04_retimed_routes_v345.csv")
    assert sorted(snap["New_Route_ID"]) == FIVE_IDS
    assert sorted(out["in_sample"]["retimed_route_ids"]) == FIVE_IDS
    # independent anchor 1: the five `matched` corridors of the reality check
    rc = pd.read_csv(C.GPS_REALITY_CSV)
    assert sorted(rc.loc[rc["klass"] == "matched", "permit"]) == FIVE_IDS
    assert sorted(rc.loc[rc["klass"] == "matched", "corridor"]) == sorted(snap["Corridor"])
    # independent anchor 2: the published plan carries the new cycle and fleet
    plan = C.load_active().set_index("Route_Code")
    for r in snap.itertuples():
        assert abs(plan.loc[r.Route_Code, "Cycle_Time_Min"] - r.New_Cycle) <= 0.05
        assert int(plan.loc[r.Route_Code, "Fleet_Required"]) == r.New_Fleet
    assert int(snap["New_Fleet"].sum()) - int(snap["Old_Fleet"].sum()) == 7     # 1,004 -> 1,011
    # independent anchor 3: the engine's own log, when the engine checkout is present
    ext = V.ENGINE_DIR / V.RETIMED_LOG_NAME
    if ext.exists():
        log = pd.read_csv(ext)
        assert sorted(log["Route_Code"]) == sorted(snap["Route_Code"])
        assert sorted(log["New_Cycle"]) == sorted(snap["New_Cycle"])


# ── which plan ───────────────────────────────────────────────────────────────
def test_published_plan_ratios_recompute_from_plan_csv(out, plan):
    rc = pd.read_csv(C.GPS_REALITY_CSV)
    five = rc[rc["klass"] == "matched"].set_index("permit")
    ratio_pub = {i: plan.loc[i, "Cycle_Time_Min"] / 2.0 / five.loc[i, "obs_oneway_min"]
                 for i in FIVE_IDS}
    # the audit's expectation, verified rather than assumed
    expected = {"FDR-050": 0.66, "FDR-262": 1.09, "FDR-270": 0.83, "FDR-370": 0.71, "FDR-575": 0.61}
    for i, e in expected.items():
        assert abs(ratio_pub[i] - e) < 0.006, (i, ratio_pub[i], e)
    row = next(r for r in out["runtime_by_subset"]
               if r["comparison"].startswith("One-way") and r["subset"] == "retimed_in_sample"
               and r["plan_basis"] == V.PUB)
    assert row["n"] == 5
    assert abs(row["ratio_median"] - float(np.median(list(ratio_pub.values())))) < 0.0015
    assert abs(row["mape_pct"] - 100 * np.mean([abs(v - 1) for v in ratio_pub.values()])) < 0.06
    # pre-correction basis is the figure the paper has been quoting (0.51 / 47.6 %)
    pre = next(r for r in out["runtime_by_subset"]
               if r["comparison"].startswith("One-way") and r["subset"] == "retimed_in_sample"
               and r["plan_basis"] == V.PRE)
    ratio_pre = [five.loc[i, "plan_oneway_min"] / five.loc[i, "obs_oneway_min"] for i in FIVE_IDS]
    assert abs(pre["ratio_median"] - np.median(ratio_pre)) < 0.0015
    assert abs(pre["mape_pct"] - 100 * np.mean([abs(v - 1) for v in ratio_pre])) < 0.06
    # and the two plan versions genuinely differ on the five, not elsewhere
    assert pre["ratio_median"] != row["ratio_median"]


def test_plan_versions_coincide_out_of_sample(out, comp):
    oos = comp[comp["sample_status"] == "out_of_sample"]
    assert float((oos["plan_oneway_min"] - oos["plan_oneway_pub_min"]).abs().max()) <= 0.06
    a = next(r for r in out["runtime_by_subset"] if r["subset"] == "out_of_sample"
             and r["comparison"].startswith("Pace") and r["plan_basis"] == V.PRE)
    b = next(r for r in out["runtime_by_subset"] if r["subset"] == "out_of_sample"
             and r["comparison"].startswith("Pace") and r["plan_basis"] == V.PUB)
    assert abs(a["mape_pct"] - b["mape_pct"]) < 0.5


# ── verdicts ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("m, rho, expected", [
    (19.9, 0.51, "pass"),
    (20.0, 0.90, "fail"),        # criterion is strict: MAPE < 20
    (10.0, 0.50, "fail"),        # criterion is strict: rho > 0.5
    (28.4, -0.069, "fail"),
    (float("nan"), 0.9, "not_computable"),
    (10.0, float("nan"), "not_computable"),
    (30.0, float("nan"), "fail"),
])
def test_verdict_from_declared_criteria(m, rho, expected):
    assert V.verdict_from(m, rho)[2] == expected


def test_every_reported_verdict_follows_from_value_and_criterion(out):
    rows = _all_comparison_rows(out)
    assert len(rows) >= 30
    for r in rows:
        m, rho = r["value_mape"], r["value_rank"]
        m = float("nan") if m is None else m
        rho = float("nan") if rho is None else rho
        vm, vr, v = V.verdict_from(m, rho)
        assert (r["verdict_mape"], r["verdict_rank"], r["verdict"]) == (vm, vr, v), r["comparison"]
        assert r["mape_pass"] == (vm == "pass") and r["rank_pass"] == (vr == "pass")
        assert r["criterion_mape"] == "MAPE < 20 %" and r["criterion_rank"] == "Spearman rho > 0.5"
    assert out["criteria"]["mape"]["threshold"] == V.MAPE_THRESHOLD == 20.0
    assert out["criteria"]["rank"]["threshold"] == V.RANK_CORR_THRESHOLD == 0.5


def test_moving_speed_fails_despite_small_signed_bias(out):
    prof = pd.read_csv(GPS / "corridor_profiles.csv")
    comp = pd.read_csv(DERIVED_DIR / "v04_corridor_comparison.csv")
    comp["corridor_id"] = comp["corridor"].str[1:].astype(int)
    j = prof.merge(comp[["corridor_id", "eng_km", "osrm_drive_min"]], on="corridor_id")
    model = (j["eng_km"] / (j["osrm_drive_min"] / 60.0)) / 2.2
    a, p = j["moving_kmh"].to_numpy(), model.to_numpy()
    mape = 100 * np.mean(np.abs(p - a) / a)
    bias = 100 * np.mean((p - a) / a)
    row = next(r for r in out["moving_speed"] if "City_Core" in r["comparison"])
    assert row["n"] == len(j) == 14
    assert abs(row["mape_pct"] - mape) < 0.06 and abs(row["mean_signed_bias_pct"] - bias) < 0.06
    assert abs(row["mean_signed_bias_pct"]) < 2.0      # the "+1.4 %" ...
    assert row["mape_pct"] > 20.0 and row["verdict"] == "fail"   # ... does not make it pass
    assert row["verdict_mape"] == "fail" and row["verdict_rank"] == "fail"
    # no moving-speed comparison anywhere passes
    assert all(r["verdict"] != "pass" for r in out["moving_speed_by_subset"])
    assert "descriptive" in out["moving_speed_note"]


def test_length_judged_on_matched_corridors_only(out, comp):
    m = comp[comp["klass"] == "matched"]
    assert out["length"]["n"] == len(m) == 5 == out["scope"]["n_matched"]
    assert abs(out["length"]["mape_pct"]
               - 100 * np.mean(np.abs(m["eng_km"] - m["obs_km"]) / m["obs_km"])) < 0.06
    assert out["matched_corridor_contract"]["satisfied"] is True
    alln = [r for r in out["length_rows"] if r["n"] == 14][0]
    assert alln["counts_toward_headline"] is False and alln["lengths_comparable"] is False
    assert out["length"]["small_n_caution"] is True


def test_no_registration_language_anywhere(out):
    src = (ANALYSIS_DIR / "v04_gps_validation.py").read_text(encoding="utf-8").lower()
    blob = json.dumps(out).lower() + src
    for bad in ("pre-registered", "preregistered", "pre-declared", "predeclared",
                "fixed in advance", "pre-specified"):
        assert bad not in blob, bad
    assert out["criteria"]["criteria_declared_in"] == "module, same commit as first results"
    assert "pass statistic" in out["criteria"]["mean_signed_bias_role"]


# ── geometry corroboration ───────────────────────────────────────────────────
def test_graded_corroboration_recomputes_and_any_count_is_qualified(out):
    ev = pd.read_csv(GPS / "route_evidence.csv")
    f = ev["obs_frac"]
    rc = out["route_coverage"]
    assert rc["n_with_any_observation"] == int((f > 0).sum())
    assert rc["n_corroborated_50pct"] == int((f >= 0.5).sum())
    assert rc["n_corroborated_80pct"] == int((f >= 0.8).sum())
    assert rc["n_fully_covered"] == int((f >= 0.999).sum())
    assert (rc["n_with_any_observation"] >= rc["n_corroborated_50pct"]
            >= rc["n_corroborated_80pct"] >= rc["n_fully_covered"])
    assert "weakest" in rc["n_with_any_observation_note"]
    head = rc["corroboration_headline"]
    assert head["n_routes"] == rc["n_corroborated_50pct"] and ">= 50 %" in head["criterion"]
    assert len(rc["graded_corroboration"]) == 5
    assert rc["n_strong_50pct_2drivers"] == int(((f >= 0.5) & (ev["n_drivers"] >= 2)).sum())


# ── fleet rule ───────────────────────────────────────────────────────────────
def test_engine_fleet_rule_ceils_not_truncates():
    # 110.1/20 -> 6 operating buses; 6 * 1.15 = 6.9 -> engine rounds UP to 7 (old code gave 6)
    assert V.engine_fleet(110.1, 20.0, "Urban") == 7
    assert int(np.ceil(110.1 / 20.0) * 1.15) == 6          # the earlier, truncating formula
    assert V.engine_fleet(5.0, 60.0, "Regional_District") == 2     # 1 * 1.15 -> 2
    assert V.engine_fleet(1.0, 60.0, "Urban") == 2                  # class floor


def test_fleet_rule_reproduces_published_plan_and_consequence_recomputes(out, plan):
    non_sscl = plan[~plan.index.str.startswith("SSCL")]
    got = [V.engine_fleet(float(r.Cycle_Time_Min), float(r.Headway_Min), str(r.Route_Type))
           for r in non_sscl.itertuples()]
    assert got == non_sscl["Fleet_Required"].astype(int).tolist()
    st = out["fleet_consequence"]["formula_self_test"]
    assert st["n_checked"] == st["n_reproduced"] == len(non_sscl)
    # independent recompute of the five-route consequence
    rc = pd.read_csv(C.GPS_REALITY_CSV)
    five = rc[rc["klass"] == "matched"]
    total = 0
    for r in five.itertuples():
        p = plan.loc[r.permit]
        obs_cycle = (r.obs_oneway_min / r.obs_km) * p.Route_KM * 2 * 1.10
        op = max(1, int(np.ceil(obs_cycle / p.Headway_Min)))
        total += max(int(np.ceil(round(op * 1.15, 9))), V.FLEET_FLOOR[p.Route_Type])
    fc = out["fleet_consequence"]
    assert fc["fleet_observed_total"] == total
    assert fc["fleet_plan_total"] == int(plan.loc[FIVE_IDS, "Fleet_Required"].sum()) == 27
    assert fc["in_sample"] == "yes"
    assert fc["fleet_plan_pre_correction_total"] == 20


# ── headline ─────────────────────────────────────────────────────────────────
def test_headline_states_n_and_in_sample_and_numbers_trace_to_json(out):
    h = out["headline"]
    assert "2,526" in h and "2,426" in h and "43,809" in h
    assert "not a count of runs" in h and "in-sample" in h
    assert "n = 5" in h
    five = next(r for r in out["runtime_by_subset"]
                if r["comparison"].startswith("One-way") and r["subset"] == "retimed_in_sample"
                and r["plan_basis"] == V.PUB)
    assert f"MAPE {five['mape_pct']:.1f} %" in h
    cs = out["route_coverage"]
    assert f"{cs['n_corroborated_50pct']}" in h and f"{cs['n_corroborated_80pct']}" in h
    assert "module, same commit as first results" in h


def test_spearman_exact_p_matches_enumeration():
    assert V.spearman_p_exact([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == pytest.approx(2 / 120)
    assert V.spearman_p_exact([1, 2, 3], [1, 3, 2]) == pytest.approx(1.0)
    assert np.isnan(V.spearman_p_exact(list(range(12)), list(range(12))))
