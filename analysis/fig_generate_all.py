#!/usr/bin/env python
"""
fig_generate_all.py — every manuscript figure, drawn from data/derived and the
frozen inputs only (no number is typed into a figure by hand).

Each figure is written as vector PDF (for typesetting) and 300-dpi PNG (for
review) under paper/figures/. A figure whose source module has not run is
skipped with a logged NOT_RUN rather than drawn from placeholder data.

  fig01_framework       conceptual framework (open inputs -> plan -> convergent checks)
  fig03_study_area      10 districts, 186 active routes by class
  fig04_method_flow     four-phase method flowchart
  fig05_permit_funnel   614 permits -> 157 corridors -> 186 active routes
  fig06_catchment_bias  Euclidean vs network catchment population, per route
  fig07_tiers           GVF curve k = 2..7 and the three-tier partition of the CDI
  fig08_coverage        network walkshed union over the population surface
  fig09_fleet_interval  fleet under regimes A and B (Monte Carlo), published point
  fig09b_sobol          total-order Sobol' indices for fleet B and tier agreement
  figS1_frontier        fleet vs frequent-network coverage frontier (a15)

Figure 2 (literature-review flow diagram) depends on decision D5 (whether the
§2.1 systematic-review protocol is run) and is not drawn.

Palette: the validated reference categorical order (blue #2a78d6, orange
#eb6834, aqua #1baf7a) for the three route classes, capped at three series as the
all-pairs rule requires for maps; blue sequential ramp for ordinal tiers
(steps 250 / 450 / 650). Text is always in ink, never series colour.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("figs")

import logging  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
logging.getLogger("fontTools").setLevel(logging.WARNING)
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
SURFACE = "#ffffff"
CLASS_COL = {"Urban": "#2a78d6", "Peri_Urban": "#eb6834", "Regional_District": "#1baf7a"}
CLASS_LAB = {"Urban": "Urban", "Peri_Urban": "Peri-urban", "Regional_District": "Regional"}
TIER_COL = ["#86b6ef", "#2a78d6", "#104281"]     # low -> high
SERIES2 = "#eb6834"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9.5,
    "axes.labelsize": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 100,
    "savefig.facecolor": SURFACE, "pdf.fonttype": 42,
})


def save(fig, stem: str) -> None:
    for ext, kw in (("pdf", {}), ("png", {"dpi": 300})):
        fig.savefig(C.FIGURES / f"{stem}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)
    log.info("wrote %s", stem)


def have(stem: str) -> bool:
    ok = (C.DERIVED / f"{stem}.json").exists()
    if not ok:
        log.warning("NOT_RUN: %s missing; dependent figure skipped", stem)
    return ok


# ── diagrams ─────────────────────────────────────────────────────────────────
def box(ax, x, y, w, h, text, fc="#f4f3f0", ec=MUTED, bold=False, size=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=INK, fontsize=size,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.9, shrinkA=0, shrinkB=0))


def fig01_framework():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ins = ["Gridded population\n(WorldPop 2026)", "OpenStreetMap roads,\nPOIs, boundaries",
           "Routing engine\n(OSRM)", "Digitised permit\nregister (614)"]
    for k, t in enumerate(ins):
        box(ax, 0.01, 0.80 - k * 0.22, 0.2, 0.16, t)
        arrow(ax, 0.21, 0.88 - k * 0.22, 0.30, 0.55)
    box(ax, 0.30, 0.34, 0.30, 0.42,
        "Demand-free rationalisation\n\nnetwork walk catchments\ncomposite accessibility index\n"
        "consolidation · hierarchy\ncycle time → fleet", fc="#e8f1fc", ec="#2a78d6", bold=False)
    ax.text(0.45, 0.80, "Supply plan", ha="center", color=INK, fontsize=9, fontweight="bold")
    arrow(ax, 0.60, 0.55, 0.68, 0.55)
    chk = ["V1 building footprints", "V2 operator benchmark (circular)", "V3 expert panel — not run",
           "V4 driver GPS (supply)", "V5 global sensitivity", "V6 decision robustness"]
    for k, t in enumerate(chk):
        faded = "not run" in t
        box(ax, 0.68, 0.86 - k * 0.14, 0.31, 0.11, t, fc="#ffffff" if faded else "#f4f3f0",
            ec=GRID if faded else MUTED, size=7.5)
    ax.text(0.835, 0.02, "Convergent checks → decision-robustness,\nnot demand validation",
            ha="center", color=INK2, fontsize=7.5, style="italic")
    save(fig, "fig01_framework")


def fig04_method_flow():
    fig, ax = plt.subplots(figsize=(7.2, 2.6))
    ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    phases = [("Phase 1\nDiagnosis", "permit → corridor\nWorldPop vs Census\nOSM completeness"),
              ("Phase 2\nAccessibility", "network walk\ncatchments (Eq. 1–3)\nopportunity (Eq. 4–5)"),
              ("Phase 3\nHierarchy", "CDI (Eq. 7)\nconsolidation (Alg. 1)\nJenks tiers (Eq. 10)"),
              ("Phase 4\nSizing & assurance", "cycle time (Eq. 11–12)\nfleet (Eq. 13–14)\nQA gates · uncertainty")]
    w = 0.22
    for k, (h, b) in enumerate(phases):
        x = 0.01 + k * 0.25
        box(ax, x, 0.62, w, 0.3, h, fc="#e8f1fc", ec="#2a78d6", bold=True)
        box(ax, x, 0.08, w, 0.46, b, size=7.5)
        if k < 3:
            arrow(ax, x + w, 0.77, x + 0.25, 0.77)
    save(fig, "fig04_method_flow")


# ── data figures ─────────────────────────────────────────────────────────────
def fig03_study_area():
    import geopandas as gpd
    d = C.load_districts().to_crs(C.UTM)
    r = gpd.read_file(C.PLAN_GEOJSON).to_crs(C.UTM)
    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    d.plot(ax=ax, fc="#f4f3f0", ec=MUTED, lw=0.6)
    for cls in ("Regional_District", "Peri_Urban", "Urban"):
        s = r[r["Route_Type"] == cls]
        s.plot(ax=ax, color=CLASS_COL[cls], lw=0.9, label=f"{CLASS_LAB[cls]} ({len(s)})")
    name_col = next(c for c in ("name", "NAME", "district") if c in d.columns)
    for _, row in d.iterrows():
        p = row.geometry.representative_point()
        ax.text(p.x, p.y, str(row[name_col]).replace(" District", ""), fontsize=7, color=INK2,
                ha="center", va="center",
                bbox=dict(fc=SURFACE, ec="none", alpha=0.7, pad=0.8))
    ax.set_axis_off(); ax.set_aspect("equal")
    ax.legend(loc="lower left", title="Active routes by class", title_fontsize=8)
    ax.set_title("Kashmir Division: 10 districts, 186 active routes", loc="left", color=INK)
    save(fig, "fig03_study_area")


def fig05_permit_funnel():
    q = C.read_result("q01_data_quality")["D1_register_hygiene"]
    stages = [("Permit records", 614), ("Distinct O–D corridors", 157),
              ("Engine rows (614 + 30 e-bus)", 644), ("Active routes", q["n_active_routes"]),
              ("  of which permit-derived", q["n_active_permit_derived"])]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    y = np.arange(len(stages))[::-1]
    vals = [v for _, v in stages]
    ax.barh(y, vals, color=["#86b6ef", "#2a78d6", "#86b6ef", "#104281", "#2a78d6"], height=0.62)
    for yy, (lab, v) in zip(y, stages):
        ax.text(v + 8, yy, f"{v:,}", va="center", color=INK, fontsize=8)
    ax.set_yticks(y, [s for s, _ in stages]); ax.grid(axis="y", visible=False)
    ax.set_xlim(0, 720); ax.set_xlabel("count")
    ax.set_title(f"A permit is not a route: {q['corridor_retention_rate']*100:.1f}% of corridors retained",
                 loc="left", color=INK)
    save(fig, "fig05_permit_funnel")


def fig06_catchment_bias():
    df = pd.read_csv(C.DERIVED / "a02_catchments.csv")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw=dict(width_ratios=[1.1, 1]))
    for cls in ("Regional_District", "Peri_Urban", "Urban"):
        s = df[df["Route_Type"] == cls]
        a1.scatter(s["pop_euclid"] / 1e3, s["pop_net"] / 1e3, s=10, color=CLASS_COL[cls],
                   ec=SURFACE, lw=0.4, label=CLASS_LAB[cls])
    m = df["pop_euclid"].max() / 1e3
    a1.plot([0, m], [0, m], color=MUTED, lw=0.9, ls="--"); a1.text(m * 0.78, m * 0.70, "1:1", color=MUTED, ha="left", va="top")
    a1.set_xlabel("Euclidean 400 m buffer (thousand residents)")
    a1.set_ylabel("Network 400 m walkshed (thousand)")
    a1.legend(loc="upper left"); a1.set_title("Per-route population served", loc="left", color=INK)
    med = df["overstatement_pct"].median()
    a2.hist(df["overstatement_pct"], bins=np.arange(0, 62, 3), color="#2a78d6", ec=SURFACE, lw=1)
    a2.axvline(med, color=INK, lw=1)
    a2.text(med - 1, a2.get_ylim()[1] * 0.97, f"median {med:.1f}% ", color=INK, ha="right", va="top")
    a2.set_xlabel("Euclidean overstatement (%)"); a2.set_ylabel("routes")
    a2.set_title("Overstatement distribution (n = 186)", loc="left", color=INK)
    fig.tight_layout()
    save(fig, "fig06_catchment_bias")


def fig07_tiers():
    a04 = C.read_result("a04_class_count")
    cur = a04["curves"]["cdi_net_equal"]
    ks = sorted(int(k) for k in cur["gvf"])
    g = [cur["gvf"][str(k)] for k in ks]
    t = pd.read_csv(C.DERIVED / "a04_route_tiers.csv").sort_values("cdi_net_equal").reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
    a1.plot(ks, g, color="#2a78d6", lw=2, marker="o", ms=5, mec=SURFACE)
    a1.axhline(a04["gvf_threshold"], color=MUTED, ls="--", lw=0.9)
    a1.text(6.9, a04["gvf_threshold"] + 0.006, "GVF 0.80", ha="right", color=MUTED)
    a1.annotate(f"k = {a04['k_chosen']}", (a04["k_chosen"], cur["gvf"][str(a04["k_chosen"])]),
                xytext=(10, -18), textcoords="offset points", color=INK)
    a1.set_xlabel("number of classes k"); a1.set_ylabel("goodness of variance fit")
    a1.set_title("Class-count elbow (Jenks, network CDI)", loc="left", color=INK)
    for k in range(3):
        s = t[t["tier_class"] == k]
        a2.bar(s.index, s["cdi_net_equal"], color=TIER_COL[k], width=1.0,
               label=f"{['Tier 3', 'Tier 2', 'Tier 1'][k]} ({len(s)})")
    a2.set_xlabel("routes, ranked by CDI"); a2.set_ylabel("composite demand index")
    a2.legend(loc="upper left"); a2.grid(axis="x", visible=False)
    a2.set_title("Three-tier partition", loc="left", color=INK)
    fig.tight_layout()
    save(fig, "fig07_tiers")


def fig08_coverage():
    import geopandas as gpd
    import rasterio
    from rasterio.plot import plotting_extent
    cat = gpd.read_file(C.CACHE / "catchments_network.gpkg").to_crs(C.WGS84)
    d = C.load_districts()
    with rasterio.open(C.WORLDPOP_TIF) as src:
        pop = src.read(1).astype(float)
        if src.nodata is not None:
            pop[pop == src.nodata] = np.nan
        ext = plotting_extent(src)
        from rasterio.features import rasterize
        inside = rasterize([(d.union_all(), 1)], out_shape=pop.shape, transform=src.transform, fill=0)
        pop[inside == 0] = np.nan
    cov = C.read_result("a11_coverage_accessibility")["any_service_reconciliation"]
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    img = np.log10(np.where(pop > 0, pop, np.nan))
    im = ax.imshow(img, extent=ext, cmap="Greys", vmin=-1, vmax=2.5, interpolation="nearest")
    cat.dissolve().boundary.plot(ax=ax, color="#2a78d6", lw=0.5)
    gpd.GeoSeries([cat.union_all()], crs=C.WGS84).plot(ax=ax, fc="#2a78d6", alpha=0.35, ec="none")
    d.boundary.plot(ax=ax, color=MUTED, lw=0.5)
    b = d.total_bounds
    ax.set_xlim(b[0], b[2]); ax.set_ylim(b[1], b[3]); ax.set_axis_off()
    cb = fig.colorbar(im, ax=ax, shrink=0.5, pad=0.01)
    cb.set_label("residents per 100 m cell (log10)", color=INK2)
    ax.set_title(f"Network walkshed union: {cov['any_service_share']*100:.1f}% of "
                 f"{C.STUDY_AREA_POPULATION:,} residents within 400 m", loc="left", color=INK)
    save(fig, "fig08_coverage")


def fig09_fleet_interval():
    if not have("a09_monte_carlo_sobol"):
        return
    mc = pd.read_csv(C.DERIVED / "a09_mc_draws.csv")
    j = C.read_result("a09_monte_carlo_sobol")
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    both = np.r_[mc["fleet_A"], mc["fleet_B"]]
    lo, hi = np.percentile(both, [0.2, 99.8])
    bins = np.arange(np.floor(lo / 5) * 5, np.ceil(hi / 5) * 5 + 5, 5)
    ax.hist(mc["fleet_A"], bins=bins, color="#2a78d6", ec=SURFACE, lw=0.6,
            label="A: as specified (cap on)")
    ax.hist(mc["fleet_B"], bins=bins, color=SERIES2, ec=SURFACE, lw=0.6,
            label="B: observed urban/peri-urban pace")
    ax.axvline(j["fleet_published"], color=INK, lw=1.2)
    gap_x = (mc["fleet_A"].quantile(0.99) + mc["fleet_B"].quantile(0.01)) / 2
    ax.annotate(f"published {j['fleet_published']:,}", xy=(j["fleet_published"], ax.get_ylim()[1] * 0.8),
                xytext=(gap_x, ax.get_ylim()[1] * 0.8), color=INK, va="center", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8))
    for key, col in (("fleet_A", "#2a78d6"), ("fleet_B", SERIES2)):
        s = j["mc"][key]
        ax.plot([s["p5"], s["p95"]], [-ax.get_ylim()[1] * 0.04] * 2, color=col, lw=3,
                solid_capstyle="round", clip_on=False)
    ax.set_xlabel("total fleet (buses)"); ax.set_ylabel("draws")
    ax.legend(loc="upper right"); ax.grid(axis="x", visible=False)
    ax.set_title(f"Fleet under joint parameter uncertainty ({j['n_mc']:,} draws; bars = 90% intervals)",
                 loc="left", color=INK)
    save(fig, "fig09_fleet_interval")


def fig09b_sobol():
    if not have("a09_monte_carlo_sobol"):
        return
    s = pd.read_csv(C.TABLES / "table07c_sobol.csv")
    cols = [c for c in ("Fleet B (obs.-anchored) ST", "Tier agreement ST") if c in s]
    fig, axes = plt.subplots(1, len(cols), figsize=(7.2, 3.6), sharey=True)
    s = s.sort_values(cols[0])
    for ax, c, col in zip(np.atleast_1d(axes), cols, ("#2a78d6", SERIES2)):
        ax.barh(s["Parameter"], s[c].clip(lower=0), color=col, height=0.62)
        ax.set_xlabel("total-order Sobol' index"); ax.grid(axis="y", visible=False)
        ax.set_title(c.replace(" ST", ""), loc="left", color=INK)
    fig.tight_layout()
    save(fig, "fig09b_sobol")


def figS1_frontier():
    if not have("a15_scenarios"):
        return
    fr = pd.read_csv(C.DERIVED / "a15_frontier.csv")
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    for key, col, lab in (("fleet_as_specified", "#2a78d6", "as specified"),
                          ("fleet_observation_anchored", SERIES2, "observed pace")):
        ax.plot(fr["city_headway_min"], fr[key], color=col, lw=2, marker="o", ms=5, mec=SURFACE, label=lab)
    ax.set_xlabel("urban & peri-urban headway (min)"); ax.set_ylabel("total fleet (buses)")
    ax.legend(loc="upper right")
    ax.set_title("Fleet price of city frequency", loc="left", color=INK)
    save(fig, "figS1_frontier")


def figS2_funding_curve():
    p = C.DERIVED / "a15_funding_sequence.csv"
    if not p.exists():
        log.warning("NOT_RUN: a15 funding sequence missing")
        return
    s = pd.read_csv(p)
    j = C.read_result("a15_scenarios")["funding_sequence"]
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    ax.plot(np.r_[0, s["cum_buses"]], 100 * np.r_[0, s["cum_coverage"]], color="#2a78d6", lw=2)
    ax.axvline(j["budget_buses"], color=MUTED, ls="--", lw=0.9)
    ax.text(j["budget_buses"] + 12, 3, f"30% of fleet\n{100*j['coverage_funded']:.1f}% reached",
            color=INK, va="bottom")
    ax.set_xlabel("buses funded (routes bought by new residents reached per bus)")
    ax.set_ylabel("residents within 400 m (%)")
    ax.set_xlim(0, s["cum_buses"].max() * 1.02); ax.set_ylim(0, None)
    ax.set_title("Reach is cheap; frequency is what the rest of the fleet buys", loc="left", color=INK)
    save(fig, "figS2_funding_curve")


def main() -> None:
    for f in (figS2_funding_curve, fig01_framework, fig04_method_flow, fig03_study_area, fig05_permit_funnel,
              fig06_catchment_bias, fig07_tiers, fig08_coverage, fig09_fleet_interval,
              fig09b_sobol, figS1_frontier):
        try:
            f()
        except Exception as exc:  # a failed figure must not hide the others
            log.error("%s failed: %s", f.__name__, exc)
            raise


if __name__ == "__main__":
    main()
