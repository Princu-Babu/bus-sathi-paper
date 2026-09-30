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
