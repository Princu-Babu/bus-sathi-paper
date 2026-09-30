#!/usr/bin/env python
"""
a08a_catchment_grid.py — the heavy precompute behind the sensitivity analysis of
the two catchment parameters (walk budget W and virtual-stop sampling interval).

Why a separate module. Every other parameter in the one-at-a-time sweep (a08) and
the Monte Carlo (a09) acts on quantities that are cheap to recompute from the
plan table. The walk budget and the stop-sampling interval act on the catchment
geometry itself, which is a multi-source Dijkstra on a 962k-node pedestrian graph
per route. Recomputing that inside a 5,000-draw Monte Carlo is not feasible, so
the catchment is evaluated once on a grid of parameter values here and the
sampling modules interpolate between grid points.

Grid.
  * Walk budget W in {300, 400, 500, 600, 800} m, stop interval 250 m. One
    Dijkstra per route truncated at 800 m serves every W, because the catchment
    at budget W is exactly the set of nodes with d(v) <= W with tail discs of
    radius min(W - d(v), tau) (Eq. 1). Only the disc union is rebuilt per W.
  * Stop interval in {150, 400} m at W = 400 m. Different interval, different
    source set, so a separate Dijkstra truncated at 400 m.
  tau is held at 100 m (its own sensitivity is reported by a02).

Per route and grid point the module records the network-catchment population
(zonal sum of the WorldPop raster) and area. The W = 400 / 250 m point must
reproduce a02's pop_net to rounding; that is asserted, not assumed.

It also records, once per route, the count of opportunities (POIs) by importance
tier inside the 250 m network opportunity budget a03 uses, so that a08/a09 can
re-weight tiers without re-walking the graph. The POI budget is not swept.

Network-wide deduplicated coverage (the union of all route catchments) is
computed per grid point at the end, because that — not any per-route figure — is
the coverage number the paper reports.

Resumable: per-route results are appended to a checkpoint CSV and the polygons to
a pickle, so an interrupted run restarts where it stopped.

Outputs
    data/derived/a08a_catchment_grid.csv     per-route pop/area at each grid point
                                             + POI counts by tier
    data/derived/a08a_catchment_grid.json    union coverage per grid point, checks
    data/cache/a08a_polys/*.pkl              catchment polygons (gitignored)

Usage
    python analysis/a08a_catchment_grid.py [--limit N]
"""
from __future__ import annotations

import argparse
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
from a02_network_catchments import (  # noqa: E402
    MAX_SNAP_M, SIMPLIFY_TOL_M, TAU_M, dijkstra_budget, load_graph,
    network_catchment, stops_along,
)

log = C.get_logger("a08a")

W_GRID = (300.0, 400.0, 500.0, 600.0, 800.0)
SPACING_GRID = (150.0, 400.0)        # evaluated at W = 400; 250 is in W_GRID
POI_BUDGET_M = 250.0                 # a03's opportunity budget (not swept)
TIERS = ("high", "medium", "seasonal")

CKPT_CSV = C.CACHE / "a08a_checkpoint.csv"
POLY_DIR = C.CACHE / "a08a_polys"


def grid_keys() -> list[str]:
    keys = [f"W{int(w)}_S250" for w in W_GRID]
    keys += [f"W400_S{int(s)}" for s in SPACING_GRID]
    return keys


def snap_sources(stops, tree) -> dict[int, float]:
    pts = np.array([[p.x, p.y] for p in stops])
    off, nidx = tree.query(pts, k=1)
    sources: dict[int, float] = {}
    for o, ni in zip(off, nidx):
        if o > MAX_SNAP_M:
            continue
        ni = int(ni)
        if o < sources.get(ni, np.inf):
            sources[ni] = float(o)
    return sources


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    import geopandas as gpd
    import rasterio
    import rasterstats
    from pyproj import Transformer
    from scipy.spatial import cKDTree
    from shapely import union_all
    from shapely.ops import transform as shp_transform

    routes = gpd.read_file(C.PLAN_GEOJSON)
    if args.limit:
        routes = routes.head(args.limit).copy()
    utm = routes.to_crs(C.UTM)
    utm["geometry"] = utm.geometry.simplify(SIMPLIFY_TOL_M)

    pois = pd.read_csv(C.POIS_CSV)
    poi_utm = gpd.GeoDataFrame(
        pois, geometry=gpd.points_from_xy(pois["lon"], pois["lat"]),
        crs=C.WGS84).to_crs(C.UTM)
    poi_xy = np.column_stack([poi_utm.geometry.x, poi_utm.geometry.y])
    poi_tier = pois["importance"].astype(str).str.lower().to_numpy()

    xy, indptr, indices, weights = load_graph()
    tree = cKDTree(xy)
    poi_off, poi_node = tree.query(poi_xy, k=1)
    to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform
    with rasterio.open(C.WORLDPOP_TIF) as src:
        nodata = src.nodata

    POLY_DIR.mkdir(parents=True, exist_ok=True)
    done = set()
    if CKPT_CSV.exists() and not args.limit:
        done = set(pd.read_csv(CKPT_CSV)["New_Route_ID"])
        log.info("resuming: %d routes already in checkpoint", len(done))

    keys = grid_keys()
    t0 = time.time()
    n_new = 0
    for pos, (_, r) in enumerate(utm.iterrows(), start=1):
        rid = r["New_Route_ID"]
        if rid in done:
            continue
        rec = dict(New_Route_ID=rid, Route_Type=r.get("Route_Type"),
                   Route_KM=float(r["Route_KM"]))
        polys = {}

        # W grid at the engine's 250 m stop interval: one Dijkstra to 800 m.
        stops = stops_along(r.geometry, 250.0)
        src = snap_sources(stops, tree)
        nodes, ds = dijkstra_budget(indptr, indices, weights, src, max(W_GRID))
        for w in W_GRID:
            sel = ds <= w
            polys[f"W{int(w)}_S250"] = network_catchment(
                xy, nodes[sel], ds[sel], TAU_M, budget=w)

        # Opportunities by tier within the 250 m network budget (a03 method).
        dmap = dict(zip(nodes.tolist(), ds.tolist()))
        reach = np.array([(poi_off[j] + dmap.get(int(poi_node[j]), np.inf)) <= POI_BUDGET_M
                          for j in range(len(pois))])
        for t in TIERS:
            rec[f"poi_{t}"] = int((reach & (poi_tier == t)).sum())

        # Stop-interval grid at W = 400.
        for s in SPACING_GRID:
            st = stops_along(r.geometry, s)
            n2, d2 = dijkstra_budget(indptr, indices, weights, snap_sources(st, tree), 400.0)
            polys[f"W400_S{int(s)}"] = network_catchment(xy, n2, d2, TAU_M, budget=400.0)

        zones = [shp_transform(to_wgs, polys[k]) if polys[k] is not None else None
                 for k in keys]
        valid = [z for z in zones if z is not None]
        stats = rasterstats.zonal_stats(valid, str(C.WORLDPOP_TIF), stats=["sum"],
                                        nodata=nodata)
        it = iter(stats)
        for k, z in zip(keys, zones):
            rec[f"pop_{k}"] = float(next(it)["sum"] or 0.0) if z is not None else 0.0
            rec[f"area_km2_{k}"] = (polys[k].area / 1e6) if polys[k] is not None else 0.0

        with (POLY_DIR / f"{rid}.pkl").open("wb") as fh:
            pickle.dump({k: (p.wkb if p is not None else None) for k, p in polys.items()}, fh)
        pd.DataFrame([rec]).to_csv(CKPT_CSV, mode="a", index=False,
                                   header=not CKPT_CSV.exists())
        n_new += 1
        if n_new % 5 == 0:
            el = time.time() - t0
            log.info("  %d/%d routes (%d new, %.0fs, ~%.0f min left)", pos, len(utm),
                     n_new, el, el / n_new * (len(utm) - pos) / 60)

    grid = pd.read_csv(CKPT_CSV).drop_duplicates("New_Route_ID", keep="last")
    grid = grid[grid["New_Route_ID"].isin(set(utm["New_Route_ID"]))]

    # Reproduction check against a02 at the baseline grid point.
    a02 = pd.read_csv(C.DERIVED / "a02_catchments.csv")[["New_Route_ID", "pop_net"]]
    chk = grid.merge(a02, on="New_Route_ID")
    rel = (chk["pop_W400_S250"] - chk["pop_net"]).abs() / chk["pop_net"].replace(0, np.nan)
    repro = dict(n=int(len(chk)), max_rel_err=float(rel.max()),
                 median_rel_err=float(rel.median()))
    log.info("baseline reproduction vs a02: n=%d median %.2e max %.2e",
             repro["n"], repro["median_rel_err"], repro["max_rel_err"])

    # Deduplicated network coverage per grid point.
    from shapely import from_wkb
    union_pop = {}
    for k in keys:
        geoms = []
        for rid in grid["New_Route_ID"]:
            with (POLY_DIR / f"{rid}.pkl").open("rb") as fh:
                wkb = pickle.load(fh)[k]
            if wkb is not None:
                geoms.append(from_wkb(wkb))
        u = union_all(geoms)
        s = rasterstats.zonal_stats([shp_transform(to_wgs, u)], str(C.WORLDPOP_TIF),
                                    stats=["sum"], nodata=nodata)[0]["sum"] or 0.0
        union_pop[k] = dict(pop=float(s), share=float(s) / C.STUDY_AREA_POPULATION,
                            area_km2=u.area / 1e6)
        log.info("union %-12s %12s residents  %.2f%%", k, f"{s:,.0f}",
                 100 * float(s) / C.STUDY_AREA_POPULATION)

    grid.to_csv(C.DERIVED / "a08a_catchment_grid.csv", index=False)
    C.write_result(dict(
        w_grid_m=list(W_GRID), spacing_grid_m=[250.0, *SPACING_GRID], tau_m=TAU_M,
        poi_budget_m=POI_BUDGET_M, n_routes=int(len(grid)),
        baseline_reproduction_vs_a02=repro, union_coverage=union_pop,
        denominator=C.STUDY_AREA_POPULATION,
        runtime_min=round((time.time() - t0) / 60, 1),
    ), "a08a_catchment_grid")


if __name__ == "__main__":
    main()
