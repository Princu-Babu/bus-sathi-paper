// Writes paper/sections/04_methodology.md from the final Section 4 content
// (section4_final_content.js), in the markdown dialect of md2pdf.py / citations.py:
// $...$ maths, $$...\tag{n}$$ display equations, [@key] citations, an ```algorithm block.
// Usage: node content_to_md.js [content.js] [out.md]
const fs = require("fs");
const path = require("path");
const C = require(process.argv[2] || "./section4_final_content.js");
const OUT = process.argv[3] || path.join(__dirname, "..", "sections", "04_methodology.md");
const EQ = JSON.parse(fs.readFileSync(path.join(__dirname, "eq_sizes_v6.json"), "utf8"));
const refs = JSON.parse(fs.readFileSync(path.join(__dirname, "refs.json"), "utf8"));

// in-text string -> bib key ("&" and "and" both accepted)
const norm = s => s.replace(/&/g, "and").replace(/\s+/g, " ").trim();
const KEY = {};
for (const [k, v] of Object.entries(refs)) KEY[norm(v.intext)] = k;
KEY["Sobol', 2001"] = "sobol2001global";
KEY["Saltelli et al., 2008, 2010"] = "saltelli2008global; @saltelli2010variance";

function cites(t) {
  return t.replace(/\(([^()]*\d{4}[^()]*)\)/g, (m, inner) => {
    const parts = inner.split(";").map(s => norm(s));
    const keys = parts.map(p => KEY[p]);
    if (keys.some(k => !k)) return m;            // not a citation group: leave as written
    return "[" + keys.map(k => "@" + k).join("; ") + "]";
  });
}
function maths(t) {
  // *x*_{c} / ρ_{c} / ẑ_{Π} / Π^{*}(*r*) / *N*^{min} -> $...$
  t = t.replace(/Π\^\{\*\}\(\*r\*\)\/ℓ\(\*r\*\)/g, "$\\Pi^{*}(r)/\\ell(r)$");
  t = t.replace(/\*O\*\(\*r\*\)\/ℓ\(\*r\*\)/g, "$O(r)/\\ell(r)$");
  t = t.replace(/\*([A-Za-z])\*_\{([^}]*)\}(\(\*([a-z])\*\))?/g, (m, a, s, _p, r) => `$${a}_{${s}}${r ? `(${r})` : ""}$`);
  t = t.replace(/\*([A-Za-z])\*\^\{([^}]*)\}/g, "$$$1^{$2}$");
  t = t.replace(/ρ_\{([^}]*)\}/g, "$\\rho_{$1}$").replace(/ẑ_\{Π\}/g, "$\\hat{z}_{\\Pi}$").replace(/ẑ_\{O\}/g, "$\\hat{z}_{O}$");
  t = t.replace(/\*y\*_\{i\}/g, "$y_i$");
  return t;
}
const L = ["# 4. Methodology", "",
  "> **Section owner:** Prashant. **Status:** final short version, 22 October 2026 (about 1,950 words of prose).",
  "> Built from `paper/word_build/section4_final_content.js` by `content_to_md.js`; edit the content file, not this one.",
  "> Line-by-line reasons and evidence: `paper/Section4_v6_Line_Justification.docx`. Equation numbers follow v6.", ""];
for (const b of C) {
  if (b.h1) continue;
  if (b.h2) L.push("## " + b.h2, "");
  else if (b.p) L.push(maths(cites(b.p.map(x => x.t).join(" "))).replace(/Table 4\.1/g, "Table 3"), "");
  else if (b.eq) L.push(`$$${EQ[b.eq].tex} \\tag{${b.eq}}$$`, "");
  else if (b.fig) L.push("> **[FIGURE 4 HERE]** " + b.caption.replace(/\*\*Figure 4\.\*\*\s*/, ""), "");
  else if (b.table) {
    const t = b.table;
    L.push(t.caption.replace("Table 4.1.", "Table 3.").replace("Inputs to the method.", "Inputs to the method (detail in Table 2)."), "");
    L.push("| " + t.head.join(" | ") + " |", "|" + t.head.map(() => "---").join("|") + "|");
    for (const r of t.rows) L.push("| " + r.join(" | ") + " |");
    L.push("");
  } else if (b.algo) {
    L.push("```algorithm");
    for (const a of b.algo) L.push(a.replace(/^\d+\.\s*/, "").replace(/θ/g, "$\\theta$").replace(/φ ≥/g, "$\\phi \\geq$"));
    L.push("```", "");
  }
}
fs.writeFileSync(OUT, L.join("\n"), "utf8");
console.log("wrote", OUT, L.length, "lines");
