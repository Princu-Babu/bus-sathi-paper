"""
Phase-1 audit fixes, work package E (equity, transfers, network diagnostics).

Reads the regenerated outputs in data/derived/ and checks the corrected
behaviour. Findings: F-03-01 (gini), F-08-12 (Gini decomposition),
F-04-11 / F-01-P (losers), F-04-13 / F-01-R / F-07-06 (wait cases, break-even),
F-04-09 (Moran decomposition), F-04-07 (snapping cross-check).
"""
import json
import math

import numpy as np
import pytest

import analysis.common as C


def _load(stem):
    path = C.DERIVED / f"{stem}.json"
    if not path.exists():
        pytest.skip(f"{path.name} not generated")
    return json.loads(path.read_text(encoding="utf-8"))


def _mad_gini(x, w=None):
    """Independent closed form: sum_ij w_i w_j |x_i - x_j| / (2 W^2 mean_w(x))."""
    x = np.asarray(x, float)
    w = np.ones_like(x) if w is None else np.asarray(w, float)
    diff = np.abs(x[:, None] - x[None, :])
    num = (w[:, None] * w[None, :] * diff).sum()
    mean = (w * x).sum() / w.sum()
    return num / (2.0 * w.sum() ** 2 * mean)


# ── F-03-01 ───────────────────────────────────────────────────────────────────
def test_gini_small_vectors_closed_form():
    assert C.gini([1, 1]) == pytest.approx(0.0, abs=1e-12)
    assert C.gini([0, 1]) == pytest.approx(0.5, abs=1e-12)
    assert C.gini([0, 0, 0, 1]) == pytest.approx(0.75, abs=1e-12)


def test_gini_matches_independent_formula_random():
    rng = np.random.default_rng(C.RANDOM_SEED)
    for _ in range(5):
        x = rng.gamma(0.7, 3.0, size=60)
        w = rng.integers(1, 20, size=60).astype(float)
        assert C.gini(x) == pytest.approx(_mad_gini(x), abs=1e-9)
        assert C.gini(x, w) == pytest.approx(_mad_gini(x, w), abs=1e-9)


# ── F-08-12 ───────────────────────────────────────────────────────────────────
def test_gini_decomposition_identity_and_headline():
    d = _load("a12_equity_gini")
    dec = d["accessibility_gini_after"]["gini_decomposition"]
    for key in ("frequency_weighted", "route_count"):
        b = dec[key]
        z, gs = b["zero_service_share_z"], b["gini_served_only"]
        assert b["gini_all"] == pytest.approx(z + (1 - z) * gs, abs=1e-9)
        assert b["component_zero_service"] == pytest.approx(z)
        assert b["share_of_gini_from_zero_service"] == pytest.approx(z / b["gini_all"])
    assert d["accessibility_gini_after"]["gini_frequency_weighted"] == pytest.approx(
        dec["frequency_weighted"]["gini_all"])
    assert d["before_after"]["plan_effect_on_equity"].startswith("not estimable")


# ── F-04-11 / F-01-P ──────────────────────────────────────────────────────────
def test_losers_totals_consistent_with_listed_routings():
    d = _load("a12_equity_gini")
    rows, s = d["losers"], d["losers_summary"]
    ok = [r for r in rows if r["status"] == "OK"]
    bad = [r for r in rows if r["status"] != "OK"]
    assert s["n_suppressed_via_routings"] == len(rows)
    assert s["n_computable"] == len(ok)
    assert s["n_not_computable"] == len(bad)
    assert len(ok) + len(bad) == len(rows)
    assert len(s["excluded_routings"]) == len(bad)
    # deduplicated union is bounded by max(single) and sum(all) of listed routings
    within = [r["pop_within_400m"] for r in ok]
    unc = [r["pop_uncovered_within_400m"] for r in ok]
    assert max(within) <= s["dedup_union_pop_within_400m"] <= sum(within) + 1e-6
    assert max(unc) <= s["dedup_union_pop_uncovered_within_400m"] <= sum(unc) + 1e-6
    assert s["dedup_union_pop_uncovered_within_400m"] <= s["dedup_union_pop_within_400m"]


def test_losers_range_across_variants_is_min_max_of_variants():
    s = _load("a12_equity_gini")["losers_summary"]
    vals = [v["dedup_union_pop_uncovered_within_400m"] for v in s["variants"].values()]
    assert len(vals) == s["range_across_variants"]["n_variants"] == 8
    assert s["range_across_variants"]["uncovered_min"] == pytest.approx(min(vals))
    assert s["range_across_variants"]["uncovered_max"] == pytest.approx(max(vals))
    assert min(vals) < max(vals)
    assert "proxy" in s["method_label"]


# ── F-04-13 / F-01-R / F-07-06 ────────────────────────────────────────────────
def test_wait_cases_complete_and_headline_range_is_min_max():
    d = _load("a13_transfers")
    cases = d["wait_cases"]
    assert len(cases) == 16                       # 4 duty x 2 baseline x 2 plan arrival
    combos = {(c["duty_case"], c["baseline_arrival_model"], c["plan_arrival_model"])
              for c in cases}
    assert len(combos) == 16
    for c in cases:
        assert c["change_of_medians_min"] == pytest.approx(
            c["median_plan_wait_min"] - c["median_baseline_wait_min"], abs=0.011)
        assert 0 <= c["pct_od_wait_worse"] <= 100 and c["n_od"] == 68
    h = d["wait_headline"]
    ch = [c["median_change_min"] for c in cases]
    assert h["median_change_min_min"] == min(ch) and h["median_change_min_max"] == max(ch)
    assert h["median_change_min_range"] == [min(ch), max(ch)]
    assert h["n_cases_plan_wait_shorter_at_median"] == sum(x < 0 for x in ch)
    assert min(ch) < 0 < max(ch)       # sign depends on the case: no single finding
    q = [c for c in cases if c["previously_quoted"]]
    assert len(q) == 1
    assert (q[0]["median_baseline_wait_min"], q[0]["median_plan_wait_min"]) == (86.68, 17.5)
    assert h["previously_quoted_case"]["median_change_min"] == q[0]["median_change_min"]
    assert d["headline"]["wait"] == h


def test_duty_factor_provenance_stated():
    d = _load("a13_transfers")
    duty = d["baseline_model"]["duty_factor_observed"]
    assert duty["is_from_permit_holder_operations"] is False
    assert "SSCL" in duty["transferability_note"]
    assert duty["median_calendar_days_per_driver"] is not None or "sidecar" in duty["source"].lower() \
        or duty["n_drivers"] > 0
    assert "NOT a measurement of permit-holder" in duty["transferability_note"]


def test_breakeven_reports_pairs_not_a_fake_median():
    b = _load("a13_transfers")["breakeven"]
    pairs = b["pairs"]
    assert len(pairs) == b["n_distinct_od"] == 2
    vals = [p["breakeven_penalty_min_central"] for p in pairs]
    assert b["central_breakeven_penalty_min_mean"] == pytest.approx(np.mean(vals), abs=0.01)
    assert b["central_breakeven_penalty_min_median"] == pytest.approx(np.mean(vals), abs=0.01)
    assert b["summary_statistic_word"] == "mean of two pairs"
    assert "MEAN of two" in b["central_breakeven_penalty_min_median_note"]
    assert min(vals) < 0 < max(vals)
    assert all(p["n_register_rows_same_od"] >= 1 for p in pairs)


# ── F-04-09 ───────────────────────────────────────────────────────────────────
def test_moran_decomposition_separates_population_from_gap():
    m = _load("a10_network_diagnostics")["morans_i_decomposition"]
    assert m["status"] == "OK" and m["permutations"] >= 999
    pp = m["primary_h2km"]
    # head-count I does not exceed total-population I: it mostly measures settlement
    assert pp["I_uncovered_headcount"] < pp["I_total_population"]
    assert 0 < pp["I_uncovered_share_inhabited"] < pp["I_uncovered_headcount"]
    assert pp["p_uncovered_share"] <= 0.05
    for v in m["variants"]:
        for k in ("uncovered_headcount_full_lattice", "total_population_full_lattice",
                  "uncovered_share_inhabited", "uncovered_residual_on_total_inhabited"):
            assert -1.0 <= v[k]["morans_I"] <= 1.0 and 0 < v[k]["p_sim"] <= 1.0


# ── F-04-07 ───────────────────────────────────────────────────────────────────
def test_snapping_cross_check_verdict_follows_its_own_numbers():
    a = _load("a10_network_diagnostics")["active"]
    s = a["snapping_cross_check"]
    exact = s["ratio_exact"]
    assert exact == pytest.approx(a["route_km_to_network_km_ratio"])
    snapped = [r["ratio"] for r in s["rows"] if 0 < r["grid_m"] <= 10]
    assert len(snapped) == 5
    rise = (max(snapped) - exact) / exact
    assert s["max_rise_pct_vs_exact"] == pytest.approx(100 * rise, abs=0.01)
    expected = "ratio_depends_on_tolerance" if rise > 0.02 else "ratio_robust_within_2pct"
    assert s["verdict"] == expected
    assert s["verdict"] == "ratio_depends_on_tolerance"   # the 10 % rise the audit found
    assert not math.isclose(max(snapped), exact, rel_tol=0.02)
