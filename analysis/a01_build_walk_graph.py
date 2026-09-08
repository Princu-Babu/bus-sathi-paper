#!/usr/bin/env python
"""
a01_build_walk_graph.py — extract a pedestrian network for the study area.

Why this exists. The engine delineates each route's catchment as a union of
Euclidean discs around virtual stops (transit_kashmir_v3.py::build_catchments).
In Srinagar that is not a harmless simplification: straight-line discs cross
Dal, Nigeen and Anchar lakes and the Jhelum, crediting a route with population
that has no walking connection to it. Replacing Euclidean discs with
network-distance walksheds is the correction most likely to be demanded on
first read, so the walkshed needs a real pedestrian graph.

Source. OpenStreetMap, from the local `india-latest.osm.pbf` extract (header
bounding box 69.17–80.17 E, 23.05–36.14 N, so the study area is fully inside
it). Nothing is fetched over the network: the build is reproducible offline.

Method. One pass over the extract. Node coordinates are cached C++-side by
pyosmium's location store and attached to each way, while an entity filter and
a `highway` key filter keep the Python loop to candidate ways only. Ways are
clipped to the padded study bounding box, and edges are added between
consecutive in-box nodes so a way that leaves and re-enters the box never
produces a spurious chord. Edge length is geodesic metres. The result is an
undirected graph written to data/cache/walk_graph.gpickle.

Walkability rule. Ways whose `highway` value is in WALKABLE are kept.
Motorways and their links are excluded (no pedestrian access), as are ways
tagged foot=no or access=private/no. Footways, paths, steps, pedestrian
streets and tracks are kept: in this study area they carry a large share of
short-distance access, especially in the old city, and dropping them would
understate the network walkshed and so understate the very bias being measured.

Usage
    python analysis/a01_build_walk_graph.py --pbf E:/kash/india-latest.osm.pbf
"""
from __future__ import annotations

import argparse
import pickle
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("walkgraph")

WALKABLE = {
    "residential", "service", "unclassified", "road",
    "tertiary", "tertiary_link", "secondary", "secondary_link",
    "primary", "primary_link", "trunk", "trunk_link",
    "living_street", "pedestrian", "footway", "path", "track", "steps",
    "cycleway", "bridleway",
}
EXCLUDE_HIGHWAY = {"motorway", "motorway_link", "construction", "proposed",
                   "raceway", "bus_guideway", "escape", "corridor", "elevator",
                   "platform", "rest_area", "services", "bus_stop", "crossing",
                   "traffic_signals", "turning_circle", "street_lamp"}

BBOX_PAD_DEG = 0.05          # pad so walksheds near the boundary stay complete
EARTH_R_M = 6_371_008.8      # IUGG mean Earth radius


def study_bbox(pad: float = BBOX_PAD_DEG) -> tuple[float, float, float, float]:
    """(min_lon, min_lat, max_lon, max_lat) of the 10-district union, padded."""
    import geopandas as gpd
    d = gpd.read_file(C.DISTRICTS_GEOJSON)
    minx, miny, maxx, maxy = d.total_bounds
    return (minx - pad, miny - pad, maxx + pad, maxy + pad)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return float(2 * EARTH_R_M * np.arcsin(np.sqrt(min(max(a, 0.0), 1.0))))


def build(pbf: Path, bbox) -> "object":
    import networkx as nx
    import osmium

    minx, miny, maxx, maxy = bbox
    G = nx.Graph()
    t0 = time.time()
    n_seen = n_kept = 0

    fp = (osmium.FileProcessor(str(pbf))
          .with_locations()
          .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))
          .with_filter(osmium.filter.KeyFilter("highway")))

    for way in fp:
        n_seen += 1
        tags = way.tags
        hw = tags.get("highway", "")
        if hw not in WALKABLE or hw in EXCLUDE_HIGHWAY:
            continue
        if tags.get("foot") == "no" or tags.get("access") in ("private", "no"):
            continue

        prev = None                     # (id, lat, lon) of previous in-box node
        prev_adjacent = False
        used = False
        for nd in way.nodes:
            loc = nd.location
            if not loc.valid():
                prev, prev_adjacent = None, False
                continue
            lon, lat = loc.lon, loc.lat
            inside = (miny <= lat <= maxy) and (minx <= lon <= maxx)
            if not inside:
                prev, prev_adjacent = None, False
                continue
            nid = int(nd.ref)
            if nid not in G:
                G.add_node(nid, y=lat, x=lon)
            if prev is not None and prev_adjacent and prev[0] != nid:
                w = _haversine_m(prev[1], prev[2], lat, lon)
                if np.isfinite(w) and w > 0:
                    if G.has_edge(prev[0], nid):
                        if w < G[prev[0]][nid]["length"]:
                            G[prev[0]][nid]["length"] = w
                    else:
                        G.add_edge(prev[0], nid, length=w)
                    used = True
            prev, prev_adjacent = (nid, lat, lon), True
        if used:
            n_kept += 1
        if n_seen % 1_000_000 == 0:
            log.info("  %s highway ways scanned, %s walkable, graph %s nodes (%.0fs)",
                     f"{n_seen:,}", f"{n_kept:,}", f"{G.number_of_nodes():,}",
                     time.time() - t0)

    log.info("pass done: %s highway ways seen, %s contributed edges (%.0fs)",
             f"{n_seen:,}", f"{n_kept:,}", time.time() - t0)
    G.remove_nodes_from(list(nx.isolates(G)))
    total_km = sum(d["length"] for *_, d in G.edges(data=True)) / 1000.0
    log.info("graph: %s nodes, %s edges, %s km walkable network",
             f"{G.number_of_nodes():,}", f"{G.number_of_edges():,}",
             f"{total_km:,.0f}")
    return G


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pbf", default="E:/kash/india-latest.osm.pbf")
    ap.add_argument("--out", default=str(C.WALK_GRAPH_PKL))
    args = ap.parse_args()

    pbf = Path(args.pbf)
    if not pbf.exists():
        raise SystemExit(f"OSM extract not found: {pbf}")

    bbox = study_bbox()
    log.info("study bbox (padded %.2f deg): lon %.3f-%.3f  lat %.3f-%.3f",
             BBOX_PAD_DEG, bbox[0], bbox[2], bbox[1], bbox[3])

    G = build(pbf, bbox)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as fh:
        pickle.dump(G, fh, protocol=pickle.HIGHEST_PROTOCOL)
    log.info("walk graph -> %s (%.1f MB)", out, out.stat().st_size / 1e6)

    import networkx as nx
    comps = sorted((len(c) for c in nx.connected_components(G)), reverse=True)
    C.write_result(dict(
        source_pbf=str(pbf),
        source_pbf_bytes=pbf.stat().st_size,
        bbox=dict(min_lon=bbox[0], min_lat=bbox[1], max_lon=bbox[2], max_lat=bbox[3]),
        bbox_pad_deg=BBOX_PAD_DEG,
        n_nodes=G.number_of_nodes(),
        n_edges=G.number_of_edges(),
        network_km=sum(d["length"] for *_, d in G.edges(data=True)) / 1000.0,
        n_components=len(comps),
        largest_component_nodes=comps[0] if comps else 0,
        largest_component_share=(comps[0] / G.number_of_nodes()) if comps else 0.0,
        walkable_classes=sorted(WALKABLE),
        excluded_classes=sorted(EXCLUDE_HIGHWAY),
    ), "a01_walk_graph")


if __name__ == "__main__":
    main()
