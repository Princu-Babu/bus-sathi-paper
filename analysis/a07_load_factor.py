#!/usr/bin/env python
"""
a07_load_factor.py — how full would the planned buses be? Offered capacity set
against (i) the one observed boarding series in the region and (ii) the plan's
own quarantined demand proxy.

Two anchors, never merged.

  Observed (e-bus backbone only). CHALO publishes monthly boardings and bus-trips
  for the 30 SSCL routes (12-month mean) and the hourly boarding profile for
  April 2026 (a05). Boardings per bus-trip TODAY is therefore observed. The plan
  runs the same 30 routes at 15 minutes with more buses. Holding ridership at
  today's level — i.e. before any frequency response — boardings per planned
  trip fall in proportion to the trip increase. That is the honest "day-one"
  load; the ridership growth needed to restore today's boardings per trip is the
  corresponding break-even, and it is reported as a requirement, not a forecast.
  CHALO's "Trip Count" is ambiguous between one-way and round trips; both
  readings are carried.

  Proxy (whole network). The plan's Daily_Demand_Pax is Eq. 8 — the quarantined
  plausibility term the paper says never sizes the fleet. It is used here only
  to express an implied peak-hour boarding-to-capacity ratio per route, with the
  peak-hour factor measured by a05 (10.67% of daily boardings in the peak hour).
  This is NOT a maximum-load-section load factor (no on-board load profile
  exists); it is labelled boarding-to-capacity throughout.

Offered peak-hour capacity per route = (60 / headway) * mean vehicle capacity,
the mean weighted by the route's HPV/MPV/LPV mix at design capacities 60/35/20
(engine VEHICLE_CAPACITY_*).

Outputs  data/derived/a07_load_factor.json, data/derived/a07_route_load.csv,
         paper/tables/table05l_load_factor.{csv,md}
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a07")

DAYS = {"January": 31, "Feburary": 28, "February": 28, "March": 31, "April": 30, "May": 31,
        "June": 30, "July": 31, "August": 31, "September": 30, "October": 31,
        "November": 30, "December": 31}
CHALO_9M, CHALO_12M = 73, 25          # chalo_deployed_buses.csv TOTAL row


def num(v) -> float:
    s = re.sub(r"[^\d.]", "", str(v))
    return float(s) if s else np.nan


def main() -> None:
    a = C.load_active().copy()
    cap = C.VEHICLE_CAPACITY
    fleet = a[["HPV_Count", "MPV_Count", "LPV_Count"]].sum(axis=1).replace(0, np.nan)
    a["mean_capacity"] = (a["HPV_Count"] * cap["HPV"] + a["MPV_Count"] * cap["MPV"]
                          + a["LPV_Count"] * cap["LPV"]) / fleet
    a["peak_hour_capacity"] = 60.0 / a["Headway_Min"] * a["mean_capacity"]

    a05 = C.read_result("a05_headway_timeofday")
    phf = a05["peak_hour_factor_pct"] / 100.0
    a["proxy_peak_hour_boardings"] = a["Daily_Demand_Pax"] * phf
    a["proxy_boarding_to_capacity"] = a["proxy_peak_hour_boardings"] / a["peak_hour_capacity"]

    # Observed anchor on the backbone.
    rid = pd.read_csv(C.CHALO_RIDERSHIP_CSV)
    rid = rid[rid["Month"].notna() & rid["Trip Count"].notna()].copy()
    rid["days"] = rid["Month"].str.strip().map(DAYS)
    daily_pax = float(rid["Total"].map(num).sum() / rid["days"].sum())
    daily_trips = float(rid["Trip Count"].map(num).sum() / rid["days"].sum())
    chalo_mean_cap = (CHALO_9M * cap["MPV"] + CHALO_12M * cap["HPV"]) / (CHALO_9M + CHALO_12M)
    sscl = a[a["CMP_Trunk"].astype(bool)]
    plan_oneway_trips = float(sscl["Daily_Trips"].sum())
    readings = {}
    for label, oneway_today in (("trip_count_is_one_way", daily_trips),
                                ("trip_count_is_round_trip", 2 * daily_trips)):
        per_trip_today = daily_pax / oneway_today
        per_trip_plan = daily_pax / plan_oneway_trips
        readings[label] = dict(
            oneway_trips_today=oneway_today,
            boardings_per_oneway_trip_today=per_trip_today,
            boardings_per_seat_slot_today=per_trip_today / chalo_mean_cap,
            plan_oneway_trips=plan_oneway_trips,
            boardings_per_oneway_trip_plan_day_one=per_trip_plan,
            trip_multiplier=plan_oneway_trips / oneway_today,
            ridership_growth_to_hold_today_per_trip=plan_oneway_trips / oneway_today,
        )

    q = a["proxy_boarding_to_capacity"]
    by_cls = []
    for cls, s in a.groupby("Route_Type"):
        by_cls.append(dict(Class=cls, Routes=len(s),
                           **{"Peak-hour capacity (median)": round(float(s["peak_hour_capacity"].median())),
                              "Proxy boarding/capacity (median)": round(float(s["proxy_boarding_to_capacity"].median()), 3),
                              "Routes > 0.85": int((s["proxy_boarding_to_capacity"] > 0.85).sum()),
                              "Routes < 0.40": int((s["proxy_boarding_to_capacity"] < 0.40).sum())}))
    by_cls.append(dict(Class="Network", Routes=len(a),
                       **{"Peak-hour capacity (median)": round(float(a["peak_hour_capacity"].median())),
                          "Proxy boarding/capacity (median)": round(float(q.median()), 3),
                          "Routes > 0.85": int((q > 0.85).sum()), "Routes < 0.40": int((q < 0.40).sum())}))
    C.write_table(pd.DataFrame(by_cls), "table05l_load_factor",
                  f"Offered peak-hour capacity vs the quarantined demand proxy (peak-hour factor "
                  f"{100*phf:.2f}%, a05); boarding-to-capacity, not max-load-section load")

    a[["New_Route_ID", "Route_Name", "Route_Type", "Headway_Min", "mean_capacity",
       "peak_hour_capacity", "Daily_Demand_Pax", "proxy_peak_hour_boardings",
       "proxy_boarding_to_capacity"]].to_csv(C.DERIVED / "a07_route_load.csv", index=False)
    C.write_result(dict(
        vehicle_capacity=cap, peak_hour_factor=phf,
        observed_backbone=dict(chalo_daily_boardings=daily_pax, chalo_daily_trip_count=daily_trips,
                               chalo_mean_vehicle_capacity=chalo_mean_cap, readings=readings,
                               note="Day-one boardings per trip hold ridership at today's level; "
                                    "the growth figure is a requirement, not a forecast."),
        proxy_network=dict(median=float(q.median()), p90=float(q.quantile(0.9)),
                           n_above_085=int((q > 0.85).sum()), n_below_040=int((q < 0.40).sum()),
                           total_proxy_daily_demand=float(a["Daily_Demand_Pax"].sum()),
                           caveat="Eq. 8 proxy (quarantined); boarding-to-capacity, not load."),
    ), "a07_load_factor")
    for k, r in readings.items():
        log.info("%s: today %.1f boardings/one-way trip (%.2f per seat-slot); plan day-one %.1f; "
                 "growth to hold %.2fx", k, r["boardings_per_oneway_trip_today"],
                 r["boardings_per_seat_slot_today"], r["boardings_per_oneway_trip_plan_day_one"],
                 r["ridership_growth_to_hold_today_per_trip"])
    log.info("proxy peak boarding/capacity median %.3f; %d routes < 0.40", q.median(), (q < 0.40).sum())


if __name__ == "__main__":
    main()
