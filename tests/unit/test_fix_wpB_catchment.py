"""
Tests for work package B (catchments, coverage, faithfulness). They read the
cached outputs and recompute headline statistics from the cached per-route data.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import common as C  # noqa: E402
import a02_network_catchments as A02  # noqa: E402

D = ROOT / "data" / "derived"
T = ROOT / "paper" / "tables"


@pytest.fixture(scope="module")
def a02():
    return json.loads((D / "a02_network_catchments.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def a02b():
    return json.loads((D / "a02b_faithfulness.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cached():
    return pd.read_csv(D / "a02_catchments.csv")


def test_overstatement_exceeds_spurious_share_whenever_network_smaller():
    E = np.array([100.0, 200.0, 50.0, 80.0])
    N = np.array([60.0, 199.0, 10.0, 80.0])
    s = A02.spurious_share_pct(E, N)
    o = A02.overstatement_of_network_pct(E, N)
    smaller = N < E
    assert np.all(o[smaller] > s[smaller])
    assert o[3] == s[3] == 0.0
    # identity overstatement = s / (1 - s)
    sf = s / 100.0
    assert np.allclose(o / 100.0, sf / (1 - sf))


def test_cached_catchments_file_keeps_original_schema_and_values(cached):
    # the heavy-build cache must not have been rewritten by the summary path
    assert len(cached) == 186
    assert "spurious_share_of_euclidean_pct" not in cached.columns
    assert list(cached.columns[:5]) == ["New_Route_ID", "Route_Name", "Route_Type", "Route_KM", "geom_km"]
    assert "overstatement_pct" in cached.columns


def test_per_route_both_bases_recompute_from_cache(a02, cached):
    E, N = cached["pop_euclid"].to_numpy(float), cached["pop_net"].to_numpy(float)
    s = 100 * (E - N) / E
    o = 100 * (E - N) / N
    assert a02["spurious_share_of_euclidean_pct_median"] == pytest.approx(np.median(s), rel=1e-9)
    assert a02["overstatement_of_network_pct_median"] == pytest.approx(np.median(o), rel=1e-9)
    assert a02["overstatement_of_network_pct_median"] > a02["spurious_share_of_euclidean_pct_median"]
    assert a02["overstatement_of_network_pct_p25"] == pytest.approx(np.percentile(o, 25), rel=1e-9)
    # the legacy name must carry the spurious share and be annotated
    assert a02["overstatement_pct_median"] == pytest.approx(np.median(s), rel=1e-9)
    assert "SPURIOUS SHARE" in a02["overstatement_pct_median_note"]
    # the legacy cached column equals the spurious share, not (E-N)/N
    assert np.allclose(cached["overstatement_pct"], s, atol=1e-6)


def test_union_both_bases_consistent(a02):
    u = a02["bias_union"]
    assert u["network_pop"] < u["euclid_pop"]
    assert u["overstatement_of_network_pct"] > u["spurious_share_of_euclidean_pct"]
    assert u["spurious_share_of_euclidean_pct"] == pytest.approx(
        100 * (u["euclid_pop"] - u["network_pop"]) / u["euclid_pop"], rel=1e-9)
    assert u["overstatement_of_network_pct"] == pytest.approx(
        100 * (u["euclid_pop"] - u["network_pop"]) / u["network_pop"], rel=1e-9)
    assert u["coverage_share_net"] == pytest.approx(u["network_pop"] / 6584762, rel=1e-12)


def test_sensitivity_beside_headline_and_no_lower_bound_claim(a02):
    s = a02["sensitivity"]
    assert {"tau50", "tau100", "tau150"} <= set(s["tau"])
    assert len(s["walk_budget_and_stop_spacing"]) >= 5
    summ = s["summary"]
    # verdict is computed from the sweep: recompute it
    head = summ["headline_spurious_share_median_pct"]
    smaller = [k for k, v in summ["spurious_share_median_by_setting"].items() if v < head - 1e-9]
    assert sorted(smaller) == sorted(summ["settings_with_smaller_bias_than_headline"])
    assert summ["headline_is_lower_bound_over_these_settings"] == (len(smaller) == 0)
    assert summ["headline_is_lower_bound_over_these_settings"] is False
    assert summ["bias_positive_at_every_setting"] is True
    # tau=150 gives a smaller spurious share than tau=100
    assert (s["tau"]["tau150"]["per_route"]["spurious_share_of_euclidean_pct"]["median"]
            < s["tau"]["tau100"]["per_route"]["spurious_share_of_euclidean_pct"]["median"])


def test_denominator_report(a02):
    d = a02["denominator"]
    assert d["engine_integer_truncation"] == 6584762
    assert d["round_half_up"] == 6584763
    assert d["used_in_all_shares"] == C.STUDY_AREA_POPULATION == 6584762
    assert 6584762 < d["raster_sum_inside_district_union"] < 6584763
    assert a02["study_area_population"] == 6584762


def test_euclidean_reconciliation_reports_both_totals(a02):
    r = a02["euclidean_union_reconciliation"]
    assert r["engine_published"]["union_pop"] == 2317958
    assert r["this_pipeline"]["union_pop"] == pytest.approx(a02["pop_euclid_union"])
    assert r["difference_persons"] == pytest.approx(r["this_pipeline"]["union_pop"] - 2317958)
    assert r["isolated_cause"] is False
    excluded = {c["cause"]: c["status"] for c in r["causes"]}
    assert excluded["tourist multiplier"] == "excluded_by_code"


def test_method_notes_present(a02):
    m = a02["method_notes"]
    assert "cell-centre" in m["zonal_rule"]
    assert m["network_construction"]["type"] == "node-sampled disc union"
    assert m["network_construction"]["formal_upper_bound_on_true_walkshed"] is False
    assert "not recomputed" in m["network_construction"]["effect_of_edge_densification"]


def test_tourist_block_not_a_coverage_quantity(a02b):
    t = a02b["tourist_inflation"]
    assert t["entered_network_coverage"] is False
    assert t["n_routes_affected"] == 8 == len(t["per_route_increments"])
    assert t["sum_of_per_route_increments"] == pytest.approx(
        sum(r["increment"] for r in t["per_route_increments"]))
    assert t["sum_of_per_route_increments"] == pytest.approx(285914, abs=1)
    assert "double-count" in t["sum_of_per_route_increments_note"]
    for r in t["per_route_increments"]:
        assert r["increment"] == pytest.approx(r["published_per_route_count"] * (1 - 1 / 1.3))
    assert "synthetic persons" not in json.dumps(t).replace("'synthetic persons injected", "").replace(
        "synthetic persons injected into the coverage numerator' was wrong", "")


def test_faithfulness_before_after_reported_separately(a02b):
    pre = a02b["reproduction"]["before_tourist_adjustment"]
    post = a02b["reproduction"]["after_tourist_adjustment"]
    for blk in (pre, post):
        assert {"n_within_1pct", "n_within_5pct", "max_abs_pct_error", "n"} <= set(blk)
    assert post["n_within_1pct"] >= pre["n_within_1pct"]
    lst = a02b["reproduction_non_reproducing_routes"]["after_tourist_adjustment"]
    assert len(lst) == post["n_not_within_1pct"] == post["n"] - post["n_within_1pct"]
    assert "NOT TESTED" in a02b["disposition_status"]


def test_faithfulness_csv_cause_status_and_counts(a02b):
    f = pd.read_csv(D / "a02b_faithfulness.csv")
    assert len(f) == 186
    nonrep = f[f["disposition"].isin(["stale_tourist_flag", "superseded_geometry", "reproduced_minor_drift"])]
    assert (nonrep["cause_status"] == "residual classification, not tested").all()
    assert f["disposition"].value_counts().to_dict() == a02b["disposition_counts"]


def test_tables_have_both_basis_columns():
    t = pd.read_csv(T / "table03a_catchment_bias.csv")
    assert {"spurious_share_of_euclidean_pct", "overstatement_of_network_pct"} <= set(t.columns)
    assert "overstatement_pct" not in t.columns
    assert (t["overstatement_of_network_pct"] > t["spurious_share_of_euclidean_pct"]).all()
    s = pd.read_csv(T / "table03a_catchment_bias_summary.csv")
    assert {"route_median_spurious_share_pct", "route_median_overstatement_pct",
            "union_spurious_share_pct", "union_overstatement_pct"} <= set(s.columns)
    assert s["setting"].iloc[0] == "HEADLINE"
    assert (s["route_median_overstatement_pct"] > s["route_median_spurious_share_pct"]).all()
    b = pd.read_csv(D / "a02_catchment_bias.csv")
    assert len(b) == 186
    assert (b["overstatement_of_network_pct"] > b["spurious_share_of_euclidean_pct"]).all()
