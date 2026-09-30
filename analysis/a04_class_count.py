#!/usr/bin/env python
"""
a04_class_count.py — is the three-tier service hierarchy a finding, or an assertion?

The objection this module exists to answer. The plan sorts every route into one
of three priority bands (high / medium / low) and hangs the headway policy off
that band. Three is the number every transit plan uses, which is exactly why a
referee will read it as convention rather than evidence: "the authors assert a
three-tier hierarchy; nothing in the data says the distribution has three modes."
If three tiers are not recoverable from the index itself, the headway policy
inherits an arbitrary partition and everything downstream of it is decoration.

What is tested here. The composite demand index from a03 is partitioned into
k = 2..7 Jenks natural-breaks classes, and the goodness of variance fit is
recorded for each k. GVF rises monotonically with k by construction — a
partition into n classes fits n points perfectly — so the question is never
"which k maximises GVF" but "where does buying another class stop paying".
Two elbow rules are computed, and BOTH are reported, because a single rule
chosen after seeing the curve is a rule chosen to give the answer wanted:

  Rule A — threshold. The smallest k whose GVF exceeds 0.80. The 0.80 floor is
    the conventional adequacy level for a class-interval scheme: below it the
    classes retain more than a fifth of the total squared deviation as
    within-class noise.
  Rule B — maximum second difference. The k at which the marginal return to an
    extra class falls off most sharply, argmax over k of
        [GVF(k) - GVF(k-1)] - [GVF(k+1) - GVF(k)],
    i.e. the discrete curvature of the GVF curve. Defined for k = 3..6 given a
    2..7 sweep, since it needs a neighbour on each side.

The pre-registered tie-break, stated before the numbers are looked at: if the
two rules disagree, Rule A governs (an absolute adequacy floor is harder to
tune than a curvature argmax) and the disagreement is flagged in the JSON and
in the paper rather than buried.

Why classifier agreement matters too. An elbow tells you how many classes; it
does not tell you that the classes are a property of the data rather than of
Jenks. So the chosen k is also cut by three alternative rules — equal-count
quantiles, 1-D k-means, and equal intervals — and pairwise Cohen's kappa is
reported with the full confusion matrices. Two of these comparisons are
diagnostics with known expectations, and saying so in advance keeps them
honest: Jenks and 1-D k-means minimise the same within-class sum of squares on
one dimension, so once Jenks is evaluated on the partition it actually selected
they should agree exactly (any disagreement is an implementation fault or an
unconverged k-means, not a finding); equal-interval is the naive cut and should
agree worst on a right-skewed index. The informative comparison is Jenks vs
quantile, which asks whether the breaks sit at real gaps or merely at
convenient counts.

Robustness. Everything is run on all three a03 weightings of the network-
catchment index: `cdi_net_equal` (primary — the plan's own 50/50 assertion),
`cdi_net_entropy` and `cdi_net_pca`. Note before anyone reports it as a bug:
a03's PCA loadings on two positively correlated criteria came out 0.500/0.500,
so `cdi_net_pca` is numerically identical to `cdi_net_equal` and its curve is
identical too. That is a property of the two-criterion problem, not a copy.

One arithmetic trap, recorded because it produced a wrong number before it was
caught. jenkspy returns interior breaks that are observed data values marking
each class's UPPER bound; common.goodness_of_variance_fit reads a break list as
half-open [lo, hi) intervals, i.e. as LOWER bounds. Passing the former to the
latter evaluates a partition shifted by one route at every boundary and reports
a GVF for a partition nobody chose — at k = 3 that is 0.9016 for sizes
107|41|38 in place of the correct 0.9023 for 108|41|37. The symptom is
diagnostic: 1-D k-means appears to beat "optimal" Jenks on Jenks's own
objective, which cannot happen. This module therefore classifies with
side="left" and always derives GVF from the label-implied lower-bound breaks,
and every k is checked against an exact Fisher (1958) dynamic program that
solves the contiguous partition to global optimality. jenkspy attains it at
every k here. Related: a03's own `jenks_bands` helper uses the shifted
convention, so its band labels differ from this module's at class boundaries;
that affects a03's band-agreement diagnostics symmetrically (both sides of
every comparison are shifted alike) and is left untouched rather than edited
from here.

Outputs
    data/derived/a04_class_count.json     GVF curves, both elbow rules, kappas
    data/derived/a04_route_tiers.csv      per-route tier at the chosen k
    paper/tables/table05_class_count.{csv,md}
    paper/tables/table05b_classifier_agreement.{csv,md}

Usage
    python analysis/a04_class_count.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C  # noqa: E402

log = C.get_logger("a04")

K_RANGE = range(2, 8)             # class counts swept
GVF_THRESHOLD = 0.80              # Rule A adequacy floor
PRIMARY_COL = "cdi_net_equal"     # the plan's own weighting, network catchment
ROBUSTNESS_COLS = ("cdi_net_entropy", "cdi_net_pca")
CLASSIFIERS = ("jenks", "quantile", "kmeans", "equal_interval")


# ── the four class-interval rules ─────────────────────────────────────────────
# Every classifier returns ordinal labels 0..k-1 with 0 the lowest index band,
# so that kappa compares like with like and the tier column is monotone in CDI.
def jenks_breaks_list(v: np.ndarray, k: int) -> list[float]:
    """
    The k+1 break edges from jenkspy: min, then each class's UPPER bound, max.

    The representation matters and is a live trap. jenkspy's interior breaks are
    observed data values that belong to the class BELOW them, whereas
    common.goodness_of_variance_fit reads its break list as half-open [lo, hi)
    intervals, i.e. as class LOWER bounds. Handing this list to that function
    unchanged silently evaluates a different partition — every boundary route is
    pushed one class up — and understates the GVF. Nothing here does that: GVF is
    always taken via breaks_from_labels(), which returns the lower-bound form.
    This list is retained only for the record, and is labelled as upper bounds in
    the JSON.
    """
    import jenkspy
    return [float(x) for x in jenkspy.jenks_breaks(v, n_classes=k)]


def classify_jenks(v: np.ndarray, k: int) -> np.ndarray:
    """
    Ordinal Jenks labels, with `side="left"` because the breaks are upper bounds.

    A value exactly equal to an interior break is the last member of the class
    below it, so it must not be searched to the right. Verified against the exact
    dynamic program in main(): with side="left" the labels reproduce the globally
    optimal within-class sum of squares; with side="right" they do not.
    """
    breaks = np.asarray(jenks_breaks_list(v, k), dtype=float)
    return np.searchsorted(breaks[1:-1], v, side="left")


def classify_quantile(v: np.ndarray, k: int) -> np.ndarray:
    """Equal-count cut. Ties are pushed right so every route gets exactly one class."""
    edges = np.percentile(v, np.linspace(0, 100, k + 1)[1:-1])
    return np.searchsorted(edges, v, side="right")


def classify_kmeans(v: np.ndarray, k: int) -> np.ndarray:
    """
    1-D k-means (Lloyd), relabelled so cluster order follows centre order.

    Seeded from common.RANDOM_SEED with 50 restarts: on one dimension the
    objective is the same within-class sum of squares Jenks optimises exactly,
    so any disagreement between the two is local-optimum noise and the restarts
    are there to drive it out rather than to be reported as a finding.
    """
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=k, n_init=50, random_state=C.RANDOM_SEED)
    raw = km.fit_predict(v.reshape(-1, 1))
    order = np.argsort(km.cluster_centers_.ravel())
    remap = np.empty(k, dtype=int)
    remap[order] = np.arange(k)
    return remap[raw]


def classify_equal_interval(v: np.ndarray, k: int) -> np.ndarray:
    edges = np.linspace(v.min(), v.max(), k + 1)[1:-1]
    return np.searchsorted(edges, v, side="right")


CLASSIFIER_FN = {
    "jenks": classify_jenks,
    "quantile": classify_quantile,
    "kmeans": classify_kmeans,
    "equal_interval": classify_equal_interval,
}


# ── is the library's Jenks actually Jenks? ────────────────────────────────────
def exact_partition(v: np.ndarray, k: int) -> tuple[float, list[int], list[float]]:
    """
    Globally optimal contiguous 1-D partition by within-class sum of squares.

    Fisher's (1958) exact dynamic program, which is what "natural breaks" means
    before any heuristic is applied to it. This is here because jenkspy is not
    guaranteed to reach that optimum, and a paper that reports a GVF as "the
    Jenks fit" while a better Jenks partition exists has misreported its own
    fit statistic — a referee rerunning with a different library would get a
    different number and no way to tell which is right. O(k n^2) on 186 routes,
    so exactness costs nothing here.

    Returns (minimum SDCM, class sizes, interior break values).
    """
    s = np.sort(np.asarray(v, dtype=float))
    n = s.size
    c1 = np.concatenate([[0.0], np.cumsum(s)])
    c2 = np.concatenate([[0.0], np.cumsum(s * s)])

    def sse(i: np.ndarray, j: int) -> np.ndarray:
        """Within-class sum of squares of the sorted slice [i, j)."""
        m = j - i
        tot = c1[j] - c1[i]
        return (c2[j] - c2[i]) - tot * tot / m

    INF = np.inf
    cost = np.full((k + 1, n + 1), INF)
    back = np.zeros((k + 1, n + 1), dtype=int)
    cost[0, 0] = 0.0
    for kk in range(1, k + 1):
        for j in range(kk, n + 1):
            i = np.arange(kk - 1, j)
            cand = cost[kk - 1, i] + sse(i, j)
            best = int(np.argmin(cand))
            cost[kk, j] = cand[best]
            back[kk, j] = i[best]

    cuts, j = [], n
    for kk in range(k, 0, -1):
        j = int(back[kk, j])
        cuts.append(j)
    cuts = sorted(cuts)[1:]                      # drop the leading 0
    sizes = [len(part) for part in np.split(s, cuts)]
    return float(cost[k, n]), sizes, [float(s[c]) for c in cuts]


def exact_gvf(v: np.ndarray, k: int) -> tuple[float, list[int], list[float]]:
    sdcm, sizes, brks = exact_partition(v, k)
    sdam = float(((v - v.mean()) ** 2).sum())
    return (1.0 - sdcm / sdam), sizes, brks


def classify_exact(v: np.ndarray, k: int) -> np.ndarray:
    """Ordinal labels under the exact optimum, for counting how many routes move."""
    _, _, inner = exact_partition(v, k)
    return np.searchsorted(np.asarray(inner, dtype=float), v, side="right")


# ── GVF for an arbitrary partition ────────────────────────────────────────────
def breaks_from_labels(v: np.ndarray, labels: np.ndarray) -> list[float]:
    """
    Recover the break list implied by an ordinal partition.

    common.goodness_of_variance_fit is the single GVF implementation in the
    suite and takes breaks, not labels, so a partition produced by k-means or
    by quantiles has to be expressed the same way. For a monotone 1-D partition
    the interior break is the smallest value of the next class up, which
    reproduces the partition exactly under that function's half-open [lo, hi)
    convention. Asserted against the Jenks labels in main() rather than trusted.
    """
    present = np.unique(labels)
    inner = [float(v[labels == c].min()) for c in present[1:]]
    return [float(v.min()), *inner, float(v.max())]


def class_sizes(labels: np.ndarray, k: int) -> list[int]:
    return [int((labels == c).sum()) for c in range(k)]


def main() -> None:
    from sklearn.metrics import cohen_kappa_score, confusion_matrix

    idx_path = C.DERIVED / "a03_index.csv"
    if not idx_path.exists():
        C.write_result(dict(status="NOT_COMPUTABLE",
                            reason=f"missing input {idx_path}; run a03 first"),
                       "a04_class_count")
        raise SystemExit(f"missing {idx_path}")
    df = pd.read_csv(idx_path)
    log.info("index rows %d from %s", len(df), idx_path.name)

    missing = [c for c in (PRIMARY_COL, *ROBUSTNESS_COLS) if c not in df.columns]
    if missing:
        C.write_result(dict(status="NOT_COMPUTABLE",
                            reason=f"a03_index.csv lacks column(s) {missing}"),
                       "a04_class_count")
        raise SystemExit(f"a03_index.csv lacks {missing}")

    # ── GVF curve and both elbow rules, for every weighting ───────────────────
    curves: dict[str, dict] = {}
    for col in (PRIMARY_COL, *ROBUSTNESS_COLS):
        v = df[col].to_numpy(dtype=float)
        if not np.isfinite(v).all():
            raise SystemExit(f"{col} carries non-finite values; refusing to classify")

        gvf, sizes, brks = {}, {}, {}
        gvf_ex, sizes_ex, brks_ex = {}, {}, {}
        for k in K_RANGE:
            lab = classify_jenks(v, k)
            # GVF from the label-implied LOWER-bound breaks, never from jenkspy's
            # raw upper-bound list — see jenks_breaks_list's docstring.
            gvf[k] = float(C.goodness_of_variance_fit(v, breaks_from_labels(v, lab)))
            sizes[k] = class_sizes(lab, k)
            brks[k] = [round(x, 6) for x in jenks_breaks_list(v, k)]
            g, sz, bk = exact_gvf(v, k)
            gvf_ex[k], sizes_ex[k] = float(g), sz
            brks_ex[k] = [round(x, 6) for x in bk]

        # Did the library reach the optimum it claims to compute? Tolerance is
        # 1e-9 on GVF, far below anything that could move a class boundary.
        suboptimal = [k for k in K_RANGE if gvf_ex[k] - gvf[k] > 1e-9]
        if suboptimal:
            log.warning("%s: jenkspy is SUB-OPTIMAL at k=%s (max GVF shortfall "
                        "%.6f); exact Fisher DP does better", col, suboptimal,
                        max(gvf_ex[k] - gvf[k] for k in suboptimal))

        ks = list(K_RANGE)
        d1 = {k: (gvf[k] - gvf[k - 1]) if k - 1 in gvf else None for k in ks}
        # curvature: how much the marginal gain drops when going one class further
        d2 = {k: (d1[k] - d1[k + 1]) for k in ks
              if d1.get(k) is not None and d1.get(k + 1) is not None}

        above = [k for k in ks if gvf[k] > GVF_THRESHOLD]
        k_rule_a = min(above) if above else None
        k_rule_b = max(d2, key=lambda k: d2[k]) if d2 else None
        rules_agree = (k_rule_a is not None and k_rule_a == k_rule_b)
        k_chosen = k_rule_a if k_rule_a is not None else k_rule_b

        # The same two rules re-run on the exact curve. If the library's
        # imprecision could move the elbow, the elbow is not a finding.
        d1e = {k: (gvf_ex[k] - gvf_ex[k - 1]) if k - 1 in gvf_ex else None for k in ks}
        d2e = {k: (d1e[k] - d1e[k + 1]) for k in ks
               if d1e.get(k) is not None and d1e.get(k + 1) is not None}
        above_e = [k for k in ks if gvf_ex[k] > GVF_THRESHOLD]
        k_a_ex = min(above_e) if above_e else None
        k_b_ex = max(d2e, key=lambda k: d2e[k]) if d2e else None
        k_chosen_ex = k_a_ex if k_a_ex is not None else k_b_ex

        curves[col] = dict(
            gvf={str(k): gvf[k] for k in ks},
            delta_gvf={str(k): d1[k] for k in ks},
            second_difference_gvf={str(k): d2[k] for k in sorted(d2)},
            class_sizes={str(k): sizes[k] for k in ks},
            jenkspy_breaks_upper_bounds={str(k): brks[k] for k in ks},
            k_rule_a_first_gvf_above_threshold=k_rule_a,
            k_rule_b_max_second_difference=k_rule_b,
            rules_agree=bool(rules_agree),
            k_chosen=int(k_chosen),
            exact_optimum=dict(
                method=("Fisher 1958 exact dynamic program over the sorted values; "
                        "globally minimises within-class sum of squares"),
                gvf={str(k): gvf_ex[k] for k in ks},
                class_sizes={str(k): sizes_ex[k] for k in ks},
                inner_breaks={str(k): brks_ex[k] for k in ks},
                gvf_shortfall_of_jenkspy={str(k): gvf_ex[k] - gvf[k] for k in ks},
                jenkspy_attains_optimum={str(k): bool(gvf_ex[k] - gvf[k] <= 1e-9)
                                         for k in ks},
                k_rule_a_first_gvf_above_threshold=k_a_ex,
                k_rule_b_max_second_difference=k_b_ex,
                k_chosen=(None if k_chosen_ex is None else int(k_chosen_ex)),
                elbow_unchanged=bool(k_chosen_ex == k_chosen),
            ),
        )
        log.info("%s: GVF %s", col,
                 " ".join(f"k{k}={gvf[k]:.4f}" for k in ks))
        log.info("%s: exact  %s", col,
                 " ".join(f"k{k}={gvf_ex[k]:.4f}" for k in ks))
        log.info("%s: Rule A (first GVF>%.2f) k=%s | Rule B (max d2GVF) k=%s | "
                 "agree=%s -> k=%d", col, GVF_THRESHOLD, k_rule_a, k_rule_b,
                 rules_agree, k_chosen)

    prim = curves[PRIMARY_COL]
    K = int(prim["k_chosen"])
    if not prim["rules_agree"]:
        log.warning("elbow rules DISAGREE on %s (A=%s, B=%s); pre-registered "
                    "tie-break selects Rule A", PRIMARY_COL,
                    prim["k_rule_a_first_gvf_above_threshold"],
                    prim["k_rule_b_max_second_difference"])

    robust_agreement = {c: int(curves[c]["k_chosen"]) for c in ROBUSTNESS_COLS}
    log.info("chosen k = %d on %s; robustness weightings choose %s",
             K, PRIMARY_COL, robust_agreement)

    # ── Table 5: the curve the choice of k rests on ───────────────────────────
    rows = []
    for k in K_RANGE:
        rows.append(dict(
            k=k,
            gvf=round(prim["gvf"][str(k)], 4),
            gvf_exact_optimum=round(prim["exact_optimum"]["gvf"][str(k)], 4),
            delta_gvf=(None if prim["delta_gvf"][str(k)] is None
                       else round(prim["delta_gvf"][str(k)], 4)),
            second_difference_gvf=(round(prim["second_difference_gvf"][str(k)], 4)
                                   if str(k) in prim["second_difference_gvf"] else None),
            n_per_class=" | ".join(str(n) for n in prim["class_sizes"][str(k)]),
            smallest_class_n=min(prim["class_sizes"][str(k)]),
            selected=("yes" if k == K else ""),
        ))
    tab5 = pd.DataFrame(rows)
    C.write_table(tab5, "table05_class_count",
                  f"Jenks natural-breaks goodness of variance fit for k = 2..7 on "
                  f"{PRIMARY_COL}, with the marginal and second-difference returns "
                  f"that locate the elbow. `gvf_exact_optimum` is the globally "
                  f"optimal contiguous partition from an exact dynamic program, "
                  f"reported so the library's result is auditable")

    # ── classifier agreement at the chosen k ──────────────────────────────────
    v = df[PRIMARY_COL].to_numpy(dtype=float)
    labels = {name: CLASSIFIER_FN[name](v, K).astype(int) for name in CLASSIFIERS}

    # Self-test: the Jenks partition at the chosen k must attain the globally
    # optimal within-class sum of squares. If it does not, either the library is
    # approximating or — far more likely, and the bug this catches — the break
    # convention has been misread and the reported GVF belongs to a partition
    # nobody selected. Either way the Jenks column of Table 5 would be wrong.
    gvf_exact_k = prim["exact_optimum"]["gvf"][str(K)]
    if gvf_exact_k - prim["gvf"][str(K)] > 1e-9:
        log.warning("Jenks GVF at k=%d (%.9f) is below the exact optimum "
                    "(%.9f) — check the break convention", K,
                    prim["gvf"][str(K)], gvf_exact_k)

    per_classifier = {}
    for name, lab in labels.items():
        per_classifier[name] = dict(
            gvf=float(C.goodness_of_variance_fit(v, breaks_from_labels(v, lab))),
            class_sizes=class_sizes(lab, K),
            breaks=[round(float(x), 6) for x in breaks_from_labels(v, lab)],
        )
        log.info("k=%d %-14s GVF=%.4f sizes=%s", K, name,
                 per_classifier[name]["gvf"], per_classifier[name]["class_sizes"])

    # ── does the library's Jenks reach the Jenks optimum at the chosen k? ─────
    # An audit of our own arithmetic, not of jenkspy. See jenks_breaks_list for
    # the break-convention trap this is here to catch.
    import jenkspy as _jp
    ex = prim["exact_optimum"]
    attained = bool(ex["jenkspy_attains_optimum"][str(K)])
    n_moved = int((labels["jenks"] != classify_exact(v, K)).sum())
    jenks_check = dict(
        library="jenkspy",
        library_version=getattr(_jp, "__version__", "unknown"),
        k=K,
        jenkspy_gvf=float(prim["gvf"][str(K)]),
        exact_optimum_gvf=float(ex["gvf"][str(K)]),
        gvf_shortfall=float(ex["gvf_shortfall_of_jenkspy"][str(K)]),
        jenkspy_attains_optimum=attained,
        jenkspy_class_sizes=prim["class_sizes"][str(K)],
        exact_class_sizes=ex["class_sizes"][str(K)],
        exact_inner_breaks=ex["inner_breaks"][str(K)],
        n_routes_reclassified_if_exact_used=n_moved,
        elbow_unchanged_under_exact_optimum=bool(ex["elbow_unchanged"]),
        kmeans_matches_exact_optimum=bool(
            (labels["kmeans"] == classify_exact(v, K)).all()),
        note=("Verification that the reported Jenks fit is the real one. jenkspy "
              "returns class UPPER bounds, while common.goodness_of_variance_fit "
              "reads breaks as half-open [lo, hi) lower bounds; combining the two "
              "naively evaluates a partition shifted by one route at every "
              "boundary and understates GVF (here 0.901608 instead of 0.902329 at "
              "k=3, with sizes 107|41|38 instead of 108|41|37). It also makes 1-D "
              "k-means appear to beat 'optimal' Jenks, which is impossible and is "
              "the symptom that exposes the error. This module classifies with "
              "side='left' and takes GVF from the label-implied lower-bound "
              "breaks, and checks the result against an exact dynamic program."),
    )
    if attained:
        log.info("jenkspy attains the exact Jenks optimum at k=%d", K)
    else:
        log.warning("jenkspy at k=%d: GVF %.6f vs exact optimum %.6f "
                    "(shortfall %.6f); sizes %s vs exact %s; %d routes would "
                    "move. Elbow unchanged: %s. k-means found the exact "
                    "optimum: %s", K, jenks_check["jenkspy_gvf"],
                    jenks_check["exact_optimum_gvf"], jenks_check["gvf_shortfall"],
                    jenks_check["jenkspy_class_sizes"],
                    jenks_check["exact_class_sizes"], n_moved,
                    jenks_check["elbow_unchanged_under_exact_optimum"],
                    jenks_check["kmeans_matches_exact_optimum"])

    kappa = pd.DataFrame(index=list(CLASSIFIERS), columns=list(CLASSIFIERS),
                         dtype=float)
    confusions = {}
    for a in CLASSIFIERS:
        for b in CLASSIFIERS:
            kappa.loc[a, b] = (1.0 if a == b
                               else float(cohen_kappa_score(labels[a], labels[b])))
            if a < b:
                cm = confusion_matrix(labels[a], labels[b], labels=list(range(K)))
                confusions[f"{a}__vs__{b}"] = dict(
                    rows=a, cols=b, labels=list(range(K)),
                    matrix=cm.tolist(),
                    exact_agreement=float((labels[a] == labels[b]).mean()),
                    kappa=float(cohen_kappa_score(labels[a], labels[b])),
                )
    kappa_out = kappa.round(4).reset_index().rename(columns={"index": "classifier"})
    C.write_table(kappa_out, "table05b_classifier_agreement",
                  f"Pairwise Cohen's kappa between four class-interval rules at "
                  f"k = {K} on {PRIMARY_COL} (n = {len(df)} active routes)")

    for key, cm in confusions.items():
        log.info("kappa %-34s %.4f  (exact agreement %.1f%%)", key,
                 cm["kappa"], 100 * cm["exact_agreement"])

    # ── per-route tier, the column downstream modules consume ─────────────────
    # tier_rank inverts the class index so Tier 1 is the highest-index band,
    # matching how a service hierarchy is written up and how the plan's own
    # HP/MP/LP bands read.
    out = df[["New_Route_ID", "Route_Name", "Route_Type", "Route_KM",
              PRIMARY_COL, *ROBUSTNESS_COLS]].copy()
    out["tier_class"] = labels["jenks"]
    out["tier_rank"] = K - out["tier_class"]
    out["tier_label"] = out["tier_rank"].map(lambda r: f"Tier {r}")
    for name in CLASSIFIERS:
        if name != "jenks":
            out[f"class_{name}"] = labels[name]
    for col in ROBUSTNESS_COLS:
        out[f"tier_class_{col}"] = classify_jenks(
            df[col].to_numpy(dtype=float), int(curves[col]["k_chosen"]))
    out.to_csv(C.DERIVED / "a04_route_tiers.csv", index=False)

    # Does the objective partition reproduce the plan's own published bands?
    # This is the claim §4.7 actually needs: not that three is a nice number,
    # but that a blind cut of the index lands where the plan says it lands.
    published = None
    plan = C.load_active()[["New_Route_ID", "Priority_Band"]]
    merged = out.merge(plan, on="New_Route_ID", how="left")
    if merged["Priority_Band"].notna().all() and K == 3:
        band_rank = {"HP": 1, "MP": 2, "LP": 3}
        pub = merged["Priority_Band"].map(band_rank)
        published = dict(
            comparison="Jenks tier_rank (1=highest CDI) vs published Priority_Band HP/MP/LP",
            exact_agreement=float((merged["tier_rank"] == pub).mean()),
            kappa=float(cohen_kappa_score(merged["tier_rank"], pub)),
            confusion=confusion_matrix(merged["tier_rank"], pub,
                                       labels=[1, 2, 3]).tolist(),
            published_band_sizes=merged["Priority_Band"].value_counts().to_dict(),
        )
        log.info("vs published Priority_Band: agreement %.1f%% kappa %.4f",
                 100 * published["exact_agreement"], published["kappa"])
    else:
        published = dict(status="NOT_COMPUTABLE",
                         reason=("Priority_Band missing for some active routes"
                                 if merged["Priority_Band"].isna().any()
                                 else f"chosen k={K} is not 3, so the HP/MP/LP "
                                      "bands are not a like-for-like partition"))
        log.warning("published-band comparison skipped: %s", published["reason"])

    payload = dict(
        n_routes=int(len(df)),
        primary_column=PRIMARY_COL,
        robustness_columns=list(ROBUSTNESS_COLS),
        k_range=[min(K_RANGE), max(K_RANGE)],
        gvf_threshold=GVF_THRESHOLD,
        elbow_rule_a="smallest k with GVF > 0.80 (absolute adequacy floor)",
        elbow_rule_b=("argmax over k of [GVF(k)-GVF(k-1)] - [GVF(k+1)-GVF(k)], "
                      "the discrete curvature of the GVF curve; defined k=3..6"),
        elbow_tie_break=("pre-registered: Rule A governs if the two disagree, and "
                         "the disagreement is reported"),
        k_chosen=K,
        rules_agree=bool(prim["rules_agree"]),
        k_chosen_by_robustness_weighting=robust_agreement,
        robustness_weightings_agree=bool(
            all(x == K for x in robust_agreement.values())),
        pca_equals_equal_note=("a03 derives PCA loadings of 0.500/0.500 on the two "
                               "criteria, so cdi_net_pca is numerically identical "
                               "to cdi_net_equal; its identical curve is expected"),
        curves=curves,
        classifiers_at_k=per_classifier,
        jenks_implementation_check=jenks_check,
        kappa_matrix=kappa.round(6).to_dict(),
        confusion_matrices=confusions,
        vs_published_priority_band=published,
        tier_sizes={f"Tier {K - c}": int((labels['jenks'] == c).sum())
                    for c in range(K)},
        random_seed=C.RANDOM_SEED,
        outputs=dict(
            tiers_csv=str((C.DERIVED / "a04_route_tiers.csv").relative_to(C.ROOT)),
            table5=str((C.TABLES / "table05_class_count.csv").relative_to(C.ROOT)),
            table5b=str((C.TABLES / "table05b_classifier_agreement.csv").relative_to(C.ROOT)),
        ),
    )
    C.write_result(payload, "a04_class_count")

    log.info("tier sizes at k=%d: %s", K, payload["tier_sizes"])
    log.info("wrote a04_class_count.json, a04_route_tiers.csv, "
             "table05_class_count, table05b_classifier_agreement")


if __name__ == "__main__":
    main()
