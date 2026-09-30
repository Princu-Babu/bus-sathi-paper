"""
make_manuscript_pdf.py
======================
Assembles every section in `paper/sections/` into one working-draft PDF:

    paper/Kashmir_Manuscript_Working_Draft.pdf

Design rules (these matter — they encode a promise made to the co-authors):

  * NOTHING IS REMOVED. Every file in `paper/sections/` is rendered in full,
    including the provenance banners, the co-author prose transcribed verbatim,
    and every `[EDITORIAL FLAG ...]` / `[FLAG ...]` callout. The PDF is the
    working draft, not the submission copy — the flags are the point.
  * Section order is by filename prefix (00 Abstract ... 08 Conclusions).
  * Ownership and status come from `SECTIONS` below and are printed on the
    contents page so a co-author can find their own section immediately.
  * Word counts are measured from the files at build time, not asserted.

Run:
    .venv/Scripts/python.exe paper/make_manuscript_pdf.py
"""

from __future__ import annotations

import datetime as dt
import re
import subprocess
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, Spacer, Table, TableStyle,
)

import citations as CI
import md2pdf as M

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SECTIONS_DIR = HERE / "sections"
OUT = HERE / "Kashmir_Manuscript_Working_Draft.pdf"

TITLE = ("Planning What You Cannot Count: An Open-Data Framework for Bus Route "
         "Rationalisation and Fleet Sizing under Demand-Data Scarcity")
JOURNAL = "Target journal: Transport Policy (Elsevier)"

# filename stem -> (display name, owners, target words, status)
SECTIONS = {
    "00_abstract": ("Abstract", "Prashant, Ankit, Sharvesh", 230,
                    "Complete draft on locked numbers"),
    "01_introduction": ("1. Introduction", "Misti, Avny", 1200,
                        "Co-author prose preserved verbatim + editorial flags"),
    "02_literature": ("2. Literature review and research gap", "Sharvesh, Ankit", 1400,
                      "Drafted for co-author review; §2.1 protocol NOT run"),
    "03_study_area": ("3. Study area and data", "Krishna", 1100,
                      "Drafted for co-author review; ethics paragraph blank"),
    "04_methodology": ("4. Methodology", "Prashant (sole owner)", 2300,
                       "Complete draft; Eqs 1-14 + Algorithm 1"),
    "05_results": ("5. Results", "Prashant, Misti", 2400,
                   "All subsections drafted; §5.12 provisional (D8)"),
    "06_validation": ("6. Validation and robustness", "Avny, Krishnan, Prashant", 900,
                      "V1, V2, V4, V5, V6 executed; V3 forward work"),
    "07_discussion": ("7. Discussion and policy implications", "Ankit, Avny, Misti", 1200,
                      "Drafted for co-author review + co-author block verbatim"),
    "08_conclusions": ("8. Conclusions", "Ankit, Prashant, Sharvesh", 400,
                       "Complete draft"),
}

# Which sections were written by a co-author and must not be edited by anyone
# assembling this document.
COAUTHOR_PROSE = {"01_introduction", "07_discussion"}


FIGURES = [
    ("fig01_framework", "**Figure 1.** Conceptual framework: four open inputs produce a supply plan that is "
     "checked through six convergent channels. V3 (expert panel) was not run."),
    ("fig02_review_flow", "**Figure 2.** Literature-review flow diagram — depends on decision D5 (§2.1 protocol)."),
    ("fig03_study_area", "**Figure 3.** Study area: the ten districts of Kashmir Division and the 186 active "
     "routes of the rationalised plan by service class."),
    ("fig04_method_flow", "**Figure 4.** The four-phase method and the equations that implement each phase."),
    ("fig05_permit_funnel", "**Figure 5.** From permits to routes: 614 permit records resolve to 157 "
     "corridors; 156 of them are retained among the 186 active routes [CL-01, CL-02, CL-08]."),
    ("fig06_catchment_bias", "**Figure 6.** Euclidean against network walk catchments. Left: per-route "
     "residents within 400 m under each definition. Right: distribution of the Euclidean overstatement "
     "(median 37.4 %) [CL-26]."),
    ("fig07_tiers", "**Figure 7.** Class count and tiers. Left: goodness of variance fit for k = 2–7; both "
     "elbow rules select k = 3. Right: routes ranked by the network composite index, coloured by tier "
     "[CL-37]."),
    ("fig08_coverage", "**Figure 8.** The deduplicated network walkshed (blue) over the WorldPop 2026 "
     "population surface: 24.2 % of the division's residents live within a 400 m walk of a route [CL-28]."),
    ("fig09_fleet_interval", "**Figure 9.** Fleet under joint parameter uncertainty, regimes A (as "
     "specified) and B (observed urban and peri-urban pace), against the published 1,011 [CL-56]."),
    ("fig09b_sobol", "**Figure 9b.** Total-order Sobol' indices: which parameters drive fleet and tier "
     "uncertainty [CL-58]."),
    ("figS1_frontier", "**Figure S1.** The fleet price of city frequency: total fleet against a common "
     "urban/peri-urban headway, as specified and at observed pace [CL-52]."),
    ("figS2_funding_curve", "**Figure S2.** Funding-constrained sequencing: residents reached as routes are "
     "bought in order of new residents per bus. 30 % of the fleet reaches 92 % of the plan's coverage "
     "[CL-61]."),
]


def word_count(md: str) -> int:
    """Words in the body only: drop blockquote callouts, headings, tables, fences."""
    out, in_fence = [], False
    for ln in md.split("\n"):
        s = ln.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith((">", "#", "|")) or re.fullmatch(r"-{3,}", s):
            continue
        out.append(s)
    txt = re.sub(r"[*_`\[\]()]", " ", " ".join(out))
    return len([w for w in txt.split() if any(c.isalnum() for c in w)])


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, timeout=10).stdout.strip() or "uncommitted"
    except Exception:
        return "unknown"


def main() -> Path:
    st = M.make_styles(base_size=9.3)
    W = M.frame_width()
    flow: list = []
    today = dt.date.today().isoformat()

    # ------------------------------------------------------------------ cover
    flow += [
        Spacer(1, 10 * mm),
        Paragraph("WORKING DRAFT — NOT FOR SUBMISSION", st["subtitle"]),
        Spacer(1, 3 * mm),
        Paragraph(TITLE, st["title"]),
        Spacer(1, 2 * mm),
        Paragraph(JOURNAL, st["subtitle"]),
        Paragraph(f"Assembled {today} &nbsp;&middot;&nbsp; repository revision <b>{git_rev()}</b>",
                  st["subtitle"]),
        Spacer(1, 6 * mm),
        HRFlowable(width="55%", thickness=1.0, color=M.ACCENT, hAlign="CENTER"),
        Spacer(1, 7 * mm),
    ]

    banner = (
        "**What this document is.** Every section file in `paper/sections/` rendered in full, in order, "
        "with nothing removed. It exists so that co-authors can read their own text in context and act on "
        "the open questions in it.\n\n"
        "**What has been done to co-author prose: nothing.** Text written by a co-author is transcribed "
        "verbatim. Where it conflicts with another part of the manuscript, the conflict is raised in a "
        "tinted callout and *proposed* replacement wording is given — the prose itself is left alone. "
        "There is exactly one exception, a section heading, and it is disclosed at the point of change "
        "(FLAG 3-A).\n\n"
        "**What the callouts mean.** Orange = an editorial decision a co-author must take. Red = a "
        "blocker that can sink the submission if unresolved. Blue = provenance or neutral notes. "
        "The companion briefing `PENDING_DECISIONS.pdf` collects every one of them into numbered "
        "decisions with options and consequences.\n\n"
        "**Author list, affiliations, corresponding author and CRediT roles are deliberately absent** "
        "— they are pending (Decision 8)."
    )
    flow += M.render_markdown(banner, st, W)

    flow += [Spacer(1, 5 * mm)]

    # contents table
    rows = [["#", "Section", "Owners", "Words (target)", "Status"]]
    total = 0
    files = sorted(SECTIONS_DIR.glob("*.md"))
    for f in files:
        stem = f.stem
        meta = SECTIONS.get(stem)
        md = f.read_text(encoding="utf-8")
        wc = word_count(md)
        total += wc
        if meta:
            name, owners, target, status = meta
            rows.append([stem.split("_")[0], name, owners, f"{wc:,} ({target:,})", status])
        else:
            rows.append([stem.split("_")[0], stem, "?", f"{wc:,}", "not registered"])
    rows.append(["", "**Total body words**", "", f"**{total:,}**", "target 9,000–10,000"])

    flow += [Paragraph("Contents, ownership and current state", st["h2"])]
    flow += [M._table(rows, st, W)]
    flow += [
        Spacer(1, 3 * mm),
        Paragraph(
            "Word counts are measured from the section files at build time and exclude headings, tables, "
            "code blocks and every editorial callout — i.e. they count only prose that would survive "
            "into a submitted manuscript. They are therefore lower than the raw file length.",
            st["small"]),
        PageBreak(),
    ]

    # ------------------------------------------------------------- the sections
    bib = CI.load_bib()
    cited: list[str] = []
    missing: set[str] = set()
    for f in files:
        md = CI.render(f.read_text(encoding="utf-8"), bib, cited, missing)
        if f.stem in COAUTHOR_PROSE:
            flow += M.render_markdown(
                "> **[PRESERVED CO-AUTHOR PROSE IN THIS SECTION]** Parts of this section are transcribed "
                "verbatim from the co-author attachment and have not been edited, condensed or reordered.",
                st, W)
        flow += M.render_markdown(md, st, W, heading_page_breaks=False)
        flow += [PageBreak()]

    # ---------------------------------------------------------------- references
    flow += [Paragraph("References", st["h1"]),
             HRFlowable(width="100%", thickness=1.1, color=M.ACCENT, spaceAfter=7)]
    if missing:
        flow += M.render_markdown("> **[UNRESOLVED CITATION KEYS]** " + ", ".join(sorted(missing)), st, W)
    flow += M.render_markdown(CI.reference_list_md(cited, bib), st, W)
    flow += [PageBreak()]

    # ------------------------------------------------------------------- figures
    from reportlab.platypus import Image
    flow += [Paragraph("Figures", st["h1"]),
             HRFlowable(width="100%", thickness=1.1, color=M.ACCENT, spaceAfter=7)]
    for stem, cap in FIGURES:
        png = HERE / "figures" / f"{stem}.png"
        if not png.exists():
            flow += M.render_markdown(f"> **[FIGURE NOT YET DRAWN]** {stem}: {cap}", st, W)
            continue
        from reportlab.lib.utils import ImageReader
        iw, ih = ImageReader(str(png)).getSize()
        w = min(W, 170 * mm); h = w * ih / iw
        if h > 200 * mm:
            h = 200 * mm; w = h * iw / ih
        flow += [Image(str(png), width=w, height=h), Spacer(1, 2 * mm)]
        flow += M.render_markdown(cap, st, W)
        flow += [Spacer(1, 6 * mm)]
    flow += [PageBreak()]

    # ------------------------------------------------------------------- closing
    flow += [Paragraph("Provenance of every number in this draft", st["h1"]),
             HRFlowable(width="100%", thickness=1.1, color=M.ACCENT, spaceAfter=7)]
    flow += M.render_markdown(
        "Every quantity carries a claim ID (`CL-xx`) or a finding ID (`F1`-`F12`) that resolves to a row in "
        "`paper/CLAIM_LEDGER.md` and, through it, to the analysis module that produced it. The rule the "
        "repository enforces on itself is short: **a number whose module has not run does not exist and is "
        "not written into the paper.** Where a result is specified in the design but not yet computed, the "
        "draft says so in a callout instead of estimating it. That is why several subsections below name a "
        "quantity and then decline to report it.\n\n"
        "The legacy framing that appears in older shared reports &mdash; 342 permits, 207 routes, a 39 % "
        "reduction, 95.7 % coverage, a ~1,009 fleet, and any Srinagar-metropolitan denominator &mdash; is "
        "superseded and barred from this manuscript. If any of those numbers appears in a draft you hold, "
        "that draft predates the current baseline.",
        st, W)

    M.build_pdf(OUT, flow, title="Kashmir manuscript working draft",
                footer_left="Kashmir bus route rationalisation — working draft, not for submission")
    print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB, {total:,} body words)")
    return OUT


if __name__ == "__main__":
    main()
