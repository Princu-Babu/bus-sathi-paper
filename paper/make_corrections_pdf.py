"""
make_corrections_pdf.py
=======================
Generates `Corrections_for_Coauthors.pdf` — a short, self-contained briefing that
brings co-authors from the OLD shared report (stale "Srinagar-metropolitan"
framing) onto the CURRENT authoritative Kashmir-Division numbers that live in
this repo (paper/CLAIM_LEDGER.md) and on the dashboard.

Every "NEW (correct)" number here is copied from paper/CLAIM_LEDGER.md — the
single source of truth. Nothing is invented. If a CL value changes, update it
here too (or regenerate from the ledger).

Run:
    .venv/Scripts/python.exe paper/make_corrections_pdf.py
Output:
    paper/Corrections_for_Coauthors.pdf
"""  # noqa: W605

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

OUT = Path(__file__).resolve().parent / "Corrections_for_Coauthors.pdf"

# ---------------------------------------------------------------------------
# Palette (calm, print-safe; not the placeholder dataviz palette)
# ---------------------------------------------------------------------------
INK       = colors.HexColor("#1a1a2e")
ACCENT    = colors.HexColor("#0b6e4f")   # green = corrected/authoritative
STALE     = colors.HexColor("#9b2226")   # red   = superseded
RULE      = colors.HexColor("#c8ccd4")
SOFT      = colors.HexColor("#f2f4f7")
SOFTGREEN = colors.HexColor("#e6f2ec")

styles = getSampleStyleSheet()

def S(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

body   = S("body", fontName="Helvetica", fontSize=9.3, leading=13.4, textColor=INK, spaceAfter=6)
h1     = S("h1", fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=INK, spaceAfter=4)
sub    = S("sub", fontName="Helvetica", fontSize=9.6, leading=13, textColor=colors.HexColor("#55607a"), spaceAfter=2)
h2     = S("h2", fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=ACCENT, spaceBefore=12, spaceAfter=5)
small  = S("small", fontName="Helvetica", fontSize=8, leading=10.5, textColor=colors.HexColor("#55607a"))
cellL  = S("cellL", fontName="Helvetica", fontSize=8.4, leading=11, textColor=INK)
cellB  = S("cellB", fontName="Helvetica-Bold", fontSize=8.4, leading=11, textColor=INK)
cellStale = S("cellStale", fontName="Helvetica", fontSize=8.4, leading=11, textColor=STALE)
cellGood  = S("cellGood", fontName="Helvetica-Bold", fontSize=8.4, leading=11, textColor=ACCENT)


def hr(space_before=2, space_after=8, col=RULE):
    return [Spacer(1, space_before), HRFlowable(width="100%", thickness=0.8, color=col), Spacer(1, space_after)]


# ---------------------------------------------------------------------------
# The corrections table — OLD (shared) vs NEW (authoritative, cited to ledger)
# Sourced verbatim from paper/CLAIM_LEDGER.md §4 (Prohibited Legacy Metrics)
# and the CL master table.
# ---------------------------------------------------------------------------
CORR = [
    # (topic, OLD shared value, NEW authoritative value, why it changed, CL)
    ("Study area",
     "Srinagar Metropolitan City",
     "Kashmir Division — all 10 districts",
     "The plan and denominator span the whole division, not one municipality.",
     "scope"),
    ("Permit base",
     "342 permits",
     "614 permit records",
     "The 342 figure counted only a geocoded subset; the full digitised register is 614.",
     "CL-01"),
    ("Route count",
     "207 routes",
     "186 active routes (32 trunk / 154 feeder)",
     "207 included unmerged duplicate trunks; 186 is the reconciled active set.",
     "CL-06"),
    ("\u201cReduction\u201d",
     "39% route reduction",
     "99.4% corridor retention (156/157)",
     "The apparent cut is a change of accounting unit (permits\u2192corridors), not lost coverage.",
     "CL-07, CL-08"),
    ("Population served",
     "95.7% coverage",
     "24.2% of division (network walkshed)",
     "Old % used a ~1.66M Srinagar denominator + straight-line buffers; corrected to 6.58M + walk network.",
     "CL-28"),
    ("Fleet size",
     "~1,009 buses",
     "1,011 buses (187 HPV / 754 MPV / 70 LPV)",
     "Re-anchored to GPS-measured cycle times in engine v3.4.5.",
     "CL-36"),
    ("Denominator",
     "~1.66M (Srinagar UA)",
     "6,584,762 residents (10 districts)",
     "WorldPop 2026 zonal sum over the district union; single denominator for every share.",
     "CL-11"),
    ("Validation claim",
     "\u201cValidated against ridership\u201d",
     "Supply-side observational GPS validation",
     "Driver GPS carries no ridership signal; the plan is decision-robust, not demand-validated.",
     "\u2014"),
    ("Engine baseline",
     "\u201cv4\u201d / mixed versions",
     "v3.4.5-geo (frozen)",
     "The authoritative operational baseline is frozen at v3.4.5-geo.",
     "\u2014"),
]

HEADLINE = [
    ("614", "permit records", "CL-01"),
    ("157", "distinct corridors", "CL-02"),
    ("186", "active routes", "CL-06"),
    ("1,011", "buses (+68.5%)", "CL-36"),
    ("37.4%", "Euclidean overstatement", "CL-26"),
    ("24.2%", "division coverage", "CL-28"),
    ("6.58M", "residents (denominator)", "CL-11"),
    ("43,809", "GPS runs (supply-side)", "CL-18"),
]


def build():
    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4,
        leftMargin=16*mm, rightMargin=16*mm, topMargin=15*mm, bottomMargin=14*mm,
        title="Corrections for Co-Authors \u2014 Kashmir Route-Rationalisation Paper",
        author="Paper team (engine makers)",
    )
    E = []

    # ---- Header ----
    E.append(Paragraph("Corrections for Co-Authors", h1))
    E.append(Paragraph(
        "Kashmir Route-Rationalisation Paper &nbsp;\u2022&nbsp; authoritative numbers supersede the earlier shared draft",
        sub))
    E += hr()

    E.append(Paragraph(
        "<b>Why you are reading this.</b> The version of the report circulated earlier was an <i>old</i> "
        "draft. Since then the plan was re-scoped to the full Kashmir Division and re-run several times "
        "(engine now frozen at <b>v3.4.5-geo</b>). The numbers in this repository "
        "(<font face='Courier'>paper/CLAIM_LEDGER.md</font>) and on the live dashboard are the current, "
        "authoritative set \u2014 we built the engine, so those are the definitive figures. Please replace any "
        "legacy numbers in your sections with the \u201cNEW\u201d column below. Every corrected value cites a "
        "Claim-Ledger ID (<font face='Courier'>CL-xx</font>) so it can be traced to the exact module that "
        "produced it.", body))

    # ---- Headline strip ----
    E.append(Paragraph("The eight headline numbers", h2))
    bignum = S("bignum", fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=ACCENT, spaceAfter=2)
    cards = []
    row = []
    for i, (big, lab, cl) in enumerate(HEADLINE):
        cell = [
            Paragraph(big, bignum),
            Paragraph(lab, small),
            Paragraph(f"<font face='Courier' size=6.5 color='#0b6e4f'>{cl}</font>", small),
        ]
        row.append(cell)
        if len(row) == 4:
            cards.append(row); row = []
    if row:
        while len(row) < 4:
            row.append("")
        cards.append(row)
    t = Table(cards, colWidths=[44*mm]*4)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SOFTGREEN),
        ("BOX", (0,0), (-1,-1), 0.5, RULE),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.white),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
    ]))
    E.append(t)

    # ---- Corrections table ----
    E.append(Paragraph("What changed, line by line", h2))
    header = [
        Paragraph("<b>Topic</b>", cellB),
        Paragraph("<b>OLD (shared draft)</b>", cellB),
        Paragraph("<b>NEW (authoritative)</b>", cellB),
        Paragraph("<b>Why</b>", cellB),
        Paragraph("<b>Ledger</b>", cellB),
    ]
    data = [header]
    for topic, old, new, why, cl in CORR:
        data.append([
            Paragraph(topic, cellB),
            Paragraph(f"<strike>{old}</strike>", cellStale),
            Paragraph(new, cellGood),
            Paragraph(why, cellL),
            Paragraph(f"<font face='Courier' size=7>{cl}</font>", cellL),
        ])
    tbl = Table(data, colWidths=[22*mm, 33*mm, 40*mm, 57*mm, 16*mm], repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INK),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, SOFT]),
        ("GRID", (0,0), (-1,-1), 0.4, RULE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    for i, h in enumerate(header):
        h.style = S("hw", parent=cellB, textColor=colors.white)
    E.append(tbl)

    # ---- Framing guidance ----
    E.append(Paragraph("Three framing points to keep consistent across all sections", h2))
    for txt in [
        "<b>1. It is not a route cut.</b> The plan <i>retains</i> 156 of 157 physical corridors and adds "
        "30 e-bus routes. The headline \u201c71% reduction\u201d is almost entirely a change of unit "
        "(collapsing duplicate permits onto the same corridor), not places losing service. Say "
        "\u201crationalised frequencies and fleet,\u201d not \u201ccut routes.\u201d [CL-07, CL-08]",
        "<b>2. Coverage is quoted on the walk network against residents.</b> The central methodological "
        "result is that straight-line buffers overstate population served by ~37% per route; corrected "
        "division coverage is 24.2% of 6.58M, not 95.7% of a metro figure. [CL-26, CL-28]",
        "<b>3. Validation is supply-side only.</b> We never write \u201cvalidated against ridership.\u201d The GPS "
        "layer validates geometry, speed, run time, and fleet arithmetic \u2014 the supply chain. The honest "
        "claim is <i>decision-robust, not demand-validated.</i>",
    ]:
        E.append(Paragraph(txt, body))

    E += hr(space_before=6, space_after=6)
    E.append(Paragraph(
        "Authoritative source: <font face='Courier'>paper/CLAIM_LEDGER.md</font> (CL-01\u2013CL-36) in the "
        "paper-companion repository, and the live dashboard. Barred legacy terms are listed in that "
        "ledger, \u00a74. Questions on any number \u2192 the engine team.", small))

    doc.build(E)
    print(f"[OK] wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    build()
