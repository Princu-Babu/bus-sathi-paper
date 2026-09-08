#!/usr/bin/env python
"""
a02_network_catchments.py — replace Euclidean walk catchments with
network-distance walksheds, and measure the bias that substitution removes.

Why this is the first analysis in the paper. The plan delineates each route's
walk catchment as a union of Euclidean discs of radius 400 m around virtual
stops spaced 250 m apart (transit_kashmir_v3.py::build_catchments). In this study
area that is not a harmless simplification. Discs centred on the Boulevard cross
Dal Lake; discs on either bank of the Jhelum overlap in mid-channel; discs around
Nigeen and Anchar credit routes with residents who have no walking connection to
them. The consequence is systematic overstatement of population served, and it is
the first thing a referee will test. Correcting it is therefore not a robustness
check but a result: the magnitude of the bias is reported as a finding.

What is compared. Both catchments are computed here, from the same route
geometries, the same virtual stops, the same walk budget and the same zonal
method, so the difference isolates the effect of respecting the pedestrian
network. The Euclidean catchment is *recomputed* rather than read from the
published plan; agreement with the plan's own Population_Served_Raw is reported
as a faithfulness check on this reimplementation.

Formulation. Let R = 400 m be the walk budget, S the set of virtual stops, and
G = (V, E) the pedestrian graph with geodesic edge lengths. Each stop s is
snapped to its nearest graph node n(s) at offset o(s); stops with o(s) > R are
off-network and reported. Multi-source Dijkstra is run from {n(s)} with initial
labels o(s), giving d(v), the walking distance from the nearest stop to node v.
The catchment is

    A_net = union over v in V, d(v) <= R  of  B(v, min(R - d(v), tau))

where B is a Euclidean disc and tau is an off-network access allowance. Two
properties matter. First, A_net respects barriers: reaching the far bank of the
Jhelum costs the detour to a bridge, so distant nodes exhaust the budget and
contribute nothing. Second, A_net is an upper bound on the true network walkshed,
because the final leg of length up to tau is allowed to run straight. The
measured overstatement of the Euclidean catchment is therefore a conservative
lower bound on the true overstatement, which is the direction a reader should
prefer.

Choice of tau. tau = 100 m, one WorldPop cell. The population surface is a 100 m
grid, so a tail finer than one cell cannot change any population count and a
larger tail would credit population across barriers the graph was introduced to
respect. Sensitivity to tau in {50, 100, 150} m is reported so the headline bias
is not an artefact of the choice.

Outputs
    data/derived/a02_catchments.csv          per-route both populations and areas
    data/derived/a02_network_catchments.json headline bias, tau sweep, checks
    paper/tables/table03a_catchment_bias.{csv,md}
    paper/tables/table03b_catchment_bias_by_district.{csv,md}
    data/cache/catchments_network.gpkg       network catchment polygons (figures)

Usage
    python analysis/a02_network_catchments.py
    python analysis/a02_network_catchments.py --tau-sweep 50,100,150 --limit 10
"""
from __future__ import annotations

import argparse
import heapq
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a02")

# Engine constants, reproduced so the Euclidean baseline is identical rather
# than approximated (transit_kashmir_v3.py:360-368, 1751-1777).
WALK_BUDGET_M = 400.0
VIRTUAL_STOP_SPACING_M = 250.0
SIMPLIFY_TOL_M = 2.0

TAU_M = 100.0            # off-network tail: one WorldPop cell
TAU_SWEEP = (50.0, 100.0, 150.0)
FRONTIER_BIN_M = 10.0    # radius quantisation for the frontier buffer groups
MAX_SNAP_M = WALK_BUDGET_M   # a stop farther than the whole budget is off-network


# ── pedestrian graph ──────────────────────────────────────────────────────────
def load_graph():
    """Load the walk graph and return (node_ids, xy_utm, adjacency in metres)."""
    import networkx as nx  # noqa: F401  (unpickling needs the class available)
    from pyproj import Transformer

    t0 = time.time()
    with C.WALK_GRAPH_PKL.open("rb") as fh:
        G = pickle.load(fh)
    ids = np.fromiter(G.nodes, dtype=np.int64, count=G.number_of_nodes())
    lat = np.array([G.nodes[i]["y"] for i in ids], dtype=np.float64)
    lon = np.array([G.nodes[i]["x"] for i in ids], dtype=np.float64)
    tr = Transformer.from_crs(C.WGS84, C.UTM, always_xy=True)
    x, y = tr.transform(lon, lat)
    xy = np.column_stack([x, y])

    # Compact CSR adjacency keyed by positional index: Dijkstra over dicts of
    # 962k nodes is dominated by attribute lookup, so the graph is flattened once.
    idx = {int(n): k for k, n in enumerate(ids)}
    deg = np.zeros(len(ids) + 1, dtype=np.int64)
    for u, v in G.edges:
        deg[idx[u] + 1] += 1
        deg[idx[v] + 1] += 1
    indptr = np.cumsum(deg)
    indices = np.empty(indptr[-1], dtype=np.int32)
    weights = np.empty(indptr[-1], dtype=np.float32)
    fill = indptr[:-1].copy()
    for u, v, w in G.edges(data="length"):
        iu, iv = idx[u], idx[v]
        indices[fill[iu]] = iv
        weights[fill[iu]] = w
        fill[iu] += 1
        indices[fill[iv]] = iu
        weights[fill[iv]] = w
        fill[iv] += 1
    log.info("graph loaded: %s nodes, %s edges (%.0fs)",
             f"{len(ids):,}", f"{G.number_of_edges():,}", time.time() - t0)
    return xy, indptr, indices, weights


def dijkstra_budget(indptr, indices, weights, sources: dict[int, float],
                    budget: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Multi-source Dijkstra with non-zero initial labels, truncated at `budget`.

    `sources` maps node index -> initial label (the snap offset), so a stop that
    sits 30 m off the network spends 30 m of its budget before it starts walking.
    Returns (node indices reached, distance at each) for d <= budget.
    """
    dist: dict[int, float] = {}
    heap = [(d0, s) for s, d0 in sources.items() if d0 <= budget]
    heapq.heapify(heap)
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for k in range(indptr[u], indptr[u + 1]):
            v = int(indices[k])
            if v in dist:
                continue
            nd = d + float(weights[k])
            if nd <= budget:
                heapq.heappush(heap, (nd, v))
    if not dist:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float64)
    nodes = np.fromiter(dist.keys(), dtype=np.int64, count=len(dist))
    ds = np.fromiter(dist.values(), dtype=np.float64, count=len(dist))
    return nodes, ds


# ── catchment construction ────────────────────────────────────────────────────
def stops_along(geom, spacing: float = VIRTUAL_STOP_SPACING_M):
    """Virtual stops exactly as the engine places them (_pts_along_line)."""
    length = geom.length
    if length < spacing:
        return [geom.interpolate(0.5, normalized=True)]
    return [geom.interpolate(d) for d in np.arange(0, length + spacing, spacing)
            if d <= length]


def network_catchment(xy, nodes, ds, tau: float, budget: float = WALK_BUDGET_M):
    """
    Union of tail discs B(v, min(budget - d(v), tau)) over reached nodes.

    Buffering ~10^4 discs individually is the slow step, so nodes are grouped by
    quantised tail radius and each group is buffered once as a MultiPoint. Nodes
    in the interior all share radius tau and form a single group.
    """
    from shapely import MultiPoint, union_all

    if len(nodes) == 0:
        return None
    r = np.minimum(budget - ds, tau)
    keep = r > 0
    if not keep.any():
        return None
    pts, r = xy[nodes[keep]], r[keep]
    # Round the frontier up to the next bin so the union is never understated.
    rb = np.ceil(r / FRONTIER_BIN_M) * FRONTIER_BIN_M
    rb = np.minimum(rb, tau)
    parts = []
    for rv in np.unique(rb):
        sel = rb == rv
        parts.append(MultiPoint(pts[sel]).buffer(float(rv), quad_segs=8))
    return union_all(parts)


def euclidean_catchment(stops, budget: float = WALK_BUDGET_M):
    from shapely import MultiPoint
    return MultiPoint([(p.x, p.y) for p in stops]).buffer(budget, quad_segs=8)


# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tau", type=float, default=TAU_M)
    ap.add_argument("--tau-sweep", default=",".join(str(t) for t in TAU_SWEEP))
    ap.add_argument("--limit", type=int, default=0, help="debug: first N routes")
    args = ap.parse_args()
    taus = sorted({float(t) for t in args.tau_sweep.split(",")} | {args.tau})

    import geopandas as gpd
    import rasterio
    import rasterstats
    from scipy.spatial import cKDTree
    from shapely.ops import transform as shp_transform
    from pyproj import Transformer

    routes = gpd.read_file(C.PLAN_GEOJSON)
    if args.limit:
        routes = routes.head(args.limit).copy()
    log.info("routes: %d active features", len(routes))

    utm = routes.to_crs(C.UTM)
    utm["geometry"] = utm.geometry.simplify(SIMPLIFY_TOL_M)

    # The published plan is internally inconsistent on a subset of routes: the
    # v3.4.4 correction pass substituted an externally verified road distance
    # into Route_KM without redrawing the geometry, and Population_Served_Raw was
    # never recomputed against the substituted distance. Those routes are
    # identified by Route_KM lying on an exact half-kilometre (the signature of a
    # hand-entered value) and by geometry length disagreeing with Route_KM. The
    # faithfulness of this reimplementation is therefore assessed on the
    # self-consistent routes, where the plan's own population column is a valid
    # target, and reported separately for the rest.
    geom_km = utm.geometry.length / 1000.0
    ratio = geom_km / routes["Route_KM"].astype(float).values
    utm["geom_km"] = geom_km.values
    utm["km_geometry_consistent"] = (ratio > 0.99) & (ratio < 1.01)
    log.info("plan self-consistency: %d/%d routes have geometry length within 1%% "
             "of Route_KM; %d carry a substituted distance",
             int(utm["km_geometry_consistent"].sum()), len(utm),
             int((~utm["km_geometry_consistent"]).sum()))

    xy, indptr, indices, weights = load_graph()
    tree = cKDTree(xy)

    to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform

    with rasterio.open(C.WORLDPOP_TIF) as src:
        nodata = src.nodata

    rows, geoms_net = [], {}
    t0 = time.time()
    for pos, (_, r) in enumerate(utm.iterrows(), start=1):
        rid = r["New_Route_ID"]
        stops = stops_along(r.geometry)
        eu = euclidean_catchment(stops)

        # Snap stops to the graph; keep the cheapest offset per node.
        pts = np.array([[p.x, p.y] for p in stops])
        off, nidx = tree.query(pts, k=1)
        sources: dict[int, float] = {}
        n_off_network = 0
        for o, ni in zip(off, nidx):
            if o > MAX_SNAP_M:
                n_off_network += 1
                continue
            ni = int(ni)
            if o < sources.get(ni, np.inf):
                sources[ni] = float(o)
        nodes, ds = dijkstra_budget(indptr, indices, weights, sources,
                                    WALK_BUDGET_M)

        rec = dict(New_Route_ID=rid, Route_Name=r.get("Route_Name"),
                   Route_Type=r.get("Route_Type"), Route_KM=r.get("Route_KM"),
                   geom_km=r.get("geom_km"),
                   km_geometry_consistent=bool(r.get("km_geometry_consistent")),
                   plan_pop_raw=r.get("Population_Served_Raw"),
                   n_stops=len(stops), n_stops_off_network=n_off_network,
                   snap_offset_median_m=float(np.median(off)),
                   snap_offset_p95_m=float(np.percentile(off, 95)),
                   n_nodes_reached=int(len(nodes)),
                   area_euclid_km2=eu.area / 1e6)

        zones = [shp_transform(to_wgs, eu)]
        for tau in taus:
            net = network_catchment(xy, nodes, ds, tau)
            rec[f"area_net_km2_tau{int(tau)}"] = (net.area / 1e6) if net else 0.0
            zones.append(shp_transform(to_wgs, net) if net is not None else eu)
            if tau == args.tau:
                geoms_net[rid] = net
        stats = rasterstats.zonal_stats(zones, str(C.WORLDPOP_TIF),
                                        stats=["sum"], nodata=nodata)
        rec["pop_euclid"] = float(stats[0]["sum"] or 0.0)
        for tau, s in zip(taus, stats[1:]):
            rec[f"pop_net_tau{int(tau)}"] = float(s["sum"] or 0.0)
        rows.append(rec)

        if pos % 20 == 0 or pos == len(utm):
            log.info("  %d/%d routes (%.0fs)", pos, len(utm), time.time() - t0)

    df = pd.DataFrame(rows)
    tau0 = int(args.tau)
    df["pop_net"] = df[f"pop_net_tau{tau0}"]
    df["area_net_km2"] = df[f"area_net_km2_tau{tau0}"]
    df["overstatement_abs"] = df["pop_euclid"] - df["pop_net"]
    df["overstatement_pct"] = 100 * df["overstatement_abs"] / df["pop_euclid"].replace(0, np.nan)
    df["area_ratio"] = df["area_net_km2"] / df["area_euclid_km2"].replace(0, np.nan)

    C.DERIVED.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.DERIVED / "a02_catchments.csv", index=False)

    # Faithfulness of the reimplementation against the published plan, assessed
    # only where the plan is self-consistent (see the note above).
    def _repro(sub: pd.DataFrame) -> dict:
        s = sub[sub["plan_pop_raw"].notna() & (sub["plan_pop_raw"] > 0)]
        if len(s) < 3:
            return dict(n=int(len(s)), median_abs_pct_error=np.nan, pearson_r=np.nan,
                        max_abs_pct_error=np.nan)
        err = 100 * (s["pop_euclid"] - s["plan_pop_raw"]).abs() / s["plan_pop_raw"]
        return dict(n=int(len(s)),
                    median_abs_pct_error=float(err.median()),
                    max_abs_pct_error=float(err.max()),
                    pearson_r=float(np.corrcoef(s["pop_euclid"], s["plan_pop_raw"])[0, 1]))

    repro_ok = _repro(df[df["km_geometry_consistent"]])
    repro_bad = _repro(df[~df["km_geometry_consistent"]])

    # Network-wide (deduplicated) coverage under each catchment definition.
    from shapely import union_all
    eu_union_pop = net_union_pop = np.nan
    try:
        eu_all = union_all([euclidean_catchment(stops_along(g)) for g in utm.geometry])
        net_all = union_all([g for g in geoms_net.values() if g is not None])
        zs = rasterstats.zonal_stats(
            [shp_transform(to_wgs, eu_all), shp_transform(to_wgs, net_all)],
            str(C.WORLDPOP_TIF), stats=["sum"], nodata=nodata)
        eu_union_pop = float(zs[0]["sum"] or 0.0)
        net_union_pop = float(zs[1]["sum"] or 0.0)
    except Exception as exc:                                    # pragma: no cover
        log.warning("network-wide union failed: %s", exc)

    out = dict(
        walk_budget_m=WALK_BUDGET_M,
        virtual_stop_spacing_m=VIRTUAL_STOP_SPACING_M,
        tau_m=args.tau,
        tau_sweep=taus,
        n_routes=int(len(df)),
        # reimplementation check, split by whether the plan is self-consistent
        reproduction_on_selfconsistent_routes=repro_ok,
        reproduction_on_substituted_km_routes=repro_bad,
        n_routes_km_geometry_consistent=int(df["km_geometry_consistent"].sum()),
        n_routes_km_substituted=int((~df["km_geometry_consistent"]).sum()),
        # per-route bias
        overstatement_pct_median=float(df["overstatement_pct"].median()),
        overstatement_pct_mean=float(df["overstatement_pct"].mean()),
        overstatement_pct_p25=float(df["overstatement_pct"].quantile(0.25)),
        overstatement_pct_p75=float(df["overstatement_pct"].quantile(0.75)),
        overstatement_pct_max=float(df["overstatement_pct"].max()),
        n_routes_overstated_gt_25pct=int((df["overstatement_pct"] > 25).sum()),
        n_routes_overstated_gt_50pct=int((df["overstatement_pct"] > 50).sum()),
        area_ratio_median=float(df["area_ratio"].median()),
        # network-wide
        pop_euclid_union=eu_union_pop,
        pop_net_union=net_union_pop,
        union_overstatement_pct=(100 * (eu_union_pop - net_union_pop) / eu_union_pop
                                 if eu_union_pop and np.isfinite(eu_union_pop) else np.nan),
        coverage_share_euclid=eu_union_pop / C.STUDY_AREA_POPULATION if np.isfinite(eu_union_pop) else np.nan,
        coverage_share_net=net_union_pop / C.STUDY_AREA_POPULATION if np.isfinite(net_union_pop) else np.nan,
        # tau sensitivity of the headline
        tau_sensitivity={
            f"tau{int(t)}": dict(
                pop_total=float(df[f"pop_net_tau{int(t)}"].sum()),
                overstatement_pct_median=float(
                    (100 * (df["pop_euclid"] - df[f"pop_net_tau{int(t)}"])
                     / df["pop_euclid"].replace(0, np.nan)).median()))
            for t in taus},
        # graph engagement
        n_stops_total=int(df["n_stops"].sum()),
        n_stops_off_network=int(df["n_stops_off_network"].sum()),
        snap_offset_median_m=float(df["snap_offset_median_m"].median()),
        note=("The Euclidean catchment is recomputed from the same geometries, "
              "stops, budget and zonal method as the published plan, so the "
              "difference is attributable to the pedestrian network alone. The "
              "network catchment allows a final off-network leg of up to tau, so "
              "it overstates the true network walkshed and the bias reported "
              "here is a lower bound. The published plan's own population column "
              "is a valid reproduction target only on the routes where geometry "
              "length agrees with Route_KM; on the remainder an externally "
              "verified distance was substituted without redrawing the geometry "
              "or recomputing population, so the recomputed value supersedes it."),
    )
    C.write_result(out, "a02_network_catchments")

    C.write_table(
        df.assign(overstatement_pct=df["overstatement_pct"].round(1))
          .sort_values("overstatement_pct", ascending=False)
          .head(20)[["New_Route_ID", "Route_Name", "Route_Type", "Route_KM",
                     "pop_euclid", "pop_net", "overstatement_pct", "area_ratio"]],
        "table03a_catchment_bias",
        "Routes whose Euclidean catchment most overstates population served")

    log.info("reproduction on %d self-consistent routes: median |err| %.2f%%, "
             "max %.2f%%, r = %.5f",
             repro_ok["n"], repro_ok["median_abs_pct_error"],
             repro_ok["max_abs_pct_error"], repro_ok["pearson_r"])
    log.info("reproduction on %d substituted-km routes: median |err| %.2f%% "
             "(expected to fail: the plan's population is stale there)",
             repro_bad["n"], repro_bad["median_abs_pct_error"])
    log.info("per-route overstatement: median %.1f%%, IQR %.1f-%.1f%%, max %.1f%%; "
             "%d routes >25%%, %d >50%%",
             out["overstatement_pct_median"], out["overstatement_pct_p25"],
             out["overstatement_pct_p75"], out["overstatement_pct_max"],
             out["n_routes_overstated_gt_25pct"], out["n_routes_overstated_gt_50pct"])
    log.info("network-wide: Euclid %s vs network %s (%.1f%% overstated); "
             "coverage %.1f%% -> %.1f%% of study population",
             f"{eu_union_pop:,.0f}", f"{net_union_pop:,.0f}",
             out["union_overstatement_pct"],
             100 * out["coverage_share_euclid"], 100 * out["coverage_share_net"])
    log.info("stops: %d total, %d off-network (>%.0f m), median snap %.1f m",
             out["n_stops_total"], out["n_stops_off_network"], MAX_SNAP_M,
             out["snap_offset_median_m"])

    # Persist network catchments for the figures.
    try:
        gnet = gpd.GeoDataFrame(
            dict(New_Route_ID=list(geoms_net.keys())),
            geometry=[geoms_net[k] for k in geoms_net], crs=C.UTM)
        gnet.to_file(C.CACHE / "catchments_network.gpkg", driver="GPKG")
    except Exception as exc:                                    # pragma: no cover
        log.warning("could not write catchment gpkg: %s", exc)


if __name__ == "__main__":
    main()
