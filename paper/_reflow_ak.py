"""Reflow the one-word-per-line PDF text extraction into readable paragraphs.

The co-author attachment ("Copy of Paper Route Rationale_AK.pdf") was extracted
with a tool that emitted one token per line. This makes it unreadable and
enormously token-expensive. Reflow heuristically: join tokens with spaces,
break a paragraph when a token looks like a structural marker.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else r"E:\kash\_copy_ak_extracted.txt")
DST = Path(sys.argv[2] if len(sys.argv) > 2 else r"E:\kash-paper\paper\_ak_reflowed.txt")

toks = [t.strip() for t in SRC.read_text(encoding="utf-8", errors="replace").splitlines()]
toks = [t for t in toks if t != ""]

# Re-join: attach punctuation that should not be preceded by a space.
NO_SPACE_BEFORE = set(list(".,;:!?)]}%") + ["’s", "'s", "”", "–", "—"])
out: list[str] = []
for t in toks:
    if out and (t in NO_SPACE_BEFORE or re.fullmatch(r"[.,;:!?)\]}%]+", t)):
        out[-1] = out[-1] + t
    elif out and out[-1].endswith(("(", "[", "{", "“", "/")):
        out[-1] = out[-1] + t
    else:
        out.append(t)

text = " ".join(out)

# Insert paragraph breaks before structural markers so the result is scannable.
MARKERS = [
    r"Abstract\b", r"Highlights\b", r"Keywords\b", r"References\b",
    r"\b\d\.\s?[A-Z][a-z]", r"\b\d\.\d\s?[A-Z][a-z]",
    r"\(Prashant", r"\(Misti", r"\(Ankit", r"\(Sharvesh", r"\(Avny", r"\(Krishna",
    r"Table\s+\d", r"Figure\s+\d", r"Equation\s+\d",
]
for m in MARKERS:
    text = re.sub("(" + m + ")", r"\n\n\1", text)

text = re.sub(r"\n{3,}", "\n\n", text)
# Also break after sentence-ending periods that precede a capital + 40+ char run,
# so long blocks become readable lines (soft wrap at ~110 chars).
lines: list[str] = []
for para in text.split("\n\n"):
    para = para.strip()
    if not para:
        continue
    words = para.split(" ")
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > 110:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    lines.append("")

DST.write_text("\n".join(lines), encoding="utf-8")
print(f"tokens_in={len(toks)}  chars_out={len(text)}  lines_out={len(lines)}")
print(f"written -> {DST}")
