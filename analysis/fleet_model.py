"""
fleet_model.py — a vectorised, verified reimplementation of the plan's supply
chain (cycle time -> fleet) and of the paper's tiering rule, shared by the
sensitivity (a08), Monte Carlo (a09) and scenario (a15) modules.

Nothing here is a new model. Each function transcribes an engine step, and
`verify_baseline()` asserts that at baseline parameter values the functions
reproduce the published plan exactly before any perturbation is trusted:

  cycle   transit_kashmir_v3.py::compute_cycle_times (step 7)
            n_stops = max(1, int(L*1000/spacing));  dwell = n_stops * penalty
            one_way = OSRM_min * congestion(zone) + dwell + junction
            cycle   = one_way * 2 * 1.10, then min(cycle, 2 * L * cap[class])
          The five v3.4.5 GPS-measured corridors (apply_reality_v345.py) carry a
          measured cycle with the cap lifted; they are held at that measured
          value under every perturbation because they are observations.
  fleet   transit_kashmir_v3.py::step8_compute_fleet_required
            op = max(1, ceil(cycle / headway)); N = max(ceil(op * spare), floor)
          SSCL e-bus backbone: the engine overwrites the formula with the CHALO
          empirical count where that is larger (the "floor, not override" rule of
          v3.3.4). The per-route empirical floor is recovered as the published
          fleet wherever it exceeds the baseline formula (2 of 30 routes); on the
          other 28 the formula governs and is recomputed.
  headway held at the published value per route. Rural lifeline headways are
          demand-responsive in the engine (apply_regional_demand_headway); the
          sensitivity modules report that dependence separately rather than
          re-running the demand proxy, which the paper quarantines.

The tier model follows the paper (§4.5, §4.7), not the engine: network-catchment
population and opportunity densities, 95th-percentile population cap, min-max
normalisation, CDI = beta*pop + (1-beta)*opp, tourist multiplier mu on the
opportunity channel only (Eq. 5), Jenks k = 3 with the lower-bound (side="left")
convention of a04.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

CAP_MIN_PER_KM = {"Urban": 4.0, "Peri_Urban": 2.5, "Regional_District": 1.5}
CONGESTION_PERI = 1.4
FLOOR = {"Urban": 2, "Peri_Urban": 2, "Regional_District": 1}
V345_MEASURED = ("FDR-050", "FDR-262", "FDR-270", "FDR-370", "FDR-575")
POP_CAP_PERCENTILE = 95

BASE = {k: v["value"] for k, v in C.PARAMETERS.items()}


@dataclass
class PlanArrays:
    """Column arrays for the 186 active routes, in plan order."""
    df: pd.DataFrame
    km: np.ndarray
    osrm_min: np.ndarray
    junction: np.ndarray
    city_core: np.ndarray       # bool
    rtype: np.ndarray           # str
    cap: np.ndarray             # min/km one-way
    floor: np.ndarray
    headway: np.ndarray
    sscl: np.ndarray            # bool
    measured: np.ndarray        # bool (v3.4.5 corridors)
    cycle_pub: np.ndarray
    fleet_pub: np.ndarray
    sscl_floor: np.ndarray      # empirical CHALO floor (0 where formula governs)


def load_arrays() -> PlanArrays:
    a = C.load_active().copy()
    rtype = a["Route_Type"].to_numpy()
    arr = PlanArrays(
        df=a,
        km=a["Route_KM"].to_numpy(float),
        osrm_min=a["OSRM_Duration_S"].to_numpy(float) / 60.0,
        junction=a["Junction_Penalty_Min"].to_numpy(float),
        city_core=(a["Congestion_Zone"] == "City_Core").to_numpy(),
        rtype=rtype,
        cap=np.array([CAP_MIN_PER_KM[t] for t in rtype]),
        floor=np.array([FLOOR[t] for t in rtype]),
        headway=a["Headway_Min"].to_numpy(float),
        sscl=a["CMP_Trunk"].astype(bool).to_numpy(),
        measured=a["New_Route_ID"].isin(V345_MEASURED).to_numpy(),
        cycle_pub=a["Cycle_Time_Min"].to_numpy(float),
        fleet_pub=a["Fleet_Required"].to_numpy(int),
        sscl_floor=np.zeros(len(a), dtype=int),
    )
    formula = fleet_from_cycle(arr, arr.cycle_pub, BASE["FLEET_SPARE_RATIO"], use_sscl_floor=False)
    arr.sscl_floor = np.where(arr.sscl & (arr.fleet_pub > formula), arr.fleet_pub, 0)
    return arr


# ── supply chain ─────────────────────────────────────────────────────────────
def one_way_modelled(arr: PlanArrays, congestion_city: float, stop_penalty: float,
                     stop_spacing_m: float) -> np.ndarray:
    n_stops = np.maximum(1, np.floor(arr.km * 1000.0 / stop_spacing_m))
    cong = np.where(arr.city_core, congestion_city, CONGESTION_PERI)
    return arr.osrm_min * cong + n_stops * stop_penalty + arr.junction


def cycle_time(arr: PlanArrays, congestion_city: float = BASE["CONGESTION_CITY_CORE"],
               stop_penalty: float = BASE["STOP_PENALTY_MIN"],
               stop_spacing_m: float = BASE["STOP_SPACING_M"],
               cap_scale: float | np.ndarray = 1.0,
               pace_override: dict[str, float] | None = None) -> np.ndarray:
    """
    Cycle minutes per route.

    cap_scale multiplies the per-km cap (1.0 = engine; np.inf = cap removed).
    pace_override maps a route class to an observed one-way pace in min/km; for
    non-SSCL, non-measured routes of that class the modelled chain AND the cap
    are replaced by pace * L (the observation-anchored regime of a09). The
    engine's own measured-corridor correction (v3.4.5) did exactly this for the
    five corridors with direct observations.
    """
    ow = one_way_modelled(arr, congestion_city, stop_penalty, stop_spacing_m)
    cyc = ow * 2.0 * C.TERMINAL_LAYOVER_FACTOR
    cap = arr.km * 2.0 * arr.cap * cap_scale
    cyc = np.minimum(cyc, cap)
    if pace_override:
        for cls, pace in pace_override.items():
            m = (arr.rtype == cls) & ~arr.sscl & ~arr.measured
            cyc = np.where(m, pace * arr.km * 2.0 * C.TERMINAL_LAYOVER_FACTOR, cyc)
    cyc = np.where(arr.measured, arr.cycle_pub, cyc)
    return np.maximum(1.0, np.round(cyc, 1))


def fleet_from_cycle(arr: PlanArrays, cycle: np.ndarray, spare: float,
                     headway: np.ndarray | None = None,
                     use_sscl_floor: bool = True) -> np.ndarray:
    h = arr.headway if headway is None else headway
    op = np.maximum(1, np.ceil(cycle / np.maximum(1.0, h)))
    raw = np.maximum(1, np.ceil(np.round(op * spare, 9)))
    n = np.maximum(raw, arr.floor).astype(int)
    if use_sscl_floor:
        n = np.where(arr.sscl, np.maximum(n, arr.sscl_floor), n)
    return n


def fleet(arr: PlanArrays, params: dict | None = None, **cycle_kw) -> np.ndarray:
    p = {**BASE, **(params or {})}
    cyc = cycle_time(arr, p["CONGESTION_CITY_CORE"], p["STOP_PENALTY_MIN"],
                     p["STOP_SPACING_M"], **cycle_kw)
    return fleet_from_cycle(arr, cyc, p["FLEET_SPARE_RATIO"])


def verify_baseline(arr: PlanArrays) -> dict:
    """Assert exact reproduction of the published plan before any sweep."""
    cyc = cycle_time(arr)
    n = fleet(arr)
    cyc_ok = int((np.abs(cyc - arr.cycle_pub) <= 0.11).sum())
    fl_ok = int((n == arr.fleet_pub).sum())
    out = dict(n_routes=len(n), cycle_reproduced=cyc_ok, fleet_reproduced=fl_ok,
               fleet_total=int(n.sum()), fleet_total_published=int(arr.fleet_pub.sum()))
    if cyc_ok != len(n) or fl_ok != len(n):
        raise AssertionError(f"baseline reproduction failed: {out}")
    return out


def at_cap_mask(arr: PlanArrays, **cycle_kw) -> np.ndarray:
    """Routes whose modelled cycle is truncated by the per-km cap."""
    p = {**BASE, **{k: v for k, v in cycle_kw.items() if k in BASE}}
    ow = one_way_modelled(arr, p["CONGESTION_CITY_CORE"], p["STOP_PENALTY_MIN"],
                          p["STOP_SPACING_M"])
    return (ow * 2.0 * C.TERMINAL_LAYOVER_FACTOR > arr.km * 2.0 * arr.cap) & ~arr.measured


# ── tier model (paper §4.5, §4.7) ────────────────────────────────────────────
def _minmax(v: np.ndarray) -> np.ndarray:
    lo, hi = np.nanmin(v), np.nanmax(v)
    return np.zeros_like(v) if hi <= lo else (v - lo) / (hi - lo)


def cdi(pop: np.ndarray, poi_high: np.ndarray, poi_med: np.ndarray, poi_seas: np.ndarray,
        km: np.ndarray, tourist: np.ndarray, beta: float, w_med: float, w_seas: float,
        mu: float) -> np.ndarray:
    dens = np.clip(pop / np.clip(km, 1e-6, None), 0, None)
    dens = np.minimum(dens, np.percentile(dens, POP_CAP_PERCENTILE))
    opp = (poi_high + w_med * poi_med + w_seas * poi_seas) * np.where(tourist, mu, 1.0)
    return beta * _minmax(dens) + (1 - beta) * _minmax(np.clip(opp / np.clip(km, 1e-6, None), 0, None))


def jenks_tiers(v: np.ndarray, k: int = 3) -> np.ndarray:
    """Ordinal tiers 0..k-1 (0 lowest), lower-bound convention as in a04."""
    import jenkspy
    v = np.asarray(v, float)
    if len(np.unique(v)) <= k:
        return np.searchsorted(np.unique(v), v)
    br = np.asarray(jenkspy.jenks_breaks(v, n_classes=k), float)[1:-1]
    # jenkspy interior breaks are observed values that are the UPPER bound of
    # the class below, so a value equal to a break stays below: side="left".
    return np.searchsorted(br, v, side="left")


def cohen_kappa(a, b) -> float:
    a, b = np.asarray(a), np.asarray(b)
    obs = float((a == b).mean())
    exp = sum((a == l).mean() * (b == l).mean() for l in np.union1d(a, b))
    return (obs - exp) / (1 - exp) if exp < 1 else 1.0


# ═════════════════════════════════════════════════════════════════════════════
# Extensions added in the 2026-10 audit fix (wpC). Everything above is
# unchanged in signature and behaviour; the functions below ADD capabilities:
#   * a moving-pace regime that follows the engine's own v3.4.5 method;
#   * switches that remove the "by construction" devices of verify_baseline;
#   * disclosure of the congestion-zone rule as data.
# ═════════════════════════════════════════════════════════════════════════════
import json  # noqa: E402

CITY_CORE_LAT_THRESHOLD = 34.07   # transit_kashmir_v3.py:136 (rule at :2085)
# plan route -> GPS corridor id in data/raw/gps/corridor_profiles.csv; these are
# the five corridors apply_reality_v345.py re-timed from measured moving speed.
V345_CORRIDOR = {"FDR-050": 1, "FDR-262": 4, "FDR-370": 6, "FDR-270": 7, "FDR-575": 8}
NON_PLAN_VERDICTS = ("OUT_OF_AREA", "INFORMAL")   # corridor_profiles.csv `verdict`


def _one_way(arr: PlanArrays, cong_city: float, cong_peri: float, stop_penalty: float,
             stop_spacing_m: float) -> np.ndarray:
    n_stops = np.maximum(1, np.floor(arr.km * 1000.0 / stop_spacing_m))
    cong = np.where(arr.city_core, cong_city, cong_peri)
    return arr.osrm_min * cong + n_stops * stop_penalty + arr.junction


def cycle_time_ext(arr: PlanArrays, congestion_city: float = BASE["CONGESTION_CITY_CORE"],
                   stop_penalty: float = BASE["STOP_PENALTY_MIN"],
                   stop_spacing_m: float = BASE["STOP_SPACING_M"],
                   cap_scale: float | np.ndarray = 1.0,
                   pace_override: dict[str, float] | None = None,
                   moving_pace_override: dict[str, float] | None = None,
                   measured_cycle: str = "published",
                   congestion_peri: float = CONGESTION_PERI) -> np.ndarray:
    """
    `cycle_time` plus additions; with the defaults the result is identical to
    `cycle_time`.

    pace_override         observed EFFECTIVE one-way pace (min/km, in-motion time
                          plus observed dwell/standstill). cycle = pace*L*2*1.10.
                          Replaces the modelled chain and the cap. (Regime B-eff.)
    moving_pace_override  observed MOVING one-way pace (min/km, dwell excluded).
                          This is the engine's own v3.4.5 method
                          (apply_reality_v345.py): drive time = L * moving pace
                          replaces OSRM x congestion; the engine's modelled dwell
                          (n_stops * stop penalty) and junction penalty are kept;
                          cycle = one_way * 2 * 1.10; the cap is lifted. (B-mov.)
    measured_cycle        how the five v3.4.5 corridors are treated:
                          "published" copy the published cycle (verify_baseline's
                                      device D2);
                          "uncapped"  recompute with the modelled chain from the
                                      plan's (back-scaled) OSRM seconds, cap lifted
                                      as the engine did for measured corridors;
                          "capped"    recompute with the modelled chain and the cap
                                      as for any unmeasured route.
    """
    if measured_cycle not in ("published", "uncapped", "capped"):
        raise ValueError(f"measured_cycle={measured_cycle!r}")
    ow = _one_way(arr, congestion_city, congestion_peri, stop_penalty, stop_spacing_m)
    chain = ow * 2.0 * C.TERMINAL_LAYOVER_FACTOR
    cap = arr.km * 2.0 * arr.cap * cap_scale
    cyc = np.minimum(chain, cap)
    if pace_override:
        for cls, pace in pace_override.items():
            m = (arr.rtype == cls) & ~arr.sscl & ~arr.measured
            cyc = np.where(m, pace * arr.km * 2.0 * C.TERMINAL_LAYOVER_FACTOR, cyc)
    if moving_pace_override:
        if pace_override and set(pace_override) & set(moving_pace_override):
            raise ValueError("a route class cannot take both effective and moving pace")
        n_stops = np.maximum(1, np.floor(arr.km * 1000.0 / stop_spacing_m))
        for cls, pace in moving_pace_override.items():
            m = (arr.rtype == cls) & ~arr.sscl & ~arr.measured
            one_way = pace * arr.km + n_stops * stop_penalty + arr.junction
            cyc = np.where(m, one_way * 2.0 * C.TERMINAL_LAYOVER_FACTOR, cyc)
    if measured_cycle == "published":
        cyc = np.where(arr.measured, arr.cycle_pub, cyc)
    elif measured_cycle == "uncapped":
        cyc = np.where(arr.measured, chain, cyc)
    return np.maximum(1.0, np.round(cyc, 1))


def fleet_ext(arr: PlanArrays, params: dict | None = None, use_sscl_floor: bool = True,
              **cycle_kw) -> np.ndarray:
    """`fleet` with the extended cycle switches and an SSCL-floor switch."""
    p = {**BASE, **(params or {})}
    cyc = cycle_time_ext(arr, p["CONGESTION_CITY_CORE"], p["STOP_PENALTY_MIN"],
                         p["STOP_SPACING_M"], **cycle_kw)
    return fleet_from_cycle(arr, cyc, p["FLEET_SPARE_RATIO"], use_sscl_floor=use_sscl_floor)


# ── observed pace: definitions, reconciliation, evidence split ────────────────
def load_corridor_profiles() -> pd.DataFrame:
    prof = pd.read_csv(C.GPS_CORRIDOR_PROFILES_CSV)
    prof["pace_effective"] = 60.0 / prof["effective_kmh"]     # km / (in-motion + dwell)
    prof["pace_moving"] = 60.0 / prof["moving_kmh"]           # km / in-motion only
    prof["is_belt"] = prof["dist_hub_km"] < 20.0
    prof["non_plan_verdict"] = prof["verdict"].isin(NON_PLAN_VERDICTS)
    prof["v345_measured"] = prof["corridor_id"].isin(V345_CORRIDOR.values())
    return prof


def observed_pace_reconciliation() -> list[dict]:
    """
    Every 'observed pace' median quoted anywhere, with the exact corridor set and
    pace definition behind it. Paces are one-way min/km. `effective` includes the
    observed dwell/standstill; `moving` excludes it.
    """
    p = load_corridor_profiles()
    belt = p[p["is_belt"]]
    sets = [
        ("all_18_corridors", p, "v04 cycle_cap.by_class observed_pace_median (4.62): all GPS corridors, effective pace"),
        ("belt_16_corridors_lt20km_of_hub", belt, "a09 prior pool before splitting by zone: corridors < 20 km from the Srinagar hub"),
        ("urban_7_belt_core_and_mid", belt[belt["zone"].isin(["core", "mid"])],
         "a09 Urban prior (Urban = zone core/mid inside the belt); a15 S1 Urban pace"),
        ("peri_9_belt_periphery", belt[belt["zone"] == "periphery"],
         "a09 Peri-Urban prior (zone periphery inside the belt); a15 S1 Peri-Urban pace"),
        ("belt_plan_corridors_only", belt[~belt["non_plan_verdict"]],
         "belt corridors whose verdict is not OUT_OF_AREA/INFORMAL (11 of 16)"),
        ("v345_measured_5", p[p["v345_measured"]],
         "the five corridors the engine itself re-timed in v3.4.5 (directly measured plan routes)"),
        ("regional_2_outside_belt", p[~p["is_belt"]],
         "corridors > 100 km from the hub (rural pace; too few for a prior; a15 S2 bound)"),
    ]
    out = []
    for name, d, what in sets:
        out.append(dict(
            set=name, what=what, n_corridors=int(len(d)),
            corridor_ids=[int(v) for v in d["corridor_id"]],
            n_runs=int(d["n_runs"].sum()),
            median_pace_effective_min_per_km=float(np.median(d["pace_effective"])),
            median_pace_moving_min_per_km=float(np.median(d["pace_moving"])),
            median_effective_kmh=float(np.median(d["effective_kmh"])),
            median_moving_kmh=float(np.median(d["moving_kmh"])),
        ))
    return out


def evidence_split(arr: PlanArrays) -> dict:
    """
    Which routes the observation-anchored regimes touch, and on what evidence.
      measured  the five v3.4.5 corridors: cycle taken from direct GPS in the plan.
      imputed   non-backbone Urban/Peri-Urban routes: pace borrowed from a
                network-level corridor prior (no GPS on the route itself).
      unaffected_backbone  SSCL e-bus routes (fleet from formula + CHALO floor).
      unaffected_regional  non-backbone Regional routes (kept as modelled, cap on).
    """
    imputed = (~arr.sscl) & (~arr.measured) & np.isin(arr.rtype, ["Urban", "Peri_Urban"])
    unaff_bb = arr.sscl & ~arr.measured
    unaff_reg = (~arr.sscl) & (~arr.measured) & (arr.rtype == "Regional_District")
    ids = arr.df["New_Route_ID"].to_numpy()
    assert int(arr.measured.sum() + imputed.sum() + unaff_bb.sum() + unaff_reg.sum()) == len(ids)
    prof = load_corridor_profiles()
    belt = prof[prof["is_belt"]]
    return dict(
        n_routes=int(len(ids)),
        directly_measured=dict(n=int(arr.measured.sum()), route_ids=[str(r) for r in ids[arr.measured]],
                               corridors={k: int(v) for k, v in V345_CORRIDOR.items()},
                               fleet_published=int(arr.fleet_pub[arr.measured].sum())),
        imputed_from_corridor_prior=dict(
            n=int(imputed.sum()),
            by_class={c: int((imputed & (arr.rtype == c)).sum()) for c in ("Urban", "Peri_Urban")},
            fleet_published=int(arr.fleet_pub[imputed].sum()),
            prior_pool_n_corridors=int(len(belt)),
            prior_pool_n_plan_corridors=int((~belt["non_plan_verdict"]).sum()),
            prior_pool_n_non_plan_corridors=int(belt["non_plan_verdict"].sum()),
            prior_pool_of_which_directly_applied_by_engine=int(belt["v345_measured"].sum()),
            prior_pool_corridors=[dict(corridor_id=int(r.corridor_id), zone=r.zone,
                                       verdict=r.verdict, n_runs=int(r.n_runs),
                                       n_drivers=int(r.n_drivers),
                                       pace_effective=round(float(r.pace_effective), 3),
                                       pace_moving=round(float(r.pace_moving), 3),
                                       directly_applied_by_engine=bool(r.v345_measured))
                                  for r in belt.itertuples()],
            note="`verdict` is the GPS pipeline's own corridor-to-permit classification "
                 "(corridor_profiles.csv); it is not re-derived in this repository.",
        ),
        unaffected_backbone=dict(n=int(unaff_bb.sum()), fleet_published=int(arr.fleet_pub[unaff_bb].sum())),
        unaffected_regional=dict(n=int(unaff_reg.sum()), fleet_published=int(arr.fleet_pub[unaff_reg].sum()),
                                 corridors_observed_outside_belt=int((~prof["is_belt"]).sum())),
    )


# ── reproduction, decomposed (F-03-03, F-11-10) ──────────────────────────────
def _agreement(arr: PlanArrays, cyc: np.ndarray, n: np.ndarray) -> dict:
    d = np.abs(cyc - arr.cycle_pub)
    return dict(cycle_reproduced=int((d <= 0.11).sum()), fleet_reproduced=int((n == arr.fleet_pub).sum()),
                fleet_total=int(n.sum()), fleet_total_published=int(arr.fleet_pub.sum()),
                max_abs_cycle_diff_min=float(d.max()),
                routes_fleet_differs=[str(r) for r in arr.df["New_Route_ID"][n != arr.fleet_pub]])


def measured_corridor_recompute(arr: PlanArrays) -> dict:
    """
    Independent re-timing of the five measured routes from the GPS corridor
    profile itself (measured moving speed), not from the plan's cycle or its
    back-scaled OSRM seconds: cycle = (L * 60/v_moving + n_stops*stop_penalty +
    junction) * 2 * 1.10, no cap (apply_reality_v345.py:76-81).
    """
    prof = load_corridor_profiles().set_index("corridor_id")
    rows = []
    for rid, cid in V345_CORRIDOR.items():
        i = int(np.where(arr.df["New_Route_ID"].to_numpy() == rid)[0][0])
        n_stops = max(1, int(arr.km[i] * 1000.0 / BASE["STOP_SPACING_M"]))
        ow = (arr.km[i] / float(prof.loc[cid, "moving_kmh"]) * 60.0
              + n_stops * BASE["STOP_PENALTY_MIN"] + arr.junction[i])
        cyc = round(max(1.0, ow * 2.0 * C.TERMINAL_LAYOVER_FACTOR), 1)
        h = arr.headway[i]
        op = max(1, int(np.ceil(cyc / max(1.0, h))))
        fl = max(int(np.ceil(round(op * BASE["FLEET_SPARE_RATIO"], 9))), int(arr.floor[i]))
        rows.append(dict(route_id=rid, corridor_id=cid, moving_kmh=float(prof.loc[cid, "moving_kmh"]),
                         cycle_recomputed=cyc, cycle_published=float(arr.cycle_pub[i]),
                         fleet_recomputed=fl, fleet_published=int(arr.fleet_pub[i])))
    return dict(routes=rows,
                n_cycle_within_0p11=int(sum(abs(r["cycle_recomputed"] - r["cycle_published"]) <= 0.11
                                            for r in rows)),
                n_fleet_equal=int(sum(r["fleet_recomputed"] == r["fleet_published"] for r in rows)))


def verify_baseline_decomposed(arr: PlanArrays) -> dict:
    """
    Reproduction of the published plan, stated exactly: what is reproduced from
    the model, and what is taken from the published plan as an input.

    `verify_baseline` (kept, unchanged) returns 186/186 cycle and fleet. It does
    so with four devices that the plan supplies rather than the model computing:
      D1 per-km cap       cycle = 2*L*cap on every route the cap truncates;
      D2 measured cycles  the five v3.4.5 routes copy the published cycle;
      D3 SSCL floors      the empirical floor IS the published fleet where that
                          exceeds the formula (2 routes);
      D4 headways         read from the plan for all 186 routes (the rural
                          demand-responsive headway rule is not reimplemented).
    This function counts each device and recomputes the agreement with D2/D3
    removed. D1 and D4 cannot be removed without a different model (D4 is bounded
    by scenario S3 in a15); they are counted, not hidden.
    """
    base = verify_baseline(arr)
    capped = at_cap_mask(arr)
    n_chain = int((~capped & ~arr.measured).sum())
    floor_routes = arr.sscl & (arr.sscl_floor > 0)
    formula_no_floor = fleet_ext(arr, use_sscl_floor=False)
    variants = {}
    spec = [
        ("V0_published_devices_kept", dict(measured_cycle="published"), True),
        ("V1_measured_recomputed_uncapped_sscl_floor_kept", dict(measured_cycle="uncapped"), True),
        ("V2_measured_recomputed_capped_sscl_floor_kept", dict(measured_cycle="capped"), True),
        ("V3_measured_published_sscl_floor_removed", dict(measured_cycle="published"), False),
        ("V4_measured_recomputed_capped_sscl_floor_removed", dict(measured_cycle="capped"), False),
        ("V5_measured_recomputed_uncapped_sscl_floor_removed", dict(measured_cycle="uncapped"), False),
    ]
    for name, kw, floor_on in spec:
        cyc = cycle_time_ext(arr, **kw)
        n = fleet_ext(arr, use_sscl_floor=floor_on, **kw)
        variants[name] = _agreement(arr, cyc, n)
    h = arr.headway
    v4 = variants["V4_measured_recomputed_capped_sscl_floor_removed"]
    return dict(
        existing_verify_baseline=base,
        devices=dict(
            D1_per_km_cap=dict(
                n_routes_cycle_set_by_cap=int(capped.sum()),
                by_class={c: int((capped & (arr.rtype == c)).sum())
                          for c in ("Urban", "Peri_Urban", "Regional_District")},
                n_of_which_sscl=int((capped & arr.sscl).sum()),
                note="On these routes the checked cycle is round(2*L*cap, 1): it verifies one "
                     "multiplication, not the OSRM/congestion/dwell chain."),
            D2_measured_cycles_copied_from_plan=dict(
                n_routes=int(arr.measured.sum()),
                route_ids=[str(r) for r in arr.df["New_Route_ID"][arr.measured]]),
            D3_sscl_floor_defined_from_published_fleet=dict(
                n_routes=int(floor_routes.sum()),
                route_ids=[str(r) for r in arr.df["New_Route_ID"][floor_routes]],
                buses_above_formula=int((arr.fleet_pub[floor_routes] - formula_no_floor[floor_routes]).sum()),
                note="Floor := published fleet where it exceeds the formula, so these cannot fail."),
            D4_headways_taken_as_inputs=dict(
                n_routes=int(len(h)),
                n_regional_type_routes_with_demand_responsive_headway=int((arr.rtype == "Regional_District").sum()),
                headway_counts={str(int(k)): int(v) for k, v in pd.Series(h).value_counts().sort_index().items()},
                note="Rural headway rule (apply_regional_demand_headway) is not reimplemented; "
                     "a15 scenario S3 bounds its effect on fleet."),
            osrm_durations_taken_as_inputs=dict(n_routes=int(len(h))),
        ),
        n_routes_cycle_independently_recomputed=n_chain,
        n_routes_cycle_independently_recomputed_note=
            "not cap-truncated and not measured: the full Eq. 11 chain is what sets the checked cycle",
        agreement=variants,
        agreement_without_devices_D2_D3=v4,
        measured_corridors_recomputed_from_gps_moving_speed=measured_corridor_recompute(arr),
        cycle_tolerance_min=0.11,
        statement=(
            "With the plan's OSRM durations, headways, the five measured cycles and the two SSCL floors "
            "supplied as inputs, the model reproduces cycle and fleet on 186/186 routes and 1,011 buses. "
            "With the measured cycles recomputed under the cap and the SSCL floors removed, it reproduces "
            f"{v4['cycle_reproduced']}/186 cycles, {v4['fleet_reproduced']}/186 fleets and "
            f"{v4['fleet_total']:,} of 1,011 buses. The cap sets the cycle on {int(capped.sum())} routes; "
            f"the full chain is exercised on {n_chain}."),
    )


# ── congestion-zone rule as data (F-03-04, F-08-14) ──────────────────────────
def terminal_latitudes(arr: PlanArrays) -> tuple[np.ndarray, np.ndarray]:
    """Latitude of the first and last vertex of each drawn route, plan order."""
    with open(C.PLAN_GEOJSON, encoding="utf-8") as fh:
        feats = {f["properties"]["New_Route_ID"]: f["geometry"] for f in json.load(fh)["features"]}
    s, e = [], []
    for rid in arr.df["New_Route_ID"]:
        g = feats[rid]
        co = g["coordinates"]
        if g["type"] == "MultiLineString":
            s.append(co[0][0][1]); e.append(co[-1][-1][1])
        else:
            s.append(co[0][1]); e.append(co[-1][1])
    return np.array(s), np.array(e)


def congestion_disclosure(arr: PlanArrays) -> dict:
    """
    How the City-Core multiplier is assigned and how much the fleet depends on it.

    Engine rule (_detect_congestion_zone): City_Core iff EITHER terminal latitude
    exceeds 34.07 N, otherwise Peri_Urban. It is a latitude half-plane, not a
    map of downtown Srinagar, and it is applied to routes of every class. The
    recorded Congestion_Zone is authoritative; the rule is re-applied here to the
    drawn terminals to show how it assigns (the engine used its geocoded terminal
    coordinates, which differ from the drawn ones on a few routes).
    """
    slat, elat = terminal_latitudes(arr)
    n_north = (slat > CITY_CORE_LAT_THRESHOLD).astype(int) + (elat > CITY_CORE_LAT_THRESHOLD).astype(int)
    rule_core = n_north >= 1
    zone_core = arr.city_core
    classes = ("Urban", "Peri_Urban", "Regional_District")
    by_type = {c: dict(n=int((arr.rtype == c).sum()),
                       city_core=int((zone_core & (arr.rtype == c)).sum()),
                       peri_urban=int((~zone_core & (arr.rtype == c)).sum()),
                       city_core_both_terminals_north=int((zone_core & (arr.rtype == c) & (n_north == 2)).sum()),
                       city_core_one_terminal_north=int((zone_core & (arr.rtype == c) & (n_north == 1)).sum()))
               for c in classes}
    grid = {}
    for chi_name, chi in (("chi_2.2_published", BASE["CONGESTION_CITY_CORE"]),
                          ("chi_1.4_peri_urban_everywhere", CONGESTION_PERI)):
        for cap_name, cs in (("cap_on", 1.0), ("cap_removed", np.inf)):
            n = fleet_ext(arr, {"CONGESTION_CITY_CORE": chi}, cap_scale=cs)
            at_cap = at_cap_mask(arr, CONGESTION_CITY_CORE=chi) if cs == 1.0 else None
            grid[f"{chi_name}__{cap_name}"] = dict(
                fleet_total=int(n.sum()),
                fleet_by_class={c: int(n[arr.rtype == c].sum()) for c in classes},
                n_routes_at_cap=None if at_cap is None else int(at_cap.sum()),
                n_routes_fleet_differs_from_published=int((n != arr.fleet_pub).sum()))
    base = fleet_ext(arr)
    chi14 = fleet_ext(arr, {"CONGESTION_CITY_CORE": CONGESTION_PERI})
    nocap = fleet_ext(arr, cap_scale=np.inf)
    nocap14 = fleet_ext(arr, {"CONGESTION_CITY_CORE": CONGESTION_PERI}, cap_scale=np.inf)
    n_cap = int(at_cap_mask(arr).sum())
    return dict(
        rule=f"City_Core iff start OR end terminal latitude > {CITY_CORE_LAT_THRESHOLD} N "
             "(transit_kashmir_v3.py:_detect_congestion_zone; threshold at :136). Latitude half-plane; "
             "no polygon, no route-class test.",
        chi_city_core=BASE["CONGESTION_CITY_CORE"], chi_peri_urban=CONGESTION_PERI,
        n_routes=int(len(arr.km)),
        n_city_core_recorded=int(zone_core.sum()), n_peri_urban_recorded=int((~zone_core).sum()),
        by_route_type=by_type,
        n_regional_assigned_city_core=by_type["Regional_District"]["city_core"],
        rule_reapplied_to_drawn_terminals=dict(
            n_agree_with_recorded_zone=int((rule_core == zone_core).sum()),
            routes_disagree=[str(r) for r in arr.df["New_Route_ID"][rule_core != zone_core]],
            note="Disagreements are routes whose drawn terminal differs from the engine's geocoded terminal "
                 "(e.g. a generic 'Srinagar' point north of 34.07 N)."),
        fleet_grid=grid,
        fleet_dependence=dict(
            published=int(base.sum()),
            chi_1p4_everywhere_cap_on=int(chi14.sum()), delta_chi_cap_on=int(chi14.sum() - base.sum()),
            cap_removed_chi_2p2=int(nocap.sum()), delta_cap_removed=int(nocap.sum() - base.sum()),
            cap_removed_chi_1p4=int(nocap14.sum()),
            chi_effect_when_cap_removed=int(nocap.sum() - nocap14.sum()),
            n_routes_cycle_set_by_cap=n_cap,
            n_routes_where_chi_changes_fleet_cap_on=int((chi14 != base).sum()),
            n_routes_where_chi_changes_fleet_cap_removed=int((nocap14 != nocap).sum()),
            reading=(f"With the cap on, setting the multiplier to the peri-urban 1.4 everywhere moves the fleet by "
                     f"{int(chi14.sum() - base.sum())} buses; the cap, not the multiplier, sets run time on "
                     f"{n_cap} of {len(arr.km)} routes. With the cap removed the multiplier is worth "
                     f"{int(nocap.sum() - nocap14.sum())} buses.")),
    )
