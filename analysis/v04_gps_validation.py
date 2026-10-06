#!/usr/bin/env python
"""
v04_gps_validation.py — validation channel V4: the run-time model against
observed driver GPS.

What this can and cannot establish. GPS records where buses went and how long
they took. It says nothing about how many people wanted to travel. So V4
validates the *supply* half of the method — the chain from geometry to cycle time
to fleet — and cannot validate the composite demand index at all. Any statement
that the plan was checked using passenger counts would be false; the defensible claim is that the run-time
model's error has been measured against observation on a small, Srinagar-centred
sample, decomposed into its causes, and carried forward as an interval.

Scope. Two observational layers are available:

  * Corridor layer — 14 corridor-to-route matches covering 11 distinct plan
    routes of 186, from 5 to 211 runs each. Five are `matched` (the observed
    corridor and the planned route are the same service) and nine `partial` (the
    observed corridor covers part of the planned route, or the planned route
    bundles several observed corridors). Every one lies in Srinagar or its
    immediate belt. This is a corridor-level check, not a network-level
    validation.
  * Route layer — an observed-coverage fraction for all 186 routes, giving the
    share of each planned alignment that appears in the GPS record. This is
    spatial corroboration of the drawn geometry, and its complement is app
    adoption among drivers, not dormancy.

What a "run" is. The corpus is 2,526 distinct service runs (2,426 after
map-matching), counted once each in `driver_days.csv`. `route_evidence.csv`
counts a run once for EVERY plan route it overlaps, so its sum (43,809) is a
count of run-route incidences, not of runs. The two are never interchangeable;
`corpus` in the output keeps them apart. Per-corridor counts in the reality
check are distinct runs, because the trace pipeline assigns each run to at most
one corridor.

In-sample status. In v3.4.5 the engine re-timed the five `matched` plan routes
from these same corridors (`corrections_applied_v345.csv`). Every statistic
that compares the published plan with those five corridors is therefore
in-sample. Each statistic here is reported three ways: all corridors, the five
re-timed corridors, and the corridors on routes that were never re-timed
(out-of-sample). A sixth corridor, C5, is a second observed corridor on a
re-timed route (FDR-370); it is in neither the five nor the out-of-sample set.

Which plan. `reality_check.csv` carries `plan_oneway_min` = (pre-v3.4.5 cycle) / 2.
The published plan carries the re-timed cycles. Plan-vs-observed time is
reported against both and labelled; the published plan's cycle is the one a
reader of the plan CSV will find.

The unit trap, and how it is handled. Observed corridor length and planned route
length disagree substantially (obs_km vs eng_km differ by up to 3x on `partial`
matches). Comparing absolute minutes across different lengths would confound the
run-time model with a length mismatch. So the primary comparison is on
length-invariant *rates* — minutes per kilometre and km/h — and the absolute-time
comparison is reported separately and flagged where the lengths are not
comparable. Route length is judged on the `matched` corridors only: on a
`partial` match `obs_km` is a sub-segment or a union, not the planned route.

The engine's run-time model, written out so each term can be tested separately
(transit_kashmir_v3.py:2126-2155):

    n_stops     = max(1, floor(L * 1000 / STOP_SPACING_M))     STOP_SPACING_M = 500
    dwell_model = n_stops * STOP_PENALTY_MIN                   STOP_PENALTY_MIN = 0.5
    one_way     = OSRM_min * congestion + dwell_model + junction_penalty
    cycle       = one_way * 2 * TERMINAL_LAYOVER_FACTOR         = 1.10
    cycle       = min(cycle, L * 2 * cap_per_km)   cap: Urban 4.0, Peri 2.5, Regional 1.5

Note that the plan's "one-way" used here is cycle / 2, which includes the 10 %
terminal-layover factor (and the cap where it binds); observed one-way times
carry no layover allowance. The comparison therefore flatters the plan slightly.

Three testable components, and a fourth thing that is not a component at all:

  1. Moving speed. Modelled as OSRM free-flow divided by a congestion
     multiplier asserted at 2.2 in the city core; observed directly as
     `moving_kmh`.
  2. Dwell. Modelled as 2 stops per km at 0.5 min each, i.e. exactly 1.0 min/km
     with no fixed component; observed directly as `dwell_min`.
  3. Length. Modelled as the drawn or substituted `Route_KM`; observed as
     `obs_km`.
  4. The per-km cycle cap. Not a model of anything — an upper bound asserted to
     catch runaway values. If observed run times exceed it, the guard truncates
     reality instead of protecting against error.

Criteria. Two criteria are declared here: MAPE < 20 % and Spearman rank
correlation > 0.5. They were written in this module in the same commit as its
first results (`criteria_declared_in` in the output); they are not registered
anywhere. A comparison passes only if BOTH are met, and the verdict string is
computed mechanically from the reported value and the criterion. The signed mean
bias is descriptive: errors of opposite sign cancel in it, so it is never used
as a pass statistic. With n of 5 neither criterion carries an interval and the
rank criterion has almost no power; rows carry `small_n_caution` accordingly.

Outputs
    data/derived/v04_corridor_comparison.csv   per-corridor errors, all channels
    data/derived/v04_fleet_consequence.csv     matched-corridor fleet re-timing
    data/derived/v04_retimed_routes_v345.csv   snapshot of the v3.4.5 re-timing log
                                               (route code, cycle and fleet before/after)
    data/derived/v04_gps_validation.json       headline metrics, verdicts, decomposition,
                                               dwell regression, Monte Carlo priors
    paper/tables/table06a_v04_runtime.{csv,md}
    paper/tables/table06b_v04_decomposition.{csv,md}
    paper/tables/table06c_v04_cap_binding.{csv,md}

Usage
    python analysis/v04_gps_validation.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("v04")

# Criteria declared in this module (same commit as the first results; not registered).
MAPE_THRESHOLD = 20.0
RANK_CORR_THRESHOLD = 0.5
CRITERIA_DECLARED_IN = "module, same commit as first results"
SMALL_N = 8  # below this a MAPE or rank statistic has no usable interval

# Engine run-time constants (values as executed; see common.PARAMETERS note).
STOP_SPACING_M = 500.0
STOP_PENALTY_MIN = 0.5
TERMINAL_LAYOVER_FACTOR = 1.10
CONGESTION = {"City_Core": 2.2, "Peri_Urban": 1.4, "Rural": 1.0}
CYCLE_CAP_MIN_PER_KM = {"Urban": 4.0, "Peri_Urban": 2.5, "Regional_District": 1.5}
FLEET_FLOOR = {"Urban": 2, "Peri_Urban": 2, "Regional_District": 1}

# Where the v3.4.5 re-timing log lives. The engine checkout is outside this
# repository; the module snapshots the non-personal columns into data/derived so
# that a clean clone can still identify the in-sample set.
RETIMED_LOG_NAME = "corrections_applied_v345.csv"
ENGINE_DIR = Path(os.environ.get("KASHMIR_ENGINE_DIR", "E:/kash"))
RETIMED_SNAPSHOT = C.DERIVED / "v04_retimed_routes_v345.csv"

IN_SAMPLE_NOTE = ("in-sample: the published cycle on these routes was re-anchored to the "
                  "measured moving speed of these same corridors in v3.4.5, so agreement is "
                  "expected by construction and is not evidence that the model is valid")

# Plan versions the plan-vs-observed comparison is run against.
PRE = "pre_v3.4.5_cycle"
PUB = "published_v3.4.5_cycle"

# Figures that exist only as statements in the GPS pipeline's own documentation.
# Recorded with their source and flagged derived=False: they cannot be recomputed
# from the files shipped in this repository.
DOCUMENTED_CLEAN_RUNS = 2426

# One-off count made on 2026-10-05 from the (private, unshipped) trace-repo files
# runs_matched.pkl.gz (driver, clean flag) joined to run_corridor.csv. Counts only;
# no identifier was copied. It exists because per-corridor driver counts cannot be
# added (one driver drives several corridors) and the exact distinct-driver count
# is not recoverable from the shipped aggregates. The shipped aggregates bound it
# (max <= distinct <= sum) and the bound is checked in tests.
PRIVATE_ONE_OFF_CHECK = dict(
    derived=False,
    date="2026-10-05",
    method=("runs_matched.pkl.gz (driver, clean) joined to run_corridor.csv "
            "(run_id, corridor_id); counts only"),
    source_files="E:/bus-sathi-trace/data (private, not shipped)",
    runs_total=2526, runs_clean=2426, driver_accounts_total=157,
    corridor_assigned_runs=989, corridor_assigned_runs_clean=989,
    each_run_in_at_most_one_corridor=True,
    distinct_drivers_by_subset={
        "retimed_in_sample": 48, "out_of_sample": 21, "all": 53,
        "profiled_corridors_all_18": 85, "profiled_corridors_out_of_sample_12": 55,
    },
)


def mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean absolute percentage error, observation in the denominator."""
    a, p = np.asarray(actual, float), np.asarray(predicted, float)
    ok = np.isfinite(a) & np.isfinite(p) & (a != 0)
    if not ok.any():
        return float("nan")
    return float(100.0 * np.mean(np.abs((p[ok] - a[ok]) / a[ok])))


def bias_pct(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Signed mean percentage error: negative means the model understates."""
    a, p = np.asarray(actual, float), np.asarray(predicted, float)
    ok = np.isfinite(a) & np.isfinite(p) & (a != 0)
    if not ok.any():
        return float("nan")
    return float(100.0 * np.mean((p[ok] - a[ok]) / a[ok]))


def _corr(x, y, kind: str = "spearman") -> tuple[float, float]:
    from scipy.stats import pearsonr, spearmanr
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3:
        return float("nan"), float("nan")
    f = spearmanr if kind == "spearman" else pearsonr
    r, p = f(x[ok], y[ok])
    return float(r), float(p)


def spearman_p_exact(x, y, max_n: int = 8) -> float:
    """
    Exact two-sided permutation p-value of Spearman's rho for small n. The
    asymptotic p that scipy reports is meaningless at n = 5 (rho = 1 gives
    0.0000; the exact value is 1/120). Returns nan outside 3 <= n <= max_n.
    """
    from itertools import permutations
    from scipy.stats import rankdata
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    n = int(ok.sum())
    if n < 3 or n > max_n:
        return float("nan")
    rx, ry = rankdata(x[ok]), rankdata(y[ok])
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    perms = np.array(list(permutations(range(n))))
    ryp = ry[perms]                                    # all rearrangements of y's ranks
    rxc = rx - rx.mean()
    num = (ryp - ryp.mean(axis=1, keepdims=True)) @ rxc
    rho_perm = num / (np.sqrt(((ryp - ryp.mean(axis=1, keepdims=True)) ** 2).sum(axis=1))
                      * np.sqrt((rxc ** 2).sum()))
    rho_obs = float(np.corrcoef(rx, ry)[0, 1])
    return float(np.mean(np.abs(rho_perm) >= abs(rho_obs) - 1e-12))


def dwell_model_min(km: np.ndarray) -> np.ndarray:
    """The engine's dwell term: floor(L*1000/500) stops at 0.5 min, min 1 stop."""
    n_stops = np.maximum(1.0, np.floor(np.asarray(km, float) * 1000.0 / STOP_SPACING_M))
    return n_stops * STOP_PENALTY_MIN


def engine_fleet(cycle: float, headway: float, route_type: str) -> int:
    """The engine's fleet rule: ceil(ceil(cycle/headway) * spare), class floor."""
    spare = C.PARAMETERS["FLEET_SPARE_RATIO"]["value"]
    op = max(1.0, float(np.ceil(cycle / max(1.0, headway))))
    return max(int(np.ceil(round(op * spare, 9))), FLEET_FLOOR.get(route_type, 2))


def verdict_from(mape_pct: float, rho: float) -> tuple[str, str, str]:
    """
    Mechanical verdicts from the declared criteria. Takes the values exactly as
    reported (already rounded), so a reader can re-derive every verdict by eye.
    A comparison passes only if both criteria pass; it fails if either fails;
    it is `not_computable` only when a criterion cannot be evaluated and none
    has failed.
    """
    vm = ("not_computable" if not np.isfinite(mape_pct)
          else "pass" if mape_pct < MAPE_THRESHOLD else "fail")
    vr = ("not_computable" if not np.isfinite(rho)
          else "pass" if rho > RANK_CORR_THRESHOLD else "fail")
    if "fail" in (vm, vr):
        v = "fail"
    elif vm == vr == "pass":
        v = "pass"
    else:
        v = "not_computable"
    return vm, vr, v


def _nat(c: str) -> int:
    return int(re.sub(r"\D", "", str(c)))


def membership(sub: pd.DataFrame, code_map: dict | None = None) -> dict:
    """
    Who is in a comparison: corridors, plan routes, runs, drivers. Per-corridor
    run counts are distinct runs (each run belongs to at most one corridor).
    Per-corridor driver counts are NOT additive across corridors, so only a
    bound on the distinct-driver count is derivable here.
    """
    corridors = sorted(sub["corridor"].astype(str).unique(), key=_nat)
    ids = sorted(sub["route_id"].dropna().astype(str).unique()) if "route_id" in sub else []
    codes = sorted({code_map[i] for i in ids if code_map and i in code_map})
    n_pairs = int(sub["n_drivers"].sum()) if len(sub) else 0
    n_max = int(sub["n_drivers"].max()) if len(sub) else 0
    return dict(
        n_corridors=len(corridors), corridors=corridors,
        n_routes=len(ids), route_ids=ids, route_codes=codes,
        n_runs=int(sub["n_runs"].sum()) if len(sub) else 0,
        n_driver_corridor_pairs=n_pairs,
        distinct_drivers_bounds=[n_max, n_pairs],
    )


def summarise(name: str, actual, predicted, unit: str, *, subset: str | None = None,
              plan_basis: str | None = None, members: dict | None = None,
              in_sample: str | None = None, lengths_comparable: bool | None = None,
              note: str | None = None) -> dict:
    """
    One comparison: MAPE, signed mean bias, both correlations, and a verdict
    computed from the declared criteria. `mean_signed_bias_pct` is descriptive
    only and never enters the verdict.
    """
    a, p = np.asarray(actual, float), np.asarray(predicted, float)
    ok = np.isfinite(a) & np.isfinite(p) & (a != 0)
    n = int(ok.sum())
    m = round(mape(a, p), 1) if n else float("nan")
    rho, rho_p = _corr(a, p, "spearman")
    r, r_p = _corr(a, p, "pearson")
    rho_r = round(rho, 3) if np.isfinite(rho) else float("nan")
    vm, vr, v = verdict_from(m, rho_r)
    bias = round(bias_pct(a, p), 1) if n else float("nan")
    row = dict(
        comparison=name, unit=unit, n=n,
        observed_median=round(float(np.median(a[ok])), 3) if n else float("nan"),
        modelled_median=round(float(np.median(p[ok])), 3) if n else float("nan"),
        mape_pct=m, bias_pct=bias, mean_signed_bias_pct=bias,
        ratio_median=round(float(np.median(p[ok] / a[ok])), 3) if n else float("nan"),
        spearman_rho=rho_r,
        spearman_p=round(rho_p, 4) if np.isfinite(rho_p) else float("nan"),
        pearson_r=round(r, 3) if np.isfinite(r) else float("nan"),
        mape_pass=bool(vm == "pass"), rank_pass=bool(vr == "pass"),
        criterion_mape=f"MAPE < {MAPE_THRESHOLD:g} %", value_mape=m,
        criterion_rank=f"Spearman rho > {RANK_CORR_THRESHOLD:g}", value_rank=rho_r,
        verdict_mape=vm, verdict_rank=vr, verdict=v,
        small_n_caution=bool(n < SMALL_N),
    )
    pe = spearman_p_exact(a[ok], p[ok])
    if np.isfinite(pe):
        row["spearman_p_exact"] = round(pe, 4)
    if subset is not None:
        row["subset"] = subset
    if plan_basis is not None:
        row["plan_basis"] = plan_basis
    if in_sample is not None:
        row["in_sample"] = in_sample
    if lengths_comparable is not None:
        row["lengths_comparable"] = bool(lengths_comparable)
    if note:
        row["note"] = note
    if members:
        row.update(members)
    return row


# ── in-sample set ─────────────────────────────────────────────────────────────
def load_retimed(active: pd.DataFrame, rc: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    The five routes re-timed from this GPS in v3.4.5. Read from the engine's
    correction log when the engine checkout is present (and snapshot the
    non-personal columns to data/derived); otherwise read the snapshot. Then
    verify the log against the published plan and the reality check, because the
    in-sample claim stands on that agreement.
    """
    ext = ENGINE_DIR / RETIMED_LOG_NAME
    keep = ["Route_Code", "Route_Name", "Corridor", "Old_Cycle", "New_Cycle",
            "Old_Fleet", "New_Fleet"]
    if ext.exists():
        raw = pd.read_csv(ext)[keep]
        raw.insert(0, "New_Route_ID", raw["Route_Code"].map(
            active.set_index("Route_Code")["New_Route_ID"]))
        retimed = raw.sort_values("New_Route_ID").reset_index(drop=True)
        retimed.to_csv(RETIMED_SNAPSHOT, index=False, lineterminator="\n")
        log.info("re-timing log read from the engine checkout (%s); snapshot refreshed", ext)
    else:
        retimed = pd.read_csv(RETIMED_SNAPSHOT)
        log.info("engine checkout not found; re-timing log read from the snapshot")
    # Fixed text: identical output whichever of the two was read.
    source = (f"{RETIMED_LOG_NAME} of engine v3.4.5 (non-personal columns), stored as "
              "data/derived/v04_retimed_routes_v345.csv")

    if retimed["New_Route_ID"].isna().any():
        raise ValueError("re-timing log has a Route_Code absent from the active plan")
    pub = active.set_index("New_Route_ID")
    cyc_gap = (retimed["New_Cycle"].to_numpy(float)
               - pub.loc[retimed["New_Route_ID"], "Cycle_Time_Min"].to_numpy(float))
    fleet_gap = (retimed["New_Fleet"].to_numpy(float)
                 - pub.loc[retimed["New_Route_ID"], "Fleet_Required"].to_numpy(float))
    matched = rc[rc["klass"] == "matched"].set_index("corridor")
    pre_gap = []
    for _, r in retimed.iterrows():
        pre_gap.append(float(r["Old_Cycle"]) / 2.0 - float(matched.loc[r["Corridor"], "plan_oneway_min"]))
    checks = dict(
        source=source,
        n_routes=int(len(retimed)),
        corridors=sorted(retimed["Corridor"], key=_nat),
        route_ids=sorted(retimed["New_Route_ID"]),
        max_abs_new_cycle_minus_published=round(float(np.abs(cyc_gap).max()), 3),
        max_abs_new_fleet_minus_published=round(float(np.abs(fleet_gap).max()), 3),
        max_abs_old_cycle_half_minus_reality_check_plan=round(float(np.abs(pre_gap).max()), 3),
        corridors_equal_reality_check_matched=bool(
            set(retimed["Corridor"]) == set(rc.loc[rc["klass"] == "matched", "corridor"])),
    )
    if (checks["max_abs_new_cycle_minus_published"] > 0.06
            or checks["max_abs_new_fleet_minus_published"] > 0
            or checks["max_abs_old_cycle_half_minus_reality_check_plan"] > 0.06
            or not checks["corridors_equal_reality_check_matched"]):
        raise ValueError(f"re-timing log disagrees with plan / reality check: {checks}")
    return retimed, checks


def sample_status(row_corridor: str, route_id, retimed: pd.DataFrame) -> str:
    """
    retimed_in_sample        the corridor itself was used to re-time its route
    same_route_as_retimed    another corridor on a route that was re-timed (C5)
    out_of_sample            neither (includes corridors with no plan match)
    """
    if row_corridor in set(retimed["Corridor"]):
        return "retimed_in_sample"
    if isinstance(route_id, str) and route_id in set(retimed["New_Route_ID"]):
        return "same_route_as_retimed"
    return "out_of_sample"


def _subsets(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "all": df,
        "retimed_in_sample": df[df["sample_status"] == "retimed_in_sample"],
        "out_of_sample": df[df["sample_status"] == "out_of_sample"],
    }


def _in_sample_label(subset: str) -> str:
    return {"all": "partly", "retimed_in_sample": "yes", "out_of_sample": "no"}[subset]


# ── the four channels ─────────────────────────────────────────────────────────
def channel_length(rc: pd.DataFrame, code_map: dict) -> tuple[dict, list[dict]]:
    """
    Channel 3: does the plan's route length match the observed corridor?
    Evaluated on the `matched` corridors only: on a `partial` match obs_km is a
    sub-segment or a union of corridors, not the planned route's length. The
    all-14 row is kept, flagged as not a valid length test.
    """
    m = rc[rc["klass"] == "matched"]
    head = summarise(
        "Route length: plan Route_KM vs observed corridor", m["obs_km"], m["eng_km"], "km",
        subset="retimed_in_sample", members=membership(m, code_map),
        in_sample="no", lengths_comparable=True,
        note=("matched corridors only. v3.4.5 re-timed these routes' cycle times but did "
              "not change Route_KM, so length is not fitted to this GPS."))
    allrow = summarise(
        "Route length: plan Route_KM vs observed corridor (all 14 incl. partial)",
        rc["obs_km"], rc["eng_km"], "km", subset="all", members=membership(rc, code_map),
        in_sample="partly", lengths_comparable=False,
        note=("NOT a valid length test: on partial matches obs_km is a sub-segment or union "
              "of corridors. Kept so the earlier all-14 figure can be traced."))
    allrow["counts_toward_headline"] = False
    return head, [head, allrow]


def channel_runtime(rc: pd.DataFrame, code_map: dict) -> list[dict]:
    """
    Plan-vs-observed time, per subset and per plan version. Pace (min/km) is
    length-invariant and valid on every row. Absolute one-way time is valid only
    where the observed corridor and the planned route are the same length class
    (the `matched` rows); elsewhere it is reported but flagged.
    """
    rows = []
    for sname, sub in _subsets(rc).items():
        mem = membership(sub, code_map)
        comparable = bool((sub["klass"] == "matched").all()) if len(sub) else False
        for basis, (ow_col, pace_col) in {
            PRE: ("plan_oneway_min", "plan_min_per_km"),
            PUB: ("plan_oneway_pub_min", "plan_pub_min_per_km"),
        }.items():
            fitted = (sname == "retimed_in_sample" and basis == PUB)
            rows.append(summarise(
                "Pace: plan min/km vs observed min/km", sub["obs_min_per_km"], sub[pace_col],
                "min/km", subset=sname, plan_basis=basis, members=mem,
                in_sample=_in_sample_label(sname), lengths_comparable=True,
                note=IN_SAMPLE_NOTE if fitted else None))
            rows.append(summarise(
                "One-way time: plan vs observed total", sub["obs_oneway_min"], sub[ow_col],
                "min", subset=sname, plan_basis=basis, members=mem,
                in_sample=_in_sample_label(sname), lengths_comparable=comparable,
                note=(IN_SAMPLE_NOTE if fitted else None) if comparable else
                "partial matches: plan and observed totals describe different lengths"))
    return rows


def channel_runtime_legacy(rc: pd.DataFrame) -> list[dict]:
    """
    The four rows earlier versions of this module reported, all against the
    PRE-v3.4.5 plan (`plan_oneway_min` in reality_check.csv). Kept so nothing
    that cites them goes missing; `runtime_by_subset` supersedes them.
    """
    m = rc["klass"] == "matched"
    out = [
        summarise("Pace: plan min/km vs observed min/km (all matches)",
                  rc["obs_min_per_km"], rc["plan_min_per_km"], "min/km"),
        summarise("Pace: plan min/km vs observed min/km (matched only)",
                  rc.loc[m, "obs_min_per_km"], rc.loc[m, "plan_min_per_km"], "min/km"),
        summarise("One-way time: plan vs observed total (all matches)",
                  rc["obs_oneway_min"], rc["plan_oneway_min"], "min"),
        summarise("One-way time: plan vs observed total (matched only)",
                  rc.loc[m, "obs_oneway_min"], rc.loc[m, "plan_oneway_min"], "min"),
    ]
    for r, sub in zip(out, ["all", "retimed_in_sample", "all", "retimed_in_sample"]):
        r["plan_basis"] = PRE
        r["subset"] = sub
        r["in_sample"] = _in_sample_label(sub)
    return out


def channel_moving_speed(prof: pd.DataFrame, code_map: dict | None = None,
                         subset: str | None = None) -> list[dict]:
    """
    Channel 1: moving speed. OSRM free-flow speed divided by the asserted
    congestion multiplier is the model's implied moving speed; `moving_kmh` is
    the observed one. Dwell is excluded from both sides, so this is not a unit
    mismatch. One row per congestion zone, because the divisor depends on zone
    and the corridors are not assigned to zones here.
    """
    rows = []
    sub = prof.dropna(subset=["osrm_free_kmh", "moving_kmh"])
    if sub.empty:
        return rows
    mem = membership(sub, code_map) if "n_runs" in sub else None
    for zone, mult in CONGESTION.items():
        rows.append(summarise(
            f"Moving speed: OSRM/{mult:.1f} ({zone}) vs observed",
            sub["moving_kmh"], sub["osrm_free_kmh"] / mult, "km/h",
            subset=subset, members=mem,
            in_sample=_in_sample_label(subset) if subset else None))
    return rows


def channel_dwell(prof: pd.DataFrame, code_map: dict | None = None,
                  subset: str | None = None, regress: bool = True) -> dict:
    """
    Channel 2: dwell. The engine's term is exactly 1.0 min/km with no fixed
    component. Two questions: is the rate right, and is a purely proportional
    form the right shape? The second is answered by regressing observed dwell on
    length with an intercept and testing whether the engine's implied
    (intercept 0, slope 1.0 min/km) lies inside the confidence region.
    """
    d = prof.dropna(subset=["km", "dwell_min"]).copy()
    rate = summarise("Dwell: engine 1.0 min/km vs observed",
                     d["dwell_min"] / d["km"], dwell_model_min(d["km"]) / d["km"],
                     "min/km", subset=subset, members=membership(d, code_map),
                     in_sample=_in_sample_label(subset) if subset else None)
    if not regress:
        return dict(rate_comparison=rate)

    import statsmodels.api as sm
    x = sm.add_constant(d["km"].to_numpy(float))
    fit = sm.OLS(d["dwell_min"].to_numpy(float), x).fit()
    a, b = float(fit.params[0]), float(fit.params[1])
    ci = fit.conf_int(alpha=0.05)
    a_lo, a_hi = float(ci[0][0]), float(ci[0][1])
    b_lo, b_hi = float(ci[1][0]), float(ci[1][1])
    return dict(
        rate_comparison=rate,
        observed_dwell_min_per_km_median=round(float((d["dwell_min"] / d["km"]).median()), 3),
        observed_dwell_share_median=round(float(d["dwell_share"].median()), 3),
        observed_dwell_share_range=[round(float(d["dwell_share"].min()), 3),
                                    round(float(d["dwell_share"].max()), 3)],
        regression=dict(
            form="dwell_min = a + b * km",
            n=int(fit.nobs), r_squared=round(float(fit.rsquared), 3),
            intercept_min=round(a, 2), intercept_ci95=[round(a_lo, 2), round(a_hi, 2)],
            slope_min_per_km=round(b, 3), slope_ci95=[round(b_lo, 3), round(b_hi, 3)],
            intercept_significant=bool(fit.pvalues[0] < 0.05),
            engine_slope_in_ci=bool(b_lo <= 1.0 <= b_hi),
            engine_intercept_in_ci=bool(a_lo <= 0.0 <= a_hi),
            implied_min_per_stop=round(b / (1000.0 / STOP_SPACING_M), 3),
            membership=membership(d, code_map),
            note=("fitted on all profiled corridors (n corridors, not n runs); the "
                  "engine's dwell term was not re-timed in v3.4.5, so this is not "
                  "fitted to GPS by the plan."),
        ),
    )


def channel_cap(prof: pd.DataFrame, active: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """
    Channel 4: is the per-km cycle cap above or below observed reality?

    The cap is expressed round-trip as L * 2 * cap_per_km, so its one-way
    equivalent is cap_per_km min/km. Observed one-way pace is 60/effective_kmh.
    Any corridor whose observed pace exceeds the cap for its class is a corridor
    the guard would truncate.
    """
    obs_pace = 60.0 / prof["effective_kmh"].to_numpy(float)
    rows = []
    for klass, cap in CYCLE_CAP_MIN_PER_KM.items():
        exceed = obs_pace > cap
        rows.append(dict(
            route_class=klass, cap_min_per_km_one_way=cap,
            n_corridors_observed=int(len(obs_pace)),
            n_observed_exceeding_cap=int(exceed.sum()),
            share_exceeding=round(float(exceed.mean()), 3),
            observed_pace_median=round(float(np.median(obs_pace)), 2),
            observed_pace_p90=round(float(np.percentile(obs_pace, 90)), 2),
        ))
    cap_tab = pd.DataFrame(rows)

    # How many of the 186 planned routes sit at their cap? A route at the cap is
    # reported at an asserted bound rather than at its own modelled cycle time.
    n_at_cap, share_at_cap = None, None
    if {"Cycle_Time_Min", "Route_KM", "Route_Type"}.issubset(active.columns):
        a = active.copy()
        a["cap_cycle_min"] = (a["Route_KM"].astype(float) * 2.0
                              * a["Route_Type"].map(CYCLE_CAP_MIN_PER_KM).fillna(4.0))
        a["at_cap"] = np.isclose(a["Cycle_Time_Min"].astype(float),
                                 a["cap_cycle_min"], rtol=0.005)
        n_at_cap = int(a["at_cap"].sum())
        share_at_cap = round(float(a["at_cap"].mean()), 3)

    return dict(by_class=cap_tab.to_dict(orient="records"),
                n_planned_routes_at_cap=n_at_cap,
                share_planned_routes_at_cap=share_at_cap,
                observed_corridors=membership(prof),
                note=("observed pace is over all profiled corridors (descriptive); "
                      "the at-cap count is over the published plan, in which the "
                      "five re-timed routes were taken off the cap in v3.4.5.")
                ), cap_tab


def channel_route_coverage(ev: pd.DataFrame, corpus: dict) -> dict:
    """
    Route layer: spatial corroboration of the drawn alignments. `obs_frac` is the
    share of a planned route covered by observed GPS runs. Its complement is app
    adoption, not dormancy, so each count is a floor on the alignments
    corroborated at that threshold. "Any observation" is the weakest criterion
    and is not reported as corroboration: the graded counts are.
    """
    f = ev["obs_frac"].astype(float)
    n = int(len(ev))

    def graded(label: str, mask: pd.Series) -> dict:
        k = int(mask.sum())
        return dict(criterion=label, n_routes=k, of=n, share_pct=round(100.0 * k / n, 1))

    strong = (f >= 0.50) & (ev["n_drivers"] >= 2)
    return dict(
        n_routes=n,
        n_with_any_observation=int((f > 0).sum()),
        n_with_any_observation_note=("weakest criterion: any single observation (obs_frac > 0). "
                                     "Not a corroboration count; use graded_corroboration."),
        obs_frac_median=round(float(f.median()), 3),
        obs_frac_median_note=f"median over all {n} routes, including those at zero",
        n_corroborated_50pct=int((f >= 0.50).sum()),
        n_corroborated_80pct=int((f >= 0.80).sum()),
        n_fully_covered=int((f >= 0.999).sum()),
        n_strong_50pct_2drivers=int(strong.sum()),
        graded_corroboration=[
            graded("any observation (obs_frac > 0)", f > 0),
            graded(">= 50 % of planned length observed", f >= 0.50),
            graded(">= 80 % of planned length observed", f >= 0.80),
            graded("fully covered (obs_frac >= 0.999)", f >= 0.999),
            graded(">= 50 % observed by >= 2 drivers (trace-repo 'strong' rule)", strong),
        ],
        corroboration_headline=dict(
            n_routes=int((f >= 0.50).sum()), of=n,
            criterion=">= 50 % of planned length observed in driver GPS",
            read_with=("the any-observation count is the weakest criterion; quote the "
                       ">= 50 % and >= 80 % counts with it")),
        total_observed_runs=int(ev["n_runs"].sum()),
        total_observed_runs_note=("ROUTE-INCIDENCES, not runs: a run is counted once for every "
                                  "plan route it overlaps. Use corpus.distinct_runs_total / "
                                  "distinct_runs_clean for run counts."),
        distinct_runs_total=corpus["distinct_runs_total"]["value"],
        distinct_runs_clean=corpus["distinct_runs_clean"]["value"],
        total_distinct_drivers_max=int(ev["n_drivers"].max()),
        total_distinct_drivers_max_note=("maximum over routes of the per-route driver count; not "
                                         "a total. Distinct drivers in the corpus: "
                                         "corpus.drivers_distinct."),
        note=("obs_frac is the share of the planned alignment seen in driver GPS. "
              "Routes at zero reflect app adoption among drivers, not proven "
              "dormancy; the corroborated counts are floors."),
    )


def corpus_accounting(ev: pd.DataFrame, dd: pd.DataFrame, dd_name: str) -> dict:
    """Run and driver counts that each state what they count, where they come from, and whether derived."""
    incid = int(ev["n_runs"].sum())
    distinct = int(dd["n_runs"].sum())
    drivers = int(dd["driver"].nunique())
    return dict(
        route_incidences=dict(
            value=incid, derived=True,
            source="data/raw/gps/route_evidence.csv: sum of n_runs over the plan routes",
            unit=("run-route incidences: a run is counted once for every plan route it "
                  "overlaps; NOT a count of runs")),
        distinct_runs_total=dict(
            value=distinct, derived=True,
            source=f"data/raw/gps/{dd_name}: sum of n_runs over driver-days",
            unit="distinct service runs after segmentation, before map-match gating"),
        distinct_runs_clean=dict(
            value=DOCUMENTED_CLEAN_RUNS, derived=False,
            source="E:/bus-sathi-trace/README.md:50 ('-> 2,426 clean runs'); AUDIT.md:19",
            unit="distinct service runs passing the map-match agreement gate",
            confirmed_by="PRIVATE_ONE_OFF_CHECK.runs_clean (private file, one-off count)"),
        incidences_per_distinct_run=round(incid / distinct, 1),
        drivers_distinct=dict(
            value=drivers, derived=True,
            source=f"data/raw/gps/{dd_name}: distinct values of the driver column",
            unit=("hashed app driver identifier (driverId, falling back to e-mail then name; "
                  "trace-repo src/pull_cache.py:24): an account, not a device and not a "
                  "verified individual")),
        driver_days=int(len(dd)),
        first_day=str(dd["day"].min()), last_day=str(dd["day"].max()),
        conflicting_statements=[
            dict(statement="~180 self-selected drivers",
                 source="E:/bus-sathi-trace/AUDIT.md:12",
                 status="earlier figure; not reproducible from any shipped file"),
            dict(statement="157 driver devices (claim-ledger wording)",
                 source="paper/CLAIM_LEDGER.md CL-18",
                 status="count is right (157), unit is wrong: accounts, not devices"),
            dict(statement="172 of 186 routes with strong road-level evidence",
                 source="E:/bus-sathi-trace/README.md:86-87",
                 status=("stale: the current route_evidence.csv gives "
                         "route_coverage.n_strong_50pct_2drivers")),
        ],
        private_one_off_check=PRIVATE_ONE_OFF_CHECK,
    )


def fleet_consequence(rc: pd.DataFrame, active: pd.DataFrame,
                      retimed: pd.DataFrame, code_map: dict) -> tuple[dict, pd.DataFrame]:
    """
    What the measured pace costs in the units the plan is written in, on the five
    `matched` corridors.

    For each, replace the modelled one-way time with the observed one-way pace
    applied to the planned route length, rebuild the cycle with the engine's own
    layover factor, and resize with the engine's own rule: ceil(ceil(cycle /
    headway) * spare), class floor. (An earlier version of this function
    truncated with int(), which understates every fleet and produced a spurious
    -14.8 %; the rule is now self-tested against the plan.) Length is held at the
    plan's value so this isolates the run-time error from the length error.

    These five are the routes the plan was re-timed on in v3.4.5, so the
    comparison with the PUBLISHED plan is in-sample: agreement is expected by
    construction. The comparison with the pre-correction fleet is what the GPS
    changed.
    """
    # Self-test of the fleet rule on the published plan (non-SSCL routes only:
    # SSCL fleets are floored at the operator's deployment, not from the formula).
    non_sscl = active[~active["New_Route_ID"].astype(str).str.startswith("SSCL")]
    pred = [engine_fleet(float(r.Cycle_Time_Min), float(r.Headway_Min), str(r.Route_Type))
            for r in non_sscl.itertuples()]
    self_test = dict(
        n_checked=int(len(non_sscl)),
        n_reproduced=int((np.array(pred) == non_sscl["Fleet_Required"].astype(int).to_numpy()).sum()),
        scope="published plan, non-SSCL active routes: engine_fleet(Cycle_Time_Min, Headway_Min, Route_Type) == Fleet_Required",
    )

    m = rc[rc["klass"] == "matched"].copy()
    keep = ["New_Route_ID", "Route_Name", "Route_Type", "Route_KM",
            "Cycle_Time_Min", "Headway_Min", "Fleet_Required"]
    m = m.merge(active[keep], left_on="route_id", right_on="New_Route_ID", how="left")
    m = m.merge(retimed[["New_Route_ID", "Old_Cycle", "Old_Fleet"]],
                on="New_Route_ID", how="left")

    rows = []
    for _, r in m.iterrows():
        if not np.isfinite(r.get("Headway_Min", np.nan)):
            continue
        km = float(r["Route_KM"])
        obs_cycle = r["obs_min_per_km"] * km * 2.0 * TERMINAL_LAYOVER_FACTOR
        headway = float(r["Headway_Min"])
        fleet_obs = engine_fleet(obs_cycle, headway, str(r["Route_Type"]))
        rows.append(dict(
            route_id=r["route_id"], route_name=r.get("Route_Name"),
            corridor=r["corridor"], n_runs=int(r["n_runs"]),
            route_km=round(km, 2), headway_min=headway,
            cycle_plan_min=round(float(r["Cycle_Time_Min"]), 1),
            cycle_observed_min=round(float(obs_cycle), 1),
            cycle_ratio=round(float(obs_cycle / float(r["Cycle_Time_Min"])), 2),
            fleet_plan=int(r["Fleet_Required"]), fleet_observed=fleet_obs,
            fleet_delta=int(fleet_obs - int(r["Fleet_Required"])),
            cycle_plan_pre_correction_min=round(float(r["Old_Cycle"]), 1),
            fleet_plan_pre_correction=int(r["Old_Fleet"]),
            fleet_delta_vs_pre_correction=int(fleet_obs - int(r["Old_Fleet"])),
        ))
    tab = pd.DataFrame(rows)
    if tab.empty:
        return dict(note="no matched corridor joined to the plan",
                    formula_self_test=self_test), tab
    n_obs, n_pub, n_pre = (int(tab["fleet_observed"].sum()), int(tab["fleet_plan"].sum()),
                           int(tab["fleet_plan_pre_correction"].sum()))
    return dict(
        n_routes=int(len(tab)),
        route_ids=sorted(tab["route_id"]),
        route_codes=sorted({code_map[i] for i in tab["route_id"] if i in code_map}),
        n_runs=int(tab["n_runs"].sum()),
        in_sample="yes",
        fleet_plan_total=n_pub,
        fleet_observed_total=n_obs,
        fleet_uplift_pct=round(100.0 * (n_obs / n_pub - 1), 1),
        fleet_uplift_pct_note=("observed-pace fleet against the PUBLISHED plan fleet; in-sample, "
                               "so near-zero change is expected by construction"),
        fleet_plan_pre_correction_total=n_pre,
        fleet_uplift_vs_pre_correction_pct=round(100.0 * (n_obs / n_pre - 1), 1),
        fleet_uplift_vs_pre_correction_note=("observed-pace fleet against the pre-v3.4.5 fleet: "
                                             "the change the GPS caused on these five routes"),
        cycle_ratio_median=round(float(tab["cycle_ratio"].median()), 2),
        cycle_ratio_median_note="observed cycle / PUBLISHED plan cycle",
        formula_self_test=self_test,
        note=("Length held at the plan's own Route_KM, so this isolates run-time "
              "error from length error. Extrapolating the uplift to all 186 "
              "routes is NOT supported: these five corridors are the densest in "
              "the record and rural pace is not observed."),
    ), tab


def monte_carlo_priors(prof: pd.DataFrame, rc: pd.DataFrame, code_map: dict) -> dict:
    """
    Hand finding F3 to the Monte Carlo as measurement rather than as a caveat.

    Two empirical marginals are exported: the observed moving-speed distribution
    (which the congestion multiplier is supposed to reproduce) and the observed
    dwell rate. Both are given as a triangular fit over the observed support with
    the observed median as the mode, which is the least-committal shape that
    respects the range actually seen.
    """
    def tri(series: pd.Series) -> dict:
        s = series.dropna().astype(float)
        return dict(low=round(float(s.min()), 3), mode=round(float(s.median()), 3),
                    high=round(float(s.max()), 3), n=int(len(s)))

    dwell_rate = prof["dwell_min"] / prof["km"]
    pace = 60.0 / prof["effective_kmh"]
    return dict(
        moving_speed_kmh=tri(prof["moving_kmh"]),
        effective_speed_kmh=tri(prof["effective_kmh"]),
        dwell_min_per_km=tri(dwell_rate),
        one_way_pace_min_per_km=tri(pace),
        plan_over_observed_oneway=tri(rc["plan_vs_obs"]),
        plan_over_observed_oneway_note=("pre-v3.4.5 plan one-way / observed one-way, 14 corridor "
                                        "matches (5 of them in-sample for the re-timing)"),
        plan_published_over_observed_oneway=tri(rc["plan_pub_vs_obs"]),
        membership=dict(
            n_corridors=int(len(prof)), n_runs=int(prof["n_runs"].sum()),
            n_driver_corridor_pairs=int(prof["n_drivers"].sum()),
            note=("the observed-pace marginals are over all profiled corridors; "
                  "five of them are the corridors the plan was re-timed on. The support is "
                  "Srinagar-weighted and one operator's app.")),
        recommended_use=("Sample one_way_pace_min_per_km directly in place of the "
                         "OSRM-times-congestion-plus-dwell chain for the urban "
                         "routes, and report fleet as an interval. The observed "
                         "support is Srinagar-weighted, so this prior is applied "
                         "to Urban and Peri_Urban classes only; rural pace is "
                         "unobserved and must stay as modelled with the "
                         "uncertainty stated."),
    )


# ── headline ─────────────────────────────────────────────────────────────────
def _pick(rows: list[dict], comparison: str, subset: str, basis: str | None = None) -> dict:
    for r in rows:
        if (r["comparison"] == comparison and r.get("subset") == subset
                and (basis is None or r.get("plan_basis") == basis)):
            return r
    raise KeyError((comparison, subset, basis))


def build_headline(corpus, scope, by_subset, length, speed_by_subset, dwell_by_subset,
                   coverage, fleet) -> list[str]:
    """Plain sentences a careful author can paste; every number comes from this run."""
    ow, pace = "One-way time: plan vs observed total", "Pace: plan min/km vs observed min/km"
    five_pre, five_pub = (_pick(by_subset, ow, "retimed_in_sample", PRE),
                          _pick(by_subset, ow, "retimed_in_sample", PUB))
    pace_oos = _pick(by_subset, pace, "out_of_sample", PUB)
    pace_all = _pick(by_subset, pace, "all", PUB)
    sp = _pick(speed_by_subset, "Moving speed: OSRM/2.2 (City_Core) vs observed", "all")
    dw = dwell_by_subset["all"]["rate_comparison"]
    drv = PRIVATE_ONE_OFF_CHECK["distinct_drivers_by_subset"]
    runs_five = five_pre["n_runs"]
    out = [
        (f"Corpus: {corpus['distinct_runs_total']['value']:,} distinct driver-GPS service runs "
         f"({corpus['distinct_runs_clean']['value']:,} clean after map-matching) from "
         f"{corpus['drivers_distinct']['value']} hashed driver accounts over "
         f"{corpus['driver_days']} driver-days ({corpus['first_day']} to {corpus['last_day']}). "
         f"The figure {corpus['route_incidences']['value']:,} is the sum of per-route run counts "
         f"over {scope['n_plan_routes_total']} plan routes (run-route incidences, "
         f"{corpus['incidences_per_distinct_run']} per run), not a count of runs."),
        (f"The run-time checks use {scope['n_corridor_matches']} corridor matches on "
         f"{scope['n_distinct_plan_routes']} plan routes ({scope['total_runs']} runs, "
         f"{drv['all']} distinct drivers [private one-off count]), all in Srinagar and its "
         f"immediate belt, one operator's app; the headline plan-vs-observed time statistics "
         f"use only the {five_pre['n']} `matched` corridors ({runs_five} runs, {drv['retimed_in_sample']} "
         f"distinct drivers; routes {', '.join(five_pre['route_ids'])})."),
        (f"Those {five_pre['n']} are the corridors the plan was re-timed on in v3.4.5, so any "
         f"comparison of the published plan with them is in-sample. Plan/observed one-way time on "
         f"them: median ratio {five_pre['ratio_median']:.2f}, MAPE {five_pre['mape_pct']:.1f} % "
         f"against the pre-correction plan (verdict {five_pre['verdict']}); median ratio "
         f"{five_pub['ratio_median']:.2f}, MAPE {five_pub['mape_pct']:.1f} % against the "
         f"published plan (verdict {five_pub['verdict']}; in-sample; n = {five_pub['n']}, "
         f"criterion MAPE < {MAPE_THRESHOLD:g} % and rho > {RANK_CORR_THRESHOLD:g})."),
        (f"Out-of-sample ({pace_oos['n']} partial-match corridors on {pace_oos['n_routes']} routes, "
         f"{pace_oos['n_runs']} runs; {drv['out_of_sample']} distinct drivers [private one-off "
         f"count]): plan/observed pace median ratio {pace_oos['ratio_median']:.2f}, MAPE "
         f"{pace_oos['mape_pct']:.1f} %, rho {pace_oos['spearman_rho']:+.2f} (verdict "
         f"{pace_oos['verdict']}); over all {pace_all['n']} corridors: median ratio "
         f"{pace_all['ratio_median']:.2f}, MAPE {pace_all['mape_pct']:.1f} % (verdict "
         f"{pace_all['verdict']})."),
        (f"Moving speed (OSRM / 2.2 against observed, n = {sp['n']} corridors, {sp['n_runs']} runs): "
         f"MAPE {sp['mape_pct']:.1f} %, rho {sp['spearman_rho']:+.2f}, verdict {sp['verdict']}; "
         f"the mean signed bias of {sp['mean_signed_bias_pct']:+.1f} % is descriptive only "
         f"(errors of opposite sign cancel) and is not a pass statistic."),
        (f"Route length, matched corridors only (n = {length['n']}): MAPE {length['mape_pct']:.1f} %, "
         f"rho {length['spearman_rho']:+.2f}, verdict {length['verdict']} (n < {SMALL_N}: no usable "
         f"interval); on all {scope['n_corridor_matches']} matches incl. partials the same test is "
         f"not valid."),
        (f"Dwell (engine 1.0 min/km against observed, n = {dw['n']} corridors, {dw['n_runs']} runs): "
         f"MAPE {dw['mape_pct']:.1f} %, rho {dw['spearman_rho']:+.2f}, verdict {dw['verdict']}."),
        (f"Alignment coverage of the {coverage['n_routes']} plan routes: observed at all on "
         f"{coverage['n_with_any_observation']} (weakest criterion), >= 50 % of length on "
         f"{coverage['n_corroborated_50pct']}, >= 80 % on {coverage['n_corroborated_80pct']}, "
         f"fully on {coverage['n_fully_covered']}; median {100 * coverage['obs_frac_median']:.0f} % "
         f"of length."),
    ]
    if "fleet_plan_total" in fleet:
        out.append(
            f"Fleet on the {fleet['n_routes']} re-timed routes at observed pace: "
            f"{fleet['fleet_observed_total']} buses against {fleet['fleet_plan_total']} in the "
            f"published plan ({fleet['fleet_uplift_pct']:+.1f} %, in-sample) and "
            f"{fleet['fleet_plan_pre_correction_total']} before re-timing "
            f"({fleet['fleet_uplift_vs_pre_correction_pct']:+.1f} %); not extrapolable to the "
            f"186 routes.")
    out.append(f"Criteria declared in: {CRITERIA_DECLARED_IN}.")
    return out


def main() -> None:
    rc = pd.read_csv(C.GPS_REALITY_CSV)
    prof = pd.read_csv(C.GPS_CORRIDOR_PROFILES_CSV)
    ev = pd.read_csv(C.GPS_ROUTE_EVIDENCE_CSV)
    active = C.load_active()
    dd_name = next(n for n in ("driver_days.csv", "driver_days_deidentified.csv")
                   if (C.RAW / "gps" / n).exists())
    dd = pd.read_csv(C.RAW / "gps" / dd_name)
    log.info("corridor matches %d (%d matched / %d partial), profiles %d, "
             "route-evidence rows %d, active plan routes %d",
             len(rc), (rc["klass"] == "matched").sum(),
             (rc["klass"] == "partial").sum(), len(prof), len(ev), len(active))

    # Join the corridor matches to the plan by route name; the reality file
    # carries the plan's route name, not its ID.
    name_to_id = (active.set_index(active["Route_Name"].astype(str).str.strip())
                  ["New_Route_ID"].to_dict())
    rc["route_id"] = rc["route"].astype(str).str.strip().map(name_to_id)
    unmatched = rc["route_id"].isna().sum()
    if unmatched:
        log.warning("  %d corridor rows did not join to a plan route by name: %s",
                    unmatched, rc.loc[rc["route_id"].isna(), "route"].tolist())
    rc["route_id"] = rc["route_id"].fillna(rc["permit"])
    code_map = active.set_index("New_Route_ID")["Route_Code"].to_dict()

    retimed, retimed_checks = load_retimed(active, rc)
    log.info("re-timed in v3.4.5 (in-sample): %s", retimed_checks["route_ids"])

    # Status of each corridor with respect to the v3.4.5 re-timing.
    rc["sample_status"] = [sample_status(c, r, retimed)
                           for c, r in zip(rc["corridor"], rc["route_id"])]
    rc["route_code"] = rc["route_id"].map(code_map)

    # Plan quantities, both versions. The pre-correction one-way is reality_check's
    # plan_oneway_min (= old cycle / 2); the published one is the plan CSV's
    # current cycle / 2. Both include the 10 % layover factor.
    pub = active.set_index("New_Route_ID")
    rc["plan_oneway_pub_min"] = rc["route_id"].map(pub["Cycle_Time_Min"].astype(float) / 2.0)
    rc["plan_route_km_published"] = rc["route_id"].map(pub["Route_KM"].astype(float))

    # Length-invariant rates. Each side uses its own length, which is the point:
    # a `partial` match has a valid pace even without a comparable total.
    rc["obs_min_per_km"] = rc["obs_oneway_min"] / rc["obs_km"]
    rc["plan_min_per_km"] = rc["plan_oneway_min"] / rc["eng_km"]
    rc["plan_pub_min_per_km"] = rc["plan_oneway_pub_min"] / rc["plan_route_km_published"]
    rc["osrm_min_per_km"] = rc["osrm_drive_min"] / rc["eng_km"]
    rc["pace_ratio"] = rc["plan_min_per_km"] / rc["obs_min_per_km"]
    rc["pace_pub_ratio"] = rc["plan_pub_min_per_km"] / rc["obs_min_per_km"]
    rc["plan_pub_vs_obs"] = rc["plan_oneway_pub_min"] / rc["obs_oneway_min"]
    rc["length_ratio"] = rc["eng_km"] / rc["obs_km"]

    # OSRM free-flow speed on the corridor, for the moving-speed channel. The
    # profiles file is keyed by corridor number; the reality file by "C<n>".
    prof = prof.copy()
    prof["corridor"] = "C" + prof["corridor_id"].astype(str)
    osrm = rc.set_index("corridor")[["osrm_drive_min", "eng_km", "route_id", "klass",
                                     "sample_status"]]
    prof = prof.join(osrm, on="corridor")
    prof["osrm_free_kmh"] = prof["eng_km"] / (prof["osrm_drive_min"] / 60.0)
    prof["sample_status"] = prof["sample_status"].fillna("out_of_sample")

    corpus = corpus_accounting(ev, dd, dd_name)

    # ── the channels ─────────────────────────────────────────────────────────
    runtime_legacy = channel_runtime_legacy(rc)
    runtime_by_subset = channel_runtime(rc, code_map)
    length_row, length_rows = channel_length(rc, code_map)
    speed_rows = channel_moving_speed(prof)
    for r in speed_rows:
        r["subset"], r["in_sample"] = "all", "partly"
    speed_by_subset = []
    for sname, sub in _subsets(prof).items():
        speed_by_subset += channel_moving_speed(sub, code_map, sname)
    dwell = channel_dwell(prof, code_map)
    dwell_by_subset = {s: channel_dwell(sub, code_map, s, regress=False)
                       for s, sub in _subsets(prof).items()}
    cap, cap_tab = channel_cap(prof, active)
    coverage = channel_route_coverage(ev, corpus)
    fleet, fleet_tab = fleet_consequence(rc, active, retimed, code_map)
    priors = monte_carlo_priors(prof, rc, code_map)

    # Membership of the corridor sets the output rests on.
    scope = dict(
        n_corridor_matches=int(len(rc)),
        n_distinct_plan_routes=int(rc["route_id"].nunique()),
        n_plan_routes_total=int(len(active)),
        share_of_network_pct=round(100.0 * rc["route_id"].nunique() / len(active), 1),
        n_matched=int((rc["klass"] == "matched").sum()),
        n_partial=int((rc["klass"] == "partial").sum()),
        runs_per_corridor_range=[int(rc["n_runs"].min()), int(rc["n_runs"].max())],
        total_runs=int(rc["n_runs"].sum()),
        total_runs_note=("distinct runs on the 14 matched or partial corridors: the trace "
                         "pipeline assigns each run to at most one corridor (checked in a "
                         "private one-off count), so per-corridor counts add without "
                         "double counting. NOT the corpus size: see corpus."),
        total_runs_matched_only=int(rc.loc[rc["klass"] == "matched", "n_runs"].sum()),
        n_driver_corridor_pairs_14=int(rc["n_drivers"].sum()),
        n_driver_corridor_pairs_matched_only=int(
            rc.loc[rc["klass"] == "matched", "n_drivers"].sum()),
        driver_count_note=("per-corridor driver counts are not additive (one driver drives "
                           "several corridors); the 69 for the five matched corridors is a "
                           "sum of corridor-driver pairs, not drivers. Distinct drivers: "
                           "corpus.private_one_off_check.distinct_drivers_by_subset, "
                           "bounded by distinct_drivers_bounds in each row."),
        geography="Srinagar and immediate belt (Pampore, Narbal); one operator's app",
        validates="the supply chain from geometry to cycle time to fleet",
        does_not_validate=("travel demand, the composite index, or any "
                           "ridership quantity — GPS carries no demand signal"),
    )
    in_sample = dict(
        retimed_corridors=retimed_checks["corridors"],
        retimed_route_ids=retimed_checks["route_ids"],
        retimed_route_codes=sorted(retimed["Route_Code"]),
        n_routes_retimed=retimed_checks["n_routes"],
        fleet_before=int(retimed["Old_Fleet"].sum()), fleet_after=int(retimed["New_Fleet"].sum()),
        statuses={s: sorted(rc.loc[rc["sample_status"] == s, "corridor"], key=_nat)
                  for s in ("retimed_in_sample", "same_route_as_retimed", "out_of_sample")},
        out_of_sample_route_ids=sorted(rc.loc[rc["sample_status"] == "out_of_sample",
                                              "route_id"].unique()),
        excluded_from_out_of_sample=[
            dict(corridor=c, route_id=r,
                 reason="a second observed corridor on a route that v3.4.5 re-timed")
            for c, r in zip(rc.loc[rc["sample_status"] == "same_route_as_retimed", "corridor"],
                            rc.loc[rc["sample_status"] == "same_route_as_retimed", "route_id"])],
        log_checks=retimed_checks,
        note=("The published plan's cycles on the five routes were re-anchored to the measured "
              "moving speed of these same corridors (apply_reality_v345.py), so plan_basis "
              f"'{PUB}' on them is in-sample. plan_basis '{PRE}' is the model before it saw "
              "this GPS, but the comparison no longer describes the published plan, and the "
              "five were then used to re-time it."),
    )
    pre_pub_gap_oos = float(np.abs(
        rc.loc[rc["sample_status"] == "out_of_sample", "plan_oneway_min"]
        - rc.loc[rc["sample_status"] == "out_of_sample", "plan_oneway_pub_min"]).max())
    plan_versions = dict(
        pre_correction=dict(basis=PRE, column="reality_check.csv plan_oneway_min",
                            definition="(pre-v3.4.5 Cycle_Time_Min) / 2"),
        published=dict(basis=PUB, column="Rationalised_Routes_Kashmir_v3.csv Cycle_Time_Min / 2",
                       definition="(published v3.4.5 Cycle_Time_Min) / 2"),
        max_abs_difference_out_of_sample_min=round(pre_pub_gap_oos, 3),
        note=("on the out-of-sample corridors the two plan versions coincide to rounding "
              "(reality_check rounds to 0.1 min); they differ only on routes v3.4.5 re-timed."),
    )
    headline = build_headline(corpus, scope, runtime_by_subset, length_row, speed_by_subset,
                              dwell_by_subset, coverage, fleet)

    verdict_rows = [r for r in (runtime_by_subset + length_rows + speed_by_subset
                                + [dwell_by_subset[s]["rate_comparison"] for s in dwell_by_subset])]
    verdict_table = [dict(
        test=r["comparison"], subset=r.get("subset"), plan_basis=r.get("plan_basis"),
        in_sample=r.get("in_sample"), n=r["n"], n_runs=r.get("n_runs"),
        criterion_mape=r["criterion_mape"], value_mape=r["value_mape"],
        criterion_rank=r["criterion_rank"], value_rank=r["value_rank"],
        verdict=r["verdict"], mean_signed_bias_pct=r["mean_signed_bias_pct"],
        counts_toward_headline=r.get("counts_toward_headline", True),
        lengths_comparable=r.get("lengths_comparable"),
    ) for r in verdict_rows]

    # ── files ────────────────────────────────────────────────────────────────
    rc.to_csv(C.DERIVED / "v04_corridor_comparison.csv", index=False)
    if not fleet_tab.empty:
        fleet_tab.to_csv(C.DERIVED / "v04_fleet_consequence.csv", index=False)
    runtime_tab = _table(runtime_by_subset + [length_rows[0], length_rows[1]])
    decomp_tab = _table(speed_by_subset
                        + [dwell_by_subset[s]["rate_comparison"] for s in dwell_by_subset])
    C.write_table(runtime_tab, "table06a_v04_runtime",
                  "Validation V4: planned against observed run time, by corridor subset "
                  "and plan version (pre-correction = cycle before v3.4.5 re-timing; "
                  "published = cycle in the plan CSV). in_sample = corridors the "
                  "published plan was re-timed on. bias_pct is the signed mean percentage "
                  "error, descriptive only; verdict applies MAPE < 20 % and Spearman "
                  "rho > 0.5 together.")
    C.write_table(decomp_tab, "table06b_v04_decomposition",
                  "Validation V4: run-time error decomposed into moving speed and dwell "
                  "against observed driver GPS, by corridor subset. bias_pct is the signed "
                  "mean percentage error, descriptive only; verdict applies MAPE < 20 % and "
                  "Spearman rho > 0.5 together.")
    C.write_table(cap_tab, "table06c_v04_cap_binding",
                  "Validation V4: observed one-way pace against the per-km "
                  "cycle-time cap asserted by route class (18 profiled corridors)")

    criteria = dict(
        mape=dict(statistic="mean absolute percentage error, observation in the denominator",
                  rule=f"< {MAPE_THRESHOLD:g} %", threshold=MAPE_THRESHOLD),
        rank=dict(statistic="Spearman rank correlation, observed vs modelled",
                  rule=f"> {RANK_CORR_THRESHOLD:g}", threshold=RANK_CORR_THRESHOLD),
        pass_rule="a comparison passes only if both criteria are met; fails if either fails",
        criteria_declared_in=CRITERIA_DECLARED_IN,
        mean_signed_bias_role=("descriptive only (errors of opposite sign cancel); never a pass "
                               "statistic. Reported as mean_signed_bias_pct."),
        small_n_caution=(f"n < {SMALL_N}: MAPE and rho carry no interval and the rank criterion "
                         "has almost no power; flagged per row in small_n_caution."),
        verdict_basis="computed from the reported (rounded) value and the criterion",
    )

    out = dict(
        headline=" ".join(headline), headline_parts=headline,
        criteria=criteria,
        thresholds=dict(mape_pct=MAPE_THRESHOLD, rank_corr=RANK_CORR_THRESHOLD),
        thresholds_note=f"criteria_declared_in: {CRITERIA_DECLARED_IN}; see criteria.",
        corpus=corpus,
        in_sample=in_sample, plan_versions=plan_versions,
        scope=scope,
        runtime=runtime_legacy,
        runtime_note=("legacy rows: all against the PRE-v3.4.5 plan (plan_basis). Use "
                      "runtime_by_subset for the published plan and for out-of-sample rows."),
        runtime_by_subset=runtime_by_subset,
        length=length_row, length_rows=length_rows,
        length_note=("matched corridors only (n = 5); the earlier all-14 length row mixed in "
                     "partial matches, where obs_km is not the planned route's length. It is in "
                     "length_rows, flagged counts_toward_headline = false."),
        moving_speed=speed_rows, moving_speed_by_subset=speed_by_subset,
        moving_speed_note=("mean_signed_bias_pct is descriptive; the verdict uses MAPE and rho. "
                           "Corridors are not assigned to congestion zones, so each divisor is "
                           "applied to every corridor."),
        dwell=dwell, dwell_by_subset=dwell_by_subset,
        cycle_cap=cap,
        route_coverage=coverage, fleet_consequence=fleet,
        monte_carlo_priors=priors,
        verdict_table=verdict_table,
        matched_corridor_contract=dict(
            rule=("length is judged on `matched` corridors only; partial matches are excluded "
                  "from the length verdict"),
            length_n=length_row["n"], n_matched=scope["n_matched"],
            satisfied=bool(length_row["n"] == scope["n_matched"]),
        ),
        bias_pct_note=("bias_pct = mean_signed_bias_pct: the signed mean of per-corridor "
                       "percentage errors. It is not a pass statistic and can sit near zero "
                       "while MAPE is large and the median ratio is not 1."),
    )
    C.write_result(out, "v04_gps_validation")

    # ── log the story in the order the paper tells it ────────────────────────
    for line in headline:
        log.info("HEADLINE  %s", line)
    for r in runtime_by_subset + length_rows:
        log.info("  %-46s %-18s %-24s n=%2d MAPE %5.1f%% bias %+6.1f%% ratio %.2f rho %+.3f -> %s",
                 r["comparison"][:46], r.get("subset", ""), r.get("plan_basis", ""), r["n"],
                 r["mape_pct"], r["mean_signed_bias_pct"], r["ratio_median"],
                 r["spearman_rho"], r["verdict"])
    for r in speed_by_subset:
        log.info("  %-58s %-18s n=%2d MAPE %5.1f%% bias %+6.1f%% -> %s", r["comparison"],
                 r["subset"], r["n"], r["mape_pct"], r["mean_signed_bias_pct"], r["verdict"])
    reg = dwell["regression"]
    log.info("DWELL  observed %.2f min/km (engine 1.00), share of run time %.2f "
             "(range %.2f-%.2f)", dwell["observed_dwell_min_per_km_median"],
             dwell["observed_dwell_share_median"], *dwell["observed_dwell_share_range"])
    log.info("       dwell = %.2f + %.3f*km  (R2 %.2f); intercept 95%% CI %s "
             "significant=%s; engine slope 1.0 inside CI %s -> implied %.2f min/stop",
             reg["intercept_min"], reg["slope_min_per_km"], reg["r_squared"],
             reg["intercept_ci95"], reg["intercept_significant"],
             reg["engine_slope_in_ci"], reg["implied_min_per_stop"])
    for row in cap["by_class"]:
        log.info("CAP    %-18s cap %.1f min/km -> %d of %d observed corridors "
                 "exceed it (median observed pace %.2f, p90 %.2f)",
                 row["route_class"], row["cap_min_per_km_one_way"],
                 row["n_observed_exceeding_cap"], row["n_corridors_observed"],
                 row["observed_pace_median"], row["observed_pace_p90"])
    log.info("CAP    %s of %d planned routes sit exactly at their cap",
             cap["n_planned_routes_at_cap"], len(active))
    if "fleet_uplift_pct" in fleet:
        log.info("FLEET  fleet rule self-test %d/%d; re-timing %d matched routes on observed "
                 "pace: %d -> %d buses (%+.1f%% vs published, in-sample; %+.1f%% vs pre-correction %d)",
                 fleet["formula_self_test"]["n_reproduced"], fleet["formula_self_test"]["n_checked"],
                 fleet["n_routes"], fleet["fleet_plan_total"], fleet["fleet_observed_total"],
                 fleet["fleet_uplift_pct"], fleet["fleet_uplift_vs_pre_correction_pct"],
                 fleet["fleet_plan_pre_correction_total"])
    p = priors["one_way_pace_min_per_km"]
    log.info("PRIOR  one-way pace %.2f-%.2f min/km (mode %.2f) -> Monte Carlo "
             "marginal for Urban/Peri_Urban", p["low"], p["high"], p["mode"])


def _table(rows: list[dict]) -> pd.DataFrame:
    """Flat table of comparison rows: scalars first, list-valued membership joined."""
    cols = ["comparison", "subset", "plan_basis", "in_sample", "lengths_comparable", "unit",
            "n", "n_corridors", "n_runs", "observed_median", "modelled_median",
            "mape_pct", "bias_pct", "ratio_median", "spearman_rho", "spearman_p",
            "spearman_p_exact", "pearson_r", "mape_pass", "rank_pass", "verdict", "small_n_caution"]
    df = pd.DataFrame(rows)
    out = df[[c for c in cols if c in df.columns]].copy()
    if "plan_basis" in out:
        out["plan_basis"] = out["plan_basis"].fillna("n/a")
    out["corridors"] = [";".join(r) if isinstance(r, list) else "" for r in df.get("corridors", [])]
    out["route_ids"] = [";".join(r) if isinstance(r, list) else "" for r in df.get("route_ids", [])]
    return out


if __name__ == "__main__":
    main()
