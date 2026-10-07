# Pending decisions and questions (v3, updated 7 October 2026)

Supersedes v2 (archived in `paper/archive/`). Written after the independent audit, the corrections to the
analysis code, Sharvesh's literature review, and the lead author's answers of 3–6 October.

## How to use this document

Part A is the short list for the meeting with Avny ma'am and Prof. Kathuria: seven questions, nothing else.
Part B is what the lead author still has to decide or supply. Part C is what each co-author is asked to fix
in their own section. Part D lists what has been settled, so it is not reopened. Part E is the remaining
work in order.

## Part A — the bare minimum to ask in the meeting

### Avny ma'am (4)

| # | Question | Why it cannot be worked around |
|---|---|---|
| A1 | What was actually done on the ground in Srinagar, and which word may the paper use: adopted, approved, or reviewed? | Decides how the whole paper is framed. Claiming implementation without a record would be the most damaging overclaim possible. |
| A2 | The 1–12 August field observations: who did them, in which year, and can we have the raw sheets? | They become a real validation channel in §6. Without the sheets they stay as her narrative. |
| A3 | Is she comfortable being listed with her post, with a line saying the department supplied the data and reviewed the plan? Does publishing need clearance? May the paper say the headway rules were set in review with the regulator? | Competing-interest statement and §4. The journal requires the first; the audit requires the second. |
| A4 | Confirm only: in the e-bus data, "Trip Count" counts one-way trips. | The operator's own kilometre column already says so (21.5 km per counted trip against a 22.8 km average route; the round-trip reading would need 398 km per bus per day against 187 operated). The paper uses the one-way reading and reports the other in a footnote; a yes from the operator closes it. |

One thing to show her, not ask: the register gives every permit an expiry date, and 678 of the 679 valid bus
permits are five-year permits. Her draft says permits have "no end validity". Suggested wording: "five-year
permits, renewed as a matter of course".

### Prof. Kathuria (3)

| # | Question | Why |
|---|---|---|
| K1 | Word limit. His brief says 9,000–10,000. The draft is about 13,800. What do we plan for? | Decides how much goes to a supplement. Our earlier reading of the journal guide (8,000) could not be re-checked and is **not** being assumed. |
| K2 | Can IIT Jammu's ethics committee review or exempt the driver-GPS collection? | Drivers were asked by the regulator to install the app and started each recording themselves; the research-consent screen was added later. The journal asks for an ethics statement. |
| K3 | Confirm the Srinagar-only numbers in his template (342 permits, 207 routes, 1,009 buses, "Srinagar Metropolitan Region") are placeholders, and the paper reports the ten-district plan (614 permits, 157 corridors, 186 routes, 1,011 buses) with Srinagar as the place it was checked on the ground. | §1, §3 and §7 are still written to the template's scope. |

## Part B — lead author (Prashant)

### To decide

| # | Decision | Recommendation |
|---|---|---|
| B8 | LinkedIn carousel | Hold until rewritten on the corrected numbers. |
| B9 | Add the place name to the title as a subtitle | Ask Prof. Kathuria only if he raises the title. |

### To supply

| # | Item |
|---|---|
| B10 | Who did what, in a few sentences, for the author-contribution statement (app, backend, engine, analysis, dashboard, data, fieldwork, writing, supervision). |
| B11 | Whether co-authors used AI tools for their own sections. Screening and coding in §2 already declare Claude. |
| B13 | Author order, corresponding author, institution for each of the six authors. |
| B16 | Who "Karroh" (logo on the app screen) is, for the acknowledgements. |
| B17 | Restrict the two Firebase keys in the console. |

## Part C — corrections each co-author is asked to make

| Section | Authors | What to fix |
|---|---|---|
| §1 Introduction | Misti, Avny | "644 legacy permits into 186 corridors" → 614 permits, 157 corridors, 186 routes. Section numbers in the roadmap. Add a reference for the report cited as "CSE & CITIES Forum (2026)" (title: *Reinventing the Urban Bus*); the 0.44 benchmark is that report's own figure, not the ministry's. "MoHUA (2014)" → the ministry's 2009 Service Level Benchmarks. Metro and BRT cost per km: replace the Badami & Haider attribution (a 2010 ministry presentation gives US$45 M and US$2.4 M per km); drop "under US$0.05 M per km" (no source exists). "Fewer than 15 GTFS agencies" (about 17 publish one). "Nine Jhelum bridges" and "2.5 million tourists" need a source or rewording. "Validated against 43,809 GPS runs" → 2,526 runs, and not "validated". Permits "in perpetuity". Grammar and spelling pass. |
| §2 Literature | Sharvesh, Ankit | One sentence in §2.8 ("no … ticketing … data at any stage") is too strong: e-bus aggregates enter at five points (§4.5). Trim towards the length agreed under K1. |
| §3 Study area | Krishna | GPS corpus is 2,526 runs. Ethics paragraph (after K2). Scope wording (after K3). Dataset names: WorldPop R2025A constrained; OpenStreetMap northern-India extract of 6 January 2026. |
| §6 Validation | Avny, Krishna | Merge the field-observation text once the raw sheets are available (A2). The Lalbazar–LD row shows 10 buses in an hour but a frequency of 5. |
| §7 Discussion | Ankit, Avny, Misti | "No statutory change needed" sits beside instruments that need one. Mention PM-eBus Sewa (100 e-buses allocated to Srinagar). "No service obligation" against the permit conditions described in §1. |
| Figures 1 and 3 | Misti, Krishna | Text describes a two-panel and a four-panel figure; both are drawn as single panels. Redraw, or change the description. |

## Part D — settled (do not reopen)

| Item | Outcome |
|---|---|
| Literature protocol | Run by Sharvesh: 5,488 records, 60 studies coded, gap figure, 37 references added. |
| Fleet today | 777 = 679 private buses with a valid permit (March 2026) + 98 e-buses. Plan is +30 %. JKRTC stays in the plan and out of the baseline, and the paper says so. |
| GPS corpus | 2,526 runs. The 43,809 figure counted each run once per route it touched. |
| Demand-sized fleet | Added: 551 buses at a 70 % load target with no minimum service; 508 of the 1,011 are explained by demand, 503 by the service standards. |
| Title | As set by Prof. Kathuria. |
| Structure and section authors | As in the co-author brief. |
| Regulator | Not named as RTOs; "the transport regulator". |
| Consent wording | Drivers were asked by the regulator to install the app and started each recording themselves; the consent screen was added later. Stated as such. |
| AI tools | Claude throughout; limited early use of Gemini and Codex, declared in one clause. |
| Vehicle classes | The register's heavy, medium and light classes; not "priority" classes. |
| Datasets | WorldPop R2025A v1 constrained; Geofabrik northern-India extract, 6 January 2026. |
| Service day | 11 h (13 h for the e-buses), as in the timetables, for time-of-day results and the central cost figure: bus-hour saving 2.9–5.7 %; operating cost ₹358–600 crore a year. The plan's 16-hour day is reported as its nominal assumption and the cost ceiling (₹513–859 crore). |
| Fleet statement | 1,011 as the plan; 1,130–1,266 (median 1,182) as what it would take at observed speeds. Not called a floor. |
| Trip Count | Read as one-way trips, on the evidence of the operator's kilometre column; the other reading is footnoted. |
| ArcGIS coordinates | 17 of 26 replaced from open sources, 8 author-placed after a sanity check, 1 not a place. Plan unchanged. No engine re-run. |
| Answered by the lead author | Route distances were not checked in person. No external funding; costs met by the authors. The app does not record who accepted the consent screen. |
| §4 length | Trimmed to about 2,000 words, with author notes in the draft. |
| Dashboard admin e-mails | Removed from client code (hashed allow-list). |
| Engine re-run | Not done; the published plan stands and its provenance is disclosed in §4.2. |
| Older repositories | Made private. Dashboard claims reworded and personal data removed (live). |
| Public repository | To be rebuilt as one clean release at the end. |
| Audit reports | Kept local, not in git. |
| Validation as it stands | Building-footprint check passes but is partly circular and its layer was changed after the first failed; e-bus benchmark fails; expert panel not conducted; GPS confirms route geometry but fails on travel time. Reported as such. |

## Part E — remaining work, in order

1. Update the claim ledger and rewrite §5, §6, §8, abstract and highlights on the corrected numbers (§4 is done; draft PDF issued).
2. Document build: full reference list, embedded tables including Table 3 and Table 7, figure numbering.
3. Corrections sheet to co-authors (Part C).
4. Cut to the agreed length; supplement.
5. Front matter: contribution statement, competing interests, AI declaration, ethics, data availability.
6. Rebuild the public repository; correct licences (Microsoft footprints are CDLA-Permissive-2.0).
7. Final re-check of numbers, figures and consistency across paper, repository and dashboard; then submit.
