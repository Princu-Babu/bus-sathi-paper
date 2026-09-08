#!/usr/bin/env python
"""
q01_data_quality.py — §3.5 data-quality diagnostics.

Section 3.5 is the part of a study-area section that separates a paper from a
consultancy report: every input is characterised, including where it is weak.
Six diagnostics are produced here, each written so the reader can see the
weakness rather than infer it.

  D1  Permit register structure. The register carries one row per permitted
      vehicle, not per route: 614 rows describe far fewer distinct origin-
      destination corridors, one of which carries 42 rows. Any "permits reduced
      to routes" headline is therefore mostly a change of unit of analysis, and
      the decomposition is reported so it cannot be read as a planning result.
      What collapsing a corridor group genuinely costs — alternative via
      routings, vehicle classes and service types that are given up — is
      counted rather than asserted away.
  D2  Permit activity. A permit is not an operating bus. Independent driver-GPS
      from the operator's own app is used to classify each planned route as
      observed or unobserved, giving an empirical floor on register dormancy.
  D3  OSM network completeness by district, and whether completeness tracks
      population — the standard peripheral-bias check for volunteered
      geographic information.
  D4  WorldPop plausibility against Census 2011 district totals, including a
      raster-coverage test so a truncated raster cannot masquerade as a low
      population.
  D5  Opportunity (POI) inventory by tier and district, with per-capita
      normalisation. No independent field enumeration was carried out, so no
      recall statistic is claimed.
  D6  Routing-engine travel-time error against observed driver GPS. The
      comparison is against observed IN-MOTION time, since OSRM returns a
      driving time that excludes passenger dwell.

Outputs
    paper/tables/table02_data_quality_*.{csv,md}
    data/derived/q01_data_quality.json
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("q01")

CENSUS_CSV = C.RAW / "census2011_kashmir_districts.csv"
# Plausible annual growth band for 2011->2026 used only to flag districts for
# comment, not to adjust any number. J&K decadal growth 2001-2011 was 23.6%
# (~2.1% p.a.); a 0.5-3.0% p.a. band is deliberately wide.
CAGR_BAND = (0.005, 0.030)
WORLDPOP_YEAR = 2026
CENSUS_YEAR = 2011


# ── D1: permit register hygiene ───────────────────────────────────────────────
def _permit_endpoints() -> pd.DataFrame:
    """
    Attach register endpoint coordinates to engine route rows.

    The engine numbers permit-derived rows R0001..R0614 in register order and
    appends the 30 synthetic e-bus backbone routes as SSCL-01..SSCL-30, so the
    join is positional. It is verified rather than assumed: the engine's
    normalised Route_Name must share a token with the register origin and with
    the register destination, and the match rate is reported.
    """
    permits = pd.read_csv(C.PERMITS_CSV).reset_index(drop=True)
    permits["Route_ID"] = [f"R{i + 1:04d}" for i in range(len(permits))]
    plan = C.load_plan()[["Route_ID", "Route_Name", "Action_Taken",
                          "New_Route_ID", "Route_KM", "Route_Type",
                          "Fleet_Required"]]
    m = plan.merge(permits[["Route_ID", "Origin", "Destination",
                            "Origin_Lat", "Origin_Lon", "Dest_Lat", "Dest_Lon",
                            "Via_Points_Raw", "Vehicle_Category", "Service_Type"]],
                   on="Route_ID", how="left")

    def token_ok(row) -> bool:
        if pd.isna(row["Origin"]):
            return True                      # synthetic backbone row, nothing to check
        name = str(row["Route_Name"]).upper()
        o = str(row["Origin"]).upper().split()
        d = str(row["Destination"]).upper().split()
        return (any(t[:4] in name for t in o if len(t) > 2)
                and any(t[:4] in name for t in d if len(t) > 2))

    checkable = m["Origin"].notna()
    rate = float(m.loc[checkable].apply(token_ok, axis=1).mean())
    log.info("D1 positional join verified on %d permit rows: %.1f%% name-token match",
             int(checkable.sum()), 100 * rate)
    m.attrs["join_match_rate"] = rate

    # Undirected endpoint key at the engine's own 4-decimal (~11 m) resolution.
    def key(r, nd=4):
        if pd.isna(r["Origin_Lat"]) or pd.isna(r["Dest_Lat"]):
            return None
        a = f"{round(float(r['Origin_Lat']), nd)},{round(float(r['Origin_Lon']), nd)}"
        b = f"{round(float(r['Dest_Lat']), nd)},{round(float(r['Dest_Lon']), nd)}"
        return " | ".join(sorted([a, b]))

    m["corridor_key"] = m.apply(key, axis=1)
    m["corridor_key_100m"] = m.apply(lambda r: key(r, 3), axis=1)
    return m


def _norm_place(s) -> str:
    """Uppercase alphabetic skeleton of a place string, for variant matching."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ""
    return re.sub(r"[^A-Z]", "", str(s).upper())


def _via_clusters(vias: list[str], thresh: float = 0.82) -> int:
    """
    Count distinct via routings in a corridor group, tolerant of spelling.

    "RAINAWARI" and "RAINAWARA" are the same place and must not be counted as
    two routings; "RAINAWARI" and "DALGATE" are different paths between the same
    endpoints and must be. Single-link agglomeration on the alphabetic skeleton
    with a similarity threshold, plus containment (so "MOMINABAD TENGPORA"
    joins "TENGPORA"), gives that behaviour without a gazetteer.
    """
    keys = [_norm_place(v) for v in vias]
    keys = [k for k in keys if k]
    if not keys:
        return 0
    reps: list[str] = []
    for k in keys:
        for i, r in enumerate(reps):
            if (k in r or r in k
                    or difflib.SequenceMatcher(None, k, r).ratio() >= thresh):
                if len(k) < len(reps[i]):
                    reps[i] = k                      # keep the shorter stem
                break
        else:
            reps.append(k)
    return len(reps)


def d1_register_hygiene() -> tuple[dict, pd.DataFrame]:
    m = _permit_endpoints()
    permit_rows = m[m["corridor_key"].notna()].copy()

    n_permits = int(len(permit_rows))
    grp = permit_rows.groupby("corridor_key")
    sizes = grp.size()
    n_corridors = int(sizes.size)
    n_dup_rows = int((sizes - 1).clip(lower=0).sum())
    n_corridors_100m = int(permit_rows.groupby("corridor_key_100m").ngroups)

    # What a corridor group contains, and therefore what collapsing it costs.
    per_corridor = grp.apply(lambda s: pd.Series(dict(
        n_permits=len(s),
        origin=s["Origin"].iloc[0],
        destination=s["Destination"].iloc[0],
        route=s["New_Route_ID"].iloc[0],
        km=float(s["Route_KM"].median()),
        n_via_routings=_via_clusters(s["Via_Points_Raw"].tolist()),
        n_vehicle_classes=int(s["Vehicle_Category"].nunique(dropna=True)),
        n_service_types=int(s["Service_Type"].nunique(dropna=True)),
        n_retained=int(s["Action_Taken"].isin(C.ACTIVE_ACTIONS).sum()),
    )), include_groups=False).reset_index()

    multi = per_corridor[per_corridor["n_permits"] > 1]
    alt_via_lost = int((per_corridor["n_via_routings"] - 1).clip(lower=0).sum())
    n_corr_multi_via = int((per_corridor["n_via_routings"] > 1).sum())
    n_corr_mixed_fleet = int((per_corridor["n_vehicle_classes"] > 1).sum())
    n_corr_mixed_service = int((per_corridor["n_service_types"] > 1).sum())

    # Decompose the merges by cause: identical corridor (a register-unit
    # artefact) against a distinct corridor absorbed on spatial overlap (a
    # planning decision).
    survivor_key = (m[m["Action_Taken"].isin(C.ACTIVE_ACTIONS)]
                    .dropna(subset=["corridor_key"])
                    .set_index("New_Route_ID")["corridor_key"].to_dict())
    merged = m[m["Action_Taken"] == C.MERGED_ACTION].copy()
    merged["survivor_key"] = merged["New_Route_ID"].map(survivor_key)
    merged["cause"] = np.where(
        merged["survivor_key"].isna(), "unresolved",
        np.where(merged["corridor_key"] == merged["survivor_key"],
                 "identical_corridor", "distinct_corridor_overlap"))
    cause = merged["cause"].value_counts().to_dict()
    n_identical = int(cause.get("identical_corridor", 0))
    n_overlap = int(cause.get("distinct_corridor_overlap", 0))

    n_engine_rows = int(len(m))
    n_active = int(m["Action_Taken"].isin(C.ACTIVE_ACTIONS).sum())
    n_synth = int(m["corridor_key"].isna().sum())
    n_active_permit = n_active - int(m[m["corridor_key"].isna()]
                                    ["Action_Taken"].isin(C.ACTIVE_ACTIONS).sum())

    worst = (per_corridor.sort_values("n_permits", ascending=False)
             .head(15)
             [["origin", "destination", "route", "n_permits", "n_via_routings",
               "n_vehicle_classes", "n_service_types", "km"]]
             .reset_index(drop=True))

    out = dict(
        join_match_rate=m.attrs.get("join_match_rate"),
        n_permit_register_rows=n_permits,
        n_synthetic_backbone_rows=n_synth,
        n_engine_route_rows=n_engine_rows,
        n_distinct_corridors_11m=n_corridors,
        n_distinct_corridors_100m=n_corridors_100m,
        n_duplicate_rows=n_dup_rows,
        duplicate_share=n_dup_rows / n_permits,
        n_corridors_with_duplicates=int(len(multi)),
        max_permits_on_one_corridor=int(sizes.max()),
        median_permits_per_corridor=float(sizes.median()),
        mean_permits_per_corridor=float(sizes.mean()),
        # what collapsing gives up
        n_corridors_with_multiple_via_routings=n_corr_multi_via,
        n_alternative_via_routings_suppressed=alt_via_lost,
        n_corridors_with_mixed_vehicle_classes=n_corr_mixed_fleet,
        n_corridors_with_mixed_service_types=n_corr_mixed_service,
        # funnel
        n_active_routes=n_active,
        n_active_permit_derived=n_active_permit,
        n_merged=int(len(merged)),
        merges_identical_corridor=n_identical,
        merges_distinct_corridor_overlap=n_overlap,
        merges_unresolved=int(cause.get("unresolved", 0)),
        corridor_retention_rate=n_active_permit / n_corridors,
        reduction_rows_to_active=1.0 - n_active / n_engine_rows,
        reduction_from_unit_change=n_identical / n_engine_rows,
        reduction_from_corridor_consolidation=n_overlap / n_engine_rows,
        note=("The register is a permit register: one row per permitted "
              "vehicle-service, with the same corridor recurring under "
              "different operators, vehicle classes, service types and "
              "spellings of the same via point. Collapsing 614 rows to 157 "
              "corridors is therefore a change in the unit of analysis and "
              "must not be reported as route rationalisation. Measured on "
              "corridors, the design retains 156 of 157 and adds a 30-route "
              "e-bus backbone, so it does not reduce route count; what it "
              "changes is frequency, vehicle allocation and fleet. The cost of "
              "collapsing is reported separately as the number of alternative "
              "via routings given up."),
    )
    log.info("D1 register: %d permit rows on %d distinct corridors at 11 m "
             "(%d at 100 m); %d duplicate rows (%.1f%%); mean %.1f, max %d "
             "permits per corridor",
             n_permits, n_corridors, n_corridors_100m, n_dup_rows,
             100 * out["duplicate_share"], out["mean_permits_per_corridor"],
             out["max_permits_on_one_corridor"])
    log.info("D1 collapsing cost: %d corridors carry >1 via routing; %d "
             "alternative routings suppressed; %d mixed vehicle class, %d "
             "mixed service type",
             n_corr_multi_via, alt_via_lost, n_corr_mixed_fleet,
             n_corr_mixed_service)
    log.info("D1 funnel: %d rows -> %d active (%.1f%%), of which %d permit-"
             "derived; %d/%d corridors retained (%.1f%%). Merges: %d identical-"
             "corridor + %d overlap (+%d unresolved). Reduction is %.1f pp unit "
             "change and %.1f pp consolidation.",
             n_engine_rows, n_active, 100 * out["reduction_rows_to_active"],
             n_active_permit, n_active_permit, n_corridors,
             100 * out["corridor_retention_rate"], n_identical, n_overlap,
             out["merges_unresolved"],
             100 * out["reduction_from_unit_change"],
             100 * out["reduction_from_corridor_consolidation"])
    return out, worst


# ── D2: permit activity / dormancy ───────────────────────────────────────────
def d2_activity() -> tuple[dict, pd.DataFrame]:
    obs = pd.read_csv(C.GPS_PERMIT_OBSERVED_CSV)
    ev = pd.read_csv(C.GPS_ROUTE_EVIDENCE_CSV)
    act = C.load_active()

    m = act.merge(obs[["route_id", "observed_cover", "status"]],
                  left_on="New_Route_ID", right_on="route_id", how="left")
    m = m.merge(ev[["route_id", "obs_frac", "n_runs", "n_drivers"]],
                on="route_id", how="left")

    by_status = (m.groupby("status", dropna=False)
                 .agg(routes=("New_Route_ID", "size"),
                      median_km=("Route_KM", "median"),
                      fleet=("Fleet_Required", "sum"),
                      median_cover=("observed_cover", "median"))
                 .reset_index())

    by_type = (m.assign(observed=m["status"].eq("OBSERVED"))
               .groupby("Route_Type")
               .agg(routes=("New_Route_ID", "size"),
                    observed=("observed", "sum"))
               .assign(observed_share=lambda d: d["observed"] / d["routes"])
               .reset_index())

    n_obs = int(m["status"].eq("OBSERVED").sum())
    out = dict(
        n_active_routes=len(m),
        n_observed_in_gps=n_obs,
        observed_share=n_obs / len(m),
        n_no_app_data=int(m["status"].eq("NO_APP_DATA").sum()),
        median_observed_cover=float(m["observed_cover"].median()),
        gps_runs_total=int(m["n_runs"].fillna(0).sum()),
        note=("The app is carried by a subset of operators, so an unobserved "
              "route is not proven dormant. The observed share is a lower "
              "bound on activity, and the unobserved set is the population "
              "from which genuine dormancy must be established by the "
              "licensing authority's own records."),
        by_type=by_type.to_dict("records"),
    )
    log.info("D2 activity: %d/%d active routes observed in driver GPS (%.0f%%)",
             n_obs, len(m), 100 * out["observed_share"])
    return out, by_status


# ── D3: OSM completeness by district ─────────────────────────────────────────
def d3_osm_completeness(district_pop: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Road-length density per district from the walk graph, against population."""
    import geopandas as gpd
    from shapely.geometry import LineString

    if not C.WALK_GRAPH_PKL.exists():
        log.warning("D3 skipped: walk graph not built yet (%s)", C.WALK_GRAPH_PKL.name)
        return dict(status="not_available"), pd.DataFrame()

    import pickle
    with C.WALK_GRAPH_PKL.open("rb") as fh:
        G = pickle.load(fh)

    rows = []
    for u, v, d in G.edges(data=True):
        rows.append((G.nodes[u]["x"], G.nodes[u]["y"],
                     G.nodes[v]["x"], G.nodes[v]["y"], d["length"]))
    e = pd.DataFrame(rows, columns=["x1", "y1", "x2", "y2", "length_m"])
    mid = gpd.GeoDataFrame(
        e[["length_m"]],
        geometry=gpd.points_from_xy((e.x1 + e.x2) / 2, (e.y1 + e.y2) / 2),
        crs=C.WGS84)

    d = C.load_districts().to_crs(C.WGS84)[["district", "geometry"]]
    j = gpd.sjoin(mid, d, how="inner", predicate="within")
    km = j.groupby("district")["length_m"].sum() / 1000.0

    area = (C.load_districts().to_crs(C.UTM).assign(
        area_km2=lambda g: g.area / 1e6).set_index("district")["area_km2"])

    t = (pd.DataFrame({"network_km": km, "area_km2": area})
         .join(district_pop.set_index("district_osm")[["worldpop_2026"]])
         .reset_index().rename(columns={"index": "district"}))
    t["km_per_km2"] = t["network_km"] / t["area_km2"]
    t["km_per_1000_pop"] = t["network_km"] / (t["worldpop_2026"] / 1000.0)
    t["pop_density"] = t["worldpop_2026"] / t["area_km2"]

    from scipy import stats
    rho, pval = stats.spearmanr(t["pop_density"], t["km_per_km2"])
    out = dict(
        status="ok",
        total_network_km=float(t["network_km"].sum()),
        rho_density_vs_road_density=float(rho),
        p_value=float(pval),
        ratio_max_min_km_per_1000=float(t["km_per_1000_pop"].max()
                                        / t["km_per_1000_pop"].min()),
        note=("A strong positive rank correlation between population density "
              "and mapped road density is expected on real ground and is also "
              "the signature of volunteered-mapping bias; the two cannot be "
              "separated without an official road inventory, which the "
              "authority does not publish. Per-capita road length is reported "
              "so the reader can see the spread directly."),
    )
    log.info("D3 OSM: %.0f km walkable network; rho(pop density, road density) = %.2f",
             out["total_network_km"], rho)
    return out, t.sort_values("km_per_km2", ascending=False)


# ── D4: WorldPop against Census 2011 ─────────────────────────────────────────
def d4_worldpop() -> tuple[dict, pd.DataFrame]:
    import geopandas as gpd
    import rasterio
    from rasterio.mask import mask

    census = pd.read_csv(CENSUS_CSV)
    d = C.load_districts().to_crs(C.WGS84)

    with rasterio.open(C.WORLDPOP_TIF) as src:
        rb = src.bounds
        db = d.total_bounds
        covered = (rb.left <= db[0] and rb.bottom <= db[1]
                   and rb.right >= db[2] and rb.top >= db[3])
        nodata = src.nodata
        rows = []
        for _, row in d.iterrows():
            arr, _ = mask(src, [row.geometry.__geo_interface__], crop=True,
                          filled=True, nodata=nodata if nodata is not None else -9999)
            a = arr[0].astype("float64")
            bad = ~np.isfinite(a)
            if nodata is not None:
                bad |= (a == nodata)
            a[bad | (a < 0)] = 0.0
            rows.append((row["district"], float(a.sum())))
        pix_area_m2 = abs(src.transform.a) * abs(src.transform.e) * (111_320 ** 2)

    zp = pd.DataFrame(rows, columns=["district_osm", "worldpop_2026"])
    t = census.merge(zp, on="district_osm", how="outer")
    t["ratio_wp_to_census"] = t["worldpop_2026"] / t["population_2011"]
    yrs = WORLDPOP_YEAR - CENSUS_YEAR
    t["implied_cagr"] = t["ratio_wp_to_census"] ** (1.0 / yrs) - 1.0
    t["cagr_plausible"] = t["implied_cagr"].between(*CAGR_BAND)

    tot_wp = float(t["worldpop_2026"].sum())
    tot_cen = float(t["population_2011"].sum())
    out = dict(
        raster_covers_district_union=bool(covered),
        raster_bounds=dict(left=rb.left, bottom=rb.bottom, right=rb.right, top=rb.top),
        district_union_bounds=dict(left=db[0], bottom=db[1], right=db[2], top=db[3]),
        approx_pixel_area_km2=pix_area_m2 / 1e6,
        worldpop_total=tot_wp,
        census2011_total=tot_cen,
        ratio_total=tot_wp / tot_cen,
        implied_total_cagr=(tot_wp / tot_cen) ** (1.0 / yrs) - 1.0,
        n_districts_outside_plausible_cagr=int((~t["cagr_plausible"]).sum()),
        engine_denominator=C.STUDY_AREA_POPULATION,
        engine_denominator_matches_zonal=bool(
            abs(tot_wp - C.STUDY_AREA_POPULATION) / C.STUDY_AREA_POPULATION < 0.02),
        note=("WorldPop 2026 is a modelled, UN-adjusted surface anchored on the "
              "2011 census frame, so it is not an independent count. Reporting "
              "the ratio district by district exposes where the surface is "
              "conservative; coverage figures computed on it inherit that "
              "conservatism, which biases the reported coverage share upward "
              "only if the denominator is understated, and is therefore stated "
              "explicitly rather than corrected."),
    )
    log.info("D4 WorldPop total %.0f vs Census 2011 %.0f (ratio %.3f, implied CAGR %.2f%%/yr)",
             tot_wp, tot_cen, out["ratio_total"], 100 * out["implied_total_cagr"])
    log.info("D4 raster covers district union: %s; engine denominator match: %s",
             covered, out["engine_denominator_matches_zonal"])
    return out, t


# ── D5: opportunity inventory ────────────────────────────────────────────────
def d5_pois(district_pop: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    import geopandas as gpd

    poi = pd.read_csv(C.POIS_CSV)
    g = gpd.GeoDataFrame(poi, geometry=gpd.points_from_xy(poi.lon, poi.lat),
                         crs=C.WGS84)
    d = C.load_districts().to_crs(C.WGS84)[["district", "geometry"]]
    j = gpd.sjoin(g, d, how="left", predicate="within")

    by_tier = (j.groupby("importance", dropna=False).size()
               .rename("n_pois").reset_index())
    by_cat = (j.groupby("category").size().sort_values(ascending=False)
              .rename("n_pois").reset_index())
    by_dist = (j.groupby("district").size().rename("n_pois").reset_index()
               .merge(district_pop[["district_osm", "worldpop_2026"]],
                      left_on="district", right_on="district_osm", how="left"))
    by_dist["pois_per_100k"] = by_dist["n_pois"] / (by_dist["worldpop_2026"] / 1e5)

    out = dict(
        n_pois=len(poi),
        n_unplaced=int(j["district"].isna().sum()),
        by_importance=by_tier.to_dict("records"),
        n_categories=int(poi["category"].nunique()),
        top_categories=by_cat.head(12).to_dict("records"),
        pois_per_100k_min=float(by_dist["pois_per_100k"].min()),
        pois_per_100k_max=float(by_dist["pois_per_100k"].max()),
        srinagar_share=float((j["district"] == "Srinagar").mean()),
        field_enumeration_performed=False,
        note=("No independent field enumeration of points of interest was "
              "carried out, so no recall statistic is reported. The inventory "
              "is characterised instead by tier composition and by per-capita "
              "density across districts, which makes the concentration in "
              "Srinagar visible; the consequence for the index is examined in "
              "the weighting and sensitivity analyses rather than asserted "
              "away here."),
    )
    log.info("D5 POIs: %d total, %d unplaced, %.0f%% in Srinagar, per-100k range %.1f-%.1f",
             len(poi), out["n_unplaced"], 100 * out["srinagar_share"],
             out["pois_per_100k_min"], out["pois_per_100k_max"])
    return out, by_dist.drop(columns=["district_osm"])


# ── D6: routing-engine travel time against GPS ───────────────────────────────
def d6_traveltime() -> tuple[dict, pd.DataFrame]:
    rc = pd.read_csv(C.GPS_REALITY_CSV)
    prof = pd.read_csv(C.GPS_CORRIDOR_PROFILES_CSV)
    m = rc[rc["klass"] == "matched"].copy()
    m["corridor_id"] = m["corridor"].str.extract(r"(\d+)").astype(int)
    m = m.merge(prof[["corridor_id", "in_motion_min", "dwell_min", "dwell_share",
                      "moving_kmh", "effective_kmh"]], on="corridor_id", how="left")

    # OSRM returns a car driving time with no passenger dwell, so the honest
    # comparator is observed in-motion time, not total observed run time.
    m["ape_motion"] = (m["osrm_drive_min"] - m["in_motion_min"]).abs() / m["in_motion_min"]
    m["ape_total"] = (m["osrm_drive_min"] - m["obs_oneway_min"]).abs() / m["obs_oneway_min"]
    m["ape_plan_total"] = (m["plan_oneway_min"] - m["obs_oneway_min"]).abs() / m["obs_oneway_min"]

    def rmse(a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        k = np.isfinite(a) & np.isfinite(b)
        return float(np.sqrt(np.mean((a[k] - b[k]) ** 2)))

    out = dict(
        n_corridors_matched=len(m),
        n_runs=int(m["n_runs"].sum()),
        n_drivers=int(m["n_drivers"].sum()),
        mape_osrm_vs_in_motion=float(m["ape_motion"].mean()),
        rmse_osrm_vs_in_motion_min=rmse(m["osrm_drive_min"], m["in_motion_min"]),
        mape_osrm_vs_total_observed=float(m["ape_total"].mean()),
        mape_plan_vs_total_observed=float(m["ape_plan_total"].mean()),
        median_plan_vs_obs_ratio=float(m["plan_vs_obs"].median()),
        median_osrm_vs_obs_ratio=float(m["osrm_vs_obs"].median()),
        median_dwell_share=float(m["dwell_share"].median()),
        note=("The routing engine understates the observed door-to-door run "
              "time because it models free-flowing car travel with no dwell; "
              "the engine's planned one-way time, which adds congestion, stop "
              "and junction penalties, closes part but not all of that gap. "
              "The residual is quantified here and carried into the "
              "cycle-time treatment rather than left implicit."),
    )
    log.info("D6 travel time: MAPE(OSRM vs in-motion) = %.1f%%, "
             "MAPE(plan vs observed total) = %.1f%%, median plan/obs = %.2f",
             100 * out["mape_osrm_vs_in_motion"],
             100 * out["mape_plan_vs_total_observed"],
             out["median_plan_vs_obs_ratio"])
    cols = ["corridor", "route", "n_runs", "n_drivers", "obs_km", "eng_km",
            "obs_oneway_min", "in_motion_min", "dwell_min", "osrm_drive_min",
            "plan_oneway_min", "ape_motion", "ape_total", "ape_plan_total"]
    return out, m[cols]


def main() -> None:
    d4, t_pop = d4_worldpop()
    district_pop = t_pop[["district_osm", "worldpop_2026", "population_2011"]].copy()
    district_pop = district_pop.rename(columns={"district_osm": "district_osm"})

    d1, t_dup = d1_register_hygiene()
    d2, t_act = d2_activity()
    d3, t_osm = d3_osm_completeness(district_pop)
    d5, t_poi = d5_pois(district_pop)
    d6, t_tt = d6_traveltime()

    C.write_table(t_dup, "table02a_permit_duplication",
                  "Corridors carrying the largest number of duplicate permits")
    C.write_table(t_act, "table02b_permit_activity",
                  "Planned routes by driver-GPS observation status")
    if not t_osm.empty:
        C.write_table(t_osm, "table02c_osm_completeness",
                      "Mapped walkable network by district against population")
    C.write_table(t_pop, "table02d_worldpop_vs_census",
                  "WorldPop 2026 zonal totals against Census 2011 district totals")
    C.write_table(t_poi, "table02e_poi_inventory",
                  "Opportunity inventory by district, per capita")
    C.write_table(t_tt, "table02f_traveltime_error",
                  "Routing-engine and planned travel time against observed driver GPS")

    C.write_result(dict(D1_register_hygiene=d1, D2_permit_activity=d2,
                        D3_osm_completeness=d3, D4_worldpop=d4,
                        D5_opportunities=d5, D6_travel_time=d6),
                   "q01_data_quality")
    log.info("q01 complete")


if __name__ == "__main__":
    main()
