"""
mathrender.py -- LaTeX-subset maths for the md2pdf ReportLab pipeline.
======================================================================

No LaTeX installation is needed. Maths is typeset with matplotlib's `mathtext`
engine (DejaVu Serif fontset, matching the body face) and drawn either as
true vector paths on the PDF canvas (display equations) or as a 600-dpi PNG
inline image (complex inline maths). Simple inline maths (a symbol with a
sub/superscript, Greek letters, numbers with units, a relation) is converted
to ordinary ReportLab markup instead, so it flows like text.

mathtext lacks a good deal of LaTeX, so a pre-processor maps what the
manuscript actually uses:

    \\tag{n}                       stripped; becomes the right-hand "(n)" number
    \\text{..} \\textrm{..}          -> \\mathrm{..} with literal spaces kept
    \\operatorname{..}              -> \\mathrm{..}
    \\tfrac \\dfrac                 -> \\frac
    \\le \\ge \\lVert \\rVert        -> \\leq \\geq \\Vert \\Vert
    \\big( \\Big[ \\bigl\\lceil ..    -> matched pairs become \\left..\\right (auto-sized);
                                   unmatched ones become the plain delimiter
    \\bar y                         -> \\bar{y}   (and \\hat/\\tilde/\\vec/\\dot)
    \\begin{cases} .. \\end{cases}  -> left brace + stacked rows, laid out here
    \\begin{aligned|align|gathered|array|split} -> stacked, column-aligned rows
    a \\\\ b  (outside an env)       -> stacked, centred lines
    \\\\[2pt]                        -> row break (the optional length is ignored)

An equation that still cannot be parsed never crashes the build: it is drawn as
monospace source inside a red box, and appended to `MATH_FAILURES` so the caller
can fail loudly. Equations scaled down to fit the line are noted in `MATH_NOTES`.
"""
from __future__ import annotations

import base64
import functools
import io
import re
from dataclasses import dataclass, field

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "dejavuserif"

import numpy as np  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from matplotlib.textpath import TextPath, text_to_path  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.platypus import Flowable  # noqa: E402

BS = chr(92)  # backslash
DBS = BS + BS

MATH_FAILURES: list[dict] = []
MATH_NOTES: list[dict] = []

INK = colors.HexColor("#15161c")
INK_HEX = "#15161c"


def reset_reports() -> None:
    MATH_FAILURES.clear()
    MATH_NOTES.clear()


class MathError(Exception):
    pass


# ---------------------------------------------------------------------------
# TeX pre-processing (mathtext dialect)
# ---------------------------------------------------------------------------

_BIG_RE = re.compile(
    re.escape(BS) + r"(?:big|Big|bigg|Bigg)([lrm]?)\s*"
    r"(" + re.escape(BS) + r"[A-Za-z]+|" + re.escape(BS) + r"[{}|]|[()\[\]|.])"
)
_OPENERS = {"(", "[", BS + "{", BS + "lceil", BS + "lfloor", BS + "langle",
            BS + "lbrace", BS + "lvert", BS + "lVert"}
_CLOSERS = {")": "(", "]": "[", BS + "}": BS + "{", BS + "rceil": BS + "lceil",
            BS + "rfloor": BS + "lfloor", BS + "rangle": BS + "langle",
            BS + "rbrace": BS + "lbrace", BS + "rvert": BS + "lvert",
            BS + "rVert": BS + "lVert"}


def _brace_depths(s: str) -> list[int]:
    """Depth of `{}` nesting before each character (escaped braces ignored)."""
    d, out, i = 0, [], 0
    while i < len(s):
        out.append(d)
        c = s[i]
        if c == BS and i + 1 < len(s):
            out.append(d)
            i += 2
            continue
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
        i += 1
    return out


def _sizes_to_left_right(s: str, pair: bool) -> str:
    """Replace \\big-family delimiters. pair=True: matched pairs -> \\left/\\right;
    pair=False: every one becomes its plain delimiter."""
    matches = list(_BIG_RE.finditer(s))
    if not matches:
        return s
    depths = _brace_depths(s)
    repl: dict[int, str] = {}      # match index -> replacement
    stack: list[tuple[int, str, int]] = []
    for k, m in enumerate(matches):
        suffix, delim = m.group(1), m.group(2)
        plain = delim
        repl[k] = plain
        if not pair:
            continue
        dep = depths[m.start()] if m.start() < len(depths) else 0
        kind = None
        if suffix == "l":
            kind = "open"
        elif suffix == "r":
            kind = "close"
        elif delim in _OPENERS:
            kind = "open"
        elif delim in _CLOSERS:
            kind = "close"
        elif delim in ("|", BS + "|", BS + "vert", BS + "Vert"):
            kind = "close" if stack and stack[-1][1] == delim else "open"
        if kind == "open":
            stack.append((k, delim, dep))
        elif kind == "close":
            want = _CLOSERS.get(delim, delim)
            if stack and stack[-1][1] == want and stack[-1][2] == dep:
                ok, _, _ = stack.pop()
                repl[ok] = BS + "left" + matches[ok].group(2)
                repl[k] = BS + "right" + delim
            elif stack and stack[-1][1] == delim and delim in ("|", BS + "|") and stack[-1][2] == dep:
                ok, _, _ = stack.pop()
                repl[ok] = BS + "left" + matches[ok].group(2)
                repl[k] = BS + "right" + delim
    out, last = [], 0
    for k, m in enumerate(matches):
        out.append(s[last:m.start()])
        out.append(repl[k])
        last = m.end()
    out.append(s[last:])
    return "".join(out)


def _balanced_arg(s: str, start: int) -> tuple[str, int]:
    """s[start] == '{' -> (content, index after the closing brace)."""
    d = 0
    for i in range(start, len(s)):
        if s[i] == BS:
            continue
        if s[i] == "{" and (i == 0 or s[i - 1] != BS):
            d += 1
        elif s[i] == "}" and (i == 0 or s[i - 1] != BS):
            d -= 1
            if d == 0:
                return s[start + 1:i], i + 1
    raise MathError("unbalanced braces")


def _map_text_macros(s: str) -> str:
    """\\text{a b} -> \\mathrm{a\\ b}; \\operatorname{x} -> \\mathrm{x}."""
    pat = re.compile(re.escape(BS) + r"(text|textrm|textnormal|mbox|operatorname\*?|textit|textbf)\s*\{")
    out, pos = [], 0
    while True:
        m = pat.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        out.append(s[pos:m.start()])
        content, end = _balanced_arg(s, m.end() - 1)
        name = m.group(1)
        content = _map_text_macros(content)
        if name.startswith("operatorname"):
            out.append(BS + "mathrm{" + content + "}")
        else:
            cc = content.replace(" ", BS + " ")
            fam = {"textit": "mathit", "textbf": "mathbf"}.get(name, "mathrm")
            out.append(BS + fam + "{" + cc + "}")
        pos = end
    return "".join(out)


_FUNCS = "min|max|sup|inf|lim|log|ln|exp|arg|det|gcd"
_FUNC_RE = re.compile(
    re.escape(BS) + r"(" + _FUNCS + r")(?![A-Za-z])"
    r"((?:_\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|_[A-Za-z0-9])?(?:\^\{[^{}]*\}|\^[A-Za-z0-9])?)"
    r"\s*(?=[A-Za-z]|" + re.escape(BS) + r"[A-Za-z])")


def _space_after_functions(s: str) -> str:
    """TeX puts a thin space between an operator name and a following letter
    (min z); mathtext does not, so add one."""
    return _FUNC_RE.sub(lambda m: BS + m.group(1) + m.group(2) + BS + ",", s)


_ACCENTS = ("bar", "hat", "tilde", "vec", "dot", "ddot", "check", "breve", "acute", "grave")


def preprocess(tex: str, pair_delims: bool = True, display: bool = False) -> str:
    s = " ".join(tex.split())
    s = re.sub(re.escape(BS) + r"(?:nonumber|notag)\b", lambda _m: "", s)
    s = re.sub(re.escape(BS) + r"label\{[^}]*\}", lambda _m: "", s)
    s = _map_text_macros(s)
    s = _sizes_to_left_right(s, pair_delims)
    s = re.sub(re.escape(BS) + r"tfrac(?![A-Za-z])", lambda _m: BS + ("dfrac" if display else "TFRAC"), s)
    s = re.sub(re.escape(BS) + r"dfrac(?![A-Za-z])", lambda _m: BS + "frac", s)
    s = re.sub(re.escape(BS) + r"frac(?![A-Za-z])", lambda _m: BS + ("dfrac" if display else "frac"), s)
    s = s.replace(BS + "TFRAC", BS + "frac")
    s = re.sub(re.escape(BS) + r"le(?![A-Za-z])", lambda _m: BS + "leq", s)
    s = re.sub(re.escape(BS) + r"ge(?![A-Za-z])", lambda _m: BS + "geq", s)
    s = re.sub(re.escape(BS) + r"[lr]Vert(?![A-Za-z])", lambda _m: BS + "Vert", s)
    s = re.sub(re.escape(BS) + r"lbrace(?![A-Za-z])", lambda _m: BS + "{", s)
    s = re.sub(re.escape(BS) + r"rbrace(?![A-Za-z])", lambda _m: BS + "}", s)
    s = re.sub(re.escape(BS) + r"displaystyle\s*", lambda _m: "", s)
    s = re.sub(re.escape(BS) + r"limits(?![A-Za-z])", lambda _m: "", s)
    s = _space_after_functions(s)
    # accent macros followed by a bare single token: \bar y -> \bar{y}
    for acc in _ACCENTS:
        s = re.sub(re.escape(BS) + acc + r"\s+([A-Za-z0-9]|" + re.escape(BS) + r"[A-Za-z]+)",
                   lambda m, a=acc: BS + a + "{" + m.group(1) + "}", s)
    return s


# ---------------------------------------------------------------------------
# Boxes: vector content with a baseline
# ---------------------------------------------------------------------------

@dataclass
class Item:
    verts: np.ndarray
    codes: np.ndarray
    stroke: float = 0.0          # 0 = filled outline, >0 = stroked polyline width


@dataclass
class Box:
    w: float
    asc: float
    desc: float
    items: list = field(default_factory=list)

    def shifted(self, dx: float, dy: float) -> list:
        out = []
        for it in self.items:
            v = it.verts.copy()
            v[:, 0] += dx
            v[:, 1] += dy
            out.append(Item(v, it.codes, it.stroke))
        return out


def _empty(w: float = 0.0) -> Box:
    return Box(w, 0.0, 0.0, [])


@functools.lru_cache(maxsize=4096)
def _mathtext_box(tex_pp: str, fs: float) -> Box:
    """Render one preprocessed mathtext fragment to a Box (raises MathError)."""
    if not tex_pp.strip():
        return _empty()
    s = "$" + tex_pp + "$"
    fp = FontProperties(size=fs)
    try:
        w, h, d = text_to_path.get_text_width_height_descent(s, fp, True)
        tp = TextPath((0, 0), s, size=fs, prop=fp)
    except Exception as e:  # mathtext raises ValueError with a long message
        msg = [ln for ln in str(e).strip().splitlines() if ln.strip()]
        raise MathError((msg[-1] if msg else repr(e))[:140] + "  <<" + tex_pp[:60] + ">>")
    verts = np.array(tp.vertices, dtype=float)
    codes = np.array(tp.codes, dtype=np.uint8)
    asc = max(h - d, 0.0)
    if len(verts):
        asc = max(asc, float(verts[:, 1].max()))
        d = max(d, float(-verts[:, 1].min()))
    return Box(w, asc, d, [Item(verts, codes)])


def tex_box(tex: str, fs: float, display: bool = True) -> Box:
    """Preprocess and render, retrying with plain delimiters if \\left/\\right fail."""
    try:
        return _mathtext_box(preprocess(tex, True, display), fs)
    except MathError:
        return _mathtext_box(preprocess(tex, False, display), fs)


def _hcat(parts: list[tuple[Box, float]], fs: float) -> Box:
    """parts: (box, gap_before). Baseline aligned."""
    x = 0.0
    items, asc, desc = [], 0.0, 0.0
    for b, gap in parts:
        x += gap
        items += b.shifted(x, 0.0)
        x += b.w
        asc, desc = max(asc, b.asc), max(desc, b.desc)
    return Box(x, asc, desc, items)


def _vstack(lines: list[Box], fs: float, align: str = "center", lead: float = 1.5,
            base_to_first: bool = True) -> Box:
    """Stack boxes top-to-bottom. Returns a box whose baseline is the first line's."""
    if not lines:
        return _empty()
    W = max(b.w for b in lines)
    items = []
    y = 0.0           # baseline of current line relative to first baseline (downwards negative)
    prev_desc = 0.0
    tops = []
    for k, b in enumerate(lines):
        asc = max(b.asc, 0.72 * fs)
        desc = max(b.desc, 0.22 * fs)
        if k:
            y -= max(prev_desc + asc + 0.30 * fs, lead * fs)
        x = {"center": (W - b.w) / 2, "left": 0.0, "right": W - b.w}[align]
        items += b.shifted(x, y)
        tops.append((y, asc, desc))
        prev_desc = desc
    asc_total = tops[0][1]
    desc_total = -(tops[-1][0]) + tops[-1][2]
    return Box(W, asc_total, desc_total, items)


def _brace(H: float, fs: float) -> Box:
    """A left curly brace of total height H, baseline-agnostic (bottom at y=0)."""
    bw = 0.42 * fs
    m = H / 2
    v = [
        (bw, H), (bw * 0.75, H), (bw * 0.5, H - bw * 0.25), (bw * 0.5, H - bw * 0.5),
        (bw * 0.5, m + bw * 0.5),
        (bw * 0.5, m + bw * 0.25), (bw * 0.25, m), (0.0, m),
        (bw * 0.25, m), (bw * 0.5, m - bw * 0.25), (bw * 0.5, m - bw * 0.5),
        (bw * 0.5, bw * 0.5),
        (bw * 0.5, bw * 0.25), (bw * 0.75, 0.0), (bw, 0.0),
    ]
    c = [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
         MPath.LINETO,
         MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
         MPath.CURVE4, MPath.CURVE4, MPath.CURVE4,
         MPath.LINETO,
         MPath.CURVE4, MPath.CURVE4, MPath.CURVE4]
    return Box(bw, 0.0, 0.0, [Item(np.array(v, float), np.array(c, np.uint8), stroke=0.055 * fs + 0.25)])


_ENV_RE = re.compile(
    re.escape(BS) + r"begin\{(cases|aligned|align\*?|gathered|split|array|matrix|rcases)\}"
    r"(?:\{[^}]*\})?(.*?)" + re.escape(BS) + r"end\{\1\}", re.S)
_ROWSEP = re.compile(re.escape(DBS) + r"(?:\[[^\]]*\])?")


def _env_box(name: str, body: str, fs: float) -> Box:
    rows = [r for r in _ROWSEP.split(body) if r.strip()]
    if not rows:
        return _empty()
    cells = [[tex_box(c.strip(), fs) for c in re.split(r"(?<!" + re.escape(BS) + r")&", r)] for r in rows]
    ncol = max(len(r) for r in cells)
    colw = [max((r[j].w for r in cells if j < len(r)), default=0.0) for j in range(ncol)]
    if name in ("cases", "rcases"):
        aligns, sep = ["left"] * ncol, 1.1 * fs
    elif name in ("aligned", "align", "align*", "split"):
        aligns = ["right" if j % 2 == 0 else "left" for j in range(ncol)]
        sep = 0.0
    elif name == "gathered":
        aligns, sep = ["center"] * ncol, 0.0
    else:
        aligns, sep = ["center"] * ncol, 1.0 * fs
    xs, x = [], 0.0
    for j in range(ncol):
        xs.append(x)
        x += colw[j] + (sep if j < ncol - 1 else 0.0)
    total_w = x
    items, y = [], 0.0
    prev_desc, spans = 0.0, []
    for k, r in enumerate(cells):
        asc = max([c.asc for c in r] + [0.72 * fs])
        desc = max([c.desc for c in r] + [0.22 * fs])
        if k:
            y -= max(prev_desc + asc + 0.32 * fs, 1.5 * fs)
        for j, c in enumerate(r):
            dx = {"left": 0.0, "right": colw[j] - c.w, "center": (colw[j] - c.w) / 2}[aligns[j]]
            items += c.shifted(xs[j] + dx, y)
        spans.append((y, asc, desc))
        prev_desc = desc
    top = spans[0][0] + spans[0][1]
    bottom = spans[-1][0] - spans[-1][2]
    H = top - bottom
    pad = 0.10 * fs
    if name == "cases":
        br = _brace(H + 2 * pad, fs)
        gap = 0.22 * fs
        all_items = br.shifted(0.0, bottom - pad) + [
            Item(i.verts + np.array([br.w + gap, 0.0]), i.codes, i.stroke) for i in items]
        w = br.w + gap + total_w
    elif name == "rcases":
        w = total_w
        all_items = items
    else:
        w, all_items = total_w, items
    # centre the whole block vertically on the math axis
    axis = 0.27 * fs
    centre = (top + bottom) / 2
    shift = axis - centre
    shifted = []
    for it in all_items:
        v = it.verts.copy()
        v[:, 1] += shift
        shifted.append(Item(v, it.codes, it.stroke))
    return Box(w, top + shift + pad, -(bottom + shift) + pad, shifted)


def _line_box(line: str, envs: dict, fs: float) -> Box:
    """A line of tex possibly containing ENV placeholders."""
    pieces = re.split(r"(@@ENV\d+@@)", line)
    parts: list[tuple[Box, float]] = []
    prev_env = False
    for p in pieces:
        if not p.strip():
            continue
        m = re.fullmatch(r"@@ENV(\d+)@@", p)
        if m:
            parts.append((envs[int(m.group(1))], 0.35 * fs if parts else 0.0))
            prev_env = True
        else:
            parts.append((tex_box(p, fs), 0.12 * fs if prev_env else 0.0))
            prev_env = False
    return _hcat(parts, fs) if parts else _empty()


_TAG_RE = re.compile(re.escape(BS) + r"tag\*?\s*\{([^}]*)\}")


def split_tag(tex: str) -> tuple[str, str | None]:
    m = _TAG_RE.search(tex)
    if not m:
        return tex, None
    return (tex[:m.start()] + tex[m.end():]).strip(), m.group(1).strip()


def display_box(tex: str, fs: float) -> Box:
    """tex has no \\tag. Handles environments and top-level line breaks."""
    envs: dict[int, Box] = {}

    def _sub(m):
        k = len(envs)
        envs[k] = _env_box(m.group(1), m.group(2), fs)
        return f"@@ENV{k}@@"

    t = _ENV_RE.sub(_sub, tex)
    t = _map_text_macros(t) if False else t
    lines = [ln for ln in _ROWSEP.split(t) if ln.strip()]
    boxes = [_line_box(ln, envs, fs) for ln in lines]
    if len(boxes) == 1:
        return boxes[0]
    return _vstack(boxes, fs, "center")


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

def _draw_items(canv, items: list[Item]) -> None:
    for it in items:
        p = canv.beginPath()
        v, c = it.verts, it.codes
        i, n = 0, len(c)
        cur = (0.0, 0.0)
        start = None
        while i < n:
            code = c[i]
            if code == MPath.MOVETO:
                p.moveTo(*v[i])
                cur = tuple(v[i])
                start = cur
                i += 1
            elif code == MPath.LINETO:
                p.lineTo(*v[i])
                cur = tuple(v[i])
                i += 1
            elif code == MPath.CURVE3:
                cx, cy = v[i]
                ex, ey = v[i + 1]
                p.curveTo(cur[0] + 2 / 3 * (cx - cur[0]), cur[1] + 2 / 3 * (cy - cur[1]),
                          ex + 2 / 3 * (cx - ex), ey + 2 / 3 * (cy - ey), ex, ey)
                cur = (ex, ey)
                i += 2
            elif code == MPath.CURVE4:
                p.curveTo(*v[i], *v[i + 1], *v[i + 2])
                cur = tuple(v[i + 2])
                i += 3
            elif code == MPath.CLOSEPOLY:
                p.close()
                i += 1
            else:       # STOP / unknown
                i += 1
        if it.stroke > 0:
            canv.setLineWidth(it.stroke)
            canv.setLineCap(1)
            canv.drawPath(p, stroke=1, fill=0)
        else:
            canv.drawPath(p, stroke=0, fill=1, fillMode=1)  # 1 = FILL_NON_ZERO


class MathLine(Flowable):
    """A display equation (optionally numbered) occupying one full line."""

    def __init__(self, box: Box, number: str | None, num_style_font: str, fs: float,
                 num_w: float = 14.0 * 2.8346):
        super().__init__()
        self.box, self.number, self.fs = box, number, fs
        self.num_font, self.num_w = num_style_font, num_w
        self.scale = 1.0
        self.pad = 3.0

    def wrap(self, aw, ah):
        self.aw = aw
        avail = aw - 2 * self.num_w
        if self.box.w > avail:
            # the number column may shrink if the equation needs the room
            avail = aw - 2 * (self.num_w * 0.6)
            self.num_w *= 0.6
        self.scale = min(1.0, avail / self.box.w) if self.box.w else 1.0
        self.h = (self.box.asc + self.box.desc) * self.scale + 2 * self.pad
        return aw, self.h

    def draw(self):
        c = self.canv
        s = self.scale
        x0 = (self.aw - self.box.w * s) / 2
        c.saveState()
        c.setFillColor(INK)
        c.setStrokeColor(INK)
        c.translate(x0, self.pad + self.box.desc * s)
        c.scale(s, s)
        _draw_items(c, self.box.items)
        c.restoreState()
        if self.number:
            c.saveState()
            c.setFillColor(INK)
            c.setFont(self.num_font, self.fs)
            y = self.pad + self.box.desc * s - 0.0
            # number baseline = equation's main baseline
            c.drawRightString(self.aw, y, f"({self.number})")
            c.restoreState()


class FailedMath(Flowable):
    """Fallback: flagged box with monospace source."""

    def __init__(self, src: str, err: str, width_hint: float = 0, fs: float = 8.0):
        super().__init__()
        self.src, self.err, self.fs = src, err, fs

    def wrap(self, aw, ah):
        from reportlab.lib.utils import simpleSplit
        self.aw = aw
        self.lines = simpleSplit(self.src, "Courier", self.fs, aw - 14)[:12]
        self.h = (len(self.lines) + 1) * (self.fs + 2) + 10
        return aw, self.h

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(colors.HexColor("#fdeceb"))
        c.setStrokeColor(colors.HexColor("#9b2226"))
        c.setLineWidth(0.8)
        c.rect(0, 0, self.aw, self.h, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#9b2226"))
        c.setFont("Helvetica-Bold", self.fs - 1)
        y = self.h - self.fs - 3
        c.drawString(5, y, "[EQUATION NOT RENDERED]  " + self.err[:90])
        c.setFillColor(INK)
        c.setFont("Courier", self.fs)
        for ln in self.lines:
            y -= self.fs + 2
            c.drawString(5, y, ln)
        c.restoreState()


def display_equation(tex: str, fs: float, number_font: str = "DejaSerif",
                     where: str = "") -> Flowable:
    """Return the flowable for one `$$ ... $$` body; never raises."""
    body, tag = split_tag(tex)
    try:
        box = display_box(body, fs)
        if box.w <= 0:
            raise MathError("empty equation")
        fl = MathLine(box, tag, number_font, fs)
        avail_guess = 174 * 2.8346 - 2 * 14 * 2.8346 * 0.6
        if box.w > avail_guess:
            MATH_NOTES.append({"where": where, "tag": tag, "note": "scaled to fit",
                               "width_pt": round(box.w, 1)})
        return fl
    except Exception as e:
        MATH_FAILURES.append({"kind": "display", "tag": tag, "where": where,
                              "source": body, "error": str(e)})
        return FailedMath(("(" + tag + ")  " if tag else "") + " ".join(body.split()), str(e))


# ---------------------------------------------------------------------------
# Inline maths
# ---------------------------------------------------------------------------

_GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "ϑ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ",
    "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
}
_GREEK_UP = {
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
_REL = {"leq": "≤", "le": "≤", "geq": "≥", "ge": "≥", "neq": "≠", "ne": "≠",
        "approx": "≈", "in": "∈", "notin": "∉", "to": "→", "rightarrow": "→",
        "equiv": "≡", "sim": "∼", "propto": "∝", "subset": "⊂", "subseteq": "⊆"}
_BIN = {"times": "×", "cdot": "·", "pm": "±", "cap": "∩", "cup": "∪",
        "ast": "∗", "mp": "∓"}
_ORD = {"infty": "∞", "ell": '<font face="DejaSans-Italic">ℓ</font>', "partial": "∂", "ldots": "…", "dots": "…",
        "cdots": '<font face="DejaSans">⋯</font>', "degree": "°", "prime": "′"}
_SPACES = {",": " ", ";": " ", ":": " ", "!": "", " ": " ", "quad": " ", "qquad": "  "}


class _Complex(Exception):
    pass


def _esc_xml(c: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(c, c)


def _simple_seq(s: str, allow_scripts: bool = True, fs: float = 9.3) -> str:
    """Convert a simple tex fragment to reportlab markup; raise _Complex otherwise."""
    out: list[str] = []
    i, n = 0, len(s)
    prev_operand = False      # for deciding unary vs binary +/-
    NB = " "

    def operand(txt):
        nonlocal prev_operand
        out.append(txt)
        prev_operand = True

    def operator(sym, spaced=True):
        nonlocal prev_operand
        out.append((NB + sym + NB) if spaced else sym)
        prev_operand = False

    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == BS:
            m = re.match(r"([A-Za-z]+)", s[i + 1:])
            if m:
                name = m.group(1)
                i += 1 + len(name)
                if name in _GREEK:
                    operand("<i>" + _GREEK[name] + "</i>")
                elif name in _GREEK_UP:
                    operand(_GREEK_UP[name])
                elif name in _REL:
                    operator(_REL[name])
                elif name in _BIN:
                    operator(_BIN[name], spaced=name not in ("cdot",) or True)
                elif name in ("min", "max", "sup", "inf", "log", "ln", "exp", "lim"):
                    out.append(name)
                    prev_operand = False
                    if i < n and (s[i].isalpha() or s[i] == BS):
                        out.append(" ")
                elif name in _ORD:
                    operand(_ORD[name])
                elif name in ("mathrm", "text", "textrm", "mathbf", "mathit", "operatorname"):
                    j = i
                    while j < n and s[j].isspace():
                        j += 1
                    if j >= n or s[j] != "{":
                        raise _Complex
                    try:
                        content, end = _balanced_arg(s, j)
                    except MathError:
                        raise _Complex
                    if BS in content or "{" in content or "^" in content or "_" in content:
                        raise _Complex
                    txt = "".join(_esc_xml(ch) for ch in content)
                    if name in ("mathbf",):
                        txt = "<b>" + txt + "</b>"
                    elif name == "mathit":
                        txt = "<i>" + txt + "</i>"
                    operand(txt)
                    i = end
                else:
                    raise _Complex
                continue
            # \, \; \! \: \  \% \{ \} \& \$ \_ \#
            if i + 1 < n:
                d = s[i + 1]
                i += 2
                if d in _SPACES:
                    out.append(_SPACES[d])
                elif d == "%":
                    operand("%")
                elif d in "{}#&_":
                    operand(d if d not in "&" else "&amp;")
                elif d == "$":
                    operand("$")
                elif d == "|":
                    raise _Complex
                else:
                    raise _Complex
                continue
            raise _Complex
        if c in "^_":
            if not allow_scripts:
                raise _Complex
            i += 1
            if i >= n:
                raise _Complex
            if s[i] == "{":
                try:
                    arg, i = _balanced_arg(s, i)
                except MathError:
                    raise _Complex
                inner = _simple_seq(arg, allow_scripts=False, fs=fs)
            elif s[i] == BS:
                m = re.match(re.escape(BS) + r"([A-Za-z]+)", s[i:])
                if not m:
                    raise _Complex
                inner = _simple_seq(m.group(0), allow_scripts=False, fs=fs)
                i += len(m.group(0))
            else:
                inner = _simple_seq(s[i], allow_scripts=False, fs=fs)
                i += 1
            tag = "sub" if c == "_" else "super"
            # strip the nbsp padding inside scripts
            inner = inner.replace(NB, "")
            rise = 0.20 * fs if c == "_" else 0.38 * fs
            out.append(f'<{tag} rise="{rise:.2f}" size="{0.72 * fs:.2f}">{inner}</{tag}>')
            prev_operand = True
            continue
        if c == "{":
            # thousands separator {,} ; a plain group {...}
            if s.startswith("{,}", i):
                out.append(",")
                i += 3
                continue
            try:
                arg, j = _balanced_arg(s, i)
            except MathError:
                raise _Complex
            nxt = s[j:j + 1]
            if nxt in ("^", "_"):
                raise _Complex
            out.append(_simple_seq(arg, allow_scripts, fs))
            prev_operand = True
            i = j
            continue
        if c == "}":
            raise _Complex
        if c.isalpha() and c.isascii():
            operand("<i>" + c + "</i>")
            i += 1
            continue
        if c.isdigit():
            operand(c)
            i += 1
            continue
        if c in "=<>":
            operator(_esc_xml(c))
            i += 1
            continue
        if c == "+":
            operator("+", spaced=prev_operand)
            i += 1
            continue
        if c == "-":
            operator("−", spaced=prev_operand)
            i += 1
            continue
        if c in ".,":
            # in "a, b" a space follows a comma
            out.append(c + (" " if c == "," and i + 1 < n and not s[i + 1].isdigit() else ""))
            prev_operand = c == "."
            i += 1
            continue
        if c == "'":
            operand("′")
            i += 1
            continue
        if c in "()[]/:;|!%−·":
            out.append(c)
            prev_operand = c in ")]%"
            i += 1
            continue
        if c == "/":
            out.append(c)
            prev_operand = False
            i += 1
            continue
        if ord(c) > 127:
            out.append(c)
            prev_operand = True
            i += 1
            continue
        raise _Complex
    return "".join(out)


def simple_inline_markup(tex: str, fs: float = 9.3) -> str | None:
    try:
        return _simple_seq(tex.strip(), fs=fs)
    except (_Complex, MathError):
        return None


@functools.lru_cache(maxsize=2048)
def _png_for(tex_pp: str, fs: float, dpi: int = 600):
    """Render an inline fragment to PNG bytes. Returns (png, width, height, depth) in pt."""
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.patches import PathPatch
    box = _mathtext_box(tex_pp, fs)
    pad = 0.6
    W, H = box.w + 2 * pad, box.asc + box.desc + 2 * pad
    fig = Figure(figsize=(W / 72, H / 72), dpi=dpi)
    FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-pad, box.w + pad)
    ax.set_ylim(-box.desc - pad, box.asc + pad)
    ax.axis("off")
    for it in box.items:
        ax.add_patch(PathPatch(MPath(it.verts, it.codes), facecolor=INK_HEX, edgecolor="none",
                               lw=0))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=True)
    return buf.getvalue(), W, H, box.desc + pad


_BIGOPS = re.compile(
    re.escape(BS) + r"(sum|prod|coprod|bigcup|bigcap|bigvee|bigwedge|int|oint|min|max|lim|sup|inf)"
    r"(?![A-Za-z])(?=\s*[_^])")


def _inline_style(tex: str) -> str:
    """Text style: limits go beside the operator, not under it (empty-group trick)."""
    return _BIGOPS.sub(lambda m: BS + m.group(1) + "{}", tex)


def inline_image_markup(tex: str, fs: float, where: str = "") -> str | None:
    """`<img>` markup for a Paragraph (temp-file PNG), or None on failure (recorded)."""
    tex = _inline_style(tex)
    try:
        try:
            pp = preprocess(tex, True, True)
            png, W, H, d = _png_for(pp, round(fs, 2))
        except MathError:
            pp = preprocess(tex, False, True)
            png, W, H, d = _png_for(pp, round(fs, 2))
    except Exception as e:
        MATH_FAILURES.append({"kind": "inline", "tag": None, "where": where,
                              "source": tex, "error": str(e)})
        return None
    import hashlib
    import tempfile
    from pathlib import Path
    cache = Path(tempfile.gettempdir()) / "kash_math_png_cache"
    cache.mkdir(exist_ok=True)
    f = cache / (hashlib.sha1(png).hexdigest()[:20] + ".png")
    if not f.exists():
        f.write_bytes(png)
    return (f'<img src="{f.as_posix()}" width="{W:.2f}" height="{H:.2f}" '
            f'valign="{-d:.2f}"/>')


# ---------------------------------------------------------------------------
# Finding maths inside running text
# ---------------------------------------------------------------------------

DISPLAY_IN_TEXT = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE_MATH = re.compile(
    r"(?<![A-Z0-9$\\])\$(?=[^\s$])((?:\\.|[^$\\])+?)(?<![\s\\])\$(?!\d)", re.S)


def math_to_markup(tex: str, fs: float, where: str = "") -> str:
    """Markup for one inline-math span (simple -> text markup, else image)."""
    tex, tag = split_tag(tex)
    suffix = f" ({tag})" if tag else ""
    simple = simple_inline_markup(tex, fs)
    if simple is not None:
        return simple + suffix
    img = inline_image_markup(tex, fs, where)
    if img is not None:
        return img + suffix
    # failure: visible, flagged source
    return ('<font face="DejaMono" color="#9b2226" backColor="#fdeceb">['
            + "".join(_esc_xml(c) for c in tex) + "]</font>")
