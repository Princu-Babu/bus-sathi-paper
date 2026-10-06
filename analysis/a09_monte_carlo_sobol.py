#!/usr/bin/env python
"""
a09_monte_carlo_sobol.py — joint uncertainty in the plan's decisions (validation
channels V5 and V6) and the fleet as an interval rather than a point.

What is sampled. Only parameters the model function actually reads. Ten of the
eleven declared parameters of §4.10 (common.PARAMETERS) are sampled, each from
its declared marginal: triangular with the engine value as mode, or uniform, over
the declared range. Draws are independent; no correlation between parameters is
asserted because none is measured. The eleventh, the corridor-merge threshold
theta (OVERLAP_THRESHOLD), is NOT sampled: this module's model takes the 186
published routes as given, so theta cannot reach any output (audit F-08-10; the
earlier version listed it and returned a Sobol' index of exactly zero). Route-set
uncertainty is therefore not propagated; the bounding scenario S4 of a15
(theta = 0.50 under the engine's own merge test) is reported beside the interval,
read from a15_scenarios.json, with no probability attached. A self-check
(`liveness_check`) perturbs every sampled input across its range and refuses to
run if any of them leaves all outputs unchanged.

Supply regimes, all reported, none privileged:

  A.     As specified. The engine's cycle model with its per-km cap.
  B-eff  Observation-anchored, EFFECTIVE pace. For Urban and Peri-Urban
         non-backbone, non-measured routes (84 of 186; the five measured
         corridors keep their plan cycle) the modelled one-way time and the cap
         are replaced by an observed one-way pace times route length, where pace
         = 60 / effective_kmh = in-motion time + observed dwell/standstill, and
         the 1.10 terminal-layover factor is applied on top. This is the original
         regime B of the paper (a bracket; it is not the engine's method).
  B-mov  Observation-anchored, the ENGINE'S OWN v3.4.5 method
         (apply_reality_v345.py): drive time = route length x MOVING pace
         (60 / moving_kmh, dwell excluded) replaces OSRM x congestion; the
         engine's modelled dwell (stops x stop penalty) and junction penalty are
         kept; cycle = one-way x 2 x 1.10; cap lifted.
  Pace is a network-level quantity drawn from the bootstrap distribution of the
  median pace of the corridor pool (v04 corridor profiles within 20 km of the
  Srinagar hub: 7 core/mid -> Urban, 9 periphery -> Peri-Urban). The two regimes
  use the same bootstrap resample of corridors in every Monte Carlo draw. The
  pool contains 5 corridors that are not plan routes (OUT_OF_AREA / INFORMAL
  verdicts) and the five that the engine measured directly; `evidence_split` and
  `prior_robustness` in the output give the counts and the shift when the pool is
  restricted. Regional lifelines are unobserved (two long corridors) and stay as
  modelled in every regime. The e-bus backbone and the five measured corridors
  stay as published.

Outputs per draw: total fleet under A, B-eff and B-mov, deduplicated coverage
share, and tier agreement with the baseline partition. Every band is labelled
with its percentiles: median, p5-p95 (a 90% interval of the sampled distribution:
not a confidence interval and not a bound), and min-max. Also the probability
that tier agreement exceeds the declared 80% target and each route's tier
stability.

Sobol' indices. Saltelli sampling (SALib), N = 1024 base samples, first-order
(S1) and total-order (ST) indices with bootstrap 95% confidence intervals
(100 resamples), for each output. S1 is the share of output variance explained by
the input alone; ST adds its interactions, so sum(ST) can exceed 1. A phrase
such as "share of variance" means S1; ST is called "total-order index". Estimates
outside [0, 1] are flagged and left as estimated, never clipped. Inputs are
sampled on the unit hypercube and mapped through each marginal's inverse CDF,
which leaves the indices unchanged. The two pace inputs are quantile coordinates:
each output maps a coordinate through its own regime's pace distribution, and no
output reads both regimes.

Seed: common.RANDOM_SEED.

Inputs
    data/derived/a08a_catchment_grid.{csv,json}, data/raw/gps/corridor_profiles.csv,
    data/derived/a15_scenarios.json (read only: bounding scenario S4)
Outputs
    data/derived/a09_monte_carlo_sobol.json
    data/derived/a09_mc_draws.csv
    data/derived/a09_route_tier_stability.csv
    data/derived/a09_sobol_indices.csv
    paper/tables/table07b_mc_intervals.{csv,md}
    paper/tables/table07c_sobol.{csv,md}        (S1 and ST per output)
    paper/tables/table07c_sobol_full.{csv,md}   (long: S1, ST, 95% CI, flags)
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
N_SOBOL_RESAMPLES = 100
URBAN_HUB_KM = 20.0            # corridors farther than this are not urban belt
TIER_TARGET = 0.80
INTERVAL_LABEL = "p5-p95 of the sampled draws (90% interval of the distribution; not a confidence interval, not a bound)"

# Parameters declared in common.PARAMETERS that this module's model cannot read.
ROUTE_SET_PARAMS = {
    "OVERLAP_THRESHOLD": "Corridor-merge threshold theta decides which permits become one of the 186 routes. "
                         "This model starts from the 186 published routes, so theta changes no output. "
                         "Route-set uncertainty is not propagated; see route_set_uncertainty.",
}
SAMPLED_PARAMS = [n for n in C.PARAMETERS if n not in ROUTE_SET_PARAMS]
PACE_DIMS = ["PACE_URBAN", "PACE_PERI"]          # quantile coordinates of the pace priors
OUTPUT_KEYS = ("fleet_A", "fleet_B", "fleet_B_moving", "coverage", "tier_agreement")
OUTPUT_LABEL = {"fleet_A": "Fleet A (as specified)",
                "fleet_B": "Fleet B (obs.-anchored)",
                "fleet_B_moving": "Fleet B-mov (engine method)",
                "tier_agreement": "Tier agreement", "coverage": "Coverage"}


# ── marginals ────────────────────────────────────────────────────────────────
def marginal(spec: dict):
    lo, hi = spec["range"]
    if spec["dist"] == "tri":
        c = (spec["value"] - lo) / (hi - lo)
        return stats.triang(c, loc=lo, scale=hi - lo)
    return stats.uniform(loc=lo, scale=hi - lo)


def pace_priors(rng) -> dict:
    """Bootstrap distribution of the median observed one-way EFFECTIVE pace by
    class. Kept unchanged: a15_scenarios imports it."""
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


def pace_priors_both(rng) -> dict:
    """
    Bootstrap distributions of the median one-way pace by class, for BOTH pace
    definitions, from the same corridor resamples (aligned arrays). The effective
    bootstrap consumes the random stream exactly as `pace_priors` does, so
    boot_eff reproduces its `boot` bit for bit from the same generator state.
    """
    prof = F.load_corridor_profiles()
    belt = prof[prof["dist_hub_km"] < URBAN_HUB_KM]
    groups = {"Urban": belt[belt["zone"].isin(["core", "mid"])],
              "Peri_Urban": belt[belt["zone"] == "periphery"]}
    out = {}
    for cls, d in groups.items():
        eff = d["pace_effective"].to_numpy()
        mov = d["pace_moving"].to_numpy()
        idx = rng.integers(0, len(d), size=(N_BOOT_PACE, len(d)))
        be, bm = np.median(eff[idx], axis=1), np.median(mov[idx], axis=1)
        rec = dict(n_corridors=int(len(d)), corridor_ids=[int(v) for v in d["corridor_id"]],
                   observed_effective=[round(float(v), 3) for v in np.sort(eff)],
                   observed_moving=[round(float(v), 3) for v in np.sort(mov)],
                   boot_eff=be, boot_mov=bm,
                   sorted_eff=np.sort(be), sorted_mov=np.sort(bm))
        for tag, x, b in (("effective", eff, be), ("moving", mov, bm)):
            p5, p50, p95 = np.percentile(b, [5, 50, 95])
            rec[f"median_{tag}"] = float(np.median(x))
            rec[f"boot_{tag}_p5"] = float(p5)
            rec[f"boot_{tag}_p50"] = float(p50)
            rec[f"boot_{tag}_p95"] = float(p95)
            rec[f"boot_{tag}_mean"] = float(b.mean())
        out[cls] = rec
    return out


def _quantile(sorted_boot: np.ndarray, u: float) -> float:
    """Empirical inverse CDF of a bootstrap distribution."""
    return float(sorted_boot[min(int(u * len(sorted_boot)), len(sorted_boot) - 1)])


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

    def evaluate(self, p: dict, pace_eff: dict | None, pace_mov: dict | None = None):
        """All outputs for one parameter vector. `p` may carry extra keys (they
        are ignored: that is exactly what liveness_check demonstrates for theta)."""
        t = self.tiers(p)
        fa = F.fleet(self.arr, p)
        out = dict(fleet_A=int(fa.sum()),
                   coverage=self.grid.coverage(p["WALK_CATCHMENT_M"], p["VIRTUAL_STOP_SPACING_M"]),
                   tier_agreement=float((t == self.base_tiers).mean()))
        if pace_eff is not None:
            fb = F.fleet(self.arr, p, pace_override=pace_eff)
            out["fleet_B"] = int(fb.sum())
            for cls in ("Urban", "Peri_Urban", "Regional_District"):
                out[f"fleet_B_{cls}"] = int(fb[self.arr.rtype == cls].sum())
        if pace_mov is not None:
            fm = F.fleet_ext(self.arr, p, moving_pace_override=pace_mov)
            out["fleet_B_moving"] = int(fm.sum())
            for cls in ("Urban", "Peri_Urban", "Regional_District"):
                out[f"fleet_B_moving_{cls}"] = int(fm[self.arr.rtype == cls].sum())
        return out, t


def summarise(x: np.ndarray) -> dict:
    x = np.asarray(x, float)
    p5, p95 = float(np.percentile(x, 5)), float(np.percentile(x, 95))
    return dict(median=float(np.median(x)), mean=float(x.mean()), p5=p5, p95=p95,
                min=float(x.min()), max=float(x.max()), n=int(len(x)),
                p5_p95=[p5, p95], min_max=[float(x.min()), float(x.max())],
                interval=INTERVAL_LABEL)


# ── self-check: every sampled input must move at least one output ────────────
def liveness_check(m: Model, margs: dict, priors: dict, seed: int = C.RANDOM_SEED, n_pts: int = 9,
                   n_contexts: int = 5) -> dict:
    """
    For each sampled input, sweep it over its declared range (parameters) or over
    the bootstrap pace distribution (pace coordinates) while the others sit at
    baseline, and again in `n_contexts` random contexts; record the largest
    change in each output. An input is live iff some output changes. Also shows
    that the excluded route-set parameters leave every output unchanged.
    """
    rng = np.random.default_rng([seed, 99])
    base_p = dict(F.BASE)
    pe0 = {c: priors[c]["median_effective"] for c in ("Urban", "Peri_Urban")}
    pm0 = {c: priors[c]["median_moving"] for c in ("Urban", "Peri_Urban")}
    ctxs = [(base_p, pe0, pm0)]
    for _ in range(n_contexts):
        u = rng.random(len(SAMPLED_PARAMS) + 2)
        p = dict(base_p)
        p.update({n: float(margs[n].ppf(u[k])) for k, n in enumerate(SAMPLED_PARAMS)})
        pe = dict(pe0); pm = dict(pm0)
        pe["Urban"] = _quantile(priors["Urban"]["sorted_eff"], u[-2])
        pm["Urban"] = _quantile(priors["Urban"]["sorted_mov"], u[-2])
        pe["Peri_Urban"] = _quantile(priors["Peri_Urban"]["sorted_eff"], u[-1])
        pm["Peri_Urban"] = _quantile(priors["Peri_Urban"]["sorted_mov"], u[-1])
        ctxs.append((p, pe, pm))

    def run(p, pe, pm):
        r, _ = m.evaluate(p, pe, pm)
        return {k: r[k] for k in OUTPUT_KEYS}

    def sweep(setter):
        mx = {k: 0.0 for k in OUTPUT_KEYS}
        for (p0, pe0_, pm0_) in ctxs:
            ref = run(p0, pe0_, pm0_)
            for u in np.linspace(0.02, 0.98, n_pts):
                p, pe, pm = dict(p0), dict(pe0_), dict(pm0_)
                setter(p, pe, pm, float(u))
                r = run(p, pe, pm)
                for k in OUTPUT_KEYS:
                    mx[k] = max(mx[k], abs(r[k] - ref[k]))
        return mx

    out = {}
    for n in SAMPLED_PARAMS:
        mx = sweep(lambda p, pe, pm, u, n=n: p.__setitem__(n, float(margs[n].ppf(u))))
        out[n] = dict(live=any(v > 0 for v in mx.values()),
                      outputs_changed=[k for k, v in mx.items() if v > 0], max_abs_change=mx)
    for dim, cls in (("PACE_URBAN", "Urban"), ("PACE_PERI", "Peri_Urban")):
        def setter(p, pe, pm, u, cls=cls):
            pe[cls] = _quantile(priors[cls]["sorted_eff"], u)
            pm[cls] = _quantile(priors[cls]["sorted_mov"], u)
        mx = sweep(setter)
        out[dim] = dict(live=any(v > 0 for v in mx.values()),
                        outputs_changed=[k for k, v in mx.items() if v > 0], max_abs_change=mx)
    excluded = {}
    for n in ROUTE_SET_PARAMS:
        lo, hi = C.PARAMETERS[n]["range"]
        mx = sweep(lambda p, pe, pm, u, n=n, lo=lo, hi=hi: p.__setitem__(n, lo + u * (hi - lo)))
        excluded[n] = dict(live=any(v > 0 for v in mx.values()), max_abs_change=mx,
                           reason=ROUTE_SET_PARAMS[n])
    dead = [n for n, v in out.items() if not v["live"]]
    if dead:
        raise RuntimeError(f"sampled inputs that change no output: {dead}; remove them from the "
                           f"sampled set (audit F-08-10)")
    return dict(sampled=out, excluded=excluded, n_sweep_points=n_pts, n_contexts=1 + n_contexts)


def route_set_block() -> dict:
    """Route-set uncertainty: not propagated; the bounding scenario read from a15."""
    blk = dict(status="not propagated",
               statement="Route-set (corridor-merge) uncertainty is not part of any interval in this module. "
                         "Scenario S4 of a15 is a one-sided bound, not a draw: it has no probability attached.",
               parameter_not_sampled="OVERLAP_THRESHOLD",
               parameter_range=list(C.PARAMETERS["OVERLAP_THRESHOLD"]["range"]),
               parameter_baseline=C.PARAMETERS["OVERLAP_THRESHOLD"]["value"])
    try:
        a15 = C.read_result("a15_scenarios")
        s = next(x for x in a15["scenarios"] if x["scenario"] == "S4")
        s0 = next(x for x in a15["scenarios"] if x["scenario"] == "S0")
        blk["bounding_scenario_S4"] = dict(
            source="data/derived/a15_scenarios.json", description=s["description"], routes=s["routes"],
            fleet=s["fleet"], fleet_change_pct_vs_published=s["fleet_change_pct"],
            coverage_any=s["coverage_any"], published_fleet=s0["fleet"],
            published_coverage_any=s0["coverage_any"], published_routes=s0["routes"])
    except (FileNotFoundError, StopIteration, KeyError) as e:
        blk["bounding_scenario_S4"] = dict(status="not_computable",
                                           why=f"a15_scenarios.json S4 unavailable ({type(e).__name__})")
    blk["structural_uncertainty_not_sampled"] = [
        "route set (merge threshold theta, 80 m buffer, 2.5 km origin test)",
        "hierarchy: Jenks k = 3 (k = 2 has GVF 0.786 against the 0.80 rule) and CDI form",
        "per-km cycle cap form and its class values (a08 sweeps the cap on/off; not sampled here)",
        "headway rule (headways are held at the published value per route)",
        "stop-count rule and pace aggregation across corridors (corridors equal-weighted)",
    ]
    return blk


# ── observation-anchored regimes: reconciliation and robustness ──────────────
def _pace_pair_for_pool(d: pd.DataFrame) -> dict | None:
    """Class medians (effective and moving) for a corridor pool; None if a class is empty."""
    ur = d[d["zone"].isin(["core", "mid"])]
    pe = d[d["zone"] == "periphery"]
    if len(ur) == 0 or len(pe) == 0:
        return None
    return dict(n=dict(Urban=int(len(ur)), Peri_Urban=int(len(pe))),
                eff={"Urban": float(np.median(ur["pace_effective"])),
                     "Peri_Urban": float(np.median(pe["pace_effective"]))},
                mov={"Urban": float(np.median(ur["pace_moving"])),
                     "Peri_Urban": float(np.median(pe["pace_moving"]))},
                _ur=ur, _pe=pe)


def prior_robustness(m: Model) -> dict:
    """
    Fleet at the pool's median pace (all other parameters at baseline), and the
    p5-p95 of the fleet when only the pace varies (bootstrap of the pool's
    corridors), for several corridor pools. Answers: how much does the observed
    -pace fleet move when non-plan or outlier corridors are dropped?
    """
    prof = F.load_corridor_profiles()
    belt = prof[prof["is_belt"]]
    pools = {
        "belt_16_all (published pool)": belt,
        "belt_11_plan_corridors_only (drop OUT_OF_AREA/INFORMAL)": belt[~belt["non_plan_verdict"]],
        "belt_15_excluding_corridor_17 (74% dwell, 3.3 km, 6 runs)": belt[belt["corridor_id"] != 17],
        "belt_10_plan_only_excluding_corridor_17": belt[(~belt["non_plan_verdict"]) & (belt["corridor_id"] != 17)],
        "belt_5_directly_measured_by_engine_only": belt[belt["v345_measured"]],
    }
    rng = np.random.default_rng([C.RANDOM_SEED, 7])
    out = {}
    for name, d in pools.items():
        pr = _pace_pair_for_pool(d)
        if pr is None:
            out[name] = dict(status="not_computable", why="a route class has no corridor in this pool")
            continue
        rec = dict(n_corridors_by_class=pr["n"],
                   median_pace_effective=pr["eff"], median_pace_moving=pr["mov"],
                   fleet_B_eff_at_median_pace=int(F.fleet(m.arr, pace_override=pr["eff"]).sum()),
                   fleet_B_moving_at_median_pace=int(F.fleet_ext(m.arr, moving_pace_override=pr["mov"]).sum()))
        if min(pr["n"].values()) >= 3:
            fe, fm = [], []
            ue, pe_ = pr["_ur"], pr["_pe"]
            for _ in range(2000):
                iu = rng.integers(0, len(ue), len(ue)); ip = rng.integers(0, len(pe_), len(pe_))
                pe = {"Urban": float(np.median(ue["pace_effective"].to_numpy()[iu])),
                      "Peri_Urban": float(np.median(pe_["pace_effective"].to_numpy()[ip]))}
                pm = {"Urban": float(np.median(ue["pace_moving"].to_numpy()[iu])),
                      "Peri_Urban": float(np.median(pe_["pace_moving"].to_numpy()[ip]))}
                fe.append(F.fleet(m.arr, pace_override=pe).sum())
                fm.append(F.fleet_ext(m.arr, moving_pace_override=pm).sum())
            rec["pace_only_bootstrap_n"] = 2000
            rec["fleet_B_eff_pace_only_p5_p95"] = [float(np.percentile(fe, 5)), float(np.percentile(fe, 95))]
            rec["fleet_B_moving_pace_only_p5_p95"] = [float(np.percentile(fm, 5)), float(np.percentile(fm, 95))]
        else:
            rec["pace_only_bootstrap"] = "not_computed: fewer than 3 corridors in a class"
        out[name] = rec
    return out


def reconciliation_block(mc: pd.DataFrame, summ: dict, base_B: int, base_Bm: int, m: Model,
                         priors: dict, pace_u: np.ndarray, pace_p: np.ndarray) -> dict:
    """Why 1,182 (MC median) differs from 1,169 (fleet at median pace) and from the component medians."""
    pe_only, pm_only = [], []
    for d in range(len(mc)):
        pe = {"Urban": float(priors["Urban"]["boot_eff"][pace_u[d]]),
              "Peri_Urban": float(priors["Peri_Urban"]["boot_eff"][pace_p[d]])}
        pm = {"Urban": float(priors["Urban"]["boot_mov"][pace_u[d]]),
              "Peri_Urban": float(priors["Peri_Urban"]["boot_mov"][pace_p[d]])}
        pe_only.append(int(F.fleet(m.arr, pace_override=pe).sum()))
        pm_only.append(int(F.fleet_ext(m.arr, moving_pace_override=pm).sum()))
    pe_only, pm_only = np.array(pe_only), np.array(pm_only)

    def one(tag, key, base, pace_only, comp_prefix):
        comps = {c: summ[f"{comp_prefix}_{c}"]["median"] for c in ("Urban", "Peri_Urban", "Regional_District")}
        return dict(
            mc_median_of_total=summ[key]["median"], mc_mean_of_total=summ[key]["mean"],
            fleet_at_median_pace_other_params_at_baseline=base,
            median_minus_fleet_at_median_pace=summ[key]["median"] - base,
            share_of_draws_above_fleet_at_median_pace=float((mc[key] > base).mean()),
            pace_only_draws_median=float(np.median(pace_only)),
            pace_only_draws_p5_p95=[float(np.percentile(pace_only, 5)), float(np.percentile(pace_only, 95))],
            pace_bootstrap_mean_minus_observed_median_min_per_km={
                c: priors[c][f"boot_{tag}_mean"] - priors[c][f"median_{tag}"] for c in ("Urban", "Peri_Urban")},
            component_medians=comps, component_medians_sum=float(sum(comps.values())),
            median_of_total=summ[key]["median"],
            component_medians_sum_minus_median_of_total=float(sum(comps.values()) - summ[key]["median"]),
            note=("The Monte Carlo median is the median of the total over draws in which the pace AND the "
                  "other parameters vary; the 'at median pace' figure fixes every input at its central value. "
                  "They differ because the fleet is a step function of ceil() cycle counts and because the "
                  "bootstrap distribution of the median pace is not symmetric about the observed median "
                  "(see pace_bootstrap_mean_minus_observed_median_min_per_km). Component medians do not add "
                  "to the median of the total because a median is not additive."))

    return dict(B_effective=one("effective", "fleet_B", base_B, pe_only, "fleet_B"),
                B_moving=one("moving", "fleet_B_moving", base_Bm, pm_only, "fleet_B_moving"))


# ── Sobol' bookkeeping ───────────────────────────────────────────────────────
def sobol_flags(sobol_out: dict) -> list[dict]:
    """Estimates outside [0, 1], or first-order above total-order beyond sampling error. Never clipped."""
    flags = []
    for out, rows in sobol_out.items():
        if "note" in rows:
            continue
        for n, v in rows.items():
            for idx, ci in (("S1", "S1_conf"), ("ST", "ST_conf")):
                x, c = v[idx], v[ci]
                if x < 0 or x > 1:
                    bound = 0.0 if x < 0 else 1.0
                    flags.append(dict(output=out, parameter=n, index=idx, estimate=x, ci95_half_width=c,
                                      kind="negative" if x < 0 else "above_1",
                                      consistent_with_bound_within_ci=bool(abs(x - bound) <= c)))
            if v["S1"] - v["ST"] > v["S1_conf"] + v["ST_conf"]:
                flags.append(dict(output=out, parameter=n, index="S1>ST", estimate=v["S1"] - v["ST"],
                                  ci95_half_width=v["S1_conf"] + v["ST_conf"], kind="first_order_exceeds_total",
                                  consistent_with_bound_within_ci=False))
    return flags


def main() -> None:
    import argparse
    global N_MC, N_SOBOL
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-mc", type=int, default=N_MC)
    ap.add_argument("--n-sobol", type=int, default=N_SOBOL)
    ap.add_argument("--out-suffix", default="",
                    help="append to every output stem (test runs only; never use for published numbers)")
    ap.add_argument("--no-tables", action="store_true", help="skip writing paper tables (test runs)")
    a = ap.parse_args()
    N_MC, N_SOBOL = a.n_mc, a.n_sobol
    sfx = a.out_suffix
    from SALib.analyze import sobol as sobol_analyze
    from SALib.sample import sobol as sobol_sample

    t0 = time.time()
    rng = np.random.default_rng(C.RANDOM_SEED)
    names = list(SAMPLED_PARAMS)
    margs = {n: marginal(C.PARAMETERS[n]) for n in names}
    priors = pace_priors_both(rng)
    m = Model()
    arr = m.arr
    decomposed = F.verify_baseline_decomposed(arr)
    evidence = F.evidence_split(arr)
    pe_med = {c: priors[c]["median_effective"] for c in ("Urban", "Peri_Urban")}
    pm_med = {c: priors[c]["median_moving"] for c in ("Urban", "Peri_Urban")}
    base_B = int(F.fleet(arr, pace_override=pe_med).sum())
    base_Bm = int(F.fleet_ext(arr, moving_pace_override=pm_med).sum())
    log.info("baseline fleet A %d; B-eff at median pace %d; B-mov at median pace %d", int(arr.fleet_pub.sum()),
             base_B, base_Bm)

    live = liveness_check(m, margs, priors)
    log.info("liveness: all %d sampled inputs change at least one output; excluded %s inert=%s",
             len(live["sampled"]), list(live["excluded"]),
             {k: not v["live"] for k, v in live["excluded"].items()})

    # ── Monte Carlo ─────────────────────────────────────────────────────────
    U = rng.random((N_MC, len(names)))
    X = np.column_stack([margs[n].ppf(U[:, k]) for k, n in enumerate(names)])
    pace_u = rng.integers(0, N_BOOT_PACE, size=N_MC)
    pace_p = rng.integers(0, N_BOOT_PACE, size=N_MC)
    draws, tier_keep = [], np.zeros(len(arr.km))
    for d in range(N_MC):
        p = dict(zip(names, X[d]))
        pe = {"Urban": float(priors["Urban"]["boot_eff"][pace_u[d]]),
              "Peri_Urban": float(priors["Peri_Urban"]["boot_eff"][pace_p[d]])}
        pm = {"Urban": float(priors["Urban"]["boot_mov"][pace_u[d]]),
              "Peri_Urban": float(priors["Peri_Urban"]["boot_mov"][pace_p[d]])}
        res, t = m.evaluate(p, pe, pm)
        tier_keep += (t == m.base_tiers)
        draws.append({**p, "pace_urban": pe["Urban"], "pace_peri": pe["Peri_Urban"],
                      "pace_urban_moving": pm["Urban"], "pace_peri_moving": pm["Peri_Urban"], **res})
        if (d + 1) % 1000 == 0:
            log.info("  MC %d/%d", d + 1, N_MC)
    mc = pd.DataFrame(draws)
    mc.to_csv(C.DERIVED / f"a09_mc_draws{sfx}.csv", index=False)

    route_stab = tier_keep / N_MC
    rs = arr.df[["New_Route_ID", "Route_Name", "Route_Type"]].copy()
    rs["baseline_tier"] = m.base_tiers
    rs["tier_stability_rate"] = route_stab
    rs.to_csv(C.DERIVED / f"a09_route_tier_stability{sfx}.csv", index=False)

    mc_keys = ("fleet_A", "fleet_B", "fleet_B_Urban", "fleet_B_Peri_Urban", "fleet_B_Regional_District",
               "fleet_B_moving", "fleet_B_moving_Urban", "fleet_B_moving_Peri_Urban",
               "fleet_B_moving_Regional_District", "coverage", "tier_agreement")
    mc_summary = {k: summarise(mc[k]) for k in mc_keys}
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
    recon = reconciliation_block(mc, mc_summary, base_B, base_Bm, m, priors, pace_u, pace_p)
    robust = prior_robustness(m)

    # ── Sobol' ──────────────────────────────────────────────────────────────
    sob_names = names + PACE_DIMS
    problem = dict(num_vars=len(sob_names), names=sob_names, bounds=[[0.0, 1.0]] * len(sob_names))
    S = sobol_sample.sample(problem, N_SOBOL, calc_second_order=False, seed=C.RANDOM_SEED)
    log.info("Sobol' inputs %d, evaluations: %d", len(sob_names), len(S))

    Y = {k: np.empty(len(S)) for k in OUTPUT_KEYS}
    for r in range(len(S)):
        p = {n: float(margs[n].ppf(S[r, k])) for k, n in enumerate(names)}
        uu, up = S[r, -2], S[r, -1]
        pe = {"Urban": _quantile(priors["Urban"]["sorted_eff"], uu),
              "Peri_Urban": _quantile(priors["Peri_Urban"]["sorted_eff"], up)}
        pm = {"Urban": _quantile(priors["Urban"]["sorted_mov"], uu),
              "Peri_Urban": _quantile(priors["Peri_Urban"]["sorted_mov"], up)}
        res, _ = m.evaluate(p, pe, pm)
        for k in Y:
            Y[k][r] = res[k]
        if (r + 1) % 5000 == 0:
            log.info("  Sobol' %d/%d", r + 1, len(S))

    sobol_rows, sobol_out, sobol_sums = [], {}, {}
    for k, y in Y.items():
        if np.var(y) == 0:
            sobol_out[k] = dict(note="zero variance")
            continue
        Si = sobol_analyze.analyze(problem, y, calc_second_order=False, num_resamples=N_SOBOL_RESAMPLES,
                                   conf_level=0.95, seed=C.RANDOM_SEED, print_to_console=False)
        sobol_out[k] = {n: dict(S1=float(Si["S1"][i]), S1_conf=float(Si["S1_conf"][i]),
                                ST=float(Si["ST"][i]), ST_conf=float(Si["ST_conf"][i]))
                        for i, n in enumerate(sob_names)}
        sobol_sums[k] = dict(sum_S1=float(np.sum(Si["S1"])), sum_ST=float(np.sum(Si["ST"])),
                             interaction_share_estimate=float(1.0 - np.sum(Si["S1"])),
                             output_variance=float(np.var(y)), n_evaluations=int(len(y)))
        for i, n in enumerate(sob_names):
            sobol_rows.append(dict(output=k, parameter=n, S1=Si["S1"][i], S1_ci95=Si["S1_conf"][i],
                                   S1_distinguishable_from_zero=bool(abs(Si["S1"][i]) > Si["S1_conf"][i]),
                                   ST=Si["ST"][i], ST_ci95=Si["ST_conf"][i],
                                   ST_distinguishable_from_zero=bool(abs(Si["ST"][i]) > Si["ST_conf"][i]),
                                   n_base=N_SOBOL, n_evals=int(len(y))))
    sob = pd.DataFrame(sobol_rows)
    flags = sobol_flags(sobol_out)
    sob["flag"] = [";".join(f["kind"] for f in flags if f["output"] == r.output and f["parameter"] == r.parameter)
                   for r in sob.itertuples()]
    sob.to_csv(C.DERIVED / f"a09_sobol_indices{sfx}.csv", index=False)

    # Tables.
    lab = {**{n: C.PARAMETERS[n]["label"] for n in names},
           "PACE_URBAN": "Observed urban pace (min/km)", "PACE_PERI": "Observed peri-urban pace (min/km)"}
    st_name = {"fleet_A": "Fleet A (as specified)", "fleet_B": "Fleet B (obs.-anchored)",
               "fleet_B_moving": "Fleet B-mov (engine method)", "tier_agreement": "Tier agreement",
               "coverage": "Coverage"}
    cols = [c for c in ("fleet_A", "fleet_B", "fleet_B_moving", "tier_agreement", "coverage") if c in sob["output"].values]
    tab_s = pd.DataFrame({"Parameter": [lab[n] for n in sob_names]}, index=sob_names)
    for c in cols:
        sub = sob[sob["output"] == c].set_index("parameter")
        tab_s[f"{st_name[c]} ST"] = sub["ST"].reindex(sob_names).round(3).to_numpy()
        tab_s[f"{st_name[c]} S1"] = sub["S1"].reindex(sob_names).round(3).to_numpy()
    tab_s = tab_s.sort_values("Fleet B (obs.-anchored) ST", ascending=False).reset_index(drop=True)
    long_t = sob.assign(Parameter=sob["parameter"].map(lab), Output=sob["output"].map(st_name))
    long_t = long_t[["Output", "Parameter", "S1", "S1_ci95", "ST", "ST_ci95", "S1_distinguishable_from_zero",
                     "ST_distinguishable_from_zero", "flag"]].round(4)

    def fmt(s, pct=False):
        f = (lambda v: f"{100*v:.1f}%") if pct else (lambda v: f"{v:,.0f}")
        return f"{f(s['median'])}", f"{f(s['p5'])}–{f(s['p95'])}", f"{f(s['min'])}–{f(s['max'])}"

    def row(label, key, published="—", pct=False):
        md, pp, mm = fmt(mc_summary[key], pct)
        return {"Output": label, "Published": published, "Median": md, "p5–p95": pp, "Min–max": mm,
                "Draws": f"{mc_summary[key]['n']:,}"}

    pub = lambda cls: f"{int(arr.fleet_pub[arr.rtype == cls].sum()):,}"  # noqa: E731
    tab_i = pd.DataFrame([
        row("Fleet, regime A (as specified, cap on)", "fleet_A", f"{int(arr.fleet_pub.sum()):,}"),
        row("Fleet, regime B-eff (observed effective pace + 1.10 layover; bracket)", "fleet_B"),
        row("  of which Urban", "fleet_B_Urban", pub("Urban")),
        row("  of which Peri-Urban", "fleet_B_Peri_Urban", pub("Peri_Urban")),
        row("  of which Regional (as modelled)", "fleet_B_Regional_District", pub("Regional_District")),
        row("Fleet, regime B-mov (observed moving pace + modelled dwell; the engine's v3.4.5 method)", "fleet_B_moving"),
        row("  of which Urban", "fleet_B_moving_Urban", pub("Urban")),
        row("  of which Peri-Urban", "fleet_B_moving_Peri_Urban", pub("Peri_Urban")),
        row("  of which Regional (as modelled)", "fleet_B_moving_Regional_District", pub("Regional_District")),
        row("Network coverage (share of 6,584,762)", "coverage", f"{100*m.grid.base_cov:.1f}%", pct=True),
        row("Tier agreement with baseline", "tier_agreement", "100%", pct=True),
    ])
    if not a.no_tables:
        C.write_table(tab_s, "table07c_sobol",
                      f"Sobol' indices, first-order (S1) and total-order (ST) (Saltelli, N = {N_SOBOL}, "
                      f"{len(S):,} evaluations, 95% bootstrap CIs in table07c_sobol_full; estimates not clipped)")
        C.write_table(long_t, "table07c_sobol_full",
                      f"Sobol' indices with 95% bootstrap confidence half-widths (N = {N_SOBOL}, {N_SOBOL_RESAMPLES} "
                      f"resamples); flag marks estimates outside [0, 1]")
        C.write_table(tab_i, "table07b_mc_intervals",
                      f"Monte Carlo ({N_MC:,} joint draws, seed {C.RANDOM_SEED}); p5–p95 = 5th–95th percentile of "
                      f"the draws (a 90% interval of the sampled distribution, not a confidence interval or bound); "
                      f"route-set uncertainty (theta) not propagated")

    rsu = route_set_block()
    out = dict(
        n_mc=N_MC, n_sobol_base=N_SOBOL, n_sobol_evals=int(len(S)), seed=C.RANDOM_SEED,
        parameters={n: dict(value=C.PARAMETERS[n]["value"], range=C.PARAMETERS[n]["range"],
                            dist=C.PARAMETERS[n]["dist"]) for n in names},
        parameters_not_sampled={n: dict(value=C.PARAMETERS[n]["value"], range=C.PARAMETERS[n]["range"],
                                        dist=C.PARAMETERS[n]["dist"], reason=ROUTE_SET_PARAMS[n])
                                for n in ROUTE_SET_PARAMS},
        route_set_uncertainty="not propagated",
        route_set_uncertainty_detail=rsu,
        liveness_check=live,
        regime_definitions=dict(
            A="engine cycle model with the per-km cap; headways, routes as published",
            B_effective="fleet_B*: Urban/Peri-Urban non-backbone non-measured routes take cycle = 60/effective_kmh "
                        "min/km x L x 2 x 1.10 (in-motion + observed dwell/standstill, plus layover factor); cap "
                        "removed. Bracket; NOT the engine's method.",
            B_moving="fleet_B_moving*: same routes take one-way = L x 60/moving_kmh + stops x stop penalty + junction "
                     "penalty, cycle = one-way x 2 x 1.10, cap lifted. This is apply_reality_v345.py's method.",
            note="Key `fleet_B` (and fleet_B_Urban/...) is B_effective, kept under its original name."),
        pace_priors={k: ({kk: vv for kk, vv in v.items()
                          if kk not in ("boot_eff", "boot_mov", "sorted_eff", "sorted_mov")}
                         if k in ("Urban", "Peri_Urban") else v) for k, v in
                     {**priors, "_regional_unobserved": pace_priors(np.random.default_rng(C.RANDOM_SEED))
                      ["_regional_unobserved"]}.items()},
        observed_pace_reconciliation=F.observed_pace_reconciliation(),
        evidence_split=evidence,
        prior_robustness=robust,
        fleet_published=int(arr.fleet_pub.sum()),
        fleet_B_at_median_pace=base_B,
        fleet_B_moving_at_median_pace=base_Bm,
        fleet_B_reconciliation=recon,
        baseline_reproduction_decomposed=decomposed,
        mc=mc_summary, tier_stability=tier_block,
        sobol=sobol_out,
        sobol_meta=dict(
            n_base_samples=N_SOBOL, n_evaluations=int(len(S)), n_inputs=len(sob_names), inputs=sob_names,
            bootstrap_resamples=N_SOBOL_RESAMPLES, confidence_level=0.95,
            second_order=False,
            definitions=dict(
                S1="first-order index: share of output variance explained by the input alone",
                ST="total-order index: share of output variance involving the input, interactions included",
                sum_ST_gt_1="sum(ST) > 1 means interactions; ST must not be quoted as a variance share"),
            headline_convention="'share of variance' / 'explains X%' => S1. Total-order values are called "
                                "'total-order index' and are quoted with their S1.",
            sums=sobol_sums, flags=flags,
            flags_note="Estimates outside [0, 1] are reported as estimated (not clipped); "
                       "consistent_with_bound_within_ci says whether the bound lies inside the 95% interval.",
            pace_inputs_note="PACE_URBAN / PACE_PERI are quantile coordinates; fleet_B reads them through the "
                             "effective-pace prior, fleet_B_moving through the moving-pace prior; no output "
                             "reads both."),
        interval_definition=INTERVAL_LABEL,
        headline=dict(
            fleet_A_90=[mc_summary["fleet_A"]["p5"], mc_summary["fleet_A"]["p95"]],
            fleet_B_90=[mc_summary["fleet_B"]["p5"], mc_summary["fleet_B"]["p95"]],
            fleet_B_median=mc_summary["fleet_B"]["median"],
            coverage_90=[mc_summary["coverage"]["p5"], mc_summary["coverage"]["p95"]],
            tier_agreement_median=mc_summary["tier_agreement"]["median"],
            p_tier_agreement_above_80=tier_block["p_agreement_above_target"],
            fleet_A_p5_p95=[mc_summary["fleet_A"]["p5"], mc_summary["fleet_A"]["p95"]],
            fleet_A_min_max=mc_summary["fleet_A"]["min_max"], fleet_A_median=mc_summary["fleet_A"]["median"],
            fleet_B_p5_p95=[mc_summary["fleet_B"]["p5"], mc_summary["fleet_B"]["p95"]],
            fleet_B_min_max=mc_summary["fleet_B"]["min_max"],
            fleet_B_moving_p5_p95=[mc_summary["fleet_B_moving"]["p5"], mc_summary["fleet_B_moving"]["p95"]],
            fleet_B_moving_min_max=mc_summary["fleet_B_moving"]["min_max"],
            fleet_B_moving_median=mc_summary["fleet_B_moving"]["median"],
            coverage_p5_p95=[mc_summary["coverage"]["p5"], mc_summary["coverage"]["p95"]],
            coverage_min_max=mc_summary["coverage"]["min_max"], coverage_median=mc_summary["coverage"]["median"],
            interval_note="*_90 and *_p5_p95 are the 5th-95th percentile of the draws; *_min_max are extremes. "
                          "Neither includes route-set (theta) uncertainty. fleet_B is the effective-pace "
                          "bracket; fleet_B_moving is the engine's own method.",
        ),
        limitations=[
            "Parameters sampled independently; no correlation structure is measured.",
            "Route-set uncertainty is NOT propagated: theta is not sampled (it is not read by this model). "
            "Scenario S4 of a15 is the bounding case, with no probability attached.",
            "Pace priors pool 16 Srinagar-belt corridors, of which 5 are not plan routes and 5 are the corridors "
            "the engine measured directly; applying the pool to the 84 other Urban/Peri-Urban routes assumes "
            "those corridors are representative. Corridors are equal-weighted whatever their run count.",
            "Regional lifeline pace is unobserved (2 long corridors); regional fleet "
            "is as modelled, cap included, in every regime.",
            "Headways held at published values; tier changes are not propagated to "
            "headway (tier and fleet are reported as separate decisions).",
            "Rural headways are demand-responsive in the engine (Eq. 8 proxy); that "
            "dependence is not sampled here.",
            "Cap form, Jenks k and the stop-count rule are structural choices that are not sampled.",
        ],
        runtime_note="wall-clock runtime is not stored (volatile); see logs/volatile/LATEST_RUN_volatile.json",
    )
    C.DERIVED.joinpath(f"a09_monte_carlo_sobol{sfx}.json")  # path only; written below
    if sfx:
        import json
        with (C.DERIVED / f"a09_monte_carlo_sobol{sfx}.json").open("w", encoding="utf-8") as fh:
            json.dump(C._jsonable(out), fh, indent=2, sort_keys=True)
    else:
        C.write_result(out, "a09_monte_carlo_sobol")
    for k in ("fleet_A", "fleet_B", "fleet_B_moving"):
        md, pp, mm = fmt(mc_summary[k])
        log.info("%s median %s  p5-p95 %s  min-max %s", k, md, pp, mm)
    md, pp, mm = fmt(mc_summary["coverage"], True)
    td, tp, tm = fmt(mc_summary["tier_agreement"], True)
    log.info("coverage %s [%s]  tier agreement %s [%s]  P(>80%%)=%.3f", md, pp, td, tp,
             tier_block["p_agreement_above_target"])


if __name__ == "__main__":
    main()
