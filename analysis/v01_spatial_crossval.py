#!/usr/bin/env python
"""
v01_spatial_crossval.py — validation channel V1: does the population surface the
whole plan rests on agree with an independently mapped layer of where people
live (OpenStreetMap building footprints)?

What it can establish. Every coverage and demand-index figure in the paper is a
zonal sum of the WorldPop raster. If the raster put people where there are no
buildings (or missed built-up areas), coverage and tiers would inherit the error.
Building footprints are a physical record of settlement, mapped by volunteers,
so agreement between the two surfaces — at the route-catchment scale the plan
uses and on a regular grid — is evidence that the raster places population
plausibly. The pre-registered target is Spearman rho > 0.60.

What it cannot establish, stated before the result.
  1. Partial circularity. WorldPop's constrained/top-down models use building
     footprints as a covariate when distributing census totals, so agreement is
     expected by construction to some degree. V1 is a consistency check on the
     spatial pattern, not an independent validation of population counts.
  2. OSM completeness. Volunteered building mapping in Kashmir is uneven. The
     share of populated grid cells with any mapped building is reported by
     district so that a weak correlation can be read as a mapping gap rather
     than a raster error, and vice versa.
  3. Only closed building WAYS are extracted; multipolygon building relations
     (a small minority, mostly large complexes) are not assembled.

Method.
  Extract: a single pass over the local India OSM extract (the same file a01
  used for the walk graph) collecting every closed way tagged building=* whose
  centroid falls in the padded 10-district bounding box; area by the shoelace
  formula on a local equirectangular projection.
  (a) Route scale: for each of the 186 network catchments (a02, W = 400 m),
      building count and footprint area inside, against catchment population.
  (b) Grid scale: 1 km cells over the 10-district union; WorldPop sum against
      building footprint area per cell, all cells and populated cells only.

Inputs
    E:/kash/india-latest.osm.pbf (or --pbf), data/cache/catchments_network.gpkg,
    data/derived/a02_catchments.csv, data/raw/kashmir_worldpop.tif
Outputs
    data/cache/osm_buildings_kashmir.csv      extracted footprints (gitignored)
    data/derived/v01_spatial_crossval.json
    data/derived/v01_route_buildings.csv
    paper/tables/table06d_v01_buildings.{csv,md}
"""
from __future__ import annotations

import argparse
import hashlib
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
BUILDINGS_CSV = C.CACHE / "osm_buildings_kashmir.csv"
EARTH_R_M = 6_371_008.8


def extract(pbf: Path) -> pd.DataFrame:
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
        a = np.asarray(pts)
        clon, clat = a[:-1, 0].mean(), a[:-1, 1].mean()
        if not (minx <= clon <= maxx and miny <= clat <= maxy):
            continue
        x = np.radians(a[:, 0] - clon) * EARTH_R_M * np.cos(np.radians(clat))
        y = np.radians(a[:, 1] - clat) * EARTH_R_M
        area = 0.5 * abs(np.dot(x[:-1], y[1:]) - np.dot(x[1:], y[:-1]))
        rows.append((clat, clon, area, way.tags.get("building", "")))
        if seen % 2_000_000 == 0:
            log.info("  %s building ways scanned, %s kept (%.0fs)", f"{seen:,}",
                     f"{len(rows):,}", time.time() - t0)
    df = pd.DataFrame(rows, columns=["lat", "lon", "area_m2", "building"])
    log.info("extracted %s footprints in the study bbox from %s building ways (%.0fs)",
             f"{len(df):,}", f"{seen:,}", time.time() - t0)
    return df


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pbf", default="E:/kash/india-latest.osm.pbf")
    ap.add_argument("--re-extract", action="store_true")
    args = ap.parse_args()

    import geopandas as gpd
    import rasterio
    from rasterio.features import rasterize
    from scipy.stats import spearmanr

    pbf = Path(args.pbf)
    if args.re_extract or not BUILDINGS_CSV.exists():
        if not pbf.exists():
            raise SystemExit(f"OSM extract not found: {pbf}")
        extract(pbf).to_csv(BUILDINGS_CSV, index=False)
    b = pd.read_csv(BUILDINGS_CSV)
    bg = gpd.GeoDataFrame(b, geometry=gpd.points_from_xy(b["lon"], b["lat"]), crs=C.WGS84)
    union = C.study_area_union()
    bg = bg[bg.within(union)].to_crs(C.UTM)
    log.info("footprints inside the 10-district union: %s (total area %.1f km2)",
             f"{len(bg):,}", bg["area_m2"].sum() / 1e6)

    # (a) route scale
    cat = gpd.read_file(C.CACHE / "catchments_network.gpkg").to_crs(C.UTM)
    a02 = pd.read_csv(C.DERIVED / "a02_catchments.csv")[["New_Route_ID", "Route_Type", "pop_net"]]
    j = gpd.sjoin(bg[["area_m2", "geometry"]], cat[["New_Route_ID", "geometry"]],
                  predicate="within", how="inner")
    agg = j.groupby("New_Route_ID").agg(n_buildings=("area_m2", "size"),
                                        footprint_m2=("area_m2", "sum")).reset_index()
    rt = a02.merge(agg, on="New_Route_ID", how="left").fillna({"n_buildings": 0, "footprint_m2": 0})
    rt.to_csv(C.DERIVED / "v01_route_buildings.csv", index=False)
    rho_area, p_area = spearmanr(rt["pop_net"], rt["footprint_m2"])
    rho_n, p_n = spearmanr(rt["pop_net"], rt["n_buildings"])
    by_type = {}
    for t, s in rt.groupby("Route_Type"):
        r_, p_ = spearmanr(s["pop_net"], s["footprint_m2"])
        by_type[t] = dict(n=int(len(s)), rho=float(r_), p=float(p_),
                          n_zero_buildings=int((s["n_buildings"] == 0).sum()))

    # (b) grid scale: aggregate raster and footprints to 1 km cells
    with rasterio.open(C.WORLDPOP_TIF) as src:
        pop = src.read(1).astype(float)
        if src.nodata is not None:
            pop[pop == src.nodata] = 0.0
        pop[~np.isfinite(pop)] = 0.0
        tr, crs = src.transform, src.crs
    mask = rasterize([(union, 1)], out_shape=pop.shape, transform=tr, fill=0).astype(bool)
    pop[~mask] = 0.0
    bw = bg.to_crs(crs)
    col, row = ~tr * (bw.geometry.x.to_numpy(), bw.geometry.y.to_numpy())
    col, row = np.floor(col).astype(int), np.floor(row).astype(int)
    ok = (row >= 0) & (row < pop.shape[0]) & (col >= 0) & (col < pop.shape[1])
    fp_grid = np.zeros_like(pop)
    np.add.at(fp_grid, (row[ok], col[ok]), bw["area_m2"].to_numpy()[ok])
    # block-sum ~100 m cells to ~1 km
    f = max(1, int(round(CELL_M / (abs(tr.a) * 111_320 * np.cos(np.radians(34.0))))))
    H, W = (pop.shape[0] // f) * f, (pop.shape[1] // f) * f
    P = pop[:H, :W].reshape(H // f, f, W // f, f).sum(axis=(1, 3))
    B = fp_grid[:H, :W].reshape(H // f, f, W // f, f).sum(axis=(1, 3))
    M = mask[:H, :W].reshape(H // f, f, W // f, f).any(axis=(1, 3))
    Pc, Bc = P[M], B[M]
    rho_g, p_g = spearmanr(Pc, Bc)
    popd = Pc > 1.0
    rho_gp, p_gp = spearmanr(Pc[popd], Bc[popd])
    pop_in_mapped = float(Pc[Bc > 0].sum() / Pc.sum())

    # completeness by district: share of populated cells with any mapped building
    d = C.load_districts()
    name_col = next(c for c in ("name", "NAME", "district", "District") if c in d.columns)
    comp = []
    for _, r in d.iterrows():
        dm = rasterize([(r.geometry, 1)], out_shape=pop.shape, transform=tr, fill=0).astype(bool)
        Pd = pop[:H, :W].copy()
        Pd[~dm[:H, :W]] = 0
        Pd = Pd.reshape(H // f, f, W // f, f).sum(axis=(1, 3))
        sel = Pd > 1.0
        comp.append(dict(district=r[name_col], populated_cells=int(sel.sum()),
                         share_cells_with_buildings=float((B[sel] > 0).mean()) if sel.any() else np.nan,
                         share_pop_in_mapped_cells=float(Pd[sel & (B > 0)].sum() / Pd[sel].sum())
                         if sel.any() else np.nan))
    comp = pd.DataFrame(comp).sort_values("share_pop_in_mapped_cells")

    tab = pd.DataFrame([
        dict(Scale="Route catchment (n = 186)", Measure="footprint area",
             rho=round(rho_area, 3), p=f"{p_area:.1e}", Target=f"> {RHO_TARGET}",
             Pass=bool(rho_area > RHO_TARGET)),
        dict(Scale="Route catchment (n = 186)", Measure="building count",
             rho=round(rho_n, 3), p=f"{p_n:.1e}", Target=f"> {RHO_TARGET}",
             Pass=bool(rho_n > RHO_TARGET)),
        dict(Scale=f"{int(CELL_M/1000)} km grid, all cells (n = {len(Pc):,})", Measure="footprint area",
             rho=round(rho_g, 3), p=f"{p_g:.1e}", Target=f"> {RHO_TARGET}", Pass=bool(rho_g > RHO_TARGET)),
        dict(Scale=f"{int(CELL_M/1000)} km grid, populated cells (n = {int(popd.sum()):,})",
             Measure="footprint area", rho=round(rho_gp, 3), p=f"{p_gp:.1e}",
             Target=f"> {RHO_TARGET}", Pass=bool(rho_gp > RHO_TARGET)),
    ])
    C.write_table(tab, "table06d_v01_buildings",
                  "Validation V1: WorldPop population vs OpenStreetMap building footprints "
                  "(Spearman rho; partial circularity disclosed in text)")
    C.write_table(comp.round(3), "table06e_v01_osm_completeness",
                  "OSM building-mapping completeness by district")

    out = dict(
        pbf=str(pbf), pbf_sha256=sha256(pbf) if pbf.exists() else None,
        n_footprints_in_union=int(len(bg)), footprint_area_km2=float(bg["area_m2"].sum() / 1e6),
        rho_target=RHO_TARGET,
        route_scale=dict(n=int(len(rt)), rho_area=float(rho_area), p_area=float(p_area),
                         rho_count=float(rho_n), p_count=float(p_n), by_route_type=by_type,
                         n_routes_zero_buildings=int((rt["n_buildings"] == 0).sum())),
        grid_scale=dict(cell_m=CELL_M, block_factor=f, n_cells=int(len(Pc)),
                        rho_all=float(rho_g), p_all=float(p_g),
                        n_populated=int(popd.sum()), rho_populated=float(rho_gp), p_populated=float(p_gp),
                        share_population_in_cells_with_buildings=pop_in_mapped),
        completeness_by_district=comp.to_dict(orient="records"),
        verdict_pass=bool(rho_area > RHO_TARGET and rho_gp > RHO_TARGET),
        caveats=[
            "WorldPop uses building footprints as a covariate; V1 is a consistency "
            "check on spatial pattern, not independent validation of counts.",
            "OSM building mapping is volunteered and uneven; see completeness table.",
            "Closed building ways only; multipolygon relations not assembled.",
        ],
    )
    C.write_result(out, "v01_spatial_crossval")
    log.info("V1 route rho(area)=%.3f rho(count)=%.3f | grid rho all=%.3f populated=%.3f | "
             "pop in mapped cells %.1f%%", rho_area, rho_n, rho_g, rho_gp, 100 * pop_in_mapped)


if __name__ == "__main__":
    main()
