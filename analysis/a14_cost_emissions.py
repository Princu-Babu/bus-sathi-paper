#!/usr/bin/env python
"""
a14_cost_emissions.py — operating cost and CO2 envelope of the plan, by vehicle
size class, and cost per resident given access.

Status: PROVISIONAL pending decision D8. Every monetary and emission constant
below is an external value that the project lead must confirm against its
source before any figure from this module enters the Abstract or conclusions.
Each constant is carried as a (low, high) RANGE with its source string, year,
applicability and a `verified` flag (True only for the three constants with a primary source URL, "press" for the
press-sourced GCC rates, False otherwise). Every output is an
interval, never a point. Nothing here is calibrated to Kashmir operations;
there are no Kashmir cost or fuel records in any input.

Vehicle size classes (F-04-15). The plan's fleet is 187 HPV (~12 m, design load
60), 754 MPV (~9 m, 35) and 70 LPV (minibus, 20). Earlier versions priced every
non-minibus bus, i.e. the 754 MPVs too, as a full-size bus. The three classes
are now costed and fuelled separately. There is no MPV-specific constant in the
repo, so the MPV range is the arithmetic midpoint of the HPV and LPV bounds
(source "assumption", verified False); the result is bracketed by pricing the
MPVs as HPV (the previous treatment, an upper envelope) and as LPV (a lower
envelope), both reported under `mpv_pricing_sensitivity`.

Vehicle-kilometre bases. The plan and observation disagree, so each base is
reported:
  PLAN                the plan's published Daily_KM column: every bus runs a
                      16-hour service day at the published headway (~320
                      service km per bus per day).
  PLAN_TRIPS_X_LENGTH the plan's own Daily_Trips x Route_KM. Check on PLAN:
                      Daily_KM exceeds trips x length on the routes whose
                      distance was substituted in v3.4.4 (Daily_KM kept the
                      pre-substitution length); the network difference is
                      emitted under `daily_km_assumption`.
  OBSERVED            the median observed in-service time per vehicle-day from
                      driver GPS (a13 duty model: 217 min) at each route's cycle
                      time (a06), i.e. what today's fleet actually runs. A floor
                      on what a scheduled operator would run, not a forecast.
Deadhead is added at a06's district-depot bound (D1).

What is NOT in the figures (`exclusions` in the JSON): crew wages as a separate
line, vehicle purchase or lease, depots and workshops, charging infrastructure
and grid connection, energy taxes, insurance, fare revenue (so this is gross
cost, not subsidy), and any winter service reduction (365 operating days are
assumed). The per-km rates are described as gross-cost-contract rates; which of
crew, vehicle capital recovery and energy they embed depends on the contract and
is not verified here.

Emission-factor cross-check. The engine's Phase-4 emissions column uses 30 g
CO2/km for the e-bus backbone ("Indian grid mix electric"). At the module's
e-bus energy-intensity range and national-average grid factor range the figure
is 630-1,150 g/km, mid-range ~874 g/km, i.e. the engine understates by a factor
of ~21-38 (mid-range ~29). The ratio is computed in code and emitted, not typed.
It rests on national-average grid factors; J&K's supply mix is different and no
state factor is in the repo, so it is an order-of-magnitude check only.
The engine column is not used.

Outputs  data/derived/a14_cost_emissions.json, paper/tables/table05m_cost_emissions.{csv,md},
         paper/tables/table05m_constants.{csv,md}
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a14")

CLASSES = ("HPV", "MPV", "LPV")
CLASS_DESC = {"HPV": "high-capacity bus (~12 m)", "MPV": "mid-size bus (~9 m)", "LPV": "minibus"}

NAMED = "named_source_not_in_repo"
ASSUMPTION = "assumption"


PRIMARY = "primary_source_url"
PRESS = "press"


def _k(low, high, unit, source, applies_to, status, year=None, note="", verified=False, url=None):
    """One constant. `verified` is True only where a primary source with URL is recorded
    (status PRIMARY), the string "press" for press-sourced values, otherwise False."""
    d = dict(low=float(low), high=float(high), unit=unit, source=source, year=year,
             applies_to=list(applies_to), source_status=status, verified=verified, note=note)
    if url:
        d["url"] = url
    return d


_HPV_KMPL = (3.5, 5.0)
_LPV_KMPL = (7.0, 10.0)
_HPV_COST = (55.0, 90.0)
_LPV_COST = (25.0, 45.0)


def _mid(a, b):
    return tuple((x + y) / 2.0 for x, y in zip(a, b))


_MPV_KMPL = _mid(_HPV_KMPL, _LPV_KMPL)
_MPV_COST = _mid(_HPV_COST, _LPV_COST)

CONSTANTS = {
    "diesel_kmpl_full_size": _k(*_HPV_KMPL, "km/L",
        "ASRTU / CIRT State Transport Undertaking performance statistics (fleet HSD km/L); "
        "range spans city and mofussil operation", ["HPV"], NAMED,
        note="legacy key name; applies to the HPV class. Table, page and year not recorded."),
    "diesel_kmpl_mpv": _k(*_MPV_KMPL, "km/L",
        ASSUMPTION, ["MPV"], ASSUMPTION,
        note="arithmetic midpoint of the HPV and LPV bounds; no 9 m-bus economy source in the repo."),
    "diesel_kmpl_lpv": _k(*_LPV_KMPL, "km/L",
        ASSUMPTION, ["LPV"], ASSUMPTION,
        note="repo text was 'manufacturer-rated economy for 12-20 seat minibuses/tempo travellers; "
             "no Kashmir record' — no named document, so treated as an assumption."),
    "diesel_kgco2_per_l": _k(2.64, 2.70, "kg CO2/L",
        "IPCC 2006 Guidelines Vol.2 Ch.3 default diesel factor (74,100 kg/TJ) at Indian HSD density",
        ["HPV", "MPV", "LPV"], NAMED, year=2006,
        note="IPCC document not held in the repo; density assumption not recorded."),
    "ebus_kwh_per_km": _k(0.98, 1.3, "kWh/km",
        "ITDP India (2022) Guidance for Electric Bus Rollout in Indian Cities, p.20 and p.33: 12 m e-bus "
        "0.98 kWh/km (Hyderabad) to 1.3 kWh/km (PMPML Pune)",
        ["HPV"], PRIMARY, year=2022, verified=True,
        url="https://www.itdp.in/wp-content/uploads/2022/10/Guidance-for-e-Bus-Rollout-in-Indian-Cities.pdf",
        note="legacy key name; the 12 m (HPV) e-bus range, two Indian operators. Replaces the earlier "
             "unsourced 0.9-1.4 range."),
    "ebus_kwh_per_km_mpv": _k(0.9, 1.4, "kWh/km",
        "no citable measured 9 m e-bus energy use found (research_R2 item 10); earlier unsourced range kept",
        ["MPV"], ASSUMPTION,
        note="9 m e-bus kWh/km NOT FOUND from a citable source; applied only to MPVs on an SSCL backbone route."),
    "grid_kgco2_per_kwh": _k(0.675, 0.705, "kg CO2/kWh",
        "CEA CO2 Baseline Database for the Indian Power Sector, User Guide v22.0, Table S, FY2025-26: "
        "weighted average 0.675 (low) to combined margin 0.705 (high) tCO2/MWh",
        ["HPV", "MPV"], PRIMARY, year=2026, verified=True,
        url="https://cea.nic.in/wp-content/uploads/baseline/2026/09/User_Guide__Version_22.0.pdf",
        note="national-average factor applied to Kashmir charging; no J&K state factor in the repo. The "
             "operating margin (0.963) is not used; no source for T&D/charging-loss uplift, so none is added "
             "(earlier range 0.70-0.82 included an unsourced loss allowance)."),
    "srtu_km_per_bus_day": _k(218.2, 218.2, "km/bus/day",
        "MoRTH Transport Research Wing, Review of the Performance of SRTUs 2019-20 to 2021-22, executive-summary "
        "table: 218.2 bus-km per bus per day, 58 SRTUs, 2021-22",
        ["HPV", "MPV", "LPV"], PRIMARY, year=2022, verified=True,
        url="http://morth.gov.in/backend/documents/uploaded/Review%20of%20the%20performance%20of%20State%20Road%20Transport%20Undertakings%20for%202019-20%20to%202021-22.pdf",
        note="third vehicle-km basis (SRTU_MORTH); an all-India state-undertaking average, not Kashmir. "
             "Used as total km per bus per day, deadhead not added (the source does not split it)."),
    "gcc_inr_per_km_ebus_12m": _k(54.3, 63.0, "INR/km",
        "low: CESL National Electric Bus Programme Jan 2023 tender, 12 m intra-city, discovered Rs 54.3/km "
        "(Outlook Business, 3 Jan 2023); high: ITDP India (2022) p.47, FAME-II tenders average L1 about Rs 63/km",
        ["HPV"], PRESS, year=2023, verified="press",
        url="https://www.outlookbusiness.com/news/e-bus-tender-discovers-29-lower-price-than-diesel-ones-cesl-news-250554",
        note="press-sourced low end (secondary reporting, CESL primary result not located); high end from an "
             "ITDP report. Gross-cost-contract rate for e-buses; used only in the `sourced_gcc_cross_check` block."),
    "gcc_inr_per_km_ebus_9m": _k(54.46, 63.0, "INR/km",
        "low: CESL Jan 2023 tender, 9 m, discovered Rs 54.46/km (Outlook Business / Mercom, press); "
        "high: ITDP India (2022) FAME-II average L1 about Rs 63/km (not size-specific)",
        ["MPV"], PRESS, year=2023, verified="press",
        url="https://mercomindia.com/e-buses-cost-effective-cesl-bidding-results-show/",
        note="press-sourced; used only in the `sourced_gcc_cross_check` block."),
    "cost_inr_per_km_full_size": _k(*_HPV_COST, "INR/km",
        "gross-cost-contract (GCC) per-km rates discovered in recent Indian e-bus and diesel bus "
        "tenders; engine uses 65", ["HPV"], NAMED,
        note="legacy key name; applies to the HPV class. No tender id, page or year recorded. "
             "Same range used for diesel and e-bus."),
    "cost_inr_per_km_mpv": _k(*_MPV_COST, "INR/km",
        ASSUMPTION, ["MPV"], ASSUMPTION,
        note="arithmetic midpoint of the HPV and LPV bounds; no 9 m-bus rate source in the repo."),
    "cost_inr_per_km_lpv": _k(*_LPV_COST, "INR/km",
        ASSUMPTION, ["LPV"], ASSUMPTION,
        note="repo text was 'private minibus operating cost; no Kashmir record' — no named "
             "document, so treated as an assumption."),
    "operating_days_per_year": _k(365, 365, "days/yr",
        ASSUMPTION, ["HPV", "MPV", "LPV"], ASSUMPTION,
        note="every route runs every day; the plan has no operating calendar. Upper bound: "
             "seasonal closures and winter reductions are not modelled."),
}
DAYS_PER_YEAR = int(CONSTANTS["operating_days_per_year"]["high"])

# which constant keys price each class: (diesel km/L, cost INR/km)
CLASS_KEYS = {"HPV": ("diesel_kmpl_full_size", "cost_inr_per_km_full_size"),
              "MPV": ("diesel_kmpl_mpv", "cost_inr_per_km_mpv"),
              "LPV": ("diesel_kmpl_lpv", "cost_inr_per_km_lpv")}

EXCLUSIONS = [
    "crew (driver/conductor) wages as a separate line: not modelled and no crew count derived from "
    "any input; whether the per-km rate embeds crew is unverified",
    "vehicle purchase or lease (capital for the ~400 vehicles above today's fleet and for replacement): "
    "not modelled; whether the per-km rate embeds capital recovery is unverified",
    "depots, workshops and layover land",
    "charging infrastructure and grid connection for the SSCL e-bus backbone",
    "fuel/energy taxes, insurance, permits, tolls",
    "fare revenue: figures are gross operating cost, not net subsidy",
    "seasonal or winter service reduction: 365 operating days assumed (upper bound)",
]

ENGINE_EBUS_GCO2_PER_KM = 30.0
ENGINE_DIESEL_GCO2_PER_KM = 950.0


def class_km(a: pd.DataFrame, km_day: pd.Series) -> dict:
    """Annual vehicle-km by class, split diesel / e-bus (SSCL backbone = e-bus).

    Every bus on a route is assumed to cover the same daily km whatever its class
    (the plan carries no class-specific duty), so a route's km is shared by its
    class counts.
    """
    fleet = a["Fleet_Required"].to_numpy(float)
    ebus = a["CMP_Trunk"].astype(bool).to_numpy()
    km_day = km_day.to_numpy(float)
    out = {}
    for c in CLASSES:
        cnt = a[f"{c}_Count"].to_numpy(float)
        km = km_day * (cnt / fleet) * DAYS_PER_YEAR
        out[c] = dict(n_buses=int(cnt.sum()), diesel_km=float(km[~ebus].sum()),
                      ebus_km=float(km[ebus].sum()))
    if out["LPV"]["ebus_km"] > 0:
        raise AssertionError("LPV vehicles on an SSCL e-bus route: e-bus LPV constants do not exist")
    return out


EBUS_KEY = {"HPV": "ebus_kwh_per_km", "MPV": "ebus_kwh_per_km_mpv", "LPV": "ebus_kwh_per_km_mpv"}


def price(km: dict, K: dict, key_for: dict) -> dict:
    """Cost (INR/yr) and CO2 (t/yr) as [low, high] per class. `key_for` maps the
    class being priced to the class whose km/L and INR/km constants are used."""
    res = {}
    for c in CLASSES:
        kmpl_key, cost_key = CLASS_KEYS[key_for[c]]
        d, e = km[c]["diesel_km"], km[c]["ebus_km"]
        cost = [(d + e) * K[cost_key]["low"], (d + e) * K[cost_key]["high"]]
        # low = best economy and cleanest energy; high = the reverse
        ek = K[EBUS_KEY[key_for[c]]]
        co2_lo = (d / K[kmpl_key]["high"] * K["diesel_kgco2_per_l"]["low"]
                  + e * ek["low"] * K["grid_kgco2_per_kwh"]["low"]) / 1000.0
        co2_hi = (d / K[kmpl_key]["low"] * K["diesel_kgco2_per_l"]["high"]
                  + e * ek["high"] * K["grid_kgco2_per_kwh"]["high"]) / 1000.0
        res[c] = dict(cost_inr_per_year=cost, co2_t_per_year=[co2_lo, co2_hi])
    return res


def _sum_ranges(res: dict, field: str) -> list:
    return [float(sum(res[c][field][i] for c in CLASSES)) for i in (0, 1)]


def daily_km_block(a: pd.DataFrame, plan_km: float) -> dict:
    """The daily-km assumption and its basis, checked against the plan's own columns."""
    fleet = a["Fleet_Required"].to_numpy(float)
    trips_x_len = a["Daily_Trips"].to_numpy(float) * a["Route_KM"].to_numpy(float)
    daily_km = a["Daily_KM"].to_numpy(float)
    ratio = daily_km / trips_x_len
    dev = np.abs(ratio - 1.0) > 0.01
    sub_flag = None
    p = C.DERIVED / "a02_catchments.csv"
    if p.exists():
        c2 = pd.read_csv(p)[["New_Route_ID", "km_geometry_consistent"]]
        m = a[["New_Route_ID"]].merge(c2, on="New_Route_ID", how="left")
        sub_flag = ~m["km_geometry_consistent"].fillna(True).astype(bool).to_numpy()
    hours = (a["Daily_Trips"] * a["Headway_Min"] / 60.0).to_numpy(float)
    per_bus = daily_km / fleet
    obs = C.read_result("a06_deadhead")["observed_day"]
    return dict(
        plan_daily_km_total=float(daily_km.sum()),
        plan_trips_x_route_km_total=float(trips_x_len.sum()),
        plan_over_trips_x_length_ratio=float(daily_km.sum() / trips_x_len.sum()),
        n_routes_daily_km_differs_from_trips_x_length_gt_1pct=int(dev.sum()),
        n_of_those_with_km_substituted_in_v344=(int((dev & sub_flag).sum()) if sub_flag is not None else None),
        n_routes_km_substituted_in_v344=(int(sub_flag.sum()) if sub_flag is not None else None),
        explanation=(f"Daily_KM equals Daily_Trips x Route_KM (within 1%) on {int((~dev).sum())} of "
                     f"{len(a)} routes; it differs on the other {int(dev.sum())}. "
                     + (f"{int((dev & sub_flag).sum())} of those coincide with the routes whose Route_KM was "
                        "replaced by an externally researched distance in v3.4.4 (the a02 km-substituted flag), "
                        "so Daily_KM probably kept the pre-substitution length (inferred from the overlap, not "
                        f"traced in the engine); the other {int((dev & ~sub_flag).sum())} are unexplained here. "
                        if sub_flag is not None else "")
                     + "PLAN_TRIPS_X_LENGTH is the internally consistent basis."),
        service_day_hours_both_directions=dict(
            derivation="Daily_Trips x Headway_Min / 60 per route; Daily_Trips counts departures in both directions",
            min=float(hours.min()), max=float(hours.max()),
            reading="32 vehicle-departure-hours = 2 directions x 16 service hours"),
        plan_km_per_bus_day=dict(
            network_mean=float(plan_km / fleet.sum()),
            route_median=float(np.median(per_bus)), route_p90=float(np.percentile(per_bus, 90)),
            route_max=float(per_bus.max()),
            note="Daily_KM / Fleet_Required, with Fleet_Required including the 1.15 spare ratio"),
        observed_km_per_bus_day=dict(
            network=float(obs["observed_service_km_per_bus_day"]),
            service_min_per_bus_day=float(obs["service_min_per_bus_day"]),
            source="a06_deadhead.json observed_day (a13 duty model, driver GPS)"),
        plan_over_observed_ratio=float(plan_km / fleet.sum() / obs["observed_service_km_per_bus_day"]),
        reading=("The plan costs a 16-hour day for every bus, minibuses included, at ~320 km per bus; "
                 "today's observed duty is ~99 km. PLAN is therefore an upper bound and OBSERVED a lower "
                 "bound; neither is a costed duty roster, and no crew count is derived."),
    )


def main() -> None:
    a = C.load_active().copy()
    dh = pd.read_csv(C.DERIVED / "a06_route_deadhead.csv")[
        ["New_Route_ID", "deadhead_km_per_bus_day_D1", "service_km_per_bus_day_observed"]]
    a = a.merge(dh, on="New_Route_ID", how="left")
    cov = C.read_result("a11_coverage_accessibility")["any_service_reconciliation"]["any_service_population"]

    fleet = a["Fleet_Required"].astype(float)
    if not (a["HPV_Count"] + a["MPV_Count"] + a["LPV_Count"] == a["Fleet_Required"]).all():
        raise AssertionError("HPV+MPV+LPV != Fleet_Required on some route")
    dead = a["deadhead_km_per_bus_day_D1"] * fleet
    plan_km = float(a["Daily_KM"].sum())
    bases = {
        "PLAN": a["Daily_KM"] + dead,
        "PLAN_TRIPS_X_LENGTH": a["Daily_Trips"] * a["Route_KM"] + dead,
        "OBSERVED": (a["service_km_per_bus_day_observed"] + a["deadhead_km_per_bus_day_D1"]) * fleet,
        "SRTU_MORTH": CONSTANTS["srtu_km_per_bus_day"]["high"] * fleet,
    }
    base_desc = {
        "PLAN": "published Daily_KM (16-h service day at the published headway) + D1 deadhead",
        "PLAN_TRIPS_X_LENGTH": "Daily_Trips x Route_KM (internally consistent plan km) + D1 deadhead",
        "OBSERVED": "observed 217 min in-service per vehicle-day at route cycle time + D1 deadhead",
        "SRTU_MORTH": "218.2 bus-km per bus per day, all-India state road transport undertakings 2021-22 "
                      "(MoRTH review), x each route's fleet; deadhead not added",
    }
    K = CONSTANTS
    identity = {c: c for c in CLASSES}
    variants = {"mpv_priced_as_hpv": {**identity, "MPV": "HPV"},
                "mpv_midpoint_central": identity,
                "mpv_priced_as_lpv": {**identity, "MPV": "LPV"}}

    rows, out_bases = [], {}
    for name, km_day in bases.items():
        km = class_km(a, km_day)
        res = price(km, K, identity)
        tot_km = sum(km[c]["diesel_km"] + km[c]["ebus_km"] for c in CLASSES)
        ebus_km = sum(km[c]["ebus_km"] for c in CLASSES)
        cost = _sum_ranges(res, "cost_inr_per_year")
        co2 = _sum_ranges(res, "co2_t_per_year")
        per_res = [cost[0] / cov, cost[1] / cov]
        by_class = {}
        for c in CLASSES:
            kmpl_key, cost_key = CLASS_KEYS[c]
            by_class[c] = dict(
                description=CLASS_DESC[c], n_buses=km[c]["n_buses"],
                vehicle_km_per_year=km[c]["diesel_km"] + km[c]["ebus_km"],
                diesel_km_per_year=km[c]["diesel_km"], ebus_km_per_year=km[c]["ebus_km"],
                cost_rate_inr_per_km=[K[cost_key]["low"], K[cost_key]["high"]],
                diesel_km_per_litre=[K[kmpl_key]["low"], K[kmpl_key]["high"]],
                cost_inr_per_year=res[c]["cost_inr_per_year"], co2_t_per_year=res[c]["co2_t_per_year"])
        sens = {}
        for vname, kf in variants.items():
            r = price(km, K, kf)
            sens[vname] = dict(cost_inr_per_year=_sum_ranges(r, "cost_inr_per_year"),
                               co2_t_per_year=_sum_ranges(r, "co2_t_per_year"))
        out_bases[name] = dict(
            description=base_desc[name],
            vehicle_km_per_year=float(tot_km), cost_inr_per_year=cost, co2_t_per_year=co2,
            cost_inr_per_covered_resident_per_year=per_res,
            ebus_share_of_km=float(ebus_km / tot_km),
            by_class=by_class, mpv_pricing_sensitivity=sens,
            sum_of_classes_check=dict(
                cost_inr_per_year=[float(sum(by_class[c]["cost_inr_per_year"][i] for c in CLASSES)) for i in (0, 1)],
                note="total is the sum of the three class rows, low with low and high with high"))
        for c in CLASSES:
            b = by_class[c]
            rows.append({"Vehicle-km basis": name, "Vehicle class": c, "Buses": b["n_buses"],
                         "Vehicle-km / yr (M)": round(b["vehicle_km_per_year"] / 1e6, 1),
                         "Operating cost / yr (INR crore)":
                             f"{b['cost_inr_per_year'][0]/1e7:,.0f}–{b['cost_inr_per_year'][1]/1e7:,.0f}",
                         "CO2 / yr (kt)": f"{b['co2_t_per_year'][0]/1e3:,.1f}–{b['co2_t_per_year'][1]/1e3:,.1f}",
                         "Cost per covered resident / yr (INR)": ""})
        rows.append({"Vehicle-km basis": name, "Vehicle class": "All (sum of classes)",
                     "Buses": int(fleet.sum()), "Vehicle-km / yr (M)": round(tot_km / 1e6, 1),
                     "Operating cost / yr (INR crore)": f"{cost[0]/1e7:,.0f}–{cost[1]/1e7:,.0f}",
                     "CO2 / yr (kt)": f"{co2[0]/1e3:,.1f}–{co2[1]/1e3:,.1f}",
                     "Cost per covered resident / yr (INR)": f"{per_res[0]:,.0f}–{per_res[1]:,.0f}"})
    C.write_table(pd.DataFrame(rows), "table05m_cost_emissions",
                  "PROVISIONAL (some constants unverified, pending D8; see table05m_constants): annual gross operating cost and CO2 range by "
                  "vehicle size class. Excludes crew as a separate line, vehicle capital, depots, charging "
                  "infrastructure and fare revenue; 365 days assumed. MPV constants are the midpoint of the HPV "
                  f"and LPV bounds (assumption). Covered residents = {cov:,.0f} (network 400 m walkshed, a11)")
    const_rows = [dict(Constant=k, Low=v["low"], High=v["high"], Unit=v["unit"],
                       Applies_to="/".join(v["applies_to"]), Source=v["source"],
                       Source_status=v["source_status"], Year=v["year"] if v["year"] is not None else "n/s",
                       Verified=v["verified"], Note=v["note"]) for k, v in K.items()]
    C.write_table(pd.DataFrame(const_rows), "table05m_constants",
                  "Cost and emission constants used by a14. Verified = True only where a primary source with URL is recorded "
                  "(grid factor, 12 m e-bus kWh/km, SRTU km/bus/day); 'press' = press-sourced; False = unverified "
                  "(named source not held in the repo, or assumption). Year n/s = not stated in the module.")
    constants_table = [dict(constant=k, applies_to=v["applies_to"], low=v["low"], high=v["high"], unit=v["unit"],
                            source=v["source"], source_status=v["source_status"], year=v["year"],
                            verified=v["verified"], note=v["note"]) for k, v in K.items()]

    kw, gr = K["ebus_kwh_per_km"], K["grid_kgco2_per_kwh"]
    ebus_lo, ebus_hi = kw["low"] * gr["low"] * 1000, kw["high"] * gr["high"] * 1000
    ebus_mid = float(np.mean([kw["low"], kw["high"]]) * np.mean([gr["low"], gr["high"]]) * 1000)
    diesel_gkm = {c: [K["diesel_kgco2_per_l"]["low"] / K[CLASS_KEYS[c][0]]["high"] * 1000,
                      K["diesel_kgco2_per_l"]["high"] / K[CLASS_KEYS[c][0]]["low"] * 1000] for c in CLASSES}
    emis_check = dict(
        engine_ebus_gco2_per_km=ENGINE_EBUS_GCO2_PER_KM,
        midrange_ebus_gco2_per_km=ebus_mid,
        understatement_factor=ebus_mid / ENGINE_EBUS_GCO2_PER_KM,
        understatement_factor_note="mid-range ratio (kWh/km and grid factor each at the midpoint of their ranges)",
        ebus_gco2_per_km_range=[ebus_lo, ebus_hi],
        understatement_factor_range=[ebus_lo / ENGINE_EBUS_GCO2_PER_KM, ebus_hi / ENGINE_EBUS_GCO2_PER_KM],
        breakeven_grid_gco2_per_kwh_range=[ENGINE_EBUS_GCO2_PER_KM / kw["high"], ENGINE_EBUS_GCO2_PER_KM / kw["low"]],
        breakeven_note=("the grid factor (g CO2/kWh) at which the engine's 30 g/km would be right for the stated "
                        f"12 m kWh/km range; compare with the CEA FY2025-26 range {gr['low']*1000:.0f}-{gr['high']*1000:.0f} g/kWh"),
        basis="12 m e-bus kWh/km (ITDP 2022, verified) x CEA v22.0 FY2025-26 grid factor (verified); the 9 m figure is not sourced and is not used in this check",
        grid_basis_caveat=("national-average grid factor; J&K's supply mix differs and no state-level factor is in "
                           "the repo, so this is an order-of-magnitude check, not a measured error"),
        engine_diesel_gco2_per_km=ENGINE_DIESEL_GCO2_PER_KM,
        module_diesel_gco2_per_km_by_class=diesel_gkm,
        note="Engine Phase-4 Emissions_GCO2_Daily is not used; diesel constants are unverified (see constants_table).")

    # Cross-check against sourced gross-cost-contract (GCC) e-bus rates: price every HPV and MPV
    # vehicle-km at the e-bus GCC range (press / ITDP), LPV at the module's own range.
    gcc = {}
    for name, km_day in bases.items():
        kmc = class_km(a, km_day)
        lo = hi = 0.0
        for c in CLASSES:
            tot = kmc[c]["diesel_km"] + kmc[c]["ebus_km"]
            if c == "HPV":
                r = K["gcc_inr_per_km_ebus_12m"]
            elif c == "MPV":
                r = K["gcc_inr_per_km_ebus_9m"]
            else:
                r = K[CLASS_KEYS["LPV"][1]]
            lo += tot * r["low"]
            hi += tot * r["high"]
        gcc[name] = dict(cost_inr_per_year=[lo, hi], module_range_cost_inr_per_year=out_bases[name]["cost_inr_per_year"])
    gcc_block = dict(
        verified="press",
        basis="all HPV vehicle-km at the 12 m e-bus GCC range, all MPV km at the 9 m range, LPV km at the module's own (unverified) "
              "minibus range; i.e. what the plan would cost if every bus were procured on an e-bus GCC",
        by_basis=gcc,
        caveat="press-sourced (CESL tender results, Outlook Business / Mercom 2023) plus one ITDP figure; a different "
               "question from the diesel-oriented module range, so reported beside it and not substituted for it")

    plan_b, obs_b = out_bases["PLAN"], out_bases["OBSERVED"]
    sens = plan_b["mpv_pricing_sensitivity"]
    envelope = dict(
        cost_inr_per_year=[obs_b["cost_inr_per_year"][0], plan_b["cost_inr_per_year"][1]],
        co2_t_per_year=[obs_b["co2_t_per_year"][0], plan_b["co2_t_per_year"][1]],
        note="lowest end of OBSERVED to highest end of PLAN (SRTU_MORTH lies between them); PROVISIONAL, cost and diesel constants unverified")
    headline = (
        f"PROVISIONAL (grid factor, 12 m e-bus energy and SRTU utilisation are sourced; diesel economy and per-km cost rates are not). Annual gross operating cost for {int(fleet.sum())} buses "
        f"(HPV {int(a['HPV_Count'].sum())} / MPV {int(a['MPV_Count'].sum())} / LPV {int(a['LPV_Count'].sum())}), "
        f"each class costed on its own constants: INR {plan_b['cost_inr_per_year'][0]/1e7:,.0f}–"
        f"{plan_b['cost_inr_per_year'][1]/1e7:,.0f} crore on the plan's own kilometres (16-hour day, a ceiling) and "
        f"INR {obs_b['cost_inr_per_year'][0]/1e7:,.0f}–{obs_b['cost_inr_per_year'][1]/1e7:,.0f} crore on observed "
        f"duty (a floor); CO2 {plan_b['co2_t_per_year'][0]/1e3:,.0f}–{plan_b['co2_t_per_year'][1]/1e3:,.0f} kt and "
        f"{obs_b['co2_t_per_year'][0]/1e3:,.0f}–{obs_b['co2_t_per_year'][1]/1e3:,.0f} kt. Pricing the 754 MPVs "
        f"as full-size buses (the earlier treatment) would give INR {sens['mpv_priced_as_hpv']['cost_inr_per_year'][0]/1e7:,.0f}–"
        f"{sens['mpv_priced_as_hpv']['cost_inr_per_year'][1]/1e7:,.0f} crore on the plan basis. Crew as a separate "
        f"line, vehicle capital, depots and charging infrastructure are excluded.")

    C.write_result(dict(
        status="PROVISIONAL_PENDING_D8",
        headline=headline,
        constants={k: {kk: vv for kk, vv in v.items()} for k, v in K.items()},
        constants_table=constants_table,
        vehicle_classes={c: dict(description=CLASS_DESC[c], design_load=C.VEHICLE_CAPACITY[c],
                                 n_buses=int(a[f"{c}_Count"].sum())) for c in CLASSES},
        exclusions=EXCLUSIONS,
        daily_km_assumption=daily_km_block(a, plan_km),
        envelope=envelope,
        covered_residents=cov, bases=out_bases,
        engine_emission_factor_check=emis_check,
        sourced_gcc_cross_check=gcc_block,
    ), "a14_cost_emissions")
    for k, v in out_bases.items():
        log.info("%s: %.0fM veh-km/yr; cost INR %.0f–%.0f cr; CO2 %.1f–%.1f kt; per covered resident "
                 "INR %.0f–%.0f", k, v["vehicle_km_per_year"] / 1e6, v["cost_inr_per_year"][0] / 1e7,
                 v["cost_inr_per_year"][1] / 1e7, v["co2_t_per_year"][0] / 1e3, v["co2_t_per_year"][1] / 1e3,
                 *v["cost_inr_per_covered_resident_per_year"])
        for vn, vv in v["mpv_pricing_sensitivity"].items():
            log.info("   %-22s cost INR %.0f–%.0f cr", vn, vv["cost_inr_per_year"][0] / 1e7,
                     vv["cost_inr_per_year"][1] / 1e7)
    log.info("engine e-bus factor %.0f g/km vs mid-range %.0f g/km (x%.1f; range x%.0f–%.0f)",
             ENGINE_EBUS_GCO2_PER_KM, ebus_mid, ebus_mid / ENGINE_EBUS_GCO2_PER_KM,
             *emis_check["understatement_factor_range"])


if __name__ == "__main__":
    main()
