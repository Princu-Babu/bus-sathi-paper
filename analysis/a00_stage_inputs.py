#!/usr/bin/env python
"""
a00_stage_inputs.py — freeze every input the paper depends on into data/raw.

Rationale. The engine repo (E:\\kash) is a working tree that keeps moving. A
reproducibility artefact must pin the exact bytes the published numbers were
computed from, so this script copies inputs in and records a SHA-256 manifest.
Re-running it on an unchanged source tree is a no-op apart from the manifest
timestamp.

It also builds an OFFLINE OSRM CACHE. The engine calls a local OSRM server for
every route geometry; that server is not part of the artefact and cannot be
assumed available to a reviewer. Route geometry and drive duration are already
determined in the published plan, so we extract them into
data/cache/osrm_responses.json keyed by Route_ID. Every downstream analysis
reads the cache, never the network.

Usage
    python analysis/a00_stage_inputs.py --engine E:/kash --gps E:/bus-sathi-trace
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("stage")

# (source relative to engine root, destination relative to data/raw, description)
ENGINE_FILES: list[tuple[str, str, str]] = [
    ("outputs_v3.4.5/Rationalised_Routes_Kashmir_v3.csv",
     "Rationalised_Routes_Kashmir_v3.csv",
     "Published rationalised plan, engine v3.4.5-geo: 644 permit-routes × 55 fields"),
    ("outputs_v3.4.5/Rationalised_Routes_Kashmir_v3.geojson",
     "Rationalised_Routes_Kashmir_v3.geojson",
     "Routed geometry of the 186 active routes"),
    ("outputs_v3.4.5/Rationalisation_Log_Kashmir_v3.csv",
     "Rationalisation_Log_Kashmir_v3.csv",
     "Per-route disposition reasoning"),
    ("existing-routes.csv", "existing-routes.csv",
     "Permit register as geocoded: origin, destination, via, operator class"),
    ("pois.csv", "pois.csv",
     "Points of interest from OpenStreetMap, tiered by attraction class"),
    ("kashmir_worldpop.tif", "kashmir_worldpop.tif",
     "WorldPop 2026 UN-adjusted population, 100 m grid, clipped to study bbox"),
    ("kashmir_districts_osm.geojson", "kashmir_districts_osm.geojson",
     "OSM admin_level 5 district boundaries, 10 districts"),
    ("kashmir_tehsils_osm.geojson", "kashmir_tehsils_osm.geojson",
     "OSM admin_level 6 tehsil boundaries, 39 tehsils"),
    ("Kashmir_Stops_Master_v4.csv", "Kashmir_Stops_Master_v4.csv",
     "Canonical stop registry, 126 stops, district and tehsil by point-in-polygon"),
    ("Hourly Passenger Count.csv", "Hourly_Passenger_Count.csv",
     "Observed hourly boardings, e-bus system, 1–30 April 2026"),
    ("Ridership Data.csv", "chalo_ridership.csv",
     "Monthly e-bus ridership and operated km, FY 2025-26"),
    ("Route Wise deployed Buses.csv", "chalo_deployed_buses.csv",
     "Buses deployed per e-bus route, by vehicle length"),
    ("ROUTE_DEEPDIVE_LEDGER.csv", "ROUTE_DEEPDIVE_LEDGER.csv",
     "Per-route real-world distance and service audit with cited sources"),
]

GPS_FILES: list[tuple[str, str, str]] = [
    ("data/reality_check.csv", "gps/reality_check.csv",
     "Planned vs measured one-way time, matched corridors"),
    ("data/corridor_profiles.csv", "gps/corridor_profiles.csv",
     "Per-corridor moving speed, effective speed and dwell share from GPS"),
    ("data/route_evidence.csv", "gps/route_evidence.csv",
     "Share of each planned route's length observed in GPS runs"),
    ("data/permit_observed.csv", "gps/permit_observed.csv",
     "Observation status per permit route"),
    ("data/geometry_divergence.csv", "gps/geometry_divergence.csv",
     "Corridors where observed path diverges from the routed line"),
    ("data/driver_days.csv", "gps/driver_days.csv",
     "Driver-day activity used to establish the service window"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_set(root: Path, spec: list[tuple[str, str, str]],
             manifest: list[dict], label: str) -> int:
    copied = 0
    for src_rel, dst_rel, desc in spec:
        src = root / src_rel
        dst = C.RAW / dst_rel
        if not src.exists():
            log.warning("MISSING  %s (%s) — skipped", src_rel, label)
            manifest.append(dict(file=dst_rel, status="MISSING", source=str(src),
                                 description=desc))
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
        manifest.append(dict(
            file=dst_rel, status="ok", source=str(src), description=desc,
            bytes=dst.stat().st_size, sha256=sha256(dst),
            source_mtime=datetime.fromtimestamp(
                src.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds"),
        ))
        log.info("staged   %-46s %9d B", dst_rel, dst.stat().st_size)
    return copied


def build_osrm_cache() -> dict:
    """
    Extract routed geometry and drive duration per route from the published
    plan into a standalone cache, so the pipeline never needs a live OSRM.
    """
    import geopandas as gpd
    import pandas as pd

    gdf = gpd.read_file(C.PLAN_GEOJSON)
    plan = pd.read_csv(C.PLAN_CSV)
    # The published geometry file carries only the 186 active routes and keys
    # them by New_Route_ID (the operational code, e.g. FDR-059); the plan CSV
    # keys every permit-route by the internal Route_ID. New_Route_ID is unique
    # across active routes, so it is the join key here.
    act = plan[plan["Action_Taken"].isin(C.ACTIVE_ACTIONS)]
    dur = act.set_index("New_Route_ID")["OSRM_Duration_S"].to_dict()
    km = act.set_index("New_Route_ID")["Route_KM"].to_dict()
    internal = act.set_index("New_Route_ID")["Route_ID"].to_dict()

    cache: dict[str, dict] = {}
    for _, row in gdf.iterrows():
        rid = row.get("New_Route_ID")
        geom = row.geometry
        if rid is None or geom is None or geom.is_empty:
            continue
        coords = [[round(x, 6), round(y, 6)] for x, y in geom.coords]
        cache[str(rid)] = dict(
            route_id=str(rid),
            internal_id=str(internal.get(rid, "")),
            distance_m=float(km.get(rid, 0.0)) * 1000.0,
            duration_s=float(dur.get(rid, 0.0)),
            coordinates=coords,
        )
    path = C.OSRM_CACHE_JSON
    with path.open("w", encoding="utf-8") as fh:
        json.dump(dict(
            note=("Offline OSRM cache. Geometry and duration extracted from the "
                  "published plan so the analysis reproduces without a routing "
                  "server. Keyed by Route_ID; coordinates are lon,lat WGS84."),
            engine_version="v3.4.5-geo",
            n_routes=len(cache),
            routes=cache,
        ), fh)
    log.info("OSRM cache: %d routes → %s", len(cache), path.name)
    return dict(n_routes=len(cache), path=str(path), sha256=sha256(path))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="E:/kash",
                    help="Engine repository root")
    ap.add_argument("--gps", default="E:/bus-sathi-trace",
                    help="GPS trace-intelligence repository root")
    args = ap.parse_args()

    C.RAW.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    n_eng = copy_set(Path(args.engine), ENGINE_FILES, manifest, "engine")
    n_gps = copy_set(Path(args.gps), GPS_FILES, manifest, "gps")
    osrm = build_osrm_cache()

    payload = dict(
        generated_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        engine_root=str(args.engine),
        gps_root=str(args.gps),
        engine_version="v3.4.5-geo",
        n_engine_files=n_eng,
        n_gps_files=n_gps,
        osrm_cache=osrm,
        files=manifest,
    )
    out = C.DATA / "MANIFEST.json"
    with out.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    log.info("Manifest → %s  (%d engine + %d gps files)", out, n_eng, n_gps)

    missing = [m["file"] for m in manifest if m["status"] == "MISSING"]
    if missing:
        log.warning("%d input(s) missing: %s", len(missing), ", ".join(missing))


if __name__ == "__main__":
    main()
