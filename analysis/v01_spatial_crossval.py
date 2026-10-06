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
threshold is Spearman rho > 0.60. It was written down in the claim ledger on
2026-09-08, before this module existed, but it was never lodged with any
registry, so it is described as "declared in advance in the repository", not
"pre-registered".

Two footprint sources, reported side by side, IN THE ORDER THEY WERE ADOPTED:
  osm        (declared first, ledger 2026-09-08) OpenStreetMap closed building
             ways from the local India extract (volunteered; uneven
             completeness). This is the layer the threshold was declared on, and
             it FAILS at the 1 km grid scale.
  microsoft  (added afterwards; first committed 2026-10-01, after the OSM
             grid-scale result was known) Microsoft Global ML Building
             Footprints (2026-02 release), machine-detected from satellite
             imagery — near-complete coverage, independent of volunteer effort.
             It is the primary V1 source when present
             (data/external/ms_buildings/*.csv.gz, fetched per quadkey).
The output carries a `sequence` block so that the pass on the second layer is
never reported without that history.

What it cannot establish, stated before the result.
  1. Circularity. WorldPop's modelling uses built-settlement layers as
     covariates, and the product named in data/MANIFEST.md is a "constrained"
     one. If it is building-constrained, cells without buildings receive zero
     population by construction and a high rank correlation with a footprint
     layer is expected from the method; V1 would then test the consistency of
     the footprint layer with the surface, not the accuracy of population
     counts. The release and covariates are not recorded in the raster file
     (see `worldpop_variant` in the output), so the size of this effect cannot
     be established from the repository.
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


# ── history of the two layers (read-only git evidence) ───────────────────────
# Commits are pinned and then verified against `git`; the module never reads the
# "latest" commit, so re-running it after unrelated commits gives identical output.
LEDGER_COMMIT = "1b9345f"      # claim ledger declares V1 on OSM footprints, rho > 0.60
FIRST_OUTPUT_COMMIT = "ab672e3"  # first V1 output: OSM only
MS_SUPPORT_COMMIT = "5d9dd64"    # module rewritten to accept a Microsoft source (data absent)
MS_RESULT_COMMIT = "69a3d1e"     # Microsoft layer data + results first committed


def _git(*args: str) -> str | None:
    import subprocess
    try:
        r = subprocess.run(["git", *args], cwd=C.ROOT, capture_output=True, text=True,
                           timeout=60, check=True)
        return r.stdout
    except Exception:
        return None


def _commit_info(h: str) -> dict:
    out = _git("show", "-s", "--format=%h|%ad|%s", "--date=iso-strict", h)
    if not out:
        return dict(commit=h, verified=False)
    short, when, subject = out.strip().split("|", 2)
    return dict(commit=short, committed=when, subject=subject, verified=True)


def build_sequence(results: dict, primary: str) -> dict:
    """Which layer was declared first, how it fared, what was added later, and when."""
    ledger = _git("show", f"{LEDGER_COMMIT}:paper/CLAIM_LEDGER.md")
    declared_on_osm = bool(ledger and "OSM building footprint density" in ledger
                           and "$\\rho > 0.60$" in ledger)
    first_json = _git("show", f"{FIRST_OUTPUT_COMMIT}:data/derived/v01_spatial_crossval.json")
    first = None
    if first_json:
        try:
            first = json.loads(first_json)
        except ValueError:
            first = None
    first_is_osm_only = bool(first is not None and "sources" not in first
                             and "microsoft" not in first_json)
    ms_json = _git("show", f"{MS_RESULT_COMMIT}:data/derived/v01_spatial_crossval.json")
    ms_first_present = bool(ms_json and '"microsoft"' in ms_json)

    def summary(label: str) -> dict:
        r = results[label]
        return dict(layer=label,
                    route_scale_rho_area=r["route_scale"]["rho_area"],
                    route_scale_rho_count=r["route_scale"]["rho_count"],
                    grid_all_cells_rho=r["grid_scale"]["rho_all"],
                    grid_populated_cells_rho=r["grid_scale"]["rho_populated"],
                    n_routes=r["route_scale"]["n"],
                    n_grid_cells_all=r["grid_scale"]["n_cells"],
                    n_grid_cells_populated=r["grid_scale"]["n_populated"],
                    passes_declared_criterion=r["verdict_pass"],
                    n_tests_above_threshold=int(sum(
                        v > RHO_TARGET for v in (r["route_scale"]["rho_area"],
                                                 r["route_scale"]["rho_count"],
                                                 r["grid_scale"]["rho_all"],
                                                 r["grid_scale"]["rho_populated"])),
                    ),
                    n_tests_total=4)

    seq = dict(
        git_verified=bool(ledger is not None and first_json is not None
                          and ms_json is not None),
        threshold=RHO_TARGET,
        declared_criterion=("module verdict: route-catchment footprint-area rho > "
                            f"{RHO_TARGET} AND 1 km populated-cell footprint-area rho > "
                            f"{RHO_TARGET}. The ledger entry of 2026-09-08 states only "
                            f"'rho > 0.60' without naming the scale."),
        declared_first=dict(
            layer="osm",
            declared_in=f"paper/CLAIM_LEDGER.md at {LEDGER_COMMIT}",
            declaration_text_found_in_git=declared_on_osm,
            **_commit_info(LEDGER_COMMIT),
        ),
        first_output=dict(
            layer="osm",
            only_layer_in_first_output=first_is_osm_only,
            first_output_verdict_pass=(first or {}).get("verdict_pass"),
            first_output_grid_rho_populated=((first or {}).get("grid_scale") or {}).get("rho_populated"),
            **_commit_info(FIRST_OUTPUT_COMMIT),
        ),
        added_later=dict(
            layer="microsoft",
            module_support_added=_commit_info(MS_SUPPORT_COMMIT),
            data_and_results_first_committed=_commit_info(MS_RESULT_COMMIT),
            microsoft_results_first_present_at_that_commit=ms_first_present,
            added_after_declared_layer_failed_at_grid_scale=bool(
                results.get("osm", {}).get("verdict_pass") is False),
            reason_recorded=("a more complete footprint source, because OpenStreetMap "
                             "building coverage is sparse (share of populated 1 km cells "
                             "containing any OSM footprint is 4-31 % by district)"),
        ),
        results_by_layer={k: summary(k) for k in results},
        primary_reported_layer=primary,
        primary_is_declared_layer=bool(primary == "osm"),
        statement=(
            "V1 was declared on the OSM layer. On that layer the module's criterion is "
            f"{'met' if results['osm']['verdict_pass'] else 'NOT met'}"
            f" (route-scale rho {results['osm']['route_scale']['rho_area']:.3f}, 1 km "
            f"populated-cell rho {results['osm']['grid_scale']['rho_populated']:.3f}; threshold "
            f"{RHO_TARGET}). The Microsoft layer was adopted afterwards and meets it "
            f"(route-scale rho {results['microsoft']['route_scale']['rho_area']:.3f}, grid "
            f"{results['microsoft']['grid_scale']['rho_populated']:.3f})."
            if "microsoft" in results and "osm" in results else
            "only one layer available in this run"),
    )
    return seq


def worldpop_variant() -> dict:
    """Product/version of the population raster, only as far as the repo records it."""
    import rasterio
    tags = {}
    with rasterio.open(C.WORLDPOP_TIF) as src:
        tags = dict(src.tags())
    manifest = C.DATA / "MANIFEST.md"
    named = None
    if manifest.exists():
        import re
        for ln in manifest.read_text(encoding="utf-8").splitlines():
            hit = re.search(r"\((WorldPop[^)]*constrained[^)]*)\)", ln)
            if hit:
                named = hit.group(1)
                break
    return dict(
        product_named_in_manifest=named,
        raster_file_tags=tags,
        worldpop_variant=("not recorded in metadata"
                          if not (set(tags) - {"AREA_OR_POINT"}) else tags),
        release_or_version="not recorded in metadata",
        covariates_used="not recorded in metadata",
        note=("The raster file carries only the generic AREA_OR_POINT tag. data/MANIFEST.md "
              "names a 'UN-adjusted constrained individual-countries 100 m' product but "
              "gives no release identifier or version. The release must be established "
              "from the download record before it is cited."),
    )


def circularity_block(results: dict) -> dict:
    """Numbers that bear on whether a high V1 rho can fail; no verdict is drawn here."""
    out = {}
    for k, r in results.items():
        out[k] = dict(
            share_population_in_cells_with_buildings=r["grid_scale"]["share_population_in_cells_with_buildings"],
            share_population_in_cells_without_buildings=1.0 - r["grid_scale"]["share_population_in_cells_with_buildings"],
        )
    return dict(
        by_layer=out,
        interpretation=("A surface that places almost no population in cells without "
                        "buildings is what a building-constrained product would produce. "
                        "The figures show the pattern; they do not show whether it comes "
                        "from the model's constraint or from real settlement."),
        independent_population_check=("none in V1; the only count-based comparison is the "
                                      "Census 2011 district comparison in q01 (D4), which "
                                      "is itself anchored on the same census frame"),
    )


# SHA-256 of the Geofabrik india-latest.osm.pbf used for the original build, recorded when the
# file was present. On a clean clone the PBF (not committed) is absent: keep this recorded value
# rather than blanking it, and say so via `pbf_present: false`.
PBF_SHA256_RECORDED = "681021c55963ed736fd95dcb89c55ca34f0dbcb5431085eeb621dbc3bf9a908a"


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

    sequence = build_sequence(results, primary)
    wp_variant = worldpop_variant()
    order = {"osm": "1st: declared 2026-09-08 (fails at grid scale)",
             "microsoft": "2nd: added 2026-10-01, after the OSM grid result"}
    rows_df = pd.DataFrame(rows)
    rows_df["Declared_order"] = rows_df["Source"].map(order)
    C.write_table(rows_df, "table06d_v01_buildings",
                  f"Validation V1: WorldPop population vs building footprints, by source, in the "
                  f"order the layers were adopted (Spearman rho; threshold > {RHO_TARGET} declared "
                  f"in the claim ledger on 2026-09-08 for the OSM layer, not registered; the "
                  f"Microsoft layer was added afterwards; circularity disclosed in text)")
    comp = pd.concat(comps).round(3)
    C.write_table(comp, "table06e_v01_completeness",
                  "Building-footprint completeness by district and source: share of populated 1 km "
                  "cells containing any footprint, and share of population in such cells")

    out = dict(
        rho_target=RHO_TARGET, primary_source=primary, sources=results,
        # primary-source headline, kept at top level for downstream readers
        route_scale=results[primary]["route_scale"], grid_scale=results[primary]["grid_scale"],
        verdict_pass=results[primary]["verdict_pass"],
        verdict_pass_note=("verdict_pass is the verdict on the PRIMARY layer "
                           f"({primary}), which is not the layer the threshold was declared on. "
                           "See verdict_pass_by_layer and sequence."),
        verdict_pass_by_layer={k: v["verdict_pass"] for k, v in results.items()},
        verdict_pass_declared_layer=results["osm"]["verdict_pass"] if "osm" in results else None,
        sequence=sequence,
        worldpop_variant_block=wp_variant,
        worldpop_variant=wp_variant["worldpop_variant"],
        circularity=circularity_block(results),
        completeness_by_district=comp.to_dict(orient="records"),
        provenance=dict(
            osm_pbf=pbf.name, osm_pbf_sha256=sha256(pbf) if pbf.exists() else PBF_SHA256_RECORDED,
            pbf_present=pbf.exists(),
            osm_cache_sha256=sha256(OSM_CSV) if OSM_CSV.exists() else None,
            microsoft_cache_sha256=sha256(MS_CSV) if MS_CSV.exists() else None,
            microsoft_release="Global ML Building Footprints, dataset-links 2026-02 (ODbL)",
            microsoft_tiles=sorted(p.name for p in MS_DIR.glob("*.csv.gz")),
            microsoft_tiles_note=("lists the tiles present in data/external/ms_buildings on the "
                                  "machine that ran the module; empty on a clean clone, where the "
                                  "cache file data/cache/ms_buildings_kashmir.csv.gz is used"),
        ),
        caveats=[
            "WorldPop's modelling uses built-settlement layers as covariates (a covariate "
            "relationship with footprints is likely but its form is not recorded for this raster); "
            "if the product is building-constrained, V1 tests the consistency of the footprint "
            "layer with the surface, not the accuracy of population counts.",
            "OSM building mapping is volunteered and uneven; Microsoft footprints are "
            "machine-detected and uncorrected. See completeness table.",
            "The threshold (rho > 0.60) was declared on the OSM layer, which fails at the 1 km "
            "grid scale; the Microsoft layer was added afterwards. See sequence.",
        ],
    )
    C.write_result(out, "v01_spatial_crossval")


if __name__ == "__main__":
    main()
