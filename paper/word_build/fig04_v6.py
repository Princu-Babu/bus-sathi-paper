"""Figure 4 for Section 4 version 6, in the style of analysis/fig_generate_all.py (fig04_method_flow).

The published figure lists equation numbers from v5 and a 'QA gates' step that v6 does not describe,
so v6 gets its own copy here; paper/figures/fig04_method_flow.* is left unchanged for the PDF builds.
Writes fig04_method_flow_v6.png next to this script."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = Path(__file__).resolve().parent
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "savefig.facecolor": "#ffffff"})


def box(ax, x, y, w, h, text, fc="#f4f3f0", ec=MUTED, bold=False, size=8, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.015",
                                fc=fc, ec=ec, lw=0.8, ls=ls))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=INK, fontsize=size,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, style="-|>", ls="-"):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle=style, color=INK2, lw=0.9, ls=ls, shrinkA=0, shrinkB=0))


fig, ax = plt.subplots(figsize=(7.2, 3.3))
ax.set_axis_off(); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
stages = [("Stage 1\nCorridors", "614 permit and\ntimetable rows\n→ 157 corridors\n(§4.2–4.3)"),
          ("Stage 2\nReach", "walking catchments\n(Eq. 1–3)\ndestinations\n(Eq. 4)"),
          ("Stage 3\nRank and merge", "index (Eq. 5–7)\nmerging (Eq. 8, Alg. 1)\ntiers (Eq. 9)"),
          ("Stage 4\nService and fleet", "headways (§4.7)\ncycle time (Eq. 10–11)\nfleet (Eq. 12–13)\nsensitivity (§4.11)")]
w = 0.22
for k, (h, b) in enumerate(stages):
    x = 0.01 + k * 0.25
    box(ax, x, 0.70, w, 0.25, h, fc="#e8f1fc", ec="#2a78d6", bold=True, size=8)
    box(ax, x, 0.31, w, 0.33, b, size=7.5)
    if k < 3:
        arrow(ax, x + w, 0.825, x + 0.25, 0.825)
# where operator, GPS and hand-checked data enter (dashed)
box(ax, 0.01, 0.02, 0.97, 0.18,
    "Operator, GPS and hand-checked inputs: e-bus operator routes, fleet and boardings (§4.9, Eq. 14)\n"
    "driver GPS running times (§4.10–4.11) · desk-reviewed road distances on 49 routes (§4.10)",
    fc="#ffffff", ec=MUTED, size=7.3, ls="--")
for k in (2, 3):
    x = 0.01 + k * 0.25 + w / 2
    arrow(ax, x, 0.20, x, 0.31, ls="--")
fig.savefig(HERE / "fig04_method_flow_v6.png", dpi=300, bbox_inches="tight", metadata={"Software": None})
print("wrote fig04_method_flow_v6.png")
