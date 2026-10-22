"""Render the 14 equations of Section 4 version 6 to PNG with matplotlib mathtext, using the
paper's own pre-processor (paper/mathrender.py) so the notation matches the PDF builds.
Writes v6_eq01.png ... v6_eq14.png and eq_sizes_v6.json next to this script.

Numbering follows the v6 order of subsections (catchments, index, merging, tiers, fleet, ridership).
Changes of substance from v5: Eq. 5 applies the tourist multiplier to the resident count, as the
engine does (transit_kashmir_v3.py:1863), not to the destination score; the corridor share in the
ridership estimate is s(r), so that sigma means only the spare allowance."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # paper/ holds mathrender.py
import mathrender as MR  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

EQ = {
    1: r"A_{net}(r) = \bigcup_{v \in V :\, d(v) \leq W} B\left(x_v,\ \min(W - d(v),\ \tau)\right)",
    2: r"\Pi(r) = \sum_{c :\, x_c \in A_{net}(r)} \rho_c",
    3: r"\pi_c(r) = \frac{\rho_c}{n_c}\,\mathbf{1}[x_c \in A_{net}(r)], \qquad \sum_r \pi_c(r) = \rho_c",
    4: r"O(r) = \sum_{q \in Q :\, d_q(r) \leq 250\,\mathrm{m}} \alpha_{t(q)}",
    5: r"\Pi^{*}(r) = \mu\, \Pi(r)\ \ \mathrm{if}\ r \in T, \qquad \Pi^{*}(r) = \Pi(r)\ \ \mathrm{otherwise}, \qquad \mu = 1.30",
    6: r"\hat{z}(r) = \frac{z(r) - \min_{r'} z(r')}{\max_{r'} z(r') - \min_{r'} z(r')}",
    7: r"CDI(r) = \beta\, \hat{z}_{\Pi}(r) + (1 - \beta)\, \hat{z}_{O}(r), \qquad \beta = 0.50",
    8: r"\phi(r_i, r_j) = \frac{|S(r_i) \cap S(r_j)|}{\min(|S(r_i)|,\ |S(r_j)|)}",
    9: r"GVF(k) = 1 - \frac{\sum_{j=1}^{k}\;\;\sum_{i \in C_j} (y_i - \bar{y}_{C_j})^2}{\sum_i (y_i - \bar{y})^2}, \qquad k = 2, \ldots, 7",
    10: r"t_{run}(r) = \chi(r)\left(t_{free}(r) + J(r)\right) + \delta\, \frac{\ell(r)}{\Delta}",
    11: r"t_{cyc}(r) = \min\left(2 \lambda\, t_{run}(r),\ 2\, \ell(r)\, \omega_{type(r)}\right)",
    12: r"N_{op}(r) = \left\lceil \frac{t_{cyc}(r)}{h(r)} \right\rceil, \qquad N(r) = \max\left(\lceil \sigma N_{op}(r) \rceil,\ N^{min}_{type(r)}\right)",
    13: r"N_{total} = \sum_{r \notin E} N(r) + \sum_{r \in E} \max\left(N(r),\ N^{emp}(r)\right) = 728 + 283 = 1{,}011",
    14: r"\tilde{D}(r) = \kappa\, g\, m_{type(r)}\, s(r) \sum_{c \in A(r)} \rho_c, \qquad \kappa = 0.33",
}
DPI, FS = 300, 13
sizes = {}
for n, tex in EQ.items():
    pp = MR.preprocess(tex, display=True)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${pp}$", fontsize=FS, color="#15161c")
    out = HERE / f"v6_eq{n:02d}.png"
    fig.savefig(out, dpi=DPI, transparent=False, facecolor="white", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    w, h = Image.open(out).size
    sizes[n] = dict(file=out.name, w=w, h=h, tex=tex)
    print(n, w, h)
(HERE / "eq_sizes_v6.json").write_text(json.dumps(sizes, indent=1), encoding="utf-8")
