"""Merge full-text recoding into Table 1, compute the Section 2.8 cross-tab and draw Figure 2.
Run from lit_review/:  python finalise_table1.py
Outputs: table1_final.csv, crosstab_intensity_plan.csv, table1_summary.json, fig02_gap_heatmap.(png|pdf)
"""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

RUBRIC_COLS = ["geography", "region_class", "planning_stage", "method_family", "demand_input", "data_intensity",
               "equity", "validation", "implementable_plan", "code_released", "basis", "note"]
PLAN = ["Yes", "Partial", "No"]
LEVELS = [1, 2, 3, 4, 5]
LEVEL_LABEL = {1: "1  Open data only", 2: "2  + official static data", 3: "3  + partial observations",
               4: "4  + full demand matrix", 5: "5  + passive ridership (AFC/APC)"}

t = pd.read_csv("table1_coded_draft.csv", dtype=str)
try:
    ft = pd.read_csv("coding/coded_fulltext_23.csv", dtype=str)
    t = t.set_index("cid")
    ft = ft.set_index("cid")
    for c in RUBRIC_COLS:
        t.loc[ft.index, c] = ft[c]
    t = t.reset_index()
    print("merged full-text rows:", len(ft))
except FileNotFoundError:
    print("no full-text recode found; using draft coding")

assert len(t) == 60 and t.cid.is_unique
t.to_csv("table1_final.csv", index=False)

is_unclear = lambda s: s.astype(str).str.strip().str.lower().str.startswith("unclear")
both = t[~is_unclear(t.data_intensity) & ~is_unclear(t.implementable_plan)].copy()
both["data_intensity"] = both.data_intensity.astype(float).astype(int)
ct = pd.crosstab(both.data_intensity, both.implementable_plan).reindex(index=LEVELS, columns=PLAN, fill_value=0)
ct.to_csv("crosstab_intensity_plan.csv")
print(ct.to_string())

summary = {
    "n_corpus": len(t),
    "n_on_both_axes": len(both),
    "excluded_unclear": sorted(set(t.cid) - set(both.cid)),
    "basis": t.basis.value_counts().to_dict(),
    "plan_yes": both[both.implementable_plan == "Yes"][["cid", "data_intensity", "demand_input"]].to_dict("records"),
    "equity_none": int((t.equity == "none").sum()),
    "benchmark_or_synthetic_od": int((t.demand_input == "synthetic or benchmark OD").sum()),
    "crosstab": ct.to_dict(),
}
json.dump(summary, open("table1_summary.json", "w"), indent=1)

# ---- Figure 2: count heatmap, single-hue sequential, counts printed in every cell ----
cmap = LinearSegmentedColormap.from_list("seq_blue", ["#f3f6fb", "#c9d8ee", "#8fb0dc", "#4f7fc0", "#234f91"])
fig, ax = plt.subplots(figsize=(6.2, 3.9), dpi=300)
vals = ct.values
vmax = max(vals.max(), 1)
ax.imshow(vals, cmap=cmap, vmin=0, vmax=vmax, aspect="auto")
for i in range(vals.shape[0]):
    for j in range(vals.shape[1]):
        v = vals[i, j]
        ax.text(j, i, str(v), ha="center", va="center", fontsize=11,
                color="white" if v > 0.6 * vmax else "#1b1f24", fontweight="bold" if v else "normal")
ax.set_xticks(range(3), ["Full plan\n(routes + frequency/fleet)", "Partial", "No plan\n(method test or assessment)"], fontsize=8)
ax.set_yticks(range(5), [LEVEL_LABEL[l] for l in LEVELS], fontsize=8)
ax.set_xlabel("Produces an implementable plan for a real city", fontsize=9)
ax.set_ylabel("Data intensity required", fontsize=9)
ax.set_xticks([x - 0.5 for x in range(1, 3)], minor=True)
ax.set_yticks([y - 0.5 for y in range(1, 5)], minor=True)
ax.grid(which="minor", color="white", linewidth=2)
ax.tick_params(which="both", length=0)
for s in ax.spines.values():
    s.set_visible(False)
# gap region: full plans at intensity 1-2 (drawn above the cell separators, label inside the box)
ax.add_patch(plt.Rectangle((-0.47, -0.47), 0.94, 1.94, fill=False, edgecolor="#1b1f24", linewidth=1.4,
                           linestyle=(0, (4, 3)), zorder=5, clip_on=False))
ax.text(0, 0.5, "gap addressed by this study", fontsize=7.5, ha="center", va="center", color="#1b1f24", zorder=6,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none"))
ax.set_title(f"Reviewed studies by data intensity and planning output (n = {len(both)})", fontsize=9, loc="left")
fig.tight_layout()
fig.savefig("fig02_gap_heatmap.png", bbox_inches="tight")
fig.savefig("fig02_gap_heatmap.pdf", bbox_inches="tight")
print("figure written; n =", len(both))
