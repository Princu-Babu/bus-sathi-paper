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
