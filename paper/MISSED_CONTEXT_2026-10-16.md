# Missed context: what the project files say that the paper does not

Prepared 16 October 2026 (one claimed error in the e-bus benchmark was checked and withdrawn) from a sweep of the engine folder (`E:\kash`), the GPS project (`E:\bus-sathi-trace`),
the dashboard (`E:\dash\bus-sathi-dashboard`), the paper repository and the source files on `D:\`. Each item gives
what the paper says now, what the files show, the file, and what to change. Items are ranked by how wrong the
paper would be without the change.

## 1. The 614 "permits" are not all permits

**Paper now.** "614 digitised stage-carriage permits" (abstract, §3, §4, claim ledger CL-01).

**Files show.** The 614 input rows (`data/raw/existing-routes.csv`, column `Vehicle_Category`) are:

| Source | Rows |
|---|---|
| Private stage-carriage permits, Srinagar RTO (MPV 347, LPV 94, HPV 4) | 445 |
| JKRTC scheduled services (Regular 76, MPS 43, City 49, MTS 1) | 169 |

The JKRTC rows come from the corporation's Kashmir Division timetable, a scanned 12-page PDF transcribed by hand
(`AUDIT_2026-06-21_SOURCE_RECHECK.md`, section A). They are the services that reach beyond Srinagar.

**Change.** Say "614 rows: 445 private permits and 169 timetabled services of the state transport corporation".
Every place that says "614 permits" needs this wording. Done in the Word Section 4 (v4).

## 2. Private permits come from one office, and most had expired

**Files show.** `latlon.py` (lines 125–128) keeps only rows whose office is `SRINAGAR RTO`. In the source file
(`Mini Buses Routes in Srinagar.xlsx`, 15,231 rows across J&K), the Kashmir offices hold:

| Office | Rows | Rows naming both ends |
|---|---|---|
| Srinagar RTO (used) | 1,259 | 453 |
| Other nine Kashmir offices (not used) | 1,742 | 133 (Budgam 54, Ganderbal 29, Pulwama 28, Kulgam 17, others 5) |

Of the 453 usable Srinagar permits, 357 had expired by 20 June 2026 and 96 were valid (`FUNNEL_AUDIT.md`,
section A). The plan therefore rests on the historically permitted network, not on live permits.

**Change.** State the single-office source, the 133 unused rows elsewhere, and the expiry share. Done in Section
4.2 of the Word file. §3 and §7 (co-author text) still describe the input as the regulator's register as a whole.

## 3. The route distances were sourced, not unsourced

**Paper now (until today).** "No sources were recorded."

**Files show.** `ROUTE_DEEPDIVE_LEDGER.csv` (all 186 routes) and `corrections_applied_v344.csv` (the 49 changes)
name the websites consulted for every route, though not specific pages (median three per corrected route, 73
distinct sites). A change was applied only above a 15% difference with confirmed place names
(`apply_corrections_v344.py`, lines 70–100). Two further facts are not yet in the paper:

- A blind second review of an 18-route random sample agreed with the first on 11 routes exactly and on all 18
  within one verdict level, and found two more misplaced end points (`ROUTE_PLAN_ASSURANCE_v3.4.4.md`, section 3).
- After the corrections, modelled distances differ from the reviewed distances by 13.3% on average
  (median 6.3%), against 37.4% before (same file, section 2). This compares the model with the review, so it is
  a consistency figure, not an independent accuracy test.

**Change.** Done in the Word file, the Markdown §4, the writing guide and the parameter register.

## 4. The 64.5% women's share has a source

**Paper now.** Flagged as unsourced (audit F-08-25).

**Files show.** `SSCL Data Updated.xlsx`, "Ridership Data": 7,504,621 of 11,632,326 boardings (May 2025 to
April 2026) were by women, 64.5%.

**Change.** Cite the operator's ridership data. The code comment that education trips drive 30% of women's
ridership is still unsourced; the sheet has no trip purpose.

## 5. Driver counts: 180 used the app, 157 recorded service runs

**Files show.** `PROFILE.md`: 180 unique drivers, 1,213 sessions, first and last trip 6 February and 29 June
2026. `data/operations_report.txt`: 855 driver-days from 157 drivers with usable service runs.

**Change.** Write "180 drivers used the app; 157 contributed service runs". Use 6 February to 29 June 2026 for
the window. (The 855 driver-days here and the 855 e-bus trips a day in V2 are unrelated.)

## 6. Measured bus speeds contradict the congestion multiplier

**Files show.** `E:\bus-sathi-trace\data\congestion_report.txt` and `calibration_report.txt`:
- moving speed is 17.4 km/h within 2.5 km of the central hub and 24.2 km/h at 5–15 km, a ratio of 1.39;
- peak-hour speed is only 1.02 times slower than midday;
- median terminal turnaround is 24 minutes (interquartile 16 to 41), where the plan allows 10% of running time.

The GPS project itself warns that a moving-speed ratio is a proxy and that it should not be published as a
congestion multiplier.

**Change.** In the parameter register and §5, report these as evidence that the 2.2 city-core multiplier and the
10% layover are not supported. Do not turn them into replacement constants without the per-corridor check the
GPS project recommends.

## 7. The regulator did review the plan

**Files show.** The engine's `CLAUDE.md`, section 11, records two review rounds with the RTO and their specific
requests: the 35-minute headway for the lowest tier (round 1), the network-wide 35-minute ceiling and the 50% cap
on heavy vehicles (round 2), and a trimmed workbook. Two other rules did not come from the regulator: the
demand-sized rural headways and the 50-minute rural maximum were the lead author's own decisions (engine
`CLAUDE.md`, version table, v3.4.2 and v3.4.3).

**Change.** None to the text until Avny ma'am confirms the paper may say so (decision A3). When it is written, say
which rules came from the regulator and which from the authors.

## 8. Scheduled e-bus departures partly support the 15-minute figure

**Files show.** `SMART CITY BUS LIST - Copy.xlsx` gives each e-bus's first morning departure. On the multi-bus
city routes the spacing is 15 minutes on three routes, 12.5, 20 and 75 minutes on others. It is a dispatch
list, not a design document, and the inter-city sheet has no times.

**Change.** Describe 15 minutes as "the spacing of the operator's morning departures on most city routes", or
keep asking the operator for the design document.

## 9. A JKRTC fleet figure exists

**Paper now.** `q02_fleet_baseline` says no JKRTC fleet count is held.

**Files show.** The ASRTU *SRTU Fleet Handbook 2024* gives J&K SRTC a fleet of 537 at 31 October 2023 (source
research R2, item 11). This is for the whole state corporation, not only Kashmir.

**Change.** Mention it beside the 777 baseline, with its scope, so readers can see what the baseline leaves out.

## 10. Smaller items

- **Spelling-variant duplicates.** `ROUTE_NETWORK_INTEGRITY_v3.4.4.md` lists near-duplicate routes, for example
  Srinagar to Ratnipora and Srinagar to Ratnipura. The 157 corridors may count a few such pairs twice.
- **Coverage gaps.** The same file names Gurez and Kokernag (no route) and Karnah (terminal pinned short) as
  real gaps. Useful for §5 or §7.
- **District-centre placements.** `GAZETTEER_RECOVERY.md` gives 43 district-centre approximations; the audit
  gives 38; §4 uses 37. Recount from the current gazetteer before submission.
- **Stale public claims.** `ROUTE_PLAN_ASSURANCE_v3.4.4.md` and `PROJECT_INDEX.md` call the plan "MoHUA-compliant"
  at 43 buses per lakh on served population. The dashboard's `KASHMIR_HANDOVER.md` still says 342 permits and
  207 routes. Neither belongs in the paper; both should be corrected where they are public.
- **Trip rate and mode share.** `E:\kash\cross_evaluate.py` (lines 53-75) says the urban bus share of 9% was
  backed out of the e-bus totals for an assumed served population of about 222,000, and that the trip rate of
  1.6 comes from per-rider e-bus app data (women about 2 round trips a day, men about 1.2). The project holds only
  monthly aggregates, so the trip-rate derivation cannot be checked. Section 4 v5 states both.
- **District-centre routes.** The 37 district-centre placements are confirmed (`E:\kash\kashmir_gazetteer.csv`),
  but the earlier "19 routes, 93 buses" could not be reproduced: matching route names gives 13 routes and 55
  buses, matching map positions 5 to 21 routes. Recompute from the plan's endpoint coordinates before quoting.
- **Field observations and bus associations.** The co-author draft (§6 block) describes a cross-check with the
  Eastern and Western bus associations and six other associations, and a table of field observations. No raw
  sheets are in any project folder (decision A2).

## 11. From the E: drive sweep

Folders read: `E:\audit` (an independent audit of plan v3.3.7, dated 10 June 2026), `E:\OSRM_Jammu` (the
routing engine's map data) and `E:\JTM` (two reference reports). Personal and unrelated folders were not
opened. Most of the June audit's findings were fixed in later versions; these still matter:

- **Big buses are missing from the private input.** Of the Srinagar RTO's 548 heavy-bus permits, 544 record no
  route, so only 4 reach the plan (`E:\audit\Kashmir_Transit_Audit_v3.3.7.md`, Finding 2; still true:
  `existing-routes.csv` has 4 HPV rows). The private permits in the plan are almost all minibuses. The paper
  should say so wherever it describes the vehicle mix of the existing network.
- **Official route lengths were available and not used.** The scanned JKRTC timetable's Anantnag depot table
  has fare and route-length columns, which were dropped when it was transcribed (same file, Finding 4). They
  are the only official route distances in the source data, and they could serve as an independent check on
  the routed distances.
- **One transcription error remains.** The timetable's City Schedule 1, row 6, says Soura; the transcription
  says Buchpora, and "Srinagar to Buchpora" is still an input row.
- **Same map extract for walking and driving.** The routing engine's `india-latest.osm.pbf` has the same SHA-256
  as the extract recorded for the walking network (`681021c5...`); the engine graph was built on 16 March 2026.
  §4 can state that road distances and walking catchments use the same OpenStreetMap extract.
- **Two Indian practice reports** that are not in the reference list: Shakti Sustainable Energy Foundation
  (2016), *Roadmap for Improving City Bus Systems in India*; WRI India, *Route Rationalization and Mass Transit
  Feeder Route Design* (Bengaluru feeder pilots). Relevant to §1–§2 rather than §4.
- **Personal data still on disk.** `E:\bus-sathi-dashboard-main\master_trips.csv` is the named-driver trip file
  flagged in the security audit; it was not opened. It should not be copied into any shared folder.
- **Correction to the June audit itself.** It calls `SMART CITY BUS LIST - Copy.xlsx` Jammu data. The
  intra-city sheet lists Srinagar routes (Parimpora to Harwan, Batamaloo to Hazratbal and others); it covers 8
  routes and 32 buses, so it is an older or partial list, not the 30-route, 98-bus deployment.

## 12. Added 22 October 2026, while writing Section 4 v6

- **GPS run count (fixed 22 October 2026 in §0, §1, §3, §5, §6, cover letter, FINDINGS, CL-18).** §3 and §6 gave "43,809 recorded runs". `v04_gps_validation.json` (corpus) shows
  that 43,809 counts run-corridor incidences, 17.3 per run; the data hold 2,526 distinct service runs (2,426 after
  the map-match gate) from 157 app accounts. An account is not a verified person or device. Correct §3, §6 and
  claim-ledger row CL-18.
- **Tourist multiplier.** v5 of Section 4 applied μ = 1.3 to the destination score. The engine applies it to the
  resident count (`transit_kashmir_v3.py:1863`). Fixed in v6, Eq. 5.
- **Tier overrides.** Besides the e-bus lock and the social floor, the engine moves routes lying within 5% of the gap between the two Jenks breaks
  by road role (lines 2895-2925). The district-headquarters floor applies only to regional routes that
  already carry the social flag. Both now in v6, §4.7.

## Not found anywhere

No document in any folder supports these, so they stay as assumptions or open questions:
the "Srinagar Traffic Police bottleneck studies" behind the 2.2 multiplier; an operator document for the 15%
spare ratio; any consent record for the GPS collection; the raw field-observation sheets.
