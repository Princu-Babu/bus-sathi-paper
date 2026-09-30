#!/usr/bin/env python
"""
a12_equity_gini.py — how equally the rationalised network's service is spread over
the people it is meant to serve, and an explicit, named account of who loses.

§5.9 — the equity result. A plan that reports only aggregate improvement invites
the reviewer's first suspicion: that the gains were bought by quietly abandoning
someone. The honest form of an equity result therefore has two halves. The first
is a distributional statistic over the whole population — a population-weighted
Gini of accessibility — that says how (un)equally service is spread. The second
is a roll call of the losers: consolidation removes service somewhere, and the
paper states where, by name and by head-count, rather than leaving the reader to
assume it away.

Accessibility, operationally (supply side, not demand). For every 100 m WorldPop
pixel the accessibility score is

    A(pixel) = sum over active routes r whose 400 m network walk catchment
               contains the pixel of  (60 / headway_min(r))

i.e. the number of scheduled departures per hour a resident of that pixel can
reach on foot. A pixel served by a single 15-minute trunk scores 4; one served by
a 50-minute rural lifeline scores 1.2; one outside every catchment scores 0. This
is a supply-side service-intensity measure — it counts departures made available,
not trips taken — and it deliberately rewards frequency, because frequency is the
lever the plan actually pulls. The population-weighted Gini then uses each pixel's
resident population as the weight (common.gini), so the coefficient describes
inequality across *people*, not across pixels: a Gini of 0 would mean every
resident can reach the same hourly service, 1 that all service accrues to a
vanishing share. A route-count variant (distinct routes reachable, ignoring
frequency) is reported alongside as a robustness check.

Why there is no before/after pair. An equity result is most persuasive as a
change — Gini before consolidation versus after. That comparison is *not*
computed here, and the reason is stated rather than finessed: the published plan
carries routed geometry only for the 186 active routes. The 458 merged permit
records have no line geometry on disk (the plan GeoJSON contains active features
only), so a pre-consolidation accessibility surface cannot be built from real
data. Manufacturing one would mean inventing the very geometries whose loss is
under study. The before-state Gini is therefore reported as NOT_COMPUTABLE, and
the equity finding rests on the after-state distribution plus the concrete losers
analysis, which needs no counterfactual geometry.

The losers, counted not asserted (the §5.1 finding made spatial). Collapsing the
permit register onto corridors suppresses 32 alternative via-routings across 20
origin-destination corridors (q01/D1): a corridor served by permits that ran via
two different intermediate places keeps one routing and drops the other(s). Each
dropped routing is enumerated here by corridor, by the surviving route that
absorbed it, and by the intermediate place it used to serve. Where that place has
a geocoded coordinate in the permit register, the population within a 400 m walk
of it is measured against WorldPop, and split into the part still inside the
plan's network catchment (retains bus access by another route) and the part
outside it (loses access outright). Where no coordinate exists, the row is marked
NOT_COMPUTABLE rather than guessed. Per-via populations overlap and are never
summed; the network-level figure is the deduplicated union of the suppressed-via
walksheds.

Outputs
    data/derived/a12_equity_gini.json       Gini (after), losers roll-call
    paper/tables/table05f_equity_gini.{csv,md}
    paper/tables/table05g_losers.{csv,md}

Usage
    python analysis/a12_equity_gini.py
"""
from __future__ import annotations

import difflib
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a12")

WALK_BUDGET_M = 400.0        # engine WALK_CATCHMENT_M, for the via-point walkshed
VIA_CLUSTER_THRESH = 0.82    # q01 _via_clusters similarity threshold (mirrored)


# ── accessibility surface + Gini (after state) ─────────────────────────────────
def accessibility_gini(cat, active):
    """
    Population-weighted accessibility Gini over WorldPop pixels.

    Each active route's network catchment is rasterised onto the WorldPop grid and
    two accumulators are built per pixel: scheduled departures per hour (frequency
    weighted) and the count of distinct routes reachable. The Gini is taken over
    inhabited pixels inside the ten-district union, weighted by pixel population,
    so it is inequality across residents.
    """
    import rasterio
    from rasterio.features import geometry_mask, rasterize
    from shapely.ops import transform as shp_transform
    from pyproj import Transformer

    to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform
    m = cat.merge(active[["New_Route_ID", "Headway_Min"]], on="New_Route_ID", how="left")
    if m["Headway_Min"].isna().any():
        raise SystemExit("headway not joined for all catchments")

    with rasterio.open(C.WORLDPOP_TIF) as src:
        pop = src.read(1).astype("float64")
        transform = src.transform
        nodata = src.nodata
        shape = pop.shape
    pop = np.where((pop == nodata) | (pop < 0) | ~np.isfinite(pop), 0.0, pop)

    union_wgs = C.load_districts().to_crs(C.WGS84).geometry.union_all()
    inside = geometry_mask([union_wgs], out_shape=shape, transform=transform, invert=True)

    freq_acc = np.zeros(shape, dtype="float32")
    cnt_acc = np.zeros(shape, dtype="float32")
    for _, r in m.iterrows():
        geom_wgs = shp_transform(to_wgs, r.geometry)
        mask = rasterize([(geom_wgs, 1)], out_shape=shape, transform=transform,
                         fill=0, all_touched=False, dtype="uint8").astype(bool)
        freq_acc[mask] += 60.0 / float(r["Headway_Min"])
        cnt_acc[mask] += 1.0

    sel = inside & (pop > 0)
    w = pop[sel]
    freq = freq_acc[sel].astype("float64")
    cnt = cnt_acc[sel].astype("float64")

    pop_total = float(w.sum())
    served = w[freq > 0]
    gini_freq = C.gini(freq, w)
    gini_cnt = C.gini(cnt, w)

    # Conditional Gini, among residents who have service at all. The headline
    # Gini is dominated by the zero-service mass, so on its own it largely
    # restates the coverage share rather than measuring how service is shared
    # out. Removing the zeros asks the separate, genuinely distributional
    # question: among the population the network does reach, is frequency spread
    # evenly or concentrated on a few corridors? Both are reported so neither
    # reading can be mistaken for the other.
    smask = freq > 0
    gini_freq_served = C.gini(freq[smask], w[smask])
    gini_cnt_served = C.gini(cnt[smask], w[smask])

    # Population-weighted quantiles of the frequency score, for context.
    order = np.argsort(freq)
    fw = np.cumsum(w[order]) / w.sum()
    def wq(q):
        return float(freq[order][np.searchsorted(fw, q)])

    out = dict(
        accessibility_definition=(
            "Per 100 m WorldPop pixel: sum over active routes whose 400 m network "
            "walk catchment contains the pixel of (60 / headway_min) = scheduled "
            "departures per hour reachable on foot. Supply-side service intensity, "
            "not realised demand."),
        gini_frequency_weighted=gini_freq,
        gini_route_count=gini_cnt,
        gini_frequency_weighted_served_only=gini_freq_served,
        gini_route_count_served_only=gini_cnt_served,
        gini_note=(
            "The whole-population Gini counts the 75.8% of residents with zero "
            "reachable service, so it is bounded below by the coverage share and "
            "should not be read as inequality of frequency alone. The served-only "
            "variant conditions on having any service and measures how frequency "
            "is distributed among those the network reaches."),
        population_total=pop_total,
        population_with_service=float(served.sum()),
        share_population_with_service=float(served.sum() / pop_total),
        share_population_zero_service=float(1 - served.sum() / pop_total),
        mean_departures_per_hour_pop_weighted=float((freq * w).sum() / w.sum()),
        median_departures_per_hour_pop_weighted=wq(0.50),
        p90_departures_per_hour_pop_weighted=wq(0.90),
        n_pixels_inhabited=int(sel.sum()),
        n_pixels_served=int((freq > 0).sum()),
    )
    log.info("accessibility Gini (pop-weighted): frequency %.4f, route-count "
             "%.4f; %.1f%% of residents have zero network service",
             gini_freq, gini_cnt, 100 * out["share_population_zero_service"])
    log.info("  conditional on having service: frequency Gini %.4f, route-count "
             "Gini %.4f over %s served residents",
             gini_freq_served, gini_cnt_served, f"{served.sum():,.0f}")
    return out


# ── losers: suppressed alternative via-routings (mirrors q01/D1) ────────────────
def _norm_place(s) -> str:
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ""
    return re.sub(r"[^A-Z]", "", str(s).upper())


def _cluster_vias(vias, thresh=VIA_CLUSTER_THRESH):
    """
    Single-link clustering of via labels, identical to q01 _via_clusters, but
    returning a cluster id per input (None for empty) and the representative stems.
    """
    reps: list[str] = []
    labels: list[int | None] = []
    for v in vias:
        k = _norm_place(v)
        if not k:
            labels.append(None)
            continue
        placed = False
        for i, rp in enumerate(reps):
            if (k in rp or rp in k
                    or difflib.SequenceMatcher(None, k, rp).ratio() >= thresh):
                if len(k) < len(reps[i]):
                    reps[i] = k
                labels.append(i)
                placed = True
                break
        if not placed:
            reps.append(k)
            labels.append(len(reps) - 1)
    return labels, reps


def _parse_latlon(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return None
    try:
        a, b = str(s).split(",")[:2]
        return float(a), float(b)
    except Exception:
        return None


def losers_analysis(cat):
    """Enumerate the 32 suppressed via-routings and cost each one against WorldPop."""
    import geopandas as gpd
    import rasterio
    import rasterstats
    from shapely import union_all
    from shapely.geometry import Point
    from shapely.ops import transform as shp_transform
    from pyproj import Transformer

    # Reproduce q01's permit->engine positional join and undirected corridor key.
    permits = pd.read_csv(C.PERMITS_CSV).reset_index(drop=True)
    permits["Route_ID"] = [f"R{i + 1:04d}" for i in range(len(permits))]
    # The permit register also carries a (mostly empty) Route_Name; drop it so the
    # engine's own Route_Name survives the join without a suffix collision.
    permits = permits.drop(columns=[c for c in ("Route_Name",) if c in permits.columns])
    plan = C.load_plan()[["Route_ID", "Route_Name", "Action_Taken", "New_Route_ID"]]
    m = plan.merge(permits, on="Route_ID", how="left")

    def key(r, nd=4):
        if pd.isna(r["Origin_Lat"]) or pd.isna(r["Dest_Lat"]):
            return None
        a = f"{round(float(r['Origin_Lat']), nd)},{round(float(r['Origin_Lon']), nd)}"
        b = f"{round(float(r['Dest_Lat']), nd)},{round(float(r['Dest_Lon']), nd)}"
        return " | ".join(sorted([a, b]))

    m["corridor_key"] = m.apply(key, axis=1)
    permit_rows = m[m["corridor_key"].notna()].copy()

    # Covered network union (all active routes) — the reference for "still served".
    to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform
    to_utm = Transformer.from_crs(C.WGS84, C.UTM, always_xy=True).transform
    covered_utm = union_all(list(cat.geometry.values))
    with rasterio.open(C.WORLDPOP_TIF) as src:
        nodata = src.nodata

    def pop_in(geom_utm):
        z = rasterstats.zonal_stats([shp_transform(to_wgs, geom_utm)],
                                    str(C.WORLDPOP_TIF), stats=["sum"], nodata=nodata)
        return float(z[0]["sum"] or 0.0)

    rows = []
    suppressed_buffers = []
    for ck, g in permit_rows.groupby("corridor_key"):
        labels, reps = _cluster_vias(g["Via_Points_Raw"].tolist())
        n_via = len(reps)
        if n_via <= 1:
            continue
        g = g.assign(_via_cluster=labels)
        origin, dest = g["Origin"].iloc[0], g["Destination"].iloc[0]

        # Retained cluster: the one carrying the surviving (active) permit; else
        # the most-permitted cluster. Mirrors the q01 count of (n_via - 1) lost.
        active_g = g[g["Action_Taken"].isin(C.ACTIVE_ACTIONS) & g["_via_cluster"].notna()]
        survivor = active_g.iloc[0] if len(active_g) else None
        if survivor is not None and survivor["_via_cluster"] is not None:
            retained = int(survivor["_via_cluster"])
        else:
            sizes = g[g["_via_cluster"].notna()].groupby("_via_cluster").size()
            retained = int(sizes.idxmax())
        survivor_id = survivor["New_Route_ID"] if survivor is not None else \
            (active_g["New_Route_ID"].iloc[0] if len(active_g) else
             g[g["Action_Taken"].isin(C.ACTIVE_ACTIONS)]["New_Route_ID"].iloc[0]
             if g["Action_Taken"].isin(C.ACTIVE_ACTIONS).any() else None)
        survivor_name = None
        if survivor_id is not None:
            sn = C.load_active()
            hit = sn.loc[sn["New_Route_ID"] == survivor_id, "Route_Name"]
            survivor_name = hit.iloc[0] if len(hit) else None

        for cid in sorted(set(l for l in labels if l is not None)):
            if cid == retained:
                continue
            members = g[g["_via_cluster"] == cid]
            # Representative via label + coordinate (first member with a coordinate).
            via_label = members["Via_Points_Raw"].dropna().iloc[0] \
                if members["Via_Points_Raw"].notna().any() else reps[cid]
            coord = None
            for _, mm in members.iterrows():
                coord = _parse_latlon(mm.get("Via_Points_Geocoded"))
                if coord is not None:
                    break
            supp_name = (members["Route_Name"].dropna().iloc[0]
                         if members["Route_Name"].notna().any() else None)

            rec = dict(
                corridor=f"{origin} -> {dest}",
                n_via_routings=n_via,
                suppressed_via=str(via_label),
                n_permits_on_routing=int(len(members)),
                survivor_route_id=survivor_id,
                survivor_route_name=survivor_name,
                suppressed_permit_name=supp_name,
                via_lat=coord[0] if coord else None,
                via_lon=coord[1] if coord else None,
            )
            if coord is None:
                rec.update(pop_within_400m=None, pop_uncovered_within_400m=None,
                           status="NOT_COMPUTABLE",
                           reason="no geocoded via point in permit register")
            else:
                pt_utm = shp_transform(to_utm, Point(coord[1], coord[0]))
                buf = pt_utm.buffer(WALK_BUDGET_M)
                gross = pop_in(buf)
                resid = buf.difference(covered_utm)
                uncov = pop_in(resid) if not resid.is_empty else 0.0
                rec.update(pop_within_400m=gross, pop_uncovered_within_400m=uncov,
                           status="OK", reason="")
                suppressed_buffers.append(buf)
            rows.append(rec)

    losers = pd.DataFrame(rows)

    # Deduplicated network-level affected population (union, never a sum).
    dedup_gross = dedup_uncovered = None
    if suppressed_buffers:
        u = union_all(suppressed_buffers)
        dedup_gross = pop_in(u)
        resid = u.difference(covered_utm)
        dedup_uncovered = pop_in(resid) if not resid.is_empty else 0.0

    n_comp = int((losers["status"] == "OK").sum())
    summary = dict(
        n_corridors_with_suppressed_routings=int(losers["corridor"].nunique()),
        n_suppressed_via_routings=int(len(losers)),
        n_computable=n_comp,
        n_not_computable=int((losers["status"] == "NOT_COMPUTABLE").sum()),
        dedup_union_pop_within_400m=dedup_gross,
        dedup_union_pop_uncovered_within_400m=dedup_uncovered,
        note=("Per-via populations overlap and must not be summed; the network "
              "figure is the deduplicated union of the suppressed-via 400 m "
              "walksheds. 'Uncovered' is the part of that walkshed outside the "
              "plan's dissolved network catchment, i.e. residents who lose bus "
              "access rather than merely a preferred routing."),
    )
    log.info("losers: %d suppressed via-routings across %d corridors; %d costed, "
             "%d not computable; dedup affected within 400 m = %s (%s uncovered)",
             summary["n_suppressed_via_routings"],
             summary["n_corridors_with_suppressed_routings"],
             summary["n_computable"], summary["n_not_computable"],
             f"{dedup_gross:,.0f}" if dedup_gross is not None else "n/a",
             f"{dedup_uncovered:,.0f}" if dedup_uncovered is not None else "n/a")
    return losers, summary


# ── main ────────────────────────────────────────────────────────────────────────
def main() -> None:
    import geopandas as gpd

    t0 = time.time()
    cat = gpd.read_file(C.CACHE / "catchments_network.gpkg")
    if cat.crs is None or cat.crs.to_epsg() != 32643:
        cat = cat.to_crs(C.UTM)
    active = C.load_active()
    log.info("inputs: %d network catchments, %d active routes", len(cat), len(active))

    gini_block = accessibility_gini(cat, active)
    losers, losers_summary = losers_analysis(cat)

    # (c) before/after: honestly not computable.
    before_after = dict(
        before_gini="NOT_COMPUTABLE",
        reason=("The 458 merged permit records carry no routed line geometry on "
                "disk (the plan GeoJSON holds the 186 active features only), so a "
                "pre-consolidation accessibility surface cannot be built from "
                "real data. A before/after Gini pair is therefore not reported; "
                "only the after-state Gini and the concrete losers analysis are."),
        after_gini_frequency_weighted=gini_block["gini_frequency_weighted"],
    )

    # ── tables ──
    gini_tab = pd.DataFrame([
        dict(measure="Accessibility Gini (frequency-weighted, pop-weighted)",
             value=round(gini_block["gini_frequency_weighted"], 4)),
        dict(measure="Accessibility Gini (route-count, pop-weighted)",
             value=round(gini_block["gini_route_count"], 4)),
        dict(measure="Accessibility Gini, served residents only (frequency-weighted)",
             value=round(gini_block["gini_frequency_weighted_served_only"], 4)),
        dict(measure="Accessibility Gini, served residents only (route-count)",
             value=round(gini_block["gini_route_count_served_only"], 4)),
        dict(measure="Share of residents with any network service",
             value=round(gini_block["share_population_with_service"], 4)),
        dict(measure="Share of residents with zero network service",
             value=round(gini_block["share_population_zero_service"], 4)),
        dict(measure="Mean departures/hour reachable (pop-weighted)",
             value=round(gini_block["mean_departures_per_hour_pop_weighted"], 4)),
        dict(measure="Median departures/hour reachable (pop-weighted)",
             value=round(gini_block["median_departures_per_hour_pop_weighted"], 4)),
        dict(measure="Before-state Gini", value="NOT_COMPUTABLE"),
    ])
    C.write_table(gini_tab, "table05f_equity_gini",
                  "Population-weighted accessibility of the rationalised network "
                  "(after state). Accessibility is supply-side departures/hour "
                  "reachable within a 400 m network walk; the before state is not "
                  "computable because merged permits have no geometry.")

    losers_out = losers.copy()
    for col in ("pop_within_400m", "pop_uncovered_within_400m"):
        losers_out[col] = losers_out[col].apply(
            lambda x: int(round(x)) if pd.notna(x) else None)
    for col in ("via_lat", "via_lon"):
        losers_out[col] = losers_out[col].apply(
            lambda x: round(x, 5) if pd.notna(x) else None)
    C.write_table(
        losers_out.sort_values(["corridor", "suppressed_via"])[
            ["corridor", "suppressed_via", "survivor_route_id", "survivor_route_name",
             "n_permits_on_routing", "pop_within_400m", "pop_uncovered_within_400m",
             "status"]],
        "table05g_losers",
        "The losers: alternative via-routings suppressed by corridor "
        "consolidation, with population within a 400 m walk of the dropped "
        "intermediate place and the part of it left outside the plan's network")

    out = dict(
        status="OK",
        study_area_population=C.STUDY_AREA_POPULATION,
        accessibility_gini_after=gini_block,
        before_after=before_after,
        losers_summary=losers_summary,
        losers=losers_out.to_dict(orient="records"),
        interpretation=(
            "Service is unequally distributed across residents (frequency-"
            "weighted accessibility Gini "
            f"{gini_block['gini_frequency_weighted']:.3f}), driven mainly by the "
            f"{100 * gini_block['share_population_zero_service']:.0f}% of the "
            "population outside every catchment. Consolidation is not free: "
            f"{losers_summary['n_suppressed_via_routings']} alternative via-"
            f"routings across {losers_summary['n_corridors_with_suppressed_routings']} "
            "corridors are suppressed, named individually in table05g. A "
            "before/after Gini is not manufactured, because the merged permits "
            "have no geometry to build a counterfactual from."),
    )
    C.write_result(out, "a12_equity_gini")
    log.info("done (%.0fs)", time.time() - t0)


if __name__ == "__main__":
    main()
