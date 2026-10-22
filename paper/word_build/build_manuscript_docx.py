"""Word versions of every manuscript section, with figures and equations as images.

Reads paper/sections/*.md (the same files make_manuscript_pdf.py renders) and writes to paper/word/:

  Section_00_Abstract.docx ... Section_08_Conclusions.docx   one per section, working version
  Kashmir_Manuscript_Working_Draft.docx                       all sections, callouts and claim tags kept
  Kashmir_Manuscript_Clean.docx                               all sections, callouts and claim tags removed

Figures are placed after the paragraph that first mentions them ("Figure 5", "Fig. 5"); figures that no
paragraph mentions are placed at the end of Section 5. Display equations ($$ ... \\tag{n} $$) use the
rendered images in this folder when the TeX matches (Section 4), otherwise they are rendered here with the
paper's own pre-processor (mathrender.py). Inline maths becomes formatted text where it is simple and a
small image otherwise. Callouts ("> ...") are shaded boxes in the working version and dropped from the
clean one. Run:

    .venv/Scripts/python.exe paper/word_build/build_manuscript_docx.py
"""
from __future__ import annotations

import io
import json
import re
import sys
from html import unescape
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
sys.path.insert(0, str(PAPER))
import citations as CI  # noqa: E402
import mathrender as MR  # noqa: E402
import make_manuscript_pdf as MM  # noqa: E402  (FIGURES and section names)

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from docx import Document  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402

OUT = PAPER / "word"
SECTIONS = PAPER / "sections"
FIGS = PAPER / "figures"
FONT = "Times New Roman"
EQ_V6 = {v["tex"]: HERE / v["file"] for v in json.loads((HERE / "eq_sizes_v6.json").read_text("utf-8")).values()}

FIG_ID = {}            # "4" -> (stem, caption)
for stem, cap in MM.FIGURES:
    m = re.match(r"\*\*Figure (\w+)\.\*\*", cap)
    FIG_ID[m.group(1)] = (stem, cap)
FIG_MENTION = re.compile(r"\b(?:Figure|Fig\.)\s*\**\s*(\d+b?|S\d)\b")
TAGS = re.compile(r"\s*`?\[(?:CL-\d+|F\d+)(?:\s*[,;–-]\s*(?:CL-\d+|F\d+))*\]`?"
                  r"|\s*\((?:CL-\d+|F\d+)(?:\s*[,;]\s*(?:CL-\d+|F\d+))*\)"
                  r"|\s*[—–]\s*CL-\d+(?=\))")
CALLOUT_FILL = {"flag": "FFF6E8", "red": "FDECEC", "note": "EEF4FB"}


# ---------------------------------------------------------------- small docx helpers
def shade(par, fill):
    ppr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def cell_shade(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def page_number_footer(doc):
    p = doc.sections[0].footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
        r._r.append(el)


def new_doc(title):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = FONT; st.font.size = Pt(11.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.15
    for name, size in (("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 12), ("Heading 4", 11.5)):
        h = doc.styles[name]; h.font.name = FONT; h.font.size = Pt(size); h.font.bold = True
        h.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        rf = h.element.rPr.find(qn("w:rFonts"))
        if rf is not None:
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                rf.attrib.pop(qn(a), None)
            rf.set(qn("w:ascii"), FONT); rf.set(qn("w:hAnsi"), FONT)
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(s, side, Cm(2.5))
    doc.core_properties.title = title
    doc.core_properties.author = "Kashmir bus route rationalisation study"
    page_number_footer(doc)
    return doc


# ---------------------------------------------------------------- maths
def math_png(tex, fontsize, display):
    pp = MR.preprocess(tex, display=display)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${pp}$", fontsize=fontsize, color="#15161c")
    buf = io.BytesIO()
    fig.savefig(buf, dpi=300, format="png", facecolor="white", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    buf.seek(0)
    return buf


_MARK = re.compile(r"<(/?)(i|b|sub|super)\b[^>]*>|([^<]+)")


def add_markup(par, markup, size=None):
    """Runs from mathrender's mini-HTML (<i>, <b>, <sub>, <super>)."""
    state = {"i": 0, "b": 0, "sub": 0, "super": 0}
    for close, tag, text in _MARK.findall(markup):
        if tag:
            state[tag] += -1 if close else 1
            continue
        r = par.add_run(unescape(text).replace("\xa0", " "))
        r.italic = state["i"] > 0; r.bold = state["b"] > 0
        r.font.subscript = state["sub"] > 0; r.font.superscript = state["super"] > 0
        if size:
            r.font.size = Pt(size)


def add_inline_math(par, tex, size):
    mk = MR.simple_inline_markup(tex)
    if mk is not None:
        add_markup(par, mk, size)
        return
    par.add_run().add_picture(math_png(tex, 11, False), height=Pt((size or 11.5) * 1.15))


# ---------------------------------------------------------------- inline markdown
TOKEN = re.compile(
    r"(`[^`]+`)"                                     # code
    r"|(?<![A-Z0-9$\\])\$(?=[^\s$])((?:\\.|[^$\\])+?)(?<![\s\\])\$(?!\d)"   # $math$ (md2pdf rule)
    r"|(\*\*[^*]+?\*\*)"                             # bold
    r"|(?<![*\w])(\*[^*\s][^*]*?\*)(?![*\w])"         # italic
    r"|(?<![\w])(_[^_\s][^_]*?_)(?![\w])"             # _italic_
    r"|(\[([^\]]+)\]\(([^)]+)\))")                   # [text](url)


def add_inline(par, text, size=None, bold=False, italic=False):
    text = text.replace(r"\$", "\x02").replace("&nbsp;", " ")
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            _run(par, text[pos:m.start()], size, bold, italic)
        code, math, b, it, it2, link, ltext, _url = m.groups()
        if code:
            r = par.add_run(code[1:-1]); r.font.name = "Consolas"; r.font.size = Pt((size or 11.5) - 1.5)
            r.bold = bold
        elif math is not None:
            add_inline_math(par, math, size)
        elif b:
            add_inline(par, b[2:-2], size, True, italic)
        elif it or it2:
            add_inline(par, (it or it2)[1:-1], size, bold, True)
        elif link:
            _run(par, ltext, size, bold, italic)
        pos = m.end()
    if pos < len(text):
        _run(par, text[pos:], size, bold, italic)


def _run(par, s, size, bold, italic):
    s = s.replace("\x02", "$")
    if not s:
        return
    r = par.add_run(s); r.bold = bold; r.italic = italic
    if size:
        r.font.size = Pt(size)


# ---------------------------------------------------------------- blocks
def equation(doc, tex):
    tag = None
    m = re.search(r"\\tag\{([^}]*)\}", tex)
    if m:
        tag = m.group(1); tex = (tex[:m.start()] + tex[m.end():]).strip()
    t = doc.add_table(rows=1, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    c0, c1 = t.rows[0].cells
    c0.width, c1.width = Cm(14.5), Cm(1.5)
    p = c0.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img = EQ_V6.get(tex)
    if img and img.exists():
        from PIL import Image
        w, _h = Image.open(img).size
        p.add_run().add_picture(str(img), width=Cm(min(14.0, w / 300 * 2.54 * 0.85)))
    else:
        buf = math_png(tex, 13, True)
        from PIL import Image
        w, _h = Image.open(buf).size; buf.seek(0)
        p.add_run().add_picture(buf, width=Cm(min(14.0, w / 300 * 2.54 * 0.85)))
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if tag:
        q.add_run(f"({tag})")
    for c in (c0, c1):
        c.vertical_alignment = 1
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def figure(doc, key, clean):
    stem, cap = FIG_ID[key]
    png = FIGS / f"{stem}.png"
    if not png.exists():
        return
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(png), width=Cm(15.5))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_inline(c, TAGS.sub("", cap) if clean else cap, size=10)


def table(doc, rows, clean):
    rows = [r for r in rows if not re.fullmatch(r"\s*\|?[\s:\-|]+\|[\s:\-|]*", r)]
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    ncol = max(len(r) for r in cells)
    t = doc.add_table(rows=len(cells), cols=ncol)
    t.style = "Table Grid"
    for i, r in enumerate(cells):
        for j in range(ncol):
            cell = t.rows[i].cells[j]
            txt = r[j] if j < len(r) else ""
            if clean:
                txt = TAGS.sub("", txt)
            p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            add_inline(p, txt, size=9.5, bold=(i == 0))
            if i == 0:
                cell_shade(cell, "E7ECF2")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def callout(doc, lines):
    text = " ".join(l.lstrip(">").strip() for l in lines).strip()
    head = text[:80].upper()
    fill = CALLOUT_FILL["red"] if ("⚠" in text[:120] or "BLOCK" in head) else (
        CALLOUT_FILL["flag"] if ("FLAG" in head or "DECISION" in head or "OPEN QUESTION" in head or "TO CONFIRM" in head)
        else CALLOUT_FILL["note"])
    paras = re.split(r"\n\s*>\s*\n", "\n".join(lines))
    for chunk in paras:
        t = " ".join(l.lstrip(">").strip() for l in chunk.split("\n")).strip()
        if not t:
            continue
        p = doc.add_paragraph(); shade(p, fill)
        p.paragraph_format.left_indent = Cm(0.4); p.paragraph_format.right_indent = Cm(0.4)
        add_inline(p, t, size=9.5)


def algorithm(doc, lines):
    rows = [l.rstrip() for l in lines if l.strip()]
    n = 0
    for i, l in enumerate(rows):
        p = doc.add_paragraph(); shade(p, "F2F2F2")
        p.paragraph_format.left_indent = Cm(0.6); p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.keep_with_next = i < len(rows) - 1
        s = l.strip()
        if i == 0:
            add_inline(p, s, size=10.5, bold=True)
        elif re.match(r"^(Input|Output)\s*:", s):
            add_inline(p, s, size=10.5)
        else:
            n += 1
            add_inline(p, f"{n}. " + re.sub(r"^\d+\.\s*", "", s), size=10.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def render(doc, md, clean, placed, fig_home):
    lines = md.replace("\r\n", "\n").split("\n")
    i, n = 0, len(lines)
    para: list[str] = []

    def flush():
        if not para:
            return
        text = " ".join(s.strip() for s in para)
        if clean:
            text = TAGS.sub("", text)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        add_inline(p, text)
        para.clear()
        for key in FIG_MENTION.findall(text):
            if key in FIG_ID and key not in placed:
                placed.add(key); figure(doc, key, clean)

    while i < n:
        ln = lines[i]; s = ln.strip()
        if not s:
            flush(); i += 1; continue
        if s.startswith("```"):
            flush()
            kind = s[3:].strip(); buf = []; i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            if kind == "algorithm":
                algorithm(doc, buf)
            else:
                for b in buf:
                    p = doc.add_paragraph(); r = p.add_run(b); r.font.name = "Consolas"; r.font.size = Pt(9)
            continue
        if s.startswith("$$"):
            flush()
            rest = s[2:]; buf = []
            if "$$" in rest:
                buf.append(rest[:rest.index("$$")]); i += 1
            else:
                buf.append(rest); i += 1
                while i < n and "$$" not in lines[i]:
                    buf.append(lines[i]); i += 1
                if i < n:
                    buf.append(lines[i][:lines[i].index("$$")]); i += 1
            equation(doc, " ".join(b.strip() for b in buf if b.strip()))
            continue
        if s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            doc.add_heading(re.sub(r"[*`]", "", s[level:].strip()), level=min(level, 4))
            i += 1; continue
        if s.startswith(">"):
            flush(); buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i]); i += 1
            body = " ".join(b.lstrip(">").strip() for b in buf)
            m = re.search(r"\[FIGURE (\w+) HERE\]", body)
            if m:
                if m.group(1) in FIG_ID and m.group(1) not in placed:
                    placed.add(m.group(1)); figure(doc, m.group(1), clean)
                continue
            if not clean:
                callout(doc, buf)
            continue
        if s.startswith("|"):
            flush(); buf = []
            while i < n and lines[i].strip().startswith("|"):
                buf.append(lines[i]); i += 1
            table(doc, buf, clean)
            continue
        if re.fullmatch(r"-{3,}|\*{3,}", s):
            flush(); i += 1; continue
        lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if lm:
            flush()
            item = [lm.group(3)]; i += 1
            while i < n and lines[i].strip() and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) \
                    and not lines[i].strip().startswith(("#", ">", "|", "$$", "```")):
                item.append(lines[i].strip()); i += 1
            text = " ".join(item)
            if clean:
                text = TAGS.sub("", text)
            style = "List Number" if lm.group(2)[0].isdigit() else "List Bullet"
            p = doc.add_paragraph(style=style)
            add_inline(p, text)
            for key in FIG_MENTION.findall(text):
                if key in FIG_ID and key not in placed:
                    placed.add(key); figure(doc, key, clean)
            continue
        para.append(ln); i += 1
    flush()


def references(doc, cited, bib):
    doc.add_heading("References", level=1)
    for entry in CI.reference_list_md(cited, bib).split("\n\n"):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
        add_inline(p, entry, size=10)


def build(files, out, title, clean, per_section=False):
    bib = CI.load_bib()
    doc = new_doc(title)
    if not per_section:
        t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = t.add_run(MM.TITLE); r.bold = True; r.font.size = Pt(16)
        s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
        s.add_run(("Manuscript, clean reading copy" if clean else "Working draft with editorial callouts")
                  + f" · {MM.JOURNAL} · revision {MM.git_rev()}").italic = True
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    cited, missing, placed = [], set(), set()
    for k, f in enumerate(files):
        md = CI.render(f.read_text(encoding="utf-8"), bib, cited, missing)
        render(doc, md, clean, placed, None)
        if f.stem == "05_results":
            for key in ("5", "6", "9", "9b", "S2"):
                if key not in placed:
                    placed.add(key); figure(doc, key, clean)
        if k < len(files) - 1:
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    if cited:
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        references(doc, cited, bib)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out, len(cited), sorted(missing), sorted(placed)


def main():
    files = sorted(SECTIONS.glob("*.md"))
    names = {"00": "Abstract", "01": "Introduction", "02": "Literature", "03": "Study_Area", "04": "Methodology",
             "05": "Results", "06": "Validation", "07": "Discussion", "08": "Conclusions"}
    for f in files:
        nn = f.stem[:2]
        out, nref, miss, figs = build([f], OUT / f"Section_{nn}_{names.get(nn, f.stem)}.docx",
                                      MM.SECTIONS.get(f.stem, (f.stem,))[0], clean=False, per_section=True)
        print(f"{out.name}: refs {nref}, figures {figs}, missing {miss}")
    for clean, name in ((False, "Kashmir_Manuscript_Working_Draft.docx"), (True, "Kashmir_Manuscript_Clean.docx")):
        out, nref, miss, figs = build(files, OUT / name, "Kashmir manuscript", clean=clean)
        print(f"{out.name}: refs {nref}, figures {figs}, missing {miss}")


if __name__ == "__main__":
    main()
