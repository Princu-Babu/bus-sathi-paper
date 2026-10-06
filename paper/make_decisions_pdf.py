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
        "**Every question in this document needs a person to answer it.** Anything that could be settled "
        "from the code, the data or published sources already has been, and is recorded in Part D.\n\n"
        "**Part A is the meeting list:** four questions for Avny ma'am and three for Prof. Kathuria. "
        "Part B is for the lead author, Part C lists what each co-author is asked to fix in their own "
        "section, and Part E is the remaining work in order.\n\n"
        "**Where things stand.** Every analysis module has run and has been corrected after an independent "
        "audit; the methodology section is rewritten on the corrected results. The other sections still "
        "carry pre-correction numbers.\n\n"
        "**Word limit.** Not assumed here. It follows Prof. Kathuria's answer to question K1.\n\n"
        "Earlier versions of this document are in `paper/archive/`.",
        st, W)

    flow += [PageBreak()]
    flow += M.render_markdown(md, st, W, heading_page_breaks=True)

    M.build_pdf(OUT, flow, title="Pending decisions and open questions",
                footer_left="Kashmir bus route rationalisation — decision briefing")
    print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    return OUT


if __name__ == "__main__":
    main()
