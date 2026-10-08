"""
make_parameters_pdf.py
======================
Renders `paper/PARAMETERS_AND_DEFENSIBILITY.md` to `paper/PARAMETERS_AND_DEFENSIBILITY.pdf`.

Run:
    .venv/Scripts/python.exe paper/make_parameters_pdf.py
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, Spacer

import md2pdf as M

HERE = Path(__file__).resolve().parent
SRC = HERE / "PARAMETERS_AND_DEFENSIBILITY.md"
OUT = HERE / "PARAMETERS_AND_DEFENSIBILITY.pdf"


def main() -> Path:
    st = M.make_styles(base_size=8.6)
    W = M.frame_width(landscape_mode=True)
    md = SRC.read_text(encoding="utf-8")

    # The markdown carries its own title for reading on GitHub; the PDF has a cover.
    anchor = "## How to use this document"
    if anchor in md:
        md = md[md.index(anchor):]

    flow: list = [
        Spacer(1, 14 * mm),
        Paragraph("PARAMETER REGISTER AND REVIEW RISKS", st["subtitle"]),
        Spacer(1, 3 * mm),
        Paragraph("Fixed numbers, their sources, and what a reviewer will not accept", st["title"]),
        Spacer(1, 1 * mm),
        Paragraph("Kashmir bus route rationalisation → <i>Transport Policy</i> manuscript", st["subtitle"]),
        Paragraph(f"Assembled {dt.date.today().isoformat()} · plan version 3.4.5-geo", st["subtitle"]),
        Spacer(1, 6 * mm),
        HRFlowable(width="55%", thickness=1.0, color=M.ACCENT, hAlign="CENTER"),
        PageBreak(),
    ]
    flow += M.render_markdown(md, st, W, heading_page_breaks=False)

    M.build_pdf(OUT, flow, title="Fixed numbers, their sources, and review risks",
                footer_left="Kashmir bus route rationalisation — parameter register",
                landscape_mode=True)
    print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")
    return OUT


if __name__ == "__main__":
    main()
