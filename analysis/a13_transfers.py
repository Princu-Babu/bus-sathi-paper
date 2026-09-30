#!/usr/bin/env python
"""
a13_transfers.py — §5.11: what consolidation costs the passenger who now has to
change buses, and whether the wait it buys is large enough to pay for that.

The objection this module exists to answer. Collapsing 614 permits onto 186
services is defended on supply grounds: duplicated permits on one corridor are
wasted vehicles, and pooling them buys a shorter headway. The passenger-side
counter-argument is immediate and, in the interchange literature, decisive. A
rider who had a one-seat ride and now must change may be worse off even though
the published headway improved, because interchange carries a disutility far
larger than the clock time it consumes (Iseki & Taylor 2009; Guo & Wilson 2011).
A plan reporting only the headway improvement has reported half the ledger.

This module reports the other half, and the headline result is not the one the
plan would prefer. It is reported as computed.

What is computed.
  1. A route-stop bipartite graph over the 143 canonical stops of
     `Kashmir_Stops_Master_v4.csv` and the 186 active route geometries. RULE: a
     stop is SERVED by a route when it lies within the plan's own walk catchment
     radius (WALK_CATCHMENT_M = 400 m) of that route's routed alignment, measured
     in UTM zone 43N. Using the plan's own catchment keeps this consistent with
     the coverage results, and the threshold is swept (200/400/600/800 m).
  2. Minimum interchanges between every pair of canonical stops, by breadth-first
     search on the route-adjacency graph (two routes adjacent when they share a
     served stop). 0 = one route serves both; 1 = one change; and so on.
  3. A GEOMETRY AUDIT, because step 1 turned out to be contaminated. 14 of the
     130 active routes whose own name cites two canonical stops have a drawn
     alignment that never comes within 400 m of one of them — FDR-147 is named
     "Hazratbal to LD" and its line stops 1,134 m short of LD. Those defects
     fabricate interchanges that the service plan does not actually impose, so
     the distribution is also reported on a NAME-AUGMENTED graph that credits
     each route with the stops its own name claims. The true answer is bracketed
     by the two; neither is presented alone.
  4. The counterfactual, per suppressed permit: did its own origin-destination
     pair keep a one-seat ride in the rationalised plan, and how did its wait
     change? Reported per DISTINCT OD PAIR (71 of them), not per permit row —
     458 suppressed permits reduce to 71 distinct ODs, and quoting permit rows
     would count the 42 identical Hazratbal-LD permits as 42 findings.
  5. The break-even transfer penalty on the ODs that lose their one-seat ride.

THE HONESTY NOTE THAT MUST TRAVEL WITH EVERY NUMBER BELOW. The stop-pair shares
are counts of STOP PAIRS, not of PASSENGERS. No origin-destination matrix exists
for Kashmir Division — none was supplied, none is published, and the fare data
(§5.6) record boardings without alightings — so it is impossible to weight a pair
by how many people travel it. A network can look excellent on unweighted stop
pairs while forcing an interchange on exactly the corridors carrying the volume,
and this measure could not tell the difference. The result is TOPOLOGICAL: it
describes the shape of the network, not the experience of its riders, and must
never be quoted as a share of trips.

Secondary limitations, each biasing in a stated direction:
  * The canonical stop file is a route-TERMINUS registry built from geocoded
    endpoints, not a full stop inventory, so the graph is coarser than reality.
  * Catchment membership proxies "you can board here"; a route passing 300 m away
    with no safe crossing does not really serve a stop.
  * Interchange is assumed feasible wherever two routes reach the same stop.
    Interchange quality — shelter, kerb-to-kerb walk, information — is not
    modelled, and Iseki & Taylor (2009) show quality dominates the penalty.

Outputs
    data/derived/a13_transfers.json
    data/derived/a13_transfer_pairs.csv            per suppressed permit
    data/derived/a13_transfer_od.csv               per distinct OD pair
    paper/tables/table05i_transfers.{csv,md}              0/1/2+ distribution
    paper/tables/table05i_transfers_sensitivity.{csv,md}  catchment sweep
    paper/tables/table05i_transfers_breakeven.{csv,md}    break-even penalty
    paper/tables/table05i_transfers_geomaudit.{csv,md}    geometry defects

Usage
    python analysis/a13_transfers.py
"""
from __future__ import annotations

import itertools
import sys
from collections import deque
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a13")

CATCHMENT_M = C.PARAMETERS["WALK_CATCHMENT_M"]["value"]      # 400 m, the plan's own
CATCHMENT_SWEEP = (200.0, 400.0, 600.0, 800.0)
UNREACHABLE = 10 ** 6

# Candidate transfer penalties for the sensitivity sweep. NOT a calibrated value
# for Kashmir: no local stated-preference study exists. The range spans what the
# international literature reports for bus interchange so a reader can locate
# their own prior on the curve.
PENALTY_SWEEP_MIN = (0.0, 5.0, 10.0, 15.0, 20.0)

# Arrival models for the expected wait. kappa multiplies the headway.
#   0.5 — passengers arrive at random, service evenly spaced: E[W] = h/2.
#   1.0 — departures themselves Poisson (uncoordinated operators): E[W] = h.
# Both follow from E[W] = (E[H]/2)(1 + Var(H)/E[H]^2); the second is the
# Var(H) = E[H]^2 case. The plan is a single scheduled operator, so kappa = 0.5
# is right for it. The permit network is many uncoordinated permit-holders, so
# kappa = 1.0 is the defensible model for the baseline. That asymmetric pairing
# is the CENTRAL case; all four corners are reported.
KAPPA_EVEN, KAPPA_POISSON = 0.5, 1.0


# ── graph construction ───────────────────────────────────────────────────────
def stop_route_incidence(stops_utm, routes_utm, radius_m: float) -> np.ndarray:
    """
    Boolean stop x route matrix: does the route pass within `radius_m` of the stop?

    Buffering the line and testing containment is equivalent to a distance test
    but vectorises over stops.
    """
    inc = np.zeros((len(stops_utm), len(routes_utm)), dtype=bool)
    pts = stops_utm.geometry
    for j, geom in enumerate(routes_utm.geometry.values):
        inc[:, j] = pts.within(geom.buffer(radius_m)).to_numpy()
    return inc


def route_distance_matrix(inc: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    """
    Minimum interchanges between routes: BFS on the route-adjacency graph.

    Two routes are adjacent when a canonical stop falls in both catchments, which
    is the operational definition of "you can change here". The distance between
    routes is then the number of changes, and the stop-pair answer follows by
    minimising over the routes serving each endpoint.
    """
    counts = inc.T.astype(np.int32) @ inc.astype(np.int32)
    adj = counts > 0
    np.fill_diagonal(adj, False)
    n = adj.shape[0]
    dist = np.full((n, n), UNREACHABLE, dtype=np.int32)
    for r in range(n):
        dist[r, r] = 0
        q = deque([r])
        while q:
            u = q.popleft()
            for v in np.nonzero(adj[u])[0]:
                if dist[r, v] == UNREACHABLE:
                    dist[r, v] = dist[r, u] + 1
                    q.append(int(v))
    seen, comps = set(), 0
    for r in range(n):
        if r in seen:
            continue
        comps += 1
        q = deque([r])
        seen.add(r)
        while q:
            u = q.popleft()
            for v in np.nonzero(adj[u])[0]:
                if int(v) not in seen:
                    seen.add(int(v))
                    q.append(int(v))
    return dist, adj, comps


def pair_transfers(inc: np.ndarray, rdist: np.ndarray) -> np.ndarray:
    """Minimum interchanges for every unordered stop pair (i<j), flattened."""
    served = [np.nonzero(inc[i])[0] for i in range(inc.shape[0])]
    out = []
    for i, j in itertools.combinations(range(inc.shape[0]), 2):
        a, b = served[i], served[j]
        if a.size == 0 or b.size == 0:
            out.append(UNREACHABLE)
        else:
            out.append(int(rdist[np.ix_(a, b)].min()))
    return np.asarray(out, dtype=np.int64)


def classify(dists: np.ndarray) -> dict:
    total = int(dists.size)
    reach = dists < UNREACHABLE
    return dict(
        n_pairs=total,
        n_0=int((dists == 0).sum()), n_1=int((dists == 1).sum()),
        n_2=int((dists == 2).sum()), n_3plus=int(((dists >= 3) & reach).sum()),
        n_unreachable=int((~reach).sum()),
        pct_0=round(100.0 * (dists == 0).mean(), 2),
        pct_1=round(100.0 * (dists == 1).mean(), 2),
        pct_2plus=round(100.0 * ((dists >= 2) & reach).mean(), 2),
        pct_unreachable=round(100.0 * (~reach).mean(), 2),
    )


def name_terminals(route_name: str, known: set[str]) -> list[str]:
    """
    Canonical stops a route's own name claims as terminals.

    Names are the engine's cleaned "A to B" or "A to B via X Y" form (v3.3.7
    `_clean_route_name`). Only exact matches against the canonical stop register
    are accepted: a fuzzy match here would re-introduce the very name-matching
    error the v3.4.0 route-code rebuild removed.
    """
    head = str(route_name).split(" via ")[0]
    return [p.strip() for p in head.split(" to ") if p.strip() in known]


def geometry_audit(routes_utm, stop_geom: dict, radius_m: float) -> pd.DataFrame:
    """
    Does each route's drawn alignment reach the canonical stops its name cites?

    A route named "Hazratbal to LD" whose line never approaches LD cannot serve
    LD, so the transfer graph invents an interchange the service plan does not
    impose. This audit is the reason the distribution is reported twice.
    """
    known = set(stop_geom)
    rows = []
    for _, r in routes_utm.iterrows():
        hits = name_terminals(r["Route_Name"], known)
        if len(hits) < 2:
            continue
        for nm in hits[:2]:
            d = r.geometry.distance(stop_geom[nm])
            rows.append(dict(New_Route_ID=r["New_Route_ID"],
                             Route_Name=r["Route_Name"],
                             Route_KM=round(float(r["Route_KM"]), 1),
                             Named_Terminal=nm,
                             Distance_To_Own_Line_M=round(float(d)),
                             Within_Catchment=bool(d <= radius_m)))
    return pd.DataFrame(rows)


# ── the counterfactual ───────────────────────────────────────────────────────
def permit_baseline(plan: pd.DataFrame) -> pd.DataFrame:
    """
    Join every plan row that came from a permit back to its register entry.

    `Route_ID` "R0001" is row 0 of `existing-routes.csv` — the engine's own
    ordering, verified here rather than assumed. The 30 SSCL rows are synthetic
    backbone services with no permit and are excluded from the counterfactual,
    which is correct: nothing was suppressed to create them.
    """
    permits = pd.read_csv(C.PERMITS_CSV)
    pr = plan[plan["Route_ID"].astype(str).str.match(r"^R\d+$", na=False)].copy()
    pr["_idx"] = pr["Route_ID"].str[1:].astype(int) - 1
    if pr["_idx"].min() < 0 or pr["_idx"].max() >= len(permits):
        raise SystemExit("Route_ID does not index the permit register")
    j = pr.merge(permits.add_prefix("P_"), left_on="_idx", right_index=True,
                 how="left", validate="one_to_one")
    if j["P_Origin"].isna().any():
        raise SystemExit("permit join left unmatched rows")
    return j


def observed_duty_factor() -> dict:
    """
    What fraction of the operating day is a real vehicle actually in service?

    The baseline headway on a corridor carrying n permits is cycle/(n*duty). The
    naive choice duty = 1 asserts that every permitted vehicle ran the whole
    operating day, which no evidence supports. The Bus Sathi driver-GPS extract
    measures it directly: service minutes per vehicle-day against the observed
    network operating window.

    Two caveats, both stated in the output. The traces are from the SSCL e-bus
    operation, not from permit-holders, so transferability is assumed and
    unverified. And app capture is partial — the median driver appears on only 2
    of 131 calendar days — so observed service minutes are a LOWER bound on a
    vehicle's true daily duty. A lower duty means a longer baseline headway,
    which flatters the plan; the reported duty is therefore conservative in the
    plan's favour, and duty = 1 is carried as the opposite bound.
    """
    dd = pd.read_csv(C.GPS_PERMIT_OBSERVED_CSV.parent / "driver_days.csv")
    fs = pd.to_timedelta(dd["first_start"] + ":00").dt.total_seconds() / 60
    le = pd.to_timedelta(dd["last_end"] + ":00").dt.total_seconds() / 60
    window = float(le.quantile(0.95) - fs.quantile(0.05))
    return dict(
        n_driver_days=int(len(dd)), n_drivers=int(dd["driver"].nunique()),
        n_calendar_days=int(dd["day"].nunique()),
        operating_window_min=round(window, 1),
        service_min_p25=float(dd["service_min"].quantile(0.25)),
        service_min_median=float(dd["service_min"].median()),
        service_min_p75=float(dd["service_min"].quantile(0.75)),
        duty_p25=round(float(dd["service_min"].quantile(0.25)) / window, 4),
        duty_median=round(float(dd["service_min"].median()) / window, 4),
        duty_p75=round(float(dd["service_min"].quantile(0.75)) / window, 4),
        runs_per_vehicle_day_median=float(dd["n_runs"].median()),
        source="data/raw/gps/driver_days.csv (Bus Sathi driver GPS, Feb-Jun 2026)",
    )


def main() -> None:
    import geopandas as gpd
    from pyproj import Transformer
    from scipy.spatial import cKDTree

    stops = pd.read_csv(C.STOPS_MASTER)
    stops_utm = gpd.GeoDataFrame(
        stops, geometry=gpd.points_from_xy(stops["Longitude"], stops["Latitude"]),
        crs=C.WGS84).to_crs(C.UTM)
    routes = gpd.read_file(C.PLAN_GEOJSON).to_crs(C.UTM)
    stop_geom = dict(zip(stops_utm["Stop_Name"], stops_utm.geometry))
    log.info("canonical stops %d, active route geometries %d", len(stops), len(routes))

    # ── primary graph at the plan's own catchment ───────────────────────────
    inc = stop_route_incidence(stops_utm, routes, CATCHMENT_M)
    rdist, adj, n_components = route_distance_matrix(inc)
    dists = pair_transfers(inc, rdist)
    geom_dist = classify(dists)

    orphans = stops.loc[inc.sum(axis=1) == 0,
                        ["Master_Stop_Code", "Stop_Name", "District"]]
    log.info("incidences %d; mean %.1f stops/route, %.1f routes/stop; "
             "%d stop(s) served by no route; route graph components %d",
             int(inc.sum()), inc.sum(axis=0).mean(), inc.sum(axis=1).mean(),
             len(orphans), n_components)
    for _, o in orphans.iterrows():
        log.warning("  unserved canonical stop: %s (%s, %s) -> its %d pairs count "
                    "as unreachable, not as 2+", o["Stop_Name"],
                    o["Master_Stop_Code"], o["District"], len(stops) - 1)

    # ── geometry audit, and the name-augmented upper bound ──────────────────
    audit = geometry_audit(routes, stop_geom, CATCHMENT_M)
    defects = audit[~audit["Within_Catchment"]].sort_values(
        "Distance_To_Own_Line_M", ascending=False)
    n_testable = audit["New_Route_ID"].nunique()
    n_defect_routes = defects["New_Route_ID"].nunique()
    log.warning("geometry audit: %d of %d active routes whose name cites two "
                "canonical stops have a drawn line >%.0f m from one of them "
                "(worst %s: %s is %d m from its own alignment)",
                n_defect_routes, n_testable, CATCHMENT_M,
                defects.iloc[0]["New_Route_ID"], defects.iloc[0]["Named_Terminal"],
                int(defects.iloc[0]["Distance_To_Own_Line_M"]))

    known = set(stop_geom)
    stop_pos = {n: i for i, n in enumerate(stops["Stop_Name"])}
    inc_named = inc.copy()
    n_added = 0
    for j, rn in enumerate(routes["Route_Name"]):
        for nm in name_terminals(rn, known):
            i = stop_pos[nm]
            if not inc_named[i, j]:
                inc_named[i, j] = True
                n_added += 1
    rdist_n, adj_n, comps_n = route_distance_matrix(inc_named)
    named_dist = classify(pair_transfers(inc_named, rdist_n))
    log.info("name-augmented graph: +%d asserted incidences -> 0=%.2f%% 1=%.2f%% "
             "2+=%.2f%% unreachable=%.2f%% (components %d)", n_added,
             named_dist["pct_0"], named_dist["pct_1"], named_dist["pct_2plus"],
             named_dist["pct_unreachable"], comps_n)

    dist_tab = pd.DataFrame([
        {"Interchanges": lab,
         "Stop pairs (geometry)": geom_dist[k],
         "Share % (geometry)": round(100.0 * geom_dist[k] / geom_dist["n_pairs"], 2),
         "Stop pairs (name-augmented)": named_dist[k],
         "Share % (name-augmented)": round(100.0 * named_dist[k] / named_dist["n_pairs"], 2)}
        for lab, k in [("0 (one-seat ride)", "n_0"), ("1", "n_1"), ("2", "n_2"),
                       ("3 or more", "n_3plus"), ("not connected", "n_unreachable")]
    ])

    # ── catchment sensitivity ───────────────────────────────────────────────
    sweep = []
    for r in CATCHMENT_SWEEP:
        if r == CATCHMENT_M:
            inc_r, rd_r, comp_r = inc, rdist, n_components
        else:
            inc_r = stop_route_incidence(stops_utm, routes, r)
            rd_r, _, comp_r = route_distance_matrix(inc_r)
        cl = classify(pair_transfers(inc_r, rd_r))
        cl.update(catchment_m=r, route_graph_components=comp_r,
                  n_incidences=int(inc_r.sum()))
        sweep.append(cl)
        log.info("catchment %4.0f m: 0=%5.2f%%  1=%5.2f%%  2+=%5.2f%%  "
                 "unreachable=%4.2f%%  (components %d)", r, cl["pct_0"],
                 cl["pct_1"], cl["pct_2plus"], cl["pct_unreachable"], comp_r)
    sweep_tab = pd.DataFrame([{
        "Walk catchment (m)": s["catchment_m"],
        "0 transfers (%)": s["pct_0"], "1 transfer (%)": s["pct_1"],
        "2+ transfers (%)": s["pct_2plus"],
        "Not connected (%)": s["pct_unreachable"],
        "Route-graph components": s["route_graph_components"],
    } for s in sweep])

    # ── suppressed permits: did their own OD keep a one-seat ride? ──────────
    plan = C.load_plan()
    joined = permit_baseline(plan)
    merged = joined[joined["Action_Taken"] == C.MERGED_ACTION].copy()

    transformer = Transformer.from_crs(C.WGS84, C.UTM, always_xy=True)
    sx = np.array([g.x for g in stops_utm.geometry])
    sy = np.array([g.y for g in stops_utm.geometry])
    tree = cKDTree(np.column_stack([sx, sy]))

    def snap(lat, lon):
        x, y = transformer.transform(np.asarray(lon, float), np.asarray(lat, float))
        d, i = tree.query(np.column_stack([x, y]), k=1)
        return np.where(d <= CATCHMENT_M, i, -1)

    merged["_oi"] = snap(merged["P_Origin_Lat"], merged["P_Origin_Lon"])
    merged["_di"] = snap(merged["P_Dest_Lat"], merged["P_Dest_Lon"])
    n_unsnapped = int(((merged["_oi"] < 0) | (merged["_di"] < 0)).sum())
    usable = merged[(merged["_oi"] >= 0) & (merged["_di"] >= 0)
                    & (merged["_oi"] != merged["_di"])].copy()
    log.info("suppressed permits %d; %d could not snap both terminals to a "
             "canonical stop within %.0f m; %d usable, on %d ordered / %d "
             "undirected OD pairs", len(merged), n_unsnapped, CATCHMENT_M,
             len(usable), usable.groupby(["_oi", "_di"]).ngroups,
             usable.groupby([usable[["_oi", "_di"]].min(axis=1),
                             usable[["_oi", "_di"]].max(axis=1)]).ngroups)

    # Baseline one-seat supply for an OD is the number of register rows offering
    # exactly that OD, undirected. A register row is one permitted
    # vehicle-service (q01, D1). Using the whole merge group instead would
    # over-credit the baseline on corridors where the group is heterogeneous.
    def od_key(a, b):
        """Undirected stop-pair key, as a string so `.loc` is unambiguous."""
        i, j = sorted((int(a), int(b)))
        return f"{i}-{j}"

    usable["_od"] = [od_key(a, b) for a, b in zip(usable["_oi"], usable["_di"])]
    all_snap = merged[(merged["_oi"] >= 0) & (merged["_di"] >= 0)].copy()
    act = joined[joined["Action_Taken"].isin(C.ACTIVE_ACTIONS)].copy()
    act["_oi"] = snap(act["P_Origin_Lat"], act["P_Origin_Lon"])
    act["_di"] = snap(act["P_Dest_Lat"], act["P_Dest_Lon"])
    reg = pd.concat([all_snap, act[act["_oi"] >= 0][act.columns]], ignore_index=True)
    reg = reg[(reg["_oi"] >= 0) & (reg["_di"] >= 0) & (reg["_oi"] != reg["_di"])]
    reg["_od"] = [od_key(a, b) for a, b in zip(reg["_oi"], reg["_di"])]
    od_supply = reg.groupby("_od").agg(n_permits_same_od=("Route_ID", "size"),
                                       cycle_min=("Cycle_Time_Min", "mean"))

    served = [np.nonzero(inc[i])[0] for i in range(inc.shape[0])]
    served_n = [np.nonzero(inc_named[i])[0] for i in range(inc_named.shape[0])]
    plan_h = routes["Headway_Min"].to_numpy(float)

    def best_itinerary(i, j, srv, rd):
        """Minimum interchanges and the smallest total scheduled wait for it."""
        a, b = srv[i], srv[j]
        if a.size == 0 or b.size == 0:
            return None, None, None, None
        d = int(rd[np.ix_(a, b)].min())
        if d == 0:
            both = a[np.isin(a, b)]
            h = float(plan_h[both].min())
            return 0, KAPPA_EVEN * h, h, None
        if d == 1:
            best, pair = np.inf, (None, None)
            for r1 in a:
                for r2 in b:
                    if rd[r1, r2] == 1:
                        s = KAPPA_EVEN * (plan_h[r1] + plan_h[r2])
                        if s < best:
                            best, pair = s, (r1, r2)
            return 1, float(best), float(plan_h[pair[0]]), float(plan_h[pair[1]])
        return d, None, None, None

    duty = observed_duty_factor()
    log.info("observed duty factor (GPS, %d driver-days / %d drivers over %d "
             "calendar days): operating window %.0f min, service min/vehicle-day "
             "p25 %.0f / median %.0f / p75 %.0f -> duty %.3f / %.3f / %.3f",
             duty["n_driver_days"], duty["n_drivers"], duty["n_calendar_days"],
             duty["operating_window_min"], duty["service_min_p25"],
             duty["service_min_median"], duty["service_min_p75"],
             duty["duty_p25"], duty["duty_median"], duty["duty_p75"])

    rows = []
    for odk, grp in usable.groupby("_od"):
        i, j = (int(x) for x in odk.split("-"))
        d_g, w_g, h1_g, h2_g = best_itinerary(i, j, served, rdist)
        d_n, w_n, h1_n, h2_n = best_itinerary(i, j, served_n, rdist_n)
        sup = od_supply.loc[odk]
        rows.append(dict(
            origin_stop=stops.iloc[i]["Stop_Name"], dest_stop=stops.iloc[j]["Stop_Name"],
            origin_code=stops.iloc[i]["Master_Stop_Code"],
            dest_code=stops.iloc[j]["Master_Stop_Code"],
            n_suppressed_permits=int(len(grp)),
            n_register_rows_same_od=int(sup["n_permits_same_od"]),
            baseline_cycle_min=round(float(sup["cycle_min"]), 2),
            successors=";".join(sorted(set(grp["New_Route_ID"].astype(str)))),
            plan_transfers_geometry=d_g, plan_wait_geometry_min=w_g,
            plan_headway_leg1_min=h1_g, plan_headway_leg2_min=h2_g,
            plan_transfers_named=d_n, plan_wait_named_min=w_n,
        ))
    od = pd.DataFrame(rows)

    # Baseline expected wait as a function of duty and arrival model:
    #   h_base = cycle / (n * duty);  E[W] = kappa * h_base
    def base_wait(n, cycle, dty, kappa):
        return kappa * cycle / (np.asarray(n, float) * dty)

    n_od, cyc = od["n_register_rows_same_od"].to_numpy(float), od["baseline_cycle_min"].to_numpy(float)
    for lab, col in (("geometry", "plan_transfers_geometry"),
                     ("named", "plan_transfers_named")):
        vc = od[col].value_counts().sort_index()
        log.info("distinct suppressed ODs by interchanges in the plan (%s graph): %s",
                 lab, {f"{int(k)}": int(v) for k, v in vc.items()})

    # ── wait ledger and break-even, over the four corners ───────────────────
    corners, be_rows = [], []
    for dlab, dval in (("all-day (duty=1.00)", 1.0),
                       (f"observed median (duty={duty['duty_median']:.3f})", duty["duty_median"]),
                       (f"observed p25 (duty={duty['duty_p25']:.3f})", duty["duty_p25"]),
                       (f"observed p75 (duty={duty['duty_p75']:.3f})", duty["duty_p75"])):
        for klab, kv in (("even spacing E[W]=h/2", KAPPA_EVEN),
                         ("Poisson departures E[W]=h", KAPPA_POISSON)):
            wb = base_wait(n_od, cyc, dval, kv)
            wp = od["plan_wait_geometry_min"].to_numpy(float)
            ok = np.isfinite(wp)
            delta = wp - wb                     # >0 means the plan waits longer
            is1 = (od["plan_transfers_geometry"] == 1).to_numpy() & ok
            is0 = (od["plan_transfers_geometry"] == 0).to_numpy() & ok
            corners.append(dict(
                duty_case=dlab, arrival_model=klab,
                central=(dval == duty["duty_median"] and kv == KAPPA_POISSON),
                n_od_evaluated=int(ok.sum()),
                median_baseline_wait_min=round(float(np.median(wb[ok])), 2),
                median_plan_wait_min=round(float(np.median(wp[ok])), 2),
                n_od_wait_worse=int((delta[ok] > 0).sum()),
                pct_od_wait_worse=round(100.0 * (delta[ok] > 0).mean(), 1),
                median_wait_change_min=round(float(np.median(delta[ok])), 2),
                n_od_losing_one_seat=int(is1.sum()),
                breakeven_penalty_min_median=(
                    round(float(np.median(wb[is1] - wp[is1])), 2) if is1.any() else None),
                breakeven_penalty_min_min=(
                    round(float((wb[is1] - wp[is1]).min()), 2) if is1.any() else None),
                breakeven_penalty_min_max=(
                    round(float((wb[is1] - wp[is1]).max()), 2) if is1.any() else None),
                n_breakeven_positive=int(((wb[is1] - wp[is1]) > 0).sum()) if is1.any() else 0,
                n_od_kept_one_seat_but_longer_wait=int((delta[is0] > 0).sum()),
            ))

    central = [c for c in corners if c["central"]][0]
    # Break-even duty factor per OD: the duty at which baseline and plan waits are
    # equal, i.e. duty* = kappa * cycle / (n * plan_wait). Above it, the permit
    # network offered the shorter wait. Reported because it converts an
    # unverifiable assumption into a single testable threshold.
    wp_all = od["plan_wait_geometry_min"].to_numpy(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        duty_star = KAPPA_POISSON * cyc / (n_od * wp_all)
    od["breakeven_duty_factor"] = np.round(duty_star, 4)
    od["plan_wait_worse_at_observed_duty"] = (
        wp_all > base_wait(n_od, cyc, duty["duty_median"], KAPPA_POISSON))

    losers = od[od["plan_transfers_geometry"] == 1].copy()
    if losers.empty:
        breakeven = dict(status="NOT_COMPUTABLE",
                         reason="no distinct suppressed OD falls to exactly one "
                                "transfer in the rationalised plan")
        be_tab = pd.DataFrame([{"note": breakeven["reason"]}])
    else:
        sens = []
        for dlab, dval in (("all-day (duty=1.00)", 1.0),
                           (f"observed median (duty={duty['duty_median']:.3f})",
                            duty["duty_median"])):
            wb = base_wait(losers["n_register_rows_same_od"], losers["baseline_cycle_min"],
                           dval, KAPPA_POISSON).to_numpy(float)
            p = wb - losers["plan_wait_geometry_min"].to_numpy(float)
            for pen in PENALTY_SWEEP_MIN:
                sens.append(dict(duty_case=dlab, assumed_transfer_penalty_min=pen,
                                 n_od_worse_off=int((p < pen).sum()),
                                 n_od_total=int(p.size),
                                 pct_od_worse_off=round(100.0 * (p < pen).mean(), 1)))
            losers[f"breakeven_penalty_min__duty_{dval:.3f}"] = np.round(p, 2)
        wb_c = base_wait(losers["n_register_rows_same_od"], losers["baseline_cycle_min"],
                         duty["duty_median"], KAPPA_POISSON).to_numpy(float)
        p_c = wb_c - losers["plan_wait_geometry_min"].to_numpy(float)
        breakeven = dict(
            status="OK",
            unit="distinct origin-destination pair of canonical stops",
            n_distinct_od=int(len(losers)),
            n_underlying_suppressed_permits=int(losers["n_suppressed_permits"].sum()),
            central_case=("baseline Poisson departures with the observed median "
                          "duty factor; plan evenly spaced"),
            central_breakeven_penalty_min=[round(float(x), 2) for x in p_c],
            central_breakeven_penalty_min_median=round(float(np.median(p_c)), 2),
            n_positive_breakeven=int((p_c > 0).sum()),
            interpretation=(
                "A POSITIVE break-even is the transfer penalty at which the wait "
                "saving is exactly cancelled: below it the passenger gains. A "
                "NON-POSITIVE break-even means the plan's two waits already "
                "exceed the single baseline wait, so no transfer penalty is "
                "needed to make the passenger worse off and the consolidation "
                "cannot be defended on wait time for that pair."),
            penalty_sensitivity=sens,
            affected_pairs=losers[[
                "origin_stop", "dest_stop", "n_suppressed_permits",
                "n_register_rows_same_od", "baseline_cycle_min", "successors",
                "plan_headway_leg1_min", "plan_headway_leg2_min",
                "plan_wait_geometry_min", "plan_transfers_named",
                "breakeven_duty_factor"]].to_dict(orient="records"),
        )
        be_tab = pd.DataFrame([{
            "Baseline duty case": s["duty_case"],
            "Assumed transfer penalty (min)": s["assumed_transfer_penalty_min"],
            "OD pairs worse off": s["n_od_worse_off"],
            "of": s["n_od_total"],
            "Share worse off (%)": s["pct_od_worse_off"],
        } for s in sens])
        log.info("break-even transfer penalty over %d DISTINCT OD pairs that lose "
                 "their one-seat ride (%d underlying permits), central case: "
                 "median %.2f min, %d of %d positive",
                 len(losers), int(losers["n_suppressed_permits"].sum()),
                 float(np.median(p_c)), int((p_c > 0).sum()), len(losers))
        for _, L in losers.iterrows():
            log.info("  %-12s -> %-12s : %2d register permits, baseline cycle "
                     "%.0f min; plan = %d transfer via %s at %.0f+%.0f min "
                     "headway; break-even duty %.3f",
                     L["origin_stop"], L["dest_stop"],
                     int(L["n_register_rows_same_od"]), L["baseline_cycle_min"],
                     int(L["plan_transfers_geometry"]), L["successors"],
                     L["plan_headway_leg1_min"] or 0, L["plan_headway_leg2_min"] or 0,
                     L["breakeven_duty_factor"])

    for c in corners:
        log.info("%-42s | %-26s | baseline wait %5.2f vs plan %5.2f min; "
                 "%3d/%3d ODs (%5.1f%%) wait LONGER under the plan%s",
                 c["duty_case"], c["arrival_model"],
                 c["median_baseline_wait_min"], c["median_plan_wait_min"],
                 c["n_od_wait_worse"], c["n_od_evaluated"], c["pct_od_wait_worse"],
                 "   <-- CENTRAL" if c["central"] else "")

    # ── emit ────────────────────────────────────────────────────────────────
    C.write_table(dist_tab, "table05i_transfers",
                  f"Minimum interchanges between the {len(stops)} canonical stops "
                  f"of the rationalised network ({CATCHMENT_M:.0f} m walk "
                  f"catchment), on the drawn geometry and on the name-augmented "
                  f"graph. Stop pairs, NOT demand-weighted.")
    C.write_table(sweep_tab, "table05i_transfers_sensitivity",
                  "Sensitivity of the interchange distribution to the walk "
                  "catchment radius")
    C.write_table(be_tab, "table05i_transfers_breakeven",
                  "Distinct suppressed origin-destination pairs made worse off, "
                  "by assumed transfer penalty and baseline duty factor")
    C.write_table(defects.reset_index(drop=True), "table05i_transfers_geomaudit",
                  "Active routes whose drawn alignment does not reach a canonical "
                  "stop named in their own route name")
    usable.drop(columns=[c for c in usable.columns if c.startswith("P_Via")]) \
          .to_csv(C.DERIVED / "a13_transfer_pairs.csv", index=False)
    od.to_csv(C.DERIVED / "a13_transfer_od.csv", index=False)

    out = dict(
        status="OK",
        demand_weighting=(
            "NONE. These are shares of STOP PAIRS. No origin-destination matrix "
            "exists for Kashmir Division and the fare data record boardings "
            "without alightings, so no passenger weighting is possible. The "
            "result is topological and must not be quoted as a share of trips."),
        graph=dict(
            n_canonical_stops=int(len(stops)), n_active_routes=int(len(routes)),
            walk_catchment_m=CATCHMENT_M,
            catchment_rule=("a stop is served by a route when it lies within the "
                            "plan's own 400 m walk catchment of the routed "
                            "alignment, in UTM zone 43N"),
            n_stop_route_incidences=int(inc.sum()),
            mean_stops_per_route=round(float(inc.sum(axis=0).mean()), 2),
            mean_routes_per_stop=round(float(inc.sum(axis=1).mean()), 2),
            n_unserved_stops=int(len(orphans)),
            unserved_stops=orphans.to_dict(orient="records"),
            route_graph_components=int(n_components),
            route_graph_edges=int(adj.sum() // 2),
        ),
        distribution_on_drawn_geometry=geom_dist,
        distribution_name_augmented=named_dist,
        bracketing_note=(
            "The two distributions bracket the truth. The drawn-geometry graph "
            "understates connectivity because 14 route alignments do not reach a "
            "terminal their own name claims; the name-augmented graph overstates "
            "it because a name is an intention, not a routed path."),
        geometry_audit=dict(
            n_routes_testable=int(n_testable),
            n_routes_not_testable=int(len(routes) - n_testable),
            not_testable_reason=("fewer than two of the route's name terminals "
                                 "match a canonical stop exactly; no fuzzy "
                                 "matching is used"),
            n_routes_with_defect=int(n_defect_routes),
            pct_routes_with_defect=round(100.0 * n_defect_routes / n_testable, 1),
            n_named_incidences_added=int(n_added),
            defects=defects.to_dict(orient="records"),
            caveat=("Some defects involve a generic district-town terminal "
                    "(\"Srinagar\"), a single gazetteer pin that a route may "
                    "legitimately terminate far from; those are gazetteer "
                    "coarseness rather than a misdrawn line. Cases naming a "
                    "specific place (LD, Chadora, JVC, Dalgate, TRC) are "
                    "genuine endpoint defects."),
        ),
        catchment_sensitivity=sweep,
        wait_model=dict(
            formula="E[W] = (E[H]/2) * (1 + Var(H)/E[H]^2)",
            even_spacing="E[W] = h/2 when departures are evenly spaced (kappa=0.5)",
            poisson="E[W] = h when departures are themselves Poisson (kappa=1.0)",
            assignment=("The plan is one scheduled operator, so kappa=0.5 applies "
                        "to it. The permit network is many uncoordinated "
                        "permit-holders, so kappa=1.0 is the defensible baseline "
                        "model. That asymmetric pairing is the central case; all "
                        "four corners are reported."),
            justification="Welding (1957); Osuna & Newell (1972)",
            caveat=("Random passenger arrival is empirically supported only at "
                    "short headways. At the 20-50 minute headways this plan uses, "
                    "passengers time their arrival to the timetable and the "
                    "realised wait falls well below h/2 (Bowman & Turnquist "
                    "1981). Both sides of the comparison are inflated by this, so "
                    "the break-even magnitudes are an upper bound, not a forecast."),
        ),
        baseline_model=dict(
            description=(
                "The counterfactual is the permit network. One register row is "
                "one permitted vehicle-service (q01 D1), so an OD offered by n "
                "register rows was offered by n vehicles; spread over the "
                "corridor cycle with duty factor d they give headway "
                "cycle/(n*d). A suppressed permit gave a one-seat ride between "
                "its own registered origin and destination."),
            supply_definition=("register rows with exactly this origin-destination "
                               "pair of canonical stops, undirected - NOT the "
                               "whole merge group, which would over-credit the "
                               "baseline where the group is heterogeneous"),
            duty_factor_observed=duty,
            duty_factor_note=(
                "duty=1 asserts every permitted vehicle ran the whole operating "
                "day; no evidence supports it, and it is the bound harshest on "
                "the plan. The GPS-observed duty is a LOWER bound (partial app "
                "capture), so it is the bound most favourable to the plan. The "
                "true value lies between, and the direction of the result is "
                "reported at both."),
            n_suppressed_permits=int(len(merged)),
            n_terminals_unsnappable=n_unsnapped,
            n_usable_suppressed_permits=int(len(usable)),
            n_distinct_od_pairs=int(len(od)),
            max_register_rows_on_one_od=int(od["n_register_rows_same_od"].max()),
            median_register_rows_per_od=float(od["n_register_rows_same_od"].median()),
        ),
        suppressed_od_outcomes_geometry={
            str(int(k)): int(v) for k, v in
            od["plan_transfers_geometry"].value_counts().sort_index().items()},
        suppressed_od_outcomes_name_augmented={
            str(int(k)): int(v) for k, v in
            od["plan_transfers_named"].value_counts().sort_index().items()},
        wait_ledger_corners=corners,
        central_case=central,
        headline=(
            f"Of {len(od)} distinct suppressed origin-destination pairs, "
            f"{int((od['plan_transfers_geometry'] == 0).sum())} keep a one-seat "
            f"ride and {int((od['plan_transfers_geometry'] == 1).sum())} fall to "
            f"one interchange. In the central case "
            f"{central['n_od_wait_worse']} of {central['n_od_evaluated']} "
            f"({central['pct_od_wait_worse']}%) wait LONGER under the plan than "
            f"under the permit network, before any transfer penalty is charged. "
            f"Consolidation on the heavily duplicated corridors therefore cannot "
            f"be defended on passenger wait; its case rests on vehicle "
            f"productivity, operating cost and congestion, not on headway."),
        breakeven=breakeven,
        penalty_sweep_is_not_a_calibration=(
            "The 0-20 minute sweep is a sensitivity range, not an estimate. No "
            "stated-preference study of interchange disutility exists for Kashmir "
            "and none was conducted here, so no single penalty is asserted. The "
            "cited literature establishes only that the penalty is substantial "
            "and varies with interchange quality."),
        citations=[
            "Welding, P.I. (1957) The instability of a close-interval service. "
            "Operational Research Quarterly 8(3): 133-142.",
            "Osuna, E.E. & Newell, G.F. (1972) Control strategies for an "
            "idealized public transportation system. Transportation Science "
            "6(1): 52-72.",
            "Bowman, L.A. & Turnquist, M.A. (1981) Service frequency, schedule "
            "reliability and passenger wait times at transit stops. "
            "Transportation Research Part A 15(6): 465-471.",
            "Iseki, H. & Taylor, B.D. (2009) Not all transfers are created "
            "equal: towards a framework relating transfer connectivity to travel "
            "behaviour. Transport Reviews 29(6): 777-800.",
            "Guo, Z. & Wilson, N.H.M. (2011) Assessing the cost of transfer "
            "inconvenience in public transport systems: a case study of the "
            "London Underground. Transportation Research Part A 45(2): 91-104.",
            "Wardman, M. (2004) Public transport values of time. Transport "
            "Policy 11(4): 363-377.",
            "Vuchic, V.R. (2005) Urban Transit: Operations, Planning and "
            "Economics. Hoboken, NJ: John Wiley & Sons.",
        ],
    )
    C.write_result(out, "a13_transfers")

    log.info("stop-pair interchange distribution over %d pairs (drawn geometry): "
             "0 = %.2f%%, 1 = %.2f%%, 2+ = %.2f%%, not connected = %.2f%% "
             "(TOPOLOGICAL, not demand-weighted)", geom_dist["n_pairs"],
             geom_dist["pct_0"], geom_dist["pct_1"], geom_dist["pct_2plus"],
             geom_dist["pct_unreachable"])
    log.info("HEADLINE │ %s", out["headline"])


if __name__ == "__main__":
    main()
