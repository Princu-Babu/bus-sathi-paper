"""_qa_render.py — rasterise selected PDF pages to PNG so they can be eyeballed.

    .venv/Scripts/python.exe paper/_qa_render.py <pdf> <outdir> [pages...]

`pages` are 1-based; omit to render the first six. Renders at ~120 DPI, which is
enough to catch overflow, clipped table columns and missing glyphs (tofu boxes).
"""
import sys
from pathlib import Path

import pypdfium2 as pdfium


def main(argv):
    pdf_path = Path(argv[1])
    outdir = Path(argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(pdf_path))
    n = len(doc)
    pages = [int(x) for x in argv[3:]] or list(range(1, min(6, n) + 1))
    written = []
    for p in pages:
        if p < 1 or p > n:
            continue
        img = doc[p - 1].render(scale=120 / 72).to_pil()
        out = outdir / f"{pdf_path.stem}_p{p:03d}.png"
        img.save(out)
        written.append(out)
    print(f"{pdf_path.name}: {n} pages; rendered {len(written)} -> {outdir}")
    for w in written:
        print("  ", w)


if __name__ == "__main__":
    main(sys.argv)
