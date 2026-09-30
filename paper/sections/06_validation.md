# 6. Validation

> **Section owners:** Prashant, Avny, Krishnan. **Target length:** ~900 words. **Status (2026-09-30):**
> V1, V2, V4, V5 and V6 executed; V3 is forward work. Every value cites `[CL-xx]`/`[F-x]`. **Standing constraints
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

**V1 — Spatial cross-validation** (executed, module `v01`). Does the population surface put people
where buildings are? Two footprint layers are tested against the pre-declared threshold Spearman
$\rho > 0.60$: volunteered OpenStreetMap buildings [@osm2024planet] and Microsoft's machine-detected
Global ML Building Footprints. One limit is stated first: WorldPop uses building footprints as a
covariate [@stevens2015disaggregating; @lloyd2017high], so agreement is partly expected by construction,
and V1 is a consistency check on the spatial pattern, not an independent count. On the near-complete
Microsoft layer (1.85 million footprints; 99.8 % of residents live in a 1 km cell that contains one), the
surface passes at every scale: **$\rho = 0.975$** for footprint area across the 186 route catchments
(0.940 for building count), and **0.907–0.950** on the 1 km grid `[CL-53]`. OSM, by contrast, maps only
12,343 buildings — any footprint in just 4–31 % of populated cells, depending on district — and
passes only at the route scale (0.657) `[CL-53]`. The OSM weakness is therefore a mapping gap, not a
population error.

**V2 — Benchmark consistency** (executed, module `v02`; circular, as disclosed in §6.1, and further
because the engine floors the backbone fleet at CHALO's deployment on 2 of 30 routes). CHALO runs 98 buses on the 30 backbone routes at about 855 bus-trips a
day (12-month mean); scaled to the plan's 15-minute headway that is **179–220 buses**, depending on
whether the operating day is taken as 13 or 16 hours. The plan's backbone fleet is 283, a ratio of
**1.29–1.58: V2 fails the pre-registered ±15 % band under every service-day assumption** `[CL-54]`, and the
rank correlation between CHALO's per-route deployment and the plan's per-route fleet is weak
($\rho = 0.22$, $p = 0.24$) `[CL-54]`. Even against the operator it was calibrated to, the plan provisions
more buses per route than frequency scaling alone explains; V2 localises the disagreement to the
backbone but cannot say whether it lies in the plan's cycle times or in CHALO's operation.

**V3 — Expert elicitation** (not conducted; §6.4). A Delphi/AHP panel would ground the index weights
(target Kendall's $W > 0.70$). Meanwhile the weights are derived three data-driven ways (§4.5).

**V4 — Supply-side GPS validation** (established, module `v04`). The empirical layer is **43,809 clean
service runs from ≈157 driver devices, February–June 2026** `[CL-18]`; its results are detailed in
§6.3. This is the study's one fully executed observational channel.

**V5 — Global sensitivity** (executed, `a08`/`a09`). Sobol' indices from 15,360 evaluations show two
different stories. Tier membership depends almost entirely on the population weight of the index
(total-order index 0.93); coverage on the walk-radius definition (0.97). The fleet as specified depends
almost only on the spare ratio (0.94), because the per-km cap discards the run-time parameters; with the
cap removed those same parameters swing the fleet by up to 956 buses `[CL-58]`.

**V6 — Decision robustness** (executed, `a09`). Tiers pass: agreement with the baseline partition is
97.8 % (90 % interval 94.6–100 %) against the 80 % target, and 179 of 186 routes keep their tier in more
than 80 % of 5,000 draws `[CL-57]`. The fleet does not have a single robust value: 989–1,058 as specified,
but **1,130–1,266 once urban and peri-urban run times follow observed pace**, an interval that excludes
the published 1,011 `[CL-56]`. The decision that survives is the hierarchy; the fleet survives only as a
range whose lower end the plan reports.

## 6.3 What the GPS actually shows

The GPS channel corroborates what it can see and falsifies two assumptions it cannot support.
*Geometry and moving speed pass:* 183 of 186 planned alignments run over roads carrying bus traffic
(median 94 % of length) `[CL-35, F12]`, and the City-Core congestion multiplier reproduces observed urban
moving speed to +1.4 % `[CL-33, F11]`. *Dwell and run time fail:* observed dwell is 1.76 min/km against the
engine's 1.0, and is fixed layover rather than distance-proportional ($R^2 = 0.03$) `[CL-34]`; modelled
one-way time is a median 0.51 of observed `[CL-17, F3]`, and the per-km cap that was meant as a guardrail
binds on 169 of 186 routes while sitting below real pace `[CL-31, CL-32, F10]` (§5.3).

*Two coverage metrics, never conflated.* Alignment coverage (94 %) is not service validation: **66 of
186 routes recur as observed services** `[CL-19, CL-35, F4, F12]`, a lower bound set by partial app
uptake, not a dormancy rate.

*The supply chain reproduces.* The cycle-time and fleet arithmetic reproduces the published plan on
all 186 routes `[CL-55]`. The problem is not the formula but its inputs — the too-fast cap and the
distance-proportional dwell — which is why V6 carries observed pace into the fleet. Taken together, the
channels agree that geometry, network structure and hierarchy are sound and disagree, in a localised and
explicable way, on time.

## 6.4 Demand-side corroboration as near-term work

The channels above validate the supply chain and the internal consistency of the index, not demand.
Two steps should precede any live procurement decision: (i) the expert elicitation (V3), which V5 shows
matters because the population weight governs the tiers; and (ii) a stratified on-street boarding count
on retained corridors, to test the index against observed patronage and the POI layer against more than
OpenStreetMap mapping effort `[CL-20]`. Neither was conducted. Until they are, the honest ceiling on the
claim is **decision-robustness of the supply plan**, not demand validation.
