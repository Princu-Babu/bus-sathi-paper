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

What the Gini is and is not. A population-weighted Gini over a surface on which
75.8% of residents score exactly zero is dominated by those zeros. The exact
decomposition G = z + (1 - z) * G_served (z = share of residents with zero
service, G_served = Gini among residents with any service) is computed and
reported, so the reader can see how much of 0.90 is "no service at all" and how
much is unequal frequency among the served. The statistic says nothing about the
EFFECT of the plan on equity (see next paragraph).

Why there is no before/after pair. An equity result is most persuasive as a
change — Gini before consolidation versus after. That comparison is *not*
computed here, and the reason is stated rather than finessed: the published plan
carries routed geometry only for the 186 active routes (the plan GeoJSON and the
offline OSRM cache hold the same 186), and the permit register records neither
route geometry nor headway for the 458 merged permits. A pre-consolidation
accessibility surface, with or without frequencies, therefore cannot be built
from real data; manufacturing one would mean inventing the very geometries whose
loss is under study. The before-state statistics are reported as NOT_COMPUTABLE
and the plan's effect on equity is reported as not estimable.

The losers, counted not asserted (the §5.1 finding made spatial). Collapsing the
permit register onto corridors suppresses 32 alternative via-routings across 20
origin-destination corridors (q01/D1): a corridor served by permits that ran via
two different intermediate places keeps one routing and drops the other(s). Each
dropped routing is enumerated here by corridor, by the surviving route that
absorbed it (and how many permits ran the retained routing, so a 41-permit
routing absorbed into a 1-permit survivor is visible), and by the intermediate
place it used to serve.

THE LOSER COUNT IS A PROXY, NOT A MEASUREMENT. Each dropped routing is
represented by ONE geocoded via-place, not by the alignment its permits ran. The
published figure measures the WorldPop population inside a 400 m STRAIGHT-LINE
disc around that point and subtracts the dissolved NETWORK-walk catchment of the
plan; that mixes metrics (the paper's own finding is that a straight-line disc
overstates network-walk reach), so it is neither an upper nor a lower bound. The
module therefore reports a range over reasonable variants: (a) disc vs 400 m
NETWORK walkshed from the via-point (same walk graph and off-network tail as the
route catchments); (b) published pins vs pins screened for plausibility. The
screen is mechanical and declared: a pin is implausible when the broken path
origin -> via -> destination is more than VIA_DETOUR_MAX times the straight
origin-destination distance (the sweep also reports 1.5 and 3.0). When a routing
has several permits with different geocodes for what clusters as the same place,
the plausible geocode carried by most permits is used (a coordinate already in the
register, never a hand-typed one); when none is plausible the routing is excluded
and the count with and without it is reported. Where no coordinate exists the
routing is marked NOT_COMPUTABLE rather than guessed. Per-via populations
overlap and are never summed; the network-level figure is the deduplicated union
of the suppressed-via walksheds.

Outputs
    data/derived/a12_equity_gini.json       Gini (after) + decomposition, losers
    paper/tables/table05f_equity_gini.{csv,md}
    paper/tables/table05g_losers.{csv,md}
    paper/tables/table05g_losers_variants.{csv,md}   total under every variant

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

# A via pin is implausible when origin -> via -> destination is more than this
# multiple of the straight origin-destination distance (detour factor). 2.0 is the
# primary screen; the sweep reports the others so the choice can be inspected.
VIA_DETOUR_MAX = 2.0
VIA_DETOUR_SWEEP = (1.5, 2.0, 3.0)
TAU_M = 100.0                # off-network tail, as a02 (one WorldPop cell)


# ── Gini helpers ───────────────────────────────────────────────────────────────
def gini_legacy(x, w):
    """
    The pre-fix `common.gini` (Lorenz curve integrated without its origin).
    Kept ONLY to report old -> new for every Gini in this module (audit F-03-01).
    """
    x, w = np.asarray(x, float), np.asarray(w, float)
    o = np.argsort(x)
    x, w = x[o], w[o]
    cw, cxw = np.cumsum(w), np.cumsum(x * w)
    area = np.trapezoid(cxw / cxw[-1], cw / cw[-1])
    return float(1.0 - 2.0 * area)


def gini_independent(x, w):
    """
    Independent closed form: G = sum_{i<j} w_i w_j |x_i - x_j| / (W * sum(w x)),
    evaluated on sorted x with cumulative weights (no Lorenz curve, no trapezoid).
    """
    x, w = np.asarray(x, float), np.asarray(w, float)
    o = np.argsort(x, kind="mergesort")
    x, w = x[o], w[o]
    c = np.cumsum(w)
    c_prev = c - w
    W = c[-1]
    u = float(np.sum(w * x * (c_prev + c - W)))
    return u / (W * float(np.sum(w * x)))


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

    # Exact decomposition G = z + (1 - z) * G_served. The Lorenz curve of a
    # distribution with a share z of the population at exactly zero is flat up to
    # z and then a scaled copy of the served residents' Lorenz curve, so the
    # identity is exact (not an approximation) for the trapezoidal Gini.
    z_share = float(1.0 - served.sum() / pop_total)

    def _decomp(g_all, g_served):
        comp_zero = z_share
        comp_served = (1.0 - z_share) * g_served
        return dict(
            gini_all=g_all, zero_service_share_z=comp_zero,
            gini_served_only=g_served,
            component_zero_service=comp_zero,
            component_unequal_among_served=comp_served,
            reconstructed=comp_zero + comp_served,
            reconstruction_error=comp_zero + comp_served - g_all,
            share_of_gini_from_zero_service=comp_zero / g_all,
            identity="G = z + (1 - z) * G_served",
            base=("all inhabited WorldPop pixels inside the ten-district union "
                  f"(n = {int(sel.sum()):,} pixels, {pop_total / 1e6:.2f} M residents); "
                  "z and G_served over the same pixels, population-weighted"))

    decomposition = dict(
        frequency_weighted=_decomp(gini_freq, gini_freq_served),
        route_count=_decomp(gini_cnt, gini_cnt_served),
    )

    # Verification of common.gini on the real surface: against the independent
    # closed form, and against the pre-fix formula (old -> new).
    gini_check = dict(
        frequency_weighted=dict(
            common_gini_fixed=gini_freq,
            independent_closed_form=gini_independent(freq, w),
            legacy_pre_fix=gini_legacy(freq, w)),
        route_count=dict(
            common_gini_fixed=gini_cnt,
            independent_closed_form=gini_independent(cnt, w),
            legacy_pre_fix=gini_legacy(cnt, w)),
        frequency_weighted_served_only=dict(
            common_gini_fixed=gini_freq_served,
            independent_closed_form=gini_independent(freq[smask], w[smask]),
            legacy_pre_fix=gini_legacy(freq[smask], w[smask])),
        route_count_served_only=dict(
            common_gini_fixed=gini_cnt_served,
            independent_closed_form=gini_independent(cnt[smask], w[smask]),
            legacy_pre_fix=gini_legacy(cnt[smask], w[smask])),
    )
    for k, v in gini_check.items():
        v["abs_diff_fixed_vs_independent"] = abs(v["common_gini_fixed"] - v["independent_closed_form"])
        v["fixed_minus_legacy"] = v["common_gini_fixed"] - v["legacy_pre_fix"]
        v["unchanged_at_4dp"] = bool(round(v["common_gini_fixed"], 4) == round(v["legacy_pre_fix"], 4))
        log.info("Gini check %-32s fixed %.6f | independent %.6f | legacy %.6f "
                 "(fixed - legacy = %+.2e)", k, v["common_gini_fixed"],
                 v["independent_closed_form"], v["legacy_pre_fix"],
                 v["fixed_minus_legacy"])

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
            "The whole-population Gini counts the residents with zero reachable "
            "service (share_population_zero_service), so it is bounded below by "
            "that share (G = z + (1 - z) * G_served, see gini_decomposition) and "
            "should not be read as inequality of frequency alone. The served-only "
            "variant conditions on having any service and measures how frequency "
            "is distributed among those the network reaches. Neither is a "
            "before/after comparison: the plan's effect on equity is not "
            "estimable (before_after)."),
        gini_decomposition=decomposition,
        gini_check=gini_check,
        gini_in_sample_note=(
            "Descriptive statistics of the published plan's own accessibility "
            "surface (n = every inhabited WorldPop pixel in the ten-district "
            "union); not an estimate with sampling error and not a comparison "
            "with any alternative network."),
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


def _enumerate_routings():
    """
    Enumerate the suppressed via-routings from the permit register + plan.

    Reproduces q01's permit->engine positional join and undirected corridor key,
    clusters the via labels of each corridor, and for every suppressed cluster
    records: the retained routing it lost to (label and permit count), every
    distinct geocode its member permits carry (with permit counts and a detour
    factor against the corridor's own origin and destination), and the pin the
    published analysis used (first member permit with a geocode).
    """
    from pyproj import Transformer

    to_utm = Transformer.from_crs(C.WGS84, C.UTM, always_xy=True).transform
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
    active_names = C.load_active().set_index("New_Route_ID")["Route_Name"]

    def detour(o_xy, d_xy, v_xy):
        od = float(np.hypot(d_xy[0] - o_xy[0], d_xy[1] - o_xy[1]))
        ov = float(np.hypot(v_xy[0] - o_xy[0], v_xy[1] - o_xy[1]))
        vd = float(np.hypot(d_xy[0] - v_xy[0], d_xy[1] - v_xy[1]))
        return (ov + vd) / od if od > 0 else float("nan")

    routings = []
    for ck, g in permit_rows.groupby("corridor_key"):
        labels, reps = _cluster_vias(g["Via_Points_Raw"].tolist())
        n_via = len(reps)
        if n_via <= 1:
            continue
        g = g.assign(_via_cluster=labels)
        origin, dest = g["Origin"].iloc[0], g["Destination"].iloc[0]
        o_xy = to_utm(float(g["Origin_Lon"].iloc[0]), float(g["Origin_Lat"].iloc[0]))
        d_xy = to_utm(float(g["Dest_Lon"].iloc[0]), float(g["Dest_Lat"].iloc[0]))

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
        if survivor_id is not None and survivor_id in active_names.index:
            survivor_name = active_names.loc[survivor_id]
        ret_members = g[g["_via_cluster"] == retained]
        retained_label = (ret_members["Via_Points_Raw"].dropna().iloc[0]
                          if ret_members["Via_Points_Raw"].notna().any() else reps[retained])
        n_retained = int(len(ret_members))

        for cid in sorted(set(l for l in labels if l is not None)):
            if cid == retained:
                continue
            members = g[g["_via_cluster"] == cid]
            # Representative via label (first member) and the published pin
            # (first member permit with a geocode), exactly as before.
            via_label = members["Via_Points_Raw"].dropna().iloc[0] \
                if members["Via_Points_Raw"].notna().any() else reps[cid]
            published = None
            cands: dict[tuple[float, float], int] = {}
            for _, mm in members.iterrows():
                c = _parse_latlon(mm.get("Via_Points_Geocoded"))
                if c is None:
                    continue
                if published is None:
                    published = c
                cands[c] = cands.get(c, 0) + 1
            cand_list = []
            for (la, lo), npm in cands.items():
                v_xy = to_utm(lo, la)
                cand_list.append(dict(lat=la, lon=lo, n_permits=npm,
                                      detour_factor=round(detour(o_xy, d_xy, v_xy), 3)))
            supp_name = (members["Route_Name"].dropna().iloc[0]
                         if members["Route_Name"].notna().any() else None)
            routings.append(dict(
                corridor=f"{origin} -> {dest}",
                n_via_routings=n_via,
                suppressed_via=str(via_label),
                n_permits_on_routing=int(len(members)),
                retained_via=str(retained_label),
                n_permits_on_retained_routing=n_retained,
                survivor_route_id=survivor_id,
                survivor_route_name=survivor_name,
                suppressed_permit_name=supp_name,
                published_pin=published,
                candidates=cand_list,
            ))
    return routings


def _select_pin(rec, thr):
    """
    Pin used for a routing under a screening threshold (None = published rule).

    Among the geocodes carried by the routing's own permits, keep those whose
    detour factor is <= thr; use the one carried by most permits (ties: smaller
    detour, then coordinate). Returns (lat, lon) or None when none is plausible.
    """
    if thr is None:
        return rec["published_pin"]
    ok = [c for c in rec["candidates"]
          if np.isfinite(c["detour_factor"]) and c["detour_factor"] <= thr]
    if not ok:
        return None
    ok.sort(key=lambda c: (-c["n_permits"], c["detour_factor"], c["lat"], c["lon"]))
    return (ok[0]["lat"], ok[0]["lon"])


class _Walkshed:
    """400 m network walkshed from a point, built as a02 builds route catchments."""

    def __init__(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import a02_network_catchments as A02
        from scipy.spatial import cKDTree
        self.A02 = A02
        self.xy, self.indptr, self.indices, self.weights = A02.load_graph()
        self.tree = cKDTree(self.xy)

    def __call__(self, x_utm: float, y_utm: float):
        """Return (polygon or None, snap offset m)."""
        off, ni = self.tree.query([x_utm, y_utm], k=1)
        off = float(off)
        if off > self.A02.MAX_SNAP_M:
            return None, off
        nodes, ds = self.A02.dijkstra_budget(
            self.indptr, self.indices, self.weights, {int(ni): off}, WALK_BUDGET_M)
        return self.A02.network_catchment(self.xy, nodes, ds, TAU_M), off


def losers_analysis(cat):
    """
    Enumerate the 32 suppressed via-routings and cost each one against WorldPop,
    under every variant (geometry x pin screen). See the module docstring: the
    result is a proxy, reported as a range.
    """
    import rasterio
    import rasterstats
    from shapely import union_all
    from shapely.geometry import Point
    from shapely.ops import transform as shp_transform
    from pyproj import Transformer

    routings = _enumerate_routings()
    log.info("enumerated %d suppressed via-routings on %d corridors",
             len(routings), len({r["corridor"] for r in routings}))

    to_wgs = Transformer.from_crs(C.UTM, C.WGS84, always_xy=True).transform
    to_utm = Transformer.from_crs(C.WGS84, C.UTM, always_xy=True).transform
    covered_utm = union_all(list(cat.geometry.values))
    with rasterio.open(C.WORLDPOP_TIF) as src:
        nodata = src.nodata

    def pop_in(geom_utm):
        z = rasterstats.zonal_stats([shp_transform(to_wgs, geom_utm)],
                                    str(C.WORLDPOP_TIF), stats=["sum"], nodata=nodata)
        return float(z[0]["sum"] or 0.0)

    def pops(geom_utm):
        """(gross, uncovered) population of a polygon against the plan network."""
        gross = pop_in(geom_utm)
        resid = geom_utm.difference(covered_utm)
        return gross, (pop_in(resid) if not resid.is_empty else 0.0)

    # Walk graph for the network-walkshed variants. If it cannot be loaded the
    # network variants are reported NOT_COMPUTABLE rather than dropped silently.
    walker, walker_err = None, None
    try:
        walker = _Walkshed()
    except Exception as e:  # noqa: BLE001 - reported in the output, not swallowed
        walker_err = f"{type(e).__name__}: {e}"
        log.warning("walk graph unavailable (%s); network-walkshed variants skipped",
                    walker_err)

    geom_cache: dict[tuple[str, float, float], object] = {}
    snap_cache: dict[tuple[float, float], float] = {}

    def geom_for(kind, coord):
        k = (kind, coord[0], coord[1])
        if k in geom_cache:
            return geom_cache[k]
        x, y = to_utm(coord[1], coord[0])
        if kind == "disc":
            g = Point(x, y).buffer(WALK_BUDGET_M)
        else:
            g, off = walker(x, y)
            snap_cache[coord] = off
        geom_cache[k] = g
        return g

    pop_cache: dict[tuple[str, float, float], tuple[float, float]] = {}

    def pops_for(kind, coord):
        k = (kind, coord[0], coord[1])
        if k not in pop_cache:
            g = geom_for(kind, coord)
            pop_cache[k] = (0.0, 0.0) if g is None or g.is_empty else pops(g)
        return pop_cache[k]

    # ── every variant: geometry kind x pin rule ──
    pin_rules = [("published", None)] + [(f"screen{t:g}", t) for t in VIA_DETOUR_SWEEP]
    kinds = ["disc"] + (["walkshed"] if walker is not None else [])
    variants = {}
    per_routing = {}          # variant name -> list aligned to routings
    for kind in kinds:
        for rname, thr in pin_rules:
            vname = f"{kind}__{rname}"
            used, rows_v = [], []
            n_excl_pin, n_excl_off = 0, 0
            for rec in routings:
                pin = _select_pin(rec, thr)
                if pin is None:
                    n_excl_pin += 1
                    rows_v.append(dict(status="EXCLUDED" if rec["published_pin"] is not None
                                       else "NOT_COMPUTABLE", pin=None,
                                       gross=None, uncovered=None))
                    continue
                g = geom_for(kind, pin)
                if g is None:
                    n_excl_off += 1
                    rows_v.append(dict(status="EXCLUDED_OFF_NETWORK", pin=pin,
                                       gross=None, uncovered=None))
                    continue
                gr, un = pops_for(kind, pin)
                used.append(g)
                rows_v.append(dict(status="OK", pin=pin, gross=gr, uncovered=un))
            if used:
                u = union_all(used)
                dg, du = pops(u)
            else:
                dg = du = None
            variants[vname] = dict(
                geometry=("400 m straight-line disc around the single via point"
                          if kind == "disc" else
                          "400 m network walkshed from the via point (a02 walk "
                          "graph, 100 m off-network tail)"),
                pin_rule=("first geocode carried by the routing's permits "
                          "(published)" if thr is None else
                          f"plausible geocode (detour factor <= {thr:g}) carried by "
                          "most permits; routing excluded if none"),
                detour_threshold=thr,
                n_routings_total=len(routings),
                n_routings_costed=len(used),
                n_excluded_no_plausible_pin=n_excl_pin,
                n_excluded_off_network=n_excl_off,
                dedup_union_pop_within_400m=dg,
                dedup_union_pop_uncovered_within_400m=du,
            )
            per_routing[vname] = rows_v
            log.info("variant %-22s costed %2d/%d : union within 400 m %s, "
                     "uncovered %s", vname, len(used), len(routings),
                     f"{dg:,.0f}" if dg is not None else "n/a",
                     f"{du:,.0f}" if du is not None else "n/a")

    # ── per-routing table ──
    PRIM = f"disc__{'published'}"                       # the published method
    SCR = f"disc__screen{VIA_DETOUR_MAX:g}"             # screened disc
    NET = "walkshed__published"
    NETS = f"walkshed__screen{VIA_DETOUR_MAX:g}"
    rows = []
    for i, rec in enumerate(routings):
        pub = per_routing[PRIM][i]
        r = {k: v for k, v in rec.items() if k not in ("published_pin", "candidates")}
        pin = rec["published_pin"]
        r["via_lat"] = pin[0] if pin else None
        r["via_lon"] = pin[1] if pin else None
        # Screen outcome for the published pin.
        pub_df = next((c["detour_factor"] for c in rec["candidates"]
                       if pin and (c["lat"], c["lon"]) == pin), None)
        r["published_pin_detour_factor"] = pub_df
        sp = _select_pin(rec, VIA_DETOUR_MAX)
        if pin is None:
            r["pin_screen"] = "NO_COORDINATE"
        elif sp is None:
            r["pin_screen"] = "EXCLUDED_IMPLAUSIBLE_PIN"
        elif sp != pin:
            r["pin_screen"] = "REPAIRED_FROM_REGISTER"
            r["screened_lat"], r["screened_lon"] = sp
        else:
            r["pin_screen"] = "OK"
        if pin is None:
            r.update(pop_within_400m=None, pop_uncovered_within_400m=None,
                     status="NOT_COMPUTABLE",
                     reason="no geocoded via point in permit register")
        else:
            r.update(pop_within_400m=pub["gross"], pop_uncovered_within_400m=pub["uncovered"],
                     status="OK", reason="")
        for tag, vn in (("screened_disc", SCR), ("network_walkshed", NET),
                        ("screened_network_walkshed", NETS)):
            if vn in per_routing:
                v = per_routing[vn][i]
                r[f"pop_uncovered_{tag}"] = v["uncovered"]
                r[f"status_{tag}"] = v["status"]
        rows.append(r)
    losers = pd.DataFrame(rows)

    # ── summary ──
    pub_v = variants[PRIM]
    n_comp = int((losers["status"] == "OK").sum())
    ret_gt = losers[losers["n_permits_on_routing"] > losers["n_permits_on_retained_routing"]]
    excluded = losers[losers["status"] != "OK"][
        ["corridor", "suppressed_via", "n_permits_on_routing", "reason"]]
    flagged = losers[losers["pin_screen"].isin(
        ["EXCLUDED_IMPLAUSIBLE_PIN", "REPAIRED_FROM_REGISTER"])]
    flagged_rows = []
    for _, fr in flagged.iterrows():
        flagged_rows.append(dict(
            corridor=fr["corridor"], suppressed_via=fr["suppressed_via"],
            published_pin=[fr["via_lat"], fr["via_lon"]],
            published_pin_detour_factor=fr["published_pin_detour_factor"],
            outcome=fr["pin_screen"],
            replacement_pin=([fr["screened_lat"], fr["screened_lon"]]
                             if fr["pin_screen"] == "REPAIRED_FROM_REGISTER" else None),
            published_pin_uncovered_pop=fr["pop_uncovered_within_400m"]))

    ok_unc = {k: v["dedup_union_pop_uncovered_within_400m"] for k, v in variants.items()
              if v["dedup_union_pop_uncovered_within_400m"] is not None}
    ok_gross = {k: v["dedup_union_pop_within_400m"] for k, v in variants.items()
                if v["dedup_union_pop_within_400m"] is not None}
    rng = dict(
        n_variants=len(ok_unc),
        uncovered_min=min(ok_unc.values()), uncovered_min_variant=min(ok_unc, key=ok_unc.get),
        uncovered_max=max(ok_unc.values()), uncovered_max_variant=max(ok_unc, key=ok_unc.get),
        within_400m_min=min(ok_gross.values()), within_400m_min_variant=min(ok_gross, key=ok_gross.get),
        within_400m_max=max(ok_gross.values()), within_400m_max_variant=max(ok_gross, key=ok_gross.get),
        published_method_variant=PRIM,
        published_uncovered=pub_v["dedup_union_pop_uncovered_within_400m"],
        published_within_400m=pub_v["dedup_union_pop_within_400m"],
    )

    summary = dict(
        n_corridors_with_suppressed_routings=int(losers["corridor"].nunique()),
        n_suppressed_via_routings=int(len(losers)),
        n_computable=n_comp,
        n_not_computable=int((losers["status"] == "NOT_COMPUTABLE").sum()),
        excluded_routings=excluded.to_dict(orient="records"),
        excluded_routings_note=(
            "The excluded routing is TRC -> Hazratbal via Shalimar / Nishat / "
            "Nehru Park / Dalgate. The permit register carries no geocode for the "
            "label as written; of its component places only Dalgate has a register "
            "geocode elsewhere, and Dalgate alone would not represent a four-place "
            "Dal-shore routing, so it is not substituted. The totals are therefore "
            "for 31 of the 32 routings in every variant and are not a bound on "
            "the 32."),
        dedup_union_pop_within_400m=pub_v["dedup_union_pop_within_400m"],
        dedup_union_pop_uncovered_within_400m=pub_v["dedup_union_pop_uncovered_within_400m"],
        published_method_label=(
            "400 m straight-line disc around ONE geocoded via-place per dropped "
            "routing, minus the dissolved 400 m NETWORK-walk catchment of the "
            "plan. A PROXY: mixes a Euclidean 'before' with a network 'after', "
            "represents each routing by one point, and is neither an upper nor a "
            "lower bound."),
        method_label=("400 m straight-line disc around a single geocoded via-point "
                      "vs network catchment - a proxy"),
        range_across_variants=rng,
        variants=variants,
        screen=dict(
            rule=("pin implausible when (|origin-via| + |via-destination|) / "
                  "|origin-destination| > threshold; straight-line UTM 43N distances"),
            primary_threshold=VIA_DETOUR_MAX, sweep=list(VIA_DETOUR_SWEEP),
            flagged_at_primary_threshold=flagged_rows,
            n_flagged_at_primary_threshold=int(len(flagged_rows)),
            note=("MOMINABAD TENGPORA: the register's geocode for that compound "
                  "label is ~18 km from the Parimpora-Pantha Chowk corridor, but "
                  "the same routing cluster also carries the register's own "
                  "geocode for TENGPORA (the clustering treats the two labels as "
                  "one place), which is plausible and is used. 90FEET has a "
                  "single geocode, implausible by the screen, and no other "
                  "register coordinate: the routing is excluded, not re-pinned."),
        ),
        retained_routing_context=dict(
            n_suppressed_routings_with_more_permits_than_retained=int(len(ret_gt)),
            routings=ret_gt[["corridor", "suppressed_via", "n_permits_on_routing",
                             "retained_via", "n_permits_on_retained_routing",
                             "survivor_route_id"]].to_dict(orient="records"),
            note=("In each listed case the plan keeps the routing carried by FEWER "
                  "permits; which routing survives is whichever permit row the "
                  "engine kept, not a demand judgement."),
        ),
        walk_graph_error=walker_err,
        note=("Per-via populations overlap and must not be summed; the network "
              "figure is the deduplicated union of the suppressed-via 400 m "
              "walksheds. 'Uncovered' is the part of that walkshed outside the "
              "plan's dissolved network catchment. Descriptive, in-sample "
              "counts of WorldPop residents; not a count of riders and not a "
              "measurement of lost access."),
    )
    log.info("losers (published method): %d routings, %d costed; union within "
             "400 m %s, uncovered %s | range over %d variants: uncovered "
             "%s - %s", summary["n_suppressed_via_routings"], n_comp,
             f"{rng['published_within_400m']:,.0f}", f"{rng['published_uncovered']:,.0f}",
             rng["n_variants"], f"{rng['uncovered_min']:,.0f}", f"{rng['uncovered_max']:,.0f}")
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
        status="NOT_COMPUTABLE",
        before_gini="NOT_COMPUTABLE",
        before_zero_service_share="NOT_COMPUTABLE",
        before_gini_served_only="NOT_COMPUTABLE",
        reason=("The 458 merged permit records carry no routed line geometry on "
                "disk: the plan GeoJSON and the offline OSRM cache "
                "(data/cache/osrm_responses.json, 186 routes) both hold the 186 "
                "active routes only, and the permit register records origin, "
                "destination and via points but neither a routed alignment nor a "
                "headway. A pre-consolidation accessibility surface (with or "
                "without frequencies), and therefore the before-state Gini, the "
                "before-state zero-service share and the before-state Gini among "
                "served residents, cannot be built from real data. Only the "
                "after-state statistics are reported."),
        plan_effect_on_equity="not estimable from the data in this repository",
        after_gini_frequency_weighted=gini_block["gini_frequency_weighted"],
        after_zero_service_share=gini_block["share_population_zero_service"],
        after_gini_frequency_weighted_served_only=gini_block["gini_frequency_weighted_served_only"],
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
        dict(measure="Gini component from zero-service residents (z)",
             value=round(gini_block["gini_decomposition"]["frequency_weighted"]
                         ["component_zero_service"], 4)),
        dict(measure="Gini component from unequal frequency among served ((1-z)*G_served)",
             value=round(gini_block["gini_decomposition"]["frequency_weighted"]
                         ["component_unequal_among_served"], 4)),
        dict(measure="Before-state Gini / zero-service share / served-only Gini",
             value="NOT_COMPUTABLE"),
    ])
    C.write_table(gini_tab, "table05f_equity_gini",
                  "Population-weighted accessibility of the rationalised network "
                  "(after state; descriptive, in-sample; n = 642,634 inhabited "
                  "WorldPop pixels, 6.58 M residents). Accessibility is supply-side "
                  "departures/hour reachable within a 400 m network walk. G = z + "
                  "(1 - z) * G_served. The before state is not computable because "
                  "merged permits have no geometry, so the plan's effect on equity "
                  "is not estimable.")

    losers_out = losers.copy()
    int_cols = [c for c in losers_out.columns
                if c.startswith("pop_") and c not in ("pop_within_400m",)] + ["pop_within_400m"]
    for col in int_cols:
        losers_out[col] = losers_out[col].apply(
            lambda x: int(round(x)) if pd.notna(x) else None)
    for col in ("via_lat", "via_lon", "screened_lat", "screened_lon"):
        if col in losers_out.columns:
            losers_out[col] = losers_out[col].apply(
                lambda x: round(x, 5) if pd.notna(x) else None)
    tab_cols = ["corridor", "suppressed_via", "survivor_route_id", "survivor_route_name",
                "n_permits_on_routing", "retained_via", "n_permits_on_retained_routing",
                "pop_within_400m", "pop_uncovered_within_400m", "status", "pin_screen",
                "published_pin_detour_factor"]
    for extra in ("pop_uncovered_screened_disc", "pop_uncovered_network_walkshed",
                  "pop_uncovered_screened_network_walkshed"):
        if extra in losers_out.columns:
            tab_cols.append(extra)
    C.write_table(
        losers_out.sort_values(["corridor", "suppressed_via"])[tab_cols],
        "table05g_losers",
        "The 32 suppressed via-routings. pop_within_400m / pop_uncovered_within_"
        "400m = published proxy (400 m straight-line disc around ONE geocoded via-"
        "place, minus the plan's 400 m network-walk catchment); the other "
        "pop_uncovered_* columns are the same routing under a plausibility-"
        "screened pin and/or a network walkshed. Per-routing counts overlap and "
        "must not be summed. pin_screen: OK / REPAIRED_FROM_REGISTER / "
        "EXCLUDED_IMPLAUSIBLE_PIN / NO_COORDINATE (detour factor > 2).")

    var_rows = []
    for vn, v in losers_summary["variants"].items():
        var_rows.append({
            "Variant": vn,
            "Via-place catchment": "straight-line disc" if vn.startswith("disc") else "network walkshed",
            "Pin rule": ("published (first register geocode)" if v["detour_threshold"] is None
                         else f"plausible pin, detour factor <= {v['detour_threshold']:g}"),
            "Routings costed": f"{v['n_routings_costed']} of {v['n_routings_total']}",
            "Residents within 400 m (union)": (int(round(v["dedup_union_pop_within_400m"]))
                                               if v["dedup_union_pop_within_400m"] is not None else None),
            "Residents outside plan network (union)": (int(round(v["dedup_union_pop_uncovered_within_400m"]))
                                                       if v["dedup_union_pop_uncovered_within_400m"] is not None else None),
        })
    C.write_table(pd.DataFrame(var_rows), "table05g_losers_variants",
                  "Deduplicated residents near suppressed via-places that lie "
                  "outside the plan's network catchment, under every geometry x "
                  "pin-screen variant. disc__published is the figure quoted so "
                  "far (a proxy; 31 of 32 routings costed in every variant).")

    dec = gini_block["gini_decomposition"]["frequency_weighted"]
    rng = losers_summary["range_across_variants"]
    headline = dict(
        gini_frequency_weighted=gini_block["gini_frequency_weighted"],
        zero_service_share=gini_block["share_population_zero_service"],
        gini_served_only=gini_block["gini_frequency_weighted_served_only"],
        share_of_gini_from_zero_service=dec["share_of_gini_from_zero_service"],
        plan_effect_on_equity="not estimable (no before-state)",
        losers_published_proxy_uncovered=rng["published_uncovered"],
        losers_published_proxy_within_400m=rng["published_within_400m"],
        losers_uncovered_range=[rng["uncovered_min"], rng["uncovered_max"]],
        losers_uncovered_range_n_variants=rng["n_variants"],
        losers_n_routings_costed=losers_summary["n_computable"],
        losers_n_routings_total=losers_summary["n_suppressed_via_routings"],
        text=(
            f"Service is unequally spread across residents (frequency-weighted "
            f"accessibility Gini {gini_block['gini_frequency_weighted']:.3f}, "
            f"descriptive and in-sample), but "
            f"{100 * gini_block['share_population_zero_service']:.1f}% of residents "
            f"have no service at all and that share alone is "
            f"{100 * dec['share_of_gini_from_zero_service']:.0f}% of the Gini "
            f"(G = z + (1 - z) * G_served, G_served = "
            f"{gini_block['gini_frequency_weighted_served_only']:.3f} among "
            f"served residents). The plan's effect on equity is not estimable: "
            f"no before-state exists. Consolidation suppresses "
            f"{losers_summary['n_suppressed_via_routings']} alternative via-"
            f"routings on {losers_summary['n_corridors_with_suppressed_routings']} "
            f"corridors; for {losers_summary['n_computable']} of them a proxy "
            f"(400 m straight-line disc around one geocoded via-place vs the "
            f"network catchment) puts {rng['published_uncovered']:,.0f} residents "
            f"outside the plan network, and the figure ranges "
            f"{rng['uncovered_min']:,.0f} to {rng['uncovered_max']:,.0f} across "
            f"{rng['n_variants']} geometry x pin-screen variants. It is neither "
            f"an upper nor a lower bound."),
    )

    out = dict(
        status="OK",
        study_area_population=C.STUDY_AREA_POPULATION,
        accessibility_gini_after=gini_block,
        before_after=before_after,
        losers_summary=losers_summary,
        losers=losers_out.to_dict(orient="records"),
        headline=headline,
        interpretation=headline["text"],
    )
    C.write_result(out, "a12_equity_gini")
    log.info("done")


if __name__ == "__main__":
    main()
