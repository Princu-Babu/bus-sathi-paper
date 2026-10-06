"""
make_section_pdf.py -- render ONE manuscript section to its own PDF.
====================================================================
Same styles, same maths/algorithm rendering and the same citation resolution
(`citations.py`) as the full build (`make_manuscript_pdf.py`, whose SECTIONS /
FIGURES / figure logic are imported, not duplicated). Meant for the section
owner to proof a rewrite without rebuilding the 47-page manuscript.

    python paper/make_section_pdf.py 04_methodology --out audit/x/04.pdf
    python paper/make_section_pdf.py 04 --draft-notes strip --figures

Arguments
    section          file stem in paper/sections (`04_methodology`), a path, or
                     just the numeric prefix (`04`)
    --out PATH       output PDF (default: paper/_section_<stem>.pdf)
    --draft-notes    keep  (default) editorial block-quote callouts render in
                           their tinted boxes
                     strip  every editorial callout is removed (a block quote
                           whose opening words are a FLAG / DECISION / OPEN
                           QUESTION / SECTION OWNER / PRESERVED / PROVENANCE /
                           BLOCKER / TODO / NOTE TO marker, or a bracketed
                           `**[...]**` marker). Other block quotes (e.g. an
                           Algorithm written as a quote) are kept.
    --figures        append the figures this section refers to ("Figure 4",
                     "Fig. 9b", "Figure S1" ...), with the full-build captions
    --strict         exit status 1 if any maths failed or raw TeX survived

The PDF ends with a reference list holding only the works cited in the section.
Maths failures / leaked TeX are printed as WARNING lines (same guard as the
full build).
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import HRFlowable, PageBreak, Paragraph, Spacer  # noqa: E402

import citations as CI  # noqa: E402
import make_manuscript_pdf as MM  # noqa: E402
import md2pdf as M  # noqa: E402

SECTIONS_DIR = MM.SECTIONS_DIR

_NOTE_START = re.compile(
    r"^\W*(?:\[|(?:EDITORIAL\s+)?FLAG|DECISION|OPEN\s+QUESTION|SECTION\s+OWNER|NOTE\s+TO|TODO|"
    r"PRESERVED|PROVENANCE|BLOCKER|⚠)", re.I)


def resolve_section(arg: str) -> Path:
    p = Path(arg)
    if p.suffix == ".md" and p.exists():
        return p.resolve()
    stem = p.stem if p.suffix == ".md" else arg
    cand = SECTIONS_DIR / f"{stem}.md"
    if cand.exists():
        return cand
    hits = sorted(SECTIONS_DIR.glob(f"{stem}*.md"))
    if len(hits) == 1:
        return hits[0]
    names = ", ".join(f.stem for f in sorted(SECTIONS_DIR.glob("*.md")))
    raise SystemExit(f"cannot resolve section {arg!r}; available: {names}")


def strip_draft_notes(md: str) -> tuple[str, int]:
    """Remove editorial block-quote callouts. Returns (markdown, n_removed)."""
    out, n, i = [], 0, 0
    lines = md.split("\n")
    in_fence = False
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            in_fence = not in_fence
        if not in_fence and ln.lstrip().startswith(">"):
            j = i
            block = []
            while j < len(lines) and lines[j].lstrip().startswith(">"):
                block.append(re.sub(r"^\s*>\s?", "", lines[j]))
                j += 1
            head = " ".join(" ".join(block).split())[:120].replace("*", "")
            if _NOTE_START.match(head):
                n += 1
                i = j
                while i < len(lines) and not lines[i].strip():   # swallow trailing blank lines
                    i += 1
                continue
            out.extend(lines[i:j])
            i = j
            continue
        out.append(ln)
        i += 1
    return "\n".join(out), n


def referenced_figures(md: str) -> list[tuple[str, str]]:
    sel = []
    for stem, cap in MM.FIGURES:
        m = re.match(r"\*\*Figure\s+([A-Za-z]?\d+[a-z]?)\.", cap)
        if not m:
            continue
        tok = re.escape(m.group(1))
        if re.search(r"\b(?:Figure|Fig\.)\s*" + tok + r"(?![A-Za-z0-9])", md):
            sel.append((stem, cap))
    return sel


def build(section: str, out: Path | None = None, draft_notes: str = "keep",
          figures: bool = False) -> dict:
    src = resolve_section(section)
    stem = src.stem
    out = Path(out) if out else HERE / f"_section_{stem}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    M.MR.reset_reports()
    st = M.make_styles(base_size=9.3)
    W = M.frame_width()
    raw = src.read_text(encoding="utf-8")
    md = raw
    removed = 0
    if draft_notes == "strip":
        md, removed = strip_draft_notes(md)

    name = MM.SECTIONS.get(stem, (stem,))[0]
    meta = MM.SECTIONS.get(stem)
    today = dt.date.today().isoformat()
    wc = MM.word_count(md)

    flow: list = [
        Paragraph(MM.TITLE, st["small"]),
        Spacer(1, 2 * mm),
        Paragraph(f"{name} &nbsp;&mdash;&nbsp; working draft", st["subtitle"]),
        Paragraph(
            f"Single-section proof &middot; {today} &middot; revision <b>{MM.git_rev()}</b> &middot; "
            f"{wc:,} body words" + (f" (target {meta[2]:,})" if meta else "")
            + (f" &middot; {removed} draft note(s) removed" if draft_notes == "strip" else ""),
            st["small"]),
        HRFlowable(width="100%", thickness=1.0, color=M.ACCENT, spaceBefore=3, spaceAfter=8),
    ]

    bib = CI.load_bib()
    cited: list[str] = []
    missing: set[str] = set()
    md = CI.render(md, bib, cited, missing)
    if draft_notes == "keep" and stem in MM.COAUTHOR_PROSE:
        flow += M.render_markdown(
            "> **[PRESERVED CO-AUTHOR PROSE IN THIS SECTION]** Parts of this section are transcribed "
            "verbatim from the co-author attachment and have not been edited.", st, W)
    flow += M.render_markdown(md, st, W)

    if figures:
        sel = referenced_figures(md)
        if sel:
            flow += [PageBreak(), Paragraph("Figures", st["h2"]),
                     HRFlowable(width="100%", thickness=0.8, color=M.ACCENT, spaceAfter=6)]
            for fstem, cap in sel:
                flow += MM.figure_flow(fstem, cap, st, W)

    flow += [Spacer(1, 4 * mm), Paragraph("References cited in this section", st["h2"]),
             HRFlowable(width="100%", thickness=0.8, color=M.ACCENT, spaceAfter=6)]
    if missing:
        flow += M.render_markdown("> **[UNRESOLVED CITATION KEYS]** " + ", ".join(sorted(missing)), st, W)
    flow += (M.render_markdown(CI.reference_list_md(cited, bib), st, W) if cited
             else [Paragraph("(no citations in this section)", st["small"])])

    M.build_pdf(out, flow, title=f"{name} (working draft)",
                footer_left=f"Kashmir bus route rationalisation — {name} — working draft, section proof")

    report = {
        "pdf": out,
        "math_failures": M.math_failures(),
        "unrendered_math": M.find_unrendered_math(out),
        "unresolved_citations": sorted(missing),
        "n_cited": len(cited),
        "notes_removed": removed,
    }
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("section")
    ap.add_argument("--out")
    ap.add_argument("--draft-notes", choices=("keep", "strip"), default="keep")
    ap.add_argument("--figures", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    rep = build(a.section, a.out, a.draft_notes, a.figures)
    out = rep["pdf"]
    print(f"wrote {out}  ({out.stat().st_size / 1024:.0f} KB; {rep['n_cited']} works cited"
          + (f"; {rep['notes_removed']} draft notes removed" if a.draft_notes == "strip" else "") + ")")
    bad = False
    for f in rep["math_failures"]:
        bad = True
        print(f"WARNING: maths fell back to flagged source [{f['kind']} {f.get('tag') or ''}] "
              f"{f['where']}: {f['error'][:110]}")
    if rep["unrendered_math"]:
        bad = True
        print(f"WARNING: {len(rep['unrendered_math'])} unrendered-maths token(s):")
        for h in rep["unrendered_math"][:40]:
            print(f"  p.{h['page']}: {h['token']!r} ...{h['context']}...")
    if rep["unresolved_citations"]:
        bad = True
        print("WARNING: unresolved citation keys:", ", ".join(rep["unresolved_citations"]))
    if not bad:
        print("maths check: no raw TeX in the PDF text; all citations resolved")
    return 1 if (bad and a.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
