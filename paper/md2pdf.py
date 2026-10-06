r"""
md2pdf.py — a small, dependency-light Markdown -> PDF renderer for this repo.
==============================================================================

Built to typeset two things:

  1. `paper/Kashmir_Manuscript_Working_Draft.pdf` — the assembled manuscript
     (all eight sections, Prashant's and the co-authors', nothing removed).
  2. `paper/PENDING_DECISIONS.pdf` — the extreme-detail decision briefing.

It is deliberately NOT a general Markdown engine. It supports exactly the
constructs used by `paper/sections/*.md` and `paper/PENDING_DECISIONS.md`:

    #, ##, ###, ####        headings
    paragraphs              with **bold**, *italic*, `code`, [text](url)
    > blockquote            rendered as a tinted callout box (used for FLAGs;
                            an "editorial flag" tint is auto-detected)
    -, *, 1.                bullet / numbered lists (one level)
    |a|b|                   pipe tables with a --- separator row
    ---                     horizontal rule
    ```fence```             code block
    ```algorithm            ruled pseudocode box with line numbers (syntax: see
      title / steps ```     `algorithm_block` docstring)
    $$ ... $$               display equation (may span lines; \tag{n} -> "(n)")
    $...$                   inline maths (simple -> text markup, else an image)

Maths is delegated to `mathrender.py` (matplotlib mathtext, vector paths). It
handles \begin{cases|aligned}, \text, \tfrac, \big-delimiters etc. via a
pre-processor; an equation that cannot be parsed is drawn as a red flagged box
and recorded (see `math_failures()`), never a crash. `find_unrendered_math(pdf)`
scans a built PDF for raw TeX that leaked through. Currency (`US$ 40`, `US$0.05`)
is not maths: an opening `$` must not follow a capital letter/digit, must not be
followed by a space, and the closing `$` must not be followed by a digit. Write
`\$` for a literal dollar sign next to something that looks like maths.

Fonts: DejaVu (shipped with matplotlib) so that Greek letters, arrows and
mathematical operators in the prose survive. Helvetica's WinAnsi encoding
does not cover rho / kappa / tau / >= / -> and would silently emit black boxes.

Run:
    .venv/Scripts/python.exe paper/md2pdf.py --help
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mathrender as MR  # noqa: E402  (LaTeX-subset maths, see mathrender.py)

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

_FONTDIR = Path(matplotlib.__file__).parent / "mpl-data" / "fonts" / "ttf"

_FONTS = {
    "DejaSerif": "DejaVuSerif.ttf",
    "DejaSerif-Bold": "DejaVuSerif-Bold.ttf",
    "DejaSerif-Italic": "DejaVuSerif-Italic.ttf",
    "DejaSerif-BoldItalic": "DejaVuSerif-BoldItalic.ttf",
    "DejaSans": "DejaVuSans.ttf",
    "DejaSans-Bold": "DejaVuSans-Bold.ttf",
    "DejaSans-Italic": "DejaVuSans-Oblique.ttf",
    "DejaSans-BoldItalic": "DejaVuSans-BoldOblique.ttf",
    "DejaMono": "DejaVuSansMono.ttf",
    "DejaMono-Bold": "DejaVuSansMono-Bold.ttf",
}

_REGISTERED = False


def register_fonts() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    for name, fn in _FONTS.items():
        pdfmetrics.registerFont(TTFont(name, str(_FONTDIR / fn)))
    for fam in ("DejaSerif", "DejaSans"):
        pdfmetrics.registerFontFamily(
            fam,
            normal=fam,
            bold=f"{fam}-Bold",
            italic=f"{fam}-Italic",
            boldItalic=f"{fam}-BoldItalic",
        )
    pdfmetrics.registerFontFamily("DejaMono", normal="DejaMono", bold="DejaMono-Bold",
                                  italic="DejaMono", boldItalic="DejaMono-Bold")
    _REGISTERED = True


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

INK = colors.HexColor("#15161c")
MUTED = colors.HexColor("#565d70")
RULE = colors.HexColor("#c9ced8")
ACCENT = colors.HexColor("#0b6e4f")      # section headings
FLAG_BG = colors.HexColor("#fff6e8")     # editorial flag callout
FLAG_EDGE = colors.HexColor("#c8791a")
WARN_BG = colors.HexColor("#fdeceb")     # hard-blocker callout
WARN_EDGE = colors.HexColor("#9b2226")
NOTE_BG = colors.HexColor("#eef3fa")     # provenance / neutral callout
NOTE_EDGE = colors.HexColor("#3b6ea5")
CODE_BG = colors.HexColor("#f4f5f7")
TABLE_HEAD = colors.HexColor("#e8edf4")


def make_styles(base_size: float = 9.4):
    register_fonts()
    ss = getSampleStyleSheet()

    def S(name, **kw):
        kw.setdefault("parent", ss["Normal"])
        return ParagraphStyle(name, **kw)

    st = {}
    st["body"] = S("body", fontName="DejaSerif", fontSize=base_size,
                   leading=base_size * 1.48, textColor=INK, spaceAfter=5,
                   alignment=TA_JUSTIFY)
    st["body_l"] = S("body_l", parent=st["body"], alignment=0)
    st["h1"] = S("h1", fontName="DejaSans-Bold", fontSize=base_size + 5.6,
                 leading=base_size + 8.6, textColor=INK, spaceBefore=4, spaceAfter=7)
    st["h2"] = S("h2", fontName="DejaSans-Bold", fontSize=base_size + 1.8,
                 leading=base_size + 4.4, textColor=ACCENT, spaceBefore=11, spaceAfter=4)
    st["h3"] = S("h3", fontName="DejaSans-Bold", fontSize=base_size + 0.3,
                 leading=base_size + 3.0, textColor=INK, spaceBefore=8, spaceAfter=3)
    st["h4"] = S("h4", fontName="DejaSans-BoldItalic", fontSize=base_size - 0.3,
                 leading=base_size + 2.4, textColor=MUTED, spaceBefore=6, spaceAfter=2)
    st["callout"] = S("callout", fontName="DejaSerif", fontSize=base_size - 0.7,
                      leading=(base_size - 0.7) * 1.46, textColor=INK, spaceAfter=3,
                      alignment=0)
    st["li"] = S("li", parent=st["body"], alignment=0, spaceAfter=2.5)
    st["cell"] = S("cell", fontName="DejaSerif", fontSize=base_size - 1.6,
                   leading=(base_size - 1.6) * 1.35, textColor=INK)
    st["cellh"] = S("cellh", fontName="DejaSans-Bold", fontSize=base_size - 1.6,
                    leading=(base_size - 1.6) * 1.35, textColor=INK)
    st["code"] = S("code", fontName="DejaMono", fontSize=base_size - 1.8,
                   leading=(base_size - 1.8) * 1.38, textColor=INK)
    st["small"] = S("small", fontName="DejaSans", fontSize=base_size - 2.0,
                    leading=(base_size - 2.0) * 1.4, textColor=MUTED)
    st["title"] = S("title", fontName="DejaSans-Bold", fontSize=19, leading=23,
                    textColor=INK, alignment=TA_CENTER, spaceAfter=6)
    st["subtitle"] = S("subtitle", fontName="DejaSans", fontSize=11, leading=15,
                       textColor=MUTED, alignment=TA_CENTER, spaceAfter=4)
    return st


# ---------------------------------------------------------------------------
# Inline markdown -> reportlab mini-HTML
# ---------------------------------------------------------------------------

_ESCAPES = ((("&", "&amp;"), ("<", "&lt;"), (">", "&gt;")))


def _esc(s: str) -> str:
    for a, b in _ESCAPES:
        s = s.replace(a, b)
    return s


def inline(text: str, mono: str = "DejaMono", size: float = 9.3) -> str:
    """Convert inline markdown to reportlab markup. Code spans are protected
    from the emphasis pass so that `**` inside backticks survives. `$...$`
    maths is converted (see mathrender.py) and protected the same way; `size`
    is the font size of the paragraph the text will sit in (inline math
    images are scaled to it)."""
    holds: list[str] = []

    def _hold(m):
        holds.append(f'<font face="{mono}" size="-0.8">{_esc(m.group(1))}</font>')
        return f"\x00{len(holds) - 1}\x00"

    text = re.sub(r"`([^`]+)`", _hold, text)

    # maths: pandoc rules (opening $ not followed by space, closing $ not
    # followed by a digit, opening $ not preceded by a word char -> "US$ 40" and
    # "US$0.05 ... US$2.5" are currency, not maths). \$ is a literal dollar.
    if "$" in text:
        mholds: list[str] = []

        def _mhold(m):
            mholds.append(MR.math_to_markup(m.group(1), size, where=text[:60]))
            return f"\x01{len(mholds) - 1}\x01"

        text = text.replace(r"\$", "\x02")
        text = MR.DISPLAY_IN_TEXT.sub(_mhold, text)
        text = MR.INLINE_MATH.sub(_mhold, text)
        text = text.replace("\x02", "$")
    else:
        mholds = []
    text = _esc(text)

    # links -> "text" in blue (PDF link if absolute)
    def _link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith(("http://", "https://")):
            return f'<link href="{href}"><font color="#3b6ea5">{label}</font></link>'
        return f'<font color="#3b6ea5">{label}</font>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text, flags=re.S)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text, flags=re.S)
    text = re.sub(r"(?<![A-Za-z0-9_])_([^_]+)_(?![A-Za-z0-9_])", r"<i>\1</i>", text)

    for i, h in enumerate(mholds):
        text = text.replace(f"\x01{i}\x01", h)
    for i, h in enumerate(holds):
        text = text.replace(f"\x00{i}\x00", h)
    return text


# ---------------------------------------------------------------------------
# Block parsing
# ---------------------------------------------------------------------------

def _classify_callout(text: str):
    """Pick a tint for a blockquote from its opening marker."""
    head = text[:220].upper()
    if "\u26a0" in text[:400] or "MUST NOT" in head or "BLOCKER" in head:
        return WARN_BG, WARN_EDGE
    if "FLAG" in head or "DECISION" in head or "OPEN QUESTION" in head:
        return FLAG_BG, FLAG_EDGE
    return NOTE_BG, NOTE_EDGE


def _callout(lines: list[str], st, width: float):
    body = "\n".join(lines)
    bg, edge = _classify_callout(body)
    # split the quote into its own paragraphs on blank lines
    paras, buf = [], []
    for ln in lines:
        if not ln.strip():
            if buf:
                paras.append(" ".join(buf))
                buf = []
        else:
            buf.append(ln.strip())
    if buf:
        paras.append(" ".join(buf))

    flow = []
    for i, p in enumerate(paras):
        if p.lstrip().startswith(("- ", "* ")):
            flow.append(Paragraph("\u2022 " + inline(p.lstrip()[2:], size=st["callout"].fontSize), st["callout"]))
        else:
            flow.append(Paragraph(inline(p, size=st["callout"].fontSize), st["callout"]))
        if i < len(paras) - 1:
            flow.append(Spacer(1, 2.5))

    t = Table([[flow]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, edge),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#d9d9d9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _table(rows: list[list[str]], st, width: float):
    header, body_rows = rows[0], rows[1:]
    ncol = max(len(r) for r in rows)
    header = header + [""] * (ncol - len(header))
    body_rows = [r + [""] * (ncol - len(r)) for r in body_rows]

    # column widths proportional to max content length, floor 8% each
    lens = [max(len(r[i]) for r in rows) for i in range(ncol)]
    total = sum(lens) or 1
    frac = [max(0.08, l / total) for l in lens]
    s = sum(frac)
    colw = [width * f / s for f in frac]

    data = [[Paragraph(inline(c, size=st["cellh"].fontSize), st["cellh"]) for c in header]]
    for r in body_rows:
        data.append([Paragraph(inline(c, size=st["cell"].fontSize), st["cell"]) for c in r])

    t = Table(data, colWidths=colw, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, RULE),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dfe3ea")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#fafbfc")))
    t.setStyle(TableStyle(style))
    return t


_TABLE_SEP = re.compile(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$")


def _split_row(line: str) -> list[str]:
    ln = line.strip()
    if ln.startswith("|"):
        ln = ln[1:]
    if ln.endswith("|"):
        ln = ln[:-1]
    return [c.strip() for c in ln.split("|")]


def render_markdown(md: str, st, width: float, heading_page_breaks: bool = False):
    """Return a list of platypus flowables for a markdown string."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list = []
    i, n = 0, len(lines)
    first_h1 = True

    while i < n:
        ln = lines[i]
        stripped = ln.strip()

        # ---- fenced code / algorithm ------------------------------------
        if stripped.startswith("```"):
            kind = stripped[3:].strip().lower()
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            if kind == "algorithm":
                out += [Spacer(1, 3), KeepTogether([algorithm_block(buf, st, width)]), Spacer(1, 7)]
                continue
            txt = "<br/>".join(_esc(b).replace(" ", "&nbsp;") for b in buf)
            t = Table([[Paragraph(txt, st["code"])]], colWidths=[width])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.4, RULE),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            out += [Spacer(1, 3), t, Spacer(1, 6)]
            continue

        # ---- blank -------------------------------------------------------
        if not stripped:
            i += 1
            continue

        # ---- display equation $$ ... $$ ----------------------------------
        if stripped.startswith("$$"):
            rest = stripped[2:]
            buf = []
            if "$$" in rest:                       # one-line equation
                buf.append(rest[:rest.index("$$")])
                i += 1
            else:
                buf.append(rest)
                i += 1
                while i < n and "$$" not in lines[i]:
                    buf.append(lines[i])
                    i += 1
                if i < n:
                    buf.append(lines[i][:lines[i].index("$$")])
                    i += 1
            where = f"line {i}"
            fl = MR.display_equation("\n".join(buf), st["body"].fontSize,
                                     number_font="DejaSerif", where=where)
            out += [Spacer(1, 2), fl, Spacer(1, 3)]
            continue

        # ---- horizontal rule --------------------------------------------
        if re.fullmatch(r"-{3,}|\*{3,}|_{3,}", stripped):
            out += [Spacer(1, 4),
                    HRFlowable(width="100%", thickness=0.6, color=RULE),
                    Spacer(1, 6)]
            i += 1
            continue

        # ---- heading -----------------------------------------------------
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level, txt = len(m.group(1)), m.group(2).strip()
            key = {1: "h1", 2: "h2", 3: "h3"}.get(level, "h4")
            if level == 1:
                if heading_page_breaks and not first_h1:
                    out.append(PageBreak())
                first_h1 = False
                out.append(Paragraph(inline(txt, size=st["h1"].fontSize), st["h1"]))
                out.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                                      spaceBefore=1, spaceAfter=7))
            else:
                out.append(CondPageBreak(22 * mm if level == 2 else 14 * mm))
                out.append(Paragraph(inline(txt, size=st[key].fontSize), st[key]))
            i += 1
            continue

        # ---- blockquote / callout ---------------------------------------
        if stripped.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out += [Spacer(1, 3), _callout(buf, st, width), Spacer(1, 7)]
            continue

        # ---- table -------------------------------------------------------
        if "|" in stripped and i + 1 < n and _TABLE_SEP.match(lines[i + 1]):
            rows = [_split_row(lines[i])]
            i += 2
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i]))
                i += 1
            out += [Spacer(1, 4), _table(rows, st, width), Spacer(1, 8)]
            continue

        # ---- list --------------------------------------------------------
        mlist = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", ln)
        if mlist:
            ordered = bool(re.match(r"\d", mlist.group(2)))
            items = []
            while i < n:
                mm2 = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", lines[i])
                if not mm2:
                    # continuation line of the current item
                    if items and lines[i].startswith(("  ", "\t")) and lines[i].strip():
                        items[-1] += " " + lines[i].strip()
                        i += 1
                        continue
                    break
                if bool(re.match(r"\d", mm2.group(2))) != ordered:
                    break
                items.append(mm2.group(3).strip())
                i += 1
            lf = ListFlowable(
                [ListItem(Paragraph(inline(t, size=st["li"].fontSize), st["li"]), leftIndent=13,
                          value=(k + 1) if ordered else None)
                 for k, t in enumerate(items)],
                bulletType="1" if ordered else "bullet",
                bulletFontName="DejaSerif",
                bulletFontSize=st["li"].fontSize - 0.5,
                start=1 if ordered else None,
                leftIndent=13,
            )
            out += [lf, Spacer(1, 5)]
            continue

        # ---- paragraph ---------------------------------------------------
        buf = [stripped]
        i += 1
        while i < n:
            s2 = lines[i].strip()
            if (not s2 or s2.startswith((">", "#", "```", "$$"))
                    or re.fullmatch(r"-{3,}|\*{3,}|_{3,}", s2)
                    # a list may interrupt a paragraph only as a bullet or "1." --
                    # a wrapped line that merely starts "614) ..." is prose
                    or re.match(r"^(\s*)([-*]|1[.)])\s+", lines[i])
                    or ("|" in s2 and i + 1 < n and _TABLE_SEP.match(lines[i + 1]))):
                break
            buf.append(s2)
            i += 1
        out.append(Paragraph(inline(" ".join(buf), size=st["body"].fontSize), st["body"]))

    return out


# ---------------------------------------------------------------------------
# Algorithm blocks
# ---------------------------------------------------------------------------

_ALG_LABEL = re.compile(r"^(Input|Output|Require|Ensure|Data|Result)\s*:\s*(.*)$", re.I)
_ALG_KW_START = re.compile(
    r"^(for each|for all|foreach|for|while|if|else if|elif|else|end for|end if|end while|"
    r"repeat|until|return|break|continue)\b")
_ALG_KW_END = re.compile(r"\b(do|then)(\s*:?)$")
ALG_BG = colors.HexColor("#f8f9fb")


def algorithm_block(buf: list[str], st, width: float):
    """Ruled-box pseudocode. Syntax (inside a fenced block):

        ```algorithm
        Algorithm 1 - Permit consolidation        <- first non-empty line = title
        Input: candidate routes $R$; threshold $\\theta$      <- unnumbered label line
        Group $R$ by corridor key                 <- numbered 1, 2, 3 ... automatically
        for each cluster $C$ do                   <- keywords at line start are bolded
          merge members of $C$ into the trunk     <- deeper indentation = nested
        return the trunk set                      <- an explicit "3." prefix is stripped
        Output: 186 active routes
        ```

    Labels recognised: Input, Output, Require, Ensure, Data, Result. Keywords
    bolded at line start: for, for each, while, if, else if, else, end for/if/
    while, repeat, until, return, break, continue; a trailing `do` / `then` is
    bolded too. Anything already wrapped in ** is left alone. A trailing
    `// comment` is shown muted. Content lines accept all inline markdown and
    `$...$` maths. Indentation is relative: the distinct indents used become
    nesting levels 0, 1, 2 ... (any consistent spacing works).
    """
    from reportlab.platypus import Paragraph as P
    rows = [ln.rstrip().replace("\t", "    ") for ln in buf if ln.strip()]
    if not rows:
        return Spacer(1, 1)
    title = rows[0].strip()
    body = rows[1:]
    indents = sorted({len(r) - len(r.lstrip()) for r in body}) or [0]
    level_of = {ind: k for k, ind in enumerate(indents)}
    fs = st["body"].fontSize - 0.4
    base = ParagraphStyle("alg", parent=st["body"], fontSize=fs, leading=fs * 1.42,
                          alignment=0, spaceAfter=0)
    numst = ParagraphStyle("algn", parent=st["small"], fontName="DejaMono", fontSize=fs - 1.6,
                           leading=fs * 1.42, alignment=2, textColor=MUTED)
    titlest = ParagraphStyle("algt", parent=st["body"], fontName="DejaSans-Bold", fontSize=fs,
                             leading=fs * 1.4, alignment=0, spaceAfter=0)
    data = [[P(inline(title, size=fs), titlest), ""]]
    num = 0
    for r in body:
        ind = len(r) - len(r.lstrip())
        lvl = level_of.get(ind, 0)
        txt = r.strip()
        m = _ALG_LABEL.match(txt)
        if m:
            data.append(["", P(f"<b>{m.group(1).capitalize()}:</b> " + inline(m.group(2), size=fs), base)])
            continue
        txt = re.sub(r"^\d+[.):]\s+", "", txt)
        com = ""
        if "//" in txt:
            txt, com = txt.split("//", 1)
            txt = txt.rstrip()
        if not txt.startswith("**"):
            txt = _ALG_KW_START.sub(lambda mm: f"**{mm.group(1)}**", txt, count=1)
            txt = _ALG_KW_END.sub(lambda mm: f"**{mm.group(1)}**{mm.group(2)}", txt, count=1)
        html = inline(txt, size=fs)
        if com.strip():
            html += f' <font color="#565d70"><i>// {inline(com.strip(), size=fs)}</i></font>'
        num += 1
        stl = ParagraphStyle("algl", parent=base, leftIndent=12 * lvl)
        data.append([P(str(num), numst), P(html, stl)])
    t = Table(data, colWidths=[9 * mm, width - 9 * mm])
    last = len(data) - 1
    t.setStyle(TableStyle([
        ("SPAN", (0, 0), (1, 0)),
        ("BACKGROUND", (0, 0), (-1, -1), ALG_BG),
        ("LINEABOVE", (0, 0), (-1, 0), 1.3, INK),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, INK),
        ("LINEBELOW", (0, last), (-1, last), 1.3, INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("TOPPADDING", (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ]))
    return t


# ---------------------------------------------------------------------------
# Build guard: maths that survived into the PDF as source
# ---------------------------------------------------------------------------

_SURVIVOR = re.compile(r"(?<!US)\$|\\[A-Za-z]+|@@ENV|\\begin\{|\[EQUATION NOT RENDERED\]")


def find_unrendered_math(pdf_path) -> list[dict]:
    """Extract text from a built PDF and report raw TeX that leaked through:
    any `$` (except currency written `US$`), any `\\macro` (e.g. \\frac, \\tag,
    \\text{, \\rho, \\begin{), and the failure-box banner. Returns a list of
    {page, token, context}; empty list = clean."""
    from pypdf import PdfReader
    hits: list[dict] = []
    reader = PdfReader(str(pdf_path))
    for pno, page in enumerate(reader.pages, 1):
        try:
            txt = page.extract_text() or ""
        except Exception as e:  # pragma: no cover
            hits.append({"page": pno, "token": "<extract failed>", "context": str(e)})
            continue
        flat = " ".join(txt.split())
        for m in _SURVIVOR.finditer(flat):
            a, b = max(0, m.start() - 35), min(len(flat), m.end() + 45)
            hits.append({"page": pno, "token": m.group(0), "context": flat[a:b]})
    return hits


def math_failures() -> list[dict]:
    """Equations/inline maths that fell back to the flagged-source rendering
    since the last `MR.reset_reports()`."""
    return list(MR.MATH_FAILURES)


# ---------------------------------------------------------------------------
# Document scaffolding
# ---------------------------------------------------------------------------

def build_pdf(out_path: Path, flowables, title: str, footer_left: str,
              margins_mm: float = 18.0, landscape_mode: bool = False):
    register_fonts()
    pagesize = A4 if not landscape_mode else (A4[1], A4[0])
    doc = SimpleDocTemplate(
        str(out_path), pagesize=pagesize,
        leftMargin=margins_mm * mm, rightMargin=margins_mm * mm,
        topMargin=(margins_mm - 2) * mm, bottomMargin=(margins_mm - 3) * mm,
        title=title, author="Kashmir transit rationalisation study",
        subject=title,
    )

    def _page(canvas, _doc):
        canvas.saveState()
        canvas.setFont("DejaSans", 6.8)
        canvas.setFillColor(MUTED)
        y = (margins_mm - 9) * mm
        canvas.drawString(margins_mm * mm, y, footer_left)
        canvas.drawRightString(pagesize[0] - margins_mm * mm, y, f"p. {canvas.getPageNumber()}")
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.3)
        canvas.line(margins_mm * mm, y + 3.4 * mm,
                    pagesize[0] - margins_mm * mm, y + 3.4 * mm)
        canvas.restoreState()

    doc.build(flowables, onFirstPage=_page, onLaterPages=_page)
    return out_path


def frame_width(margins_mm: float = 18.0, landscape_mode: bool = False) -> float:
    w = A4[0] if not landscape_mode else A4[1]
    return w - 2 * margins_mm * mm


__all__ = ["render_markdown", "make_styles", "build_pdf", "frame_width",
           "inline", "register_fonts", "find_unrendered_math", "math_failures",
           "algorithm_block", "MR", "INK", "MUTED", "RULE", "ACCENT",
           "KeepTogether", "Paragraph", "Spacer", "PageBreak", "Table",
           "TableStyle", "HRFlowable"]
