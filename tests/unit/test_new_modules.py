"""
Tests for the modules added 2026-09-30: the verified supply model (fleet_model),
the operational modules (a06, a07, a14, a15), validation channels (v01, v02),
and the citation audit. Each test checks a contract the manuscript relies on,
not an incidental value.
"""
import json
import sys

import numpy as np
import pytest

from tests.conftest import ANALYSIS_DIR, DERIVED_DIR, PAPER_DIR, EXPECTED_STATED_FLEET

sys.path.insert(0, str(ANALYSIS_DIR))
sys.path.insert(0, str(PAPER_DIR))


def _load(stem):
    p = DERIVED_DIR / f"{stem}.json"
    if not p.exists():
        pytest.skip(f"{stem} has not run")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def arr():
    import fleet_model as F
    return F.load_arrays()


def test_fleet_model_reproduces_published_plan_exactly(arr):
    import fleet_model as F
    out = F.verify_baseline(arr)
    assert out["cycle_reproduced"] == 186
    assert out["fleet_reproduced"] == 186
    assert out["fleet_total"] == EXPECTED_STATED_FLEET


def test_cap_binds_on_169_routes(arr):
    import fleet_model as F
    assert int(F.at_cap_mask(arr).sum()) == 169


def test_fleet_monotone_in_spare_ratio(arr):
    import fleet_model as F
    lo = F.fleet(arr, {"FLEET_SPARE_RATIO": 1.05}).sum()
    hi = F.fleet(arr, {"FLEET_SPARE_RATIO": 1.25}).sum()
    assert lo <= EXPECTED_STATED_FLEET <= hi


def test_removing_cap_never_reduces_fleet(arr):
    import fleet_model as F
    assert np.all(F.fleet(arr, cap_scale=np.inf) >= F.fleet(arr))


def test_measured_corridors_held_at_published_cycle(arr):
    import fleet_model as F
    cyc = F.cycle_time(arr, congestion_city=2.8, stop_penalty=1.5)
    assert np.allclose(cyc[arr.measured], arr.cycle_pub[arr.measured])


def test_scenario_s0_is_the_published_plan():
    j = _load("a15_scenarios")
    s0 = next(s for s in j["scenarios"] if s["scenario"] == "S0")
    assert s0["fleet"] == EXPECTED_STATED_FLEET
    assert s0["routes"] == 186
    assert abs(s0["coverage_any"] - 0.242) < 0.001


def test_deadhead_is_bounded_not_measured():
    j = _load("a06_deadhead")
    assert j["status"] == "BOUNDED_NOT_MEASURED"
    assert j["network"]["deadhead_share_D0"] == 0.0
    assert 0 < j["network"]["deadhead_share_D1"] < j["observed_day"]["deadhead_share_D1"] < 1


def test_cost_module_is_marked_provisional_and_unverified():
    j = _load("a14_cost_emissions")
    assert j["status"] == "PROVISIONAL_PENDING_D8"
    # only the primary-sourced constants (and press-sourced GCC rates) are flagged; diesel and cost rates are not
    assert j["constants"]["diesel_kmpl_full_size"]["verified"] is False
    assert j["constants"]["cost_inr_per_km_full_size"]["verified"] is False
    assert all(c["verified"] in (True, False, "press") for c in j["constants"].values())
    for b in j["bases"].values():
        lo, hi = b["cost_inr_per_year"]
        assert lo < hi


def test_v02_discloses_circularity_and_reports_failure_honestly():
    j = _load("v02_benchmark")
    assert len(j["circularity"]) >= 3
    ratios = [r["ratio"] for r in j["sweep"]]
    assert all(r > 1.15 for r in ratios)                 # fails the band everywhere
    assert j["n_assumptions_within_tolerance"] == 0


def test_v01_states_partial_circularity():
    j = _load("v01_spatial_crossval")
    assert any("covariate" in c for c in j["caveats"])
    assert j["route_scale"]["n"] == 186


def test_every_citation_key_resolves():
    import citations as CI
    bib = CI.load_bib()
    cited, missing = [], set()
    for f in sorted((PAPER_DIR / "sections").glob("*.md")):
        CI.render(f.read_text(encoding="utf-8"), bib, cited, missing)
    assert not missing, f"unresolved citation keys: {sorted(missing)}"


def test_mc_interval_brackets_published_fleet_under_regime_a():
    j = _load("a09_monte_carlo_sobol")
    a = j["mc"]["fleet_A"]
    assert a["p5"] <= EXPECTED_STATED_FLEET <= a["p95"]
    # observation-anchored regime can only add run time on urban/peri routes
    assert j["mc"]["fleet_B"]["median"] >= a["median"]
