"""
Tests for audit work package C (fleet model, sensitivity, Monte Carlo / Sobol').

Covers F-08-10 (theta not sampled; every sampled input live), F-04-03 (S1 and ST),
F-01-V (named intervals), F-01-X (reconciliation), F-04-01/02 (two observed-pace
methods, evidence split), F-03-03/F-11-10 (decomposed reproduction), F-03-04/F-08-14
(congestion disclosure). Reads published outputs in data/derived and recomputes the
model; the determinism test runs a09 twice at reduced n with an output suffix.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import common as C  # noqa: E402
import fleet_model as F  # noqa: E402
import a09_monte_carlo_sobol as A9  # noqa: E402

PY = sys.executable


@pytest.fixture(scope="module")
def arr():
    return F.load_arrays()


@pytest.fixture(scope="module")
def a09():
    return json.loads((C.DERIVED / "a09_monte_carlo_sobol.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def a08():
    return json.loads((C.DERIVED / "a08_sensitivity_oat.json").read_text(encoding="utf-8"))


# ── F-08-10 ──────────────────────────────────────────────────────────────────
def test_theta_not_sampled_and_not_in_sobol(a09):
    assert "OVERLAP_THRESHOLD" not in A9.SAMPLED_PARAMS
    assert "OVERLAP_THRESHOLD" not in a09["parameters"]
    assert "OVERLAP_THRESHOLD" in a09["parameters_not_sampled"]
    assert a09["route_set_uncertainty"] == "not propagated"
    for out, rows in a09["sobol"].items():
        assert "OVERLAP_THRESHOLD" not in rows, out
    s4 = a09["route_set_uncertainty_detail"]["bounding_scenario_S4"]
    a15 = json.loads((C.DERIVED / "a15_scenarios.json").read_text(encoding="utf-8"))
    ref = next(x for x in a15["scenarios"] if x["scenario"] == "S4")
    assert s4["fleet"] == ref["fleet"] and s4["routes"] == ref["routes"]


def test_every_sampled_input_is_live_and_theta_is_inert():
    m = A9.Model()
    rng = np.random.default_rng(1)
    priors = A9.pace_priors_both(rng)
    margs = {n: A9.marginal(C.PARAMETERS[n]) for n in A9.SAMPLED_PARAMS}
    live = A9.liveness_check(m, margs, priors)   # default sweep (9 points x 6 contexts); raises if any input is dead
    assert set(live["sampled"]) == set(A9.SAMPLED_PARAMS) | set(A9.PACE_DIMS)
    assert all(v["live"] for v in live["sampled"].values())
    # the excluded parameter really is inert (the property that justified removing it)
    assert live["excluded"]["OVERLAP_THRESHOLD"]["live"] is False


def test_liveness_detects_a_dead_input():
    m = A9.Model()
    priors = A9.pace_priors_both(np.random.default_rng(1))
    margs = {n: A9.marginal(C.PARAMETERS[n]) for n in A9.SAMPLED_PARAMS}
    A9.SAMPLED_PARAMS.append("OVERLAP_THRESHOLD")
    margs["OVERLAP_THRESHOLD"] = A9.marginal(C.PARAMETERS["OVERLAP_THRESHOLD"])
    try:
        with pytest.raises(RuntimeError, match="OVERLAP_THRESHOLD"):
            A9.liveness_check(m, margs, priors, n_pts=3, n_contexts=0)
    finally:
        A9.SAMPLED_PARAMS.remove("OVERLAP_THRESHOLD")


# ── F-04-03 ──────────────────────────────────────────────────────────────────
def test_first_order_not_above_total_order_beyond_ci(a09):
    n_checked = 0
    for out, rows in a09["sobol"].items():
        for n, v in rows.items():
            assert set(("S1", "S1_conf", "ST", "ST_conf")) <= set(v)
            assert v["S1"] <= v["ST"] + v["S1_conf"] + v["ST_conf"], (out, n)
            n_checked += 1
    assert n_checked >= 5 * 12
    meta = a09["sobol_meta"]
    assert meta["n_evaluations"] == 1024 * (12 + 2) == a09["n_sobol_evals"]
    assert meta["confidence_level"] == 0.95
    assert "S1" in meta["headline_convention"]


def test_sobol_out_of_range_estimates_are_flagged_not_clipped(a09):
    flagged = {(f["output"], f["parameter"], f["index"]) for f in a09["sobol_meta"]["flags"]}
    for out, rows in a09["sobol"].items():
        for n, v in rows.items():
            for idx in ("S1", "ST"):
                if v[idx] < 0 or v[idx] > 1:
                    assert (out, n, idx) in flagged
    # synthetic: the flagging function itself
    fake = {"o": {"p": dict(S1=-0.02, S1_conf=0.01, ST=0.0, ST_conf=0.01),
                  "q": dict(S1=0.5, S1_conf=0.01, ST=1.2, ST_conf=0.01),
                  "r": dict(S1=0.9, S1_conf=0.01, ST=0.2, ST_conf=0.01)}}
    kinds = {(f["parameter"], f["kind"]) for f in A9.sobol_flags(fake)}
    assert ("p", "negative") in kinds and ("q", "above_1") in kinds and ("r", "first_order_exceeds_total") in kinds


# ── F-01-V ───────────────────────────────────────────────────────────────────
def test_intervals_are_named_with_percentiles(a09):
    assert "p5-p95" in a09["interval_definition"] and "not a confidence interval" in a09["interval_definition"]
    for k, s in a09["mc"].items():
        assert s["p5"] <= s["median"] <= s["p95"] and s["min"] <= s["p5"] and s["p95"] <= s["max"], k
        assert s["n"] == a09["n_mc"]
        assert s["p5_p95"] == [s["p5"], s["p95"]] and s["min_max"] == [s["min"], s["max"]]
    h = a09["headline"]
    assert h["fleet_A_p5_p95"] == h["fleet_A_90"]
    assert h["fleet_A_min_max"][0] < h["fleet_A_p5_p95"][0]
    assert "percentile" in h["interval_note"]


# ── F-04-01 / F-04-02 ────────────────────────────────────────────────────────
def test_two_observed_pace_methods_reported(a09, arr):
    assert {"fleet_B", "fleet_B_moving"} <= set(a09["mc"])
    assert a09["fleet_B_at_median_pace"] == 1169 and a09["fleet_B_moving_at_median_pace"] != 1169
    # method (b) is implemented: it differs from (a) and leaves non-targeted routes unchanged
    pm = {"Urban": 3.3, "Peri_Urban": 2.9}
    pe = {"Urban": 4.8, "Peri_Urban": 4.55}
    fb = F.fleet(arr, pace_override=pe)
    fm = F.fleet_ext(arr, moving_pace_override=pm)
    other = arr.sscl | arr.measured | (arr.rtype == "Regional_District")
    assert (fb[other] == arr.fleet_pub[other]).all() and (fm[other] == arr.fleet_pub[other]).all()
    assert fb.sum() != fm.sum()
    with pytest.raises(ValueError):
        F.cycle_time_ext(arr, pace_override=pe, moving_pace_override=pe)


def test_evidence_split_counts(a09, arr):
    es = a09["evidence_split"]
    assert es["directly_measured"]["n"] == 5 == int(arr.measured.sum())
    assert es["imputed_from_corridor_prior"]["n"] == 84
    total = (es["directly_measured"]["n"] + es["imputed_from_corridor_prior"]["n"]
             + es["unaffected_backbone"]["n"] + es["unaffected_regional"]["n"])
    assert total == 186
    pool = es["imputed_from_corridor_prior"]
    assert pool["prior_pool_n_corridors"] == pool["prior_pool_n_plan_corridors"] + pool["prior_pool_n_non_plan_corridors"] == 16
    assert pool["prior_pool_n_non_plan_corridors"] == 5
    assert pool["prior_pool_of_which_directly_applied_by_engine"] == 5
    # fleet shares reconcile to the published total
    fl = sum(es[k]["fleet_published"] for k in ("directly_measured", "imputed_from_corridor_prior",
                                                "unaffected_backbone", "unaffected_regional"))
    assert fl == int(arr.fleet_pub.sum()) == 1011


def test_observed_pace_reconciliation_definitions(a09):
    rec = {r["set"]: r for r in a09["observed_pace_reconciliation"]}
    assert rec["all_18_corridors"]["n_corridors"] == 18
    assert rec["belt_16_corridors_lt20km_of_hub"]["n_corridors"] == 16
    assert rec["urban_7_belt_core_and_mid"]["n_corridors"] + rec["peri_9_belt_periphery"]["n_corridors"] == 16
    for r in rec.values():   # moving pace excludes dwell, so it is always the faster (smaller) pace
        assert r["median_pace_moving_min_per_km"] < r["median_pace_effective_min_per_km"]


def test_reconciliation_block_adds_up(a09):
    r = a09["fleet_B_reconciliation"]["B_effective"]
    assert r["component_medians_sum"] == sum(r["component_medians"].values())
    assert r["component_medians_sum_minus_median_of_total"] == pytest.approx(
        r["component_medians_sum"] - r["mc_median_of_total"])
    assert r["median_minus_fleet_at_median_pace"] == r["mc_median_of_total"] - r["fleet_at_median_pace_other_params_at_baseline"]
    assert a09["mc"]["fleet_B"]["median"] == r["mc_median_of_total"]


# ── F-03-03 / F-11-10 ────────────────────────────────────────────────────────
def test_published_reproduction_still_186_of_186(arr):
    b = F.verify_baseline(arr)
    assert (b["cycle_reproduced"], b["fleet_reproduced"], b["fleet_total"]) == (186, 186, 1011)
    assert int(F.fleet(arr).sum()) == int(arr.fleet_pub.sum()) == 1011
    assert (F.fleet(arr) == arr.fleet_pub).all()


def test_decomposed_verification_sums_and_drops(arr, a08):
    d = F.verify_baseline_decomposed(arr)
    dev = d["devices"]
    cap = F.at_cap_mask(arr)
    assert dev["D1_per_km_cap"]["n_routes_cycle_set_by_cap"] == int(cap.sum())
    assert sum(dev["D1_per_km_cap"]["by_class"].values()) == int(cap.sum())
    assert dev["D2_measured_cycles_copied_from_plan"]["n_routes"] == 5
    assert dev["D4_headways_taken_as_inputs"]["n_routes"] == 186
    assert sum(dev["D4_headways_taken_as_inputs"]["headway_counts"].values()) == 186
    assert d["n_routes_cycle_independently_recomputed"] == int((~cap & ~arr.measured).sum())
    assert d["n_routes_cycle_independently_recomputed"] + int((cap & ~arr.measured).sum()) + int(arr.measured.sum()) == 186
    ag = d["agreement"]
    assert ag["V0_published_devices_kept"]["fleet_reproduced"] == 186
    v4 = d["agreement_without_devices_D2_D3"]
    assert v4 == ag["V4_measured_recomputed_capped_sscl_floor_removed"]
    # removing the devices must make the agreement strictly worse than the published 186/186
    assert v4["fleet_reproduced"] < 186 and v4["fleet_total"] != 1011
    # audit measured 180/186 and 1,000 of 1,011
    assert (v4["fleet_reproduced"], v4["fleet_total"]) == (180, 1000)
    # fleet_total in each variant equals the sum of per-route fleets recomputed independently
    n = F.fleet_ext(arr, use_sscl_floor=False, measured_cycle="capped")
    assert int(n.sum()) == v4["fleet_total"]
    assert a08["baseline_reproduction_decomposed"]["agreement_without_devices_D2_D3"]["fleet_total"] == 1000
    g = d["measured_corridors_recomputed_from_gps_moving_speed"]
    assert len(g["routes"]) == 5 and g["n_cycle_within_0p11"] <= 5


# ── F-03-04 / F-08-14 ────────────────────────────────────────────────────────
def test_congestion_disclosure_counts(arr, a08):
    c = a08["congestion_disclosure"]
    assert c["n_city_core_recorded"] == int(arr.city_core.sum())
    assert c["n_city_core_recorded"] + c["n_peri_urban_recorded"] == 186
    assert sum(v["city_core"] for v in c["by_route_type"].values()) == c["n_city_core_recorded"]
    assert sum(v["n"] for v in c["by_route_type"].values()) == 186
    assert c["n_regional_assigned_city_core"] == c["by_route_type"]["Regional_District"]["city_core"] > 0
    assert "latitude" in c["rule"].lower()
    fd = c["fleet_dependence"]
    assert fd["published"] == 1011 == int(F.fleet_ext(arr).sum())
    assert fd["n_routes_cycle_set_by_cap"] == int(F.at_cap_mask(arr).sum())
    # direction and size are recomputed, not copied
    assert fd["cap_removed_chi_2p2"] == int(F.fleet_ext(arr, cap_scale=np.inf).sum())
    assert fd["chi_1p4_everywhere_cap_on"] == int(F.fleet_ext(arr, {"CONGESTION_CITY_CORE": F.CONGESTION_PERI}).sum())
    assert fd["cap_removed_chi_2p2"] > fd["cap_removed_chi_1p4"] > fd["published"] - 100
    assert abs(fd["delta_chi_cap_on"]) < abs(fd["chi_effect_when_cap_removed"])


def test_extension_defaults_equal_existing_functions(arr):
    assert (F.cycle_time_ext(arr) == F.cycle_time(arr)).all()
    assert (F.fleet_ext(arr) == F.fleet(arr)).all()
    assert (F.fleet_ext(arr, {"CONGESTION_CITY_CORE": 1.6}, cap_scale=np.inf)
            == F.fleet(arr, {"CONGESTION_CITY_CORE": 1.6}, cap_scale=np.inf)).all()


# ── determinism ──────────────────────────────────────────────────────────────
def test_a09_deterministic_at_reduced_n():
    sfx = "_wpCtest"
    outs = []
    created = []
    try:
        for _ in range(2):
            r = subprocess.run([PY, str(ROOT / "analysis" / "a09_monte_carlo_sobol.py"), "--n-mc", "60",
                                "--n-sobol", "16", "--out-suffix", sfx, "--no-tables"],
                               cwd=str(ROOT), capture_output=True, text=True, timeout=900)
            assert r.returncode == 0, r.stderr[-2000:]
            p = C.DERIVED / f"a09_monte_carlo_sobol{sfx}.json"
            created = sorted(C.DERIVED.glob(f"*{sfx}*"))
            d = json.loads(p.read_text(encoding="utf-8"))
            assert "runtime_sec" not in d   # wall-clock is volatile and no longer stored
            outs.append(json.dumps(d, sort_keys=True))
        assert outs[0] == outs[1]
        assert json.loads(outs[0])["n_mc"] == 60
    finally:
        for f in C.DERIVED.glob(f"*{sfx}*"):
            f.unlink()
