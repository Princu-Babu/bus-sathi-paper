// Builds (1) the Section 4 Word file and (2) a landscape Word file with the line-by-line justification.
// Usage: node build_section4_v6.js <section.docx> <justification.docx>
// Version 6: adds table blocks, takes figures from word_build/ when b.dir is set, and numbers equations by b.eq.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, TabStopType, LevelFormat,
  BorderStyle, ShadingType, Table, TableRow, TableCell, WidthType, PageOrientation, ImageRun, Footer, PageNumber,
} = require("docx");

const C = require("./section4_v6_content.js");
const refs = JSON.parse(fs.readFileSync(path.join(__dirname, "refs.json"), "utf8"));
const [OUT_SECTION, OUT_JUST] = process.argv.slice(2);
const FONT = "Times New Roman", MATH = "Cambria Math";

function runs(text, base = {}) {
  const out = []; const re = /(\*[^*]+\*|_\{[^}]*\}|\^\{[^}]*\})/g; let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("*")) out.push(new TextRun({ text: tok.slice(1, -1), ...base, italics: true }));
    else if (tok.startsWith("_")) out.push(new TextRun({ text: tok.slice(2, -1), ...base, subScript: true }));
    else out.push(new TextRun({ text: tok.slice(2, -1), ...base, superScript: true }));
    last = re.lastIndex;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const plain = t => t.replace(/\*([^*]+)\*/g, "$1").replace(/_\{([^}]*)\}/g, "$1").replace(/\^\{([^}]*)\}/g, "$1");
const bodyText = C.map(b => (b.p || []).concat(b.list || []).map(x => x.t).join(" ")).join(" ");
const cited = Object.keys(refs).filter(k => bodyText.includes(refs[k].intext.split(/[ ,]/)[0]));

const styles = (size) => ({
  default: { document: { run: { font: FONT, size }, paragraph: { spacing: { after: 140, line: 288 } } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 32, bold: true, font: FONT }, paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 26, bold: true, font: FONT }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
  ],
});
const numbering = { config: [
  { reference: "points", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
] };

// ---------- images: equations rendered by render_eqs.py, figures from the paper repository ----------
const EQS = JSON.parse(fs.readFileSync(path.join(__dirname, "eq_sizes_v6.json"), "utf8"));
const FIG_DIR = path.join(__dirname, "..", "figures");
const figPath = b => b.dir === "word_build" ? path.join(__dirname, b.fig) : path.join(FIG_DIR, b.fig);
const pngSize = buf => ({ w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) });  // PNG IHDR
const NOB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const NOBORDERS = { top: NOB, bottom: NOB, left: NOB, right: NOB, insideHorizontal: NOB, insideVertical: NOB };
function eqImage(n, maxPx, scale) {
  const e = EQS[n]; const data = fs.readFileSync(path.join(__dirname, e.file));
  const k = Math.min(scale, maxPx / e.w);
  return new ImageRun({ type: "png", data, transformation: { width: Math.round(e.w * k), height: Math.round(e.h * k) },
    altText: { title: `Equation ${n}`, description: e.tex, name: `eq${n}` } });
}
function eqTable(b) {   // equation centred, number flush right, no borders
  const W = [8326, 700];
  const c = (children, w) => new TableCell({ width: { size: w, type: WidthType.DXA }, verticalAlign: "center", borders: NOBORDERS, children });
  return new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: W, borders: NOBORDERS, rows: [new TableRow({ cantSplit: true, children: [
    c([new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 100 }, children: [eqImage(b.eq, 540, 0.30)] })], W[0]),
    c([new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { before: 100, after: 100 }, children: [new TextRun(`(${b.eq})`)] })], W[1]),
  ] })] });
}
function captionRuns(text, base = {}) {   // "**Figure 4.** rest" -> bold label + plain rest
  const m = text.match(/^\*\*(.+?)\*\*\s*(.*)$/);
  return m ? [new TextRun({ text: m[1] + " ", bold: true, ...base }), ...runs(m[2], base)] : runs(text, base);
}
function figureBlock(b, maxPx) {
  const data = fs.readFileSync(figPath(b)); const { w, h } = pngSize(data); const k = maxPx / w;
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 160, after: 80 },
      children: [new ImageRun({ type: "png", data, transformation: { width: Math.round(w * k), height: Math.round(h * k) },
        altText: { title: b.fig, description: b.caption.replace(/\*/g, ""), name: b.fig } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: captionRuns(b.caption, { size: 20 }) }),
  ];
}

function dataTable(t) {
  const W = [3000, 3826, 2200];
  const rule = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
  const tc = (text, w, bold, fill) => new TableCell({ width: { size: w, type: WidthType.DXA }, margins: { top: 40, bottom: 40, left: 80, right: 80 },
    shading: fill ? { type: ShadingType.CLEAR, color: "auto", fill } : undefined,
    borders: { top: rule, bottom: rule, left: NOB, right: NOB },
    children: [new Paragraph({ spacing: { after: 0, line: 252 }, children: runs(text, { size: 19, bold }) })] });
  return [
    new Paragraph({ keepNext: true, spacing: { before: 160, after: 80 }, children: captionRuns(t.caption, { size: 20 }) }),
    new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: W, rows: [
      new TableRow({ tableHeader: true, children: t.head.map((h, i) => tc(h, W[i], true, "E7ECF2")) }),
      ...t.rows.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => tc(c, W[i], false)) })),
    ] }),
    new Paragraph({ spacing: { after: 120 }, children: [] }),
  ];
}

// ---------- (1) the section ----------
const sec = [];
for (const b of C) {
  if (b.h1) sec.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(b.h1)] }));
  else if (b.h2) sec.push(new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, children: [new TextRun(b.h2)] }));
  else if (b.p) sec.push(new Paragraph({ alignment: AlignmentType.JUSTIFIED, children: runs(b.p.map(x => x.t).join(" ")) }));
  else if (b.list) for (const x of b.list) sec.push(new Paragraph({ numbering: { reference: "points", level: 0 }, children: runs(x.t) }));
  else if (b.eq) sec.push(eqTable(b));
  else if (b.fig) sec.push(...figureBlock(b, 602));
  else if (b.table) sec.push(...dataTable(b.table));
  else if (b.algo) b.algo.forEach((line, i) => sec.push(new Paragraph({
    keepNext: i < b.algo.length - 1, keepLines: true,
    spacing: { before: i === 0 ? 120 : 0, after: i === b.algo.length - 1 ? 160 : 40 }, indent: { left: 360, right: 360 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: "F2F2F2" },
    border: i === 0 ? { top: { style: BorderStyle.SINGLE, size: 6, color: "808080", space: 4 } }
      : (i === b.algo.length - 1 ? { bottom: { style: BorderStyle.SINGLE, size: 6, color: "808080", space: 4 } } : undefined),
    children: runs(line, { size: 22, bold: i === 0 }) })));
  else if (b.refs) {
    sec.push(new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, children: [new TextRun("References cited in this section")] }));
    for (const r of cited.map(k => refs[k].ref).sort((a, b) => a.localeCompare(b)))
      sec.push(new Paragraph({ indent: { left: 360, hanging: 360 }, spacing: { after: 80 }, children: runs(r, { size: 20 }) }));
  }
}
const docA = new Document({ creator: "Kashmir bus route rationalisation study", title: "Section 4. Methodology",
  styles: styles(24), numbering,
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
    children: sec }] });

// ---------- (2) the justification ----------
const W = [700, 6300, 3900, 3060]; // landscape A4 content width 13958
const cell = (text, w, opts = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 90, right: 90 },
  shading: opts.fill ? { type: ShadingType.CLEAR, color: "auto", fill: opts.fill } : undefined,
  children: [new Paragraph({ spacing: { after: 0, line: 252 }, children: runs(text, { size: 18, bold: !!opts.bold, font: opts.font || FONT }) })] });
const header = (cols, widths) => new TableRow({ tableHeader: true,
  children: cols.map((c, i) => cell(c, widths[i], { bold: true, fill: "E7ECF2" })) });
const tbl = (rows, widths) => new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows });

const just = [
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Section 4: why each sentence is there")] }),
  new Paragraph({ children: runs("Companion to Section4_Methodology_v6.docx, 22 October 2026. Version 6 was written from a blank page with a new structure, using v5 only as a list of checked facts. Every sentence, equation, the table, the figure and the algorithm of Section 4 is listed in order with the reason it is in the section and the file or claim-ledger row that supports it. After each subsection, a second table lists what was considered and left out, and why. File paths are relative to E:\\kash-paper unless they begin with another drive or folder.") }),
  new Paragraph({ children: runs("Rules applied while writing: a sentence stays only if a reader needs it to repeat the method, to judge a choice, or to see a limitation; every number must trace to a file; nothing still waiting on an answer from a co-author is stated; and the draft followed the nature-writing method guide (each subsection: why the step is needed, what it does, its limits) and was checked with nature-polishing, paper-self-review, citation-verification, humanizer and academic-humanizer (no dashes, no stock phrases, claims no stronger than their evidence, every citation present in references.bib).") }),
  new Paragraph({ children: runs("A human author still has to open each cited source and confirm it before submission. The evidence column records where the support is; it does not certify that a person has checked it.", { italics: true }) }),
];
let no = 0, current = null, rows = [];
const flush = () => {
  if (!current) return;
  if (rows.length) just.push(tbl([header(["No.", "Sentence", "Why it is there", "Evidence"], W), ...rows], W));
  if (current.out && current.out.length) {
    just.push(new Paragraph({ spacing: { before: 160, after: 80 }, keepNext: true, children: [new TextRun({ text: "Considered and left out", bold: true, size: 20 })] }));
    const W2 = [5200, 8758];
    just.push(tbl([header(["Item", "Reason"], W2), ...current.out.map(([a, b]) => new TableRow({ children: [cell(a, W2[0]), cell(b, W2[1])] }))], W2));
  }
  rows = [];
};
for (const b of C) {
  if (b.h2) { flush(); current = b; just.push(new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, children: [new TextRun(b.h2)] })); continue; }
  const add = (label, text, why, ev, font) => rows.push(new TableRow({ cantSplit: true, children: [cell(label, W[0]), cell(text, W[1], { font }), cell(why, W[2]), cell(ev, W[3])] }));
  if (b.p) for (const x of b.p) add(String(++no), x.t, x.why, x.ev);
  if (b.list) for (const x of b.list) add(String(++no), x.t, x.why, x.ev);
  if (b.eq) rows.push(new TableRow({ cantSplit: true, children: [cell(`Eq. ${b.eq}`, W[0]),
    new TableCell({ width: { size: W[1], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 90, right: 90 },
      children: [new Paragraph({ spacing: { after: 0 }, children: [eqImage(b.eq, 400, 0.24)] })] }),
    cell(b.why, W[2]), cell(b.ev, W[3])] }));
  if (b.fig) {
    const data = fs.readFileSync(figPath(b)); const { w, h } = pngSize(data); const k = 400 / w;
    rows.push(new TableRow({ cantSplit: true, children: [cell("Fig. 4", W[0]),
      new TableCell({ width: { size: W[1], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 90, right: 90 },
        children: [new Paragraph({ spacing: { after: 40 }, children: [new ImageRun({ type: "png", data,
          transformation: { width: Math.round(w * k), height: Math.round(h * k) }, altText: { title: b.fig, description: b.caption, name: b.fig } })] }),
          new Paragraph({ spacing: { after: 0 }, children: captionRuns(b.caption, { size: 18 }) })] }),
      cell(b.why, W[2]), cell(b.ev, W[3])] }));
  }
  if (b.algo) add("Alg. 1", b.algo.join(" / "), b.why, b.ev);
  if (b.table) add("Table 4.1", b.table.caption.replace(/\*/g, "") + " " + b.table.rows.map(r => r.join(": ")).join(" / "), b.why, b.ev);
}
flush();
const docB = new Document({ creator: "Kashmir bus route rationalisation study", title: "Section 4 line justification (v6)",
  styles: styles(20), numbering,
  sections: [{ properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE },
    margin: { top: 1080, right: 1440, bottom: 1080, left: 1440 } } }, children: just }] });

Promise.all([Packer.toBuffer(docA), Packer.toBuffer(docB)]).then(([a, b]) => {
  fs.writeFileSync(OUT_SECTION, a); fs.writeFileSync(OUT_JUST, b);
  console.log("wrote", OUT_SECTION, a.length, "|", OUT_JUST, b.length, "| sentences", no, "| references", cited.length);
});
