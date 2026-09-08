#!/usr/bin/env python
"""
v04_gps_validation.py — validation channel V4: the run-time model against
observed driver GPS.

What this can and cannot establish. GPS records where buses went and how long
they took. It says nothing about how many people wanted to travel. So V4
validates the *supply* half of the method — the chain from geometry to cycle time
to fleet — and cannot validate the composite demand index at all. The paper must
say this in those words. "Validated against ridership" would be false; the
defensible claim is that the run-time model's error has been measured against
observation, decomposed into its causes, and carried forward as an interval.

Scope, stated before any result. Two observational layers are available:

  * Corridor layer — 14 corridor-to-route matches covering 11 distinct plan
    routes of 186 (5.9%), from 5 to 211 runs each. Five are `matched` (the
    observed corridor and the planned route are the same service) and nine
    `partial` (the observed corridor covers part of the planned route, or the
    planned route bundles several observed corridors). Every one lies in Srinagar
    or its immediate belt. This is a corridor-level check, not a network-level
    validation.
  * Route layer — an observed-coverage fraction for all 186 routes, giving the
    share of each planned alignment that appears in the GPS record. This is
    spatial corroboration of the drawn geometry, and its complement is app
    adoption among drivers, not dormancy (finding F4).

The unit trap, and how it is handled. Observed corridor length and planned route
length disagree substantially (obs_km vs eng_km differ by up to 3x on `partial`
matches). Comparing absolute minutes across different lengths would confound the
run-time model with a length mismatch. So the primary comparison is on
length-invariant *rates* — minutes per kilometre and km/h — and the absolute-time
comparison is reported separately with the length disagreement quantified as its
own error channel.

The engine's run-time model, written out so each term can be tested separately
(transit_kashmir_v3.py:2126-2155):

    n_stops     = max(1, floor(L * 1000 / STOP_SPACING_M))     STOP_SPACING_M = 500
    dwell_model = n_stops * STOP_PENALTY_MIN                   STOP_PENALTY_MIN = 0.5
    one_way     = OSRM_min * congestion + dwell_model + junction_penalty
    cycle       = one_way * 2 * TERMINAL_LAYOVER_FACTOR         = 1.10
    cycle       = min(cycle, L * 2 * cap_per_km)   cap: Urban 4.0, Peri 2.5, Regional 1.5

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
     reality instead of protecting against error, and every route it binds on is
     reported at the cap rather than at its modelled value.

Thresholds. The validation protocol sets MAPE < 20% and rank correlation > 0.5.
Both are reported as pass or fail without adjustment. A failed threshold is a
result about the model, not a reason to change the threshold.

Outputs
    data/derived/v04_corridor_comparison.csv   per-corridor errors, all channels
    data/derived/v04_gps_validation.json       headline metrics, decomposition,
                                               dwell regression, Monte Carlo priors
    paper/tables/table06a_v04_runtime.{csv,md}
    paper/tables/table06b_v04_decomposition.{csv,md}
    paper/tables/table06c_v04_cap_binding.{csv,md}

Usage
    python analysis/v04_gps_validation.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("v04")

# Protocol thresholds — fixed in advance, reported without adjustment.
MAPE_THRESHOLD = 20.0
RANK_CORR_THRESHOLD = 0.5

# Engine run-time constants (values as executed; see common.PARAMETERS note).
STOP_SPACING_M = 500.0
STOP_PENALTY_MIN = 0.5
TERMINAL_LAYOVER_FACTOR = 1.10
CONGESTION = {"City_Core": 2.2, "Peri_Urban": 1.4, "Rural": 1.0}
CYCLE_CAP_MIN_PER_KM = {"Urban": 4.0, "Peri_Urban": 2.5, "Regional_District": 1.5}


def mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Mean absolute percentage error, observation in the denominator."""
    a, p = np.asarray(actual, float), np.asarray(predicted, float)
    ok = np.isfinite(a) & np.isfinite(p) & (a != 0)
    return float(100.0 * np.mean(np.abs((p[ok] - a[ok]) / a[ok])))


def bias_pct(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Signed mean percentage error: negative means the model understates."""
    a, p = np.asarray(actual, float), np.asarray(predicted, float)
    ok = np.isfinite(a) & np.isfinite(p) & (a != 0)
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


def dwell_model_min(km: np.ndarray) -> np.ndarray:
    """The engine's dwell term: floor(L*1000/500) stops at 0.5 min, min 1 stop."""
    n_stops = np.maximum(1.0, np.floor(np.asarray(km, float) * 1000.0 / STOP_SPACING_M))
    return n_stops * STOP_PENALTY_MIN


def summarise(name: str, actual, predicted, unit: str) -> dict:
    """One comparison: MAPE, signed bias, both correlations, threshold verdicts."""
    a, p = np.asarray(actual, float), np.asarray(predicted, float)
    ok = np.isfinite(a) & np.isfinite(p) & (a != 0)
    m = mape(a, p)
    rho, rho_p = _corr(a, p, "spearman")
    r, r_p = _corr(a, p, "pearson")
    return dict(
        comparison=name, unit=unit, n=int(ok.sum()),
        observed_median=round(float(np.median(a[ok])), 3),
        modelled_median=round(float(np.median(p[ok])), 3),
        mape_pct=round(m, 1), bias_pct=round(bias_pct(a, p), 1),
        ratio_median=round(float(np.median(p[ok] / a[ok])), 3),
        spearman_rho=round(rho, 3), spearman_p=round(rho_p, 4),
        pearson_r=round(r, 3),
        mape_pass=bool(m < MAPE_THRESHOLD),
        rank_pass=bool(np.isfinite(rho) and rho > RANK_CORR_THRESHOLD),
    )


# ── the four channels ─────────────────────────────────────────────────────────
def channel_length(rc: pd.DataFrame) -> dict:
    """Channel 3: does the plan's route length match the observed corridor?"""
    return summarise("Route length: plan Route_KM vs observed corridor",
                     rc["obs_km"], rc["eng_km"], "km")


def channel_runtime_absolute(rc: pd.DataFrame) -> list[dict]:
    """
    Absolute one-way time, reported for completeness and with the caveat that
    the two series describe different lengths on `partial` matches.
    """
    return [
        summarise("One-way time: plan vs observed total (all matches)",
                  rc["obs_oneway_min"], rc["plan_oneway_min"], "min"),
        summarise("One-way time: plan vs observed total (matched only)",
                  rc.loc[rc["klass"] == "matched", "obs_oneway_min"],
                  rc.loc[rc["klass"] == "matched", "plan_oneway_min"], "min"),
    ]


def channel_runtime_rate(rc: pd.DataFrame) -> list[dict]:
    """
    Primary comparison: minutes per kilometre. Length-invariant, so a `partial`
    match contributes a valid rate even though its absolute time is not
    comparable. Modelled rate uses the plan's own length and time; observed rate
    uses the observed corridor's own length and time.
    """
    return [
        summarise("Pace: plan min/km vs observed min/km (all matches)",
                  rc["obs_min_per_km"], rc["plan_min_per_km"], "min/km"),
        summarise("Pace: plan min/km vs observed min/km (matched only)",
                  rc.loc[rc["klass"] == "matched", "obs_min_per_km"],
                  rc.loc[rc["klass"] == "matched", "plan_min_per_km"], "min/km"),
    ]


def channel_moving_speed(prof: pd.DataFrame) -> list[dict]:
    """
    Channel 1: moving speed. OSRM free-flow speed divided by the asserted
    congestion multiplier is the model's implied moving speed; `moving_kmh` is
    the observed one. Dwell is excluded from both sides, so this is not a unit
    mismatch.
    """
    rows = []
    for zone, mult in CONGESTION.items():
        sub = prof.dropna(subset=["osrm_free_kmh", "moving_kmh"])
        if sub.empty:
            continue
        rows.append(summarise(f"Moving speed: OSRM/{mult:.1f} ({zone}) vs observed",
                              sub["moving_kmh"], sub["osrm_free_kmh"] / mult, "km/h"))
    return rows


def channel_dwell(prof: pd.DataFrame) -> dict:
    """
    Channel 2: dwell. The engine's term is exactly 1.0 min/km with no fixed
    component. Two questions: is the rate right, and is a purely proportional
    form the right shape? The second is answered by regressing observed dwell on
    length with an intercept and testing whether the engine's implied
    (intercept 0, slope 1.0 min/km) lies inside the confidence region.
    """
    import statsmodels.api as sm

    d = prof.dropna(subset=["km", "dwell_min"]).copy()
    x = sm.add_constant(d["km"].to_numpy(float))
    fit = sm.OLS(d["dwell_min"].to_numpy(float), x).fit()
    a, b = float(fit.params[0]), float(fit.params[1])
    ci = fit.conf_int(alpha=0.05)
    a_lo, a_hi = float(ci[0][0]), float(ci[0][1])
    b_lo, b_hi = float(ci[1][0]), float(ci[1][1])

    rate = summarise("Dwell: engine 1.0 min/km vs observed",
                     d["dwell_min"] / d["km"], dwell_model_min(d["km"]) / d["km"],
                     "min/km")
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
    at_cap = pd.DataFrame()
    n_at_cap, share_at_cap = None, None
    if {"Cycle_Time_Min", "Route_KM", "Route_Type"}.issubset(active.columns):
        a = active.copy()
        a["cap_cycle_min"] = (a["Route_KM"].astype(float) * 2.0
                              * a["Route_Type"].map(CYCLE_CAP_MIN_PER_KM).fillna(4.0))
        a["at_cap"] = np.isclose(a["Cycle_Time_Min"].astype(float),
                                 a["cap_cycle_min"], rtol=0.005)
        n_at_cap = int(a["at_cap"].sum())
        share_at_cap = round(float(a["at_cap"].mean()), 3)
        at_cap = (a.loc[a["at_cap"], ["New_Route_ID", "Route_Name", "Route_Type",
                                      "Route_KM", "Cycle_Time_Min", "cap_cycle_min"]]
                  .sort_values("Route_KM", ascending=False))

    return dict(by_class=cap_tab.to_dict(orient="records"),
                n_planned_routes_at_cap=n_at_cap,
                share_planned_routes_at_cap=share_at_cap), cap_tab


def channel_route_coverage(ev: pd.DataFrame) -> dict:
    """
    Route layer: spatial corroboration of the drawn alignments. `obs_frac` is the
    share of a planned route covered by observed GPS runs. Its complement is app
    adoption, not dormancy — so the statistic reported is a floor on the number
    of alignments corroborated, at several thresholds.
    """
    f = ev["obs_frac"].astype(float)
    return dict(
        n_routes=int(len(ev)),
        n_with_any_observation=int((f > 0).sum()),
        obs_frac_median=round(float(f.median()), 3),
        n_corroborated_50pct=int((f >= 0.50).sum()),
        n_corroborated_80pct=int((f >= 0.80).sum()),
        n_fully_covered=int((f >= 0.999).sum()),
        total_observed_runs=int(ev["n_runs"].sum()),
        total_distinct_drivers_max=int(ev["n_drivers"].max()),
        note=("obs_frac is the share of the planned alignment seen in driver GPS. "
              "Routes at zero reflect app adoption among drivers, not proven "
              "dormancy; the corroborated counts are floors."),
    )


def fleet_consequence(rc: pd.DataFrame, active: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """
    What the measured error costs in the units the plan is written in.

    For each `matched` corridor, replace the modelled one-way time with the
    observed one-way pace applied to the planned route length, rebuild the cycle
    with the engine's own layover factor, and resize the fleet with the engine's
    own rule (ceil(cycle/headway) times the spare ratio). Length is held at the
    plan's value so this isolates the run-time error from the length error.
    """
    m = rc[rc["klass"] == "matched"].copy()
    keep = ["New_Route_ID", "Route_Name", "Route_Type", "Route_KM",
            "Cycle_Time_Min", "Headway_Min", "Fleet_Required"]
    have = [c for c in keep if c in active.columns]
    m = m.merge(active[have], left_on="route_id", right_on="New_Route_ID", how="left")

    rows = []
    for _, r in m.iterrows():
        if not np.isfinite(r.get("Headway_Min", np.nan)):
            continue
        km = float(r["Route_KM"])
        obs_cycle = r["obs_min_per_km"] * km * 2.0 * TERMINAL_LAYOVER_FACTOR
        headway = float(r["Headway_Min"])
        fleet_obs = int(np.ceil(obs_cycle / headway) * C.PARAMETERS["FLEET_SPARE_RATIO"]["value"])
        rows.append(dict(
            route_id=r["route_id"], route_name=r.get("Route_Name"),
            corridor=r["corridor"], n_runs=int(r["n_runs"]),
            route_km=round(km, 2), headway_min=headway,
            cycle_plan_min=round(float(r["Cycle_Time_Min"]), 1),
            cycle_observed_min=round(float(obs_cycle), 1),
            cycle_ratio=round(float(obs_cycle / float(r["Cycle_Time_Min"])), 2),
            fleet_plan=int(r["Fleet_Required"]), fleet_observed=fleet_obs,
            fleet_delta=int(fleet_obs - int(r["Fleet_Required"])),
        ))
    tab = pd.DataFrame(rows)
    if tab.empty:
        return dict(note="no matched corridor joined to the plan"), tab
    return dict(
        n_routes=int(len(tab)),
        fleet_plan_total=int(tab["fleet_plan"].sum()),
        fleet_observed_total=int(tab["fleet_observed"].sum()),
        fleet_uplift_pct=round(100.0 * (tab["fleet_observed"].sum()
                                        / tab["fleet_plan"].sum() - 1), 1),
        cycle_ratio_median=round(float(tab["cycle_ratio"].median()), 2),
        note=("Length held at the plan's own Route_KM, so this isolates run-time "
              "error from length error. Extrapolating the uplift to all 186 "
              "routes is NOT supported: these five corridors are the densest in "
              "the record and rural pace is not observed."),
    ), tab


def monte_carlo_priors(prof: pd.DataFrame, rc: pd.DataFrame) -> dict:
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
        recommended_use=("Sample one_way_pace_min_per_km directly in place of the "
                         "OSRM-times-congestion-plus-dwell chain for the urban "
                         "routes, and report fleet as an interval. The observed "
                         "support is Srinagar-weighted, so this prior is applied "
                         "to Urban and Peri_Urban classes only; rural pace is "
                         "unobserved and must stay as modelled with the "
                         "uncertainty stated."),
    )


def main() -> None:
    rc = pd.read_csv(C.GPS_REALITY_CSV)
    prof = pd.read_csv(C.GPS_CORRIDOR_PROFILES_CSV)
    ev = pd.read_csv(C.GPS_ROUTE_EVIDENCE_CSV)
    active = C.load_active()
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

    # Length-invariant rates. Each side uses its own length, which is the point:
    # a `partial` match has a valid pace even without a comparable total.
    rc["obs_min_per_km"] = rc["obs_oneway_min"] / rc["obs_km"]
    rc["plan_min_per_km"] = rc["plan_oneway_min"] / rc["eng_km"]
    rc["osrm_min_per_km"] = rc["osrm_drive_min"] / rc["eng_km"]
    rc["pace_ratio"] = rc["plan_min_per_km"] / rc["obs_min_per_km"]
    rc["length_ratio"] = rc["eng_km"] / rc["obs_km"]

    # OSRM free-flow speed on the corridor, for the moving-speed channel. The
    # profiles file is keyed by corridor number; the reality file by "C<n>".
    prof = prof.copy()
    prof["corridor"] = "C" + prof["corridor_id"].astype(str)
    osrm = rc.set_index("corridor")[["osrm_drive_min", "eng_km"]]
    prof = prof.join(osrm, on="corridor")
    prof["osrm_free_kmh"] = prof["eng_km"] / (prof["osrm_drive_min"] / 60.0)

    # ── the channels ─────────────────────────────────────────────────────────
    runtime_rows = channel_runtime_rate(rc) + channel_runtime_absolute(rc)
    length_row = channel_length(rc)
    speed_rows = channel_moving_speed(prof)
    dwell = channel_dwell(prof)
    cap, cap_tab = channel_cap(prof, active)
    coverage = channel_route_coverage(ev)
    fleet, fleet_tab = fleet_consequence(rc, active)
    priors = monte_carlo_priors(prof, rc)

    runtime_tab = pd.DataFrame(runtime_rows + [length_row])
    decomp_tab = pd.DataFrame(speed_rows + [dwell["rate_comparison"]])

    rc.to_csv(C.DERIVED / "v04_corridor_comparison.csv", index=False)
    if not fleet_tab.empty:
        fleet_tab.to_csv(C.DERIVED / "v04_fleet_consequence.csv", index=False)
    C.write_table(runtime_tab, "table06a_v04_runtime",
                  "Validation V4: planned against observed run time on 14 "
                  "corridor matches, length-invariant pace first")
    C.write_table(decomp_tab, "table06b_v04_decomposition",
                  "Validation V4: run-time error decomposed into moving speed "
                  "and dwell against observed driver GPS")
    C.write_table(cap_tab, "table06c_v04_cap_binding",
                  "Validation V4: observed one-way pace against the per-km "
                  "cycle-time cap asserted by route class")

    out = dict(
        thresholds=dict(mape_pct=MAPE_THRESHOLD, rank_corr=RANK_CORR_THRESHOLD),
        scope=dict(
            n_corridor_matches=int(len(rc)),
            n_distinct_plan_routes=int(rc["route_id"].nunique()),
            n_plan_routes_total=int(len(active)),
            share_of_network_pct=round(100.0 * rc["route_id"].nunique() / len(active), 1),
            n_matched=int((rc["klass"] == "matched").sum()),
            n_partial=int((rc["klass"] == "partial").sum()),
            runs_per_corridor_range=[int(rc["n_runs"].min()), int(rc["n_runs"].max())],
            total_runs=int(rc["n_runs"].sum()),
            geography="Srinagar and immediate belt (Pampore, Narbal); one operator's app",
            validates="the supply chain from geometry to cycle time to fleet",
            does_not_validate=("travel demand, the composite index, or any "
                               "ridership quantity — GPS carries no demand signal"),
        ),
        runtime=runtime_rows, length=length_row,
        moving_speed=speed_rows, dwell=dwell, cycle_cap=cap,
        route_coverage=coverage, fleet_consequence=fleet,
        monte_carlo_priors=priors,
    )
    C.write_result(out, "v04_gps_validation")

    # ── log the story in the order the paper tells it ────────────────────────
    log.info("SCOPE  %d matches -> %d of %d plan routes (%.1f%%), %d total runs",
             len(rc), out["scope"]["n_distinct_plan_routes"], len(active),
             out["scope"]["share_of_network_pct"], out["scope"]["total_runs"])
    for r in runtime_rows + [length_row]:
        log.info("  %-58s n=%2d MAPE %5.1f%% bias %+6.1f%% ratio %.2f rho %+.3f  %s/%s",
                 r["comparison"], r["n"], r["mape_pct"], r["bias_pct"],
                 r["ratio_median"], r["spearman_rho"],
                 "MAPE-PASS" if r["mape_pass"] else "MAPE-FAIL",
                 "RANK-PASS" if r["rank_pass"] else "RANK-FAIL")
    for r in speed_rows:
        log.info("  %-58s MAPE %5.1f%% bias %+6.1f%%", r["comparison"],
                 r["mape_pct"], r["bias_pct"])
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
    log.info("COVER  %d of %d alignments seen in GPS; %d at >=50%%, %d at >=80%%, "
             "%d fully; median obs_frac %.2f",
             coverage["n_with_any_observation"], coverage["n_routes"],
             coverage["n_corroborated_50pct"], coverage["n_corroborated_80pct"],
             coverage["n_fully_covered"], coverage["obs_frac_median"])
    if "fleet_uplift_pct" in fleet:
        log.info("FLEET  re-timing %d matched routes on observed pace: %d -> %d "
                 "buses (%+.1f%%), median cycle ratio %.2f",
                 fleet["n_routes"], fleet["fleet_plan_total"],
                 fleet["fleet_observed_total"], fleet["fleet_uplift_pct"],
                 fleet["cycle_ratio_median"])
    p = priors["one_way_pace_min_per_km"]
    log.info("PRIOR  one-way pace %.2f-%.2f min/km (mode %.2f) -> Monte Carlo "
             "marginal for Urban/Peri_Urban", p["low"], p["high"], p["mode"])


if __name__ == "__main__":
    main()
