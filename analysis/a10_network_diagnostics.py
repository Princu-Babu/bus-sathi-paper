#!/usr/bin/env python
"""
a10_network_diagnostics.py — §5.5: the route count falls, the road network does not.

The single most communicable result in the paper, and the one that decides
whether "rationalisation" reads as a euphemism for cuts. Going from 644 permit
routes to 186 sounds like removing service. It is only defensible if what was
removed was duplication — several permits grinding along the same tarmac — and
not reach. The statistic that separates those two readings is the ratio of
route-km to unique network-km: how many kilometres of scheduled route sit on
each kilometre of road that actually gets a bus.

Why this needs its own module rather than a line in a spreadsheet. Summing the
plan's `Route_KM` column gives route-km and nothing else; the denominator has
to come from geometry, because two routes on one road contribute two route-km
and one network-km, and no attribute column knows that. So every length here is
measured on the published geometry, projected to UTM 43N (common.UTM) because
degrees are not metres at 34 degrees north.

Two independent measurements of the same quantity, which is the point.
  * LINK method (primary). The published geometries are OSRM polylines drawn on
    one road graph, so two routes sharing a road share the *same vertices* —
    118,447 vertex occurrences collapse to 35,443 distinct positions. Each
    consecutive vertex pair is treated as an undirected link, keyed on its
    endpoints; unique network-km is the sum over distinct links, and link
    duplication is the number of distinct routes whose polyline contains that
    link. Exact: no tolerance, no buffer, and the identity
        sum over links of (duplication x length)  ==  total route-km
    closes to the kilometre, with the residual being routes that double back
    over a link they have already used.
  * UNION method (cross-check). shapely.unary_union over the same geometries,
    which nodes and dissolves them with no knowledge of the vertex keys, plus
    the same union after snapping coordinates to 0.5/1/2/5/10 m grids to show
    the figure is not an artefact of floating-point coincidence.
  If the two disagreed, the vertex-sharing premise would be wrong and the
  duplication counts with it. They are reported side by side for that reason.

The baseline, and what cannot be computed. The published GeoJSON carries the
186 active features only; the 458 MERGED_INTO_TRUNK rows have attributes but no
geometry, and the offline OSRM cache is a metadata stub with no coordinates in
it. Baseline route-km is therefore exact (the `Route_KM` column over all 644
rows) while baseline *unique network-km* is not computable from this release.
It is reported as NOT_COMPUTABLE with the two bounds that do follow — the
active union below it, since the active geometries are a subset of the baseline
set, and baseline route-km above it, the zero-overlap case — rather than
estimated. A straight-line chord network built from the permit register's own
coordinates is reported alongside as an explicitly labelled proxy: real
coordinates, real arithmetic, but chords are not roads, so its kilometres are
not comparable with the routed figures and its ratio is a floor on permit
duplication, not a measurement of it.

Outputs
    data/derived/a10_network_diagnostics.json
    paper/tables/table05c_network_diagnostics.{csv,md}

Usage
    python analysis/a10_network_diagnostics.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a10")

PRECISION_GRIDS_M = (0.5, 1.0, 2.0, 5.0, 10.0)   # union robustness snapping
DUP_THRESHOLD = 10          # "heavily duplicated": a road carrying >= 10 routes
DUP_BANDS = (1, 2, 3, 5, 10, 20)
TOP_CORRIDORS = 10


def link_network(geoms) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[set[int]], dict]:
    """
    Decompose routed polylines into a set of distinct undirected links.

    Returns (endpoint index array, link length m, duplication count, route-id
    sets, diagnostics). Coordinates are used as exact keys: the projection is
    applied to every route by the same transform, so a position shared in WGS84
    is shared in UTM bit-for-bit. A route that revisits a link is credited with
    it once, and the number of such revisits is returned so the route-km
    identity can be closed rather than waved at.
    """
    vertex_id: dict[tuple[float, float], int] = {}
    links: dict[tuple[int, int], set[int]] = {}
    route_km = np.zeros(len(geoms))
    repeats = 0
    repeat_m = 0.0

    for ri, geom in enumerate(geoms):
        idx = []
        for xy in geom.coords:
            key = (xy[0], xy[1])
            if key not in vertex_id:
                vertex_id[key] = len(vertex_id)
            idx.append(vertex_id[key])
        seen: set[tuple[int, int]] = set()
        coords = list(geom.coords)
        for pos, (a, b) in enumerate(zip(idx[:-1], idx[1:])):
            if a == b:                     # zero-length step in the polyline
                continue
            seg = float(np.hypot(coords[pos][0] - coords[pos + 1][0],
                                 coords[pos][1] - coords[pos + 1][1]))
            route_km[ri] += seg
            key = (a, b) if a < b else (b, a)
            if key in seen:
                repeats += 1
                repeat_m += seg
            seen.add(key)
            links.setdefault(key, set()).add(ri)

    keys = list(vertex_id)
    X = np.fromiter((k[0] for k in keys), dtype=float, count=len(keys))
    Y = np.fromiter((k[1] for k in keys), dtype=float, count=len(keys))
    ab = np.array(list(links), dtype=np.int64)
    length = np.hypot(X[ab[:, 0]] - X[ab[:, 1]], Y[ab[:, 0]] - Y[ab[:, 1]])
    members = list(links.values())
    count = np.fromiter((len(s) for s in members), dtype=np.int64, count=len(members))
    diag = dict(n_vertex_occurrences=int(sum(len(g.coords) for g in geoms)),
                n_distinct_vertices=len(vertex_id),
                n_distinct_links=len(links),
                self_repeated_link_traversals=repeats,
                self_repeated_km=repeat_m / 1000.0,
                route_km=route_km / 1000.0,
                vertex_x=X, vertex_y=Y)
    return ab, length, count, members, diag


def union_lengths(geoms) -> dict[str, float]:
    """Dissolved network length from shapely, natively and on snapped grids."""
    import shapely as sh
    from shapely.ops import unary_union
    out = {"native": float(unary_union(list(geoms)).length) / 1000.0}
    for g in PRECISION_GRIDS_M:
        snapped = [sh.set_precision(x, g) for x in geoms]
        out[f"grid_{g:g}m"] = float(unary_union(snapped).length) / 1000.0
    return out


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    """Quantile of `values` where each observation carries `weights` of mass."""
    order = np.argsort(values)
    v, w = values[order], weights[order]
    cum = np.cumsum(w) / w.sum()
    return float(v[np.searchsorted(cum, q)])


def nearest_stop(stops_xy: np.ndarray, stops: pd.DataFrame,
                 x: float, y: float) -> dict:
    """
    Name a location by the closest stop in the plan's own stop register.

    Corridors have no names in the data, only routes do, so a corridor is
    identified by the nearest entry in Kashmir_Stops_Master_v4 together with the
    distance to it — which is reported so a 4 km "nearest" stop is not mistaken
    for a precise label.
    """
    d = np.hypot(stops_xy[:, 0] - x, stops_xy[:, 1] - y)
    j = int(d.argmin())
    return dict(nearest_stop=str(stops.iloc[j]["Stop_Name"]),
                district=str(stops.iloc[j]["District"]),
                distance_to_stop_m=round(float(d[j]), 1))


def main() -> None:
    import geopandas as gpd
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    # ── active network geometry ───────────────────────────────────────────────
    gdf = gpd.read_file(C.PLAN_GEOJSON).to_crs(C.UTM)
    plan = C.load_plan()
    active = plan[plan["Action_Taken"].isin(C.ACTIVE_ACTIONS)]
    merged = plan[plan["Action_Taken"] == C.MERGED_ACTION]
    log.info("geojson features %d | plan rows %d (active %d, merged %d)",
             len(gdf), len(plan), len(active), len(merged))
    if len(gdf) != len(active):
        log.warning("geojson feature count %d != active plan rows %d",
                    len(gdf), len(active))

    names = gdf["Route_Name"].astype(str).tolist()
    ids = gdf["New_Route_ID"].astype(str).tolist()

    ab, link_m, dup, members, diag = link_network(list(gdf.geometry))
    total_route_km = float(diag["route_km"].sum())
    network_km = float(link_m.sum()) / 1000.0
    ratio = total_route_km / network_km

    # The identity that makes the duplication counts auditable.
    attributed_km = float((dup * link_m).sum()) / 1000.0
    residual_km = total_route_km - attributed_km - diag["self_repeated_km"]
    log.info("links: %d vertex occurrences -> %d distinct vertices -> %d links",
             diag["n_vertex_occurrences"], diag["n_distinct_vertices"],
             diag["n_distinct_links"])
    log.info("route-km %.3f | unique network-km %.3f | RATIO %.4f : 1",
             total_route_km, network_km, ratio)
    log.info("reconciliation: sum(dup x len) %.3f + self-repeats %.3f = %.3f "
             "(residual %.6f km)", attributed_km, diag["self_repeated_km"],
             attributed_km + diag["self_repeated_km"], residual_km)
    if abs(residual_km) > 1e-6:
        log.warning("route-km identity does not close exactly (%.6f km)", residual_km)

    union_km = union_lengths(list(gdf.geometry))
    union_gap_pct = 100.0 * (union_km["native"] - network_km) / network_km
    log.info("union cross-check: native %.3f km (%.4f%% vs link method); "
             "snapped %s", union_km["native"], union_gap_pct,
             {k: round(v, 1) for k, v in union_km.items() if k != "native"})

    # Published Route_KM vs measured geometry: the v3.4.4 corrections substituted
    # audited road km on some routes without redrawing the line, so the two are
    # not required to be identical and the gap is reported instead of hidden.
    km_attr = float(gdf["Route_KM"].sum())
    log.info("published Route_KM (active) %.3f vs measured geometry %.3f "
             "(%.3f%% apart)", km_attr, total_route_km,
             100.0 * (km_attr - total_route_km) / total_route_km)

    # ── duplication distribution ──────────────────────────────────────────────
    w = link_m / link_m.sum()
    dist = dict(
        n_links=int(len(dup)),
        mean_routes_per_link=float(dup.mean()),
        median_routes_per_link=float(np.median(dup)),
        p90_routes_per_link=float(np.percentile(dup, 90)),
        max_routes_per_link=int(dup.max()),
        km_weighted_mean=float((dup * w).sum()),
        km_weighted_median=weighted_quantile(dup.astype(float), link_m, 0.50),
        km_weighted_p90=weighted_quantile(dup.astype(float), link_m, 0.90),
    )
    bands = {}
    for b in DUP_BANDS:
        sel = dup >= b
        bands[f">={b}_routes"] = dict(
            network_km=round(float(link_m[sel].sum()) / 1000.0, 3),
            share_of_network=round(float(link_m[sel].sum() / link_m.sum()), 6),
            n_links=int(sel.sum()))
    sole = dup == 1
    dist["sole_served_network_km"] = round(float(link_m[sole].sum()) / 1000.0, 3)
    dist["sole_served_share"] = round(float(link_m[sole].sum() / link_m.sum()), 6)
    log.info("duplication: mean %.3f, median %.0f, p90 %.0f, max %d routes per "
             "link; km-weighted mean %.3f (median %.0f, p90 %.0f)",
             dist["mean_routes_per_link"], dist["median_routes_per_link"],
             dist["p90_routes_per_link"], dist["max_routes_per_link"],
             dist["km_weighted_mean"], dist["km_weighted_median"],
             dist["km_weighted_p90"])
    log.info("%.1f%% of network-km is sole-served; %.1f%% carries >=%d routes",
             100 * dist["sole_served_share"],
             100 * bands[f">={DUP_THRESHOLD}_routes"]["share_of_network"],
             DUP_THRESHOLD)

    # ── naming the duplicated corridors ───────────────────────────────────────
    stops = pd.read_csv(C.STOPS_MASTER)
    sg = gpd.GeoDataFrame(
        stops, geometry=gpd.points_from_xy(stops["Longitude"], stops["Latitude"]),
        crs=C.WGS84).to_crs(C.UTM)
    stops_xy = np.column_stack([sg.geometry.x, sg.geometry.y])
    X, Y = diag["vertex_x"], diag["vertex_y"]
    mid_x = (X[ab[:, 0]] + X[ab[:, 1]]) / 2.0
    mid_y = (Y[ab[:, 0]] + Y[ab[:, 1]]) / 2.0

    def corridors(threshold: int) -> list[dict]:
        """Contiguous runs of links carrying at least `threshold` routes."""
        sel = np.where(dup >= threshold)[0]
        if sel.size == 0:
            return []
        nodes = np.unique(ab[sel])
        remap = {int(v): i for i, v in enumerate(nodes)}
        rows = [remap[int(v)] for v in ab[sel, 0]]
        cols = [remap[int(v)] for v in ab[sel, 1]]
        adj = coo_matrix((np.ones(len(sel)), (rows, cols)),
                         shape=(len(nodes), len(nodes)))
        _, comp = connected_components(adj, directed=False)
        comp_of = {int(i): int(comp[remap[int(ab[i, 0])]]) for i in sel}
        out = []
        for c in sorted(set(comp_of.values())):
            li = [i for i in sel if comp_of[int(i)] == c]
            km = float(link_m[li].sum()) / 1000.0
            peak = int(dup[li].max())
            loc = nearest_stop(stops_xy, stops,
                               float(np.mean(mid_x[li])), float(np.mean(mid_y[li])))
            out.append(dict(km=round(km, 3), n_links=len(li), peak_routes=peak,
                            **loc))
        return sorted(out, key=lambda r: -r["km"])

    top = corridors(DUP_THRESHOLD)[:TOP_CORRIDORS]
    peak_links = np.where(dup == dup.max())[0]
    peak_routes = sorted(set().union(*[members[int(i)] for i in peak_links]))
    peak_loc = nearest_stop(stops_xy, stops,
                            float(np.mean(mid_x[peak_links])),
                            float(np.mean(mid_y[peak_links])))
    most_duplicated = dict(
        routes_on_corridor=int(dup.max()),
        share_of_active_routes=round(float(dup.max()) / len(gdf), 4),
        corridor_km=round(float(link_m[peak_links].sum()) / 1000.0, 4),
        n_links=int(len(peak_links)),
        **peak_loc,
        route_ids=[ids[i] for i in peak_routes],
        route_names=[names[i] for i in peak_routes],
    )
    log.info("most-duplicated corridor: %d of %d routes over %.3f km near %s "
             "(%s, %.0f m away)", most_duplicated["routes_on_corridor"], len(gdf),
             most_duplicated["corridor_km"], most_duplicated["nearest_stop"],
             most_duplicated["district"], most_duplicated["distance_to_stop_m"])
    for c in top[:5]:
        log.info("  corridor >=%d routes: %7.3f km  peak %2d  near %s (%s, %.0f m)",
                 DUP_THRESHOLD, c["km"], c["peak_routes"], c["nearest_stop"],
                 c["district"], c["distance_to_stop_m"])

    # ── baseline: what the 644-row permit layer looked like ───────────────────
    baseline_route_km = float(plan["Route_KM"].sum())
    merged_route_km = float(merged["Route_KM"].sum())
    baseline = dict(
        n_rows=int(len(plan)),
        n_active=int(len(active)),
        n_merged=int(len(merged)),
        total_route_km=round(baseline_route_km, 3),
        total_route_km_source="Route_KM column, all 644 rows of the plan CSV",
        merged_route_km=round(merged_route_km, 3),
        unique_network_km=dict(
            status="NOT_COMPUTABLE",
            reason=("the published GeoJSON carries only the 186 active features; "
                    "the 458 MERGED_INTO_TRUNK rows have attributes but no "
                    "geometry, and data/cache/osrm_responses.json is a metadata "
                    "stub with no coordinates, so the baseline union cannot be "
                    "dissolved from this release"),
            lower_bound_km=round(network_km, 3),
            lower_bound_basis=("the 186 active geometries are a subset of the "
                               "644-row baseline, so the baseline union contains "
                               "the active union"),
            upper_bound_km=round(baseline_route_km, 3),
            upper_bound_basis="baseline route-km, the zero-overlap case",
        ),
        route_count_reduction=round(1 - len(active) / len(plan), 4),
        route_km_reduction=round(1 - total_route_km / baseline_route_km, 4),
        merged_rows_with_active_successor=int(
            merged["New_Route_ID"].isin(set(active["New_Route_ID"])).sum()),
        n_distinct_successors=int(merged["New_Route_ID"].nunique()),
    )
    log.info("baseline: %d rows, route-km %.3f; unique network-km NOT_COMPUTABLE "
             "(bounds %.1f - %.1f km)", baseline["n_rows"],
             baseline["total_route_km"],
             baseline["unique_network_km"]["lower_bound_km"],
             baseline["unique_network_km"]["upper_bound_km"])
    log.info("consolidation: route count -%.1f%%, route-km -%.1f%%; %d/%d merged "
             "rows resolve to an active successor (%d distinct survivors)",
             100 * baseline["route_count_reduction"],
             100 * baseline["route_km_reduction"],
             baseline["merged_rows_with_active_successor"], len(merged),
             baseline["n_distinct_successors"])

    # ── permit-register chord proxy (explicitly not a road network) ───────────
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    permits = pd.read_csv(C.PERMITS_CSV)
    chords, dropped = [], 0
    for _, r in permits.iterrows():
        pts = [(r["Origin_Lon"], r["Origin_Lat"])]
        via = r.get("Via_Points_Geocoded")
        if isinstance(via, str) and via.strip():
            try:
                lat, lon = (float(x) for x in via.split(",")[:2])
                pts.append((lon, lat))
            except ValueError:
                pass
        pts.append((r["Dest_Lon"], r["Dest_Lat"]))
        if any(not np.isfinite(c) for p in pts for c in p):
            dropped += 1
            continue
        chords.append(pts)
    cg = gpd.GeoSeries([LineString(p) for p in chords], crs=C.WGS84).to_crs(C.UTM)
    cg = gpd.GeoSeries([LineString(dict.fromkeys(g.coords)) for g in cg
                        if len(dict.fromkeys(g.coords)) >= 2], crs=C.UTM)
    chord_total = float(cg.length.sum()) / 1000.0
    chord_union = float(unary_union(list(cg)).length) / 1000.0
    distinct_chords = len({tuple(g.coords) for g in cg})
    permit_proxy = dict(
        status="PROXY_STRAIGHT_LINE",
        caveat=("origin -> via -> destination chords from the permit register's "
                "own coordinates. Chords are not road alignments, so these "
                "kilometres are NOT comparable with the routed figures above; "
                "and two permits along one road with different intermediate "
                "stops produce different chords, so the ratio is a floor on "
                "permit duplication rather than a measurement of it"),
        n_permits=int(len(permits)),
        n_chords_built=int(len(cg)),
        n_permits_dropped_bad_coords=int(dropped),
        n_distinct_chord_geometries=int(distinct_chords),
        exact_duplicate_share=round(1 - distinct_chords / len(cg), 4),
        total_chord_km=round(chord_total, 3),
        union_chord_km=round(chord_union, 3),
        chord_km_ratio=round(chord_total / chord_union, 4),
    )
    log.info("permit chord proxy: %d permits -> %d distinct chord geometries "
             "(%.1f%% exact duplicates); %.1f chord-km over %.1f union-km "
             "= %.3f : 1", permit_proxy["n_permits"], distinct_chords,
             100 * permit_proxy["exact_duplicate_share"], chord_total,
             chord_union, permit_proxy["chord_km_ratio"])

    # ── table ─────────────────────────────────────────────────────────────────
    tab = pd.DataFrame([
        dict(quantity="Active routes carrying service", value=len(gdf),
             unit="routes", status="COMPUTED", basis="GeoJSON features"),
        dict(quantity="Baseline permit-routes", value=len(plan),
             unit="routes", status="COMPUTED", basis="plan CSV, all rows"),
        dict(quantity="Route-km, active network", value=round(total_route_km, 1),
             unit="km", status="COMPUTED", basis="geometry length, UTM 43N"),
        dict(quantity="Route-km, baseline", value=round(baseline_route_km, 1),
             unit="km", status="COMPUTED", basis="Route_KM column, all rows"),
        dict(quantity="Unique network-km, active",
             value=round(network_km, 1), unit="km", status="COMPUTED",
             basis="distinct OSRM links (union cross-check "
                   f"{union_km['native']:.1f} km)"),
        dict(quantity="Unique network-km, baseline", value=None, unit="km",
             status="NOT_COMPUTABLE",
             basis=f"no geometry for the {len(merged)} merged rows; bounded to "
                   f"[{network_km:.1f}, {baseline_route_km:.1f}] km"),
        dict(quantity="Route-km : network-km, active", value=round(ratio, 3),
             unit="ratio", status="COMPUTED",
             basis="headline duplication statistic"),
        dict(quantity="Mean routes per network link",
             value=round(dist["mean_routes_per_link"], 3), unit="routes",
             status="COMPUTED", basis=f"{dist['n_links']} distinct links"),
        dict(quantity="Mean routes per network-km (km-weighted)",
             value=round(dist["km_weighted_mean"], 3), unit="routes",
             status="COMPUTED", basis="weighted by link length"),
        dict(quantity="Median routes per network-km (km-weighted)",
             value=dist["km_weighted_median"], unit="routes", status="COMPUTED",
             basis="weighted by link length"),
        dict(quantity="90th percentile routes per network-km (km-weighted)",
             value=dist["km_weighted_p90"], unit="routes", status="COMPUTED",
             basis="weighted by link length"),
        dict(quantity="Maximum routes on one link",
             value=dist["max_routes_per_link"], unit="routes", status="COMPUTED",
             basis=f"{most_duplicated['nearest_stop']}, "
                   f"{most_duplicated['district']}"),
        dict(quantity="Network-km served by exactly one route",
             value=dist["sole_served_network_km"], unit="km", status="COMPUTED",
             basis=f"{100 * dist['sole_served_share']:.1f}% of the network"),
        dict(quantity=f"Network-km carrying >= {DUP_THRESHOLD} routes",
             value=bands[f">={DUP_THRESHOLD}_routes"]["network_km"], unit="km",
             status="COMPUTED",
             basis=f"{100 * bands[f'>={DUP_THRESHOLD}_routes']['share_of_network']:.1f}%"
                   " of the network"),
        dict(quantity="Permit chords, distinct geometries",
             value=permit_proxy["n_distinct_chord_geometries"], unit="chords",
             status="PROXY_STRAIGHT_LINE",
             basis=f"of {permit_proxy['n_chords_built']} permits; chords are not "
                   "road alignments"),
    ])
    # The one NOT_COMPUTABLE row has no value by construction; render it blank
    # rather than as "nan", which reads like a failed computation instead of a
    # quantity the published release cannot support.
    tab["value"] = tab["value"].astype(object).where(tab["value"].notna(), "")
    C.write_table(tab, "table05c_network_diagnostics",
                  "Network diagnostics for the rationalised plan: route-km "
                  "against unique network-km, link duplication, and the "
                  "baseline quantities that the published release does and "
                  "does not support")

    payload = dict(
        crs=C.UTM,
        active=dict(
            n_routes=int(len(gdf)),
            total_route_km=round(total_route_km, 3),
            total_route_km_published_attribute=round(km_attr, 3),
            published_vs_measured_pct=round(
                100.0 * (km_attr - total_route_km) / total_route_km, 4),
            unique_network_km=round(network_km, 3),
            route_km_to_network_km_ratio=round(ratio, 4),
            method="undirected OSRM-link decomposition (exact, no tolerance)",
            n_vertex_occurrences=diag["n_vertex_occurrences"],
            n_distinct_vertices=diag["n_distinct_vertices"],
            n_distinct_links=diag["n_distinct_links"],
            reconciliation=dict(
                attributed_km=round(attributed_km, 4),
                self_repeated_link_traversals=diag["self_repeated_link_traversals"],
                self_repeated_km=round(diag["self_repeated_km"], 4),
                residual_km=round(residual_km, 8),
                identity="sum(duplication x link length) + self-repeats = route-km",
            ),
            union_cross_check_km={k: round(v, 3) for k, v in union_km.items()},
            union_vs_link_pct=round(union_gap_pct, 4),
        ),
        duplication=dict(distribution=dist, bands=bands,
                         most_duplicated_corridor=most_duplicated,
                         threshold_for_corridors=DUP_THRESHOLD,
                         top_corridors=top),
        baseline=baseline,
        permit_chord_proxy=permit_proxy,
        random_seed=C.RANDOM_SEED,
    )
    C.write_result(payload, "a10_network_diagnostics")
    log.info("wrote a10_network_diagnostics.json and table05c_network_diagnostics")


if __name__ == "__main__":
    main()
