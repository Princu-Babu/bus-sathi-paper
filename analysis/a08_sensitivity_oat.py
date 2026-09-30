#!/usr/bin/env python
"""
a08_sensitivity_oat.py — one-at-a-time sensitivity of the plan's three decisions
to the eleven pre-declared parameters of §4.10 / Table 3.

The three decisions, and the parameters that can move each:

  Fleet (total buses)       CONGESTION_CITY_CORE, STOP_PENALTY_MIN,
                            STOP_SPACING_M, FLEET_SPARE_RATIO
  Tier  (service hierarchy) CDI_POP_WEIGHT, POI_TIER2_WEIGHT, POI_TIER3_WEIGHT,
                            TOURIST_POPULATION_MULTIPLIER, WALK_CATCHMENT_M,
                            VIRTUAL_STOP_SPACING_M
  Coverage (deduplicated    WALK_CATCHMENT_M, VIRTUAL_STOP_SPACING_M
  share of residents)
  Consolidation             OVERLAP_THRESHOLD

A parameter that cannot move a decision is reported as zero effect on it rather
than omitted, because "does not matter" is itself a result a reader needs.

Why the fleet is swept twice. v04 found the per-km cycle cap binding on 169 of
186 routes (F10). Where the cap binds, the run-time parameters cannot reach the
fleet at all: congestion and dwell are computed and then discarded. A sweep that
leaves the cap on therefore reports insensitivity that is an artefact of the
guard, not robustness of the model. Every fleet parameter is swept (a) as the
engine executes, cap on, and (b) with the cap removed, so the masking is shown
rather than hidden. Neither is "the" answer; the gap between them is the finding.

Tiers are compared with the baseline tier partition of the same model (all
parameters at baseline), as share of routes unchanged and Cohen's kappa. The
baseline tier model differs from a04 only by applying the tourist multiplier
mu = 1.30 to the opportunity channel of the 8 tourist routes (Eq. 5), which a03
omitted; agreement with a04 is reported.

Consolidation. The engine merges route i into cluster leader t when the 80 m
line-buffer overlap is >= theta AND their start points are within 2.5 km
(transit_kashmir_v3.py:2640, 2696). The overlap test alone is not the rule. The
sweep counts, among the 186 survivors, pairs of non-backbone routes that would
satisfy the engine's own merge test at each theta — i.e. how many further merges
the rule would license — and, separately, pairs satisfying the overlap test only
(the rule as §4.6 currently describes it).

Inputs
    data/derived/a08a_catchment_grid.csv   per-route pop at W/spacing grid + POI tiers
    data/derived/a08a_catchment_grid.json  union coverage at each grid point
Outputs
    data/derived/a08_sensitivity_oat.json
    data/derived/a08_oat_sweeps.csv
    paper/tables/table07a_oat_sensitivity.{csv,md}
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import fleet_model as F  # noqa: E402

log = C.get_logger("a08")

N_STEPS = 9          # sweep points per parameter across its declared range
FLEET_PARAMS = ("CONGESTION_CITY_CORE", "STOP_PENALTY_MIN", "STOP_SPACING_M",
                "FLEET_SPARE_RATIO")
TIER_PARAMS = ("CDI_POP_WEIGHT", "POI_TIER2_WEIGHT", "POI_TIER3_WEIGHT",
               "TOURIST_POPULATION_MULTIPLIER", "WALK_CATCHMENT_M",
               "VIRTUAL_STOP_SPACING_M")
LINE_BUFFER_M = 80.0
OD_TOL_M = 2500.0


# ── catchment interpolation (shared with a09) ────────────────────────────────
class CatchmentGrid:
    """Per-route population and network coverage as functions of W and spacing.

    Population at (W, S) is interpolated linearly in W on the S = 250 m grid and
    scaled multiplicatively by the S-ratio observed at W = 400 m:
        pop(W, S) = pop(W, 250) * pop(400, S) / pop(400, 250)
    The separability assumption is stated in the paper; spacing is only
    evaluated at W = 400, so an interaction between the two is not observable
    here. Linear interpolation in S uses the three points {150, 250, 400}.
    """

    def __init__(self, route_ids):
        g = pd.read_csv(C.DERIVED / "a08a_catchment_grid.csv").set_index("New_Route_ID")
        missing = [r for r in route_ids if r not in g.index]
        if missing:
            raise SystemExit(f"a08a catchment grid incomplete: {len(missing)} of {len(route_ids)} routes "
                             f"missing — run analysis/a08a_catchment_grid.py (resumable) first")
        g = g.loc[list(route_ids)]
        meta = C.read_result("a08a_catchment_grid")
        self.W = np.array(meta["w_grid_m"], float)
        self.S = np.array(sorted(meta["spacing_grid_m"]), float)
        self.popW = np.column_stack([g[f"pop_W{int(w)}_S250"] for w in self.W])
        self.popS = np.column_stack([g[f"pop_W400_S{int(s)}"] for s in self.S])
        u = meta["union_coverage"]
        self.covW = np.array([u[f"W{int(w)}_S250"]["share"] for w in self.W])
        self.covS = np.array([u[f"W400_S{int(s)}"]["share"] for s in self.S])
        self.poi = {t: g[f"poi_{t}"].to_numpy(float) for t in ("high", "medium", "seasonal")}
        self.base_cov = u["W400_S250"]["share"]
        self.base_pop = u["W400_S250"]["pop"]

    @staticmethod
    def _interp_cols(x, xs, M):
        """Row-wise linear interpolation at scalar x (clamped to the grid)."""
        x = float(np.clip(x, xs[0], xs[-1]))
        k = int(np.clip(np.searchsorted(xs, x, side="right") - 1, 0, len(xs) - 2))
        f = (x - xs[k]) / (xs[k + 1] - xs[k])
        return M[:, k] * (1.0 - f) + M[:, k + 1] * f

    def pop(self, W: float, S: float) -> np.ndarray:
        pw = self._interp_cols(W, self.W, self.popW)
        ps = self._interp_cols(S, self.S, self.popS)
        base = self.popS[:, list(self.S).index(250.0)]
        ratio = np.divide(ps, base, out=np.ones_like(ps), where=base > 0)
        return pw * ratio

    def coverage(self, W: float, S: float) -> float:
        return float(np.interp(W, self.W, self.covW)
                     * np.interp(S, self.S, self.covS) / self.base_cov)


def tier_inputs(arr: F.PlanArrays) -> np.ndarray:
    """Tourist-corridor flags: the routes Eq. 5's multiplier acts on."""
    return arr.df["Tourist_Corridor"].astype(bool).to_numpy()


def tiers_at(arr, grid, tourist, p: dict) -> np.ndarray:
    pop = grid.pop(p["WALK_CATCHMENT_M"], p["VIRTUAL_STOP_SPACING_M"])
    c = F.cdi(pop, grid.poi["high"], grid.poi["medium"], grid.poi["seasonal"],
              arr.km, tourist, p["CDI_POP_WEIGHT"], p["POI_TIER2_WEIGHT"],
              p["POI_TIER3_WEIGHT"], p["TOURIST_POPULATION_MULTIPLIER"])
    return F.jenks_tiers(c)


# ── consolidation rule ───────────────────────────────────────────────────────
def merge_pairs(arr: F.PlanArrays):
    """Pairwise 80 m line-buffer overlap coefficient and start-point distance."""
    import geopandas as gpd
    from shapely import STRtree
    from shapely.geometry import Point

    g = gpd.read_file(C.PLAN_GEOJSON).to_crs(C.UTM).set_index("New_Route_ID")
    g = g.loc[arr.df["New_Route_ID"]]
    lines = g.geometry.simplify(C_SIMPLIFY).values
    bufs = [ln.buffer(LINE_BUFFER_M, resolution=2) for ln in lines]
    area = np.array([b.area for b in bufs])
    starts = [Point(ln.geoms[0].coords[0]) if ln.geom_type == "MultiLineString"
              else Point(ln.coords[0]) for ln in lines]
    tree = STRtree(bufs)
    i, j = tree.query(bufs, predicate="intersects")
    keep = i < j
    i, j = i[keep], j[keep]
    phi = np.array([bufs[a].intersection(bufs[b]).area for a, b in zip(i, j)])
    phi = phi / np.minimum(area[i], area[j])
    dstart = np.array([starts[a].distance(starts[b]) for a, b in zip(i, j)])
    return i, j, phi, dstart


C_SIMPLIFY = 4.0     # engine simplifies at SIMPLIFY_TOL_M * 2 before buffering


def main() -> None:
    arr = F.load_arrays()
    base_check = F.verify_baseline(arr)
    log.info("baseline reproduced: %s", base_check)
    grid = CatchmentGrid(arr.df["New_Route_ID"])
    tourist = tier_inputs(arr)
    base = dict(F.BASE)

    base_tiers = tiers_at(arr, grid, tourist, base)
    a04 = (pd.read_csv(C.DERIVED / "a04_route_tiers.csv").set_index("New_Route_ID")
           .loc[arr.df["New_Route_ID"], "tier_class"].to_numpy())
    agree_a04 = float((base_tiers == a04).mean())
    log.info("baseline tiers vs a04 (mu applied here, not in a03): %.1f%% agree",
             100 * agree_a04)

    fleet_base = int(F.fleet(arr).sum())
    fleet_nocap_base = int(F.fleet(arr, cap_scale=np.inf).sum())
    cov_base = grid.coverage(base["WALK_CATCHMENT_M"], base["VIRTUAL_STOP_SPACING_M"])

    rows = []
    for name, spec in C.PARAMETERS.items():
        if name == "OVERLAP_THRESHOLD":        # swept separately below
            continue
        lo, hi = spec["range"]
        xs = np.unique(np.r_[np.linspace(lo, hi, N_STEPS), spec["value"]])
        for x in xs:
            p = {**base, name: float(x)}
            rec = dict(parameter=name, label=spec["label"], value=float(x),
                       is_baseline=bool(np.isclose(x, spec["value"])))
            if name in FLEET_PARAMS:
                rec["fleet_cap_on"] = int(F.fleet(arr, p).sum())
                rec["fleet_cap_off"] = int(F.fleet(arr, p, cap_scale=np.inf).sum())
                rec["n_at_cap"] = int(F.at_cap_mask(arr, **p).sum())
            if name in TIER_PARAMS:
                t = tiers_at(arr, grid, tourist, p)
                rec["tier_agreement"] = float((t == base_tiers).mean())
                rec["tier_kappa"] = float(F.cohen_kappa(t, base_tiers))
                rec["n_tier_changed"] = int((t != base_tiers).sum())
            if name in ("WALK_CATCHMENT_M", "VIRTUAL_STOP_SPACING_M"):
                rec["coverage_share"] = grid.coverage(p["WALK_CATCHMENT_M"],
                                                      p["VIRTUAL_STOP_SPACING_M"])
            rows.append(rec)
    sweeps = pd.DataFrame(rows)

    # Consolidation threshold.
    i, j, phi, dstart = merge_pairs(arr)
    nonbb = ~arr.sscl[i] & ~arr.sscl[j]
    theta_rows = []
    for th in np.unique(np.r_[np.linspace(*C.PARAMETERS["OVERLAP_THRESHOLD"]["range"], N_STEPS),
                              C.PARAMETERS["OVERLAP_THRESHOLD"]["value"]]):
        ov = (phi >= th) & nonbb
        rule = ov & (dstart <= OD_TOL_M)
        theta_rows.append(dict(parameter="OVERLAP_THRESHOLD",
                               label=C.PARAMETERS["OVERLAP_THRESHOLD"]["label"],
                               value=float(th),
                               is_baseline=bool(np.isclose(th, 0.65)),
                               pairs_overlap_only=int(ov.sum()),
                               pairs_engine_rule=int(rule.sum()),
                               routes_in_engine_rule_pairs=int(len(np.union1d(i[rule], j[rule])))))
    sweeps = pd.concat([sweeps, pd.DataFrame(theta_rows)], ignore_index=True)
    sweeps.to_csv(C.DERIVED / "a08_oat_sweeps.csv", index=False)

    # Summary: swing over the declared range for each parameter and decision.
    summ = []
    for name, spec in C.PARAMETERS.items():
        s = sweeps[sweeps["parameter"] == name]
        rec = dict(parameter=name, label=spec["label"], baseline=spec["value"],
                   range_lo=spec["range"][0], range_hi=spec["range"][1])
        if name in FLEET_PARAMS:
            rec["fleet_min_cap_on"] = int(s["fleet_cap_on"].min())
            rec["fleet_max_cap_on"] = int(s["fleet_cap_on"].max())
            rec["fleet_swing_cap_on"] = int(s["fleet_cap_on"].max() - s["fleet_cap_on"].min())
            rec["fleet_min_cap_off"] = int(s["fleet_cap_off"].min())
            rec["fleet_max_cap_off"] = int(s["fleet_cap_off"].max())
            rec["fleet_swing_cap_off"] = int(s["fleet_cap_off"].max() - s["fleet_cap_off"].min())
        if name in TIER_PARAMS:
            rec["tier_agreement_min"] = round(float(s["tier_agreement"].min()), 4)
            rec["tier_kappa_min"] = round(float(s["tier_kappa"].min()), 4)
        if "coverage_share" in s and s["coverage_share"].notna().any():
            rec["coverage_min"] = round(float(s["coverage_share"].min()), 4)
            rec["coverage_max"] = round(float(s["coverage_share"].max()), 4)
        if name == "OVERLAP_THRESHOLD":
            rec["engine_rule_pairs_at_lo"] = int(s["pairs_engine_rule"].max())
            rec["engine_rule_pairs_at_base"] = int(s.loc[s["is_baseline"], "pairs_engine_rule"].iloc[0])
            rec["engine_rule_pairs_at_hi"] = int(s["pairs_engine_rule"].min())
            rec["overlap_only_pairs_at_base"] = int(s.loc[s["is_baseline"], "pairs_overlap_only"].iloc[0])
        summ.append(rec)
    summ = pd.DataFrame(summ)

    tab = pd.DataFrame({
        "Parameter": summ["label"],
        "Baseline": summ["baseline"],
        "Range": summ.apply(lambda r: f"{r.range_lo:g}–{r.range_hi:g}", axis=1),
        "Fleet, cap on": summ.apply(lambda r: f"{r.fleet_min_cap_on:.0f}–{r.fleet_max_cap_on:.0f}"
                                    if pd.notna(r.get("fleet_min_cap_on")) else "—", axis=1),
        "Fleet, cap off": summ.apply(lambda r: f"{r.fleet_min_cap_off:.0f}–{r.fleet_max_cap_off:.0f}"
                                     if pd.notna(r.get("fleet_min_cap_off")) else "—", axis=1),
        "Tier agreement (min)": summ.apply(lambda r: f"{100*r.tier_agreement_min:.1f}%"
                                           if pd.notna(r.get("tier_agreement_min")) else "—", axis=1),
        "Coverage": summ.apply(lambda r: f"{100*r.coverage_min:.1f}–{100*r.coverage_max:.1f}%"
                               if pd.notna(r.get("coverage_min")) else "—", axis=1),
    })
    C.write_table(tab, "table07a_oat_sensitivity",
                  f"One-at-a-time sensitivity of fleet, tier and coverage to the eleven "
                  f"declared parameters (baseline fleet {fleet_base:,}; cap removed "
                  f"{fleet_nocap_base:,}; baseline network coverage {100*cov_base:.1f}%)")

    fleet_swings = summ.dropna(subset=["fleet_swing_cap_on"])
    out = dict(
        baseline_reproduction=base_check,
        fleet_baseline=fleet_base,
        fleet_baseline_cap_removed=fleet_nocap_base,
        n_at_cap_baseline=int(F.at_cap_mask(arr).sum()),
        coverage_baseline_share=cov_base,
        baseline_tiers_vs_a04_agreement=agree_a04,
        baseline_tier_sizes=[int((base_tiers == k).sum()) for k in range(3)],
        largest_fleet_swing_cap_on=fleet_swings.sort_values("fleet_swing_cap_on").iloc[-1][
            ["parameter", "fleet_swing_cap_on"]].to_dict(),
        largest_fleet_swing_cap_off=fleet_swings.sort_values("fleet_swing_cap_off").iloc[-1][
            ["parameter", "fleet_swing_cap_off"]].to_dict(),
        summary=summ.to_dict(orient="records"),
        consolidation=dict(line_buffer_m=LINE_BUFFER_M, od_tolerance_m=OD_TOL_M,
                           n_intersecting_pairs=int(len(phi)),
                           by_theta=theta_rows),
        notes=[
            "Fleet parameters swept with the per-km cycle cap as executed (cap on) "
            "and removed (cap off); the gap is the masking effect of finding F10.",
            "Tier agreement is against the same model at baseline, not against the "
            "published engine bands (a04 reports that comparison: 68.3%).",
            "Coverage interpolates the a08a grid; W and stop-spacing effects are "
            "assumed separable (spacing evaluated at W = 400 m only).",
            "Consolidation counts pairs among the 186 survivors; the engine merges "
            "only into a cluster leader, so a pair meeting the test is a merge the "
            "rule would license, not one it necessarily performs.",
        ],
    )
    C.write_result(out, "a08_sensitivity_oat")
    for r in summ.itertuples():
        log.info("%-32s %s", r.parameter, {k: v for k, v in r._asdict().items()
                                          if k not in ("Index", "parameter", "label")
                                          and pd.notna(v)})


if __name__ == "__main__":
    main()
