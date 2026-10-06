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

Names. "CHALO" here is the ticketing-data export; the deployed-bus counts come
from CHALO's deployment file (98 buses on 30 routes). The 283 buses are the PLAN's
recommended backbone fleet, not anything an operator deploys.

The comparison. CHALO deploys 98 buses on 30 routes at its current frequency;
the plan runs the same 30 routes at a 15-minute headway. Buses scale with
frequency at fixed cycle time, so the like-for-like reference is the deployed
fleet scaled to 15 minutes:

    h_eff    = service_minutes / (daily departures per route-direction)
    F_scaled = 98 * h_eff / 15

and the test is |F_plan / F_scaled - 1| <= 15 %.

The band. The +-15 % band is NOT pre-registered. It is declared here in the
analysis code (TOLERANCE) and it was written down in the claim ledger on
2026-09-08, three weeks before this module existed; no registry holds it. The
engine's own earlier cross-check (cross_evaluate.py, in the engine repository)
used +-25 %. The verdict is also reported under +-25 % so a reader can see that
the conclusion does not turn on the choice.

The unresolved quantity: what CHALO's "Trip Count" counts. The export does not
define it. Two readings are possible and they move the answer by a factor of 2:

  A  "departure"  Trip Count is departures per route-direction (equivalently, one
                  complete there-and-back cycle counts as one trip):
                  departures per direction per day = Trip Count / (30 routes).
  B  "one-way run" Trip Count counts every one-way run, both directions:
                  departures per direction per day = Trip Count / (30 routes x 2).

Reading A was the module's original (and only) assumption. The only evidence in
the data is the operated distance per counted trip (Operated KM / Trip Count)
against the plan's one-way and round-trip route length for the same 30 routes;
it is reported below under `trip_count_evidence`. It is evidence, not a
definition: `needs_data_owner_confirmation` stays true until CHALO / SSCL says
what the field counts. Both readings are carried through to a verdict and neither
is dropped.

The service day behind h_eff is an assumption (the engine's cross_evaluate used
16 h); it is swept over 13-16 h because the result depends on it.

Also reported, per route (n = 30): rank agreement between CHALO's deployed buses
and the plan's recommended buses (Spearman), which tests whether the plan puts
more buses where the operator already does. It does not depend on the reading.

Inputs    data/raw/chalo_ridership.csv, data/raw/chalo_deployed_buses.csv, plan CSV
Outputs   data/derived/v02_benchmark.json, paper/tables/table06f_v02_benchmark.{csv,md}
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
import fleet_model as F  # noqa: E402

log = C.get_logger("v02")

TOLERANCE = 0.15                 # declared here; NOT pre-registered
ENGINE_CROSSCHECK_TOLERANCE = 0.25   # band used by the engine's own cross_evaluate.py
TARGET_HEADWAY = 15.0
SERVICE_HOURS = (13.0, 14.0, 15.0, 16.0)
ENGINE_SERVICE_HOURS = 16.0
LEDGER_COMMIT = "1b9345f"        # claim ledger first states the +-15 % band (2026-09-08)
MODULE_COMMIT = "ab672e3"        # this module first committed, with its first results
DAYS = {"January": 31, "Feburary": 28, "February": 28, "March": 31, "April": 30, "May": 31,
        "June": 30, "July": 31, "August": 31, "September": 30, "October": 31,
        "November": 30, "December": 31}

READINGS = {
    "A_departure": dict(
        label="A: Trip Count = departures per route-direction (a round trip counts once)",
        direction_divisor=1.0),
    "B_one_way_run": dict(
        label="B: Trip Count = one-way runs, both directions counted",
        direction_divisor=2.0),
}


def num(v) -> float:
    s = re.sub(r"[^\d.]", "", str(v))
    return float(s) if s else np.nan


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=C.ROOT, capture_output=True, text=True,
                           timeout=60, check=True)
        return r.stdout
    except Exception:
        return None


def verdict_from_ratios(ratios: list[float], tol: float) -> dict:
    """Verdict derived only from the band; never chosen."""
    inside = [abs(r - 1.0) <= tol for r in ratios]
    n_in, n = int(sum(inside)), len(ratios)
    if n_in == n:
        v = "pass"
    elif n_in == 0:
        v = "fail"
    else:
        v = "mixed"
    if all(r > 1.0 + tol for r in ratios):
        direction = "plan_above_scaled_reference"
    elif all(r < 1.0 - tol for r in ratios):
        direction = "plan_below_scaled_reference"
    elif n_in == n:
        direction = "within_band"
    else:
        direction = "mixed"
    return dict(verdict=v, n_service_day_assumptions_in_band=n_in,
                n_service_day_assumptions_total=n, band=tol, direction=direction)


def main() -> None:
    from scipy.stats import spearmanr

    rid = pd.read_csv(C.CHALO_RIDERSHIP_CSV)
    rid = rid[rid["Month"].notna() & rid["Trip Count"].notna()].copy()
    rid["month"] = rid["Month"].str.strip()
    rid["days"] = rid["month"].map(DAYS)
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

    # ---- evidence on what "Trip Count" counts: operated km per counted trip -------------
    km_per_trip_monthly = rid["Operated KM"] / rid["Trip Count"]
    km_per_trip_overall = float(rid["Operated KM"].sum() / rid["Trip Count"].sum())
    one_way_mean = float(sscl["Route_KM"].mean())
    one_way_median = float(sscl["Route_KM"].median())
    err_one_way = abs(km_per_trip_overall - one_way_mean) / one_way_mean
    err_round_trip = abs(km_per_trip_overall - 2 * one_way_mean) / (2 * one_way_mean)
    evidence = dict(
        operated_km_per_counted_trip_by_month={
            ("February" if m == "Feburary" else m): float(v)   # source spells it "Feburary"
            for m, v in zip(rid["month"], km_per_trip_monthly)},
        operated_km_per_counted_trip_range=[float(km_per_trip_monthly.min()),
                                            float(km_per_trip_monthly.max())],
        operated_km_per_counted_trip_overall=km_per_trip_overall,
        plan_backbone_one_way_route_km=dict(n_routes=int(len(sscl)), mean=one_way_mean,
                                            median=one_way_median),
        plan_backbone_round_trip_km_mean=2 * one_way_mean,
        relative_gap_to_one_way_mean=err_one_way,
        relative_gap_to_round_trip_mean=err_round_trip,
        evidence_favours=("B_one_way_run" if err_one_way < err_round_trip else "A_departure"),
        base=(f"n = {months} monthly CHALO rows (operated km / trip count) against n = {len(sscl)} "
              f"plan backbone alignments (Route_KM, one-way); in-sample for the plan, since the "
              f"alignments are the CHALO routes"),
        reading=("If a counted trip were a complete there-and-back cycle (reading A), operated km "
                 "per trip would be near the round-trip length; if it is a one-way run (reading B), "
                 "near the one-way length. The observed figure is "
                 f"{km_per_trip_overall:.1f} km against {one_way_mean:.1f} km one-way and "
                 f"{2 * one_way_mean:.1f} km round trip. This is circumstantial: route lengths are "
                 "the plan's, and a definition from the data owner is needed."),
    )

    # ---- both readings x service-day sweep --------------------------------------------
    trips_per_route = daily_trips / n_routes
    by_reading = {}
    sweep_rows = []
    for key, spec in READINGS.items():
        dep_per_dir = trips_per_route / spec["direction_divisor"]
        rows = []
        for h in SERVICE_HOURS:
            h_eff = h * 60.0 / dep_per_dir
            scaled = chalo_fleet * h_eff / TARGET_HEADWAY
            ratio = plan_fleet / scaled
            rows.append(dict(service_hours=h, chalo_effective_headway_min=round(h_eff, 1),
                             chalo_scaled_fleet=round(scaled, 1), plan_fleet=plan_fleet,
                             ratio=round(ratio, 3),
                             within_tolerance=bool(abs(ratio - 1) <= TOLERANCE),
                             within_engine_crosscheck_band=bool(
                                 abs(ratio - 1) <= ENGINE_CROSSCHECK_TOLERANCE)))
        df = pd.DataFrame(rows)
        eng = df[df["service_hours"] == ENGINE_SERVICE_HOURS].iloc[0]
        ratios = df["ratio"].tolist()
        by_reading[key] = dict(
            label=spec["label"],
            departures_per_route_direction_per_day=dep_per_dir,
            sweep=rows,
            engine_assumption=dict(service_hours=ENGINE_SERVICE_HOURS, ratio=float(eng["ratio"]),
                                   within_tolerance=bool(eng["within_tolerance"])),
            ratio_range=[float(df["ratio"].min()), float(df["ratio"].max())],
            n_assumptions_within_tolerance=int(df["within_tolerance"].sum()),
            verdict_declared_band=verdict_from_ratios(ratios, TOLERANCE),
            verdict_engine_crosscheck_band=verdict_from_ratios(ratios, ENGINE_CROSSCHECK_TOLERANCE),
        )
        for r in rows:
            sweep_rows.append(dict(reading=key, **r))
    sweep_a = pd.DataFrame(by_reading["A_departure"]["sweep"])
    sweep_b = pd.DataFrame(by_reading["B_one_way_run"]["sweep"])
    va = by_reading["A_departure"]["verdict_declared_band"]
    vb = by_reading["B_one_way_run"]["verdict_declared_band"]
    both_fail = va["verdict"] == "fail" and vb["verdict"] == "fail"

    m = sscl.merge(per_route.rename("chalo_buses"), left_on="route_no", right_index=True, how="left")
    rho, p = spearmanr(m["chalo_buses"], m["Fleet_Required"])
    rho_cyc, p_cyc = spearmanr(m["chalo_buses"], m["Cycle_Time_Min"])

    tab = pd.DataFrame(sweep_rows).rename(columns={
        "reading": "Trip Count reading", "service_hours": "Service day (h)",
        "chalo_effective_headway_min": "CHALO effective headway (min)",
        "chalo_scaled_fleet": "CHALO deployed fleet scaled to 15 min",
        "plan_fleet": "Plan backbone fleet", "ratio": "Plan / scaled",
        "within_tolerance": "Within ±15%",
        "within_engine_crosscheck_band": "Within ±25% (engine cross-check band)"})
    C.write_table(tab, "table06f_v02_benchmark",
                  f"Validation V2 (consistency check, circular, see text): plan backbone fleet "
                  f"({plan_fleet}) vs the {chalo_fleet} buses CHALO deploys, scaled to a 15-min "
                  f"headway ({months}-month mean), under both readings of the unresolved 'Trip Count' "
                  f"field. The ±15% band is declared in the analysis code, not pre-registered")

    reading_a = by_reading["A_departure"]
    out = dict(
        circularity=["CHALO ridership anchors kappa in Eq. 8",
                     f"engine floors SSCL fleet at CHALO deployment on {n_floored} of 30 routes",
                     "the 30 backbone alignments are the CHALO routes"],
        months=months, chalo_daily_trips=daily_trips, chalo_daily_pax=daily_pax,
        chalo_daily_operated_km=daily_km, chalo_fleet=chalo_fleet, n_routes=n_routes,
        # correctly named quantities (the older keys above/below are kept for readers)
        operator_deployed_buses=chalo_fleet,
        operator_deployed_buses_note=("buses CHALO's deployment file lists on the 30 routes; "
                                      "an operator figure, not a plan output"),
        plan_backbone_fleet=plan_fleet,
        plan_backbone_fleet_note=(f"the PLAN's recommended fleet for the 30 backbone routes: the "
                                  f"larger of the formula and the operator's deployed count, which "
                                  f"binds on {n_floored} of 30 routes. It is not CHALO's deployment."),
        plan_sscl_fleet=plan_fleet, n_routes_floored_by_chalo=n_floored,
        plan_sscl_fleet_note="same quantity as plan_backbone_fleet (283); not what CHALO deploys (98)",
        # the original single-reading block (reading A), kept under its old keys
        sweep=reading_a["sweep"],
        engine_assumption=reading_a["engine_assumption"],
        ratio_range=reading_a["ratio_range"],
        n_assumptions_within_tolerance=reading_a["n_assumptions_within_tolerance"],
        sweep_note=("These top-level sweep/ratio keys are READING A only (the module's original "
                    "assumption). Reading B is under readings.B_one_way_run. Neither reading is "
                    "confirmed."),
        tolerance=TOLERANCE,
        band=dict(
            value=TOLERANCE,
            declared_in=("analysis/v02_benchmark.py (TOLERANCE); first written in the claim ledger at "
                         f"commit {LEDGER_COMMIT} (2026-09-08), before this module was first "
                         f"committed at {MODULE_COMMIT} (2026-09-30)"),
            registered_anywhere=False,
            pre_registered=False,
            git_check_ledger_states_15pct=bool(
                "Ratio within $\\pm 15\\%$"
                in (_git("show", f"{LEDGER_COMMIT}:paper/CLAIM_LEDGER.md") or "")),
            engine_cross_check_band=ENGINE_CROSSCHECK_TOLERANCE,
            engine_cross_check_source=("the engine's cross_evaluate.py in the engine repository "
                                       "(E:/kash/CLAUDE.md section 6: 'within +-25 % band')"),
            wording=("a +-15 % acceptance band declared in the analysis code before V2 was run; "
                     "the engine's earlier cross-check used +-25 %"),
        ),
        trip_count_definition=dict(
            unresolved=True,
            needs_data_owner_confirmation=True,
            question_for_data_owner=("In the CHALO / SSCL ridership export, does 'Trip Count' count "
                                     "one-way runs (each direction separately) or complete round "
                                     "trips / departures per route?"),
            evidence=evidence,
        ),
        needs_data_owner_confirmation=True,
        readings=by_reading,
        verdict_by_reading={k: v["verdict_declared_band"] for k, v in by_reading.items()},
        ratio_range_all_readings=[float(min(sweep_a["ratio"].min(), sweep_b["ratio"].min())),
                                  float(max(sweep_a["ratio"].max(), sweep_b["ratio"].max()))],
        verdict_robust_to_reading=bool(both_fail),
        verdict_summary=(
            f"Reading A: ratio {reading_a['ratio_range'][0]:.2f}-{reading_a['ratio_range'][1]:.2f} "
            f"({va['verdict']}, {va['direction']}); reading B: "
            f"{by_reading['B_one_way_run']['ratio_range'][0]:.2f}-"
            f"{by_reading['B_one_way_run']['ratio_range'][1]:.2f} ({vb['verdict']}, {vb['direction']}), "
            f"against a +-{int(100 * TOLERANCE)} % band over a {SERVICE_HOURS[0]:.0f}-"
            f"{SERVICE_HOURS[-1]:.0f} h service day. "
            + ("The plan falls outside the band under both readings, but on opposite sides of it, "
               "so the sign of the departure from the operator's scaled fleet is not established."
               if both_fail and va["direction"] != vb["direction"] else
               "See readings for the per-reading verdicts.")),
        route_rank=dict(n=int(m["chalo_buses"].notna().sum()), spearman_fleet=float(rho),
                        p_fleet=float(p), spearman_chalo_vs_cycle=float(rho_cyc), p_cycle=float(p_cyc),
                        base="n = 30 backbone routes, plan fleet vs operator-deployed buses; "
                             "independent of the Trip Count reading; partly mechanical because the "
                             "plan floors the fleet at the deployed count on 2 routes"),
    )
    C.write_result(out, "v02_benchmark")
    log.info("operator deploys %d buses on %d routes, %.0f trips/day (%.1f/route), %d-month mean; "
             "plan backbone fleet %d", chalo_fleet, n_routes, daily_trips, trips_per_route, months,
             plan_fleet)
    log.info("operated km per counted trip %.1f (monthly %.1f-%.1f) vs plan one-way mean %.1f / "
             "round trip %.1f -> evidence favours %s", km_per_trip_overall,
             km_per_trip_monthly.min(), km_per_trip_monthly.max(), one_way_mean, 2 * one_way_mean,
             evidence["evidence_favours"])
    for key, br in by_reading.items():
        for r in br["sweep"]:
            log.info("  %-14s %2.0f h: h_eff %.1f min, scaled %.0f, plan %d, ratio %.3f %s",
                     key, r["service_hours"], r["chalo_effective_headway_min"],
                     r["chalo_scaled_fleet"], r["plan_fleet"], r["ratio"],
                     "in band" if r["within_tolerance"] else "outside band")
        log.info("  %s verdict (±15%%): %s; (±25%%): %s", key,
                 br["verdict_declared_band"]["verdict"], br["verdict_engine_crosscheck_band"]["verdict"])
    log.info("route rank: rho(operator-deployed buses, plan fleet) = %.3f (p=%.3g)", rho, p)


if __name__ == "__main__":
    main()
