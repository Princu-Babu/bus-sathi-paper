# 6. Validation

> **Section owners:** Prashant, Avny, Krishnan. **Target length:** ~900 words. **Status:** complete draft
> for the established and planned channels. Every value cites `[CL-xx]`/`[F-x]`. **Standing constraints
> honoured:** convergent validity is stated first; the CHALO circularity is disclosed up front; ridership
> is never claimed as a validation target; no field or expert-elicitation data are fabricated.
>
> <!-- TODO (near-term, before submission): the expert-elicitation channel (Delphi/AHP) and a field
> boarding/enumeration survey are demand-side validation steps that are not yet in hand. This draft
> carries them as forward work in §6.4 rather than foregrounding their absence channel-by-channel. Team
> decision needed: either (a) convene the panel + run a stratified boarding count and promote them to
> executed channels, or (b) keep them as declared future work. Do NOT fabricate either dataset. -->


## 6.1 A convergent-validity frame, not a single test

A demand-free plan cannot be validated the way a demand model is, because there is no withheld
ridership series to predict. We therefore adopt a **convergent-validity** design: six channels, each
individually insufficient and each biased in a *different* direction, are assembled so that agreement
among them raises confidence while any one disagreement localises a specific weakness. The target is
explicitly **decision-robustness** — that the tier and fleet decisions survive scrutiny from every
independent angle we can construct from open data — and never a claim that the composite index (Eq. 7)
predicts travel demand. Table 7 records all six channels, their evidence source, test statistic,
threshold, result, and status.

Two disclosures come first, not last. The one ridership dataset available — CHALO electronic-ticketing
aggregates on the e-bus backbone — is **not independent of the plan**: the same published aggregate
anchors the capture scale $\kappa = 0.33$ in the quarantined plausibility term (Eq. 8) and is offered
as benchmark channel V2. V2 is therefore a **consistency check, not an independent validation**, and
is reported as such. Second, the driver-GPS layer measures vehicle motion and geometry only; it
carries **zero ridership signal**, so channel V4 validates the *supply* chain — geometry → speed →
run time → cycle time → fleet — and nothing about demand.

## 6.2 The six channels and their status

**V1 — Spatial cross-validation** (executed, module `v01`). The population surface is checked against
an independently mapped record of settlement, OpenStreetMap building footprints [@osm2024planet] (12,343 closed building
ways inside the division), with the pre-declared threshold Spearman $
ho > 0.60$. Two limits are stated
first: WorldPop uses building footprints as a covariate [@stevens2015disaggregating; @lloyd2017high], so some agreement is expected by construction,
and building coverage in the OSM extract used here is thin (it may also be partially filtered;
data/MANIFEST.md). At the scale the plan uses — the 186 route
catchments — footprint area tracks catchment population at **$
ho = 0.657$ (pass)**, building count at
0.544 (fail) `[CL-53]`. On a 1 km grid the correlation falls to **0.316 (fail)**, and the completeness
table explains why: outside Srinagar only 4–17 % of populated cells contain any mapped building
(Srinagar 31 %) `[CL-53]`. V1 therefore supports the population surface where the buildings are mapped
and is uninformative where they are not; it is reported as a partial pass, not rounded up.

**V2 — Benchmark consistency** (executed, module `v02`; circular, as disclosed in §6.1 — and more
so than that paragraph alone implies, because the engine also floors the backbone fleet at CHALO's
deployment on 2 of the 30 routes). CHALO runs 98 buses on the 30 backbone routes at about 855 bus-trips a
day (12-month mean); scaled to the plan's 15-minute headway that is **179–220 buses**, depending on
whether the operating day is taken as 13 or 16 hours. The plan's backbone fleet is 283, a ratio of
**1.29–1.58: V2 fails the pre-registered ±15 % band under every service-day assumption** `[CL-54]`, and the
rank correlation between CHALO's per-route deployment and the plan's per-route fleet is weak
($
ho = 0.22$, $p = 0.24$) `[CL-54]`. Even against the operator it was calibrated to, the plan provisions
more buses per route than frequency scaling alone explains. V2 cannot say whether the excess lies in
the plan's cycle times or in CHALO's buses covering longer cycles than its trip count implies; it
records the disagreement and localises it to the backbone.

**V3 — Expert elicitation** (module `v03`, forward work — §6.4). A structured Delphi/AHP panel would
ground the index weights against practitioner judgement (target Kendall's $W > 0.70$). Pending its
elicitation, the index weighting is derived by three data-driven schemes — equal, entropy, and PCA
(§4.5) — and the tier decision is shown to be robust across all three; the panel is planned rather
than presumed.

**V4 — Supply-side GPS validation** (established, module `v04`). The empirical layer is **43,809 clean
service runs from ≈157 driver devices, February–June 2026** `[CL-18]`; its results are detailed in
§6.3. This is the study's one fully executed observational channel.

**V5 — Global sensitivity** and **V6 — Decision robustness** (planned, module `a09`). A 5,000-draw
Monte Carlo consuming the GPS pace prior yields Sobol' variance decomposition (V5) and a fleet 90 %
confidence interval with a tier-stability rate (V6, target > 80 %). Method fixed in §4.10; results
pending.

## 6.3 What the GPS actually shows

The GPS channel corroborates the parts of the supply chain it can see and falsifies two engine
assumptions it cannot support — which is exactly the behaviour a convergent design should surface.

*Geometry and moving speed pass.* GPS traces confirm that **183 of 186 planned alignments (median
`obs_frac` = 94.0 %) run over roads carrying active bus traffic** `[CL-35, F12]`, and the City-Core
congestion divisor (÷2.20) reproduces observed urban moving speed to **+1.4 % median bias** (modelled
17.95 vs observed 20.55 km/h) `[CL-33, F11]`. Where the model represents motion on mapped roads, it is
close.

*Dwell and run time fail against reality.* The engine's constant 1.0 min/km dwell is unsupported:
observed dwell is **1.76 min/km** (median dwell share 38 %), and an OLS fit
$\text{dwell}=17.67+0.247\,\ell$ ($R^2=0.03$) has a significant intercept and a non-significant
distance slope `[CL-34, F11]` — dwell is dominated by fixed terminal layover, not by distance.
Consequently modelled run time understates observed run time badly: **MAPE(OSRM vs in-motion) = 65.1 %,
MAPE(plan vs observed one-way) = 47.6 %, median ratio 0.51** `[CL-15, CL-16, CL-17, F3]`.

*The cap is the hidden governor.* The per-km sanity ceiling (Eq. 12) **binds on 169 of 186 routes
(90.9 %)** — 100 % of Regional, 97.9 % of Peri-Urban, 76.5 % of Urban `[CL-31, F10]` — while sitting
*below* real pace (observed median 4.62 min/km against the 4.0 Urban cap; exceeded on 83–100 % of
observed corridors) `[CL-32]`. An intended guardrail became the primary driver of cycle time and hence
fleet across nine-tenths of the network, and it truncates cycle time downward.

*Two coverage metrics, never conflated.* Physical alignment coverage (94 %) is not service validation:
only **66 of 186 routes (35.5 %) recur as observed services** in the GPS record `[CL-19, CL-35, F4,
F12]`, and the remaining 120 are `NO_APP_DATA` — an artefact of partial driver-app uptake, an
**observational lower bound on activity, not a dormancy rate**.

*The supply chain reproduces.* Against this, the fleet formula (Eqs. 13) reproduces the published
per-route fleet on all 156 non-backbone routes with **zero mismatches** `[CL-36]`: the arithmetic is
exact and auditable. The problem is not the formula but its inputs — the too-fast cap and the
distance-proportional dwell — which is why the fleet is reported as an interval anchored to the
GPS-measured 0.51 run-time ratio (V6, §4.10) rather than as a single number. Taken together, the
channels agree that the geometry and network structure are sound and disagree, in a localised and
explicable way, on time — precisely the finding a demand-free plan must expose rather than smooth over.

## 6.4 Demand-side corroboration as near-term work

The channels above validate the *supply* chain and the internal consistency of the index; they do not
yet close the demand-side loop. Two steps are earmarked as immediate next work and should be completed
before the framework is relied on for a live procurement decision: (i) the structured expert
elicitation (V3) to anchor the index weights against practitioner judgement, and (ii) a stratified
on-street boarding/enumeration survey on a sample of retained corridors, to test the index against
observed patronage rank and to give the POI opportunity layer a ground-truth reference beyond
OpenStreetMap mapping effort `[CL-20]`. The expert elicitation is scoped in §4.5; neither channel is
presumed here.
Until they are in hand, the plan's demand-side term rests on open proxies, and the honest ceiling on
the present claim remains **decision-robustness of the supply plan**, not demand validation — the
distinction §6.1 draws and §8 carries into the conclusions.
