"""
Shared configuration, paths and I/O for the paper analysis suite.

Every analysis module imports from here so that parameter values, CRS choices
and file locations exist in exactly one place. Nothing in this module reads the
network; all inputs are frozen files under data/raw and data/cache.

Study area: Kashmir Division, Jammu & Kashmir, India — 10 districts.
Engine build under analysis: v3.4.5-geo.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CACHE = DATA / "cache"
DERIVED = DATA / "derived"
PAPER = ROOT / "paper"
FIGURES = PAPER / "figures"
TABLES = PAPER / "tables"

for _d in (DERIVED, FIGURES, TABLES, CACHE):
    _d.mkdir(parents=True, exist_ok=True)

# ── frozen input files ───────────────────────────────────────────────────────
PLAN_CSV = RAW / "Rationalised_Routes_Kashmir_v3.csv"
PLAN_GEOJSON = RAW / "Rationalised_Routes_Kashmir_v3.geojson"
PERMITS_CSV = RAW / "existing-routes.csv"
POIS_CSV = RAW / "pois.csv"
WORLDPOP_TIF = RAW / "kashmir_worldpop.tif"
DISTRICTS_GEOJSON = RAW / "kashmir_districts_osm.geojson"
TEHSILS_GEOJSON = RAW / "kashmir_tehsils_osm.geojson"
STOPS_MASTER = RAW / "Kashmir_Stops_Master_v4.csv"
HOURLY_PAX_CSV = RAW / "Hourly_Passenger_Count.csv"
CHALO_RIDERSHIP_CSV = RAW / "chalo_ridership.csv"
CHALO_DEPLOYED_CSV = RAW / "chalo_deployed_buses.csv"
WALK_GRAPH_PKL = CACHE / "walk_graph.gpickle"
OSRM_CACHE_JSON = CACHE / "osrm_responses.json"

# GPS ground truth (mined from the Bus Sathi app; see data/raw/gps/PROVENANCE.md)
GPS_REALITY_CSV = RAW / "gps" / "reality_check.csv"
GPS_CORRIDOR_PROFILES_CSV = RAW / "gps" / "corridor_profiles.csv"
GPS_ROUTE_EVIDENCE_CSV = RAW / "gps" / "route_evidence.csv"
GPS_PERMIT_OBSERVED_CSV = RAW / "gps" / "permit_observed.csv"

# ── coordinate reference systems ─────────────────────────────────────────────
WGS84 = "EPSG:4326"
UTM = "EPSG:32643"          # UTM zone 43N — Kashmir Valley; metric, for buffers/length

# ── engine parameters under test ─────────────────────────────────────────────
# Values mirror transit_kashmir_v3.py v3.4.5. `RANGE` is the interval swept in
# the one-at-a-time sensitivity analysis (§4.10) and sampled in the Monte Carlo.
# `dist` is the Monte Carlo marginal: "unif" over RANGE, or "tri" triangular
# with the engine value as mode.
#
# Two traps in reading the engine's constants, both resolved in favour of the
# code that actually executes:
#   * STOP_PENALTY_MIN is 0.5 min in the engine source (line 155); the docstring
#     of its own consumer (line 2110) says 1.5. The executed value is 0.5. The
#     range is widened upward to 1.5 because v04 measures a median observed dwell
#     of ~0.87 min per implied stop, so the engine value sits near the bottom of
#     the credible interval rather than at its centre.
#   * VIRTUAL_STOP_SPACING_M (250 m) samples the alignment for catchments;
#     STOP_SPACING_M (500 m) is the separate assumption converting length into a
#     stop count for dwell. They drive different mechanisms and are swept apart.
PARAMETERS: dict[str, dict[str, Any]] = {
    "WALK_CATCHMENT_M":        dict(value=400.0, range=(300.0, 800.0),  dist="tri",
                                    label="Walk catchment radius (m)"),
    "VIRTUAL_STOP_SPACING_M":  dict(value=250.0, range=(150.0, 400.0),  dist="unif",
                                    label="Catchment sampling interval (m)"),
    "STOP_SPACING_M":          dict(value=500.0, range=(300.0, 800.0),  dist="unif",
                                    label="Assumed stop spacing for dwell (m)"),
    "CDI_POP_WEIGHT":          dict(value=0.50,  range=(0.20, 0.80),    dist="unif",
                                    label="Composite weight on population"),
    "POI_TIER2_WEIGHT":        dict(value=0.40,  range=(0.20, 0.60),    dist="tri",
                                    label="Tier-2 opportunity weight"),
    "POI_TIER3_WEIGHT":        dict(value=0.60,  range=(0.30, 0.90),    dist="tri",
                                    label="Tier-3 (seasonal) opportunity weight"),
    "TOURIST_POPULATION_MULTIPLIER": dict(value=1.30, range=(1.00, 1.80), dist="tri",
                                    label="Tourist-corridor catchment boost"),
    "OVERLAP_THRESHOLD":       dict(value=0.65,  range=(0.50, 0.90),    dist="unif",
                                    label="Corridor consolidation threshold θ"),
    "CONGESTION_CITY_CORE":    dict(value=2.20,  range=(1.60, 2.80),    dist="tri",
                                    label="City-core congestion multiplier"),
    "STOP_PENALTY_MIN":        dict(value=0.50,  range=(0.30, 1.50),    dist="tri",
                                    label="Dwell penalty per stop (min)"),
    "FLEET_SPARE_RATIO":       dict(value=1.15,  range=(1.05, 1.25),    dist="tri",
                                    label="Fleet spare ratio"),
}

# Headway policy (v3.4.5). City bands are policy constants; rural bands are
# demand-responsive buckets with a hard 50-minute maximum wait.
HEADWAY_SSCL_TRUNK_MIN = 15
HEADWAY_HP_MIN = 20
HEADWAY_MP_MIN = 35
HEADWAY_LP_MIN = 35
HEADWAY_MAX_MIN = 35                       # urban/peri-urban ceiling
REGIONAL_HEADWAY_BUCKETS = (35, 40, 45, 50)  # rural lifelines

TERMINAL_LAYOVER_FACTOR = 1.10
STOP_SPACING_M = 500.0
MIN_FLEET_URBAN = 2
MIN_FLEET_REGIONAL = 1

# Vehicle capacities (seated + standing, design load) used for offered capacity.
VEHICLE_CAPACITY = {"HPV": 60, "MPV": 35, "LPV": 20}

# Study-area denominator: population inside the 10-district union, WorldPop
# 2026 UN-adjusted, established by point-in-polygon in engine v3.4.1.
STUDY_AREA_POPULATION = 6_584_762

DISTRICTS = ["Anantnag", "Bandipore", "Baramulla", "Budgam", "Ganderbal",
             "Kulgam", "Kupwara", "Pulwama", "Shopian", "Srinagar"]

ACTIVE_ACTIONS = ("UPGRADED_TO_TRUNK", "RETAINED_AS_FEEDER")
MERGED_ACTION = "MERGED_INTO_TRUNK"

RANDOM_SEED = 20260823


# ── logging ──────────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)-7s %(name)s │ %(message)s",   # no wall-clock time: logs are tracked and must be deterministic
    )
    return logging.getLogger(name)


# ── loaders ──────────────────────────────────────────────────────────────────
def load_plan() -> pd.DataFrame:
    """Full engine output: all 644 permit-routes, active and merged."""
    return pd.read_csv(PLAN_CSV)


def load_active() -> pd.DataFrame:
    """The 186 routes that carry service in the rationalised plan."""
    df = load_plan()
    return df[df["Action_Taken"].isin(ACTIVE_ACTIONS)].reset_index(drop=True)


def load_active_geo():
    """Active routes with routed geometry (186 features)."""
    import geopandas as gpd
    return gpd.read_file(PLAN_GEOJSON)


def load_districts():
    import geopandas as gpd
    return gpd.read_file(DISTRICTS_GEOJSON)


def study_area_union():
    """Dissolved 10-district polygon in WGS84."""
    return load_districts().geometry.union_all()


# ── result emission ──────────────────────────────────────────────────────────
def write_table(df: pd.DataFrame, stem: str, caption: str = "",
                index: bool = False) -> Path:
    """Emit a result table as CSV (machine) plus Markdown (manuscript paste)."""
    csv_path = TABLES / f"{stem}.csv"
    df.to_csv(csv_path, index=index)
    md_path = TABLES / f"{stem}.md"
    with md_path.open("w", encoding="utf-8") as fh:
        if caption:
            fh.write(f"**{caption}**\n\n")
        md_df = df.astype(object).where(df.notna(), None) if df.isna().any().any() else df
        fh.write(md_df.to_markdown(index=index, missingval=""))   # missing values print blank, never "nan"
        fh.write("\n")
    return csv_path


def write_result(payload: dict, stem: str) -> Path:
    """Persist scalar findings as JSON so figures and prose read one source."""
    path = DERIVED / f"{stem}.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(_jsonable(payload), fh, indent=2, sort_keys=True)
    return path


def read_result(stem: str) -> dict:
    with (DERIVED / f"{stem}.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return _jsonable(obj.tolist())
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj


# ── small statistics helpers used in more than one module ────────────────────
def gini(x: np.ndarray, weights: np.ndarray | None = None) -> float:
    """
    Gini coefficient of a non-negative distribution.

    Used for the accessibility Gini (§5.10), where `x` is per-person
    accessibility and `weights` is population per unit, so the coefficient is
    population-weighted rather than unit-weighted.
    """
    x = np.asarray(x, dtype=float)
    if weights is None:
        weights = np.ones_like(x)
    weights = np.asarray(weights, dtype=float)
    keep = np.isfinite(x) & np.isfinite(weights) & (weights > 0)
    x, weights = x[keep], weights[keep]
    if x.size == 0 or x.sum() <= 0:
        return float("nan")
    order = np.argsort(x)
    x, weights = x[order], weights[order]
    cw = np.cumsum(weights)
    cxw = np.cumsum(x * weights)
    total_w, total_xw = cw[-1], cxw[-1]
    # Trapezoidal Lorenz-curve integration. The curve starts at the origin
    # (0, 0): without that point the first segment (area 0.5 * pop[0] * lorenz[0])
    # is dropped and the Gini is biased upward (gini([1, 1]) came out 0.25, not 0;
    # audit F-03-01). For unweighted x this is exactly the mean-absolute-
    # difference Gini sum_ij |x_i - x_j| / (2 n^2 mean(x)).
    lorenz = np.r_[0.0, cxw / total_xw]
    pop = np.r_[0.0, cw / total_w]
    area = np.trapezoid(lorenz, pop) if hasattr(np, "trapezoid") else np.trapz(lorenz, pop)
    return float(1.0 - 2.0 * area)


def entropy_weights(matrix: np.ndarray) -> np.ndarray:
    """
    Shannon-entropy objective weighting (Zhou, Ang & Poh 2006).

    Each column of `matrix` is a min-max normalised criterion over the same
    units. A criterion whose values are near-uniform carries little
    information and receives a small weight. Returns weights summing to 1.
    """
    m = np.asarray(matrix, dtype=float)
    m = np.where(np.isfinite(m), m, 0.0)
    col_sums = m.sum(axis=0)
    col_sums[col_sums == 0] = 1.0
    p = m / col_sums
    with np.errstate(divide="ignore", invalid="ignore"):
        logp = np.where(p > 0, np.log(p), 0.0)
    n = m.shape[0]
    e = -(p * logp).sum(axis=0) / np.log(n)
    d = 1.0 - e                       # degree of diversification
    if d.sum() <= 0:
        return np.full(m.shape[1], 1.0 / m.shape[1])
    return d / d.sum()


def minmax(s: pd.Series | np.ndarray) -> np.ndarray:
    v = np.asarray(s, dtype=float)
    lo, hi = np.nanmin(v), np.nanmax(v)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return np.zeros_like(v)
    return (v - lo) / (hi - lo)


def goodness_of_variance_fit(values: np.ndarray, breaks: list[float]) -> float:
    """
    GVF = 1 − SDCM/SDAM, the standard fit statistic for a class interval scheme.

    SDAM is squared deviation from the array mean; SDCM is the sum over classes
    of squared deviation from each class mean. Reported for k = 2..7 in §4.7 so
    the choice of three tiers rests on an elbow rather than an assertion.
    """
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    sdam = float(((v - v.mean()) ** 2).sum())
    if sdam == 0:
        return float("nan")
    sdcm = 0.0
    edges = list(breaks)
    for lo, hi in zip(edges[:-1], edges[1:]):
        if hi == edges[-1]:
            cls = v[(v >= lo) & (v <= hi)]
        else:
            cls = v[(v >= lo) & (v < hi)]
        if cls.size:
            sdcm += float(((cls - cls.mean()) ** 2).sum())
    return 1.0 - sdcm / sdam
