#!/usr/bin/env python
"""
a09_monte_carlo_sobol.py — joint uncertainty in the plan's decisions (validation
channels V5 and V6) and the fleet as an interval rather than a point.

What is sampled. The eleven declared parameters of §4.10 (common.PARAMETERS),
each from its declared marginal: triangular with the engine value as mode, or
uniform, over the declared range. Draws are independent; no correlation between
parameters is asserted because none is measured.

Two supply regimes, both reported, neither privileged:

  A. As specified. The engine's cycle model with its per-km cap. This is the
     uncertainty the plan's own assumptions imply.
  B. Observation-anchored. For Urban and Peri-Urban non-backbone routes, the
     modelled one-way time and the cap are replaced by an observed one-way pace
     (min/km) times route length — the substitution the engine itself made for
     the five GPS-measured corridors in v3.4.5, extended to the classes the GPS
     record actually observes. The pace is a network-level quantity drawn from
     the bootstrap distribution of the median observed pace (v04 corridor
     profiles within 20 km of the Srinagar hub: 7 core/mid, 9 periphery), so the
     interval reflects uncertainty in the typical pace, not route-to-route
     scatter. Regional lifelines are unobserved (two long corridors only) and
     stay as modelled, cap included; that limitation is stated, not patched.
     The e-bus backbone (fleet fixed by CHALO floors and formula) and the five
     measured corridors stay as published.

Why B exists. v04 measured observed urban pace at 4.62 min/km against a 4.0
min/km urban cap and 2.5 peri-urban cap, and found the cap binding on 169/186
routes (F10). Under A, the fleet interval is narrow because the cap discards the
run-time parameters; that narrowness is not robustness. B is the defensible
counterfactual in which observation, not the guard, sets urban run time.

Outputs per draw: total fleet under A and B, deduplicated coverage share, and
tier agreement with the baseline partition. Reported: median and 90% interval
(5th–95th percentile) of each; the probability that tier agreement exceeds the
pre-registered 80% target; each route's tier-stability rate (share of draws in
which it keeps its baseline tier) and the share of routes above 80%.

Sobol' indices. Saltelli sampling (SALib), N = 1024 base samples, first-order
(S1) and total-order (ST) indices with bootstrap 95% confidence intervals, for
each output. Inputs are sampled on the unit hypercube and mapped through each
marginal's inverse CDF, which leaves the indices unchanged (a bijection per
input). Under regime B the two pace levels are added as inputs.

Seed: common.RANDOM_SEED.

Inputs
    data/derived/a08a_catchment_grid.{csv,json}, data/raw/gps/corridor_profiles.csv
Outputs
    data/derived/a09_monte_carlo_sobol.json
    data/derived/a09_mc_draws.csv
    data/derived/a09_route_tier_stability.csv
    paper/tables/table07b_mc_intervals.{csv,md}
    paper/tables/table07c_sobol.{csv,md}
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import fleet_model as F  # noqa: E402
from a08_sensitivity_oat import CatchmentGrid, tier_inputs  # noqa: E402

log = C.get_logger("a09")

N_MC = 5000
N_SOBOL = 1024
N_BOOT_PACE = 10000
URBAN_HUB_KM = 20.0            # corridors farther than this are not urban belt
TIER_TARGET = 0.80


# ── marginals ────────────────────────────────────────────────────────────────
def marginal(spec: dict):
    lo, hi = spec["range"]
    if spec["dist"] == "tri":
        c = (spec["value"] - lo) / (hi - lo)
        return stats.triang(c, loc=lo, scale=hi - lo)
    return stats.uniform(loc=lo, scale=hi - lo)


def pace_priors(rng) -> dict:
    """Bootstrap distribution of the median observed one-way pace by class."""
    prof = pd.read_csv(C.GPS_CORRIDOR_PROFILES_CSV)
    prof["pace"] = 60.0 / prof["effective_kmh"]
    belt = prof[prof["dist_hub_km"] < URBAN_HUB_KM]
    groups = {"Urban": belt[belt["zone"].isin(["core", "mid"])]["pace"].to_numpy(),
              "Peri_Urban": belt[belt["zone"] == "periphery"]["pace"].to_numpy()}
    out = {}
    for cls, x in groups.items():
        boot = np.median(rng.choice(x, size=(N_BOOT_PACE, len(x)), replace=True), axis=1)
        p5, p50, p95 = np.percentile(boot, [5, 50, 95])
        out[cls] = dict(n_corridors=int(len(x)), observed=[round(float(v), 3) for v in np.sort(x)],
                        median=float(np.median(x)), boot_p5=float(p5), boot_p50=float(p50),
                        boot_p95=float(p95), boot=boot)
    excluded = prof[prof["dist_hub_km"] >= URBAN_HUB_KM]
    out["_regional_unobserved"] = dict(
        n_corridors=int(len(excluded)),
        paces=[round(float(v), 3) for v in excluded["pace"]],
        note="Too few to form a prior; regional routes stay as modelled with the cap.")
    return out


class Model:
    def __init__(self):
        self.arr = F.load_arrays()
        F.verify_baseline(self.arr)
        self.grid = CatchmentGrid(self.arr.df["New_Route_ID"])
        self.tourist = tier_inputs(self.arr)
        self.base_tiers = self.tiers(F.BASE)

    def tiers(self, p: dict) -> np.ndarray:
        pop = self.grid.pop(p["WALK_CATCHMENT_M"], p["VIRTUAL_STOP_SPACING_M"])
        c = F.cdi(pop, self.grid.poi["high"], self.grid.poi["medium"], self.grid.poi["seasonal"],
                  self.arr.km, self.tourist, p["CDI_POP_WEIGHT"], p["POI_TIER2_WEIGHT"],
                  p["POI_TIER3_WEIGHT"], p["TOURIST_POPULATION_MULTIPLIER"])
        return F.jenks_tiers(c)

    def evaluate(self, p: dict, pace: dict | None) -> dict:
        t = self.tiers(p)
        fa = F.fleet(self.arr, p)
        out = dict(fleet_A=int(fa.sum()),
                   coverage=self.grid.coverage(p["WALK_CATCHMENT_M"], p["VIRTUAL_STOP_SPACING_M"]),
                   tier_agreement=float((t == self.base_tiers).mean()))
        if pace is not None:
            fb = F.fleet(self.arr, p, pace_override=pace)
            out["fleet_B"] = int(fb.sum())
            for cls in ("Urban", "Peri_Urban", "Regional_District"):
                out[f"fleet_B_{cls}"] = int(fb[self.arr.rtype == cls].sum())
        return out, t


def summarise(x: np.ndarray) -> dict:
    x = np.asarray(x, float)
    return dict(median=float(np.median(x)), mean=float(x.mean()), p5=float(np.percentile(x, 5)),
                p95=float(np.percentile(x, 95)), min=float(x.min()), max=float(x.max()))


def main() -> None:
    import argparse
    global N_MC, N_SOBOL
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-mc", type=int, default=N_MC)
    ap.add_argument("--n-sobol", type=int, default=N_SOBOL)
    a = ap.parse_args()
    N_MC, N_SOBOL = a.n_mc, a.n_sobol
    from SALib.analyze import sobol as sobol_analyze
    from SALib.sample import sobol as sobol_sample

    t0 = time.time()
    rng = np.random.default_rng(C.RANDOM_SEED)
    names = list(C.PARAMETERS)
    margs = [marginal(C.PARAMETERS[n]) for n in names]
    paces = pace_priors(rng)
    m = Model()
    arr = m.arr
    base_B = int(F.fleet(arr, pace_override={c: paces[c]["median"] for c in ("Urban", "Peri_Urban")}).sum())
    log.info("baseline fleet A %d; B at observed median pace %d; pace priors %s", int(arr.fleet_pub.sum()),
             base_B, {c: (round(paces[c]["boot_p5"], 2), round(paces[c]["boot_p95"], 2))
                      for c in ("Urban", "Peri_Urban")})

    # ── Monte Carlo ─────────────────────────────────────────────────────────
    U = rng.random((N_MC, len(names)))
    X = np.column_stack([mg.ppf(U[:, k]) for k, mg in enumerate(margs)])
    pace_u = rng.integers(0, N_BOOT_PACE, size=N_MC)
    pace_p = rng.integers(0, N_BOOT_PACE, size=N_MC)
    draws, tier_keep = [], np.zeros(len(arr.km))
    for d in range(N_MC):
        p = dict(zip(names, X[d]))
        pace = {"Urban": float(paces["Urban"]["boot"][pace_u[d]]),
                "Peri_Urban": float(paces["Peri_Urban"]["boot"][pace_p[d]])}
        res, t = m.evaluate(p, pace)
        tier_keep += (t == m.base_tiers)
        draws.append({**p, "pace_urban": pace["Urban"], "pace_peri": pace["Peri_Urban"], **res})
        if (d + 1) % 1000 == 0:
            log.info("  MC %d/%d (%.0fs)", d + 1, N_MC, time.time() - t0)
    mc = pd.DataFrame(draws)
    mc.to_csv(C.DERIVED / "a09_mc_draws.csv", index=False)

    route_stab = tier_keep / N_MC
    rs = arr.df[["New_Route_ID", "Route_Name", "Route_Type"]].copy()
    rs["baseline_tier"] = m.base_tiers
    rs["tier_stability_rate"] = route_stab
    rs.to_csv(C.DERIVED / "a09_route_tier_stability.csv", index=False)

    mc_summary = {k: summarise(mc[k]) for k in
                  ("fleet_A", "fleet_B", "fleet_B_Urban", "fleet_B_Peri_Urban",
                   "fleet_B_Regional_District", "coverage", "tier_agreement")}
    tier_block = dict(
        p_agreement_above_target=float((mc["tier_agreement"] > TIER_TARGET).mean()),
        target=TIER_TARGET,
        share_routes_stability_above_target=float((route_stab > TIER_TARGET).mean()),
        n_routes_stability_below_target=int((route_stab <= TIER_TARGET).sum()),
        route_stability_median=float(np.median(route_stab)),
        least_stable=rs.sort_values("tier_stability_rate").head(10)
                       [["New_Route_ID", "Route_Name", "baseline_tier", "tier_stability_rate"]]
                       .to_dict(orient="records"),
    )

    # ── Sobol' ──────────────────────────────────────────────────────────────
    sob_names = names + ["PACE_URBAN", "PACE_PERI"]
    problem = dict(num_vars=len(sob_names), names=sob_names,
                   bounds=[[0.0, 1.0]] * len(sob_names))
    S = sobol_sample.sample(problem, N_SOBOL, calc_second_order=False, seed=C.RANDOM_SEED)
    log.info("Sobol' evaluations: %d", len(S))
    bu, bp = np.sort(paces["Urban"]["boot"]), np.sort(paces["Peri_Urban"]["boot"])

    def q(boot, u):  # empirical inverse CDF of the bootstrap distribution
        return float(boot[min(int(u * len(boot)), len(boot) - 1)])

    Y = {k: np.empty(len(S)) for k in ("fleet_A", "fleet_B", "coverage", "tier_agreement")}
    for r in range(len(S)):
        p = {n: float(margs[k].ppf(S[r, k])) for k, n in enumerate(names)}
        pace = {"Urban": q(bu, S[r, -2]), "Peri_Urban": q(bp, S[r, -1])}
        res, _ = m.evaluate(p, pace)
        for k in Y:
            Y[k][r] = res[k]
        if (r + 1) % 5000 == 0:
            log.info("  Sobol' %d/%d (%.0fs)", r + 1, len(S), time.time() - t0)

    sobol_rows, sobol_out = [], {}
    for k, y in Y.items():
        if np.var(y) == 0:
            sobol_out[k] = dict(note="zero variance")
            continue
        Si = sobol_analyze.analyze(problem, y, calc_second_order=False,
                                   seed=C.RANDOM_SEED, print_to_console=False)
        sobol_out[k] = {n: dict(S1=float(Si["S1"][i]), S1_conf=float(Si["S1_conf"][i]),
                                ST=float(Si["ST"][i]), ST_conf=float(Si["ST_conf"][i]))
                        for i, n in enumerate(sob_names)}
        for i, n in enumerate(sob_names):
            sobol_rows.append(dict(output=k, parameter=n, S1=Si["S1"][i], S1_ci95=Si["S1_conf"][i],
                                   ST=Si["ST"][i], ST_ci95=Si["ST_conf"][i]))
    sob = pd.DataFrame(sobol_rows)

    # Tables.
    lab = {**{n: C.PARAMETERS[n]["label"] for n in names},
           "PACE_URBAN": "Observed urban pace (min/km)", "PACE_PERI": "Observed peri-urban pace (min/km)"}
    tab_s = (sob.assign(label=sob["parameter"].map(lab))
             .pivot_table(index="label", columns="output", values="ST").round(3))
    tab_s = tab_s[[c for c in ("fleet_A", "fleet_B", "tier_agreement", "coverage") if c in tab_s]]
    tab_s = tab_s.sort_values("fleet_B", ascending=False).reset_index()
    tab_s.columns = ["Parameter"] + [{"fleet_A": "Fleet A (as specified) ST",
                                       "fleet_B": "Fleet B (obs.-anchored) ST",
                                       "tier_agreement": "Tier agreement ST",
                                       "coverage": "Coverage ST"}[c] for c in tab_s.columns[1:]]
    C.write_table(tab_s, "table07c_sobol",
                  f"Total-order Sobol' indices (Saltelli, N = {N_SOBOL}, {len(S):,} evaluations)")

    def fmt(s, pct=False):
        f = (lambda v: f"{100*v:.1f}%") if pct else (lambda v: f"{v:,.0f}")
        return f"{f(s['median'])} [{f(s['p5'])}–{f(s['p95'])}]"

    tab_i = pd.DataFrame([
        dict(Output="Fleet, regime A (as specified, cap on)", Published=f"{int(arr.fleet_pub.sum()):,}",
             **{"Median [90% interval]": fmt(mc_summary["fleet_A"])}),
        dict(Output="Fleet, regime B (observation-anchored urban/peri pace)", Published="—",
             **{"Median [90% interval]": fmt(mc_summary["fleet_B"])}),
        dict(Output="  of which Urban", Published=f"{int(arr.fleet_pub[arr.rtype=='Urban'].sum()):,}",
             **{"Median [90% interval]": fmt(mc_summary["fleet_B_Urban"])}),
        dict(Output="  of which Peri-Urban", Published=f"{int(arr.fleet_pub[arr.rtype=='Peri_Urban'].sum()):,}",
             **{"Median [90% interval]": fmt(mc_summary["fleet_B_Peri_Urban"])}),
        dict(Output="  of which Regional (as modelled)",
             Published=f"{int(arr.fleet_pub[arr.rtype=='Regional_District'].sum()):,}",
             **{"Median [90% interval]": fmt(mc_summary["fleet_B_Regional_District"])}),
        dict(Output="Network coverage (share of 6,584,762)", Published=f"{100*m.grid.base_cov:.1f}%",
             **{"Median [90% interval]": fmt(mc_summary["coverage"], pct=True)}),
        dict(Output="Tier agreement with baseline", Published="100%",
             **{"Median [90% interval]": fmt(mc_summary["tier_agreement"], pct=True)}),
    ])
    C.write_table(tab_i, "table07b_mc_intervals",
                  f"Monte Carlo intervals ({N_MC:,} joint draws, seed {C.RANDOM_SEED})")

    out = dict(
        n_mc=N_MC, n_sobol_base=N_SOBOL, n_sobol_evals=int(len(S)), seed=C.RANDOM_SEED,
        parameters={n: dict(value=C.PARAMETERS[n]["value"], range=C.PARAMETERS[n]["range"],
                            dist=C.PARAMETERS[n]["dist"]) for n in names},
        pace_priors={k: {kk: vv for kk, vv in v.items() if kk != "boot"} for k, v in paces.items()},
        fleet_published=int(arr.fleet_pub.sum()),
        fleet_B_at_median_pace=base_B,
        mc=mc_summary, tier_stability=tier_block, sobol=sobol_out,
        headline=dict(
            fleet_A_90=[mc_summary["fleet_A"]["p5"], mc_summary["fleet_A"]["p95"]],
            fleet_B_90=[mc_summary["fleet_B"]["p5"], mc_summary["fleet_B"]["p95"]],
            fleet_B_median=mc_summary["fleet_B"]["median"],
            coverage_90=[mc_summary["coverage"]["p5"], mc_summary["coverage"]["p95"]],
            tier_agreement_median=mc_summary["tier_agreement"]["median"],
            p_tier_agreement_above_80=tier_block["p_agreement_above_target"],
        ),
        limitations=[
            "Parameters sampled independently; no correlation structure is measured.",
            "Regime B pace comes from 16 Srinagar-belt corridors; applying it to all "
            "Urban/Peri-Urban routes assumes those corridors are representative.",
            "Regional lifeline pace is unobserved (2 long corridors); regional fleet "
            "is as modelled, cap included, in both regimes.",
            "Headways held at published values; tier changes are not propagated to "
            "headway (tier and fleet are reported as separate decisions).",
            "Rural headways are demand-responsive in the engine (Eq. 8 proxy); that "
            "dependence is not sampled here.",
        ],
        runtime_sec=round(time.time() - t0, 1),
    )
    C.write_result(out, "a09_monte_carlo_sobol")
    log.info("fleet A %s", fmt(mc_summary["fleet_A"]))
    log.info("fleet B %s", fmt(mc_summary["fleet_B"]))
    log.info("coverage %s  tier agreement %s  P(>80%%)=%.3f", fmt(mc_summary["coverage"], True),
             fmt(mc_summary["tier_agreement"], True), tier_block["p_agreement_above_target"])


if __name__ == "__main__":
    main()
