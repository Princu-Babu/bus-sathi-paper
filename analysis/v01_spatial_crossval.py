#!/usr/bin/env python
"""
v01_spatial_crossval.py — validation channel V1: does the population surface the
whole plan rests on agree with an independently mapped layer of where people
live (building footprints)?

What it can establish. Every coverage and demand-index figure in the paper is a
zonal sum of the WorldPop raster. If the raster put people where there are no
buildings (or missed built-up areas), coverage and tiers would inherit the error.
Building footprints are a physical record of settlement, so agreement between
the two surfaces — at the route-catchment scale the plan uses and on a regular
grid — is evidence that the raster places population plausibly. The
pre-registered target is Spearman rho > 0.60.

Two footprint sources, reported side by side:
  osm        OpenStreetMap closed building ways from the local India extract
             (volunteered; uneven completeness).
  microsoft  Microsoft Global ML Building Footprints (2026-02 release, ODbL),
             machine-detected from satellite imagery — near-complete coverage,
             independent of volunteer effort. This is the primary V1 source when
             present (data/external/ms_buildings/*.csv.gz, fetched per quadkey).

What it cannot establish, stated before the result.
  1. Partial circularity. WorldPop's constrained/top-down models use building
     footprints as a covariate when distributing census totals, so agreement is
     expected by construction to some degree — more so for a machine-detected
     layer of the kind such models ingest. V1 is a consistency check on the
     spatial pattern, not an independent validation of population counts.
  2. Completeness. The share of populated grid cells with any footprint is
     reported by district for each source, so a weak correlation can be read as
     a mapping gap rather than a raster error, and vice versa.
  3. OSM: closed building ways only; multipolygon relations not assembled.
     Microsoft: detection errors (false positives on rock/snow, misses under
     canopy) are not corrected.

Method.
  Each footprint is reduced to its centroid and planar area (shoelace formula on
  a local equirectangular projection).
  (a) Route scale: for each of the 186 network catchments (a02, W = 400 m),
      building count and footprint area inside, against catchment population.
  (b) Grid scale: ~1 km cells over the 10-district union; WorldPop sum against
      building footprint area per cell, all cells and populated cells only.

Inputs
    E:/kash/india-latest.osm.pbf (or --pbf); data/external/ms_buildings/*.csv.gz;
    data/cache/catchments_network.gpkg; data/derived/a02_catchments.csv;
    data/raw/kashmir_worldpop.tif
Outputs
    data/cache/osm_buildings_kashmir.csv, data/cache/ms_buildings_kashmir.csv.gz
    data/derived/v01_spatial_crossval.json
    data/derived/v01_route_buildings_<source>.csv
    paper/tables/table06d_v01_buildings.{csv,md}
    paper/tables/table06e_v01_completeness.{csv,md}
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("v01")

RHO_TARGET = 0.60
CELL_M = 1000.0
OSM_CSV = C.CACHE / "osm_buildings_kashmir.csv"
MS_DIR = C.DATA / "external" / "ms_buildings"
MS_CSV = C.CACHE / "ms_buildings_kashmir.csv.gz"
EARTH_R_M = 6_371_008.8


def _centroid_area(coords) -> tuple[float, float, float]:
    a = np.asarray(coords, float)
    if len(a) < 4:
        return np.nan, np.nan, np.nan
    clon, clat = a[:-1, 0].mean(), a[:-1, 1].mean()
    x = np.radians(a[:, 0] - clon) * EARTH_R_M * np.cos(np.radians(clat))
    y = np.radians(a[:, 1] - clat) * EARTH_R_M
    return clat, clon, 0.5 * abs(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1]))


def extract_osm(pbf: Path) -> pd.DataFrame:
    import osmium
    from a01_build_walk_graph import study_bbox

    minx, miny, maxx, maxy = study_bbox()
    fp = (osmium.FileProcessor(str(pbf))
          .with_locations()
          .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))
          .with_filter(osmium.filter.KeyFilter("building")))
    rows, seen, t0 = [], 0, time.time()
    for way in fp:
        seen += 1
        try:
            pts = [(n.location.lon, n.location.lat) for n in way.nodes if n.location.valid()]
        except Exception:
            continue
        if len(pts) < 4 or pts[0] != pts[-1]:
            continue
        clat, clon, area = _centroid_area(pts)
        if minx <= clon <= maxx and miny <= clat <= maxy:
            rows.append((clat, clon, area))
    log.info("OSM: %s footprints in bbox from %s building ways (%.0fs)", f"{len(rows):,}",
             f"{seen:,}", time.time() - t0)
    return pd.DataFrame(rows, columns=["lat", "lon", "area_m2"])


def ms_tiles_complete() -> bool:
    """True only if every tile in kashmir_tiles.csv is present and a valid gzip stream."""
    index = MS_DIR / "kashmir_tiles.csv"
    if not index.exists():
        return False
    tiles = pd.read_csv(index, dtype={"QuadKey": str})
    for _, t in tiles.iterrows():
        f = MS_DIR / f"{t['Location']}_{t['QuadKey']}.csv.gz"
        if not f.exists():
            return False
        try:
            with gzip.open(f, "rb") as fh:
                while fh.read(1 << 22):
                    pass
        except (EOFError, OSError):
            return False
    return True


def extract_ms() -> pd.DataFrame:
    """Stream every downloaded Microsoft tile (GeoJSON-lines, gzipped) once."""
    from a01_build_walk_graph import study_bbox

    minx, miny, maxx, maxy = study_bbox()
    files = sorted(MS_DIR.glob("*.csv.gz"))
    if not files:
        raise FileNotFoundError(f"no Microsoft tiles in {MS_DIR}")
    rows, seen, t0 = [], 0, time.time()
    for f in files:
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                seen += 1
                g = json.loads(line)["geometry"]
                ring = g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"][0][0]
                clat, clon, area = _centroid_area(ring)
                if minx <= clon <= maxx and miny <= clat <= maxy:
                    rows.append((clat, clon, area))
        log.info("  %s: cumulative %s kept of %s read (%.0fs)", f.name, f"{len(rows):,}",
                 f"{seen:,}", time.time() - t0)
    return pd.DataFrame(rows, columns=["lat", "lon", "area_m2"])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def analyse(label: str, b: pd.DataFrame, ctx: dict) -> tuple[dict, list, pd.DataFrame]:
    import geopandas as gpd
    from rasterio.features import rasterize
    from scipy.stats import spearmanr

    union, pop, mask, tr, crs, cat, a02, f, H, W = (ctx[k] for k in
        ("union", "pop", "mask", "tr", "crs", "cat", "a02", "f", "H", "W"))
    bg = gpd.GeoDataFrame(b, geometry=gpd.points_from_xy(b["lon"], b["lat"]), crs=C.WGS84)
    bg = bg[bg.within(union)].to_crs(C.UTM)
    log.info("%s: %s footprints inside the union (%.1f km2)", label, f"{len(bg):,}",
             bg["area_m2"].sum() / 1e6)

    # (a) route scale
    j = gpd.sjoin(bg[["area_m2", "geometry"]], cat[["New_Route_ID", "geometry"]],
                  predicate="within", how="inner")
    agg = j.groupby("New_Route_ID").agg(n_buildings=("area_m2", "size"),
                                        footprint_m2=("area_m2", "sum")).reset_index()
    rt = a02.merge(agg, on="New_Route_ID", how="left").fillna({"n_buildings": 0, "footprint_m2": 0})
    rt.to_csv(C.DERIVED / f"v01_route_buildings_{label}.csv", index=False)
    rho_area, p_area = spearmanr(rt["pop_net"], rt["footprint_m2"])
    rho_n, p_n = spearmanr(rt["pop_net"], rt["n_buildings"])

    # (b) grid scale
    bw = bg.to_crs(crs)
    col, row = ~tr * (bw.geometry.x.to_numpy(), bw.geometry.y.to_numpy())
    col, row = np.floor(col).astype(int), np.floor(row).astype(int)
    ok = (row >= 0) & (row < pop.shape[0]) & (col >= 0) & (col < pop.shape[1])
    fp_grid = np.zeros_like(pop)
    np.add.at(fp_grid, (row[ok], col[ok]), bw["area_m2"].to_numpy()[ok])
    P = pop[:H, :W].reshape(H // f, f, W // f, f).sum(axis=(1, 3))
    B = fp_grid[:H, :W].reshape(H // f, f, W // f, f).sum(axis=(1, 3))
    M = mask[:H, :W].reshape(H // f, f, W // f, f).any(axis=(1, 3))
    Pc, Bc = P[M], B[M]
    rho_g, p_g = spearmanr(Pc, Bc)
    popd = Pc > 1.0
    rho_gp, p_gp = spearmanr(Pc[popd], Bc[popd])
    pop_in_mapped = float(Pc[Bc > 0].sum() / Pc.sum())

    comp = []
    for name, dmask in ctx["district_masks"]:
        Pd = np.where(dmask[:H, :W], pop[:H, :W], 0).reshape(H // f, f, W // f, f).sum(axis=(1, 3))
        sel = Pd > 1.0
        comp.append(dict(source=label, district=name, populated_cells=int(sel.sum()),
                         share_cells_with_buildings=float((B[sel] > 0).mean()) if sel.any() else np.nan,
                         share_pop_in_mapped_cells=float(Pd[sel & (B > 0)].sum() / Pd[sel].sum())
                         if sel.any() else np.nan))

    rows = [
        dict(Source=label, Scale="Route catchment (n = 186)", Measure="footprint area",
             rho=round(rho_area, 3), p=f"{p_area:.1e}", Pass=bool(rho_area > RHO_TARGET)),
        dict(Source=label, Scale="Route catchment (n = 186)", Measure="building count",
             rho=round(rho_n, 3), p=f"{p_n:.1e}", Pass=bool(rho_n > RHO_TARGET)),
        dict(Source=label, Scale=f"1 km grid, all cells (n = {len(Pc):,})", Measure="footprint area",
             rho=round(rho_g, 3), p=f"{p_g:.1e}", Pass=bool(rho_g > RHO_TARGET)),
        dict(Source=label, Scale=f"1 km grid, populated cells (n = {int(popd.sum()):,})",
             Measure="footprint area", rho=round(rho_gp, 3), p=f"{p_gp:.1e}",
             Pass=bool(rho_gp > RHO_TARGET)),
    ]
    out = dict(
        n_footprints_in_union=int(len(bg)), footprint_area_km2=float(bg["area_m2"].sum() / 1e6),
        route_scale=dict(n=int(len(rt)), rho_area=float(rho_area), p_area=float(p_area),
                         rho_count=float(rho_n), p_count=float(p_n),
                         n_routes_zero_buildings=int((rt["n_buildings"] == 0).sum())),
        grid_scale=dict(cell_m=CELL_M, block_factor=f, n_cells=int(len(Pc)),
                        rho_all=float(rho_g), p_all=float(p_g), n_populated=int(popd.sum()),
                        rho_populated=float(rho_gp), p_populated=float(p_gp),
                        share_population_in_cells_with_buildings=pop_in_mapped),
        verdict_pass=bool(rho_area > RHO_TARGET and rho_gp > RHO_TARGET),
    )
    log.info("%s: route rho(area)=%.3f rho(count)=%.3f | grid all=%.3f populated=%.3f | "
             "pop in cells with buildings %.1f%%", label, rho_area, rho_n, rho_g, rho_gp,
             100 * pop_in_mapped)
    return out, rows, pd.DataFrame(comp)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pbf", default="E:/kash/india-latest.osm.pbf")
    ap.add_argument("--re-extract", action="store_true")
    args = ap.parse_args()

    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize

    pbf = Path(args.pbf)
    sources = {}
    if args.re_extract or not OSM_CSV.exists():
        if pbf.exists():
            extract_osm(pbf).to_csv(OSM_CSV, index=False)
    if OSM_CSV.exists():
        sources["osm"] = pd.read_csv(OSM_CSV)
    if args.re_extract or not MS_CSV.exists():
        if ms_tiles_complete():
            extract_ms().to_csv(MS_CSV, index=False, compression="gzip")
        elif any(MS_DIR.glob("*.csv.gz")):
            log.warning("Microsoft tiles incomplete or corrupt — skipping that source this run")
    if MS_CSV.exists():
        sources["microsoft"] = pd.read_csv(MS_CSV)
    if not sources:
        raise SystemExit("no building source available")

    union = C.study_area_union()
    with rasterio.open(C.WORLDPOP_TIF) as src:
        pop = src.read(1).astype(float)
        if src.nodata is not None:
            pop[pop == src.nodata] = 0.0
        pop[~np.isfinite(pop)] = 0.0
        tr, crs = src.transform, src.crs
    mask = rasterize([(union, 1)], out_shape=pop.shape, transform=tr, fill=0).astype(bool)
    pop[~mask] = 0.0
    f = max(1, int(round(CELL_M / (abs(tr.a) * 111_320 * np.cos(np.radians(34.0))))))
    H, W = (pop.shape[0] // f) * f, (pop.shape[1] // f) * f
    d = C.load_districts()
    name_col = next(c for c in ("name", "NAME", "district", "District") if c in d.columns)
    ctx = dict(
        union=union, pop=pop, mask=mask, tr=tr, crs=crs, f=f, H=H, W=W,
        cat=gpd.read_file(C.CACHE / "catchments_network.gpkg").to_crs(C.UTM),
        a02=pd.read_csv(C.DERIVED / "a02_catchments.csv")[["New_Route_ID", "Route_Type", "pop_net"]],
        district_masks=[(r[name_col], rasterize([(r.geometry, 1)], out_shape=pop.shape,
                                                transform=tr, fill=0).astype(bool))
                        for _, r in d.iterrows()],
    )

    results, rows, comps = {}, [], []
    for label, b in sources.items():
        out, r, comp = analyse(label, b, ctx)
        results[label], rows, comps = out, rows + r, comps + [comp]
    primary = "microsoft" if "microsoft" in results else "osm"

    C.write_table(pd.DataFrame(rows), "table06d_v01_buildings",
                  f"Validation V1: WorldPop population vs building footprints, by source "
                  f"(Spearman rho, target > {RHO_TARGET}; partial circularity disclosed in text)")
    comp = pd.concat(comps).round(3)
    C.write_table(comp, "table06e_v01_completeness",
                  "Building-footprint completeness by district and source: share of populated 1 km "
                  "cells containing any footprint, and share of population in such cells")

    out = dict(
        rho_target=RHO_TARGET, primary_source=primary, sources=results,
        # primary-source headline, kept at top level for downstream readers
        route_scale=results[primary]["route_scale"], grid_scale=results[primary]["grid_scale"],
        verdict_pass=results[primary]["verdict_pass"],
        completeness_by_district=comp.to_dict(orient="records"),
        provenance=dict(
            osm_pbf=str(pbf), osm_pbf_sha256=sha256(pbf) if pbf.exists() else None,
            microsoft_release="Global ML Building Footprints, dataset-links 2026-02 (ODbL)",
            microsoft_tiles=sorted(p.name for p in MS_DIR.glob("*.csv.gz")),
        ),
        caveats=[
            "WorldPop uses building footprints as a covariate; V1 is a consistency check on "
            "spatial pattern, not independent validation of counts.",
            "OSM building mapping is volunteered and uneven; Microsoft footprints are "
            "machine-detected and uncorrected. See completeness table.",
        ],
    )
    C.write_result(out, "v01_spatial_crossval")


if __name__ == "__main__":
    main()
