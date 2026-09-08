# Gap 3 — Methodological Risks a Hostile-but-Fair Reviewer Will Attack

**Severity: HIGH. These are not bugs — they are the substantive weaknesses of the study design.**
None of these is fatal, but each must be pre-empted in the manuscript (Limitations + Discussion) or a
reviewer will raise it and the response will look defensive. Ranked by how damaging an unaddressed
version would be.

---

## R1 — The demand-index-to-demand gap (the existential critique)

**The attack.** "You rank and tier routes with a *Composite Demand Index* built from population +
POIs, then size fleet from it. You never show the index correlates with actual travel demand. So the
whole prioritisation could be wrong and you would never know."

**How exposed we are.** Very. This is the paper's central conceptual bet. We have **no demand-side
ground truth at all** — V4 (GPS) is explicitly supply-side, V2 (CHALO) is circular, V3 (expert panel)
is not collected. The honest defence is already in the design: we never claim the index predicts
demand; we claim *decision-robustness of the supply plan*. But the paper must state, in the
Limitations, in one blunt sentence, that **the index is a normative accessibility-opportunity
prioritiser, not a validated demand model**, and that closing this loop (boarding survey, §6.4) is the
single most important piece of future work. Do not let a reviewer be the first to say it.

## R2 — n = 5 matched corridors for the headline runtime ratio

**The attack.** "Your headline 'plan runtime is 0.51× reality' — the finding that motivates the entire
interval-fleet argument — rests on **five** matched corridors (`CL-16`, `CL-17`). Five. That is an
anecdote, not a validation."

**How exposed we are.** High, and it is the most quotable weakness. Mitigations that are true and must
be stated: (a) the *supporting* pace/cap findings (`CL-31`, `CL-32`) rest on 14–18 corridors and 43,809
runs, not 5; (b) the 0.51 ratio is corroborated mechanistically by the cap-binding rate (90.9%) and the
dwell-model failure, so it is not a lone number. But we must **report the 5 explicitly, give the CI, and
frame the fleet as an interval precisely because n is small** — turning the weakness into the reason for
the interval rather than hiding it. Never state 0.51 without "on 5 matched corridors" in the same
sentence.

## R3 — Tourism multiplier provenance (1.30×)

**The attack.** "Where does 1.30 come from? You inject 285,914 synthetic persons (`CL-30`) into a
headcount with a multiplier that has no citation."

**How exposed we are.** Moderate–high, and partly self-inflicted — `CL-30` itself documents this as a
*distortion* (a demand multiplier wrongly placed in a physical headcount). The paper's position must be
consistent: the 1.30× is an **engine legacy artefact we diagnose and quarantine**, not a method we
endorse. Coverage numbers in the paper must be the *resident* headcounts, with the tourist-boosted
figure shown only as the thing being corrected. If any headline still carries the multiplier, it is a
defect. Confirm every coverage number in §5/Abstract traces to a resident (non-boosted) `CL`.

## R4 — τ = 100 m off-network tolerance choice

**The attack.** "Your 37.4% overstatement depends on τ. Choose τ differently and the headline moves."

**How exposed we are.** Low — this one is already well-defended. `CL-29` sweeps τ = 50/100/150 m
(52.8%/37.4%/29.2%) and the qualitative finding (large overstatement) survives across the range. Keep
the sweep in the paper and state that 37.4% is a **lower bound** because the network catchment is an
upper bound on the true walkshed. This is a strength, not a risk, as long as the sweep stays visible.

## R5 — CHALO circularity (V2)

**The attack.** "You calibrate the capture scale κ = 0.18 from CHALO and then 'validate' against CHALO.
Circular."

**How exposed we are.** Low, *if* disclosed first — which §6.1 now does. The rule: V2 is a
**consistency check, not independent validation**, and the circularity is stated before the result, not
buried. Do not upgrade V2's language to "validation" anywhere. This is handled; keep it handled.

## R6 — Fleet self-test proves arithmetic, not correctness

**The attack.** "Your '0 mismatches' fleet self-test (`CL-36`) only proves the formula reproduces its
own outputs. It is a tautology, not a validation."

**How exposed we are.** Moderate. The claim is true but easy to over-read. The paper must frame the
self-test as an **auditability/reproducibility guarantee** (the arithmetic is exact and re-runnable),
explicitly *not* as evidence the inputs are right — indeed §6.3 already says the problem is the inputs
(cap, dwell), not the formula. Make sure that framing is unambiguous wherever `CL-36` appears.

## R7 — WorldPop below Census (denominator is conservative)

**The attack.** "Your population raster (6.58M) is *below* the 2011 Census (6.89M) for the same
boundary. Your coverage denominator is wrong."

**How exposed we are.** Low. `CL-13` already turns this into a disclosed, quantified caveat: the raster
is structurally conservative, so **coverage percentages are biased upward and absolute headcounts
served biased downward** — i.e. our coverage claims are, if anything, generous to ourselves and the
headcounts conservative. State the direction of bias explicitly so the reviewer cannot imply we hid it.

## R8 — GPS spatial coverage is Srinagar-centric

**The attack.** "All 18 observed corridors are in greater Srinagar. Your congestion/pace findings do
not generalise to the rural network you spend half the fleet on."

**How exposed we are.** Moderate. `CL-33` already flags that Peri-Urban/Rural congestion multipliers are
**classification counterfactuals** (not observed). The paper must not claim the GPS validates rural
cycle times — it validates the urban core and flags the rural extrapolation as unvalidated. This
intersects R2. State the geographic limit of the GPS layer plainly in §6.

---

## Summary posture for the Discussion/Limitations section

A single honest paragraph should concede, in order: (1) no demand-side ground truth — index is
normative, not predictive [R1]; (2) the runtime ratio rests on 5 corridors, which is *why* fleet is an
interval [R2]; (3) the tourist multiplier is a diagnosed artefact, not an endorsed method [R3]; (4) the
GPS layer is supply-side and Srinagar-centric [R8]. Every one of these is already true in the analysis —
the risk is only that the manuscript under-states them and lets a reviewer land the punch first.
