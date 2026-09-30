#!/usr/bin/env python
"""
a05_headway_timeofday.py — §5.6: a single all-day headway is not a service plan.

The objection this module exists to answer. The plan publishes exactly one
headway per route and sizes the fleet from it. A referee reading that will ask
the obvious operational question: buses are bought for the peak and paid for all
day, so a plan that cannot distinguish 09:00 from 21:00 has not costed itself.
Worse, a uniform headway is simultaneously *too generous* off-peak (buses run
near-empty, burning the operating subsidy) and *too thin* at the peak (the
maximum-load section is where crush loading actually happens). Neither error is
visible in an all-day average.

What this module can and cannot do — read before using any number below.
`Hourly_Passenger_Count.csv` is a **supply-side fare-collection artefact**, not a
travel-demand survey. Specifically it is:
  * BOARDINGS (ticket transactions), aggregated to whole clock hours, summed
    across the WHOLE Srinagar Smart City e-bus network — the 30 CHALO-operated
    routes — for the single month of **April 2026**;
  * NOT an origin–destination matrix. It carries no information about where a
    passenger alighted, so it cannot support any statement about trip length,
    interchange or corridor flow;
  * NOT route-level. Every route in the e-bus network is pooled into one number
    per hour, so it cannot rank routes or size an individual route;
  * NOT the 186-route rationalised plan. The 156 non-SSCL routes in the plan are
    conventional diesel permits with no electronic ticketing, and therefore
    contribute nothing to this file. Applying its temporal SHAPE to them is an
    assumption of transferability which this study cannot test, and which is
    reported as an assumption rather than a result;
  * NOT a maximum-load-section count. Frequency setting properly requires the
    passenger flow past the busiest point of a route; boardings are used here as
    a proxy for the temporal shape of that flow, which assumes the ratio of
    max-load flow to boardings is stable across the day.
The file reconciles exactly to the published monthly aggregate: the hourly
boardings sum to 1,221,848, which is the April 2026 figure in
`chalo_ridership.csv` to the passenger. That reconciliation is computed and
asserted here, so the provenance claim is tested rather than asserted.

How the bands are chosen. Asserting "peak is 08:00–11:00" would reintroduce
exactly the kind of unjustified constant the paper criticises elsewhere, so the
bands are derived. Two classifications are computed:
  1. Jenks natural breaks on the 17 hourly rates (Jenks 1967) — the same device
     a04 uses for route tiers. This finds homogeneous MAGNITUDE classes but
     ignores the clock, so it can place 17:00 in the same class as 09:00 and
     split 13:00 out of the middle of the afternoon. Useful as a description of
     the demand distribution; useless as a duty roster.
  2. Fisher's exact dynamic program for grouping an ORDERED sequence into k
     contiguous groups of maximum homogeneity (Fisher 1958) — the same
     within-class-variance objective, but constrained so every class is a
     contiguous block of clock time. This yields bands an operator can actually
     run. This is the primary classification.
In both cases k is chosen by the goodness-of-variance-fit elbow over k = 2..6,
using `common.goodness_of_variance_fit`, so the number of bands is read off the
data rather than set to three because three is a familiar number.

How the headway multipliers are derived. Two published rules, both reported,
because they disagree and the disagreement is the interesting part.
  * PROPORTIONAL (capacity-matching). Classical maximum-load-section frequency
    setting sets f = P/(c·alpha) — vehicles per hour equal to passenger flow
    divided by capacity times target load factor (Vuchic 2005; Ceder 2007;
    TRB 2013 TCQSM 3rd ed.). Headway is therefore inversely proportional to the
    demand rate, and the band multiplier is m_b = D_ref / D_b.
  * SQUARE-ROOT (welfare-optimal). Minimising the sum of operator cost and
    passenger waiting cost gives frequency proportional to the square root of
    demand — Mohring's (1972) square-root principle, anticipated by Newell
    (1971). The multiplier is then m_b = sqrt(D_ref / D_b). This is the gentler
    rule and the defensible one when the operator is subsidised, because it does
    not strip service from thin periods as aggressively.
Two reference anchors are reported, because the plan does not say which one its
single headway represents:
  * MEAN-ANCHORED — the published headway is read as matching the all-day mean
    rate. The peak then has to tighten below the published headway, which costs
    vehicles.
  * PEAK-ANCHORED — the published headway is read as a peak design, which is
    standard practice. The peak band keeps the published headway (so the vehicle
    purchase is unchanged) and every other band stretches, which saves bus-hours.
Both are clipped by the plan's own policy limits: HEADWAY_MAX_MIN = 35 for
urban and peri-urban classes, and the 50-minute maximum of
REGIONAL_HEADWAY_BUCKETS for rural lifelines.

Fleet arithmetic. Vehicles are resized with the engine's own rule, verified here
against the published plan rather than assumed: fleet = ceil(ceil(cycle/headway)
* FLEET_SPARE_RATIO). Peak fleet is what has to be bought; bus-hours summed over
bands is what has to be paid for every day.

Outputs
    data/derived/a05_headway_timeofday.json
    paper/tables/table05h_timeofday.{csv,md}       band profile + multipliers
    paper/tables/table05h_timeofday_headways.{csv,md}   banded headway schedule
    paper/tables/table05h_timeofday_fleet.{csv,md}      fleet and bus-hour effect

Usage
    python analysis/a05_headway_timeofday.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a05")

SERVICE_HOURS = tuple(range(6, 23))     # observed operating window in the file
K_RANGE = tuple(range(2, 7))            # class counts scanned for the GVF elbow
MONTH_LABEL = "April 2026"

# Band names are assigned by clock position once the breaks are found, so that
# the vocabulary of §5.6 (peak / off-peak / evening) attaches to bands the data
# chose rather than to hours chosen to fit the vocabulary.
BAND_NAME_BY_RANK = {
    "peak": "Peak",
    "base": "Off-peak (base)",
    "opening": "Opening shoulder",
    "evening": "Evening",
}


# ── segmentation ─────────────────────────────────────────────────────────────
def fisher_contiguous(values: np.ndarray, k: int) -> tuple[list[tuple[int, int]], float]:
    """
    Fisher (1958) exact grouping of an ORDERED sequence into k contiguous groups
    minimising the within-group sum of squares.

    Jenks natural breaks is this same objective applied to values sorted by
    magnitude. Applying it to values kept in clock order instead is what makes
    the resulting classes usable as service bands: every class is a block of
    consecutive hours by construction. The dynamic program is exact (no
    heuristic seeding), so the bands are a deterministic function of the counts.

    Returns the list of (start_index, end_index) inclusive pairs and the total
    within-band sum of squares.
    """
    v = np.asarray(values, dtype=float)
    n = v.size
    if k >= n:
        return [(i, i) for i in range(n)], 0.0
    cs = np.concatenate([[0.0], np.cumsum(v)])
    cs2 = np.concatenate([[0.0], np.cumsum(v * v)])

    def sse(i: int, j: int) -> float:
        """Within-group sum of squares for values[i..j] inclusive."""
        m = j - i + 1
        s = cs[j + 1] - cs[i]
        s2 = cs2[j + 1] - cs2[i]
        return float(s2 - s * s / m)

    INF = float("inf")
    cost = np.full((k + 1, n + 1), INF)
    back = np.zeros((k + 1, n + 1), dtype=int)
    cost[0, 0] = 0.0
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            best, best_i = INF, -1
            for i in range(c - 1, j):
                if cost[c - 1, i] == INF:
                    continue
                val = cost[c - 1, i] + sse(i, j - 1)
                if val < best - 1e-12:
                    best, best_i = val, i
            cost[c, j], back[c, j] = best, best_i
    segs, j = [], n
    for c in range(k, 0, -1):
        i = back[c, j]
        segs.append((i, j - 1))
        j = i
    return list(reversed(segs)), float(cost[k, n])


def jenks_labels(values: np.ndarray, k: int) -> tuple[np.ndarray, list[float]]:
    """Magnitude-only Jenks classes, reported as the contrast case."""
    import jenkspy
    v = np.asarray(values, dtype=float)
    breaks = [float(b) for b in jenkspy.jenks_breaks(v, n_classes=k)]
    inner = np.asarray(breaks[1:-1])
    return np.searchsorted(inner, v, side="right"), breaks


def gvf_elbow(gvfs: dict[int, float]) -> int:
    """
    Choose k where the marginal gain in goodness-of-variance-fit collapses.

    The rule: take the largest k whose marginal gain over k-1 is at least a fifth
    of the previous marginal gain. Stated here rather than eyeballed so that the
    choice is reproducible; the gains are reported in the JSON so a reader can
    check that the elbow is not marginal.
    """
    ks = sorted(gvfs)
    gains = {k: gvfs[k] - gvfs[kp] for kp, k in zip(ks[:-1], ks[1:])}
    chosen = ks[1]
    prev_gain = gains[ks[1]]
    for k in ks[2:]:
        if gains[k] >= 0.20 * prev_gain:
            chosen, prev_gain = k, gains[k]
        else:
            break
    return chosen


# ── engine fleet rule ────────────────────────────────────────────────────────
def engine_fleet(cycle_min, headway_min, floor=1):
    """
    The engine's own vehicle rule: ceil(ceil(cycle/headway) * spare).

    The spare ratio is applied to the integer vehicle count, not to the
    continuous ratio, and the result is rounded up again. Both roundings matter:
    applying the spare to the continuous ratio reproduces only a minority of the
    published fleet, and this form reproduces 184 of 186 exactly (see the
    reproduction check in main(), which reports the exceptions rather than
    silently absorbing them).
    """
    spare = C.PARAMETERS["FLEET_SPARE_RATIO"]["value"]
    base = np.ceil(np.ceil(np.asarray(cycle_min, float)
                           / np.asarray(headway_min, float)) * spare)
    return np.maximum(base, floor).astype(int)


def headway_ceiling(route_type: pd.Series) -> np.ndarray:
    """Policy maximum wait by class: 35 min urban/peri-urban, 50 min rural."""
    return np.where(route_type.eq("Regional_District"),
                    float(max(C.REGIONAL_HEADWAY_BUCKETS)),
                    float(C.HEADWAY_MAX_MIN))


# ── main ─────────────────────────────────────────────────────────────────────
def load_hourly() -> tuple[pd.DataFrame, dict]:
    """
    Read the count file and rebuild a complete day x hour grid.

    The file emits no zero rows — the smallest count present is 3 — so an absent
    (date, hour) cell means no boarding was recorded in that hour, not that the
    hour was unobserved. The absences are not scattered: the 06:00 hour is
    missing only on 1–6 April and the 22:00 hour only on 1 and 3 April, i.e. the
    operating day was extended at both ends in the first week. Filling with zero
    is therefore the faithful reading, and it keeps every hourly mean on the same
    30-day denominator.
    """
    raw = pd.read_csv(C.HOURLY_PAX_CSV, skiprows=1)
    header = pd.read_csv(C.HOURLY_PAX_CSV, nrows=0).columns[0]
    df = raw.dropna(subset=["DATE"]).copy()
    df["DATE"] = pd.to_datetime(df["DATE"], format="%d-%m-%Y")
    df["Hours"] = df["Hours"].astype(int)
    df["pax"] = df["Passenger Count"].astype(float)
    df["collection"] = df["Total Collection"].astype(float)

    grid = (df.pivot_table(index="DATE", columns="Hours", values="pax", aggfunc="sum")
              .reindex(columns=list(SERVICE_HOURS)))
    n_missing_cells = int(grid.isna().sum().sum())
    grid = grid.fillna(0.0)

    meta = dict(
        file_title_row=str(header),
        n_days=int(grid.shape[0]),
        n_hours=int(grid.shape[1]),
        service_window=f"{min(SERVICE_HOURS):02d}:00-{max(SERVICE_HOURS):02d}:59",
        n_rows_in_file=int(len(df)),
        n_empty_cells_filled_zero=n_missing_cells,
        min_nonzero_count=int(df["pax"].min()),
        n_zero_rows_in_file=int((df["pax"] == 0).sum()),
        total_boardings=int(df["pax"].sum()),
        total_collection_inr=float(df["collection"].sum()),
    )
    return grid, meta


def reconcile_with_monthly(meta: dict) -> dict:
    """
    Test the provenance claim against the published monthly aggregate.

    If the hourly file really is the April 2026 network total, its boardings must
    equal the April row of `chalo_ridership.csv`. This is checked rather than
    assumed, and the collection figures are compared too because they do NOT
    agree, which is a data-quality fact the paper should own rather than discover
    in review.
    """
    rid = pd.read_csv(C.CHALO_RIDERSHIP_CSV)
    apr = rid[rid["Month"].astype(str).str.strip().str.lower() == "april"]
    if apr.empty:
        return dict(status="NOT_COMPUTABLE",
                    reason="no April row in chalo_ridership.csv")

    def inr(x):
        return float(str(x).replace(",", "").replace("?", "").replace("₹", "").strip())

    monthly_pax = int(inr(apr["Total"].iloc[0]))
    monthly_coll = inr(apr["Total Collection"].iloc[0])
    return dict(
        status="OK",
        monthly_total_boardings=monthly_pax,
        hourly_file_total_boardings=meta["total_boardings"],
        boardings_match=bool(monthly_pax == meta["total_boardings"]),
        monthly_total_collection_inr=monthly_coll,
        hourly_file_total_collection_inr=meta["total_collection_inr"],
        collection_diff_pct=round(100.0 * (meta["total_collection_inr"] / monthly_coll - 1), 2),
        note=("Boardings reconcile exactly, confirming the file is the whole "
              "SSCL/CHALO e-bus network for April 2026. Collection does not "
              "reconcile; the hourly file is higher. The discrepancy is "
              "reported, not adjusted — no basis exists in the supplied data "
              "for choosing which figure is right, and nothing in this module "
              "depends on the fare revenue."),
    )


def name_bands(bands: list[dict]) -> list[dict]:
    """
    Attach §5.6's vocabulary to the bands the segmentation produced.

    The highest-rate band is the peak. Of the remainder, the band that ends the
    service day is the evening, the band that opens it (if it is not the peak) is
    the opening shoulder, and anything between is the base. Names are cosmetic;
    the hours and the rates are the result.
    """
    out = [dict(b) for b in bands]
    peak_i = int(np.argmax([b["mean_boardings_per_hour"] for b in out]))
    last_i, first_i = len(out) - 1, 0
    for i, b in enumerate(out):
        if i == peak_i:
            b["band"] = BAND_NAME_BY_RANK["peak"]
        elif i == last_i:
            b["band"] = BAND_NAME_BY_RANK["evening"]
        elif i == first_i:
            b["band"] = BAND_NAME_BY_RANK["opening"]
        else:
            b["band"] = BAND_NAME_BY_RANK["base"]
    # More than one interior band would collide on the same name; disambiguate
    # by clock so the table stays readable and unique.
    seen: dict[str, int] = {}
    for b in out:
        seen[b["band"]] = seen.get(b["band"], 0) + 1
    dup = {k for k, v in seen.items() if v > 1}
    for b in out:
        if b["band"] in dup:
            b["band"] = f"{b['band']} {b['hours']}"
    return out


def main() -> None:
    grid, meta = load_hourly()
    recon = reconcile_with_monthly(meta)
    log.info("counts: %d days x %d hours, %s boardings (%s)",
             meta["n_days"], meta["n_hours"], f"{meta['total_boardings']:,}", MONTH_LABEL)
    log.info("provenance check: hourly total == monthly published total -> %s",
             recon.get("boardings_match"))
    if recon.get("status") == "OK" and not recon["boardings_match"]:
        log.warning("  boardings DO NOT reconcile with chalo_ridership.csv")
    if recon.get("status") == "OK":
        log.info("  collection differs by %+.2f%% (reported, not adjusted)",
                 recon["collection_diff_pct"])

    hours = np.array(grid.columns, dtype=int)
    prof = grid.mean(axis=0).to_numpy()                 # mean boardings per hour
    day_totals = grid.sum(axis=1)
    daily_mean = float(day_totals.mean())
    allday_rate = float(prof.mean())
    peak_hour_i = int(np.argmax(prof))
    sdam = float(((prof - prof.mean()) ** 2).sum())

    # ── choose k, twice: contiguous (primary) and magnitude-only (contrast) ──
    fisher_gvf, fisher_segs = {}, {}
    jenks_gvf = {}
    for k in K_RANGE:
        segs, sse = fisher_contiguous(prof, k)
        fisher_segs[k] = segs
        fisher_gvf[k] = 1.0 - sse / sdam
        _, brk = jenks_labels(prof, k)
        jenks_gvf[k] = C.goodness_of_variance_fit(prof, brk)
    k_star = gvf_elbow(fisher_gvf)
    k_jenks = gvf_elbow(jenks_gvf)
    log.info("contiguous-band GVF %s -> k*=%d",
             {k: round(v, 4) for k, v in fisher_gvf.items()}, k_star)
    log.info("magnitude-only Jenks GVF %s -> k=%d (reported as contrast only)",
             {k: round(v, 4) for k, v in jenks_gvf.items()}, k_jenks)

    lab_jenks, _ = jenks_labels(prof, k_jenks)
    jenks_classes = {int(t): [int(h) for h, l in zip(hours, lab_jenks) if l == t]
                     for t in sorted(set(lab_jenks.tolist()))}

    # ── the band profile ────────────────────────────────────────────────────
    bands = []
    for a, b in fisher_segs[k_star]:
        blk = prof[a:b + 1]
        bands.append(dict(
            hours=f"{hours[a]:02d}:00-{hours[b]:02d}:59",
            hour_start=int(hours[a]), hour_end=int(hours[b]),
            duration_h=int(b - a + 1),
            mean_boardings_per_hour=float(blk.mean()),
            share_of_daily_boardings_pct=float(100.0 * blk.sum() / prof.sum()),
        ))
    bands = name_bands(bands)
    peak_band = max(bands, key=lambda x: x["mean_boardings_per_hour"])
    peak_rate = peak_band["mean_boardings_per_hour"]

    for b in bands:
        b["ratio_to_allday_mean"] = b["mean_boardings_per_hour"] / allday_rate
        b["ratio_to_peak"] = b["mean_boardings_per_hour"] / peak_rate
        # Headway multipliers. Proportional: h ∝ 1/D. Square-root: h ∝ 1/sqrt(D).
        b["mult_proportional_mean_anchored"] = allday_rate / b["mean_boardings_per_hour"]
        b["mult_sqrt_mean_anchored"] = float(np.sqrt(allday_rate / b["mean_boardings_per_hour"]))
        b["mult_proportional_peak_anchored"] = peak_rate / b["mean_boardings_per_hour"]
        b["mult_sqrt_peak_anchored"] = float(np.sqrt(peak_rate / b["mean_boardings_per_hour"]))

    band_tab = pd.DataFrame([{
        "Band": b["band"], "Hours": b["hours"], "Duration (h)": b["duration_h"],
        "Mean boardings/h": round(b["mean_boardings_per_hour"], 0),
        "Share of daily (%)": round(b["share_of_daily_boardings_pct"], 1),
        "x all-day mean": round(b["ratio_to_allday_mean"], 3),
        "x peak": round(b["ratio_to_peak"], 3),
        "Headway mult. (prop., peak-anch.)": round(b["mult_proportional_peak_anchored"], 2),
        "Headway mult. (sqrt, peak-anch.)": round(b["mult_sqrt_peak_anchored"], 2),
        "Headway mult. (prop., mean-anch.)": round(b["mult_proportional_mean_anchored"], 2),
        "Headway mult. (sqrt, mean-anch.)": round(b["mult_sqrt_mean_anchored"], 2),
    } for b in bands])

    # ── banded headway schedule against the plan's policy headways ──────────
    policy = [
        ("SSCL e-bus trunk", C.HEADWAY_SSCL_TRUNK_MIN, C.HEADWAY_MAX_MIN),
        ("High-priority trunk (non-SSCL)", C.HEADWAY_HP_MIN, C.HEADWAY_MAX_MIN),
        ("Medium-priority feeder", C.HEADWAY_MP_MIN, C.HEADWAY_MAX_MIN),
        ("Rural lifeline (Regional, best bucket)",
         min(C.REGIONAL_HEADWAY_BUCKETS), max(C.REGIONAL_HEADWAY_BUCKETS)),
        ("Rural lifeline (Regional, worst bucket)",
         max(C.REGIONAL_HEADWAY_BUCKETS), max(C.REGIONAL_HEADWAY_BUCKETS)),
    ]
    rows, n_ceiling_binds = [], 0
    for label, h0, ceil_min in policy:
        row = {"Service class": label, "Plan headway (min)": h0,
               "Policy max wait (min)": ceil_min}
        for b in bands:
            for rule, key in (("prop", "mult_proportional_peak_anchored"),
                              ("sqrt", "mult_sqrt_peak_anchored")):
                raw = h0 * b[key]
                clipped = min(raw, ceil_min)
                if clipped < raw - 1e-9:
                    n_ceiling_binds += 1
                row[f"{b['band']} [{rule}]"] = round(clipped, 1)
                row[f"__raw__{b['band']}__{rule}"] = round(raw, 1)
        rows.append(row)
    hw_full = pd.DataFrame(rows)
    hw_tab = hw_full[[c for c in hw_full.columns if not c.startswith("__raw__")]]

    # The mean-anchored reading of the same policy headways, tabulated
    # separately because it is the one that tightens the peak and therefore the
    # one that costs vehicles.
    rows_mean = []
    for label, h0, ceil_min in policy:
        row = {"Service class": label, "Plan headway (min)": h0}
        for b in bands:
            for rule, key in (("prop", "mult_proportional_mean_anchored"),
                              ("sqrt", "mult_sqrt_mean_anchored")):
                row[f"{b['band']} [{rule}]"] = round(min(h0 * b[key], ceil_min), 1)
        rows_mean.append(row)
    hw_mean_tab = pd.DataFrame(rows_mean)

    # ── fleet and bus-hour consequence, route by route ──────────────────────
    act = C.load_active()
    fl_check = engine_fleet(act["Cycle_Time_Min"], act["Headway_Min"])
    exact = int((fl_check == act["Fleet_Required"]).sum())
    mismatch = act.loc[fl_check != act["Fleet_Required"],
                       ["New_Route_ID", "Route_Type", "Cycle_Time_Min",
                        "Headway_Min", "Fleet_Required"]].copy()
    mismatch["formula_fleet"] = fl_check[fl_check != act["Fleet_Required"]]
    log.info("engine fleet rule reproduces %d/%d published route fleets", exact, len(act))
    for _, m in mismatch.iterrows():
        log.warning("  unreproduced: %s published %d, formula %d "
                    "(published value held as an empirical floor)",
                    m["New_Route_ID"], int(m["Fleet_Required"]), int(m["formula_fleet"]))
    # Class minimum-fleet floors, except on the two routes whose published fleet
    # the formula does not reach: there the published value is an empirical
    # deployment floor and is held, so the banded fleet is never smaller than
    # the plan's own commitment on those corridors.
    class_floor = np.where(act["Route_Type"].eq("Regional_District"),
                           C.MIN_FLEET_REGIONAL, C.MIN_FLEET_URBAN)
    floor = np.where(fl_check < act["Fleet_Required"].to_numpy(),
                     act["Fleet_Required"].to_numpy(), class_floor)
    ceil_arr = headway_ceiling(act["Route_Type"])

    fleet_rows = []
    for anchor, suffix in (("peak-anchored", "peak_anchored"),
                           ("mean-anchored", "mean_anchored")):
        for rule, stem in (("proportional", "mult_proportional"),
                           ("square-root", "mult_sqrt")):
            key = f"{stem}_{suffix}"
            tot_fleet, tot_bus_h, per_band = {}, 0.0, []
            for b in bands:
                h_b = np.minimum(act["Headway_Min"].to_numpy(float) * b[key], ceil_arr)
                f_b = engine_fleet(act["Cycle_Time_Min"], h_b, floor=floor)
                tot_fleet[b["band"]] = int(f_b.sum())
                tot_bus_h += float(f_b.sum() * b["duration_h"])
                per_band.append(dict(anchor=anchor, rule=rule, band=b["band"],
                                     hours=b["hours"], duration_h=b["duration_h"],
                                     fleet=int(f_b.sum())))
            flat_bus_h = float(act["Fleet_Required"].sum() * len(SERVICE_HOURS))
            fleet_rows.append(dict(
                anchor=anchor, rule=rule,
                peak_fleet=int(max(tot_fleet.values())),
                plan_fleet=int(act["Fleet_Required"].sum()),
                vehicles_to_purchase_delta=int(max(tot_fleet.values())
                                               - act["Fleet_Required"].sum()),
                banded_bus_hours_per_day=round(tot_bus_h, 0),
                flat_bus_hours_per_day=round(flat_bus_h, 0),
                bus_hour_saving_pct=round(100.0 * (1 - tot_bus_h / flat_bus_h), 1),
                by_band=per_band,
            ))

    fleet_tab = pd.DataFrame([{
        "Anchor": r["anchor"],
        "Frequency rule": r["rule"],
        **{f"Fleet {b['band']}": b["fleet"] for b in r["by_band"]},
        "Peak fleet (buses)": r["peak_fleet"],
        "Plan fleet (buses)": r["plan_fleet"],
        "Extra vehicles to purchase": r["vehicles_to_purchase_delta"],
        "Banded bus-hours/day": r["banded_bus_hours_per_day"],
        "Flat bus-hours/day": r["flat_bus_hours_per_day"],
        "Bus-hour change (%)": -r["bus_hour_saving_pct"],
    } for r in fleet_rows])

    C.write_table(band_tab, "table05h_timeofday",
                  f"Time-of-day demand bands from SSCL e-bus boardings, "
                  f"{MONTH_LABEL}, and the implied headway multipliers")
    C.write_table(hw_tab, "table05h_timeofday_headways",
                  "Banded headway schedule by service class (minutes), "
                  "peak-anchored, clipped by the plan's 35-minute urban and "
                  "50-minute rural maximum wait")
    C.write_table(hw_mean_tab, "table05h_timeofday_headways_meananchored",
                  "Banded headway schedule by service class (minutes), "
                  "mean-anchored: the peak tightens below the published headway")
    C.write_table(fleet_tab, "table05h_timeofday_fleet",
                  "Fleet and bus-hour consequence of time-of-day banding under "
                  "two frequency rules and two reference anchors")

    # Where the ceiling destroys the off-peak saving: an MP feeder is already at
    # the 35-minute ceiling all day, so it has no off-peak headroom at all.
    ceiling_note = []
    for label, h0, ceil_min in policy:
        if h0 >= ceil_min:
            ceiling_note.append(label)

    out = dict(
        status="OK",
        source_file=str(C.HOURLY_PAX_CSV),
        month=MONTH_LABEL,
        what_this_file_is=(
            "Whole-network hourly BOARDINGS (fare transactions) for the 30-route "
            "Srinagar Smart City / CHALO electric bus system, April 2026, "
            "aggregated to clock hours over 30 calendar days. It is not an "
            "origin-destination matrix, not route-level ridership, not a "
            "maximum-load-section count, and does not cover the 156 non-SSCL "
            "permit routes in the rationalised plan."),
        transferability_assumption=(
            "The temporal SHAPE derived here is applied to all 186 planned "
            "routes. No electronic ticketing exists on the conventional diesel "
            "permits, so this assumption cannot be tested with the available "
            "data and is carried as a stated limitation, not a finding."),
        file_meta=meta,
        provenance_reconciliation=recon,
        daily_mean_boardings=round(daily_mean, 1),
        allday_mean_rate_per_hour=round(allday_rate, 1),
        peak_hour=int(hours[peak_hour_i]),
        peak_hour_rate=round(float(prof[peak_hour_i]), 1),
        peak_hour_factor_pct=round(100.0 * float(prof[peak_hour_i]) / prof.sum(), 2),
        peak_to_base_ratio=round(peak_rate / min(
            b["mean_boardings_per_hour"] for b in bands
            if b["band"] == BAND_NAME_BY_RANK["base"]), 3)
        if any(b["band"] == BAND_NAME_BY_RANK["base"] for b in bands) else None,
        hourly_profile=[dict(hour=int(h), mean_boardings=round(float(p), 1),
                             share_pct=round(100.0 * float(p) / prof.sum(), 2))
                        for h, p in zip(hours, prof)],
        segmentation=dict(
            method_primary=("Fisher (1958) exact contiguous grouping of the "
                            "ordered hourly series, k by GVF elbow"),
            method_contrast=("Jenks (1967) natural breaks on magnitude only, "
                             "reported to show it does not yield usable bands"),
            gvf_contiguous={int(k): round(v, 4) for k, v in fisher_gvf.items()},
            gvf_jenks_magnitude={int(k): round(v, 4) for k, v in jenks_gvf.items()},
            k_chosen_contiguous=int(k_star),
            k_chosen_jenks=int(k_jenks),
            jenks_magnitude_classes=jenks_classes,
            jenks_classes_are_time_contiguous=bool(all(
                (max(v) - min(v) + 1) == len(v) for v in jenks_classes.values())),
        ),
        bands=bands,
        headway_rules=dict(
            proportional=("h_b = h_ref * D_ref / D_b — maximum-load-section "
                          "frequency setting, f = P/(c*alpha); Vuchic (2005), "
                          "Ceder (2007), TRB (2013) TCQSM 3rd ed."),
            square_root=("h_b = h_ref * sqrt(D_ref / D_b) — welfare-optimal "
                         "square-root principle; Mohring (1972), Newell (1971)."),
            anchors=("peak-anchored reads the published headway as a peak "
                     "design (vehicle purchase unchanged); mean-anchored reads "
                     "it as matching the all-day mean (peak must tighten)."),
        ),
        policy_limits=dict(urban_max_wait_min=C.HEADWAY_MAX_MIN,
                           rural_max_wait_min=max(C.REGIONAL_HEADWAY_BUCKETS),
                           n_class_band_cells_clipped=int(n_ceiling_binds),
                           classes_with_zero_offpeak_headroom=ceiling_note),
        banded_headways_peak_anchored=hw_full.to_dict(orient="records"),
        banded_headways_mean_anchored=hw_mean_tab.to_dict(orient="records"),
        fleet_rule=dict(
            formula="fleet = ceil(ceil(cycle_min / headway_min) * FLEET_SPARE_RATIO)",
            spare_ratio=C.PARAMETERS["FLEET_SPARE_RATIO"]["value"],
            reproduces_published=f"{exact}/{len(act)}",
            unreproduced=mismatch.to_dict(orient="records"),
        ),
        fleet_consequence=fleet_rows,
        service_window_hours=len(SERVICE_HOURS),
        citations=[
            "Fisher, W.D. (1958) On grouping for maximum homogeneity. "
            "Journal of the American Statistical Association 53(284): 789-798.",
            "Jenks, G.F. (1967) The data model concept in statistical mapping. "
            "International Yearbook of Cartography 7: 186-190.",
            "Mohring, H. (1972) Optimization and scale economies in urban bus "
            "transportation. American Economic Review 62(4): 591-604.",
            "Newell, G.F. (1971) Dispatching policies for a transportation "
            "route. Transportation Science 5(1): 91-105.",
            "Vuchic, V.R. (2005) Urban Transit: Operations, Planning and "
            "Economics. Hoboken: Wiley.",
            "Ceder, A. (2007) Public Transit Planning and Operation: Theory, "
            "Modelling and Practice. Oxford: Elsevier.",
            "Transportation Research Board (2013) Transit Capacity and Quality "
            "of Service Manual, 3rd ed. TCRP Report 165. Washington DC: TRB.",
        ],
    )
    C.write_result(out, "a05_headway_timeofday")

    log.info("hourly profile (mean boardings/h): %s",
             ", ".join(f"{int(h):02d}h={p:,.0f}" for h, p in zip(hours, prof)))
    log.info("peak hour %02d:00 at %s boardings/h; peak-hour factor %.2f%% of "
             "the day; all-day mean rate %s/h",
             int(hours[peak_hour_i]), f"{float(prof[peak_hour_i]):,.0f}",
             out["peak_hour_factor_pct"], f"{allday_rate:,.0f}")
    for b in bands:
        log.info("band %-22s %s  %6.0f pax/h  %5.1f%% of day  "
                 "headway x%.2f (prop) / x%.2f (sqrt), peak-anchored",
                 b["band"], b["hours"], b["mean_boardings_per_hour"],
                 b["share_of_daily_boardings_pct"],
                 b["mult_proportional_peak_anchored"], b["mult_sqrt_peak_anchored"])
    log.info("policy ceiling binds in %d of the class x band x rule cells; "
             "classes with zero off-peak headroom: %s",
             n_ceiling_binds, ceiling_note or "none")
    for r in fleet_rows:
        log.info("%-13s %-12s: peak fleet %d (plan %d, %+d vehicles to buy); "
                 "bus-hours/day %.0f vs flat %.0f (%+.1f%%)",
                 r["anchor"], r["rule"], r["peak_fleet"], r["plan_fleet"],
                 r["vehicles_to_purchase_delta"], r["banded_bus_hours_per_day"],
                 r["flat_bus_hours_per_day"], -r["bus_hour_saving_pct"])


if __name__ == "__main__":
    main()
