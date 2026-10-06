#!/usr/bin/env python
"""
a15_scenarios.py — five policy scenarios against the published plan, and the
fleet-versus-frequent-coverage trade-off frontier (Table 8, §7.7).

Each scenario changes ONE policy lever relative to the published plan (S0), so
its effect is attributable. All are evaluated with the verified supply model
(fleet_model, which reproduces the plan exactly at S0) and with deduplicated
network coverage computed from the a02 network catchments (W = 400 m,
tau = 100 m), never by summing per-route walksheds.

  S0  Published plan (v3.4.5-geo).
  S1  Observed urban run time. Urban and Peri-Urban non-backbone cycle times set
      from the observed median one-way pace (v04 corridors within 20 km of the
      Srinagar hub; a09 regime B at its central value). Everything else as S0.
  S2  S1 + rural run-time bound. Regional lifelines' per-km cap raised to the
      mean pace of the only two long observed corridors. n = 2: a BOUND on what
      observed rural pace could do to the fleet, not an estimate.
  S3  Flat 35-minute rural headway. The RTO round-2 rule (v3.3.7) in place of the
      demand-responsive 35/40/45/50 buckets: every Regional non-backbone route
      at 35 min. Isolates the fleet cost of the 50-minute rural maximum wait.
  S4  Consolidation at theta = 0.50. The engine's own merge test (80 m line-
      buffer overlap >= theta AND starts within 2.5 km) applied to the 186
      survivors at the low end of the declared theta range; each connected
      component of qualifying pairs is contracted to its highest-CDI route
      (backbone routes never merged). Measures what the stated rule would give
      up in coverage for the buses it saves. INTERPRETATION: an UPPER BOUND on
      consolidation (F-04-17). Components are contracted transitively (chaining:
      A~B and B~C remove A, B and C to one route even if A and C do not overlap)
      and survivors are NOT re-sized for the pooled demand, so the routes cut and
      buses saved overstate what the stated pairwise rule would deliver.
      `consolidation_diagnostics` quantifies how many removals are chain-only.
  S5  Urban frequent network. Every Urban non-backbone route at 15 minutes (from
      20/35): the "turn-up-and-go" core. Measures the fleet price of frequency.

Scenario fleets (F-04-17): S0-S3 and S5 are RECOMPUTED from the verified fleet
model (cycle time -> fleet formula); none is a scaled number. S4 is not
recomputed: it is the published fleet of the surviving routes.

Funding sequence (F-02-09, F-10-16): budget = 30% of the fleet (303 buses); the
greedy prefix allocates fewer (299) because the next route does not fit; budget,
allocation, routes funded and coverage at the allocated figure are all emitted.
Ordering: greedy by marginal coverage per bus; order-dependent; not an optimum.

Frontier: Urban + Peri-Urban non-backbone headway h swept over 10–35 min, fleet
(as specified and observation-anchored) against the share of residents within
400 m of service every <= h minutes.

Outputs  data/derived/a15_scenarios.json, data/derived/a15_frontier.csv,
         paper/tables/table08_scenarios.{csv,md}
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import fleet_model as F  # noqa: E402

log = C.get_logger("a15")

FREQ_THRESHOLDS = (15, 20)
FRONTIER_H = (10, 12, 15, 20, 25, 30, 35)


class Coverage:
    def __init__(self, route_ids):
        import geopandas as gpd
        import rasterio
        from pyproj import Transformer
        g = gpd.read_file(C.CACHE / "catchments_network.gpkg").set_index("New_Route_ID")
        self.geoms = g.loc[list(route_ids)].geometry.values
        self.to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform
        with rasterio.open(C.WORLDPOP_TIF) as src:
            self.nodata = src.nodata
        self.cache = {}

    def share(self, mask: np.ndarray) -> float:
        import rasterstats
        from shapely import union_all
        from shapely.ops import transform
        key = np.packbits(mask.astype(np.uint8)).tobytes()
        if key not in self.cache:
            if not mask.any():
                self.cache[key] = 0.0
            else:
                u = transform(self.to_wgs, union_all(list(self.geoms[mask])))
                s = rasterstats.zonal_stats([u], str(C.WORLDPOP_TIF), stats=["sum"],
                                            nodata=self.nodata)[0]["sum"] or 0.0
                self.cache[key] = float(s) / C.STUDY_AREA_POPULATION
        return self.cache[key]


def central_paces() -> dict:
    """Observed median paces, from the same corridor grouping a09 samples."""
    from a09_monte_carlo_sobol import pace_priors
    j = pace_priors(np.random.default_rng(C.RANDOM_SEED))
    return {"Urban": j["Urban"]["median"], "Peri_Urban": j["Peri_Urban"]["median"]}, \
        float(np.mean(j["_regional_unobserved"]["paces"]))


def consolidation(arr: F.PlanArrays, theta: float):
    """Keep-mask after contracting components of engine-rule pairs at theta, with
    diagnostics on how much of the removal is transitive chaining."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from a08_sensitivity_oat import OD_TOL_M, merge_pairs
    i, j, phi, dstart = merge_pairs(arr)
    ok = (phi >= theta) & (dstart <= OD_TOL_M) & ~arr.sscl[i] & ~arr.sscl[j]
    n = len(arr.km)
    A = coo_matrix((np.ones(ok.sum()), (i[ok], j[ok])), shape=(n, n))
    _, lab = connected_components(A, directed=False)
    cdi = arr.df["Final_CDI"].to_numpy(float)
    keep = np.zeros(n, bool)
    survivor = np.full(n, -1)
    for c in np.unique(lab):
        idx = np.where(lab == c)[0]
        k = idx[np.argmax(cdi[idx])]
        keep[k] = True
        survivor[idx] = k
    keep |= arr.sscl
    direct = {(min(a, b), max(a, b)) for a, b in zip(i[ok].tolist(), j[ok].tolist())}
    removed = np.where(~keep)[0]
    indirect = [int(d) for d in removed if (min(d, survivor[d]), max(d, survivor[d])) not in direct]
    sizes = np.bincount(lab)
    diag = dict(
        theta=theta, n_qualifying_pairs=int(ok.sum()),
        n_components_with_2plus_routes=int((sizes > 1).sum()),
        largest_component_routes=int(sizes.max()),
        n_routes_removed=int(len(removed)),
        n_removed_with_no_direct_qualifying_pair_to_their_survivor=len(indirect),
        n_backbone_routes_never_merged=int(arr.sscl.sum()),
        fleet_removed_buses=int(arr.fleet_pub[removed].sum()),
        fleet_removed_without_direct_pair_buses=int(arr.fleet_pub[indirect].sum()) if indirect else 0)
    return keep, diag


def consolidate(arr: F.PlanArrays, theta: float) -> np.ndarray:
    """Keep-mask after contracting components of engine-rule pairs at theta."""
    return consolidation(arr, theta)[0]


FUNDED_SHARE = 0.30


def funding_sequence(arr: F.PlanArrays):
    """
    If only part of the fleet is funded, what is bought first? (§7.7, FLAG 7-D)

    Each route's network catchment is rasterised onto the WorldPop grid (cell
    centres, as rasterstats counts them). Routes are then bought greedily by
    NEW residents reached per bus — residents already inside a bought route's
    walkshed count once — until the published fleet is exhausted; the funded
    share is the prefix whose cumulative buses fit FUNDED_SHARE of 1,011.
    Greedy marginal-gain-per-cost is the standard approximation for this
    budgeted maximum-coverage problem; it is reported as a ranking, not an optimum.
    Per-route fleet is the published value (headways as planned).
    """
    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize

    g = gpd.read_file(C.CACHE / "catchments_network.gpkg").set_index("New_Route_ID")
    g = g.loc[arr.df["New_Route_ID"]].to_crs(C.WGS84)
    with rasterio.open(C.WORLDPOP_TIF) as src:
        pop = src.read(1).astype(float)
        if src.nodata is not None:
            pop[pop == src.nodata] = 0.0
        pop[~np.isfinite(pop)] = 0.0
        tr, shape = src.transform, pop.shape
    cells = []
    for geom in g.geometry.values:
        m = rasterize([(geom, 1)], out_shape=shape, transform=tr, fill=0, dtype="uint8")
        cells.append(np.flatnonzero(m))
    flat = pop.ravel()
    fleet = arr.fleet_pub.astype(float)
    covered = np.zeros(flat.size, bool)
    remaining = list(range(len(cells)))
    rows, cum_bus, cum_pop = [], 0, 0.0
    budget = int(round(FUNDED_SHARE * fleet.sum()))
    while remaining:
        gains = np.array([flat[cells[r]][~covered[cells[r]]].sum() for r in remaining])
        k = int(np.argmax(gains / fleet[remaining]))
        r = remaining.pop(k)
        covered[cells[r]] = True
        cum_bus += int(fleet[r]); cum_pop += float(gains[k])
        rows.append(dict(order=len(rows) + 1, New_Route_ID=arr.df["New_Route_ID"].iloc[r],
                         Route_Name=arr.df["Route_Name"].iloc[r], Route_Type=arr.rtype[r],
                         fleet=int(fleet[r]), marginal_pop=float(gains[k]),
                         marginal_pop_per_bus=float(gains[k] / fleet[r]),
                         cum_buses=cum_bus, cum_pop=cum_pop,
                         cum_coverage=cum_pop / C.STUDY_AREA_POPULATION,
                         within_budget=cum_bus <= budget))
    seq = pd.DataFrame(rows)
    full_pop = seq["cum_pop"].iloc[-1]
    fund = seq[seq["within_budget"]]
    funded_pop = float(fund["cum_pop"].iloc[-1]) if len(fund) else 0.0
    buses_used = int(fund["fleet"].sum())

    # Variant (not the primary result): the prefix stops at the first route that
    # does not fit, which can leave buses unspent. Continue down the same greedy
    # order and buy any later route whose fleet still fits the remainder.
    pos = {r: k for k, r in enumerate(arr.df["New_Route_ID"])}
    bought = [pos[r] for r in fund["New_Route_ID"]]
    extra, left = [], budget - buses_used
    for rid, fl in zip(seq["New_Route_ID"].iloc[len(fund):], seq["fleet"].iloc[len(fund):]):
        if fl <= left:
            extra.append(pos[rid]); left -= int(fl)
    cov_mask = np.zeros(flat.size, bool)
    for r in bought + extra:
        cov_mask[cells[r]] = True
    variant_pop = float(flat[cov_mask].sum())
    next_fleet = int(seq["fleet"].iloc[len(fund)]) if len(fund) < len(seq) else None

    summary = dict(
        funded_share=FUNDED_SHARE, budget_buses=budget, n_routes_funded=int(len(fund)),
        buses_used=buses_used, coverage_funded=funded_pop / C.STUDY_AREA_POPULATION,
        coverage_full=full_pop / C.STUDY_AREA_POPULATION,
        share_of_full_coverage=funded_pop / full_pop,
        class_mix_funded=fund["Route_Type"].value_counts().to_dict(),
        n_backbone_funded=int(fund["New_Route_ID"].str.startswith("SSCL").sum()),
        raster_vs_zonal_note="coverage_full is the raster count of the same union a11 reports as 24.19%; "
                             "small differences are cell-centre rounding.",
        # F-02-09 / F-10-16 / F-04-18: say what was budgeted, what was allocated, what it reached.
        buses_budgeted=budget,
        buses_allocated=buses_used,
        buses_unspent=int(budget - buses_used),
        routes_funded=int(len(fund)),
        coverage_reached_at_allocated_buses=funded_pop / C.STUDY_AREA_POPULATION,
        coverage_reached_note=(f"{buses_used} of the {budget}-bus budget are allocated; the next route in the "
                               f"greedy order needs {next_fleet} buses and does not fit, so the prefix stops "
                               f"with {budget - buses_used} unspent. The coverage figures are at {buses_used} buses."),
        share_of_full_coverage_note=("share_of_full_coverage is a share of the full plan's own reach "
                                     f"({100 * full_pop / C.STUDY_AREA_POPULATION:.1f}% of study-area residents), "
                                     "not a share of residents; coverage_funded is the share of residents."),
        ordering_method="greedy by marginal coverage per bus; order-dependent; not an optimum",
        ordering_method_detail=("at each step buy the route with the most NEW residents (cells not already in a "
                                "bought route's walkshed) per bus; residents counted once; later choices depend "
                                "on earlier ones; per-route fleet is the published value."),
        variant_fill_remaining_budget=dict(
            note="same greedy order, but continue past the first route that does not fit and buy any later "
                 "route whose fleet fits the remainder; reported only to show how much the unspent buses matter",
            n_extra_routes=len(extra), buses_allocated=int(buses_used + arr.fleet_pub[extra].sum()),
            coverage=variant_pop / C.STUDY_AREA_POPULATION,
            coverage_gain_pp=100 * (variant_pop - funded_pop) / C.STUDY_AREA_POPULATION),
    )
    log.info("funding sequence: budget %d buses, %d allocated to %d routes -> %.1f%% coverage = %.0f%% of "
             "the full plan's %.1f%% (variant filling the remainder: +%d routes, +%.2f pp)",
             budget, buses_used, summary["n_routes_funded"], 100 * summary["coverage_funded"],
             100 * summary["share_of_full_coverage"], 100 * summary["coverage_full"], len(extra),
             summary["variant_fill_remaining_budget"]["coverage_gain_pp"])
    return seq, summary


FLEET_METHOD = {
    "S0": "recomputed from the fleet model (cycle time -> fleet formula); equals the published fleet on 186 of 186 routes",
    "S1": "recomputed from the fleet model: urban and peri-urban cycle times re-derived at the observed pace, then the fleet formula",
    "S2": "recomputed from the fleet model: S1 plus the rural per-km cap raised, then the fleet formula",
    "S3": "recomputed from the fleet model: published cycle times, 35-min headway on rural non-backbone routes, fleet formula",
    "S4": "NOT recomputed: sum of the published fleet of the surviving routes; survivors keep their own fleet and "
          "headway (not re-sized for pooled demand)",
    "S5": "recomputed from the fleet model: 15-min headway on Urban non-backbone routes, published cycle times, fleet formula",
}
S4_INTERPRETATION = "upper bound on consolidation"
S4_WHY = [
    "components of qualifying pairs are contracted transitively: if A~B and B~C then A, B and C collapse to one "
    "route even when A and C do not overlap, so the stated pairwise rule would remove fewer routes",
    "survivors are not re-sized: each keeps its own fleet and headway, so a pooled corridor that would need "
    "more buses than either route alone is not charged for them",
    "the buses saved are the dropped routes' published fleet; no demand model re-allocates riders",
]


def evaluate(name, desc, arr, cov, fleet_vec, headway, keep=None) -> dict:
    keep = np.ones(len(arr.km), bool) if keep is None else keep
    n = np.where(keep, fleet_vec, 0)
    rec = dict(scenario=name, description=desc, routes=int(keep.sum()), fleet=int(n.sum()),
               coverage_any=cov.share(keep), fleet_method=FLEET_METHOD[name],
               interpretation=(S4_INTERPRETATION if name == "S4" else "scenario result"))
    for t in FREQ_THRESHOLDS:
        rec[f"coverage_le{t}"] = cov.share(keep & (headway <= t))
    rec["max_wait_rural_min"] = float(headway[keep & (arr.rtype == "Regional_District")].max())
    rec["buses_per_1000_covered"] = rec["fleet"] / (rec["coverage_any"] * C.STUDY_AREA_POPULATION) * 1000
    return rec


def main() -> None:
    arr = F.load_arrays()
    F.verify_baseline(arr)
    cov = Coverage(arr.df["New_Route_ID"])
    paces, rural_pace = central_paces()
    h0 = arr.headway.copy()
    reg_nonbb = (arr.rtype == "Regional_District") & ~arr.sscl

    sc = []
    sc.append(evaluate("S0", "Published plan (v3.4.5-geo)", arr, cov, F.fleet(arr), h0))
    sc.append(evaluate("S1", "Observed urban/peri-urban run time", arr, cov,
                       F.fleet(arr, pace_override=paces), h0))
    cap_scale = np.where(reg_nonbb, rural_pace / F.CAP_MIN_PER_KM["Regional_District"], 1.0)
    sc.append(evaluate("S2", f"S1 + rural cap at observed rural pace ({rural_pace:.2f} min/km, n=2; bound)",
                       arr, cov, F.fleet(arr, pace_override=paces, cap_scale=cap_scale), h0))
    h3 = np.where(reg_nonbb, 35.0, h0)
    cyc = F.cycle_time(arr)
    sc.append(evaluate("S3", "Flat 35-min rural headway (no 50-min buckets)", arr, cov,
                       F.fleet_from_cycle(arr, cyc, F.BASE["FLEET_SPARE_RATIO"], headway=h3), h3))
    keep, s4_diag = consolidation(arr, 0.50)
    sc.append(evaluate("S4", "Consolidation at theta = 0.50 (engine merge test)", arr, cov,
                       F.fleet(arr), h0, keep=keep))
    sc[-1]["interpretation_why"] = S4_WHY
    sc[-1]["consolidation_diagnostics"] = s4_diag
    h5 = np.where((arr.rtype == "Urban") & ~arr.sscl, 15.0, h0)
    sc.append(evaluate("S5", "Urban frequent network (all Urban routes 15 min)", arr, cov,
                       F.fleet_from_cycle(arr, cyc, F.BASE["FLEET_SPARE_RATIO"], headway=h5), h5))
    base_fleet = sc[0]["fleet"]
    for r in sc:
        r["fleet_change_pct"] = 100 * (r["fleet"] / base_fleet - 1)
    tab = pd.DataFrame(sc)

    out_tab = pd.DataFrame({
        "Scenario": tab["scenario"], "Lever": tab["description"], "Routes": tab["routes"],
        "Fleet": tab["fleet"], "Δ fleet": tab["fleet_change_pct"].map(lambda v: f"{v:+.1f}%"),
        "Coverage (any)": tab["coverage_any"].map(lambda v: f"{100*v:.1f}%"),
        "Coverage ≤15 min": tab["coverage_le15"].map(lambda v: f"{100*v:.1f}%"),
        "Coverage ≤20 min": tab["coverage_le20"].map(lambda v: f"{100*v:.1f}%"),
        "Max rural wait (min)": tab["max_wait_rural_min"].map(lambda v: f"{v:.0f}"),
        "Fleet basis": tab["fleet_method"].map(
            lambda s: "published fleet of survivors; not re-sized" if s.startswith("NOT") else "recomputed (fleet model)"),
        "Reading": tab["interpretation"],
    })
    C.write_table(out_tab, "table08_scenarios",
                  "Policy scenarios: one lever changed at a time from the published plan (S0); coverage is "
                  "the deduplicated share of 6,584,762 residents within a 400 m network walk. S4 is an UPPER "
                  "BOUND on consolidation: qualifying pairs are contracted transitively (chaining) and surviving "
                  "routes are not re-sized, so its fleet saving and route cut overstate what the stated rule "
                  "would deliver. S0-S3 and S5 fleets are recomputed from the fleet model; none is scaled.")

    # Frontier.
    fr = []
    cityish = np.isin(arr.rtype, ["Urban", "Peri_Urban"]) & ~arr.sscl & ~arr.measured
    for h in FRONTIER_H:
        hh = np.where(cityish, float(h), h0)
        fa = F.fleet_from_cycle(arr, F.cycle_time(arr), F.BASE["FLEET_SPARE_RATIO"], headway=hh)
        fb = F.fleet_from_cycle(arr, F.cycle_time(arr, pace_override=paces), F.BASE["FLEET_SPARE_RATIO"],
                                headway=hh)
        fr.append(dict(city_headway_min=h, fleet_as_specified=int(fa.sum()),
                       fleet_observation_anchored=int(fb.sum()),
                       coverage_le_h=cov.share(hh <= h), coverage_le15=cov.share(hh <= 15),
                       coverage_le20=cov.share(hh <= 20), coverage_any=cov.share(np.ones(len(hh), bool))))
    fr = pd.DataFrame(fr)
    fr.to_csv(C.DERIVED / "a15_frontier.csv", index=False)

    seq, seq_summary = funding_sequence(arr)
    seq.to_csv(C.DERIVED / "a15_funding_sequence.csv", index=False)
    top = seq[seq["within_budget"]]
    C.write_table(pd.DataFrame({
        "Order": top["order"], "Route": top["Route_Name"], "Class": top["Route_Type"],
        "Buses": top["fleet"], "New residents reached": top["marginal_pop"].round(0).astype(int),
        "Residents per bus": top["marginal_pop_per_bus"].round(0).astype(int),
        "Cumulative coverage": top["cum_coverage"].map(lambda v: f"{100*v:.1f}%"),
    }), "table08b_funding_sequence",
        f"Funding-constrained sequencing ({seq_summary['ordering_method']}): routes bought in order of new "
        f"residents reached per bus. Budget {seq_summary['buses_budgeted']} buses "
        f"({int(100*FUNDED_SHARE)}% of the fleet); {seq_summary['buses_allocated']} allocated to "
        f"{seq_summary['routes_funded']} routes; coverage {100*seq_summary['coverage_reached_at_allocated_buses']:.1f}% "
        f"of residents at {seq_summary['buses_allocated']} buses")

    C.write_result(dict(
        scenarios=sc, frontier=fr.to_dict(orient="records"),
        funding_sequence=seq_summary,
        central_paces_min_per_km=paces, rural_bound_pace_min_per_km=rural_pace,
        s4_merged_routes=arr.df.loc[~keep, ["New_Route_ID", "Route_Name", "Route_Type"]].to_dict(orient="records"),
        fleet_method_summary=("S0-S3 and S5 fleets are recomputed from the verified fleet model; none is obtained by "
                              "scaling. S4 is the sum of the published fleet of surviving routes (no re-sizing)."),
        frontier_fleet_method=("fleet_as_specified and fleet_observation_anchored are both recomputed from the "
                               "fleet model at each city headway (published cycles / observed-pace cycles)."),
        notes=["Each scenario changes one lever; coverage is deduplicated.",
               "S2 rural pace rests on 2 corridors and is a bound.",
               "S4 is an UPPER BOUND on consolidation (interpretation key): it contracts connected components, "
               "which chains, and the survivors are not re-sized; it is an upper bound on what the stated rule "
               "would merge.",
               f"Funding sequence: {seq_summary['ordering_method']}. The budget is "
               f"{seq_summary['buses_budgeted']} buses, {seq_summary['buses_allocated']} are allocated "
               f"({seq_summary['routes_funded']} routes); coverage is reported at "
               f"{seq_summary['buses_allocated']}."],
    ), "a15_scenarios")
    for r in tab.itertuples():
        log.info("%s %-60s routes %3d fleet %5d (%+.1f%%) cov %.1f%% le15 %.1f%% le20 %.1f%%", r.scenario,
                 r.description[:60], r.routes, r.fleet, r.fleet_change_pct, 100 * r.coverage_any,
                 100 * r.coverage_le15, 100 * r.coverage_le20)
    log.info("frontier:\n%s", fr.to_string(index=False))


if __name__ == "__main__":
    main()
