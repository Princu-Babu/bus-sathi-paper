#!/usr/bin/env python
"""
a06_deadhead.py — non-revenue (deadhead) running between depot and route, as a
share of bus-kilometres. The plan sizes service kilometres only; deadhead is
the part of operating cost and bus-hours it does not see.

The data gap, stated first. There is no depot register for Kashmir Division in
any input: the permit register names no depot, the plan carries none, and the
e-bus operator's depot locations are not published in the CHALO aggregates. A
deadhead figure therefore cannot be MEASURED here. What can be done honestly is
to bound it between two explicit, reproducible depot assumptions, and to report
both — not to pick one:

  D0  Terminal parking. Buses lay over at a route terminus (the prevailing
      practice of Kashmir's private minibus and matador operators, who park at
      the terminal or at the owner's home near it). Deadhead = 0.
  D1  District depot. Every bus pulls out from and returns to its district
      headquarters bus stand once per day. The headquarters stand is the stop
      master entry named after its district (e.g. "Anantnag" AN-01-01); where no
      such entry exists the district's stops' mean position is used and flagged.
      Depot-to-route distance is the straight line to the NEARER terminus,
      scaled by the route's own measured circuity (Route_KM / terminus-to-
      terminus straight line, clipped to [1.1, 2.0]) so that no external road
      factor is assumed. Two deadhead legs per bus per day.

Denominator: in-service kilometres per bus-day = Daily_KM / Fleet_Required from
the plan (16-hour service day, as the plan computes it). Reported per route,
per class and network-wide, as deadhead share = D / (D + in-service km).

The literature range often quoted (5–12% of bus-kilometres) is NOT used as an
input; D1 is compared with it after the fact.

Outputs  data/derived/a06_deadhead.json, data/derived/a06_route_deadhead.csv,
         paper/tables/table05k_deadhead.{csv,md}
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a06")

CIRCUITY_CLIP = (1.1, 2.0)
LEGS_PER_DAY = 2


def hav_km(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def main() -> None:
    import geopandas as gpd

    geo = gpd.read_file(C.PLAN_GEOJSON)
    act = C.load_active()
    ends = []
    for _, r in geo.iterrows():
        g = r.geometry
        line = g.geoms[0] if g.geom_type == "MultiLineString" else g
        last = g.geoms[-1] if g.geom_type == "MultiLineString" else g
        (x0, y0), (x1, y1) = line.coords[0], last.coords[-1]
        ends.append(dict(New_Route_ID=r["New_Route_ID"], s_lat=y0, s_lon=x0, e_lat=y1, e_lon=x1))
    df = act.merge(pd.DataFrame(ends), on="New_Route_ID", how="left")

    stops = pd.read_csv(C.STOPS_MASTER)
    hq = {}
    for d in C.DISTRICTS:
        m = stops[(stops["District"] == d) & (stops["Stop_Name"].str.strip().str.lower() == d.lower())]
        if len(m):
            hq[d] = (float(m.iloc[0]["Latitude"]), float(m.iloc[0]["Longitude"]), "named_stop")
        else:
            s = stops[stops["District"] == d]
            hq[d] = (float(s["Latitude"].mean()), float(s["Longitude"].mean()), "stop_mean_FLAG")
    hq_df = pd.DataFrame([dict(district=k, lat=v[0], lon=v[1], basis=v[2]) for k, v in hq.items()])

    # Nearest district HQ to the nearer terminus.
    best = np.full(len(df), np.inf)
    best_d = np.empty(len(df), dtype=object)
    for d, (la, lo, _) in hq.items():
        dist = np.minimum(hav_km(df["s_lat"], df["s_lon"], la, lo),
                          hav_km(df["e_lat"], df["e_lon"], la, lo))
        upd = dist < best
        best[upd], best_d[upd] = dist[upd], d
    crow = hav_km(df["s_lat"], df["s_lon"], df["e_lat"], df["e_lon"])
    circ = np.clip(df["Route_KM"] / np.where(crow > 0.2, crow, np.nan), *CIRCUITY_CLIP)
    circ = np.where(np.isfinite(circ), circ, np.nanmedian(circ))
    df["depot_district"] = best_d
    df["depot_leg_km"] = best * circ
    df["circuity"] = circ
    df["service_km_per_bus_day"] = df["Daily_KM"] / df["Fleet_Required"]
    df["deadhead_km_per_bus_day_D1"] = LEGS_PER_DAY * df["depot_leg_km"]
    df["deadhead_share_D1"] = df["deadhead_km_per_bus_day_D1"] / (
        df["deadhead_km_per_bus_day_D1"] + df["service_km_per_bus_day"])

    # Alternative denominator: the OBSERVED operating day. The plan's Daily_KM
    # assumes every bus runs the full 16-hour day (~320 service km/bus/day);
    # driver GPS shows a median of 217 in-service minutes per vehicle-day
    # (a13 duty factor 0.24). At the route's own cycle time that is
    # 217 / cycle round trips of 2 * Route_KM each.
    obs_min = C.read_result("a13_transfers")["baseline_model"]["duty_factor_observed"]["service_min_median"]
    df["service_km_per_bus_day_observed"] = obs_min / df["Cycle_Time_Min"] * 2 * df["Route_KM"]
    df["deadhead_share_D1_observed_day"] = df["deadhead_km_per_bus_day_D1"] / (
        df["deadhead_km_per_bus_day_D1"] + df["service_km_per_bus_day_observed"])

    fleet = df["Fleet_Required"]
    net_obs_serv = float((df["service_km_per_bus_day_observed"] * fleet).sum())
    net_dead = float((df["deadhead_km_per_bus_day_D1"] * fleet).sum())
    net_serv = float(df["Daily_KM"].sum())
    rows = []
    for cls, s in df.groupby("Route_Type"):
        d = float((s["deadhead_km_per_bus_day_D1"] * s["Fleet_Required"]).sum())
        v = float(s["Daily_KM"].sum())
        vo = float((s["service_km_per_bus_day_observed"] * s["Fleet_Required"]).sum())
        rows.append(dict(Class=cls, Routes=len(s), Buses=int(s["Fleet_Required"].sum()),
                         **{"Service km/day": round(v), "Deadhead km/day (D1)": round(d),
                            "Deadhead share D0": "0%", "Deadhead share D1": f"{100*d/(d+v):.1f}%",
                            "D1, observed operating day": f"{100*d/(d+vo):.1f}%",
                            "Median depot leg (km)": round(float(s["depot_leg_km"].median()), 1)}))
    rows.append(dict(Class="Network", Routes=len(df), Buses=int(fleet.sum()),
                     **{"Service km/day": round(net_serv), "Deadhead km/day (D1)": round(net_dead),
                        "Deadhead share D0": "0%",
                        "Deadhead share D1": f"{100*net_dead/(net_dead+net_serv):.1f}%",
                        "D1, observed operating day": f"{100*net_dead/(net_dead+net_obs_serv):.1f}%",
                        "Median depot leg (km)": round(float(df["depot_leg_km"].median()), 1)}))
    C.write_table(pd.DataFrame(rows), "table05k_deadhead",
                  "Depot deadhead bounded by two depot assumptions (no depot register exists)")
    df[["New_Route_ID", "Route_Name", "Route_Type", "Fleet_Required", "depot_district",
        "depot_leg_km", "circuity", "service_km_per_bus_day", "deadhead_km_per_bus_day_D1",
        "deadhead_share_D1", "service_km_per_bus_day_observed",
        "deadhead_share_D1_observed_day"]].to_csv(C.DERIVED / "a06_route_deadhead.csv", index=False)

    share = net_dead / (net_dead + net_serv)
    C.write_result(dict(
        status="BOUNDED_NOT_MEASURED",
        reason="No depot register exists in any input; deadhead is bounded by two stated assumptions.",
        assumptions=dict(D0="terminal parking, deadhead = 0",
                         D1="district-HQ depot, two legs/day, nearer terminus, route's own circuity"),
        district_hq=hq_df.to_dict(orient="records"),
        network=dict(service_km_per_day=net_serv, deadhead_km_per_day_D1=net_dead,
                     deadhead_share_D0=0.0, deadhead_share_D1=share),
        route_share_D1=dict(median=float(df["deadhead_share_D1"].median()),
                            p90=float(df["deadhead_share_D1"].quantile(0.9)),
                            max=float(df["deadhead_share_D1"].max())),
        observed_day=dict(service_min_per_bus_day=obs_min,
                          service_km_per_day=net_obs_serv,
                          deadhead_share_D1=net_dead / (net_dead + net_obs_serv),
                          plan_service_km_per_bus_day=net_serv / float(fleet.sum()),
                          observed_service_km_per_bus_day=net_obs_serv / float(fleet.sum())),
        literature_range_for_comparison=[0.05, 0.12],
        d1_inside_literature_range=bool(0.05 <= share <= 0.12),
        service_km_basis="plan Daily_KM (16-h service day at the published headway)",
    ), "a06_deadhead")
    log.info("observed-day denominator: %.0f vs plan %.0f service km/bus/day -> D1 %.1f%%",
             net_obs_serv / fleet.sum(), net_serv / fleet.sum(), 100 * net_dead / (net_dead + net_obs_serv))
    log.info("deadhead share network: D0 0%%, D1 %.1f%% (%.0f of %.0f km/day); route median %.1f%%",
             100 * share, net_dead, net_serv + net_dead, 100 * df["deadhead_share_D1"].median())


if __name__ == "__main__":
    main()
