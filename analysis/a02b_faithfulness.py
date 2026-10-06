#!/usr/bin/env python
"""
a02b_faithfulness.py — verify that the reimplementation reproduces the published
plan exactly, and account for every route where it does not.

Why this is separate from a02. a02 does the expensive work: 22,360 virtual stops,
a multi-source Dijkstra per route over a 962k-node graph, and four zonal-statistics
passes each. That takes about seventy minutes. The faithfulness check is a
comparison of two columns, so it belongs in its own module that reads a02's output
and can be re-run in seconds as the accounting is refined.

Why faithfulness matters. The network comparison in a02 is only interpretable if
the Euclidean baseline reproduces the plan's own Euclidean number; otherwise it
measures reimplementation error and network effect together. The reproduction is
therefore reported twice, BEFORE and AFTER putting the recomputed resident count
through the tourist multiplier the engine applies, so the reader can see how much
of the agreement depends on that adjustment (n within 1 %, within 5 %, maximum
error, for each).

What the residuals are, and what they are not (audit F-03-13). The routes that do
not reproduce are sorted into labels by a numerical pattern in the ratio of
recomputed to published value:

  * `substituted_distance`: declared length disagrees with drawn geometry (a
    length comparison made in a02), so no like-for-like target exists.
  * `stale_tourist_flag`: ratio x 1.3 is within 5 % of 1 although the flag is off.
  * `superseded_geometry`: any other residual above 5 %.
  * `reproduced_minor_drift`: 1-5 % residual.

These labels are a RESIDUAL CLASSIFICATION, NOT TESTED CAUSES. No test here
establishes that a flag was cleared late or that a line was redrawn after its
population was computed; they are the hypotheses that fit the pattern, and each
output row carries `cause_status` saying so.

The tourist multiplier. `transit_kashmir_v3.py:1863` multiplies the per-route
`Population_Served` of `Tourist_Corridor` routes by 1.3 (8 active routes). That
column is a per-route walkshed count. The engine's NETWORK coverage figure is
`compute_network_population_total` (:1955-1980), which dissolves the `Catchment`
geometries and sums the raster once; it never reads `Population_Served`, so the
multiplier does not enter network coverage. The sum of the eight per-route
increments (reported in the output) double-counts overlapping walksheds and is
not a network quantity.

Outputs
    data/derived/a02b_faithfulness.csv        per-route target, recomputed, residual
    data/derived/a02b_faithfulness.json       reproduction metrics and inventory
    paper/tables/table03b_faithfulness.{csv,md}

Usage
    python analysis/a02b_faithfulness.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a02b")

TOURIST_MULTIPLIER = 1.3     # transit_kashmir_v3.py:506, applied at line 1863
TOL_EXACT = 0.01             # within 1% counts as reproduced
TOL_CLOSE = 0.05


def classify(row) -> str:
    """
    Name the reason a route's published population cannot be reproduced.

    Order matters: the substituted-distance group is established independently in
    a02 by comparing declared length against drawn length, so it is assigned
    first and the remaining labels describe only the geometry-consistent routes.
    """
    if not row["km_geometry_consistent"]:
        return "substituted_distance"
    if abs(row["ratio_adj"] - 1.0) <= TOL_EXACT:
        return "reproduced"
    if abs(row["ratio_adj"] * TOURIST_MULTIPLIER - 1.0) <= TOL_CLOSE:
        return "stale_tourist_flag"
    if abs(row["ratio_adj"] - 1.0) <= TOL_CLOSE:
        return "reproduced_minor_drift"
    return "superseded_geometry"


CAUSE_STATUS = {
    "reproduced": "reproduced (measured agreement within 1 %)",
    "reproduced_minor_drift": "residual classification, not tested",
    "stale_tourist_flag": "residual classification, not tested",
    "superseded_geometry": "residual classification, not tested",
    "substituted_distance": ("km/geometry mismatch established by length comparison in a02; "
                             "cause of the population gap not tested"),
}


def _metrics(target: pd.Series, recomputed: pd.Series) -> dict:
    """Reproduction metrics on a subset: nothing is dropped silently."""
    from scipy.stats import pearsonr
    t, v = target.to_numpy(float), recomputed.to_numpy(float)
    ok = np.isfinite(t) & np.isfinite(v) & (t > 0)
    if ok.sum() < 3:
        return dict(n=int(ok.sum()))
    err = 100.0 * np.abs(v[ok] - t[ok]) / t[ok]
    return dict(
        n=int(ok.sum()),
        median_abs_pct_error=round(float(np.median(err)), 3),
        p95_abs_pct_error=round(float(np.percentile(err, 95)), 3),
        max_abs_pct_error=round(float(err.max()), 3),
        n_within_1pct=int((err <= 100 * TOL_EXACT).sum()),
        n_within_5pct=int((err <= 100 * TOL_CLOSE).sum()),
        n_not_within_1pct=int((err > 100 * TOL_EXACT).sum()),
        pearson_r=round(float(pearsonr(t[ok], v[ok])[0]), 5),
        basis=("geometry-consistent routes only (declared length agrees with drawn "
               "geometry); in-sample reproduction of one plan, no held-out data"),
    )


def _non_reproducing(sub: pd.DataFrame, col: str) -> list[dict]:
    """Routes (geometry-consistent) whose recomputed value in `col` is off by > 1 %."""
    s = sub[sub["target_published"] > 0].copy()
    s["abs_pct_error_here"] = 100.0 * (s[col] / s["target_published"] - 1.0).abs()
    s = s[s["abs_pct_error_here"] > 100 * TOL_EXACT].sort_values("abs_pct_error_here",
                                                                 ascending=False)
    return [dict(New_Route_ID=r.New_Route_ID, Tourist_Corridor=bool(r.tourist),
                 target_published=float(r.target_published), recomputed=float(getattr(r, col)),
                 abs_pct_error=round(float(r.abs_pct_error_here), 3))
            for r in s.itertuples()]


def main() -> None:
    catch = pd.read_csv(C.DERIVED / "a02_catchments.csv")
    plan = pd.read_csv(C.PLAN_CSV)
    active = plan[plan["Action_Taken"].isin(C.ACTIVE_ACTIONS)]
    df = catch.merge(
        active[["New_Route_ID", "Tourist_Corridor", "Population_Served",
                "Population_Served_Raw"]],
        on="New_Route_ID", how="left", validate="one_to_one")
    if len(df) != len(catch):
        raise SystemExit(f"join changed row count: {len(catch)} -> {len(df)}")

    df["tourist"] = df["Tourist_Corridor"].fillna(False).astype(bool)
    df["target_published"] = df["plan_pop_raw"].astype(float)

    # The recomputed Euclidean count is a resident headcount. To compare it with
    # the published column it must be put through the same tourist adjustment the
    # engine applied, which is the only way to tell reimplementation error apart
    # from an undocumented transformation.
    df["recomputed_resident"] = df["pop_euclid"].astype(float)
    df["recomputed_as_published"] = np.where(
        df["tourist"], df["recomputed_resident"] * TOURIST_MULTIPLIER,
        df["recomputed_resident"])
    df["ratio_raw"] = df["recomputed_resident"] / df["target_published"]
    df["ratio_adj"] = df["recomputed_as_published"] / df["target_published"]
    df["abs_pct_error"] = 100.0 * (df["ratio_adj"] - 1.0).abs()
    df["disposition"] = df.apply(classify, axis=1)
    df["cause_status"] = df["disposition"].map(CAUSE_STATUS)
    df["tourist_increment_published_minus_resident"] = np.where(
        df["tourist"], df["target_published"] - df["target_published"] / TOURIST_MULTIPLIER, 0.0)

    consistent = df[df["km_geometry_consistent"]]
    out = dict(
        tourist_multiplier=TOURIST_MULTIPLIER,
        tourist_multiplier_source="transit_kashmir_v3.py:506, applied at line 1863",
        n_routes=int(len(df)),
        n_tourist_flagged_active=int(df["tourist"].sum()),
        reproduction=dict(
            before_tourist_adjustment=_metrics(consistent["target_published"],
                                               consistent["recomputed_resident"]),
            after_tourist_adjustment=_metrics(consistent["target_published"],
                                              consistent["recomputed_as_published"]),
        ),
        disposition_counts={k: int(v) for k, v in
                            df["disposition"].value_counts().items()},
        disposition_status=("RESIDUAL CLASSIFICATION, NOT TESTED CAUSES: the labels sort routes by "
                            "the pattern of recomputed/published ratio; no test establishes why a "
                            "route fails to reproduce (audit F-03-13). Per-route status in "
                            "a02b_faithfulness.csv:cause_status."),
        reproduction_non_reproducing_routes=dict(
            before_tourist_adjustment=_non_reproducing(consistent, "recomputed_resident"),
            after_tourist_adjustment=_non_reproducing(consistent, "recomputed_as_published"),
            note="geometry-consistent routes with absolute error above 1 %; ids, no personal data",
        ),
        note=("Reproduction is assessed only on routes whose declared length "
              "agrees with their drawn geometry; on the remainder the published "
              "population belongs to a different alignment than the published "
              "distance, so no target exists. The tourist multiplier is applied "
              "to the recomputed value purely to make the two series comparable "
              "— the reproduction package itself keeps resident population and "
              "demand adjustments in separate columns."),
    )

    # Name every route that does not reproduce, so nothing is left as a residual.
    unexplained = df[df["disposition"].isin(["stale_tourist_flag",
                                             "superseded_geometry",
                                             "reproduced_minor_drift"])]
    out["not_reproduced"] = unexplained[
        ["New_Route_ID", "Route_Name", "Route_Type", "Route_KM", "geom_km",
         "target_published", "recomputed_resident", "ratio_adj", "disposition"]
    ].round(4).to_dict(orient="records")

    # The tourist multiplier: per-route increments, and why they are NOT a network quantity.
    tf = df[df["tourist"]].sort_values("tourist_increment_published_minus_resident",
                                       ascending=False)
    boosted = float(tf["target_published"].sum())
    resident = boosted / TOURIST_MULTIPLIER
    # Does the data support reading the published column as 1.3 x resident on these routes?
    tf_ratio_raw = tf["ratio_raw"]
    out["tourist_inflation"] = dict(
        n_routes_affected=int(len(tf)),
        n_routes=int(len(tf)),
        multiplier=TOURIST_MULTIPLIER,
        per_route_increments=[
            dict(New_Route_ID=r.New_Route_ID, published_per_route_count=float(r.target_published),
                 implied_resident_count=float(r.target_published / TOURIST_MULTIPLIER),
                 increment=float(r.tourist_increment_published_minus_resident),
                 recomputed_resident_count=float(r.recomputed_resident),
                 disposition=r.disposition)
            for r in tf.itertuples()],
        sum_of_per_route_increments=float(tf["tourist_increment_published_minus_resident"].sum()),
        sum_of_per_route_increments_note=(
            "Sum over the affected routes of (published per-route walkshed count minus the same "
            "count divided by 1.3). Per-route walksheds overlap, so this double-counts residents "
            "who live in more than one of these walksheds. It is NOT a number of persons in any "
            "network coverage figure and is reported only to size the per-route adjustment."),
        published_sum=int(boosted),
        resident_sum=int(round(resident)),
        excess=int(round(boosted - resident)),
        excess_note=("LEGACY key, same quantity as sum_of_per_route_increments; the earlier label "
                     "'synthetic persons injected into the coverage numerator' was wrong - see "
                     "entered_network_coverage"),
        entered_network_coverage=False,
        entered_network_coverage_evidence=(
            "transit_kashmir_v3.py:1863 applies the multiplier to the per-route 'Population_Served' "
            "column only. The network coverage figure is compute_network_population_total "
            "(transit_kashmir_v3.py:1955-1980, called at :6029), which reads only gdf['Catchment'] "
            "and takes one rasterstats.zonal_stats sum over the dissolved union; it never reads "
            "Population_Served, so the multiplier has zero effect on the published network "
            "coverage (2,317,958 / 35.2 %). Established by reading the code, not by re-running it."),
        data_support_for_reading_published_as_1p3_x_resident=dict(
            n_geometry_consistent_tourist_routes=int(tf["km_geometry_consistent"].sum()),
            median_ratio_recomputed_resident_to_published=float(tf_ratio_raw.median()),
            n_within_1pct_after_x1p3=int(((tf["ratio_adj"] - 1).abs() <= TOL_EXACT)[
                tf["km_geometry_consistent"]].sum()),
            note=("on geometry-consistent tourist routes the recomputed resident count is about "
                  "1/1.3 of the published value and matches it within 1 % after x1.3; this is the "
                  "evidence that the published per-route column carries the multiplier")),
        note=("Per-route walkshed counts overlap between routes and must not be summed for a "
              "network total; this sum is reported only to size the adjustment embedded in the "
              "published per-route column. It did not enter network coverage."),
    )

    df["abs_pct_error_before_adjustment"] = 100.0 * (df["ratio_raw"] - 1.0).abs()
    tab = (df.groupby("disposition")
           .agg(n_routes=("New_Route_ID", "size"),
                median_abs_pct_error_before_adjustment=("abs_pct_error_before_adjustment", "median"),
                median_abs_pct_error=("abs_pct_error", "median"),
                max_abs_pct_error=("abs_pct_error", "max"))
           .reset_index()
           .assign(cause_status=lambda t: t["disposition"].map(CAUSE_STATUS))
           .round(3)
           .sort_values("n_routes", ascending=False))

    df.to_csv(C.DERIVED / "a02b_faithfulness.csv", index=False)
    C.write_table(tab, "table03b_faithfulness",
                  "Reproduction of the published population-served column by the "
                  "reimplemented Euclidean method, 186 active routes (in-sample). Labels "
                  "other than 'reproduced' are a residual classification, not tested causes; "
                  "'error' columns are after / before the x1.3 tourist adjustment")
    C.write_result(out, "a02b_faithfulness")

    before = out["reproduction"]["before_tourist_adjustment"]
    after = out["reproduction"]["after_tourist_adjustment"]
    log.info("geometry-consistent routes: %d", before["n"])
    log.info("  before tourist adjustment: median |err| %.3f%%, within 1%% %d/%d, r=%.5f",
             before["median_abs_pct_error"], before["n_within_1pct"], before["n"],
             before["pearson_r"])
    log.info("  before: max err %.2f%%; after: max err %.2f%%; routes not within 1%% after adjustment: %d",
             before["max_abs_pct_error"], after["max_abs_pct_error"], after["n_not_within_1pct"])
    log.info("  after  tourist adjustment: median |err| %.3f%%, within 1%% %d/%d, r=%.5f",
             after["median_abs_pct_error"], after["n_within_1pct"], after["n"],
             after["pearson_r"])
    log.info("disposition: %s", out["disposition_counts"])
    for r in out["not_reproduced"]:
        log.info("  NOT REPRODUCED %-9s %-34s %-18s ratio %.3f  (%s)",
                 r["New_Route_ID"], str(r["Route_Name"])[:34], r["Route_Type"],
                 r["ratio_adj"], r["disposition"])
    ti = out["tourist_inflation"]
    log.info("tourist multiplier raises the per-route column on %d routes; per-route increments "
             "sum to %s (overlapping walksheds double-counted; entered_network_coverage=%s)",
             ti["n_routes_affected"], f"{ti['sum_of_per_route_increments']:,.0f}",
             ti["entered_network_coverage"])


if __name__ == "__main__":
    main()
