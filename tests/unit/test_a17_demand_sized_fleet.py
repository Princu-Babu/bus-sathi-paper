"""Tests for a17_demand_sized_fleet: demand-sized headway and fleet grid."""
import hashlib
import json
import subprocess
import sys

import numpy as np

from tests.conftest import ANALYSIS_DIR, DERIVED_DIR

sys.path.insert(0, str(ANALYSIS_DIR))

import a17_demand_sized_fleet as A  # noqa: E402
import common as C  # noqa: E402
import fleet_model as FM  # noqa: E402


def _ctx():
    arr, mean_cap, counts, phf, mults, _, _ = A.load_inputs()
    shares = counts / counts.sum(axis=1, keepdims=True)
    return arr, mean_cap, shares, phf, mults


def _fleet(rho, mname, pol, **kw):
    arr, mean_cap, shares, phf, mults = _ctx()
    return A.size(arr, mean_cap, shares, phf, rho, mults[mname], pol, **kw)["fleet"]


def test_monotone_in_target_load_and_demand():
    arr, *_ = _ctx()
    mnames = ["x1", "x2.24", "x4.49"]
    for pol in "abcd":
        for m in mnames:
            tot = [int(_fleet(r, m, pol).sum()) for r in (0.50, 0.70, 0.85)]
            assert tot[0] >= tot[1] >= tot[2], (pol, m, tot)
            assert tot[0] > tot[2]
        for r in (0.50, 0.70, 0.85):
            tot = [int(_fleet(r, m, pol).sum()) for m in mnames]
            assert tot[0] <= tot[1] <= tot[2], (pol, r, tot)
            assert tot[0] < tot[2]


def test_policy_ordering_c_ge_b_ge_a_per_route():
    for r in (0.50, 0.70, 0.85):
        for m in ("x1", "x2.24", "x4.49"):
            fa, fb, fc = (_fleet(r, m, p) for p in "abc")
            assert (fc >= fb).all() and (fb >= fa).all()
            assert fc.sum() > fa.sum()


def test_minimum_vehicle_respected_and_class_split_sums():
    arr, mean_cap, shares, phf, mults = _ctx()
    for pol in "abc":
        res = A.size(arr, mean_cap, shares, phf, 0.85, 1.0, pol)
        assert (res["fleet"] >= 1).all()
        assert (res["split"].sum(axis=1) == res["fleet"]).all()
        assert (res["split"] >= 0).all()
    # extreme: effectively zero demand under policy (a) -> every route still has a bus
    res = A.size(arr, mean_cap, shares, phf, 0.85, 1.0, "a", demand=np.full(len(arr.km), 1e-9))
    assert (res["fleet"] >= 1).all()
    assert int(res["fleet"].min()) == 2   # ceil(1 operating bus x 1.15 spare)


def test_reproduces_published_fleet_when_no_route_is_demand_bound():
    arr, mean_cap, shares, phf, mults = _ctx()
    res = A.size(arr, mean_cap, shares, phf, 0.70, 1.0, "d", floor_mode="plan",
                 demand=np.full(len(arr.km), 1e-6))
    assert not res["demand_bound"].any()
    nb = ~arr.sscl
    assert (res["fleet"][nb] == arr.fleet_pub[nb]).all()      # exact on all 156 non-backbone routes
    assert (res["fleet"] == arr.fleet_pub).all()               # and on the backbone (floor kept)
    assert int(res["fleet"].sum()) == 1011


def test_headway_inverts_to_target_load_and_matches_a07_definition():
    arr, mean_cap, shares, phf, mults = _ctx()
    D = arr.df["Daily_Demand_Pax"].to_numpy(float)
    h = A.demand_headway(D, mean_cap, phf, 0.70, 1.0)
    load = D * phf / (2.0 * (60.0 / h) * mean_cap)
    assert np.allclose(load, 0.70)
    a07 = C.read_result("a07_load_factor")
    pub_load = D * phf / (2.0 * (60.0 / arr.headway) * mean_cap)
    assert abs(float(np.median(pub_load)) - a07["proxy_network_both_directions"]["median"]) < 1e-9


def test_json_grid_matches_recomputation_and_decomposition_identity():
    j = json.loads((DERIVED_DIR / "a17_demand_sized_fleet.json").read_text(encoding="utf-8"))
    assert len(j["grid"]) == 3 * 3 * 4
    for g in j["grid"]:
        rho, mn, pol = g["target_load"], g["demand_level"], g["policy"]
        assert g["fleet_total"] == int(_fleet(rho, mn, pol).sum())
        assert g["HPV"] + g["MPV"] + g["LPV"] == g["fleet_total"]
        assert g["fleet_backbone"] + g["fleet_non_backbone"] == g["fleet_total"]
    d = j["decomposition_at_load_0p70"]["all_routes"]
    assert d["explained_by_demand"] + d["above_demand_need_service_standard"] == d["published"] == 1011
    assert d["net_published_minus_demand"] == (d["above_demand_need_service_standard"]
                                               - d["demand_need_beyond_plan"])
    bb = j["decomposition_at_load_0p70"]["backbone"]
    nb = j["decomposition_at_load_0p70"]["non_backbone"]
    assert bb["published"] + nb["published"] == 1011
    assert bb["n_routes"] == 30 and nb["n_routes"] == 156
    assert j["parameters"]["demand_multipliers"]["x2.24"] > 2.24 and \
        abs(j["parameters"]["demand_multipliers"]["x4.49"] - 2 * j["parameters"]["demand_multipliers"]["x2.24"]) < 1e-9
    assert j["reproduction_check"]["non_backbone_equal"] == j["reproduction_check"]["non_backbone_n"]


def test_deterministic_second_run():
    files = ["a17_demand_sized_fleet.json", "a17_route_demand_fleet.csv"]
    before = [hashlib.sha256((DERIVED_DIR / f).read_bytes()).hexdigest() for f in files]
    r = subprocess.run([sys.executable, str(ANALYSIS_DIR / "a17_demand_sized_fleet.py")],
                       capture_output=True, text=True, cwd=str(C.ROOT))
    assert r.returncode == 0, r.stderr[-500:]
    after = [hashlib.sha256((DERIVED_DIR / f).read_bytes()).hexdigest() for f in files]
    assert before == after
