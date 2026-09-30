"""
make_decisions_pdf.py
=====================
Renders `paper/PENDING_DECISIONS.md` to `paper/PENDING_DECISIONS.pdf`.

This is the briefing the project lead reads to answer the open questions. It is
deliberately a separate document from the manuscript working draft: the draft
shows the flags in context, this one collects them into decisions with options
and consequences.

Run:
    .venv/Scripts/python.exe paper/make_decisions_pdf.py
"""

from __future__ import annotations

import datetime as dt
import subprocess
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, Spacer

import md2pdf as M

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = HERE / "PENDING_DECISIONS.md"
OUT = HERE / "PENDING_DECISIONS.pdf"


def git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True,
                              timeout=10).stdout.strip() or "uncommitted"
    except Exception:
        return "unknown"


def main() -> Path:
    st = M.make_styles(base_size=9.3)
    W = M.frame_width()
    md = SRC.read_text(encoding="utf-8")
    today = dt.date.today().isoformat()

    # The markdown carries its own title block for reading on GitHub; the PDF has
    # a cover page instead, so drop everything before the first real section.
    anchor = "## How to use this document"
    if anchor in md:
        md = md[md.index(anchor):]

    flow: list = [
        Spacer(1, 16 * mm),
        Paragraph("DECISION BRIEFING", st["subtitle"]),
        Spacer(1, 3 * mm),
        Paragraph("Pending Decisions and Open Questions", st["title"]),
        Spacer(1, 1 * mm),
        Paragraph("Kashmir bus route rationalisation → <i>Transport Policy</i> manuscript",
                  st["subtitle"]),
        Paragraph(f"Assembled {today} · repository revision <b>{git_rev()}</b>", st["subtitle"]),
        Spacer(1, 7 * mm),
        HRFlowable(width="55%", thickness=1.0, color=M.ACCENT, hAlign="CENTER"),
        Spacer(1, 8 * mm),
    ]

    flow += M.render_markdown(
        "**Every question in this document needs a human on this project to answer it.** None of them can be "
        "settled by reading the code, re-running a module or searching the literature — where a question "
        "*could* be settled that way it already has been, and the answer is recorded in Part F rather than "
        "asked here. Every analysis module has run; nothing below waits on computation.\n\n"
        "**Read Part A first.** It ranks all open items. Items 1–9 block submission; items 1–4 are the ones "
        "to start this week. Parts B–E give each item's question, evidence, options and recommendation.\n\n"
        "**Checked against the journal.** The *Transport Policy* Guide for Authors was read on 2026-10-01: "
        "8,000-word norm, 250-word abstract, double-anonymised review, and a mandatory declaration of "
        "generative-AI use.\n\n"
        "**Companion files.** Each editorial flag appears in place in `Kashmir_Manuscript_Working_Draft.pdf`. "
        "The superseded v1 of this document is in `paper/archive/`.",
        st, W)

    flow += [PageBreak()]
    flow += M.render_markdown(md, st, W, heading_page_breaks=True)

    M.build_pdf(OUT, flow, title="Pending decisions and open questions",
                footer_left="Kashmir bus route rationalisation — decision briefing")
    print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    return OUT


if __name__ == "__main__":
    main()
