#!/usr/bin/env python
"""
v02_benchmark.py — validation channel V2: consistency of the plan's e-bus
backbone with the one operator that publishes its operations (CHALO / SSCL).

Circularity, stated before any result. The CHALO aggregates are not independent
of the plan. (1) The same published ridership anchors the capture scale kappa in
the quarantined plausibility term (Eq. 8). (2) The engine's SSCL fleet is floored
at CHALO's empirical deployment on routes where the formula would give fewer
buses (fleet_model: 2 of 30 routes). (3) The 30 backbone alignments ARE the CHALO
routes. V2 is therefore a consistency check of the plan against the operator it
was built around, not an independent validation, and it is reported that way.

The comparison. CHALO operates 98 buses on 30 routes at its current frequency;
the plan runs the same 30 routes at a 15-minute headway. Buses scale with
frequency at fixed cycle time, so the like-for-like reference is CHALO's fleet
scaled to 15 minutes:

    h_eff    = service_minutes / (daily bus-trips per route)       (CHALO, 12-month mean)
    F_scaled = 98 * h_eff / 15

and the pre-registered test is |F_plan / F_scaled - 1| <= 15%. The service day
behind h_eff is an assumption (the engine's cross_evaluate used 16 h); it is
swept over 13–16 h because the result depends on it and the sweep shows how.

Also reported, per route (n = 30): rank agreement between CHALO's deployed
buses and the plan's recommended buses (Spearman), which tests whether the plan
puts more buses where the operator already does — the one part of V2 that is not
mechanically forced by the floor.

Inputs    data/raw/chalo_ridership.csv, data/raw/chalo_deployed_buses.csv, plan CSV
Outputs   data/derived/v02_benchmark.json, paper/tables/table06f_v02_benchmark.{csv,md}
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import fleet_model as F  # noqa: E402

log = C.get_logger("v02")

TOLERANCE = 0.15
TARGET_HEADWAY = 15.0
SERVICE_HOURS = (13.0, 14.0, 15.0, 16.0)
ENGINE_SERVICE_HOURS = 16.0
DAYS = {"January": 31, "Feburary": 28, "February": 28, "March": 31, "April": 30, "May": 31,
        "June": 30, "July": 31, "August": 31, "September": 30, "October": 31,
        "November": 30, "December": 31}


def num(v) -> float:
    s = re.sub(r"[^\d.]", "", str(v))
    return float(s) if s else np.nan


def main() -> None:
    from scipy.stats import spearmanr

    rid = pd.read_csv(C.CHALO_RIDERSHIP_CSV)
    rid = rid[rid["Month"].notna() & rid["Trip Count"].notna()].copy()
    rid["days"] = rid["Month"].str.strip().map(DAYS)
    for c in ("Trip Count", "Total", "Operated KM"):
        rid[c] = rid[c].map(num)
    months = int(len(rid))
    daily_trips = float(rid["Trip Count"].sum() / rid["days"].sum())
    daily_pax = float(rid["Total"].sum() / rid["days"].sum())
    daily_km = float(rid["Operated KM"].sum() / rid["days"].sum())

    dep = pd.read_csv(C.CHALO_DEPLOYED_CSV)
    dep["route_no"] = pd.to_numeric(dep["PROPSED ROUTE NO"], errors="coerce").ffill()
    dep = dep[dep["route_no"].notna() & (dep["PROPSED ROUTE NO"].astype(str) != "TOTAL")]
    per_route = dep.groupby("route_no")["New Deployement"].sum(min_count=1)
    per_route = pd.to_numeric(per_route, errors="coerce").fillna(0)
    chalo_fleet = int(per_route.sum())
    n_routes = int(per_route.index.nunique())

    arr = F.load_arrays()
    a = arr.df
    sscl = a[a["CMP_Trunk"].astype(bool)].copy()
    sscl["route_no"] = sscl["CMP_Route_ID"].str.extract(r"(\d+)").astype(float)
    plan_fleet = int(sscl["Fleet_Required"].sum())
    n_floored = int((arr.sscl_floor > 0).sum())

    trips_per_route = daily_trips / n_routes
    sweep = []
    for h in SERVICE_HOURS:
        h_eff = h * 60.0 / trips_per_route
        scaled = chalo_fleet * h_eff / TARGET_HEADWAY
        ratio = plan_fleet / scaled
        sweep.append(dict(service_hours=h, chalo_effective_headway_min=round(h_eff, 1),
                          chalo_scaled_fleet=round(scaled, 1), plan_fleet=plan_fleet,
                          ratio=round(ratio, 3), within_tolerance=bool(abs(ratio - 1) <= TOLERANCE)))
    sweep = pd.DataFrame(sweep)
    eng = sweep[sweep["service_hours"] == ENGINE_SERVICE_HOURS].iloc[0]

    m = sscl.merge(per_route.rename("chalo_buses"), left_on="route_no", right_index=True, how="left")
    rho, p = spearmanr(m["chalo_buses"], m["Fleet_Required"])
    rho_cyc, p_cyc = spearmanr(m["chalo_buses"], m["Cycle_Time_Min"])

    tab = sweep.rename(columns={
        "service_hours": "Service day (h)", "chalo_effective_headway_min": "CHALO effective headway (min)",
        "chalo_scaled_fleet": "CHALO fleet scaled to 15 min", "plan_fleet": "Plan SSCL fleet",
        "ratio": "Plan / scaled", "within_tolerance": "Within ±15%"})
    C.write_table(tab, "table06f_v02_benchmark",
                  f"Validation V2 (consistency check, circular — see text): plan e-bus fleet "
                  f"vs CHALO's {chalo_fleet} buses scaled to a 15-min headway ({months}-month mean)")

    out = dict(
        circularity=["CHALO ridership anchors kappa in Eq. 8",
                     f"engine floors SSCL fleet at CHALO deployment on {n_floored} of 30 routes",
                     "the 30 backbone alignments are the CHALO routes"],
        months=months, chalo_daily_trips=daily_trips, chalo_daily_pax=daily_pax,
        chalo_daily_operated_km=daily_km, chalo_fleet=chalo_fleet, n_routes=n_routes,
        plan_sscl_fleet=plan_fleet, n_routes_floored_by_chalo=n_floored,
        sweep=sweep.to_dict(orient="records"),
        engine_assumption=dict(service_hours=ENGINE_SERVICE_HOURS, ratio=float(eng["ratio"]),
                               within_tolerance=bool(eng["within_tolerance"])),
        ratio_range=[float(sweep["ratio"].min()), float(sweep["ratio"].max())],
        n_assumptions_within_tolerance=int(sweep["within_tolerance"].sum()),
        tolerance=TOLERANCE,
        route_rank=dict(n=int(m["chalo_buses"].notna().sum()), spearman_fleet=float(rho),
                        p_fleet=float(p), spearman_chalo_vs_cycle=float(rho_cyc), p_cycle=float(p_cyc)),
    )
    C.write_result(out, "v02_benchmark")
    log.info("CHALO %d buses, %.0f trips/day (%.1f/route), %d-month mean", chalo_fleet,
             daily_trips, trips_per_route, months)
    for r in sweep.itertuples():
        log.info("  %2.0f h: h_eff %.1f min, scaled %.0f, plan %d, ratio %.3f %s", r.service_hours,
                 r.chalo_effective_headway_min, r.chalo_scaled_fleet, r.plan_fleet, r.ratio,
                 "PASS" if r.within_tolerance else "FAIL")
    log.info("route rank: rho(CHALO buses, plan fleet) = %.3f (p=%.3g)", rho, p)


if __name__ == "__main__":
    main()
