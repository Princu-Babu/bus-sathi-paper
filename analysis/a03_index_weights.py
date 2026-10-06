#!/usr/bin/env python
"""
a03_index_weights.py — derive the composite demand index under alternative
weightings, and test whether the planning decision survives the choice.

HOW MANY WEIGHTINGS ARE THERE? Two, not three. Three schemes are computed (equal,
Shannon entropy, first principal component) but with exactly TWO criteria the
first principal component of the correlation matrix [[1, r], [r, 1]] is
(1, 1)/sqrt(2) for every r > 0, so PCA weights are 0.5/0.5 — identical to equal
weights BY CONSTRUCTION, not by finding. PCA is therefore reported only as a
check; the number of genuinely distinct weightings (`n_distinct_weightings` in
the JSON) is computed from the weight vectors rather than asserted, and every
pair that coincides is listed in `identical_by_construction`. The only
data-driven, non-trivial alternative is entropy; a direct sweep of the
population weight from 0.1 to 0.9 is added as the genuine robustness evidence.

The objection this module exists to answer. A referee's summary rejection of a
supply-side plan reads: "the paper does not establish that their composite index
bears any relationship to travel demand, and therefore does not establish that
the resulting network is better than the one it replaces." Part of the answer is
external validation (v01, v04). The other part is here: showing that the index is
not a knob, i.e. that the weights are derived rather than asserted, and that the
decision the index drives is insensitive to which derivation is used.

What the plan does. The engine sets

    Pop_Score = minmax( clip( P_i / L_i , P95 ) )          population density
    POI_Score = minmax( sum_j w(tier_j) [d_ij <= 250 m] / L_i )   opportunity density
    CDI_i     = 0.50 * Pop_Score_i + 0.50 * POI_Score_i

with tier weights 1.0 / 0.4 / 0.6 for high / medium / seasonal opportunities,
L_i the route length, and the 95th-percentile cap on population density
preventing one dense corridor from compressing every other score. The 0.50/0.50
split is asserted, and is the single most exposed assumption in the method.

What is done here.
  1. Both index inputs are recomputed on the pedestrian network rather than
     straight-line, using a02's graph. For population that means a02's network
     catchment. For opportunities it means an exact network test: an opportunity
     counts for a route when its own walking distance to the nearest virtual stop
     is within the 250 m budget, offset from the network included. No Euclidean
     tail is needed for point opportunities, so this measure is exact rather than
     an upper bound.
  2. Three weighting schemes are computed: equal (the plan's assertion), Shannon
     entropy (Zhou, Ang & Poh 2006 — weight rises with the information content
     of a criterion across alternatives) and the first principal component (a
     check that equals the equal weights here by construction — see above).
     Analytic hierarchy process weights are NOT derived: no expert panel was
     convened for this study, and inventing pairwise comparisons would be
     fabrication. That absence is stated in the paper rather than papered over.
  3. Redundancy between the two channels is measured. If population and
     opportunity density are near-collinear the weighting cannot matter much,
     which is a robustness result and must be reported as such rather than
     presented as a validated weighting. The paper (§4.5) declares a rule — if
     rho(Pop, POI) > 0.85 the composite adds little beyond the first principal
     component and a PCA reduction is substituted. The statistic, the declared
     threshold (an assumption: no source is cited for 0.85) and the rule's
     outcome AS WRITTEN are all recorded in `collinearity_rule` in the JSON,
     including the case where the rule fires and the substitution changes
     nothing because PCA equals equal weights.
  4. Decision stability. The policy-relevant output is not the index value but
     the decision it drives: whether a route clears the trunk-eligibility gate at
     the 30th percentile of the CDI, and which of three Jenks bands it lands in.
     Agreement is reported as the share of routes unchanged and as Cohen's kappa,
     across weightings and across the Euclidean/network switch.

Outputs
    data/derived/a03_index.csv               per-route scores under every variant
    data/derived/a03_index_weights.json      weights, correlations, stability
    paper/tables/table04a_index_weights.{csv,md}
    paper/tables/table04b_decision_stability.{csv,md}
    paper/tables/table04c_weight_sweep.{csv,md}

All statistics are in-sample over the n = 186 active plan routes; none is
out-of-sample.

Usage
    python analysis/a03_index_weights.py                  # reuse cached POI incidence
    python analysis/a03_index_weights.py --recompute-poi  # rebuild it (slow: network Dijkstra)

The per-route opportunity incidence (poi_w_*, n_poi_*) is the only slow step. It
is deterministic, so when data/derived/a03_index.csv already holds it for exactly
the same routes it is re-read rather than recomputed; the weighting analysis
below it always runs afresh. `--recompute-poi` forces the full rebuild.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402
from a02_network_catchments import (  # noqa: E402
    MAX_SNAP_M, SIMPLIFY_TOL_M, dijkstra_budget, load_graph, stops_along,
)

log = C.get_logger("a03")

POI_BUDGET_M = 250.0          # engine POI_BUFFER_M
POP_CAP_PERCENTILE = 95       # engine POP_CAP_PERCENTILE (Directive 5)
TRUNK_GATE_PERCENTILE = 30    # engine TRUNK_CDI_GATE_PERCENTILE
N_BANDS = 3
COLLINEARITY_THRESHOLD = 0.85  # paper §4.5 rule: rho(Pop, POI) above this -> PCA reduction
TIER_WEIGHT = {"high": 1.0, "medium": 0.4, "seasonal": 0.6}


# ── index construction, following the engine exactly ──────────────────────────
def pop_score(pop: pd.Series, km: pd.Series) -> pd.Series:
    """Engine step1: length-normalised density, 95th-percentile cap, min-max."""
    raw = (pop / km.clip(lower=1e-6)).clip(lower=0)
    capped = raw.clip(upper=float(np.percentile(raw, POP_CAP_PERCENTILE)))
    return C.minmax(capped)


def poi_score(weight_sum: pd.Series, km: pd.Series) -> pd.Series:
    """Engine step2: length-normalised weighted opportunity gravity, min-max."""
    return C.minmax((weight_sum / km.clip(lower=1e-6)).clip(lower=0))


def pca_weights(matrix: np.ndarray) -> np.ndarray:
    """
    First-principal-component weights on the standardised criteria.

    The loadings are taken in absolute value and normalised to sum to one. With
    two positively correlated criteria the first component loads on both, so this
    tends towards equal weighting — which is informative, not a failure.
    """
    x = matrix - matrix.mean(axis=0)
    sd = x.std(axis=0, ddof=1)
    sd[sd == 0] = 1.0
    z = x / sd
    _, _, vt = np.linalg.svd(z, full_matrices=False)
    load = np.abs(vt[0])
    return load / load.sum()


def jenks_bands(values: np.ndarray, k: int = N_BANDS) -> np.ndarray:
    """Jenks natural-breaks band index (0 = lowest) for each value."""
    import jenkspy
    v = np.asarray(values, dtype=float)
    if len(np.unique(v)) <= k:
        return np.searchsorted(np.unique(v), v)
    breaks = np.asarray(jenkspy.jenks_breaks(v, n_classes=k), dtype=float)
    inner = breaks[1:-1]
    # side="left": jenkspy breaks are UPPER bounds of the class below (a04 convention, D19)
    return np.searchsorted(inner, v, side="left")


def cohen_kappa(a, b) -> float:
    """Cohen's kappa for two labellings of the same items."""
    a, b = np.asarray(a), np.asarray(b)
    labels = np.union1d(np.unique(a), np.unique(b))
    n = len(a)
    obs = float((a == b).mean())
    exp = sum(((a == l).mean() * (b == l).mean()) for l in labels)
    return (obs - exp) / (1 - exp) if exp < 1 else 1.0


# ── opportunity accessibility ─────────────────────────────────────────────────
def poi_tier_weights(pois: pd.DataFrame) -> pd.Series:
    """
    Tier weight per opportunity.

    The staged POI file carries the engine's own three-level `importance`
    (high/medium/seasonal), which is the tier already resolved. Unrecognised
    values fall back to the engine's medium default of 0.4 rather than being
    dropped, so no opportunity silently disappears from the index.
    """
    w = pois["importance"].map(TIER_WEIGHT)
    n_default = int(w.isna().sum())
    if n_default:
        log.warning("  %d POIs with unrecognised importance -> default 0.4", n_default)
    return w.fillna(TIER_WEIGHT["medium"])


POI_INCIDENCE_COLS = ["New_Route_ID", "poi_w_euclid", "n_poi_euclid",
                      "poi_w_net", "n_poi_net"]


def cached_poi_incidence(catch: pd.DataFrame) -> pd.DataFrame | None:
    """
    Per-route opportunity incidence from a previous run of this module, or None.

    Reused only when the cached file covers exactly the same route ids as the
    catchment table, so a stale cache for a different route set is never used.
    """
    path = C.DERIVED / "a03_index.csv"
    if not path.exists():
        return None
    # round_trip: pandas' default float parser is inexact in the last bit, which
    # would make a cached re-read differ from the freshly computed values.
    prev = pd.read_csv(path, float_precision="round_trip")
    if any(c not in prev.columns for c in POI_INCIDENCE_COLS):
        return None
    if set(prev["New_Route_ID"]) != set(catch["New_Route_ID"]):
        return None
    return prev[POI_INCIDENCE_COLS].copy()


def compute_poi_incidence() -> pd.DataFrame:
    """The slow step: Euclidean and exact network opportunity incidence per route."""
    import geopandas as gpd
    from scipy.spatial import cKDTree

    routes = gpd.read_file(C.PLAN_GEOJSON).to_crs(C.UTM)
    routes["geometry"] = routes.geometry.simplify(SIMPLIFY_TOL_M)
    log.info("routes %d", len(routes))

    pois = pd.read_csv(C.POIS_CSV)
    pw = poi_tier_weights(pois).to_numpy()
    poi_utm = gpd.GeoDataFrame(
        pois, geometry=gpd.points_from_xy(pois["lon"], pois["lat"]),
        crs=C.WGS84).to_crs(C.UTM)
    poi_xy = np.column_stack([poi_utm.geometry.x, poi_utm.geometry.y])
    log.info("opportunities %d, tier weights %s", len(pois),
             {k: int((pois['importance'] == k).sum()) for k in TIER_WEIGHT})

    xy, indptr, indices, weights = load_graph()
    tree = cKDTree(xy)
    # Snap every opportunity once: its own walk to the network is part of its
    # access cost, so it is added to the network distance rather than ignored.
    poi_off, poi_node = tree.query(poi_xy, k=1)

    rows = []
    t0 = time.time()
    for pos, (_, r) in enumerate(routes.iterrows(), start=1):
        stops = stops_along(r.geometry)
        line = r.geometry

        # Euclidean opportunity gravity, as the engine computes it.
        eu_mask = np.array([line.distance(p) <= POI_BUDGET_M
                            for p in poi_utm.geometry.values])

        # Network opportunity gravity: offset + network distance within budget.
        pts = np.array([[p.x, p.y] for p in stops])
        off, nidx = tree.query(pts, k=1)
        sources: dict[int, float] = {}
        for o, ni in zip(off, nidx):
            if o > MAX_SNAP_M:
                continue
            ni = int(ni)
            if o < sources.get(ni, np.inf):
                sources[ni] = float(o)
        nodes, ds = dijkstra_budget(indptr, indices, weights, sources, POI_BUDGET_M)
        dmap = dict(zip(nodes.tolist(), ds.tolist()))
        net_mask = np.array([
            (poi_off[j] + dmap.get(int(poi_node[j]), np.inf)) <= POI_BUDGET_M
            for j in range(len(pois))])

        rows.append(dict(
            New_Route_ID=r["New_Route_ID"], Route_Name=r.get("Route_Name"),
            Route_Type=r.get("Route_Type"), Route_KM=float(r["Route_KM"]),
            poi_w_euclid=float(pw[eu_mask].sum()), n_poi_euclid=int(eu_mask.sum()),
            poi_w_net=float(pw[net_mask].sum()), n_poi_net=int(net_mask.sum()),
        ))
        if pos % 25 == 0 or pos == len(routes):
            log.info("  %d/%d routes", pos, len(routes))

    return pd.DataFrame(rows)[POI_INCIDENCE_COLS]


def distinct_weightings(schemes: dict[str, np.ndarray], tol: float = 1e-6) -> dict:
    """
    How many of the named weighting schemes are genuinely different vectors?

    Computed from the weight vectors, not asserted. Two schemes are the same
    weighting when every component agrees within `tol`. Returns the number of
    distinct vectors, the groups of coincident schemes and, for each coincident
    pair, whether the coincidence is an identity of the method (PCA on exactly
    two positively correlated criteria is (1,1)/sqrt(2) whatever the
    correlation, so it must equal equal weights) rather than a finding.
    """
    names = list(schemes)
    groups: list[list[str]] = []
    for nm in names:
        for g in groups:
            if np.allclose(schemes[nm], schemes[g[0]], atol=tol, rtol=0):
                g.append(nm)
                break
        else:
            groups.append([nm])
    n_criteria = len(next(iter(schemes.values())))
    pairs = []
    for g in groups:
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                pair = sorted([g[i], g[j]])
                by_construction = (pair == ["equal", "pca"] and n_criteria == 2)
                pairs.append(dict(
                    schemes=pair,
                    identical_by_construction=bool(by_construction),
                    reason=("PCA on two positively correlated criteria loads "
                            "(1,1)/sqrt(2) for every correlation r > 0, so its "
                            "normalised weights are exactly 0.5/0.5 — an identity "
                            "of the method, not an empirical agreement"
                            if by_construction else
                            "coincident numerically; not shown to be an identity")))
    return dict(n_schemes_computed=len(names), n_distinct_weightings=len(groups),
                groups=groups, identical_pairs=pairs)


def collinearity_rule_record(pearson_r: float, spearman_rho: float,
                             w_pca: np.ndarray, w_equal: np.ndarray) -> dict:
    """
    The paper's declared collinearity rule, its statistic and its outcome as written.

    Declared rule (paper §4.5): if rho(Pop, POI) > 0.85, the composite adds little
    beyond the first principal component and a PCA reduction is substituted. The
    paper does not say which correlation coefficient, so both are evaluated and
    the rule is recorded as fired if EITHER exceeds the threshold. The threshold
    0.85 carries no citation here: it is an assumption.
    """
    thr = COLLINEARITY_THRESHOLD
    fired_p, fired_s = bool(pearson_r > thr), bool(spearman_rho > thr)
    fired = fired_p or fired_s
    pca_same = bool(np.allclose(w_pca, w_equal, atol=1e-6, rtol=0))
    if fired:
        outcome = ("rule fired: the declared action is to substitute the PCA "
                   "reduction for the 50/50 composite; here the PCA weights equal "
                   "the equal weights, so the substitution changes nothing")
        if not pca_same:
            outcome = ("rule fired: the declared action is to substitute the PCA "
                       "reduction; PCA weights differ from equal weights here, so "
                       "the substitution WOULD change the composite")
    else:
        outcome = "rule did not fire; the 50/50 composite is kept"
    return dict(
        declared_rule="if rho(Pop, POI) > threshold, substitute the first-principal-"
                      "component reduction for the composite",
        threshold=thr,
        threshold_source="assumption (declared in paper §4.5; no citation)",
        pearson_r=float(pearson_r), spearman_rho=float(spearman_rho),
        pearson_r_squared=float(pearson_r ** 2),
        pearson_exceeds_threshold=fired_p, spearman_exceeds_threshold=fired_s,
        rule_fired=fired,
        pca_weights_equal_equal_weights=pca_same,
        outcome_as_written=outcome,
        interpretation=("the two criteria share about "
                        f"{100 * pearson_r ** 2:.0f}% of their variance (Pearson r^2), "
                        "so the composite is close to one-dimensional; the 50/50 "
                        "asymmetry argument cannot be read as two independent "
                        "channels"),
    )


def weight_sweep(P: np.ndarray, Q: np.ndarray, base_cdi: np.ndarray,
                 base_gate: np.ndarray, base_band: np.ndarray) -> list[dict]:
    """
    Direct sweep of the population weight, w_pop from 0.1 to 0.9, w_poi = 1 - w_pop.

    This, not PCA, is the genuine weighting-robustness evidence: it moves the
    weight over most of its feasible range and reports how many routes change
    gate status or Jenks band relative to the plan's 0.5/0.5.
    """
    from scipy.stats import spearmanr
    out = []
    for wp in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        cdi = wp * P + (1 - wp) * Q
        gate = (cdi >= np.percentile(cdi, TRUNK_GATE_PERCENTILE)).astype(int)
        band = jenks_bands(cdi)
        out.append(dict(
            w_population=wp, w_opportunity=round(1 - wp, 1),
            gate_agreement_with_equal=float((gate == base_gate).mean()),
            gate_kappa=cohen_kappa(base_gate, gate),
            band_agreement_with_equal=float((band == base_band).mean()),
            band_kappa=cohen_kappa(base_band, band),
            n_routes_changing_band=int((band != base_band).sum()),
            spearman_cdi_with_equal=float(spearmanr(base_cdi, cdi)[0]),
        ))
    return out


def main(recompute_poi: bool = False) -> None:
    from scipy.stats import pearsonr, spearmanr

    catch = pd.read_csv(C.DERIVED / "a02_catchments.csv")
    poi_df = None if recompute_poi else cached_poi_incidence(catch)
    poi_source = "cached_from_a03_index_csv"
    if poi_df is None:
        poi_df = compute_poi_incidence()
        poi_source = "recomputed"
    log.info("catchment rows %d; opportunity incidence %s", len(catch), poi_source)

    df = catch.merge(poi_df, on="New_Route_ID", how="inner")
    if len(df) != len(catch) or len(poi_df) != len(catch):
        raise SystemExit(f"join lost rows: {len(df)} of {len(catch)}")

    # Two variants of each channel: as-published (Euclidean) and corrected
    # (network). Route length is the plan's own Route_KM in both, so the only
    # thing that changes is how accessibility is measured.
    km = df["Route_KM"]
    df["pop_score_euclid"] = pop_score(df["pop_euclid"], km)
    df["pop_score_net"] = pop_score(df["pop_net"], km)
    df["poi_score_euclid"] = poi_score(df["poi_w_euclid"], km)
    df["poi_score_net"] = poi_score(df["poi_w_net"], km)

    results, stability_rows, weight_rows = {}, [], []
    for variant in ("euclid", "net"):
        P = df[f"pop_score_{variant}"].to_numpy()
        Q = df[f"poi_score_{variant}"].to_numpy()
        M = np.column_stack([P, Q])

        w_equal = np.array([0.5, 0.5])
        w_entropy = C.entropy_weights(M)
        w_pca = pca_weights(M)
        schemes = dict(equal=w_equal, entropy=w_entropy, pca=w_pca)

        pr, pp = pearsonr(P, Q)
        sr, sp = spearmanr(P, Q)
        dw = distinct_weightings(schemes)
        results[variant] = dict(
            pearson_r=float(pr), pearson_p=float(pp),
            spearman_rho=float(sr), spearman_p=float(sp),
            weights={k: [float(x) for x in v] for k, v in schemes.items()},
            distinct_weightings=dw,
            collinearity_rule=collinearity_rule_record(pr, sr, w_pca, w_equal),
        )
        for name, w in schemes.items():
            cdi = M @ w
            df[f"cdi_{variant}_{name}"] = cdi
            gate = float(np.percentile(cdi, TRUNK_GATE_PERCENTILE))
            df[f"gate_{variant}_{name}"] = (cdi >= gate).astype(int)
            df[f"band_{variant}_{name}"] = jenks_bands(cdi)
            weight_rows.append(dict(variant=variant, scheme=name,
                                    w_population=round(float(w[0]), 4),
                                    w_opportunity=round(float(w[1]), 4),
                                    cdi_gate_30th=round(gate, 4),
                                    cdi_mean=round(float(cdi.mean()), 4),
                                    identical_to_equal_by_construction=(
                                        "yes (2 criteria)" if name == "pca" else "")))

        # Stability of the decision across weightings, within this variant.
        for other in ("entropy", "pca"):
            stability_rows.append(dict(
                note=("identity, not a result: PCA on two criteria = equal weights"
                      if other == "pca" else ""),
                comparison=f"{variant}: equal vs {other}",
                gate_agreement=float((df[f"gate_{variant}_equal"]
                                      == df[f"gate_{variant}_{other}"]).mean()),
                gate_kappa=cohen_kappa(df[f"gate_{variant}_equal"],
                                       df[f"gate_{variant}_{other}"]),
                band_agreement=float((df[f"band_{variant}_equal"]
                                      == df[f"band_{variant}_{other}"]).mean()),
                band_kappa=cohen_kappa(df[f"band_{variant}_equal"],
                                       df[f"band_{variant}_{other}"]),
                spearman_cdi=float(spearmanr(df[f"cdi_{variant}_equal"],
                                             df[f"cdi_{variant}_{other}"])[0]),
            ))

    # Stability across the Euclidean/network switch, holding the weighting fixed.
    for name in ("equal", "entropy", "pca"):
        stability_rows.append(dict(
            note=("same as the equal row: PCA = equal weights by construction"
                  if name == "pca" else ""),
            comparison=f"{name}: Euclidean vs network",
            gate_agreement=float((df[f"gate_euclid_{name}"] == df[f"gate_net_{name}"]).mean()),
            gate_kappa=cohen_kappa(df[f"gate_euclid_{name}"], df[f"gate_net_{name}"]),
            band_agreement=float((df[f"band_euclid_{name}"] == df[f"band_net_{name}"]).mean()),
            band_kappa=cohen_kappa(df[f"band_euclid_{name}"], df[f"band_net_{name}"]),
            spearman_cdi=float(spearmanr(df[f"cdi_euclid_{name}"],
                                         df[f"cdi_net_{name}"])[0]),
        ))

    stab = pd.DataFrame(stability_rows).round(4)
    stab = stab[["comparison", "gate_agreement", "gate_kappa", "band_agreement",
                 "band_kappa", "spearman_cdi", "note"]]
    wtab = pd.DataFrame(weight_rows)
    df.to_csv(C.DERIVED / "a03_index.csv", index=False)
    C.write_table(wtab, "table04a_index_weights",
                  "Composite index weights under three schemes, for Euclidean and "
                  "network accessibility (two are distinct: PCA equals equal "
                  "weights by construction with two criteria; n = 186 routes)")
    C.write_table(stab, "table04b_decision_stability",
                  "Stability of the trunk-eligibility gate and Jenks band "
                  "under alternative weightings and accessibility measures "
                  "(in-sample, n = 186 routes)")

    # Direct weight sweep — the genuine weighting-robustness evidence.
    sweeps = {}
    for variant in ("net", "euclid"):
        Pv = df[f"pop_score_{variant}"].to_numpy()
        Qv = df[f"poi_score_{variant}"].to_numpy()
        sweeps[variant] = weight_sweep(
            Pv, Qv, df[f"cdi_{variant}_equal"].to_numpy(),
            df[f"gate_{variant}_equal"].to_numpy(),
            df[f"band_{variant}_equal"].to_numpy())
    sweep_tab = pd.DataFrame(
        [dict(variant=v, **{k: (round(x, 4) if isinstance(x, float) else x)
                            for k, x in r.items()})
         for v, rows_ in sweeps.items() for r in rows_])
    C.write_table(sweep_tab, "table04c_weight_sweep",
                  "Population-weight sweep (w_population 0.1-0.9, opportunity "
                  "weight = 1 - w_population): agreement of trunk gate and Jenks "
                  "band with the plan's 0.5/0.5 weighting (in-sample, n = 186 routes)")

    poi_shift = 100 * (df["poi_w_euclid"] - df["poi_w_net"]) / df["poi_w_euclid"].replace(0, np.nan)
    out = dict(
        n_routes=int(len(df)),
        poi_budget_m=POI_BUDGET_M,
        trunk_gate_percentile=TRUNK_GATE_PERCENTILE,
        n_bands=N_BANDS,
        ahp_weights_derived=False,
        ahp_note=("No expert panel was convened for this study, so analytic "
                  "hierarchy process weights are not derived. Weighting schemes "
                  "computed are equal, Shannon entropy and first principal "
                  "component; only two of the three are distinct (see "
                  "n_distinct_weightings)."),
        evidence_status=dict(
            in_sample=True, n=int(len(df)),
            base="all 186 active plan routes; no hold-out",
            poi_incidence_source=poi_source),
        n_schemes_computed=results["net"]["distinct_weightings"]["n_schemes_computed"],
        n_distinct_weightings=int(min(
            results[v]["distinct_weightings"]["n_distinct_weightings"]
            for v in results)),
        n_distinct_weightings_note=(
            "Three schemes are computed but only two are distinct weightings: "
            "PCA on exactly two positively correlated criteria returns 0.5/0.5 "
            "for every correlation, so 'equal' and 'pca' are identical by "
            "construction (not a robustness finding). The data-driven "
            "alternative is entropy only."),
        identical_by_construction=[
            dict(variant=v, **p)
            for v in results
            for p in results[v]["distinct_weightings"]["identical_pairs"]
            if p["identical_by_construction"]],
        collinearity_rule=dict(
            threshold=COLLINEARITY_THRESHOLD,
            threshold_source="assumption (paper §4.5; no citation)",
            by_variant={v: results[v]["collinearity_rule"] for v in results},
            fired_in_all_variants=bool(all(results[v]["collinearity_rule"]["rule_fired"]
                                           for v in results)),
            headline=(
                "Pearson r = {:.3f} (Euclidean) / {:.3f} (network); Spearman rho = "
                "{:.3f} / {:.3f}. The declared rho > 0.85 rule fires; its declared "
                "action (substitute PCA) leaves the composite unchanged because PCA "
                "= equal weights here.").format(
                    results["euclid"]["pearson_r"], results["net"]["pearson_r"],
                    results["euclid"]["spearman_rho"], results["net"]["spearman_rho"]),
        ),
        weight_sweep_population_weight=dict(
            note=("w_population swept 0.1-0.9; agreement is with the plan's "
                  "0.5/0.5 composite; in-sample over the 186 routes"),
            by_variant=sweeps,
        ),
        opportunity_overstatement_note=(
            "The Euclidean arm measures distance to the continuous route line, the "
            "network arm to discrete virtual stops up to 125 m apart, so part of the "
            "median overstatement is stop discretisation, not the network itself."),
        by_variant=results,
        opportunity_overstatement_pct_median=float(poi_shift.median()),
        n_poi_euclid_total=int(df["n_poi_euclid"].sum()),
        n_poi_net_total=int(df["n_poi_net"].sum()),
        stability=stab.to_dict(orient="records"),
        weights_table=wtab.to_dict(orient="records"),
    )
    C.write_result(out, "a03_index_weights")

    for v in ("euclid", "net"):
        rr = results[v]
        log.info("%s: rho(Pop,POI) Pearson %.3f (p=%.2g), Spearman %.3f; "
                 "weights equal %.2f/%.2f entropy %.2f/%.2f pca %.2f/%.2f",
                 v, rr["pearson_r"], rr["pearson_p"], rr["spearman_rho"],
                 *rr["weights"]["equal"], *rr["weights"]["entropy"],
                 *rr["weights"]["pca"])
    log.info("opportunity gravity: %d POI-route incidences Euclidean vs %d "
             "network (median route overstatement %.1f%%)",
             out["n_poi_euclid_total"], out["n_poi_net_total"],
             out["opportunity_overstatement_pct_median"])
    for row in stability_rows:
        log.info("stability %-32s gate %.1f%% (k=%.3f)  band %.1f%% (k=%.3f)  "
                 "rho(CDI)=%.4f", row["comparison"],
                 100 * row["gate_agreement"], row["gate_kappa"],
                 100 * row["band_agreement"], row["band_kappa"],
                 row["spearman_cdi"])


if __name__ == "__main__":
    main(recompute_poi="--recompute-poi" in sys.argv[1:])
