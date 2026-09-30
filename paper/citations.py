"""
citations.py — minimal pandoc-style citation handling for the working draft.

Section files cite as `[@key]` or `[@key1; @key2]`. This module resolves each key
against `paper/references.bib`, renders an author–year in-text citation, and
builds the reference list from the keys actually cited (nothing uncited is
listed). An unresolved key is rendered visibly as `[?key]` and reported, so a
typo can never silently disappear.

    python paper/citations.py            # audit: every cited key resolves?
"""
from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIB = HERE / "references.bib"
CITE_RE = re.compile(r"\[(@[\w:-]+(?:\s*;\s*@[\w:-]+)*)\]")


def _strip(s: str) -> str:
    s = re.sub(r"\\url\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\['`^\"~]\{?(\w)\}?", r"\1", s)     # crude accent strip: \'e -> e
    s = s.replace("\\&", "&").replace("\\%", "%").replace("--", "–")
    return re.sub(r"[{}]", "", s).strip()


def load_bib(path: Path = BIB) -> dict[str, dict]:
    txt = path.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", txt, re.S):
        typ, key, body = m.group(1).lower(), m.group(2).strip(), m.group(3)
        fields = {}
        for f in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|\d+)", body):
            v = f.group(2)
            if v[0] in "{\"":
                v = v[1:-1]
            fields[f.group(1).lower()] = v
        fields["_type"] = typ
        out[key] = fields
    return out


def _authors(entry: dict) -> list[str]:
    a = entry.get("author", "")
    if a.startswith("{") and a.endswith("}") and " and " not in a:
        return [_strip(a)]
    names = []
    for part in re.split(r"\s+and\s+", a):
        part = part.strip()
        if part.startswith("{"):
            names.append(_strip(part))
        elif "," in part:
            names.append(_strip(part.split(",")[0]))
        else:
            names.append(_strip(part.split()[-1]) if part else "")
    return [n for n in names if n]


def intext(entry: dict) -> str:
    au = _authors(entry)
    y = entry.get("year", "n.d.")
    if not au:
        return y
    if len(au) == 1:
        return f"{au[0]}, {y}"
    if len(au) == 2:
        return f"{au[0]} & {au[1]}, {y}"
    return f"{au[0]} et al., {y}"


def render(md: str, bib: dict, cited: list[str], missing: set[str]) -> str:
    def rep(m):
        keys = [k.strip()[1:] for k in m.group(1).split(";")]
        parts = []
        for k in keys:
            if k in bib:
                if k not in cited:
                    cited.append(k)
                parts.append(intext(bib[k]))
            else:
                missing.add(k)
                parts.append(f"[?{k}]")
        return "(" + "; ".join(parts) + ")"
    return CITE_RE.sub(rep, md)


def reference_entry(entry: dict) -> str:
    au = _authors(entry)
    names = ", ".join(au[:-1]) + (" & " if len(au) > 1 else "") + au[-1] if au else ""
    t = _strip(entry.get("title", ""))
    y = entry.get("year", "n.d.")
    venue = _strip(entry.get("journal") or entry.get("booktitle") or entry.get("publisher")
                   or entry.get("howpublished") or entry.get("institution") or "")
    vol = entry.get("volume", "")
    num = entry.get("number", "")
    pages = _strip(entry.get("pages", ""))
    doi = entry.get("doi", "")
    s = f"{names} ({y}). {t}."
    if venue:
        s += f" *{venue}*"
        if vol:
            s += f", {vol}" + (f"({num})" if num else "")
        if pages:
            s += f", {pages}"
        s += "."
    if doi:
        s += f" https://doi.org/{doi}"
    return s


def reference_list_md(keys: list[str], bib: dict) -> str:
    ents = sorted(keys, key=lambda k: (_authors(bib[k])[:1] or [""])[0].lower() + bib[k].get("year", ""))
    return "\n\n".join(reference_entry(bib[k]) for k in ents)


if __name__ == "__main__":
    bib = load_bib()
    cited, missing = [], set()
    for f in sorted((HERE / "sections").glob("*.md")):
        render(f.read_text(encoding="utf-8"), bib, cited, missing)
    print(f"{len(bib)} bib entries; {len(cited)} cited; {len(missing)} unresolved: {sorted(missing)}")
    print("uncited entries:", sorted(set(bib) - set(cited)))
