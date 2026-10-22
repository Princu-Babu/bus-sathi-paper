# Independent critic review: "Planning What You Cannot Count" (Kashmir Division bus rationalisation)

Reviewer stance: senior transport-planning academic, skeptical, reviewing manuscript plus evidence chain.
Date: 23 October 2026. Branch reviewed: `fix/audit-phase1` of `E:\kash-paper` (HEAD `1813f08`), engine
`E:\kash` (HEAD `c8cab92`). Read-only review; the only file written is this one.

Scope of "new". I read `PARAMETERS_AND_DEFENSIBILITY.md`, `MISSED_CONTEXT_2026-10-16.md`,
`PENDING_DECISIONS.md`, `CLAIM_LEDGER.md`, `gaps/*.md`, `audit/2026-10-02/STATE.md`, `99_TRIAGE.md`,
`FIX_STATE.md` and the slice reports (05, 08 and others by grep) before reporting. Everything in those files is
treated as known. Where a finding overlaps a known item, I say how it differs. Known Tier-1 items that are still
present in the text (43,809 is fixed, but "+1.4 % passes", "285,914 synthetic persons", "+68.5 % over ~600",
"pre-registered", 97.8 % without the 68.3 % caveat, 65.1/47.6/0.51, cost ₹642–1,054 crore, 15,360 vs 14,336
Sobol evaluations, "eleven" vs "twelve" sampled inputs) are listed once in section 3 and not counted as findings.

---

## 1. Summary verdict

**Recommendation: major revision. At *Transport Policy* as it stands: reject and resubmit.**

What this paper is: a careful, unusually self-critical audit of a bus plan that the lead author built with an
engine, revised over about fifteen versions in review with the transport regulator, and then evaluated with an
independent analysis repository and driver-app GPS. What it contributes: a handful of transferable diagnostics.
A permit register is not a route register. Straight-line catchments inflate reach. A per-kilometre "sanity"
cap can become the binding model. A single-headway, frequency-blind coverage metric hides where the fleet goes.
What it does not contribute, despite the framing: a validated or demand-independent planning method. The paper
already concedes most of this. My review adds a further problem. Several headline numbers that the authors
now treat as their solid ground are themselves artefacts of the pipeline. The 157 corridors and the 99.4 %
retention are partly a geocoding artefact. The "demand" proxy is proportional to the published headways. The
fleet carries about 80 buses of per-route rounding spare. "30 % of the fleet gives 92 % of coverage" is a
property of the metric, not a finding about the network. None of this is fatal to a case-study paper, but each
changes a sentence in the abstract. Taken together they mean the paper is better positioned as an audit case
study in a case-study journal than as a methods contribution in *Transport Policy*.

---

## 2. New findings, ranked

Severity scale: **fatal** = invalidates a headline claim if uncorrected; **major** = changes a headline number
or its interpretation; **minor** = changes a secondary claim or a sentence. "Confirmed" = I reproduced it from
code or data in this review; "suspected" = plausible but not fully verified.

### N1. [MAJOR, near-fatal for the headline] The 157 corridors and 99.4 % retention are partly a geocoding artefact: 23 distinct village corridors collapse onto district-centre points, and their services vanish from the plan — CONFIRMED

**Where.** Abstract `paper/sections/00_abstract.md:14-15`; highlights `paper/front_matter/highlights.md:6`;
§4.3 `paper/Section4_Methodology_2300.txt:27`; §4.6 `:79`; §5.1 `paper/sections/05_results.md:10-21`
("155 at 100 m, so the count is structural, not a rounding artefact"); §5.9 `:151-165`; CL-02/07/08
(`paper/CLAIM_LEDGER.md:32,37,38`); corridor key `analysis/q01_data_quality.py:152-161`.

**Evidence.** The corridor key is an undirected hash of endpoint coordinates rounded to 4 decimals. The gazetteer
puts many different villages on one district-centre coordinate (`E:\kash\kashmir_gazetteer.csv`, for example lines
73, 94, 95, 102, 104: NARISTAN, TARTHPORA, TRAL DADSUR, ZACHALDAR, ZURHAMA all at 34.014, 74.719, tagged
`district_centre(Budgam)`). Those villages therefore hash to one "corridor". I re-keyed `data/raw/existing-routes.csv`
by coordinate and by place name. Within 10 coordinate-corridors there are several distinct name pairs. After
removing spelling variants (Pantha Chowk/Pathachowk, Uri/Uri Baramulla), **23 distinct village corridors (32
rows) are hidden inside 8 coordinate-corridors.** Examples:
- Srinagar to {Beeru, Gaguldara, Sheikhpora Kakuthal, Milyaal, Zurhama, Tarthpora, Gazriyal, Tral Dadsur, Naristan,
  Zachaldar}: 10 rows, one Budgam point.
- Srinagar to {Mawan, Kaprun, Chowgund, Vailo, Chakil Pora}: one Anantnag point.
- Anantnag to {Lammer, Haftnar, Kherum}; Baramulla to {Garkote, Nambia, Kachoo}; Srinagar to {Fathgath, Maidanan,
  Ijara}; Srinagar to {Bankoot, Arin, Malangam}; Srinagar to {Lettar, Achguze}; Srinagar to {Khull Ahmadabad, DH Pora}.

In the published plan (`data/raw/Rationalised_Routes_Kashmir_v3.csv`) each group keeps exactly one active route
and the rest are `MERGED_INTO_TRUNK`. "Srinagar to Beeru" (FDR-384, line 453, 25 km, 3 buses, 50 min) absorbs
nine other villages' services. Seven of them are tagged MPS (state-corporation) services (for example line 469
Zurhama and line 478 Tral Dadsur).

At least one placement is in the wrong district, and the plan's own files show it. The e-bus route SSCL-25
"Batamaloo to Dadsara Tral via Awantipora" (`data/raw/chalo_deployed_buses.csv:32`) terminates at
`PW-04-01 Dadsara Tral, Pulwama, Tral tehsil, 33.930, 75.110` (`data/raw/Kashmir_Stops_Master_v4.csv:85`).
The permit row "Srinagar to Tral Dadsur" sits on the Budgam point, about 37 km away, and carries route code
`SRBG…` (Budgam). From local geography I suspect, but have not verified, that Zurhama, Zachaldara and Tarathpora
are in Kupwara and Naristan is in Tral (Pulwama).

The same collapse creates phantom short routes. "Garkote to Baramulla" (line 505) is 2.96 km Urban with 2 buses.
"Lammer to Anantnagh" (line 555) is 4.33 km Urban with 2 buses. Both are the distance from a district-centre pin
to the town pin, not a real service.

**Consequences.**
- The corridor count is at least about 180, not 157. Corridor retention is about 156/180 = 87 %, not 99.4 %. The
  "71.0 pp change of unit" decomposition (CL-07) is overstated by the same margin.
- The §5.1 sentence "the count is structural, not a rounding artefact" is wrong. The count is stable to rounding
  because the artefact is upstream, in the gazetteer.
- The 13,087 "lose access" (§5.9) counts only suppressed via-places (`analysis/a12_equity_gini.py:314-460`). By
  construction it excludes these terminal villages, which lose their direct service entirely.

**How this differs from what is known.** F-05-10 (`audit/2026-10-02/05_method_fidelity_paper_vs_engine.md:116,135`)
counted shared coordinates and named "two genuine collapses". It did not connect them to CL-02/07/08, to the losers
count or to the wrong-district placements. §4.3 now discloses "37 villages at their district's centre", but not
that this merges distinct corridors.

**Fix.** (i) Re-key corridors on (coordinate, normalised name) or on name with fuzzy de-duplication, and report
157 as a lower bound with the name-aware count beside it. (ii) Re-place the 37–38 district-centre villages
(OSM/Wikidata, as already done for the ArcGIS 26), or at minimum list the services the plan drops. (iii) Add
terminal-village losses to Table 5g. (iv) Remove the "structural, not a rounding artefact" sentence. The highlights
bullet "the plan keeps 99.4 %" should not survive in its current form.

### N2. [MAJOR] The "demand" proxy is proportional to the published headway; Eq. 14 misdescribes it; the regional-headway rule and the demand-sized fleet inherit the circularity — CONFIRMED

**Where.** Engine `E:\kash\transit_kashmir_v3.py:5677-5689`:
```
inv_h       = 1.0 / headway
mean_inv_h  = float(inv_h.mean()) ...
freq_weight = inv_h / mean_inv_h
corridor_share = (freq_weight / eff_comp).clip(upper=1.0)
daily_demand   = (pop_raw * corridor_share * mode_share * PHASE4_TRIP_RATE * PHASE4_CORRIDOR_CAPTURE_SCALE)
```
Paper §4.9 Eq. 14 `paper/Section4_Methodology_2300.txt:115-117` describes s(r) as "the route's share of its
corridor's residents". §4.7 `:89` describes the rural rule. Consumers include `analysis/a17_demand_sized_fleet.py`
(uses `Daily_Demand_Pax`) and a07.

**Evidence.** I rebuilt `Daily_Demand_Pax` for all 186 active routes from published columns:
`Population_Served_Raw × (freq_weight / max(1, Corridor_Competitors × Overlap_Metric)) × m_type × 1.6 × 0.33`,
with the mean of 1/h taken over all 644 rows. The reconstruction matches the published value to within ±2 %
(mean ratio 1.000; the residual is rounding of `Overlap_Metric`). The share cap of 1 never binds. So
demand ∝ 1/headway. A 15-minute e-bus route gets weight 1.98, a 35-minute route 0.85 and a 50-minute route 0.59.
For an identical catchment, the e-bus route is assigned 3.4 times the demand of a rural lifeline.

**Consequences.**
- *Eq. 14 is misdescribed.* The frequency weighting is the largest route-level factor after catchment size, and
  the paper does not mention it.
- *The regional rule is internally inconsistent.* `apply_regional_demand_headway` (`transit_kashmir_v3.py:5551-5586`)
  sets h_new = h0 × 0.55/load, which assumes demand is fixed (elasticity 0). The demand model has elasticity 1, and
  capacity also scales with 1/h. Load is therefore roughly invariant to headway, and the rule's "proportional
  lengthening" has no behavioural basis. In the plan, 62 of 67 regional routes hit the 50-minute cap.
- *The demand-sized fleet (a17, "508 of 1,011 explained by demand") partly echoes the published headways.*
  Removing the frequency weight (setting every route to network-mean frequency, total demand preserved) changes
  little in total (551 → 552 at ρ = 0.70, no ceiling). It does move the backbone's demand-sized fleet from 148 to
  104 buses (−30 %) and the rest from 403 to 448. The split of the fleet between "demand" and "standards", by
  class, depends on the policy headway.
- *κ is entangled with the 15-minute e-bus headway.* κ was fitted on e-bus routes carrying weight 1.98. Without
  the weight, κ would be about twice as large. Separately, the urban share m = 0.090 was "backed out for an assumed
  served population of about 222,000" (§4.9). The paper's own network walkshed of the 30 e-bus routes is 687,629
  residents (`data/derived/a11_coverage_accessibility.json`, frequent_network_coverage ≤ 15 min). The ratio,
  222,000/687,629 = 0.32, is numerically κ. The decomposition into g, m and κ is cosmetic: one parameter, fitted
  to one total. §4.9's "only the product κgm is identified" is honest but understates this.
- *Inactive rows affect active demand.* The normalising mean is taken over all 644 rows, including 458 merged
  rows that run no service.

**Not previously recorded.** No hits for `freq_weight`, inverse-headway or frequency-weighted demand in the audit,
PARAMETERS, gaps or ledger files.

**Fix.** Describe s(r) truthfully. Either drop the frequency weight from the demand proxy and recompute a07, a17
and the rural rule, or keep it and state that the proxy is conditional on the plan's own frequencies, so it
cannot justify those frequencies.

### N3. [MAJOR] The fleet carries about 29 % spare on non-backbone routes, not 15 %, because spare is rounded up route by route; a pooled 15 % would remove about 79 buses — CONFIRMED

**Where.** Eq. 12 `paper/Section4_Methodology_2300.txt:103-105`; `analysis/fleet_model.py:134-143`
(`op = ceil(cycle/h)`, `raw = ceil(op*spare)`, floor 2); engine same.

**Evidence.** From the published plan: Σ N_op (buses in service, ceil(cycle/h)) = 794 network-wide and 564 off
the backbone. The published fleet is 1,011 and 728. **The effective spare ratio is 1.27 network-wide and 1.29
off the backbone**, against the stated σ = 1.15. A pooled depot-level spare of 15 % on 564 in-service buses is
649, which is 79 fewer than 728. The double ceiling explains this:
- 8 routes with N_op = 1 get 2 buses (100 % spare);
- 31 routes with N_op = 2 get 3 buses (50 % spare);
- Σ cycle/h before any ceiling is 488.5 off the backbone, so the two ceilings together add about 166 buses (23 %
  of the non-backbone fleet).

This is also why Sobol' attributes 0.946 of fleet-A variance to the spare ratio
(`data/derived/a09_monte_carlo_sobol.json`, sobol.fleet_A). The ceiling turns σ into a step function on 186 routes.

**How this differs from what is known.** PARAMETERS notes σ = 1.15 is unsourced. F-10 noted spikes in the fleet
histogram. Neither identifies that the *applied* spare is about 1.27–1.29 or that spares are not pooled. Real
operators hold spares at depot level and interline. This is standard practice (Vuchic 2005; Ceder 2007), and a
transport reviewer will spot it.

**Fix.** Report N_op (794) and the fleet with pooled spare (about 913 network-wide at 1.15 × 794) beside 1,011.
State that the rounding is a design choice. The operator data hold direct evidence on availability (N16).

### N4. [MAJOR] The composite index, the paper's central instrument, changes the fleet by 35 buses (3.5 %); the §2.8 "decision logic" is not what produced the fleet — CONFIRMED (a deeper version of a known item)

**Where.** §2.8 `paper/sections/02_literature.md:104-112` ("Demand enters at one point, the frequency rule.
Replace that rule with policy headway bands assigned by an ordinal open-data index, and everything downstream is
computable"); §4.5–4.7; §5.7–5.8; V5/V6.

**Evidence.** Cross-tabulating the published plan by tier, type and headway:
- MP and LP both run at 35 minutes in the city and at 50 (or 35) in the regional class.
- The 30 e-bus routes are locked to 15 minutes regardless of index.
- The 67 regional headways come from the load proxy (N2), not the index.

Only the 25 non-backbone HP routes owe their headway (20 minutes) to the index. Their fleet is 120. At 35 minutes
it would be 85. **The index's entire effect on the fleet is about 35 buses of 1,011.** The tier stability analysis
(97.3 %/97.8 %), the 68.3 % published-vs-objective agreement, the weighting comparisons and the Sobol' tier
indices all concern a classification that drives about 3.5 % of the fleet.

**Known part.** F-05 recorded that "MP vs LP changes nothing". **New part.** The quantification, and the fact
that this contradicts the stated core contribution in §2.8 and the abstract's claim of "decision-robust in its
hierarchy".

**Fix.** State it in §4.7 and §5.7. Re-weight the paper's emphasis away from tier stability, towards what
actually sets the fleet: headway standards, cap and rounding.

### N5. [MAJOR] Two-thirds of the calibration ridership is women's travel that appears to be fare-free with government reimbursement; this is undisclosed and affects κ, m, g, V2, the "growth needed" result and transferability — CONFIRMED (data structure); policy SUSPECTED (to verify)

**Where.** `data/raw/chalo_ridership.csv:1`; source `E:\kash\SSCL Data Updated.xlsx`, sheet "Ridership Data".
Used in §4.9 (κ, m, g), §5.11 (load, "ridership must grow 2.2–4.5-fold"), §6 V2, and MISSED_CONTEXT item 4
(64.5 % women share).

**Evidence.** The sheet separates "Paid Pass Count" from "Women Passenger Count". It has a separate "Women
Ridership Value" column. "Cash EPKM" equals paid collection over operated km: May 2025, 5,913,049/526,803 = ₹11.22.
"Overall EPKM" adds the women's value: 18,478,659/526,803 = ₹35.08. Women's value per trip is ₹18.5, against paid
revenue of ₹17.9 per paid trip. This is the signature of fare-free travel for women reimbursed per trip. Women
are 7,504,621 of 11,632,326 boardings (64.5 %). As I recall, though I have not verified it, J&K announced free bus
travel for women in early 2025, so the whole calibration window (May 2025 to April 2026) is post-policy.

**Consequences.**
- The demand scale fitted to a service that is free for two-thirds of its riders is applied to fare-charging
  private minibuses. Eq. 14 and the regional rule therefore over-state demand where the fare is paid.
- The 64.5 % women share is a policy effect, not a gendered demand pattern.
- The "ridership must grow 2.2–4.5×" benchmark is relative to a subsidised base.
- The paper has a natural experiment and an equity angle it does not use.

No mention of fare-free travel anywhere in sections, audits or registers (grep).

**Fix.** Confirm the policy and its start date with the operator. Disclose it in §4.9 and §6. Either fit κ on paid
boardings only (as a sensitivity) or state the bias direction.

### N6. [MAJOR, framing] "Thirty per cent of the fleet delivers 92 % of coverage" is a property of a frequency-blind metric; 31 routes (148 buses) add no coverage at all — CONFIRMED

**Where.** Abstract `:22-23`; highlights `:9`; §8 `paper/sections/08_conclusions.md:25`; cover letter
`paper/front_matter/cover_letter.md:27-28` ("the rest buys frequency"); `analysis/a15_scenarios.py:150-255`.

**Evidence.** From `data/derived/a15_funding_sequence.csv`, the greedy curve gives 5 % of the fleet → 48 % of
reach, 10 % → 67 %, 20 % → 84 %, 30 % → 92.5 %, 50 % → 98.5 %. **31 routes (148 buses) add zero new residents**
once the other 155 are bought. That is order-independent: they lie entirely inside the union of the others'
walksheds. Twenty-one are urban, two are e-bus. **85 routes (466 buses) add fewer than 1,000 residents each.**
Because coverage counts any route at any frequency, a two-bus-per-route network (372 buses, 37 % of the fleet)
reaches 100 % of the plan's coverage. The 30 %/92 % figure is one point on a concave curve whose shape is set by
the metric.

**Policy reading the paper does not draw.** "The rest buys frequency", but the paper's own load estimates
(median 0.113 peak; 168/186 below 0.40) say that frequency is not needed for current demand. Thirty-one routes
wholly inside other routes' catchments is exactly what a rationalisation should merge. That cuts against
presenting 99.4 % corridor retention as a virtue (§5.1 policy line `:23-24`).

**Fix.** Replace the headline with the curve and the minimum-service network size. Report the 31 zero-marginal
routes as merge candidates. Pair coverage with a frequency-weighted measure (departures per hour within the
walkshed) for the funding sequence.

### N7. [MAJOR] The "observed pace" fleet of 1,130–1,266 is itself a lower bound: the 384 regional buses keep a cap whose implied bus running time already equals the desk-researched (largely car) times — CONFIRMED (deeper version of a known item)

**Where.** Abstract `:20-21`; §4.11 `paper/Section4_Methodology_2300.txt:129` ("E-bus and regional routes keep
modelled cycles, as no usable pace was observed"); §5.7; `data/derived/a09_monte_carlo_sobol.json`
(fleet_B_Regional_District 376–398).

**Evidence.** Every regional route runs at exactly 40.0 km/h round-trip average including layover (cap 1.5 min/km
binds on 71/71). Srinagar–Tangdar (151 km, over Sadhna Pass) has a one-way running time of 206 minutes. I parsed
`data/raw/ROUTE_DEEPDIVE_LEDGER.csv` `Real_OneWay_Time` (the same ledger whose distances were substituted into the
plan) and compared it with modelled one-way running time (cycle/2/1.1). The median ratio is 1.07, and on 50 of 71
routes the researched time is longer than the modelled bus time. Tangdar is 1.46 (about 5 h). Audit 05 found these
times are car times. Buses with stops are slower than cars, so the regional cycle is understated by at least that
margin. Regional buses are 384 of the 1,182 regime-B median (32 %) and are held fixed.

**Known part.** PARAMETERS ("state the rural cap as untested"); scenario S2 (two corridors → 1,271); audit
05:113 (ledger times are car times). **New part.** The ledger already gives per-route evidence, for all 71
regional routes, that the cap is too fast. The abstract's 1,130–1,266 is presented as "at observed pace" but
excludes a third of the fleet whose pace is known to be optimistic.

**Fix.** In the abstract, either give S2 (1,271) as the upper reference or add a regime B′ with regional cycles
from ledger times × a bus/car factor. At minimum, say "urban and peri-urban pace observed; regional pace assumed
and likely optimistic".

### N8. [MINOR–MAJOR] The merge rule depends on the direction in which the clerk wrote the permit — CONFIRMED in code; magnitude INDICATIVE

**Where.** `E:\kash\transit_kashmir_v3.py:2641,2697` (`start_i.distance(start_t) <= OD_PROXIMITY_TOLERANCE_M`);
§4.6 `paper/Section4_Methodology_2300.txt:75`.

**Evidence.** The merge test compares only the two routes' start points. The duplicate consolidation was made
undirected in v3.4.1. The overlap merge was not. Two fully overlapping services written "A to B" and "B to A"
never merge. I computed 80 m-buffer overlap among the 186 active geometries (`Rationalised_Routes_Kashmir_v3.geojson`).
Of pairs with φ ≥ 0.65, 264 pass the start-point test, **250 fail it only because of orientation** (start of one
within 2.5 km of the other's end), and 234 fail both ways. This is a diagnostic on survivors, not a re-run of the
leader-only algorithm, and geometry orientation is taken as drawn.

**Why it matters.** It helps explain why spatial consolidation is only 0.16 pp (CL-07). The rule's main effect is
set by an arbitrary data-entry convention. PARAMETERS notes 2.5 km is "judgement, never varied". The orientation
asymmetry is new.

**Fix.** Make the test symmetric (min over start-start and start-end) in S4 and report the change. Disclose the
asymmetry in §4.6.

### N9. [MINOR] §2 disclaims the network-catchment correction; §8 and the cover letter call it the central contribution — CONFIRMED

`paper/sections/02_literature.md:58-60` ("Two results from this tradition bear directly on our method, and we
claim neither. First, straight-line buffers overstate catchment population…"). Against this,
`paper/sections/08_conclusions.md:12` says "The central methodological contribution is to measure catchments on a
walkable pedestrian network", and `paper/front_matter/cover_letter.md` lists it as the second of three results. §2
was rewritten after the October audit (Sharvesh's PR), so F-08-07 did not see this exact contradiction. A reviewer
will quote §2.4 back at §8. **Fix:** in §8, call it an application whose size in this setting (29–53 %) is the
finding, not a methodological contribution.

### N10. [MINOR] The "network catchment is a formal upper bound, so 37.4 % is a lower bound on the bias" argument fails where OpenStreetMap footpaths are missing — SUSPECTED direction, CONFIRMED premise

`paper/sections/05_results.md:33-36`. The argument holds only if the walk graph is complete. Where paths are
missing, network distances lengthen and the network catchment *under*-states the true walkshed, so the bias is
over-stated. `paper/tables/table02c_osm_completeness.md` shows mapped walkable network of 0.42–0.89 km/km² in
Bandipore, Kupwara, Anantnag, Kulgam and Ganderbal, against 5.1 in Srinagar. Rural lanes and old-city gullies are
the likeliest gaps. F-03-11 dealt only with node-sampling in code. This is a different and larger issue. **Fix:**
drop "formal upper bound". Report the bias by district alongside OSM density, or as a range bounded by τ.

### N11. [MINOR] The permit digitiser destroys multi-via strings: 17 of 18 multi-via Srinagar permits lost every via point — CONFIRMED

`E:\kash\latlon.py:65` removes commas (`re.sub(r'[^\w\s-]', '', ...)`) inside `clean_location`, which is applied to
the via string at `:186`. `geocode_via_string` then splits on commas (`:69-80`, called at `:220`). Source
`Mini Buses Routes in Srinagar.xlsx` has 18 multi-via strings, for example
"RAMBAGH, EXCROSSING, BUND , SRTC, NEW BRIDGE, KHAYA, RAJOURI KADAL". In `data/raw/existing-routes.csv`, all 444
private via fields are single tokens. The 17 multi-via rows have no geocoded via, and some names are fused
("KHAYAMKHANYARRAINAWARISAIDA KADALDALGATE"). Affected: LD–Budgam ×4, Parimpora–Budgam via Batamaloo/Tengpora ×6,
Chanapora–Soura ×2 and others. Effect: those permits' alignments and via-routings ("32 suppressed via-routings",
losers) are computed without their recorded vias. Small in count, but a confirmed defect in the evidence chain's
first step. **Fix:** split before cleaning, re-geocode the 17 rows' vias, and re-run q01/a12 counts.

### N12. [MINOR] The e-bus per-route deployment file is labelled as a proposal — CONFIRMED (label); status UNVERIFIED

`data/raw/chalo_deployed_buses.csv:1` (and the source sheet "Route Wise deployed Buses") has header
`PROPSED ROUTE NO, PROPOSED ROUTE NAME, New Deployement, 9 Meter, 12 Meter`. The paper uses it as the operator's
deployed fleet N^emp (Eq. 13 floor), as the V2 per-route comparison (ρ = 0.22) and in the 777 baseline
("CHALO runs 98 buses on the 30 backbone routes", §6 `paper/sections/06_validation.md:50`). The only timetable-backed
list (`SMART CITY BUS LIST - Copy.xlsx`) covers 8 routes and 32 buses (MISSED_CONTEXT item 11). The ridership is a
network aggregate, so nothing in hand shows that buses actually run on these 30 routes in these numbers. **Fix:**
ask the operator (bundle with A4). Until then, write "the operator's route allocation of 98 e-buses".

### N13. [MINOR] The GPS corpus behind the abstract number is not reproducible from the shipped data, and most runs are not used in the time comparison — CONFIRMED

`analysis/v04_gps_validation.py:150-175` hard-codes `runs_total=2526, runs_clean=2426` from private, unshipped
files (`derived=False`). Of 2,426 clean runs, only 989 (41 %) are assigned to any corridor. The cap/pace analysis
uses 964 runs on 18 corridors. The plan-vs-observed time test uses 470 runs on 5 corridors (known). The abstract's
"Against 2,526 driver-GPS service runs, modelled run times are too fast" (`:18-19`) implies the full corpus
supports the comparison. **Fix:** "Against 964 GPS runs on 18 corridors (of a 2,526-run corpus)". State in the
data-availability text that the corpus counts are not recomputable from the public release.

### N14. [MINOR] Sobol' mixes a definitional choice with uncertain parameters, and the coverage interval is set by an asymmetric prior — CONFIRMED

`analysis/common.py` PARAMETERS: WALK_CATCHMENT_M triangular (300, 400, 800). In
`data/derived/a09_monte_carlo_sobol.json`, coverage ST for walk radius is 0.975 and the MC coverage median is
26.6 % (22.0–32.2 %), not the headline 24.2 %. The walking radius is a policy definition, not an uncertain
physical quantity. "Coverage depends on the walk-radius definition" (§6 V5) is a tautology dressed as a finding,
and the skewed prior manufactures an upward-shifted interval. **Fix:** treat walk radius as a scenario (300/400/800,
already in a08a), not a sampled input. Keep Sobol' for genuinely uncertain physical parameters.

### N15. [MINOR] The GPS window is seasonally unrepresentative and this is not discussed — CONFIRMED (dates); effect SUSPECTED

GPS: 6 February to 29 June 2026 (`paper/sections/06_validation.md:62-63`). This spans late winter and Ramadan
(about 18 February to 19 March 2026). March boardings in the operator data fall to 788,434, against roughly
0.9–1.0 million in other months (`SSCL Data Updated.xlsx`). Observed pace, duty factor (0.242) and dwell feed
regime B, the deadhead bound and the waiting-time result. No section mentions season or Ramadan in connection with
the GPS. **Fix:** split pace and duty by month, or at least by Ramadan vs non-Ramadan, and report the difference.

### N16. [MINOR, opportunity] The operator data contain direct evidence on fleet availability that the paper calls unsourced

PARAMETERS and MISSED_CONTEXT say there is no operator document for the 15 % spare. The operator sheet reports
operated km as 70–91 % of scheduled km by month (May 2025: 526,803/675,800 = 78 %; March 2026: 70 %; April 2026:
90 %). This is not a spare ratio, but it is the best available evidence on availability and reliability. It
suggests the effective reserve needed is at least of the order the plan assumes. **Fix:** cite it as indirect
support for σ, alongside N3's pooling point.

### N17. [MINOR] §3.3 says permits "specify an area of operation rather than a route"; the paper's own corridors are built from the permits' route fields — CONFIRMED

`paper/sections/03_study_area.md:66-67`. The source register has `Route Covered`, `From Location`, `To Location`,
`Via Location` (`Mini Buses Routes in Srinagar.xlsx`), and §4.3 builds 157 corridors from them. "Perpetuity" is
already flagged (F-09-03/04). This sentence is a separate contradiction and undercuts §5.1's own diagnosis.
**Fix (co-author text):** "specify end points and sometimes a via, but no schedule, frequency or stopping pattern".

---

## 3. Evidence-chain trace

| # | Claim (location) | Chain checked | Result |
|---|---|---|---|
| 1 | 614 records = 445 private + 169 state-corporation (abstract :14, §4.2) | Source xlsx (1,259 Srinagar-RTO rows, 453 with both ends) → `latlon.py` → `existing-routes.csv` (MPV 347, LPV 94, HPV 4; Regular 76, City 49, MPS 43, MTS 1) | **Holds** |
| 2 | 548 heavy permits, 544 with no route (§4.2) | Source xlsx crosstab | **Holds** |
| 3 | 157 corridors; 99.4 % retained; 71.0 pp change of unit (abstract, §5.1, CL-02/07/08) | `existing-routes.csv` → q01 key → plan CSV | **Reproduces numerically; invalid as a corridor count** (N1) |
| 4 | 186 active; 1,011 = 728 + 283; 187/754/70 (§4.8 Eq. 13) | Plan CSV sums | **Holds** |
| 5 | Headways 15/20/35/50; "62 of 67 regional at 50, 5 at 35" (§4.7) | Plan CSV crosstab | **Holds** (MP regional at 50 while 5 LP regional at 35, an inversion the rule produces) |
| 6 | Cap binds on 169 of 186 (abstract, §4.8) | Plan CSV: cycle = 2ℓω on 170 at ±0.6 min; a09 says 169 | **Holds** |
| 7 | 35.5 % → 24.2 %; median 37.4 % (abstract) | `a02_network_catchments.json`: 2,339,393.75 → 1,592,846.75; 37.39 = per-route median "spurious share of Euclidean" (overstatement of network is 59.7 %) | **Numbers hold; base issue known** (F-14-27) |
| 8 | 10.4 % near a 15-minute service (abstract) | `a11…json`: 687,629 / 6,584,762 | **Holds** |
| 9 | 2,526 runs (abstract) | `v04` constants `derived=False` | **Not reproducible from repo** (N13) |
| 10 | Fleet 989–1,058 / 1,130–1,266 (abstract) | `a09…json` headline | **Numbers hold; B excludes the regional pace issue** (N7); A dominated by rounding (N3) |
| 11 | "Hierarchy robust (97.8 %)" (abstract :21-22) | a09 `tier_agreement_median` = 0.973 | **Stale** (known); the hierarchy moves 35 buses (N4) |
| 12 | 30 % of fleet → 92 % coverage (abstract :22-23) | `a15_funding_sequence.csv`: 299 buses → 92.5 % | **Numbers hold; interpretation fails** (N6) |
| 13 | Eq. 14 demand = κ g m s Σρ with s = corridor share of residents (§4.9) | Engine 5677-5689; reconstruction ±2 % | **Misdescribed** (N2) |
| 14 | κ = 0.33 fitted to 11.63 M boardings (§4.9) | Source sheet: 11,632,326 total, 7,504,621 women | **Holds; composition undisclosed** (N5) |
| 15 | Women share 64.5 % (MISSED_CONTEXT 4) | Same | **Holds; a fare-free policy artefact** (N5) |
| 16 | 98 e-buses on 30 routes (§6 V2, baseline 777) | `chalo_deployed_buses.csv` header "PROPOSED…" | **Unverified as operation** (N12) |
| 17 | 13,087 lose access (§5.9) | a12 losers = via-places only | **Excludes terminal-village losses** (N1) |
| 18 | Via-routings suppressed: 32 on 20 corridors (§5.1) | `latlon.py` via parsing | **Undercounted input** (N11) |
| 19 | Route-km 5,567.7 on 1,524.5 km of road (§5.5) | `a10…json` | **Holds** |
| 20 | WorldPop 95.6 % of 2011 Census (§4.2) | `table02d` | **Holds** (bias direction known) |

**Known Tier-1 errors still in the manuscript text on this branch.** §5 header still dated 30 September. The
following are still present: "+68.5 % over ~600" (`05_results.md:69`, `08_conclusions.md:9`), "285,914 synthetic
persons" (`05:40`, `07:173`, `08:20`), "+1.4 %" passing (`05:55`, `06:84`), 65.1/47.6/0.51 (`03:131`, `05:49`,
`06:86`, `07:168`), "pre-registered" (`05:137`, `06:53`, `08:29`), 97.8 % (abstract, `05:121`, `06:73`, `07:114`,
`08:25`), "eleven declared parameters" (`05:110`) against "twelve" (§4.11), "15,360 evaluations" (`06:66`) against
14,336 (§4.11 and a09), cost ₹642–1,054 crore (`05:203`), "reproducible end to end" (`08:9-10`). CL-61 in the
ledger says 303 buses; a15 allocates 299. These are known (99_TRIAGE Tier 1). They are listed only so the
"Phase 2 prose" step does not miss them.

---

## 4. What the paper does well

- **Self-scrutiny far above the norm.** Fourteen audit slices, a claim ledger, a parameter register graded by
  defensibility, and explicit disclosure of circularity (V2) and failed tests. Most published route
  rationalisation papers would not survive this level of checking. This one at least documents where it does not.
- **The permit-versus-route diagnostic is genuinely useful** for Indian RTO registers, even after N1 shrinks its
  headline. The idea that "route reduction" is mostly a change of unit is a policy-relevant warning.
- **Measured GPS against a modelled plan, at route level, in an Indian secondary city** is rare. Finding that a
  safety cap became the binding model is a transferable modelling lesson.
- **The analysis repository is well engineered**: frozen inputs, deterministic seeds, reproduction of the fleet
  arithmetic, data-as-limitations JSON blocks.
- **Honest headline posture** ("decision-robust, not demand-validated") is the right register for a demand-scarce
  study.

---

## 5. Career and publication outlook

### 5(a) Target journals, ranked by fit × acceptance odds

My reading of fit and odds is for the paper *after* the fixes in section 6. Impact and turnaround are indicative.
Check each journal's current Guide for Authors (the *Transport Policy* guide could not be fetched in October).

| Rank | Journal | Why it fits | Reframing needed | Typical review expectations |
|---|---|---|---|---|
| 1 | **Case Studies on Transport Policy** (Elsevier/WCTRS) | Built for single-case policy studies with transferable lessons. Indian cases are common. Tolerates "audit of a real plan" framing. | "What an open-data, regulator-reviewed bus plan can and cannot establish: lessons from Kashmir." Lead with the four diagnostics (permit ≠ route; network catchments; binding cap and rounding; frequency-blind coverage). Drop "framework". | Clear policy lessons, honest limitations, modest methods. Will not demand demand validation. Will ask for an implementation and institutional discussion. Good odds. |
| 2 | **Transportation in Developing Economies** (Springer) | Indian and Global South focus; India-based editorial board; methods-and-case papers welcome. | Same as 1, with more on Indian permit and MV Act context and PM-eBus Sewa. | Lower bar on novelty, higher on local relevance and data description. Good odds, lower international visibility. |
| 3 | **Journal of Public Transportation** | Practitioner-facing methods for service planning, fleet sizing and network redesign. | A shorter paper on "fleet-sizing artefacts": cap, per-route spare rounding (N3), frequency-blind coverage (N6), GPS pace. Generalisable beyond Kashmir. | Wants practical, replicable guidance; moderate rigour. Moderate odds. |
| 4 | **Journal of Transport and Land Use** (open access) | Accessibility measurement and open-data ethos; the catchment result fits. | Generalise the catchment piece. Ideally run the network-vs-Euclidean comparison for several Indian cities with OSM, and address OSM completeness (N10). | Methodological care on accessibility measures. Single-case catchment bias alone is not novel (the paper's own §2.4 says so). Moderate odds only if multi-city. |
| 5 | **Journal of Transport Geography** | Permit geography, coverage gaps, Moran's I and equity. | Needs a geographic research question (spatial structure of informal permit networks, or access deserts across a mountain region) and stronger theory. | Demanding on novelty and literature. Single-case planning audits often rejected. Low–moderate odds. |
| 6 | **Transportation Research Record** | Short methods papers. TRB Annual Meeting route. | Split out one method: GPS-observed pace vs modelled caps, or the permit-register corridor algorithm. | 7,500-word equivalent including tables. Next practical deadline is the August 2027 TRB cycle. Moderate odds, slow calendar. |
| 7 | **Transport Policy** (current target) | High prestige; policy audience. | Requires a real policy contribution: permit reform, contracting, operator transition, finance, regulator decision process. Currently present only in co-author blocks of §7. Must fix length, ethics, framing. | High desk-reject rate for single-city technical papers. Reviewers will press validation (none independent passes), demand-free framing and generalisability. **Low odds as is; possible after a policy-led rewrite.** |
| 8 | Public Transport (Springer), Transportation Research Interdisciplinary Perspectives (OA) | Reasonable fallbacks: planning methods; broad scope. | Modest. | Moderate odds; TRIP charges an APC. |
| — | Research in Transportation Economics, Travel Behaviour and Society | **Poor fit as written.** RTE needs an economics question (costing, contracting); TBS needs behavioural data. | TBS becomes a fit for a separate paper on the women's free-fare effect (N5) if pre-policy data can be obtained. | — |

Avoid low-scrutiny or predatory outlets. One reference already points to *Scientific Research and Essays*
(`ergun2011alteration`), which reviewers may read as a weak source.

### 5(b) What the paper can do for each co-author

The author list is taken from `paper/front_matter/credit_statement.md` and PENDING_DECISIONS B13 (six authors;
affiliations not in the repository). The CRediT table currently lists both "Krishna" and "Krishnan" plus a
"[Supervisor]". That needs resolving.

- **Prashant Bhadana (lead, early-career, no prior publications).** A first-author paper in CSTP or TiDE is a real
  asset for graduate applications or research posts. It shows independent end-to-end work: data engineering,
  modelling, GPS processing and policy writing. The bigger career risk is not a lower-tier venue but a
  **post-publication problem**. The realistic retraction or expression-of-concern vectors here are:
  - driver GPS collected without research consent or ethics review;
  - operator ridership and revenue data published without written permission;
  - incomplete AI-use disclosure (AI-researched distances that entered the plan; AI-drafted sections);
  - an undeclared conflict of interest with a regulator co-author.

  The numbers are now heavily caveated and are unlikely to trigger a retraction. Undisclosed consent or
  permission problems could. A retraction on a first paper follows a name in every database. Settle K2 (ethics),
  the operator permission and the AI declaration before submission, even if that costs two months. Also avoid
  submitting from a branch whose public repositories still differ from the paper. The linked repository is part of
  the record.
- **Prof. Ankit Kathuria (senior/corresponding).** Modest marginal benefit: one more applied case in a
  well-published profile, and a dataset and student pipeline for follow-ons. His exposure is reputational and
  institutional. As corresponding author he warrants the ethics statement and data permissions. He should insist
  on an IIT Jammu ethics determination (even an exemption) for the GPS, and should read §2/§8 for the novelty
  contradiction (N9) that a reviewer will use against the framing.
- **Student co-authors (Misti, Krishna/Krishnan, Sharvesh).** Authorship on a peer-reviewed paper helps
  applications. It is defensible only if each can explain and defend their section. Their sections (§1, §3, §7)
  currently carry the largest concentration of flagged errors: scope, perpetuity, CSE/MoHUA, area of operation
  (N17), Srinagar-only framing. Owning those fixes is what turns a courtesy line into a contribution. Sharvesh's
  executed literature review (5,488 records, 60 coded) is the most separable student contribution. It could
  become a standalone scoping review: "planning bus networks without demand data", targeted at *Transport Reviews*
  or *Transportation Research Interdisciplinary Perspectives*.
- **Avny (practitioner co-author with an official role).** Benefit: documented practice-research collaboration.
  Risk: competing interest (the regulator reviewed and shaped the plan's headway rules) and possibly a need for
  departmental clearance (A3). If clearance is not given, an acknowledgement is safer than authorship.

**Follow-on papers and datasets the work can seed (most promising first):**
1. **Women's free fares and e-bus ridership in Srinagar** (if the policy date and any pre-policy months can be
   obtained from the operator). A clean policy natural experiment with gender equity relevance. Fits *Transport
   Policy* or TBS far better than the current paper does.
2. **A digitised, de-identified permit-to-corridor dataset for Kashmir Division**, with the name-aware corridor
   key (N1) and an open gazetteer: a data paper (e.g. *Data in Brief*). Licensing and personal-data issues must be
   cleared first.
3. **Network vs Euclidean catchment bias across 10–20 Indian cities** using OSM and WorldPop, with OSM-completeness
   controls (N10): *JTLU* or *JTG*.
4. **Observed minibus pace, dwell and duty from driver-app GPS** (after ethics and de-identification), as an
   empirical input paper for Indian bus planning: TRR or *Public Transport*.
5. **A field boarding count on 10–15 stops** to test the index–demand link. This is the single cheapest step that
   would let a future paper claim validation.

---

## 6. Five things to do before submission, in order

1. **Fix the corridor unit (N1).** Re-key corridors with place names. Re-place the district-centre villages from
   open sources. List the terminal villages the plan drops. Re-state CL-02/07/08 and the 99.4 % highlight. This
   touches the abstract's first finding.
2. **Close the governance items that can end the paper after publication.** These are: an ethics determination
   for the driver GPS (K2); written operator permission for the ridership data, plus confirmation of the women's
   free-fare policy (N5), the "proposed" deployment status (N12) and Trip Count (A4); a regulator co-author COI
   statement and clearance (A3); and a complete AI declaration.
3. **De-circularise and re-describe the supply/demand arithmetic.** Rewrite Eq. 14 honestly or remove the
   frequency weight (N2). Report in-service buses (794) and pooled spare beside 1,011 (N3). Add the regional pace
   bound (N7). Then write the **one** fleet paragraph the triage asks for (1.12), using these numbers.
4. **Reframe and choose the venue first.** Present the work as an audit of an open-data, regulator-reviewed plan.
   The contributions are the diagnostics (permit ≠ route; network catchments; binding cap and rounding;
   frequency-blind coverage, N6; inert index, N4). Remove "central methodological contribution" (N9). Target
   *Case Studies on Transport Policy* (or TiDE) and cut to that journal's length, moving the rest to a supplement.
5. **Regenerate every number from the derived JSON in one pass.** The known Tier-1 stale values listed at the end
   of section 3 are still in §3, §5, §6, §7, §8 and the ledger. Then have one co-author who did not write the
   numbers trace the abstract end to end, as in the table in section 3.
