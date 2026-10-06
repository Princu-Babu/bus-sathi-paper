#!/usr/bin/env python
"""
q02_fleet_baseline.py — the existing-fleet baseline against which the plan's fleet
uplift is stated.

Why this module exists. The paper's "+68.5 % over ~600 buses" had no source in the
repository (audit F-02-13 / F-09-06). This module derives the baseline from two
inputs that ARE in the repository:

  1. data/raw/permit_register_summary.csv — counts only, written by
     tools/summarise_permit_register.py from the private all-J&K stage-carriage
     register (which holds vehicle registration numbers and is never copied here).
  2. data/raw/chalo_deployed_buses.csv — the buses the e-bus operator deploys on
     the 30 backbone routes.

Definition (decided by the lead author, not derived): baseline = buses holding a
VALID private permit in the ten Kashmir Division transport offices
+ the e-buses in CHALO's deployment file. Bus-class vehicles are vehicle class
"Bus" and "Omni Bus". JKRTC (the state road transport corporation) is EXCLUDED BY
DECISION; the plan's routes include former JKRTC services, so the baseline
understates the fleet that served the plan's routes. The figures are recomputed
from the inputs on every run; none is typed in.

Validity is evaluated on the register's latest permit date (as_of in the meta
file): valid = Permit Upto on or after that date; expired = before it; placeholder
= the register's dummy end date (before 1990).

A valid permit is not proof that the bus operates. The register also shows how
much of it is stale on paper (expired / placeholder), how few permit rows record
a route, and that permit validity is almost always 1 or 5 years.

Outputs   data/derived/q02_fleet_baseline.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("q02")

SUMMARY_CSV = C.RAW / "permit_register_summary.csv"
SUMMARY_META = C.RAW / "permit_register_summary_meta.json"
BUS_CLASSES = ("Bus", "Omni Bus")
STATUSES = ("valid", "expired", "placeholder", "no_end_date")
CAVEAT = "A valid permit is not proof that the bus operates."


def read_summary(path: Path = SUMMARY_CSV) -> pd.DataFrame:
    return pd.read_csv(path, keep_default_na=False)


def _count(df: pd.DataFrame, col: str = "n_vehicles") -> int:
    return int(df[col].sum())


def stock_counts(summary: pd.DataFrame) -> dict:
    s = summary[(summary["block"] == "stock") & (summary["in_kashmir_division"] == "yes")]
    bus = s[s["vehicle_class"].isin(BUS_CLASSES)]
    out = {"n_offices": int(s["office"].nunique()), "offices": sorted(s["office"].unique())}
    for col, key in (("n_vehicles", "vehicles"), ("n_permit_rows", "permit_rows")):
        by_status = {st: _count(bus[bus["validity_status"] == st], col) for st in STATUSES}
        by_class = {cl: {st: _count(bus[(bus["vehicle_class"] == cl)
                                        & (bus["validity_status"] == st)], col)
                         for st in STATUSES} for cl in BUS_CLASSES}
        out[key] = dict(total=_count(bus, col), by_status=by_status, by_class=by_class)
    return out


def route_recorded(summary: pd.DataFrame, block: str) -> dict:
    s = summary[(summary["block"] == block) & (summary["in_kashmir_division"] == "yes")
                & (summary["vehicle_class"].isin(BUS_CLASSES))]
    res = {}
    for scope, sub in (("all_statuses", s), ("valid_only", s[s["validity_status"] == "valid"])):
        yes = _count(sub[sub["route_recorded"] == "yes"], "n_permit_rows")
        tot = _count(sub, "n_permit_rows")
        res[scope] = dict(n_permit_rows_with_route=yes, n_permit_rows=tot,
                          share=(yes / tot if tot else None))
    return res


def validity_length(summary: pd.DataFrame) -> dict:
    s = summary[(summary["block"] == "validity_length") & (summary["in_kashmir_division"] == "yes")
                & (summary["vehicle_class"].isin(BUS_CLASSES))]
    res = {}
    for scope, sub in (("all_statuses", s), ("valid_only", s[s["validity_status"] == "valid"])):
        g = sub.groupby("validity_years_rounded")["n_permit_rows"].sum()
        tot = int(g.sum())
        res[scope] = dict(
            n_permit_rows=tot,
            counts_by_years={str(k): int(v) for k, v in
                             sorted(g.items(), key=lambda kv: (not str(kv[0]).isdigit(),
                                                               int(kv[0]) if str(kv[0]).isdigit() else 0,
                                                               str(kv[0])))},
            shares_by_years={str(k): float(v / tot) for k, v in g.items()} if tot else {})
    return res


def chalo_ebuses() -> dict:
    dep = pd.read_csv(C.CHALO_DEPLOYED_CSV)
    dep["route_no"] = pd.to_numeric(dep["PROPSED ROUTE NO"], errors="coerce").ffill()
    dep = dep[dep["route_no"].notna() & (dep["PROPSED ROUTE NO"].astype(str) != "TOTAL")]
    per_route = pd.to_numeric(dep.groupby("route_no")["New Deployement"].sum(min_count=1),
                              errors="coerce").fillna(0)
    return dict(n_ebuses=int(per_route.sum()), n_routes=int(per_route.index.nunique()),
                source="data/raw/chalo_deployed_buses.csv (column 'New Deployement', summed by route)")


def uplift(plan_fleet: int, baseline: int) -> dict:
    return dict(baseline=int(baseline), plan_fleet=int(plan_fleet),
                additional_buses=int(plan_fleet - baseline),
                uplift_fraction=float(plan_fleet / baseline - 1.0))


def compute(summary: pd.DataFrame, n_ebuses: int, plan_fleet: int) -> dict:
    """Pure arithmetic on the summary counts; used by the tests."""
    stock = stock_counts(summary)
    valid_private = stock["vehicles"]["by_status"]["valid"]
    total = stock["vehicles"]["total"]
    expired = stock["vehicles"]["by_status"]["expired"]
    placeholder = stock["vehicles"]["by_status"]["placeholder"]
    baseline = valid_private + n_ebuses
    return dict(
        stock=stock, valid_private_buses=valid_private, n_ebuses=n_ebuses,
        baseline_valid_private_plus_ebuses=baseline,
        uplift_vs_valid_private_only=uplift(plan_fleet, valid_private),
        uplift_vs_baseline=uplift(plan_fleet, baseline),
        share_expired_on_paper=dict(
            vehicles_expired=expired, vehicles_placeholder=placeholder, vehicles_total=total,
            share_expired=expired / total, share_expired_or_placeholder=(expired + placeholder) / total,
            base="distinct bus-class vehicles (Bus + Omni Bus) in the ten Kashmir Division offices, "
                 "status on the register's latest permit date"),
    )


def main() -> None:
    summary = read_summary()
    meta = json.loads(SUMMARY_META.read_text(encoding="utf-8"))
    chalo = chalo_ebuses()
    plan = C.load_active()
    plan_fleet = int(plan["Fleet_Required"].sum())
    res = compute(summary, chalo["n_ebuses"], plan_fleet)

    out = dict(
        as_of_date=meta["as_of_date"],
        scope="Kashmir Division: the ten RTO/ARTO offices; vehicle class Bus + Omni Bus",
        caveat=CAVEAT,
        definition=("baseline = distinct bus-class vehicles with a valid permit on the register's "
                    "latest permit date + e-buses in the CHALO deployment file; decided by the lead "
                    "author; every figure recomputed from the inputs"),
        decided_by="lead author (definition); figures computed",
        inputs=dict(permit_register_summary="data/raw/permit_register_summary.csv "
                                            "(counts only; made by tools/summarise_permit_register.py)",
                    permit_register_meta="data/raw/permit_register_summary_meta.json",
                    permit_register_sha256=meta.get("source_file_sha256"),
                    ebus_deployment="data/raw/chalo_deployed_buses.csv"),
        kashmir_division_offices=res["stock"]["offices"],
        n_kashmir_division_offices=res["stock"]["n_offices"],
        bus_class_vehicles=res["stock"]["vehicles"],
        bus_class_permit_rows=res["stock"]["permit_rows"],
        valid_private_buses=res["valid_private_buses"],
        ebuses=chalo,
        jkrtc=dict(status="excluded_by_decision",
                   note=("JKRTC (state corporation) buses are not in the baseline by decision of the "
                         "lead author. The plan's routes include former JKRTC services, so the "
                         "baseline understates the fleet that served those routes and the uplift "
                         "against it is overstated to that extent. No JKRTC fleet count is held in "
                         "the repository.")),
        baseline_valid_private_plus_ebuses=res["baseline_valid_private_plus_ebuses"],
        plan_fleet=plan_fleet,
        plan_fleet_base="sum of Fleet_Required over the 186 active routes of the plan CSV "
                        "(includes the 283-bus SSCL backbone)",
        uplift_vs_valid_private_only=res["uplift_vs_valid_private_only"],
        uplift_vs_baseline=res["uplift_vs_baseline"],
        share_expired_on_paper=res["share_expired_on_paper"],
        route_recorded_either_end=route_recorded(summary, "route_recorded_either_end"),
        route_recorded_both_ends=route_recorded(summary, "route_recorded_both_ends"),
        permit_validity_length_years=validity_length(summary),
        superseded_unsourced_baseline=dict(
            value="~600", status="unsourced",
            note=("The earlier '~600 buses today' figure (engine CLAUDE.md) has no source in this "
                  "repository (audit F-02-13, F-09-06) and is replaced by the computed baseline.")),
        caveats=[CAVEAT,
                 "the register is a paper record: it does not show which permitted buses run, "
                 "nor how many hours a day",
                 "a vehicle holding permits in several offices is counted once per division scope "
                 "(see meta vehicle_rule)"],
        base="permit register: all-J&K stage-carriage register, one row per permit; Kashmir Division "
             "= ten offices; counts are distinct registration numbers (numbers not stored)",
    )
    C.write_result(out, "q02_fleet_baseline")
    log.info("valid private buses %d + e-buses %d = baseline %d; plan %d (uplift %.1f %% vs baseline, "
             "%.1f %% vs valid private only)", out["valid_private_buses"], chalo["n_ebuses"],
             out["baseline_valid_private_plus_ebuses"], plan_fleet,
             100 * out["uplift_vs_baseline"]["uplift_fraction"],
             100 * out["uplift_vs_valid_private_only"]["uplift_fraction"])
    log.info("bus-class vehicles %d: %s; expired on paper %.1f %%", out["bus_class_vehicles"]["total"],
             out["bus_class_vehicles"]["by_status"], 100 * out["share_expired_on_paper"]["share_expired"])


if __name__ == "__main__":
    main()
