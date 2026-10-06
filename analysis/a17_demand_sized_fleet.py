#!/usr/bin/env python
"""
a17_demand_sized_fleet.py — what fleet would the plan's 186 routes need if headways
were sized to the plan's own demand estimate instead of to policy bands?

Question (referee). The published headways are policy bands (15/20/35 min city,
35-50 min rural), not demand outputs. On the plan's demand proxy the median route
runs about 11 % full (a07, direction-corrected). What fleet would the SAME routes
need if headway were set so that peak-hour load equals a target load factor?

Definitions (all reuse a07's corrected, direction-consistent quantities)
  D_i       Daily_Demand_Pax: whole-route boardings, both directions (engine Eq. 8).
  phf       peak-hour factor, a05 JSON `peak_hour_factor_pct` (CHALO Hourly_Passenger_
            Count.csv, April 2026, share of daily boardings in the busiest hour).
  cap_i     mean vehicle capacity of the route's published HPV/MPV/LPV mix at design
            capacities common.VEHICLE_CAPACITY (60/35/20) — identical to a07.
  load_i(h) = D_i * m * phf / (2 * (60/h) * cap_i)        [a07 corrected ratio]
            Two-direction boardings over two-direction capacity, i.e. a SYMMETRIC
            50/50 direction split of the peak hour. Equivalent to peak-direction
            load with split 0.5. It is boarding-to-capacity, NOT a max-load-section
            load factor (no on-board load profile exists).
  h_dem_i   = 120 * cap_i * rho / (D_i * m * phf)    headway at which load = rho.
  Fleet     fleet_model.fleet_from_cycle(cycle = published Cycle_Time_Min, headway,
            spare = 1.15): op = max(1, ceil(cycle/max(1,h))); N = max(ceil(op*spare),
            floor); SSCL empirical floor kept (binds on 2 routes). Because
            ceil(1 * 1.15) = 2 the arithmetic minimum per route is 2 vehicles.
  Policies (max headway)
    a  none: h = h_dem
    b  60-minute lifeline ceiling: h = min(h_dem, 60)
    c  plan ceilings: h = min(h_dem, 35 city [Urban, Peri_Urban] | 50 rural
       [Regional_District] | 15 for the 30 SSCL backbone routes, the operator design
       target common.HEADWAY_SSCL_TRUNK_MIN)
    d  (reference) each route's own PUBLISHED headway as ceiling: h = min(h_dem,
       h_published). Demand-sized only where demand needs more than the plan gives.
       With no demand binding this reproduces the published fleet.
  Floors: grid uses a minimum of 1 vehicle per route (as asked; the spare ratio makes
  the effective minimum 2). A sensitivity applies the plan's own floors (2/2/1).
  Demand level m: 1, and the a07 backbone growth multipliers (round-trip reading
  2.2446, one-way reading 4.4892), read from a07_load_factor.json.

Limitations are emitted as data (`limitations`). This is a scenario calculation on
a proxy: D_i is a corridor-share walkshed estimate scaled by a capture factor
kappa (engine PHASE4_CORRIDOR_CAPTURE_SCALE = 0.33, CL-59) calibrated on CHALO
e-bus ridership; it is not observed demand on these routes.

Outputs  data/derived/a17_demand_sized_fleet.json, a17_route_demand_fleet.csv,
         paper/tables/table05n_demand_sized_fleet.{csv,md}
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import fleet_model as FM  # noqa: E402

log = C.get_logger("a17")

LOADS = (0.50, 0.70, 0.85)
POLICIES = ("a", "b", "c", "d")
POLICY_LABEL = {
    "a": "(a) none",
    "b": "(b) 60-min ceiling",
    "c": "(c) plan ceilings 35 city / 50 rural / 15 backbone",
    "d": "(d) published headway as ceiling (reference)",
}
LIFELINE_CEILING_MIN = 60.0
CITY_CEILING_MIN = float(C.HEADWAY_MAX_MIN)                      # 35
RURAL_CEILING_MIN = float(max(C.REGIONAL_HEADWAY_BUCKETS))       # 50
BACKBONE_CEILING_MIN = float(C.HEADWAY_SSCL_TRUNK_MIN)           # 15
CENTRAL = dict(rho=0.70, policy="c", mult_name="x1")
TOL = 1e-9


def load_inputs():
    arr = FM.load_arrays()
    a = arr.df
    cap = C.VEHICLE_CAPACITY
    n = a[["HPV_Count", "MPV_Count", "LPV_Count"]].to_numpy(float)
    total = n.sum(axis=1)
    assert (total > 0).all() and (total == a["Fleet_Required"].to_numpy(float)).all()
    mean_cap = (n[:, 0] * cap["HPV"] + n[:, 1] * cap["MPV"] + n[:, 2] * cap["LPV"]) / total
    a05 = C.read_result("a05_headway_timeofday")
    a07 = C.read_result("a07_load_factor")
    phf = a05["peak_hour_factor_pct"] / 100.0
    r = a07["observed_backbone"]["readings"]
    mults = {"x1": 1.0,
             "x2.24": float(r["trip_count_is_round_trip"]["trip_multiplier"]),
             "x4.49": float(r["trip_count_is_one_way"]["trip_multiplier"])}
    return arr, mean_cap, n, phf, mults, a05, a07


def ceilings(arr, policy):
    if policy == "a":
        return np.full(len(arr.km), np.inf)
    if policy == "b":
        return np.full(len(arr.km), LIFELINE_CEILING_MIN)
    if policy == "c":
        base = np.where(arr.rtype == "Regional_District", RURAL_CEILING_MIN, CITY_CEILING_MIN)
        return np.where(arr.sscl, BACKBONE_CEILING_MIN, base)
    if policy == "d":
        return arr.headway.astype(float)
    raise ValueError(policy)


def demand_headway(demand_pax, mean_cap, phf, rho, mult):
    """Headway (min) at which two-direction peak-hour boardings / two-direction capacity = rho."""
    d = demand_pax * mult * phf
    with np.errstate(divide="ignore"):
        return np.where(d > 0, 120.0 * mean_cap * rho / np.where(d > 0, d, 1.0), np.inf)


def split_by_class(fleet, shares):
    """Largest-remainder split of each route's fleet over HPV/MPV/LPV in the published mix."""
    out = np.zeros((len(fleet), 3), dtype=int)
    for i, (f, s) in enumerate(zip(fleet, shares)):
        raw = f * s
        base = np.floor(raw + 1e-9).astype(int)
        rem = int(f - base.sum())
        order = np.argsort(-(raw - base), kind="stable")
        for k in order[:rem]:
            base[k] += 1
        out[i] = base
    return out


def size(arr, mean_cap, shares, phf, rho, mult, policy, floor_mode="one", ceil_override=None,
         demand=None):
    """Return dict with headway, fleet, class split, demand_bound mask for one grid cell."""
    a = arr.df
    d = a["Daily_Demand_Pax"].to_numpy(float) if demand is None else demand
    h_dem = demand_headway(d, mean_cap, phf, rho, mult)
    ceil = ceilings(arr, policy) if ceil_override is None else ceil_override
    h = np.minimum(h_dem, ceil)
    a2 = arr if floor_mode == "plan" else dataclasses.replace(arr, floor=np.ones_like(arr.floor))
    n = FM.fleet_from_cycle(a2, arr.cycle_pub, FM.BASE["FLEET_SPARE_RATIO"], headway=h)
    h_eff = np.maximum(1.0, h)
    bound = h_dem < ceil - TOL
    return dict(h_dem=h_dem, h=h, h_eff=h_eff, fleet=n, split=split_by_class(n, shares),
                demand_bound=bound, n_below_1min=int((h_dem < 1.0).sum()))


def cell_record(arr, res, rho, mult_name, mult, policy):
    n, h = res["fleet"], res["h_eff"]
    pub = int(arr.fleet_pub.sum())
    s = res["split"]
    return dict(
        target_load=rho, policy=policy, policy_label=POLICY_LABEL[policy],
        demand_level=mult_name, demand_multiplier=mult,
        fleet_total=int(n.sum()), HPV=int(s[:, 0].sum()), MPV=int(s[:, 1].sum()), LPV=int(s[:, 2].sum()),
        fleet_share_of_published=float(n.sum() / pub), fleet_published=pub,
        fleet_backbone=int(n[arr.sscl].sum()), fleet_non_backbone=int(n[~arr.sscl].sum()),
        n_routes=int(len(n)), n_demand_bound=int(res["demand_bound"].sum()),
        n_demand_bound_non_backbone=int(res["demand_bound"][~arr.sscl].sum()),
        n_demand_headway_shorter_than_published=int((res["h_dem"] < arr.headway - TOL).sum()),
        n_demand_headway_below_1_min_clamped=res["n_below_1min"],
        headway_median=float(np.median(h)), headway_p10=float(np.percentile(h, 10)),
        headway_p90=float(np.percentile(h, 90)), share_headway_over_60=float((h > 60.0).mean()),
    )


def main() -> None:
    arr, mean_cap, counts, phf, mults, a05, a07 = load_inputs()
    a = arr.df
    shares = counts / counts.sum(axis=1, keepdims=True)
    n_routes = len(a)
    pub_total = int(arr.fleet_pub.sum())
    D = a["Daily_Demand_Pax"].to_numpy(float)

    # consistency with a07 (same definition, not re-derived differently)
    load_pub = D * phf / (2.0 * (60.0 / arr.headway) * mean_cap)
    a07_med = a07["proxy_network_both_directions"]["median"]
    assert abs(float(np.median(load_pub)) - a07_med) < 1e-9, (np.median(load_pub), a07_med)
    assert bool((arr.headway[arr.sscl] == BACKBONE_CEILING_MIN).all())

    # ---- grid ---------------------------------------------------------------
    grid, results = [], {}
    for rho in LOADS:
        for mname, m in mults.items():
            for pol in POLICIES:
                res = size(arr, mean_cap, shares, phf, rho, m, pol)
                results[(rho, mname, pol)] = res
                grid.append(cell_record(arr, res, rho, mname, m, pol))
    gdf = pd.DataFrame(grid)

    # ---- decomposition of the published fleet at rho 0.70, policy (a), x1 ----
    dec_res = results[(0.70, "x1", "a")]
    dem_fleet = dec_res["fleet"]
    pub = arr.fleet_pub
    explained = np.minimum(pub, dem_fleet)
    excess = np.maximum(0, pub - dem_fleet)      # published buses above demand-sized need
    deficit = np.maximum(0, dem_fleet - pub)     # buses demand would need beyond the plan

    def dec(mask, label):
        return dict(group=label, n_routes=int(mask.sum()), published=int(pub[mask].sum()),
                    demand_sized_fleet_policy_a=int(dem_fleet[mask].sum()),
                    explained_by_demand=int(explained[mask].sum()),
                    above_demand_need_service_standard=int(excess[mask].sum()),
                    demand_need_beyond_plan=int(deficit[mask].sum()),
                    net_published_minus_demand=int(pub[mask].sum() - dem_fleet[mask].sum()),
                    n_routes_published_above_demand=int((excess[mask] > 0).sum()),
                    n_routes_published_below_demand=int((deficit[mask] > 0).sum()))
    allm = np.ones(n_routes, bool)
    decomposition = dict(
        definition=("At target load 0.70, policy (a) no ceiling, demand x1, minimum 1 vehicle: demand-sized "
                    "fleet per route. 'Explained by demand' = sum over routes of min(published, demand-sized); "
                    "'above demand need' = sum of max(0, published - demand-sized), the buses that exist because "
                    "the service-standard headways (and spare/floor arithmetic common to both) are more frequent "
                    "than demand needs; 'demand need beyond plan' = routes where the proxy would need MORE buses "
                    "than published. net = published - demand-sized = above - beyond."),
        base=f"{n_routes} active routes, published fleet {pub_total}",
        all_routes=dec(allm, "all 186"), backbone=dec(arr.sscl, "30 SSCL backbone"),
        non_backbone=dec(~arr.sscl, "156 non-backbone"),
        backbone_note=("Backbone headway (15 min) is the operator's design target and its fleet is floored at "
                       "the operator's own deployment on 2 routes; the backbone 'service-standard' share is "
                       "therefore a design choice by SSCL, not a policy ceiling set by the plan."),
        in_sample=True, is_model_proxy_not_observation=True)

    # ---- central case --------------------------------------------------------
    central = results[(CENTRAL["rho"], CENTRAL["mult_name"], CENTRAL["policy"])]
    central_d = results[(0.70, "x1", "d")]
    cen_rec = cell_record(arr, central, 0.70, "x1", 1.0, "c")
    cen_rec_d = cell_record(arr, central_d, 0.70, "x1", 1.0, "d")

    # ---- sensitivities --------------------------------------------------------
    sens = dict(plan_floors=[], backbone_at_35_in_policy_c=[])
    for mname, m in mults.items():
        r_pf = size(arr, mean_cap, shares, phf, 0.70, m, "c", floor_mode="plan")
        sens["plan_floors"].append(dict(demand_level=mname, policy="c", target_load=0.70,
                                        fleet_total=int(r_pf["fleet"].sum()),
                                        note="plan floors 2 urban / 2 peri-urban / 1 regional"))
        ov = np.where(arr.rtype == "Regional_District", RURAL_CEILING_MIN, CITY_CEILING_MIN)
        r_bb = size(arr, mean_cap, shares, phf, 0.70, m, "c", ceil_override=ov)
        sens["backbone_at_35_in_policy_c"].append(dict(demand_level=mname, target_load=0.70,
                                                       fleet_total=int(r_bb["fleet"].sum()),
                                                       backbone_fleet=int(r_bb["fleet"][arr.sscl].sum())))

    # ---- reproduction check (policy d, vanishing demand, plan floors) ---------
    rep = size(arr, mean_cap, shares, phf, 0.70, 1.0, "d", floor_mode="plan", demand=np.full(n_routes, 1e-6))
    same = rep["fleet"] == pub
    reproduction = dict(
        definition="policy (d), demand ~0 so no route is demand-bound, plan floors, published cycles and headways",
        n_routes_equal=int(same.sum()), n_routes=n_routes,
        non_backbone_equal=int(same[~arr.sscl].sum()), non_backbone_n=int((~arr.sscl).sum()),
        backbone_equal=int(same[arr.sscl].sum()), backbone_n=int(arr.sscl.sum()),
        total_reproduced=int(rep["fleet"].sum()), total_published=pub_total,
        max_abs_route_diff=int(np.abs(rep["fleet"] - pub).max()),
        routes_differing=[str(r) for r in a["New_Route_ID"][~same]],
        note=(f"{int(same.sum())} of {n_routes} routes reproduce exactly from the published (0.1-min rounded) "
              "cycle; any route that differed would be listed in routes_differing, unadjusted."))

    # ---- per-route CSV (central case + published) -----------------------------
    out = pd.DataFrame(dict(
        New_Route_ID=a["New_Route_ID"], Route_Name=a["Route_Name"], Route_Type=a["Route_Type"],
        SSCL_backbone=arr.sscl, Cycle_Time_Min=arr.cycle_pub, Headway_Published_Min=arr.headway,
        Fleet_Published=arr.fleet_pub, Mean_Capacity=mean_cap, Daily_Demand_Pax=D,
        Load_At_Published_Headway=load_pub))
    for pol in ("a", "b", "c", "d"):
        r = results[(0.70, "x1", pol)]
        out[f"Headway_Demand_0.70_min"] = r["h_dem"]
        out[f"Headway_{pol}_min"] = r["h_eff"]
        out[f"Fleet_{pol}"] = r["fleet"]
    out["Demand_Bound_c"] = central["demand_bound"]
    out["Demand_Bound_d"] = central_d["demand_bound"]
    out["Fleet_Published_minus_a"] = pub - dem_fleet
    out.to_csv(C.DERIVED / "a17_route_demand_fleet.csv", index=False, float_format="%.6g")

    # ---- table -----------------------------------------------------------------
    tab = pd.DataFrame(dict(
        **{"Target load": gdf["target_load"], "Max-headway policy": gdf["policy_label"],
           "Demand": gdf["demand_level"], "Fleet": gdf["fleet_total"], "HPV": gdf["HPV"],
           "MPV": gdf["MPV"], "LPV": gdf["LPV"],
           "% of published 1,011": (100 * gdf["fleet_share_of_published"]).round(1),
           "Demand-bound routes": gdf["n_demand_bound"],
           "Headway median (min)": gdf["headway_median"].round(1),
           "p10": gdf["headway_p10"].round(1), "p90": gdf["headway_p90"].round(1),
           "% routes > 60 min": (100 * gdf["share_headway_over_60"]).round(1)}))
    C.write_table(tab, "table05n_demand_sized_fleet",
                  f"Fleet if headways were sized to the plan's demand proxy; n = {n_routes} active routes, "
                  f"published fleet {pub_total}. Peak-hour factor {100*phf:.2f}% (a05, CHALO April 2026); "
                  f"load = two-direction peak-hour boardings / two-direction capacity (a07 definition); "
                  f"published cycle times; spare 1.15; minimum 1 vehicle per route (arithmetic minimum 2). "
                  f"Demand x2.24 / x4.49 = a07 backbone growth multipliers. Demand-bound routes: policy "
                  f"ceiling not binding (under (a) every route by definition). The demand proxy is a "
                  f"corridor-share estimate calibrated on e-bus ridership, not observed demand; static, "
                  f"in-sample")

    # ---- headline ---------------------------------------------------------------
    def cell(rho, m, p):
        return gdf[(gdf.target_load == rho) & (gdf.demand_level == m) & (gdf.policy == p)].iloc[0]
    ca, cb, cc, cd = (cell(0.70, "x1", p) for p in "abcd")
    d_all, d_bb = decomposition["all_routes"], decomposition["backbone"]
    lo = int(gdf["fleet_total"].min())
    hi = int(gdf["fleet_total"].max())
    headline = (
        f"If headways were set so that peak-hour boarding-to-capacity equals 0.70 on the plan's own demand "
        f"proxy (peak-hour share {100*phf:.2f}%), the {n_routes} routes would need {int(ca.fleet_total)} buses "
        f"with no headway ceiling, {int(cb.fleet_total)} with a 60-minute ceiling and {int(cc.fleet_total)} with "
        f"the plan's own ceilings (35 min city, 50 min rural, 15 min backbone), against the published "
        f"{pub_total}; over the full grid (load 0.50-0.85, demand x1 to x{mults['x4.49']:.2f}, policies a-c) "
        f"fleets range from {int(gdf[gdf.policy.isin(list('abc'))].fleet_total.min())} to "
        f"{int(gdf[gdf.policy.isin(list('abc'))].fleet_total.max())}. Under the no-ceiling sizing, "
        f"{d_all['explained_by_demand']} of the {pub_total} published buses are explained by demand and "
        f"{d_all['above_demand_need_service_standard']} exist because service-standard headways are more "
        f"frequent than demand needs ({d_bb['above_demand_need_service_standard']} of those on the 30 "
        f"e-bus backbone routes, whose 15-minute headway is the operator's design target); on "
        f"{d_all['n_routes_published_below_demand']} routes the proxy would need more buses than published "
        f"({d_all['demand_need_beyond_plan']} buses). With the plan's ceilings and load 0.70, demand rather "
        f"than the ceiling sets the headway on {int(cc.n_demand_bound)} of {n_routes} routes. The demand "
        f"figure is a corridor-share proxy scaled by a capture factor calibrated on e-bus ridership, "
        f"static and not observed on these routes, so these fleets are scenario values, not forecasts.")

    limitations = [
        dict(id="L1", text=("Demand is the engine's Eq. 8 corridor-share proxy: 400 m walkshed population x "
                            "corridor share x capture factor kappa. kappa = 0.33 (engine "
                            "PHASE4_CORRIDOR_CAPTURE_SCALE, transit_kashmir_v3.py; recorded in paper/"
                            "CLAIM_LEDGER.md CL-59) was calibrated on CHALO e-bus ridership. It is not observed "
                            "demand on these routes; the engine source is not in this repository, so kappa is "
                            "taken from the ledger, not re-verified here."), kappa=0.33),
        dict(id="L2", text=("Demand is static: no response of ridership to frequency, so a thinner service "
                            "does not lose riders and a denser one does not gain any. Demand multipliers "
                            "x2.24 / x4.49 are the growth a07 reports as needed to restore today's e-bus "
                            "boardings per trip, scenarios not forecasts.")),
        dict(id="L3", text=(f"All-day demand is converted to peak hour by one profile, the CHALO e-bus system's "
                            f"April-2026 hourly shape (peak share {100*phf:.2f}%, a05), applied to every route "
                            f"including rural lifelines; peak-direction split fixed at 50/50 (a07 corrected "
                            f"definition), so directional imbalance is ignored.")),
        dict(id="L4", text=("Cycle times are the plan's published (per-km capped) values and are held fixed; "
                            "faster or slower running would change fleets proportionally.")),
        dict(id="L5", text=("Boarding-to-capacity is not a maximum-load-section load factor; no on-board load "
                            "profile exists. Vehicle capacity is design load (60/35/20), standing included.")),
        dict(id="L6", text=("Headways are continuous (not rounded to schedulable values) and clamped at 1 minute "
                            "by the fleet model; the number of routes whose demand headway is below 1 minute "
                            "is reported per cell. Class mix is held at the published mix per route.")),
        dict(id="L7", text=("The backbone fleet floor (operator's empirical deployment) binds on 2 routes and "
                            "is kept in every cell; the backbone ceiling in policy (c) is the 15-minute design "
                            "target. Spare ratio 1.15 is the plan's.")),
    ]

    C.write_result(dict(
        status="computed", in_sample=True, is_model_proxy_not_observation=True,
        n_routes=n_routes, fleet_published=pub_total,
        base=f"{n_routes} active plan routes; Eq. 8 Daily_Demand_Pax proxy; published cycle times; spare 1.15",
        parameters=dict(
            target_loads=list(LOADS), demand_multipliers=mults,
            demand_multiplier_source="a07_load_factor.json observed_backbone.readings.*.trip_multiplier (round-trip 2.2446; one-way 4.4892)",
            peak_hour_factor=phf, peak_hour_factor_source=("a05_headway_timeofday.json peak_hour_factor_pct "
                                                           "(CHALO Hourly_Passenger_Count.csv, April 2026, peak hour "
                                                           f"{a05['peak_hour']}, share of daily boardings)"),
            peak_direction_split=0.5, peak_direction_split_note="implied by a07's two-direction/two-direction ratio",
            vehicle_capacity=C.VEHICLE_CAPACITY, spare_ratio=FM.BASE["FLEET_SPARE_RATIO"],
            ceilings_min=dict(lifeline_b=LIFELINE_CEILING_MIN, city_c=CITY_CEILING_MIN,
                              rural_c=RURAL_CEILING_MIN, backbone_c=BACKBONE_CEILING_MIN),
            ceilings_source="common.py HEADWAY_MAX_MIN, REGIONAL_HEADWAY_BUCKETS, HEADWAY_SSCL_TRUNK_MIN",
            policies=POLICY_LABEL, minimum_vehicles_per_route=1,
            effective_minimum_vehicles_per_route=int(min(r["fleet"].min() for r in results.values())),
            effective_minimum_note="ceil(1 operating bus x spare 1.15) = 2",
            kappa_capture_scale=0.33, kappa_source="engine PHASE4_CORRIDOR_CAPTURE_SCALE; CL-59"),
        a07_consistency=dict(median_load_at_published_headway=float(np.median(load_pub)),
                             a07_median=a07_med, equal=True),
        central_case=dict(definition="target load 0.70, demand x1, policy (c) plan ceilings",
                          cell=cen_rec, reference_policy_d=cen_rec_d,
                          n_demand_bound=int(cc.n_demand_bound), n_routes=n_routes),
        grid=grid, decomposition_at_load_0p70=decomposition, sensitivity=sens,
        reproduction_check=reproduction, limitations=limitations, headline=headline,
    ), "a17_demand_sized_fleet")

    log.info("published %d; central (c) %d; (a) %d; (b) %d; grid range %d-%d", pub_total,
             cc.fleet_total, ca.fleet_total, cb.fleet_total, lo, hi)
    log.info("decomposition: explained %d, above need %d, beyond plan %d; demand-bound (c) %d",
             d_all["explained_by_demand"], d_all["above_demand_need_service_standard"],
             d_all["demand_need_beyond_plan"], cc.n_demand_bound)


if __name__ == "__main__":
    main()
