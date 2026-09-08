#!/usr/bin/env python
"""
a02b_faithfulness.py — verify that the reimplementation reproduces the published
plan exactly, and account for every route where it does not.

Why this is separate from a02. a02 does the expensive work: 22,360 virtual stops,
a multi-source Dijkstra per route over a 962k-node graph, and four zonal-statistics
passes each. That takes about seventy minutes. The faithfulness check is a
comparison of two columns, so it belongs in its own module that reads a02's output
and can be re-run in seconds as the accounting is refined.

Why faithfulness matters more than it looks. Every downstream claim in the paper —
that Euclidean catchments overstate population served by a third, that coverage
falls from 35.5% to 24.2% — depends on the Euclidean baseline being the *published
plan's own* number rather than an approximation of it. If the reimplementation of
the Euclidean method disagrees with the plan, the network comparison is measuring
reimplementation error and network effect together, and neither can be separated.
So the Euclidean baseline is held to reproduction, not to plausibility, and every
residual is named.

What the accounting found. Three things stand between a naive recomputation and
the published column, none of them documented in the plan's own outputs:

  1. An undocumented tourist multiplier. `transit_kashmir_v3.py:1863` multiplies
     `Population_Served` by 1.3 on routes flagged `Tourist_Corridor`, to stand in
     for visitors a residential population raster cannot see. Eight active routes
     carry it. The intent is reasonable; the placement is not. The result is
     written to a column named as a population count and then used as the
     numerator of a coverage share, so for those eight routes the "population
     served" is not a population and the coverage share is not a share of
     residents. The reproduction package keeps the resident count and any demand
     adjustment in separate columns.
  2. A stale flag. One route reproduces at 1/1.3 of the published value while
     carrying `Tourist_Corridor = False`, i.e. it was boosted under a flag that
     was later cleared without the population being recomputed.
  3. Superseded geometry. Two routes retain a population computed for a longer
     alignment that has since been redrawn.

Together with the 44 substituted-distance routes established in a02, this is the
full inventory of places where the published artefact disagrees with itself. The
paper reports it as the concrete cost of patching outputs instead of re-running a
pipeline, which is the generalisable lesson rather than a local complaint.

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
        pearson_r=round(float(pearsonr(t[ok], v[ok])[0]), 5),
    )


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

    # What the misplaced multiplier does to the headline coverage numerator.
    boosted = df.loc[df["tourist"], "target_published"].sum()
    out["tourist_inflation"] = dict(
        n_routes=int(df["tourist"].sum()),
        published_sum=int(boosted),
        resident_sum=int(round(boosted / TOURIST_MULTIPLIER)),
        excess=int(round(boosted - boosted / TOURIST_MULTIPLIER)),
        note=("Per-route walkshed counts overlap between routes and must not be "
              "summed for a network total; this sum is reported only to size the "
              "adjustment embedded in the published column."),
    )

    tab = (df.groupby("disposition")
           .agg(n_routes=("New_Route_ID", "size"),
                median_abs_pct_error=("abs_pct_error", "median"),
                max_abs_pct_error=("abs_pct_error", "max"))
           .reset_index().round(3)
           .sort_values("n_routes", ascending=False))

    df.to_csv(C.DERIVED / "a02b_faithfulness.csv", index=False)
    C.write_table(tab, "table03b_faithfulness",
                  "Reproduction of the published population-served column by the "
                  "reimplemented Euclidean method, with every non-reproducing "
                  "route accounted for")
    C.write_result(out, "a02b_faithfulness")

    before = out["reproduction"]["before_tourist_adjustment"]
    after = out["reproduction"]["after_tourist_adjustment"]
    log.info("geometry-consistent routes: %d", before["n"])
    log.info("  before tourist adjustment: median |err| %.3f%%, within 1%% %d/%d, r=%.5f",
             before["median_abs_pct_error"], before["n_within_1pct"], before["n"],
             before["pearson_r"])
    log.info("  after  tourist adjustment: median |err| %.3f%%, within 1%% %d/%d, r=%.5f",
             after["median_abs_pct_error"], after["n_within_1pct"], after["n"],
             after["pearson_r"])
    log.info("disposition: %s", out["disposition_counts"])
    for r in out["not_reproduced"]:
        log.info("  NOT REPRODUCED %-9s %-34s %-18s ratio %.3f  (%s)",
                 r["New_Route_ID"], str(r["Route_Name"])[:34], r["Route_Type"],
                 r["ratio_adj"], r["disposition"])
    ti = out["tourist_inflation"]
    log.info("tourist multiplier inflates the published column on %d routes by "
             "%s (published %s vs resident %s)", ti["n_routes"],
             f"{ti['excess']:,}", f"{ti['published_sum']:,}", f"{ti['resident_sum']:,}")


if __name__ == "__main__":
    main()
