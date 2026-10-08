"""
poi_retier_check.py
===================
One-off check behind paper/PARAMETERS_AND_DEFENSIBILITY.md (section 3, group A).

Question: the engine gives every mapped place of worship, shop tagged "mall" and
hospital the top destination weight (1.0), and every hotel or hostel 0.6. If
those categories are moved to a lower tier or dropped, how many of the 186
routes change class?

Method: the engine's own rule (destinations within 250 m straight line of the
route, weighted count per route km, min-max, 0.5/0.5 with the population score,
Jenks k = 3), exactly as analysis/a03_index_weights.py builds its
`band_euclid_equal` column. The baseline here must reproduce that column on all
186 routes before any variant is read.

This is an index-only partition. The published Priority_Band also carries
overrides (e-bus lock, social floor, district-headquarters floor, road
tie-break), so these counts describe the index, not the published bands.

Not part of run_all and not in the claim ledger. Output:
analysis/checks/poi_retier_check.csv

Run:
    .venv/Scripts/python.exe analysis/checks/poi_retier_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import a03_index_weights as A  # noqa: E402
import common as C  # noqa: E402

OUT = HERE / "poi_retier_check.csv"
POI_BUFFER_M = 250.0
SHOP_CATS = ["mall", "supermarket"]
HOTEL_CATS = ["tourist_hotel"]


def main() -> None:
    import geopandas as gpd
    import shapely
    from scipy.stats import spearmanr

    routes = gpd.read_file(C.PLAN_GEOJSON).to_crs(C.UTM)
    routes["geometry"] = routes.geometry.simplify(2.0)
    ids = routes["New_Route_ID"].tolist()

    pois = pd.read_csv(C.POIS_CSV)
    pts = gpd.GeoSeries(gpd.points_from_xy(pois.lon, pois.lat), crs=C.WGS84).to_crs(C.UTM).values
    inc = np.vstack([shapely.distance(g, pts) <= POI_BUFFER_M for g in routes.geometry.values])

    catch = pd.read_csv(C.DERIVED / "a02_catchments.csv").set_index("New_Route_ID")
    idx = pd.read_csv(C.DERIVED / "a03_index.csv").set_index("New_Route_ID")
    km = pd.Series(routes.set_index("New_Route_ID").loc[ids, "Route_KM"].astype(float).to_numpy(), index=ids)
    pop = np.asarray(A.pop_score(catch.loc[ids, "pop_euclid"], km))

    name = pois["name"].fillna("").str.lower()
    cat = pois["category"]
    worship = cat == "jamia_masjid"
    generic_worship = worship & ~name.str.contains(r"jamia|jama |jama$")
    base_w = pois["importance"].map(A.TIER_WEIGHT).to_numpy()

    def bands(w: np.ndarray | None):
        if w is None:
            return A.jenks_bands(pop), pop
        q = np.asarray(A.poi_score(pd.Series(inc @ w, index=ids), km))
        cdi = 0.5 * pop + 0.5 * q
        return A.jenks_bands(cdi), cdi

    b0, c0 = bands(base_w)
    reproduced = int((b0 == idx.loc[ids, "band_euclid_equal"].to_numpy()).sum())
    if reproduced != len(ids):
        raise SystemExit(f"baseline reproduces a03 on {reproduced} of {len(ids)} routes; stop")

    def variant(**changes) -> np.ndarray:
        w = base_w.copy()
        for mask, value in changes.values():
            w[mask.to_numpy()] = value
        return w

    variants = {
        "Places of worship not named Jamia/Jama: 1.0 -> 0.4": variant(a=(generic_worship, 0.4)),
        "Places of worship not named Jamia/Jama: dropped": variant(a=(generic_worship, 0.0)),
        "All places of worship: dropped": variant(a=(worship, 0.0)),
        "Worship (generic), shops, hotels: all 0.4": variant(
            a=(generic_worship, 0.4), b=(cat.isin(SHOP_CATS + HOTEL_CATS), 0.4)),
        "Worship (generic) and hotels dropped; shops 0.4": variant(
            a=(generic_worship, 0.0), b=(cat.isin(HOTEL_CATS), 0.0), c=(cat.isin(SHOP_CATS), 0.4)),
        "Every destination weight 1 (plain count)": np.ones(len(pois)),
        "No destination layer (population only)": None,
    }
    rows = []
    for label, w in variants.items():
        b, c = bands(w)
        rows.append(dict(
            variant=label,
            routes_changing_class=int((b != b0).sum()),
            agreement_pct=round(100 * float((b == b0).mean()), 1),
            kappa=round(A.cohen_kappa(b, b0), 3),
            spearman_of_index=round(float(spearmanr(c, c0)[0]), 3),
            moved_up=int((b > b0).sum()), moved_down=int((b < b0).sum())))
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)

    share = (inc @ (base_w * worship.to_numpy())) / np.maximum(inc @ base_w, 1e-9)
    print(f"baseline reproduces a03 band_euclid_equal on {reproduced} of {len(ids)} routes")
    print(f"tier-1 destinations {int((pois.importance == 'high').sum())}; places of worship {int(worship.sum())}; "
          f"not named Jamia/Jama {int(generic_worship.sum())}")
    print(f"share of a route's destination score from places of worship: median {np.median(share):.2f}, "
          f"routes above one half: {int((share > 0.5).sum())}")
    print(f"routes with no destination within {POI_BUFFER_M:.0f} m: {int(((inc @ np.ones(len(pois))) == 0).sum())}")
    print(df.to_string(index=False))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
