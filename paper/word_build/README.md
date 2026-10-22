# Word build of Section 4 (version 5)

Builds two Word files in `paper/`:

- `Section4_Methodology_v5.docx`: the methodology section, with Figure 4 after the paragraph that cites it and
  each equation as a typeset image in place, numbered on the right.
- `Section4_v5_Line_Justification.docx`: every sentence, equation, the figure and the algorithm, each with the
  reason it is in the section and the file or claim-ledger row that supports it, plus a table per subsection of
  what was considered and left out.

## Files

| File | Role |
|---|---|
| `section4_v5_content.js` | The text. Each sentence carries `t` (text), `why` (reason) and `ev` (evidence). |
| `render_equations.py` | Renders Eqs. 1 to 14 to `eq01.png` ... `eq14.png` with matplotlib mathtext, through `paper/mathrender.py`. |
| `build_section4_v5.js` | Builds both Word files with the `docx` npm package. |
| `refs.json` | In-text and full references for the cited keys, generated from `paper/references.bib` by `paper/citations.py`. |

## Rebuild

```bash
cd paper/word_build
../../.venv/Scripts/python.exe render_equations.py
npm install docx
node build_section4_v5.js ../Section4_Methodology_v5.docx ../Section4_v5_Line_Justification.docx
```

Edit the text in `section4_v5_content.js`, not in Word, so the justification file stays in step with the section.

# Version 6 (22 October 2026)

Written again from a blank page with a new structure (11 subsections; v5 used only as a list of checked facts).
Builds `paper/Section4_Methodology_v6.docx` and `paper/Section4_v6_Line_Justification.docx`.

| File | Role |
|---|---|
| `section4_v6_content.js` | The text, with `why` and `ev` per sentence, Table 4.1 and a "considered and left out" list per subsection. |
| `render_equations_v6.py` | Renders `v6_eq01.png` ... `v6_eq14.png` and `eq_sizes_v6.json` (v6 numbering). |
| `fig04_v6.py` | Draws `fig04_method_flow_v6.png`: Figure 4 with v6 equation numbers and no "QA gates" box. `paper/figures/fig04_method_flow.*` is unchanged for the PDF builds. |
| `build_section4_v6.js` | Builds both Word files; adds table blocks and figures from this folder. |

```bash
cd paper/word_build
../../.venv/Scripts/python.exe render_equations_v6.py
../../.venv/Scripts/python.exe fig04_v6.py
node build_section4_v6.js ../Section4_Methodology_v6.docx ../Section4_v6_Line_Justification.docx
node build_section4_v6.js ../Section4_Methodology_Final.docx ../Section4_v6_Line_Justification.docx   # final copy, same text
```

Changes of substance from v5, each checked against the engine or the derived data:

- Eq. 5: the tourist multiplier applies to the resident count (`transit_kashmir_v3.py:1863`), not to the destination
  score as v5 had it.
- Eq. 14: the corridor share is `s(r)`, so that σ means only the spare allowance (v5 used σ for both).
- Three tiers are stated as a choice that the fit supports (0.90 against 0.79 for two), not derived from the 0.80
  threshold.
- All tier overrides are listed, including the road-role move for routes within 5% of the gap between the two breaks; the district-headquarters floor
  is part of the social rule (engine lines 2945–2960 require the social flag).
- The driver GPS is described (2,526 service runs, 157 app accounts, 6 February to 29 June 2026). Sections 3 and 6
  give 43,809 "runs", which is the count of run-corridor incidences, not runs.
- The changes made to the plan before publication (desk review, GPS re-timing, headway revisions) have their own
  subsection after the model, so the model can be read first.
