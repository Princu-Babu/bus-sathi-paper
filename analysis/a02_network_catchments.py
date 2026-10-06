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
as a faithfulness check on this reimplementation (module a02b).

Formulation. Let R = 400 m be the walk budget, S the set of virtual stops, and
G = (V, E) the pedestrian graph with geodesic edge lengths. Each stop s is
snapped to its nearest graph node n(s) at offset o(s); stops with o(s) > R are
off-network and reported. Multi-source Dijkstra is run from {n(s)} with initial
labels o(s), giving d(v), the walking distance from the nearest stop to node v.
The catchment is

    A_net = union over v in V, d(v) <= R  of  B(v, min(R - d(v), tau))

where B is a Euclidean disc and tau is an off-network access allowance. The
catchment respects barriers: reaching the far bank of the Jhelum costs the detour
to a bridge, so distant nodes exhaust the budget and contribute nothing.

What this construction is NOT (audit F-03-11, F-01-U). The final leg of length up
to tau is allowed to run straight, which pushes the set outward; but the discs are
centred on graph NODES only, so stretches of a long edge more than 2 x tau
between two nodes are not covered. The coded set is therefore a node-sampled disc
union, not the continuous set the formula describes, and it is NOT claimed here
to be a formal upper bound on the true walkshed. The effect of sampling edges
densely was measured by the audit on a sample only and is NOT recomputed here
(it needs the graph Dijkstra, which this module's summary path never runs). For
the same reason the earlier statement that the reported bias is "a lower bound"
is withdrawn: the sensitivity analysis below shows settings (tau = 150 m, for one)
that give a smaller bias than the headline. What is robust is the sign, which is
positive at every setting tested, not the size.

Choice of tau. tau = 100 m, roughly one WorldPop cell (the cell is 0.000833 deg,
about 77 m east-west by 92 m north-south at 34 N, not exactly 100 m). Sensitivity
to tau in {50, 100, 150} m is reported beside the headline, and so are the walk
budget and stop-spacing grid of module a08a and the raster rasterisation rule.

Two bases for "how much does Euclidean overstate" (audit F-14-27, F-10-09,
F-02-24). With E the Euclidean count and N the network count for the same route
(or the same dissolved union):

    spurious_share_of_euclidean = (E - N) / E     share of the Euclidean count
                                                  that is not reachable on foot
    overstatement_of_network    = (E - N) / N     how much larger E is than N

They are related by overstatement = s / (1 - s) where s is the first. Only the
second is an "overstatement" in the usual sense. Both are reported everywhere;
the legacy JSON/CSV names `overstatement_pct*` carry the FIRST quantity and are
kept only so existing readers do not break (each has a `_note` sibling).

Outputs
    data/derived/a02_catchments.csv            per-route both populations and areas
    data/derived/a02_network_catchments.json   both bases, sensitivity, method notes,
                                               Euclidean-union reconciliation
    data/derived/a02_catchment_sensitivity.csv per-route Euclidean counts across the
                                               a08a grid and rasterisation rules
    paper/tables/table03a_catchment_bias.{csv,md}          20 routes, both bases
    paper/tables/table03a_catchment_bias_summary.{csv,md}  headline + sensitivity
    data/cache/catchments_network.gpkg         network catchment polygons (figures)

Usage
    python analysis/a02_network_catchments.py                 # HEAVY: full rebuild
    python analysis/a02_network_catchments.py --summary-only  # light: reporting from cache
    python analysis/a02_network_catchments.py --summary-only \
        --engine-outputs-root E:/kash   # optional: re-run the external geometry-version diagnostic
"""
from __future__ import annotations

import argparse
import heapq
import json
import pickle
import re
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

TAU_M = 100.0            # off-network tail: roughly one WorldPop cell
TAU_SWEEP = (50.0, 100.0, 150.0)
FRONTIER_BIN_M = 10.0    # radius quantisation for the frontier buffer groups
MAX_SNAP_M = WALK_BUDGET_M   # a stop farther than the whole budget is off-network

# Disc resolution used by THIS pipeline for both catchments (quad_segs per
# quarter circle). The engine calls `p.buffer(WALK_CATCHMENT_M)` with no
# argument, i.e. shapely's default of 16 (transit_kashmir_v3.py:1767).
BUFFER_QUAD_SEGS = 8
ENGINE_BUFFER_QUAD_SEGS = 16

# Coverage figure published by the engine (compute_network_population_total,
# transit_kashmir_v3.py:1955-1980): README.md:23 "2.32M ... = 35.2 %" and
# CLAUDE.md v3.4.1 notes record 2,317,958. Not stored in any raw input of this
# repository; the plan CSV's active Population_Served is rescaled to it
# (reconcile_active_population, :2186) and is used below as an in-repo check.
ENGINE_PUBLISHED_UNION_POP = 2_317_958

CATCH_CSV = C.DERIVED / "a02_catchments.csv"
NET_GPKG = C.CACHE / "catchments_network.gpkg"
A08A_CSV = C.DERIVED / "a08a_catchment_grid.csv"
A08A_JSON = C.DERIVED / "a08a_catchment_grid.json"
SENS_CSV = C.DERIVED / "a02_catchment_sensitivity.csv"
BIAS_CSV = C.DERIVED / "a02_catchment_bias.csv"
ENGINE_GEOM_DIAG = C.DERIVED / "a02_engine_geometry_versions.json"
BASE_KEY = "W400_S250"


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
    log.info("graph loaded: %s nodes, %s edges",
             f"{len(ids):,}", f"{G.number_of_edges():,}")
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
    Union of tail discs B(v, min(budget - d(v), tau)) over reached NODES.

    Node-sampled: only graph nodes carry a disc, so this is not the continuous
    set of the formula (see module docstring, audit F-03-11).

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
        parts.append(MultiPoint(pts[sel]).buffer(float(rv), quad_segs=BUFFER_QUAD_SEGS))
    return union_all(parts)


def euclidean_catchment(stops, budget: float = WALK_BUDGET_M,
                        quad_segs: int = BUFFER_QUAD_SEGS):
    from shapely import MultiPoint
    return MultiPoint([(p.x, p.y) for p in stops]).buffer(budget, quad_segs=quad_segs)


# ── the two bases (audit F-14-27 / F-10-09 / F-02-24) ─────────────────────────
def spurious_share_pct(E, N):
    """(E - N) / E in percent: the share of the Euclidean count not reachable on foot."""
    E = np.asarray(E, dtype=float)
    N = np.asarray(N, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(E > 0, 100.0 * (E - N) / E, np.nan)


def overstatement_of_network_pct(E, N):
    """(E - N) / N in percent: how much larger the Euclidean count is than the network count."""
    E = np.asarray(E, dtype=float)
    N = np.asarray(N, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(N > 0, 100.0 * (E - N) / N, np.nan)


def add_bias_columns(df: pd.DataFrame, tau0: int) -> pd.DataFrame:
    """Per-route bias columns at the base tau. Legacy `overstatement_pct` is kept
    (it equals the spurious share) and the two honestly named columns are added."""
    df = df.copy()
    df["pop_net"] = df[f"pop_net_tau{tau0}"]
    df["area_net_km2"] = df[f"area_net_km2_tau{tau0}"]
    df["overstatement_abs"] = df["pop_euclid"] - df["pop_net"]
    df["overstatement_pct"] = spurious_share_pct(df["pop_euclid"], df["pop_net"])
    df["spurious_share_of_euclidean_pct"] = df["overstatement_pct"]
    df["overstatement_of_network_pct"] = overstatement_of_network_pct(
        df["pop_euclid"], df["pop_net"])
    df["area_ratio"] = df["area_net_km2"] / df["area_euclid_km2"].replace(0, np.nan)
    return df


def dist_block(x) -> dict:
    s = pd.Series(np.asarray(x, dtype=float)).dropna()
    if s.empty:
        return dict(n=0)
    return dict(n=int(len(s)), median=float(s.median()), mean=float(s.mean()),
                p25=float(s.quantile(0.25)), p75=float(s.quantile(0.75)),
                min=float(s.min()), max=float(s.max()))


def pair_stats(E, N) -> dict:
    """Per-route distribution of both statistics (in-sample, n = routes passed)."""
    return dict(spurious_share_of_euclidean_pct=dist_block(spurious_share_pct(E, N)),
                overstatement_of_network_pct=dist_block(overstatement_of_network_pct(E, N)))


def union_stats(E_union: float, N_union: float) -> dict:
    E_union, N_union = float(E_union), float(N_union)
    return dict(
        euclid_pop=E_union, network_pop=N_union, difference=E_union - N_union,
        spurious_share_of_euclidean_pct=float(spurious_share_pct(E_union, N_union)),
        overstatement_of_network_pct=float(overstatement_of_network_pct(E_union, N_union)),
        coverage_share_euclid=E_union / C.STUDY_AREA_POPULATION,
        coverage_share_net=N_union / C.STUDY_AREA_POPULATION,
    )


# ── denominator (audit F-01-F: 6,584,762 vs 6,584,763) ────────────────────────
def denominator_report() -> dict:
    """What the raster actually sums to inside the 10-district union, and which of
    6,584,762 / 6,584,763 is the rounding. Same cell-centre rule and float64
    arithmetic as the engine's `study_area_population` (transit_kashmir_v3.py:1901)."""
    import rasterio
    from rasterio.mask import mask as rmask

    geoms = [f["geometry"] for f in
             json.loads(Path(C.DISTRICTS_GEOJSON).read_text(encoding="utf-8"))["features"]]
    with rasterio.open(C.WORLDPOP_TIF) as src:
        out, _ = rmask(src, geoms, crop=True, nodata=0)
    arr = out[0].astype("float64")
    raw = float(arr[arr > 0].sum())
    used = int(C.STUDY_AREA_POPULATION)
    return dict(
        used_in_all_shares=used,
        used_source="common.STUDY_AREA_POPULATION (the engine's int() of the raster sum)",
        raster_sum_inside_district_union=raw,
        engine_integer_truncation=int(raw),
        round_half_up=int(round(raw)),
        which_is_rounding=("6,584,762 is the raster sum truncated by int() (as in the "
                           "engine); 6,584,763 is the same sum rounded to nearest. The "
                           "underlying value is 6,584,762.6; the choice moves any "
                           "coverage share by about 1e-7 of itself."),
        relative_effect_on_shares=abs(round(raw) - used) / raw,
        used_equals_engine_truncation=bool(int(raw) == used),
    )


# ── zonal helper ──────────────────────────────────────────────────────────────
def _make_zonal(nodata):
    import rasterstats
    from pyproj import Transformer
    from shapely.ops import transform as shp_transform
    to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform

    def zsum(geoms_utm, all_touched: bool = False) -> list[float]:
        zones = [shp_transform(to_wgs, g) for g in geoms_utm]
        st = rasterstats.zonal_stats(zones, str(C.WORLDPOP_TIF), stats=["sum"],
                                     nodata=nodata, all_touched=all_touched)
        return [float(s["sum"] or 0.0) for s in st]
    return zsum


def _parse_key(key: str) -> tuple[int, int]:
    m = re.fullmatch(r"W(\d+)_S(\d+)", key)
    if not m:
        raise ValueError(f"unrecognised a08a grid key {key!r}")
    return int(m.group(1)), int(m.group(2))


def external_geometry_diagnostic(root: Path) -> dict:
    """OPTIONAL, run only with --engine-outputs-root. Euclidean union of the active
    routes' geometry as shipped in each engine release, using this module's
    construction. Reads files outside this repository, so the result is stored in
    a02_engine_geometry_versions.json and only *embedded* by later runs."""
    import geopandas as gpd
    import rasterio
    from shapely import union_all

    with rasterio.open(C.WORLDPOP_TIF) as src:
        nodata = src.nodata
    zsum = _make_zonal(nodata)
    res = {}
    for v in ("3.4.1", "3.4.2", "3.4.3", "3.4.4", "3.4.5"):
        p = Path(root) / f"outputs_v{v}" / "Rationalised_Routes_Kashmir_v3.geojson"
        if not p.exists():
            res[v] = dict(status="file_not_found", path=str(p))
            continue
        g = gpd.read_file(p)
        if "Action_Taken" in g.columns:
            g = g[g["Action_Taken"].isin(C.ACTIVE_ACTIONS)]
        u = g.to_crs(C.UTM)
        u["geometry"] = u.geometry.simplify(SIMPLIFY_TOL_M)
        polys = [euclidean_catchment(stops_along(x)) for x in u.geometry
                 if x is not None and not x.is_empty]
        pop = zsum([union_all(polys)])[0]
        res[v] = dict(n_routes=int(len(g)), euclid_union_pop=pop)
        log.info("external geometry v%s: %d routes, Euclid union %s", v, len(g), f"{pop:,.0f}")
    out = dict(
        status="external_diagnostic",
        what=("Euclidean-union population of the ACTIVE routes' geometry in each engine "
              "release's Rationalised_Routes_Kashmir_v3.geojson, with this module's "
              "construction (W=400 m, S=250 m, quad_segs=8, cell-centre rule)."),
        source_root="E:/kash (not part of this repository; optional, regenerate with --engine-outputs-root)",
        by_release=res)
    ENGINE_GEOM_DIAG.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    return out


# ── reporting / light entry point ─────────────────────────────────────────────
def run_summary(tau: float = TAU_M, tau_sweep=TAU_SWEEP,
                engine_outputs_root: str | None = None) -> dict:
    """
    Rebuild a02's JSON and tables from CACHED data only (no graph, no Dijkstra):
      * per-route populations from data/derived/a02_catchments.csv,
      * the network union from data/cache/catchments_network.gpkg,
      * the Euclidean union (and the Euclidean side of the a08a grid) recomputed
        from the plan geometry, which is cheap (a few seconds per configuration),
      * the network side of the a08a grid from data/derived/a08a_catchment_grid.*.
    """
    import geopandas as gpd
    import rasterio
    from shapely import union_all

    t0 = time.time()
    taus = sorted({float(t) for t in tau_sweep} | {float(tau)})
    tau0 = int(tau)

    cached = pd.read_csv(CATCH_CSV)
    df = add_bias_columns(cached, tau0)
    if "overstatement_pct" in cached.columns:
        d = np.nanmax(np.abs(cached["overstatement_pct"].to_numpy(float)
                             - df["overstatement_pct"].to_numpy(float)))
        if d > 1e-9:
            raise SystemExit(f"cached overstatement_pct disagrees with recomputation ({d:g})")
    ids = df["New_Route_ID"].tolist()

    routes = gpd.read_file(C.PLAN_GEOJSON)
    utm = routes.to_crs(C.UTM)
    utm["geometry"] = utm.geometry.simplify(SIMPLIFY_TOL_M)
    utm = utm.set_index("New_Route_ID").loc[ids]

    with rasterio.open(C.WORLDPOP_TIF) as src:
        nodata = src.nodata
    zsum = _make_zonal(nodata)

    # ── base Euclidean catchments, recomputed ──
    eu_polys = [euclidean_catchment(stops_along(g)) for g in utm.geometry]
    eu_union = union_all(eu_polys)
    z = zsum(eu_polys + [eu_union])
    eu_pop, eu_union_pop = np.array(z[:-1]), z[-1]
    eu_diff = float(np.max(np.abs(eu_pop - df["pop_euclid"].to_numpy(float))))

    # ── base network catchments, from the cached polygons ──
    gnet = gpd.read_file(NET_GPKG)
    if gnet.crs is None or gnet.crs.to_epsg() != 32643:
        gnet = gnet.to_crs(C.UTM)
    net_by_id = dict(zip(gnet["New_Route_ID"], gnet.geometry))
    net_polys = [net_by_id.get(r) for r in ids]
    valid_idx = [i for i, p in enumerate(net_polys) if p is not None and not p.is_empty]
    net_union = union_all([net_polys[i] for i in valid_idx])
    z = zsum([net_polys[i] for i in valid_idx] + [net_union])
    net_pop = np.zeros(len(ids))
    net_pop[valid_idx] = z[:-1]
    net_union_pop = z[-1]
    net_diff = float(np.max(np.abs(net_pop - df["pop_net"].to_numpy(float))))
    log.info("cache check: max |recomputed - cached| per route: Euclid %.4g, network %.4g",
             eu_diff, net_diff)

    # ── rasterisation rule: cell-centre (headline) vs all-touched ──
    z_eu_at = zsum(eu_polys + [eu_union], all_touched=True)
    z_net_at = zsum([net_polys[i] for i in valid_idx] + [net_union], all_touched=True)
    eu_pop_at, eu_union_at = np.array(z_eu_at[:-1]), z_eu_at[-1]
    net_pop_at = np.zeros(len(ids))
    net_pop_at[valid_idx] = z_net_at[:-1]
    net_union_at = z_net_at[-1]

    # ── Euclidean construction: engine disc resolution ──
    eu_polys16 = [euclidean_catchment(stops_along(g), quad_segs=ENGINE_BUFFER_QUAD_SEGS)
                  for g in utm.geometry]
    eu_union16 = union_all(eu_polys16)
    eu_union_pop16 = zsum([eu_union16])[0]

    # ── a08a walk-budget / stop-spacing grid: Euclidean side recomputed ──
    grid = pd.read_csv(A08A_CSV).set_index("New_Route_ID").loc[ids]
    grid_json = json.loads(A08A_JSON.read_text(encoding="utf-8"))
    keys = sorted(grid_json["union_coverage"].keys(),
                  key=lambda k: (_parse_key(k)[1] != 250, _parse_key(k)[1], _parse_key(k)[0]))
    sens_rows = pd.DataFrame({"New_Route_ID": ids})
    grid_blocks = {}
    for key in keys:
        W, S = _parse_key(key)
        if key == BASE_KEY:
            polys, upoly = eu_polys, eu_union
        else:
            polys = [euclidean_catchment(stops_along(g, float(S)), float(W))
                     for g in utm.geometry]
            upoly = union_all(polys)
        zz = zsum(polys + [upoly])
        E_route, E_union = np.array(zz[:-1]), zz[-1]
        N_route = grid[f"pop_{key}"].to_numpy(float)
        N_union = float(grid_json["union_coverage"][key]["pop"])
        sens_rows[f"pop_euclid_{key}"] = E_route
        grid_blocks[key] = dict(
            walk_budget_m=W, stop_spacing_m=S, tau_m=float(grid_json["tau_m"]),
            rasterisation="cell-centre",
            per_route=pair_stats(E_route, N_route),
            union=union_stats(E_union, N_union),
            network_side_source="a08a_catchment_grid (cached; heavy build not re-run)",
            euclid_side_source="recomputed here from plan geometry",
        )
    sens_rows["pop_euclid_base_all_touched"] = eu_pop_at
    sens_rows["pop_net_base_all_touched"] = net_pop_at
    sens_rows["pop_euclid_base_quad16"] = zsum(eu_polys16)
    sens_rows.to_csv(SENS_CSV, index=False)

    # ── headline blocks ──
    E, N = df["pop_euclid"].to_numpy(float), df["pop_net"].to_numpy(float)
    per_route = pair_stats(E, N)
    union = union_stats(eu_union_pop, net_union_pop)

    spur = per_route["spurious_share_of_euclidean_pct"]
    over = per_route["overstatement_of_network_pct"]
    sp_arr = spurious_share_pct(E, N)
    ov_arr = overstatement_of_network_pct(E, N)

    # ── tau sensitivity (per-route from the cached CSV; union needs a heavy rebuild) ──
    tau_block, tau_legacy = {}, {}
    for t in taus:
        Nt = df[f"pop_net_tau{int(t)}"].to_numpy(float)
        ps = pair_stats(E, Nt)
        tau_block[f"tau{int(t)}"] = dict(
            tau_m=t, walk_budget_m=WALK_BUDGET_M, stop_spacing_m=VIRTUAL_STOP_SPACING_M,
            rasterisation="cell-centre", per_route=ps,
            union=(union if int(t) == tau0 else dict(
                status="not_computable_from_cache",
                why=("the deduplicated union needs the network polygons at this tau, which "
                     "exist only for the base tau in catchments_network.gpkg; rebuilding "
                     "them re-runs the graph Dijkstra, which this summary path never does"))),
            sum_of_per_route_network_pop=float(Nt.sum()),
            sum_of_per_route_network_pop_note=("sum of overlapping per-route counts; NOT a "
                                               "network quantity (walksheds overlap)"),
        )
        tau_legacy[f"tau{int(t)}"] = dict(
            pop_total=float(Nt.sum()),
            pop_total_note=("sum of overlapping per-route counts; not a deduplicated network "
                            "total"),
            overstatement_pct_median=float(np.nanmedian(spurious_share_pct(E, Nt))),
            overstatement_pct_median_note=("median of (E-N)/E, i.e. the SPURIOUS SHARE of the "
                                           "Euclidean count, not an overstatement; see "
                                           "spurious_share_of_euclidean_pct_median / "
                                           "overstatement_of_network_pct_median"),
            spurious_share_of_euclidean_pct_median=ps["spurious_share_of_euclidean_pct"]["median"],
            spurious_share_of_euclidean_pct_p25=ps["spurious_share_of_euclidean_pct"]["p25"],
            spurious_share_of_euclidean_pct_p75=ps["spurious_share_of_euclidean_pct"]["p75"],
            overstatement_of_network_pct_median=ps["overstatement_of_network_pct"]["median"],
            overstatement_of_network_pct_p25=ps["overstatement_of_network_pct"]["p25"],
            overstatement_of_network_pct_p75=ps["overstatement_of_network_pct"]["p75"],
        )

    # ── rasterisation-rule sensitivity ──
    zonal_block = dict(
        headline_rule="cell-centre",
        all_touched=dict(
            per_route=pair_stats(eu_pop_at, net_pop_at),
            union=union_stats(eu_union_at, net_union_at),
            note=("same polygons, only the rasterisation rule changed; recomputed on all "
                  f"{len(ids)} routes (the audit's own check used a 17-route sample)"),
        ),
    )

    # ── is the headline a lower bound?  computed from the data, never asserted ──
    head_med = spur["median"]
    setting_medians = {f"tau={int(t)} m": tau_block[f"tau{int(t)}"]["per_route"][
        "spurious_share_of_euclidean_pct"]["median"] for t in taus}
    for key, b in grid_blocks.items():
        setting_medians[f"{key} (tau={int(b['tau_m'])} m)"] = b["per_route"][
            "spurious_share_of_euclidean_pct"]["median"]
    setting_medians["all-touched rule (base W/S/tau)"] = zonal_block["all_touched"][
        "per_route"]["spurious_share_of_euclidean_pct"]["median"]
    smaller = sorted(k for k, v in setting_medians.items() if v < head_med - 1e-9)
    over_medians = {}
    for t in taus:
        over_medians[f"tau={int(t)} m"] = tau_block[f"tau{int(t)}"]["per_route"][
            "overstatement_of_network_pct"]["median"]
    for key, b in grid_blocks.items():
        over_medians[f"{key} (tau={int(b['tau_m'])} m)"] = b["per_route"][
            "overstatement_of_network_pct"]["median"]
    over_medians["all-touched rule (base W/S/tau)"] = zonal_block["all_touched"][
        "per_route"]["overstatement_of_network_pct"]["median"]
    sensitivity_summary = dict(
        n_settings=len(setting_medians),
        headline_spurious_share_median_pct=head_med,
        spurious_share_median_by_setting=setting_medians,
        overstatement_of_network_median_by_setting=over_medians,
        spurious_share_median_range_pct=[min(setting_medians.values()),
                                         max(setting_medians.values())],
        overstatement_of_network_median_range_pct=[min(over_medians.values()),
                                                   max(over_medians.values())],
        bias_positive_at_every_setting=bool(all(v > 0 for v in setting_medians.values())),
        headline_is_lower_bound_over_these_settings=bool(len(smaller) == 0),
        settings_with_smaller_bias_than_headline=smaller,
        note=("The headline (W=400 m, S=250 m, tau=100 m, cell-centre rule) is NOT the "
              "smallest bias among the settings tried unless the list of smaller settings "
              "is empty; what holds at every setting is the sign. 'Lower bound' is not "
              "claimed."),
    )

    # ── reconciliation of the two Euclidean totals (audit F-03-10, F-05-16) ──
    plan = pd.read_csv(C.PLAN_CSV)
    act = plan[plan["Action_Taken"].isin(C.ACTIVE_ACTIONS)]
    plan_active_sum = float(act["Population_Served"].sum())
    ext = None
    if engine_outputs_root:
        ext = external_geometry_diagnostic(Path(engine_outputs_root))
    elif ENGINE_GEOM_DIAG.exists():
        ext = json.loads(ENGINE_GEOM_DIAG.read_text(encoding="utf-8"))
    diff = eu_union_pop - ENGINE_PUBLISHED_UNION_POP
    reconciliation = dict(
        engine_published=dict(
            union_pop=ENGINE_PUBLISHED_UNION_POP,
            coverage_share=ENGINE_PUBLISHED_UNION_POP / C.STUDY_AREA_POPULATION,
            source=("E:/kash/README.md:23 ('2.32M residents ... 35.2 %') and E:/kash/CLAUDE.md "
                    "v3.4.1 notes (2,317,958); computed by compute_network_population_total, "
                    "transit_kashmir_v3.py:1955-1980, called at :6029"),
            in_repo_check=dict(
                plan_csv_active_population_served_sum=plan_active_sum,
                difference_from_published=plan_active_sum - ENGINE_PUBLISHED_UNION_POP,
                note=("the plan CSV's active Population_Served is rescaled to the engine union "
                      "(reconcile_active_population, :2186) and rounded per row, so it matches "
                      "the published union to a few persons; this is the only in-repo trace of "
                      "the published figure")),
        ),
        this_pipeline=dict(
            union_pop=eu_union_pop,
            coverage_share=eu_union_pop / C.STUDY_AREA_POPULATION,
            construction=("186 active routes; plan geometry as shipped (v3.4.5-geo), 2 m "
                          "simplification, 250 m virtual stops, discs of 400 m with "
                          f"quad_segs={BUFFER_QUAD_SEGS}, one zonal sum over the dissolved "
                          "union, cell-centre rule; no tourist multiplier anywhere"),
        ),
        difference_persons=diff,
        difference_pct_of_engine=100.0 * diff / ENGINE_PUBLISHED_UNION_POP,
        difference_pp_of_study_area=100.0 * diff / C.STUDY_AREA_POPULATION,
        causes=[
            dict(cause="tourist multiplier", status="excluded_by_code",
                 evidence=("the x1.3 is applied to the per-route Population_Served column "
                           "(:1863); compute_network_population_total (:1961-1973) reads only "
                           "gdf['Catchment'] and takes one zonal_stats sum over the dissolved "
                           "union, so the boosted column never enters the union")),
            dict(cause="zonal rule", status="excluded_by_code",
                 evidence=("the engine's zonal_stats call (:1967) uses the rasterstats default "
                           "(cell-centre), the same as this pipeline")),
            dict(cause="disc resolution (quad_segs 8 here vs shapely default 16 in the engine)",
                 status="measured_small_wrong_direction",
                 evidence=(f"Euclidean union at quad_segs=16 = {eu_union_pop16:,.0f}, i.e. "
                           f"{eu_union_pop16 - eu_union_pop:+,.0f} persons "
                           f"({100 * (eu_union_pop16 / eu_union_pop - 1):+.2f} %) - it would "
                           "widen, not close, the gap with the engine at today's geometry")),
            dict(cause="route set: the engine's union dissolves ALL 644 rows incl. merged ones",
                 status="not_isolated",
                 evidence=("compute_network_population_total is called at :6029 with the full "
                           "frame and does not filter Action_Taken; merged rows' geometry is not "
                           "in this repository, so their contribution cannot be recomputed. This "
                           "pushes the engine figure UP relative to a 186-route union")),
            dict(cause="geometry version of the 186 active routes", status="partly_measured",
                 evidence=("the active geometry changed after the engine's coverage run "
                           "(v3.4.4 distance work; v3.4.5-geo redrew 15 lines). The Euclidean "
                           "union of the shipped geometry moves with release - see "
                           "external_geometry_diagnostic. This pushes this pipeline's figure "
                           "UP relative to the run that produced 2,317,958")),
        ],
        external_geometry_diagnostic=(ext if ext else dict(
            status="not_run",
            why="optional; needs the engine outputs directory (--engine-outputs-root)")),
        isolated_cause=False,
        conclusion=("The 21k-person gap (about 0.9 % of the figure; 0.3 pp of coverage) is not "
                    "attributable to a single cause from what is in this repository. Two "
                    "effects of opposite sign are identified (the engine unions merged rows as "
                    "well; the geometry has since been redrawn) and neither can be quantified "
                    "without the engine's run-time geometry. State both numbers; do not "
                    "present 35.5 % as the plan's published coverage (35.2 %)."),
    )

    # ── faithfulness of the Euclidean reimplementation (unchanged logic) ──
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

    consistent = df["km_geometry_consistent"].astype(bool)
    repro_ok = _repro(df[consistent])
    repro_bad = _repro(df[~consistent])

    legacy_note = ("LEGACY NAME. Computed as (E - N) / E, the SPURIOUS SHARE of the Euclidean "
                   "count; it is not an overstatement. Use spurious_share_of_euclidean_pct_* "
                   "or overstatement_of_network_pct_* (audit F-14-27, F-10-09, F-02-24).")
    n_routes = int(len(df))
    out = dict(
        # ---- provenance --------------------------------------------------------
        mode="summary_only (reporting rebuilt from cached per-route CSV, network polygons and "
             "a08a outputs; graph/Dijkstra not re-run)",
        in_sample_note=(f"All statistics describe the {n_routes} active routes of the published "
                        "plan (no resampling, no held-out data): they are in-sample descriptive "
                        "statistics of that one plan, not estimates for other networks."),
        cache_consistency=dict(
            max_abs_diff_pop_euclid_recomputed_vs_cached_csv=eu_diff,
            max_abs_diff_pop_net_from_gpkg_vs_cached_csv=net_diff,
            a08a_base_vs_a02_pop_net_max_abs_diff=float(np.max(np.abs(
                grid[f"pop_{BASE_KEY}"].to_numpy(float) - df["pop_net"].to_numpy(float)))),
        ),
        # ---- parameters --------------------------------------------------------
        walk_budget_m=WALK_BUDGET_M,
        virtual_stop_spacing_m=VIRTUAL_STOP_SPACING_M,
        tau_m=float(tau),
        tau_sweep=taus,
        n_routes=n_routes,
        denominator=denominator_report(),
        study_area_population=int(C.STUDY_AREA_POPULATION),
        # ---- definitions -------------------------------------------------------
        definitions=dict(
            spurious_share_of_euclidean="(E - N) / E : share of the Euclidean count that is not reachable on the walk network",
            overstatement_of_network="(E - N) / N : how much larger the Euclidean count is than the network count",
            relation="overstatement = s / (1 - s), s = spurious share (as fractions)",
            base="E = Euclidean count, N = network count (tau = base), same route or same dissolved union",
        ),
        # ---- headline, both bases, named --------------------------------------------
        bias_per_route=dict(
            basis=f"per route, n = {n_routes} active routes, base setting W=400 m S=250 m tau=100 m, cell-centre rule, in-sample",
            **per_route,
            n_routes_spurious_share_gt_25pct=int((sp_arr > 25).sum()),
            n_routes_spurious_share_gt_50pct=int((sp_arr > 50).sum()),
            n_routes_overstatement_of_network_gt_50pct=int((ov_arr > 50).sum()),
            n_routes_overstatement_of_network_gt_100pct=int((ov_arr > 100).sum()),
        ),
        bias_union=dict(
            basis=("one deduplicated union over the 186 active routes, base setting, "
                   f"denominator {C.STUDY_AREA_POPULATION:,}; in-sample"),
            **union,
        ),
        spurious_share_of_euclidean_pct_median=spur["median"],
        spurious_share_of_euclidean_pct_p25=spur["p25"],
        spurious_share_of_euclidean_pct_p75=spur["p75"],
        overstatement_of_network_pct_median=over["median"],
        overstatement_of_network_pct_p25=over["p25"],
        overstatement_of_network_pct_p75=over["p75"],
        spurious_share_of_euclidean_pct_union=union["spurious_share_of_euclidean_pct"],
        overstatement_of_network_pct_union=union["overstatement_of_network_pct"],
        # ---- legacy keys, values unchanged, each with a _note sibling -----------------
        reproduction_on_selfconsistent_routes=repro_ok,
        reproduction_on_substituted_km_routes=repro_bad,
        n_routes_km_geometry_consistent=int(consistent.sum()),
        n_routes_km_substituted=int((~consistent).sum()),
        overstatement_pct_median=spur["median"],
        overstatement_pct_mean=spur["mean"],
        overstatement_pct_p25=spur["p25"],
        overstatement_pct_p75=spur["p75"],
        overstatement_pct_max=spur["max"],
        n_routes_overstated_gt_25pct=int((sp_arr > 25).sum()),
        n_routes_overstated_gt_50pct=int((sp_arr > 50).sum()),
        area_ratio_median=float(df["area_ratio"].median()),
        pop_euclid_union=eu_union_pop,
        pop_net_union=net_union_pop,
        union_overstatement_pct=union["spurious_share_of_euclidean_pct"],
        coverage_share_euclid=union["coverage_share_euclid"],
        coverage_share_net=union["coverage_share_net"],
        tau_sensitivity=tau_legacy,
        n_stops_total=int(df["n_stops"].sum()),
        n_stops_off_network=int(df["n_stops_off_network"].sum()),
        snap_offset_median_m=float(df["snap_offset_median_m"].median()),
        # ---- sensitivity beside the headline -------------------------------------
        sensitivity=dict(
            tau=tau_block,
            walk_budget_and_stop_spacing=grid_blocks,
            rasterisation_rule=zonal_block,
            summary=sensitivity_summary,
        ),
        euclidean_union_reconciliation=reconciliation,
        # ---- method notes as data -------------------------------------------------
        method_notes=dict(
            zonal_rule=("cell-centre: rasterstats.zonal_stats default (all_touched=False); a "
                        "WorldPop cell is counted when its centre lies inside the polygon. The "
                        "effect of all_touched=True is recomputed on all routes in "
                        "sensitivity.rasterisation_rule."),
            raster_cell=dict(
                degrees=0.00083333333,
                approx_metres_east_west_at_34N=round(0.00083333333 * 111320 * np.cos(np.radians(34.0)), 1),
                approx_metres_north_south_at_34N=round(0.00083333333 * 110950, 1),
                note="not 100 m x 100 m; tau = 100 m is 'roughly one cell'"),
            euclidean_construction=dict(
                type="union of Euclidean discs around virtual stops",
                virtual_stop_spacing_m=VIRTUAL_STOP_SPACING_M,
                walk_budget_m=WALK_BUDGET_M,
                simplification_tolerance_m=SIMPLIFY_TOL_M,
                buffer_quad_segs=BUFFER_QUAD_SEGS,
                engine_buffer_quad_segs=ENGINE_BUFFER_QUAD_SEGS,
                effect_of_engine_resolution_on_union=dict(
                    status="recomputed",
                    euclid_union_pop_at_engine_resolution=eu_union_pop16,
                    change_persons=eu_union_pop16 - eu_union_pop,
                    change_pct=100 * (eu_union_pop16 / eu_union_pop - 1)),
                note=("both catchments use the same disc resolution here, so the comparison "
                      "is like-for-like")),
            network_construction=dict(
                type="node-sampled disc union",
                description=("discs of radius min(R - d(v), tau) centred on reached graph nodes "
                             "only; between two nodes more than 2 x tau apart the edge is not "
                             "fully covered"),
                formal_upper_bound_on_true_walkshed=False,
                effect_of_edge_densification="not recomputed (needs the graph Dijkstra; the cached outputs are node-sampled)",
                audit_sample_estimate=("the audit reported a small effect on a 17-route sample; "
                                       "those figures are not reproduced here"),
            ),
            lower_bound_claim=("withdrawn: the headline bias is not the smallest in the "
                               "sensitivity sweep (see sensitivity.summary) and the construction "
                               "is node-sampled; only the sign is robust"),
        ),
        note=("The Euclidean catchment is recomputed from the same geometries, stops, budget and "
              "zonal method as the published plan, so the difference is attributable to the "
              "pedestrian network (plus the stated construction choices) alone. The headline "
              "bias is reported on two bases (spurious share of the Euclidean count; "
              "overstatement of the network count) and beside its sensitivity to tau, the "
              "walk budget, the stop spacing and the rasterisation rule; it is not claimed to "
              "be a lower bound. The published plan's own population column is a valid "
              "reproduction target only on the routes where geometry length agrees with "
              "Route_KM; on the remainder an externally verified distance was substituted "
              "without redrawing the geometry or recomputing population, so the recomputed "
              "value supersedes it."),
    )
    for k in ("overstatement_pct_median", "overstatement_pct_mean", "overstatement_pct_p25",
              "overstatement_pct_p75", "overstatement_pct_max",
              "n_routes_overstated_gt_25pct", "n_routes_overstated_gt_50pct",
              "union_overstatement_pct"):
        out[f"{k}_note"] = legacy_note
    out["pop_euclid_union_note"] = ("recomputed here (this pipeline's Euclidean construction on the "
                                    "shipped geometry); NOT the engine-published 2,317,958 - see "
                                    "euclidean_union_reconciliation")
    out["tau_sensitivity_note"] = ("legacy block: `overstatement_pct_median` is the spurious share "
                                   "(E-N)/E and `pop_total` is a sum of overlapping per-route "
                                   "counts; both-basis statistics are in sensitivity.tau")
    C.write_result(out, "a02_network_catchments")

    # ── per-route bias columns: a SEPARATE file. a02_catchments.csv is the cached output of
    # the heavy build and is never rewritten by the summary path (so its values and column
    # set stay exactly as built). The legacy `overstatement_pct` column in it equals the
    # spurious share (E-N)/E; the two honestly named columns live here. ──
    bias_csv = df[["New_Route_ID", "Route_Name", "Route_Type", "pop_euclid", "pop_net"]].copy()
    bias_csv["spurious_share_of_euclidean_pct"] = df["spurious_share_of_euclidean_pct"].to_numpy()
    bias_csv["overstatement_of_network_pct"] = df["overstatement_of_network_pct"].to_numpy()
    bias_csv["legacy_overstatement_pct_in_a02_catchments"] = df["overstatement_pct"].to_numpy()
    bias_csv["legacy_overstatement_pct_note"] = ("equals spurious_share_of_euclidean_pct = (E-N)/E; "
                                                 "not an overstatement")
    bias_csv.to_csv(BIAS_CSV, index=False)

    # ── tables ──
    top = (df.assign(spurious_share_of_euclidean_pct=df["spurious_share_of_euclidean_pct"].round(1),
                     overstatement_of_network_pct=df["overstatement_of_network_pct"].round(1),
                     area_ratio=df["area_ratio"].round(3))
             .sort_values("spurious_share_of_euclidean_pct", ascending=False)
             .head(20)[["New_Route_ID", "Route_Name", "Route_Type", "Route_KM",
                        "pop_euclid", "pop_net", "spurious_share_of_euclidean_pct",
                        "overstatement_of_network_pct", "area_ratio"]]
             .rename(columns={"pop_euclid": "euclidean_count", "pop_net": "network_count"}))
    C.write_table(
        top, "table03a_catchment_bias",
        "The 20 routes whose Euclidean catchment count most exceeds the network-walk count. "
        "Two bases: (E-N)/E is the share of the Euclidean count not reachable on foot; "
        "(E-N)/N is how much larger the Euclidean count is than the network count")

    def _row(label, wm, sp, tau_m, rule, pr, un):
        s, o = pr["spurious_share_of_euclidean_pct"], pr["overstatement_of_network_pct"]
        u = un if isinstance(un, dict) and "euclid_pop" in un else {}
        return {
            "setting": label, "walk_budget_m": wm, "stop_spacing_m": sp, "tau_m": tau_m,
            "rasterisation": rule, "n_routes": s["n"],
            "union_euclidean_pop": u.get("euclid_pop", np.nan),
            "union_network_pop": u.get("network_pop", np.nan),
            "union_spurious_share_pct": u.get("spurious_share_of_euclidean_pct", np.nan),
            "union_overstatement_pct": u.get("overstatement_of_network_pct", np.nan),
            "route_median_spurious_share_pct": s["median"], "route_p25_spurious_share_pct": s["p25"],
            "route_p75_spurious_share_pct": s["p75"],
            "route_median_overstatement_pct": o["median"], "route_p25_overstatement_pct": o["p25"],
            "route_p75_overstatement_pct": o["p75"],
        }
    rows = [_row("HEADLINE", WALK_BUDGET_M, VIRTUAL_STOP_SPACING_M, tau, "cell-centre",
                 per_route, union)]
    for t in taus:
        if int(t) == tau0:
            continue
        b = tau_block[f"tau{int(t)}"]
        rows.append(_row(f"tau = {int(t)} m", WALK_BUDGET_M, VIRTUAL_STOP_SPACING_M, t,
                         "cell-centre", b["per_route"], b["union"]))
    for key, b in grid_blocks.items():
        if key == BASE_KEY:
            continue
        rows.append(_row(f"W/S grid {key}", b["walk_budget_m"], b["stop_spacing_m"], b["tau_m"],
                         "cell-centre", b["per_route"], b["union"]))
    rows.append(_row("all-touched rasterisation", WALK_BUDGET_M, VIRTUAL_STOP_SPACING_M, tau,
                     "all_touched", zonal_block["all_touched"]["per_route"],
                     zonal_block["all_touched"]["union"]))
    summ = pd.DataFrame(rows).round(2)
    C.write_table(
        summ, "table03a_catchment_bias_summary",
        "Euclidean versus network-walk population counts: headline and sensitivity, on both "
        "bases. (E-N)/E = share of the Euclidean count not reachable on foot; (E-N)/N = how "
        "much larger the Euclidean count is than the network count. Per-route columns are "
        "medians and quartiles over the 186 active routes (in-sample); union columns are "
        "deduplicated and blank where the union cannot be recomputed from cached data")

    log.info("reproduction on %d self-consistent routes: median |err| %.2f%%, "
             "max %.2f%%, r = %.5f", repro_ok["n"], repro_ok["median_abs_pct_error"],
             repro_ok["max_abs_pct_error"], repro_ok["pearson_r"])
    log.info("per route (n=%d): spurious share (E-N)/E median %.1f%% IQR %.1f-%.1f%%; "
             "overstatement (E-N)/N median %.1f%% IQR %.1f-%.1f%%",
             n_routes, spur["median"], spur["p25"], spur["p75"],
             over["median"], over["p25"], over["p75"])
    log.info("union: Euclid %s vs network %s: (E-N)/E %.1f%%, (E-N)/N %.1f%%; coverage "
             "%.2f%% -> %.2f%% of %s", f"{eu_union_pop:,.0f}", f"{net_union_pop:,.0f}",
             union["spurious_share_of_euclidean_pct"], union["overstatement_of_network_pct"],
             100 * union["coverage_share_euclid"], 100 * union["coverage_share_net"],
             f"{C.STUDY_AREA_POPULATION:,}")
    log.info("sensitivity: spurious-share median across %d settings %.1f-%.1f%%; settings "
             "below the headline: %s", sensitivity_summary["n_settings"],
             *sensitivity_summary["spurious_share_median_range_pct"], smaller)
    log.info("summary done")
    return out


# ── HEAVY: full rebuild ───────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tau", type=float, default=TAU_M)
    ap.add_argument("--tau-sweep", default=",".join(str(t) for t in TAU_SWEEP))
    ap.add_argument("--limit", type=int, default=0, help="debug: first N routes")
    ap.add_argument("--summary-only", action="store_true",
                    help="light: rebuild JSON/tables from the cached CSV, gpkg and a08a outputs; "
                         "never runs the graph Dijkstra")
    ap.add_argument("--engine-outputs-root", default=None,
                    help="optional: directory holding outputs_vX.Y.Z (e.g. E:/kash) to "
                         "re-run the external geometry-version diagnostic")
    args = ap.parse_args()
    if args.summary_only:
        sweep = [float(t) for t in args.tau_sweep.split(",")]
        run_summary(args.tau, sweep, args.engine_outputs_root)
        return
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
            log.info("  %d/%d routes", pos, len(utm))

    df = add_bias_columns(pd.DataFrame(rows), int(args.tau))

    C.DERIVED.mkdir(parents=True, exist_ok=True)
    df.to_csv(CATCH_CSV, index=False)

    # Persist network catchments (the summary path and the figures read them).
    try:
        gnet = gpd.GeoDataFrame(
            dict(New_Route_ID=list(geoms_net.keys())),
            geometry=[geoms_net[k] for k in geoms_net], crs=C.UTM)
        gnet.to_file(NET_GPKG, driver="GPKG")
    except Exception as exc:                                    # pragma: no cover
        log.warning("could not write catchment gpkg: %s", exc)

    # Everything that is reported (JSON, tables, sensitivity, reconciliation) is
    # produced by the same light path that can be re-run from cache.
    if not args.limit:
        run_summary(args.tau, [float(t) for t in args.tau_sweep.split(",")],
                    args.engine_outputs_root)


if __name__ == "__main__":
    main()
