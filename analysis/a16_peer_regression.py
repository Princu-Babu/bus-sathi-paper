#!/usr/bin/env python
"""
a16_peer_regression.py — is the plan's fleet size plausible against Indian peers?

The objection this module exists to answer. A supply-side plan that raises the
Kashmir-Division bus fleet to ~1,011 vehicles invites the referee question "how
do you know that is not simply too many (or too few) buses?" A defensible answer
is not an assertion but an external benchmark: fit the empirical relationship
between fleet size and city scale across Indian cities that actually operate
public buses, then read off what that relationship predicts for a place of
Kashmir's population and density, with an honest interval, and report where the
plan sits relative to it.

What the data is, exactly (this is the load-bearing part).
  * Dependent variable — buses. The public-sector city bus fleet HELD, from the
    Association of State Road Transport Undertakings, SRTU Fleet Handbook-2024,
    the "City" column of its 31-Oct-2023 fleet-by-operation table (pp. 7-8). The
    coordinating research agent reconciled every column to the document's own
    printed totals (City 47,653; Rural 101,095; Grand 148,748 all match) and read
    the table by word-coordinate reconstruction, not `pdftotext`, to avoid column
    bleed. This is fleet HELD (not on-road), it INCLUDES wet-leased buses, and it
    covers only ASRTU-member public undertakings — it EXCLUDES private stage- and
    contract-carriage operators and Smart-City SPV e-bus fleets not routed through
    a member STU.
  * Independent variables — population and area. Census of India 2011, Table
    A-04(I) (Class-I towns), file CLASS_I.xlsx, SHA-256 8ab1bafd…a58dd. Urban-
    agglomeration figure where a UA exists, else the municipal-corporation figure;
    area matched to the same basis so density is internally consistent per row.

Three comparability facts that must travel with every number below.
  1. DEFINITION MISMATCH on the dependent variable. The peer figure is a
     PUBLIC-SECTOR fleet; Kashmir's 1,011 is a PLANNED, ALL-OPERATOR fleet (it
     absorbs the private minibus permit network and the SSCL/CHALO e-buses). The
     regression therefore predicts the public STU fleet a city of Kashmir's scale
     tends to run — a floor on "buses that exist", not a like-for-like target. The
     plan sitting above the public-STU expectation is partly this definitional gap,
     not necessarily over-provision. This is the single most important caveat.
  2. UNIT MISMATCH on the predictors. Peers are cities/urban agglomerations;
     Kashmir Division is a 10-district region that is mostly rural. Its density,
     413.8 persons/km^2 over 15,913.7 km^2, sits BELOW the minimum density of every
     fitted city. The density term is therefore an extrapolation far outside
     support, and the two-predictor model's interval at Kashmir is reported but
     flagged unreliable; the population-only model (in which 6.58M is interior to
     the city range) is the more honest basis.
  3. A 12-YEAR DENOMINATOR GAP. Fleet is 2023; population is the 2011 Census (the
     last enumerated; the 2021 round was postponed). Every peer buses-per-1,000 is
     therefore somewhat overstated, and unevenly so across cities. Stated, not
     silently projected away.

Srinagar is deliberately EXCLUDED from the fit. Its only handbook figure (40
buses) is J&K SRTC's city fleet for the whole Union Territory (Srinagar and
Jammu), and it omits the SSCL e-buses and the private minibus permits that carry
most Srinagar trips — "Srinagar" is not named anywhere in the 164-page handbook.
Using it would both fabricate a Srinagar-specific number and contaminate the
benchmark with the very undercount the plan sets out to correct. It is kept as a
documented row in peer_cities.csv (use_in_fit=False) so the omission is visible.

The plan's own ratio is reported against three denominators, explicitly labelled:
  * TOTAL study-area population 6,584,762 (common.STUDY_AREA_POPULATION; WorldPop
    2026 in the 10-district union) — the comparable, whole-unit denominator.
  * SERVED population 2,317,958 — the engine's self-reported 400 m-walkshed
    coverage (engine v3.4.5-geo CLAUDE.md). NOT reproduced inside this repo; cited
    as an external engine figure and flagged as such.
  * SERVED population 1,592,847 — this repo's OWN reproducible coverage
    (a11_coverage_accessibility.json, network 400 m walkshed). Given so the
    served-denominator claim rests on an in-repo computation, not only the engine.

Outputs
    data/raw/peer_cities.csv                 (input; built once from cited sources)
    data/derived/a16_peer_regression.json    coefficients, R^2, intervals, placement
    paper/tables/table05j_peer_regression.{csv,md}          fitted models
    paper/tables/table05j_peer_cities.{csv,md}              the observation set
    paper/tables/table05j_peer_prediction.{csv,md}          Kashmir placement

Usage
    python analysis/a16_peer_regression.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a16")

# Kashmir served-population, engine self-report (engine v3.4.5-geo, CLAUDE.md
# "Network reaches 2,317,958 residents within 400m = 35.2%"). Not reproduced in
# this repo; the in-repo reproducible coverage (a11) is read at runtime as the
# preferred served figure and reported alongside it.
SERVED_POP_ENGINE = 2_317_958
SERVED_POP_ENGINE_CITE = ("engine v3.4.5-geo CLAUDE.md, 400 m-walkshed coverage "
                          "(35.2% of the 6.58M study area); not reproduced in-repo")

PEER_CITIES_CSV = C.RAW / "peer_cities.csv"


def division_density() -> tuple[float, float]:
    """Kashmir-Division area (km^2) and person-density from the OSM district union."""
    import geopandas as gpd
    d = gpd.read_file(C.DISTRICTS_GEOJSON).to_crs(C.UTM)
    area_km2 = float(d.geometry.union_all().area / 1e6)
    return area_km2, C.STUDY_AREA_POPULATION / area_km2


def served_pop_a11() -> float | None:
    """This repo's reproducible served population (network 400 m walkshed)."""
    p = C.DERIVED / "a11_coverage_accessibility.json"
    if not p.exists():
        return None
    import json
    d = json.loads(p.read_text(encoding="utf-8"))
    try:
        return float(d["any_service_reconciliation"]["any_service_population"])
    except (KeyError, TypeError):
        return None


def fit_ols(df: pd.DataFrame, cols: list[str], log_dv: bool = False):
    """OLS of buses_per_1000 (or its log10) on `cols`."""
    import statsmodels.api as sm
    y = df["buses_per_1000"].to_numpy()
    if log_dv:
        y = np.log10(y)
    X = sm.add_constant(df[cols], has_constant="add")
    return sm.OLS(y, X.to_numpy()).fit(), cols


def predict_at(res, cols: list[str], point: dict[str, float],
               log_dv: bool = False) -> dict:
    """
    Point estimate with 95% mean-CI and 95% observation-PI at one design row.

    With `log_dv`, the model was fitted on log10(buses per 1,000) and the interval
    is back-transformed. Because 10**x is monotonic the interval maps exactly, so
    the back-transformed PI is a valid 95% PI in level space — and, unlike the
    level-form model, it cannot contain a negative fleet. The back-transformed
    point estimate is the conditional MEDIAN, not the mean; it is labelled as such
    rather than silently presented as an expectation.
    """
    row = np.asarray([1.0] + [point[c] for c in cols], dtype=float).reshape(1, -1)
    sf = res.get_prediction(row).summary_frame(alpha=0.05).iloc[0]
    vals = dict(point=float(sf["mean"]),
                mean_ci=[float(sf["mean_ci_lower"]), float(sf["mean_ci_upper"])],
                pred_interval=[float(sf["obs_ci_lower"]), float(sf["obs_ci_upper"])])
    if not log_dv:
        return vals
    return dict(
        point=float(10 ** vals["point"]),
        point_is="conditional median (back-transformed from log10)",
        mean_ci=[float(10 ** v) for v in vals["mean_ci"]],
        pred_interval=[float(10 ** v) for v in vals["pred_interval"]],
    )


def diagnostics(res) -> dict:
    """
    Residual diagnostics that decide whether the level-form model is defensible.

    Jarque-Bera tests the normality the prediction interval assumes; Breusch-Pagan
    tests the constant variance it assumes. Both are reported for the level and
    log specifications so the choice between them rests on evidence.
    """
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.stattools import jarque_bera
    jb, jb_p, skew, kurt = jarque_bera(res.resid)
    _, bp_p, _, _ = het_breuschpagan(res.resid, res.model.exog)
    return dict(jarque_bera_p=float(jb_p), residual_skew=round(float(skew), 3),
                residual_kurtosis=round(float(kurt), 3),
                breusch_pagan_p=float(bp_p))


def placement(actual: float, pred: dict, peer_vals: np.ndarray) -> dict:
    """Where an actual ratio falls vs a prediction's PI and vs the peer spread."""
    lo, hi = pred["pred_interval"]
    if actual < lo:
        pos = "below_prediction_interval"
    elif actual > hi:
        pos = "above_prediction_interval"
    else:
        pos = "inside_prediction_interval"
    return dict(
        actual_buses_per_1000=round(actual, 4),
        predicted_buses_per_1000=round(pred["point"], 4),
        residual=round(actual - pred["point"], 4),
        position_vs_pred_interval=pos,
        peer_percentile=round(100.0 * float((peer_vals < actual).mean()), 1),
    )


def model_record(name: str, res, cols: list[str], dv: str) -> dict:
    """Serialise coefficients (named), fit stats, diagnostics and n for one model."""
    names = ["const"] + cols
    return dict(
        model=name, dependent_variable=dv,
        formula=f"{dv} ~ " + " + ".join(cols),
        n=int(res.nobs), r_squared=round(float(res.rsquared), 4),
        adj_r_squared=round(float(res.rsquared_adj), 4),
        f_pvalue=float(res.f_pvalue),
        coefficients={nm: dict(estimate=round(float(b), 6),
                               std_err=round(float(se), 6),
                               p_value=float(p))
                      for nm, b, se, p in zip(names, res.params, res.bse, res.pvalues)},
        residual_diagnostics=diagnostics(res),
    )


def main() -> None:
    if not PEER_CITIES_CSV.exists():
        C.write_result(dict(status="NOT_COMPUTABLE",
                            reason=f"missing input {PEER_CITIES_CSV}"),
                       "a16_peer_regression")
        raise SystemExit(f"missing {PEER_CITIES_CSV}")

    peers = pd.read_csv(PEER_CITIES_CSV)
    # every observation must be sourced — enforce, do not assume
    unsourced = peers[(peers["source"].fillna("").str.len() < 20)
                      | (peers["source_url"].fillna("").str.len() < 10)]
    if len(unsourced):
        raise SystemExit(f"{len(unsourced)} peer rows lack a source/url")

    peers["buses_per_1000"] = peers["buses"] / peers["population"] * 1000.0
    peers["density"] = peers["population"] / peers["area_km2"]
    peers["log10_pop"] = np.log10(peers["population"])

    fit = peers[peers["use_in_fit"]].reset_index(drop=True)
    excluded = peers[~peers["use_in_fit"]]
    log.info("peer cities: %d total, %d in fit, %d excluded (%s)",
             len(peers), len(fit), len(excluded),
             ", ".join(excluded["city"].tolist()) or "none")

    peer_vals = fit["buses_per_1000"].to_numpy()
    dmin, dmax = float(fit["density"].min()), float(fit["density"].max())
    pmin, pmax = float(fit["population"].min()), float(fit["population"].max())

    # Kashmir design point
    area_km2, kdens = division_density()
    kpop = float(C.STUDY_AREA_POPULATION)
    fleet = int(C.load_active()["Fleet_Required"].sum())
    served_a11 = served_pop_a11()
    log.info("Kashmir: pop %.0f, area %.1f km2, density %.1f /km2, planned fleet %d",
             kpop, area_km2, kdens, fleet)

    # ── models ────────────────────────────────────────────────────────────────
    # M1/M2 are the specification the analysis plan asks for: buses per 1,000 in
    # LEVELS. They are reported in full, but the dependent variable is strictly
    # positive and right-skewed (a 35-fold spread across the peer set), so a
    # normal-error model in levels puts mass below zero — the level-form intervals
    # below do have negative lower bounds, which is not a possible fleet. M3 fits
    # the same relationship on log10(buses per 1,000); it cannot predict a negative
    # fleet, and the diagnostics decide which specification to believe.
    res1, c1 = fit_ols(fit, ["log10_pop"])                       # population only
    res2, c2 = fit_ols(fit, ["log10_pop", "density"])            # plan's 2-predictor
    fit_nomulti = fit[~fit["multi_city_operator"]].reset_index(drop=True)
    res2b, _ = fit_ols(fit_nomulti, ["log10_pop", "density"])    # robustness
    res3, _ = fit_ols(fit, ["log10_pop"], log_dv=True)           # log DV, pop only
    res3d, _ = fit_ols(fit, ["log10_pop", "density"], log_dv=True)  # log DV, +density

    models = [
        model_record("M1_pop_only", res1, c1, "buses_per_1000"),
        model_record("M2_pop_density", res2, c2, "buses_per_1000"),
        model_record("M2b_pop_density_excl_multicity", res2b, c2, "buses_per_1000"),
        model_record("M3_log_pop_only", res3, c1, "log10(buses_per_1000)"),
        model_record("M3d_log_pop_density", res3d, c2, "log10(buses_per_1000)"),
    ]

    # ── predictions at Kashmir ──────────────────────────────────────────────────
    # Two-predictor model at the true division density — flagged extrapolation.
    p2_div = predict_at(res2, c2, dict(log10_pop=np.log10(kpop), density=kdens))
    # Population-only model, evaluated at each population denominator. 6.58M is
    # interior to the city population range; the served figures are treated as a
    # what-if "city of this many people", stated as such.
    p1_total = predict_at(res1, c1, dict(log10_pop=np.log10(kpop)))
    p1_serv_eng = predict_at(res1, c1, dict(log10_pop=np.log10(SERVED_POP_ENGINE)))
    p1_serv_a11 = (predict_at(res1, c1, dict(log10_pop=np.log10(served_a11)))
                   if served_a11 else None)
    # Preferred specification: log DV, back-transformed, strictly positive.
    p3_total = predict_at(res3, c1, dict(log10_pop=np.log10(kpop)), log_dv=True)
    p3_serv_eng = predict_at(res3, c1, dict(log10_pop=np.log10(SERVED_POP_ENGINE)),
                             log_dv=True)
    p3_serv_a11 = (predict_at(res3, c1, dict(log10_pop=np.log10(served_a11)),
                              log_dv=True) if served_a11 else None)

    actual = dict(
        total=fleet / kpop * 1000.0,
        served_engine=fleet / SERVED_POP_ENGINE * 1000.0,
        served_a11=(fleet / served_a11 * 1000.0) if served_a11 else None,
    )

    place = dict(
        total_vs_M1=placement(actual["total"], p1_total, peer_vals),
        total_vs_M2_extrapolated=placement(actual["total"], p2_div, peer_vals),
        total_vs_M3_preferred=placement(actual["total"], p3_total, peer_vals),
        served_engine_vs_M1=placement(actual["served_engine"], p1_serv_eng, peer_vals),
        served_engine_vs_M3_preferred=placement(actual["served_engine"], p3_serv_eng,
                                                peer_vals),
    )
    if served_a11 and p1_serv_a11:
        place["served_a11_vs_M1"] = placement(actual["served_a11"], p1_serv_a11, peer_vals)
        place["served_a11_vs_M3_preferred"] = placement(actual["served_a11"],
                                                        p3_serv_a11, peer_vals)

    # ── tables ──────────────────────────────────────────────────────────────────
    peers_out = peers[[
        "city", "state", "population", "population_basis", "population_year",
        "area_km2", "density", "buses", "buses_year", "buses_per_1000",
        "fleet_operator", "multi_city_operator", "use_in_fit", "notes",
    ]].copy()
    peers_out["density"] = peers_out["density"].round(1)
    peers_out["buses_per_1000"] = peers_out["buses_per_1000"].round(4)
    peers_out = peers_out.sort_values("buses", ascending=False)
    C.write_table(peers_out, "table05j_peer_cities",
                  "Indian peer cities: public-sector city bus fleet held "
                  "(ASRTU Fleet Handbook-2024, 31 Oct 2023) against 2011-Census "
                  "population; buses per 1,000. Srinagar shown but excluded from the fit.")

    mrows = []
    for m in models:
        d = m["residual_diagnostics"]
        r = dict(model=m["model"], dv=m["dependent_variable"], n=m["n"],
                 R2=m["r_squared"], adj_R2=m["adj_r_squared"],
                 F_pvalue=round(m["f_pvalue"], 6),
                 jarque_bera_p=round(d["jarque_bera_p"], 4),
                 breusch_pagan_p=round(d["breusch_pagan_p"], 4))
        for nm, cf in m["coefficients"].items():
            r[f"b_{nm}"] = cf["estimate"]
            r[f"p_{nm}"] = round(cf["p_value"], 6)
        mrows.append(r)
    C.write_table(pd.DataFrame(mrows), "table05j_peer_regression",
                  "OLS of buses per 1,000 on log10 population and density across "
                  "36 Indian peer cities. M2b drops 3 multi-city-operator rows; "
                  "M3 repeats the fit on log10(buses per 1,000) so the prediction "
                  "interval cannot contain a negative fleet.")

    pred_specs = [
        ("Kashmir Division (TOTAL pop)", int(kpop), "M1 (pop only, levels)",
         actual["total"], p1_total, "total_vs_M1"),
        ("Kashmir Division (TOTAL pop)", int(kpop),
         "M2 (pop+density, EXTRAPOLATED density)", actual["total"], p2_div,
         "total_vs_M2_extrapolated"),
        ("Kashmir Division (TOTAL pop)", int(kpop), "M3 (log DV, PREFERRED)",
         actual["total"], p3_total, "total_vs_M3_preferred"),
        ("Served (engine self-report)", SERVED_POP_ENGINE, "M1 (pop only, levels)",
         actual["served_engine"], p1_serv_eng, "served_engine_vs_M1"),
        ("Served (engine self-report)", SERVED_POP_ENGINE, "M3 (log DV, PREFERRED)",
         actual["served_engine"], p3_serv_eng, "served_engine_vs_M3_preferred"),
    ]
    if served_a11 and p1_serv_a11:
        pred_specs += [
            ("Served (a11 in-repo)", int(served_a11), "M1 (pop only, levels)",
             actual["served_a11"], p1_serv_a11, "served_a11_vs_M1"),
            ("Served (a11 in-repo)", int(served_a11), "M3 (log DV, PREFERRED)",
             actual["served_a11"], p3_serv_a11, "served_a11_vs_M3_preferred"),
        ]
    pred_rows = [
        dict(basis=basis, denominator_population=pop, model=mname,
             actual_bp1000=round(act, 4), predicted_bp1000=round(pr["point"], 4),
             pi_low=round(pr["pred_interval"][0], 4),
             pi_high=round(pr["pred_interval"][1], 4),
             pi_low_is_impossible=bool(pr["pred_interval"][0] < 0),
             position=place[key]["position_vs_pred_interval"],
             peer_pctile=place[key]["peer_percentile"])
        for basis, pop, mname, act, pr, key in pred_specs
    ]
    C.write_table(pd.DataFrame(pred_rows), "table05j_peer_prediction",
                  "Kashmir plan fleet placement against the peer regression, by "
                  "denominator and model. Density is extrapolated below the fitted "
                  "range, so the population-only models are the honest basis; the "
                  "level-form intervals (M1/M2) have negative lower bounds, which is "
                  "not a possible fleet, so M3 (log dependent variable) is preferred.")

    # ── JSON payload ────────────────────────────────────────────────────────────
    out = dict(
        status="OK",
        dependent_variable=dict(
            name="buses (public-sector city fleet held)",
            source="ASRTU (2024) SRTU Fleet Handbook-2024, 'City' column, as on 31 Oct 2023",
            source_url="https://www.asrtu.org/resource/front/uploads/STUs%20Fleet%20Book%202024.pdf",
            scope_caveats=[
                "fleet HELD, not buses on road (utilisation < 100%)",
                "includes wet-leased/hired buses",
                "public ASRTU-member undertakings only — excludes private stage/contract "
                "carriage and non-member Smart-City SPV e-buses",
            ],
            definition_mismatch_with_kashmir=(
                "peer = public STU fleet; Kashmir 1,011 = planned ALL-operator fleet "
                "(absorbs private minibus permits + SSCL/CHALO e-buses). The regression "
                "benchmarks public STU provision, not a like-for-like target."),
        ),
        predictors=dict(
            source="Census of India 2011, Table A-04(I) (Class-I towns), CLASS_I.xlsx",
            source_url="https://censusindia.gov.in/nada/index.php/catalog/42876",
            sha256="8ab1bafd6e49aec4a6b2709398dbdeaab2b53bc369a53e62eacac601647a58dd",
            population_basis="UA where a UA exists, else municipal corporation; area matched",
            denominator_year_gap_note=(
                "fleet 2023 vs population 2011 (2021 Census postponed) — peer ratios "
                "somewhat overstated and unevenly so; not projected forward"),
        ),
        peer_set=dict(
            n_total_rows=int(len(peers)),
            n_in_fit=int(len(fit)),
            excluded=[dict(city=r.city, reason="scope: UT-wide J&K SRTC city fleet, "
                           "excludes SSCL e-bus + private permits; not a Srinagar figure")
                      for r in excluded.itertuples()],
            n_multi_city_operator=int(fit["multi_city_operator"].sum()),
            buses_per_1000=dict(
                min=round(float(peer_vals.min()), 4),
                median=round(float(np.median(peer_vals)), 4),
                max=round(float(peer_vals.max()), 4)),
            population_range=[int(pmin), int(pmax)],
            density_range=[round(dmin, 1), round(dmax, 1)],
        ),
        kashmir=dict(
            planned_fleet=fleet,
            division_area_km2=round(area_km2, 1),
            division_density=round(kdens, 1),
            density_is_below_fitted_min=bool(kdens < dmin),
            population_denominators=dict(
                total=dict(value=int(kpop), buses_per_1000=round(actual["total"], 4),
                           note="common.STUDY_AREA_POPULATION; WorldPop 2026, 10-district union"),
                served_engine=dict(value=SERVED_POP_ENGINE,
                                   buses_per_1000=round(actual["served_engine"], 4),
                                   note=SERVED_POP_ENGINE_CITE),
                served_a11=(dict(value=int(served_a11),
                                 buses_per_1000=round(actual["served_a11"], 4),
                                 note="a11_coverage_accessibility.json, in-repo network 400 m walkshed")
                            if served_a11 else None),
            ),
        ),
        models=models,
        predictions=dict(
            M2_at_division_EXTRAPOLATED=dict(
                design=dict(log10_pop=round(np.log10(kpop), 4), density=round(kdens, 1)),
                warning="density below the fitted minimum — interval unreliable, reported for completeness",
                **p2_div),
            M1_at_total=dict(design=dict(population=int(kpop)), **p1_total),
            M1_at_served_engine=dict(design=dict(population=SERVED_POP_ENGINE), **p1_serv_eng),
            M1_at_served_a11=(dict(design=dict(population=int(served_a11)), **p1_serv_a11)
                              if p1_serv_a11 else None),
            M3_at_total=dict(design=dict(population=int(kpop)), **p3_total),
            M3_at_served_engine=dict(design=dict(population=SERVED_POP_ENGINE), **p3_serv_eng),
            M3_at_served_a11=(dict(design=dict(population=int(served_a11)), **p3_serv_a11)
                              if p3_serv_a11 else None),
        ),
        specification_note=dict(
            level_form_pi_lower_bound_negative=bool(
                min(p1_total["pred_interval"][0], p2_div["pred_interval"][0]) < 0),
            explanation=(
                "buses per 1,000 is strictly positive and right-skewed across the peer "
                "set (0.021 to 0.732, a 35-fold spread), so a normal-error OLS in levels "
                "assigns probability to a negative fleet: the M1/M2 95% prediction "
                "intervals do have negative lower bounds. They are reported because they "
                "are the specification the analysis plan names, but M3 — the same "
                "regressors on log10(buses per 1,000) — is preferred for the interval, "
                "since a monotone back-transform gives an exact and strictly positive "
                "95% prediction interval. M3's point estimate is a conditional median."),
        ),
        placement=place,
        headline=(
            f"Fit on {len(fit)} Indian peer cities (Srinagar excluded as a non-city "
            f"undercount). The relationship is weak: population-only R^2="
            f"{models[0]['r_squared']}, adding density R^2={models[1]['r_squared']} "
            f"(density p={models[1]['coefficients']['density']['p_value']:.2f}, i.e. it "
            f"adds nothing). The plan's {fleet} buses are {actual['total']:.3f}/1,000 on "
            f"the total population — the peer "
            f"{place['total_vs_M3_preferred']['peer_percentile']:.0f}th percentile and "
            f"{place['total_vs_M3_preferred']['position_vs_pred_interval'].replace('_',' ')} "
            f"of the preferred (M3) 95% interval — and {actual['served_engine']:.3f}/1,000 "
            f"on the served population. Kashmir's density {kdens:.0f}/km^2 is below every "
            f"fitted city, so the density term is extrapolation. Because R^2 is low the "
            f"interval is wide, and the honest reading is a plausibility band: the plan "
            f"is not an outlier against Indian public-sector fleet provision."),
        interpretation_caveats=[
            "Peer fleet is public-sector only; Kashmir fleet is planned all-operator — "
            "sitting above the public-STU expectation is partly this definitional gap.",
            "Kashmir Division is a mostly-rural region, not a city; its density is an "
            "extrapolation below the fitted range, so trust the population-only models.",
            "R^2 is low (0.10 in levels), so population and density explain little of the "
            "variation in Indian city fleet provision. The regression supports a wide "
            "plausibility band, NOT a point target — do not read the fitted value as a norm.",
            "The level-form (M1/M2) 95% intervals have negative lower bounds, which is not "
            "a possible fleet; M3's log specification is the interval to quote.",
            "buses-per-1,000 is capitalisation (fleet held), not delivered service; and the "
            "2011 population denominator predates the 2023 fleet by 12 years.",
            "The served-population predictions treat the covered population as a notional "
            "city of that size — a what-if, not a claim that the served area is a city.",
        ],
        citations=[
            "Association of State Road Transport Undertakings (2024). SRTU Fleet "
            "Handbook-2024: A Journey to Efficiency (Make-wise & Type-wise). New Delhi: ASRTU.",
            "Office of the Registrar General & Census Commissioner, India (2011). Census "
            "of India 2011, Table A-04(I): Towns and Urban Agglomerations Classified by "
            "Population Size Class. NADA catalogue 42876.",
            "Central Institute of Road Transport (2022). State Transport Undertakings — "
            "Profile & Performance 2021-22. Pune: CIRT (network-structure covariates).",
        ],
    )
    C.write_result(out, "a16_peer_regression")

    # ── console ─────────────────────────────────────────────────────────────────
    for m in models:
        b = m["coefficients"]
        log.info("%-32s n=%d R2=%.3f  %s", m["model"], m["n"], m["r_squared"],
                 "  ".join(f"{k}={v['estimate']:+.4g}(p={v['p_value']:.3f})"
                          for k, v in b.items()))
    log.info("peer buses/1000: min %.3f  median %.3f  max %.3f  (density range %.0f-%.0f /km2)",
             peer_vals.min(), np.median(peer_vals), peer_vals.max(), dmin, dmax)
    log.info("Kashmir density %.0f /km2 is %s the fitted minimum %.0f",
             kdens, "BELOW" if kdens < dmin else "within", dmin)
    for k, pl in place.items():
        log.info("  %-28s actual %.3f/1000  pred %.3f  -> %s  (peer %.0fth pctile)",
                 k, pl["actual_buses_per_1000"], pl["predicted_buses_per_1000"],
                 pl["position_vs_pred_interval"], pl["peer_percentile"])


if __name__ == "__main__":
    main()
