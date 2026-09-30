#!/usr/bin/env python
"""
a14_cost_emissions.py — operating cost and CO2 envelope of the plan, and cost
per resident given access.

Status: PROVISIONAL pending decision D8. Every monetary and emission constant
below is an external value that the project lead must confirm against its
source before any figure from this module enters the Abstract or conclusions.
Each constant is therefore carried as a (low, high) RANGE with its source and a
`verified` flag, and every output is an interval, never a point. Nothing here
is calibrated to Kashmir operations; there are no Kashmir cost or fuel records
in any input.

Two vehicle-kilometre bases, because the plan and observation disagree:
  PLAN      the plan's Daily_KM: every bus runs a 16-hour day at the published
            headway (~320 service km per bus per day).
  OBSERVED  the median observed in-service time per vehicle-day from driver GPS
            (a13 duty model: 217 min) at each route's cycle time (a06), i.e.
            what today's fleet actually runs. This is a floor on what a
            scheduled operator would run, not a forecast.
Deadhead is added at a06's district-depot bound (D1).

A correction the paper must carry. The engine's Phase-4 emissions column uses
30 g CO2/km for the e-bus backbone ("Indian grid mix electric"). At any
published e-bus energy intensity (~1 kWh/km) and the Indian grid factor
(~0.7 kg CO2/kWh) the figure is of order 700–900 g/km — the engine understates
e-bus tailpipe-equivalent emissions by roughly 25x. The engine column is
therefore not used; the magnitude of the discrepancy is reported.

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

DAYS_PER_YEAR = 365
# (low, high, unit, source, verified)
CONSTANTS = {
    "diesel_kmpl_full_size": (3.5, 5.0, "km/L",
        "ASRTU / CIRT State Transport Undertaking performance statistics (fleet HSD km/L); "
        "range spans city and mofussil operation", False),
    "diesel_kmpl_lpv": (7.0, 10.0, "km/L",
        "manufacturer-rated economy for 12–20 seat minibuses/tempo travellers; no Kashmir record", False),
    "diesel_kgco2_per_l": (2.64, 2.70, "kg CO2/L",
        "IPCC 2006 Guidelines Vol.2 Ch.3 default diesel factor (74,100 kg/TJ) at Indian HSD density", False),
    "ebus_kwh_per_km": (0.9, 1.4, "kWh/km",
        "reported energy intensity of 9–12 m Indian e-buses (CESL / operator disclosures)", False),
    "grid_kgco2_per_kwh": (0.70, 0.82, "kg CO2/kWh",
        "CEA CO2 Baseline Database for the Indian Power Sector (weighted average; high end "
        "adds T&D and charging losses)", False),
    "cost_inr_per_km_full_size": (55.0, 90.0, "INR/km",
        "gross-cost-contract (GCC) per-km rates discovered in recent Indian e-bus and diesel "
        "bus tenders; engine uses 65", False),
    "cost_inr_per_km_lpv": (25.0, 45.0, "INR/km", "private minibus operating cost; no Kashmir record", False),
}
ENGINE_EBUS_GCO2_PER_KM = 30.0
ENGINE_DIESEL_GCO2_PER_KM = 950.0


def main() -> None:
    a = C.load_active().copy()
    dh = pd.read_csv(C.DERIVED / "a06_route_deadhead.csv")[
        ["New_Route_ID", "deadhead_km_per_bus_day_D1", "service_km_per_bus_day_observed"]]
    a = a.merge(dh, on="New_Route_ID", how="left")
    cov = C.read_result("a11_coverage_accessibility")["any_service_reconciliation"]["any_service_population"]

    fleet = a["Fleet_Required"].astype(float)
    lpv_share = a["LPV_Count"] / fleet
    ebus = a["CMP_Trunk"].astype(bool)
    bases = {
        "PLAN": a["Daily_KM"] + a["deadhead_km_per_bus_day_D1"] * fleet,
        "OBSERVED": (a["service_km_per_bus_day_observed"] + a["deadhead_km_per_bus_day_D1"]) * fleet,
    }
    K = CONSTANTS
    rows, out_bases = [], {}
    for name, km_day in bases.items():
        km_yr = km_day * DAYS_PER_YEAR
        km_lpv = km_yr * lpv_share
        km_full_diesel = km_yr * (1 - lpv_share) * (~ebus)
        km_full_ebus = km_yr * (1 - lpv_share) * ebus
        tot_km = float(km_yr.sum())

        def band(fn):
            lo, hi = fn("lo"), fn("hi")
            return (min(lo, hi), max(lo, hi))

        pick = lambda key, e: K[key][0] if e == "lo" else K[key][1]  # noqa: E731
        cost = band(lambda e: float((km_full_diesel + km_full_ebus).sum() * pick("cost_inr_per_km_full_size", e)
                                    + km_lpv.sum() * pick("cost_inr_per_km_lpv", e)))
        # emissions: low = best economy & cleanest grid, high = the reverse
        co2 = band(lambda e: float(
            km_full_diesel.sum() / (K["diesel_kmpl_full_size"][1] if e == "lo" else K["diesel_kmpl_full_size"][0])
            * pick("diesel_kgco2_per_l", e)
            + km_lpv.sum() / (K["diesel_kmpl_lpv"][1] if e == "lo" else K["diesel_kmpl_lpv"][0])
            * pick("diesel_kgco2_per_l", e)
            + km_full_ebus.sum() * pick("ebus_kwh_per_km", e) * pick("grid_kgco2_per_kwh", e)) / 1000.0)
        per_res = (cost[0] / cov, cost[1] / cov)
        out_bases[name] = dict(vehicle_km_per_year=tot_km, cost_inr_per_year=cost, co2_t_per_year=co2,
                               cost_inr_per_covered_resident_per_year=per_res,
                               ebus_share_of_km=float(km_full_ebus.sum() / tot_km))
        rows.append({"Vehicle-km basis": name,
                     "Vehicle-km / yr (M)": round(tot_km / 1e6, 1),
                     "Operating cost / yr (INR crore)": f"{cost[0]/1e7:,.0f}–{cost[1]/1e7:,.0f}",
                     "CO2 / yr (kt)": f"{co2[0]/1e3:,.1f}–{co2[1]/1e3:,.1f}",
                     "Cost per covered resident / yr (INR)": f"{per_res[0]:,.0f}–{per_res[1]:,.0f}"})
    C.write_table(pd.DataFrame(rows), "table05m_cost_emissions",
                  "PROVISIONAL (constants pending D8): annual operating cost and CO2 envelope; "
                  f"covered residents = {cov:,.0f} (network walkshed, a11)")
    C.write_table(pd.DataFrame([dict(Constant=k, Low=v[0], High=v[1], Unit=v[2], Source=v[3],
                                     Verified=v[4]) for k, v in K.items()]),
                  "table05m_constants", "Cost and emission constants used by a14 (all pending verification, D8)")

    ebus_mid = np.mean(K["ebus_kwh_per_km"][:2]) * np.mean(K["grid_kgco2_per_kwh"][:2]) * 1000
    C.write_result(dict(
        status="PROVISIONAL_PENDING_D8",
        constants={k: dict(low=v[0], high=v[1], unit=v[2], source=v[3], verified=v[4]) for k, v in K.items()},
        covered_residents=cov, bases=out_bases,
        engine_emission_factor_check=dict(
            engine_ebus_gco2_per_km=ENGINE_EBUS_GCO2_PER_KM,
            midrange_ebus_gco2_per_km=float(ebus_mid),
            understatement_factor=float(ebus_mid / ENGINE_EBUS_GCO2_PER_KM),
            engine_diesel_gco2_per_km=ENGINE_DIESEL_GCO2_PER_KM,
            note="Engine Phase-4 Emissions_GCO2_Daily not used; e-bus factor implausibly low."),
    ), "a14_cost_emissions")
    for k, v in out_bases.items():
        log.info("%s: %.0fM veh-km/yr; cost INR %.0f–%.0f cr; CO2 %.1f–%.1f kt; per covered resident "
                 "INR %.0f–%.0f", k, v["vehicle_km_per_year"] / 1e6, v["cost_inr_per_year"][0] / 1e7,
                 v["cost_inr_per_year"][1] / 1e7, v["co2_t_per_year"][0] / 1e3, v["co2_t_per_year"][1] / 1e3,
                 *v["cost_inr_per_covered_resident_per_year"])
    log.info("engine e-bus factor %.0f g/km vs mid-range %.0f g/km (x%.0f)", ENGINE_EBUS_GCO2_PER_KM,
             ebus_mid, ebus_mid / ENGINE_EBUS_GCO2_PER_KM)


if __name__ == "__main__":
    main()
