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
      up in coverage for the buses it saves.
  S5  Urban frequent network. Every Urban non-backbone route at 15 minutes (from
      20/35): the "turn-up-and-go" core. Measures the fleet price of frequency.

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


def consolidate(arr: F.PlanArrays, theta: float) -> np.ndarray:
    """Keep-mask after contracting components of engine-rule pairs at theta."""
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
    for c in np.unique(lab):
        idx = np.where(lab == c)[0]
        keep[idx[np.argmax(cdi[idx])]] = True
    keep |= arr.sscl
    return keep


def evaluate(name, desc, arr, cov, fleet_vec, headway, keep=None) -> dict:
    keep = np.ones(len(arr.km), bool) if keep is None else keep
    n = np.where(keep, fleet_vec, 0)
    rec = dict(scenario=name, description=desc, routes=int(keep.sum()), fleet=int(n.sum()),
               coverage_any=cov.share(keep))
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
    keep = consolidate(arr, 0.50)
    sc.append(evaluate("S4", "Consolidation at theta = 0.50 (engine merge test)", arr, cov,
                       F.fleet(arr), h0, keep=keep))
    h5 = np.where((arr.rtype == "Urban") & ~arr.sscl, 15.0, h0)
    sc.append(evaluate("S5", "Urban frequent network (all Urban routes 15 min)", arr, cov,
                       F.fleet_from_cycle(arr, cyc, F.BASE["FLEET_SPARE_RATIO"], headway=h5), h5))
    tab = pd.DataFrame(sc)
    base = tab.iloc[0]
    tab["fleet_change_pct"] = 100 * (tab["fleet"] / base["fleet"] - 1)

    out_tab = pd.DataFrame({
        "Scenario": tab["scenario"], "Lever": tab["description"], "Routes": tab["routes"],
        "Fleet": tab["fleet"], "Δ fleet": tab["fleet_change_pct"].map(lambda v: f"{v:+.1f}%"),
        "Coverage (any)": tab["coverage_any"].map(lambda v: f"{100*v:.1f}%"),
        "Coverage ≤15 min": tab["coverage_le15"].map(lambda v: f"{100*v:.1f}%"),
        "Coverage ≤20 min": tab["coverage_le20"].map(lambda v: f"{100*v:.1f}%"),
        "Max rural wait (min)": tab["max_wait_rural_min"].map(lambda v: f"{v:.0f}"),
    })
    C.write_table(out_tab, "table08_scenarios",
                  "Policy scenarios: one lever changed at a time from the published plan (S0); coverage is "
                  "the deduplicated share of 6,584,762 residents within a 400 m network walk")

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

    C.write_result(dict(
        scenarios=tab.to_dict(orient="records"), frontier=fr.to_dict(orient="records"),
        central_paces_min_per_km=paces, rural_bound_pace_min_per_km=rural_pace,
        s4_merged_routes=arr.df.loc[~keep, ["New_Route_ID", "Route_Name", "Route_Type"]].to_dict(orient="records"),
        notes=["Each scenario changes one lever; coverage is deduplicated.",
               "S2 rural pace rests on 2 corridors and is a bound.",
               "S4 contracts connected components, which chains; it is an upper bound on "
               "what the stated rule would merge."],
    ), "a15_scenarios")
    for r in tab.itertuples():
        log.info("%s %-60s routes %3d fleet %5d (%+.1f%%) cov %.1f%% le15 %.1f%% le20 %.1f%%", r.scenario,
                 r.description[:60], r.routes, r.fleet, r.fleet_change_pct, 100 * r.coverage_any,
                 100 * r.coverage_le15, 100 * r.coverage_le20)
    log.info("frontier:\n%s", fr.to_string(index=False))


if __name__ == "__main__":
    main()
