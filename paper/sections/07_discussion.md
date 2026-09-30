# 7. Discussion and policy implications

> **Provenance and editorial status.** The attachment assigns §7 to **Ankit, Avny and Misti** with a
> 1,200-word budget, an eight-subsection skeleton (§7.1–§7.8), detailed hints and a Table 8 specification. It
> also contains one block of **drafted co-author prose**, headed *"Policy Contribution"*, which is
> **reproduced verbatim below and has not been edited, shortened or absorbed into my text.** Everything else
> here is a draft written for co-author review.
>
> The attachment's own note is worth repeating: *"Transport Policy weights this more heavily than any section
> except the abstract."* Body length below: ~1,320 words excluding flags and excluding the preserved
> co-author block.

---

## 7.1 What the results mean for planning under data scarcity

**The demand dependency is severable.** The conventional planning chain consumes demand data at four points
(§1.3), but only one of them is load-bearing. Cycle time follows from distance, speed and dwell; fleet follows
from cycle time and headway; coverage follows from geometry and population. Demand enters only at the
frequency rule. Substituting a policy-anchored headway band for that rule leaves the rest of the chain intact
and computable from open data. This is a structural observation about the method, not a claim about Kashmir,
and it is the finding most likely to transfer.

**Proxy error is tolerable because the decision is ordinal.** The composite index is not asked to predict how
many people will board; it is asked to sort corridors into three service tiers. A proxy can be badly wrong in
level and still be right in order. This is why the paper reports tier stability under parameter perturbation
rather than index accuracy against ridership — and why the honest ceiling on the claim is decision
robustness, not demand validation.

**Open data has crossed the threshold from assessment to planning.** Gridded population, an open street
network and an open routing engine are now jointly sufficient to produce a service plan with frequencies, a
vehicle mix and a fleet count — not merely a diagnostic map. The constraint that has moved is data
availability, not method.

**Data scarcity is a design constraint, not an excuse.** The counterfactual for a data-poor authority is not a
better plan produced later from better data. It is **no plan**, indefinitely, while permits continue to be
granted one at a time and in perpetuity. A defensible supply-side plan that is revised as data arrive
dominates that counterfactual.

## 7.2 Instruments for the State Transport Authority

The results convert into four instruments rather than recommendations.

**Convert permits into route-bundle contracts.** The binding pathology identified in §3.5 is that a permit
attaches to a vehicle and an area, in perpetuity, with no service obligation. Bundling permits by corridor and
contracting for a *route with a frequency* is the minimum structural change that makes any plan enforceable.

**Write the headway ceiling into permit conditions.** The maximum-wait standard used in this plan — 15/20/35
minutes in urban and peri-urban tiers, and a hard 50-minute ceiling on rural lifeline services — is a
publishable, auditable service standard. It is enforceable against a contracted bundle in a way it can never
be against an area permit.

**Publish the hierarchy as a statutory service standard**, so that tier assignment is a public commitment
rather than an internal planning artefact, and so that changes to it require justification.

**Adopt gross-cost contracting with explicit operator absorption.** The plan requires more buses than are
currently operated, which means incumbent operators are absorbed rather than displaced in aggregate — but
consolidation still redistributes who runs what.

> **[FLAG 7-A — the political-feasibility paragraph is missing and its absence is a predictable objection.]**
> The attachment is explicit: *"Add the political feasibility of merging 135 permits — 135 contested
> livelihoods — and cite the international evidence on resistance to network redesign. Its absence is a
> predictable objection here."* In the current framing the corresponding figure is **458 permit rows merged**
> (CL-05/CL-06), which makes the point larger, not smaller. This draft does **not** include that paragraph,
> because doing it properly requires citing the international redesign-resistance literature (Houston,
> Auckland, Barcelona and Santiago's Transantiago are the usual reference cases) and `paper/references.bib`
> is still being verified. **This is a required addition before submission, not an optional one.** The
> honest sentence to build it around: consolidation is politically hard precisely because its costs are
> concentrated on identifiable incumbents while its benefits are diffuse.

## 7.3 Urban local bodies, land use and metropolitan governance

The plan crosses municipal boundaries, and no single agency holds the mandate for the network it describes —
the statutory position set out in the "Policy Failure" block. The institutional implication is a **unified
metropolitan transport authority function**: not necessarily a new agency, but a named body with the power to
set network-level service standards across RTA, STA, Smart City and corporation services. Absent that
function, this plan can be adopted in parts by each operator and coordinated by none, which reproduces the
problem it diagnoses.

## 7.4 Smart City and electric-bus integration

The electric-bus backbone is the one part of the network that already has a designed service level (a
15-minute headway), published ridership aggregates, and electronic ticketing. It is therefore both the
integration opportunity and a methodological hazard: the same ridership series calibrates the plausibility
term in §4 and is offered as benchmark channel V2, which is why §6 discloses that circularity rather than
resting validation on it. For policy, the practical point is that the e-bus corridors are the natural first
site for the data-maturity transition described next — they are where fare-card data already exists.

## 7.5 A low-data planning framework and the data-maturity ladder

The framework defines four levels of data maturity, each of which unlocks a specific methodological upgrade:

- **Level 0 — open data only.** Gridded population, OSM network, open POIs, open routing. This is the whole
  framework as presented. It yields an ordinal service hierarchy, a headway plan and a fleet estimate.
- **Level 1 — adds ward-level census population and a road-width/bridge-capacity register.** Replaces modelled
  population with enumerated population, and converts vehicle-size allocation from a flat policy split into a
  physically constrained one.
- **Level 2 — adds operator GPS traces.** Replaces modelled runtime with observed runtime. The present study
  reaches this level for a subset of corridors and the effect is large (F3, F10).
- **Level 3 — adds fare-card or automatic-passenger-count ridership.** Permits genuine demand validation and
  closes the loop the paper deliberately leaves open.

The Sobol' decomposition (§5.7, §6.2) now ranks the rungs by what each would actually resolve
`[CL-58]`, and the order is not the order of methodological dependency above:

1. **For the fleet, the cheapest datum is the operator's own vehicle-availability record.** The spare
   ratio carries 55 % of fleet variance at observed pace (94 % as specified). It is not a demand datum at
   all and sits on no rung; a year of maintenance logs would pin it.
2. **Next, peri-urban GPS (Level 2).** Observed peri-urban and urban pace together carry 45 % of fleet
   variance, peri-urban alone 32 % — and the present GPS has only nine peri-urban corridors. Extending
   instrumentation there buys more fleet certainty than any demand survey.
3. **For the hierarchy, demand-side weighting (Level 3, or the V3 panel).** The population weight in the
   index carries 93 % of the variance in tier agreement; only observed ridership or an expert elicitation
   can fix it. Tiers are already 97.8 % stable, so this rung sharpens a decision that is largely made.
4. **Coverage is a definition, not an uncertainty.** 97 % of its variance is the walk-radius choice
   (20.3 % of residents at 300 m, 34.5 % at 800 m); no dataset resolves it — a standard does.

Ward-level census population (Level 1) does not appear in the ranking because population uncertainty was
not sampled; its value is therefore unmeasured here, not shown to be small.

> **[FLAG 7-B — resolved 2026-09-30 (Decision 6).]** Ranking from the total-order Sobol' indices of a09.

## 7.6 Transferability: which cities, under what conditions

The framework's preconditions are modest and enumerable: an inherited route or permit register in digital or
digitisable form; OSM road-network completeness sufficient for pedestrian routing (tested here at ρ = 0.915
against population density, F6); a gridded population product; and an authority willing to set service
standards by policy rather than derive them from demand. Where those four hold, the method applies.

On scale: India alone has **over 400 Class-I cities with no organised municipal bus network** (§1.1), and the
condition that defines them — permit-based provision without demand data — is the condition this framework
targets. The wider Global South set of paratransit and minibus networks extends that population substantially.

> **[FLAG 7-C — transferability claims must not outrun the evidence.]** The method has been applied **once**,
> to one region. "Applies to 400+ cities" is a statement about *preconditions being met*, not about
> demonstrated external validity, and the sentence must be built so that a reviewer cannot read it the other
> way. §8's future-work item on transferring the protocol to three to five further cities is what would
> convert this from a scope claim into a tested one.

## 7.7 Implementation sequencing under budget constraint

The question an authority actually asks is not "what is the optimal network?" but "if only part of the fleet
is funded, what do I buy first?" The framework answers it directly: rank routes by **accessibility gain per
additional bus**, and fund down that ranking until the budget is exhausted.

Run that way (`a15`, Table 8b), the answer is stark. **Thirty per cent of the fleet — 303 buses, spent on
63 routes — reaches 22.4 % of the division's residents, 92 % of the coverage the full 1,011-bus plan
achieves** `[CL-61]`. Half of the plan's reach costs 54 buses; 90 % costs 264. The first routes bought are
long radial lifelines (Srinagar–Aboora, Shopian–Srinagar, Bandipora–Baramulla), because a few buses on a
long route put many residents inside a walkshed. The remaining 70 % of the fleet therefore buys
*frequency* on corridors already reached, not *reach*. That split is the choice an authority should make
explicitly: a coverage-first tranche that is cheap and nearly complete, followed by frequency tranches whose
value depends on the ridership response §5.11 shows the plan is betting on.

> **[FLAG 7-D — resolved 2026-09-30.]** The ranking is greedy marginal coverage per bus at published
> headways — the standard approximation for budgeted maximum coverage, reported as a ranking, not an
> optimum. It measures reach only; it says nothing about how many of the newly reached residents would ride.

## 7.8 Limitations

Stated flatly, because softening them invites reviewers to sharpen them.

1. **The index is a proxy, not observed demand**, and is validated for ordinal decisions only. No claim is
   made that it predicts ridership.
2. **Population is modelled and 2011-anchored.** WorldPop 2026 sits 4.4% below the 2011 Census total for the
   same ten districts (F2), an implausible implied growth rate that is reported rather than corrected.
3. **Travel times are routing-engine estimates**, and they understate observed in-motion times substantially
   (MAPE 65.1%; median planned-to-observed 0.51 — F3). Where GPS permitted re-anchoring, it was applied; most
   corridors have no GPS.
4. **Seasonal operability, bridge load limits and road width are not hard constraints in the model.** They
   are acknowledged in the narrative and absent from the optimisation.
5. **Tourist demand is inferred from destinations, not arrivals**, via a 1.3× multiplier on eight routes that
   contributes 285,914 synthetic headcount (F9). It is parameterised and sensitivity-tested, not observed.
6. **Behavioural response is out of scope.** No mode-shift or induced-demand elasticity is modelled. One
   consequence helps the argument rather than harming it: if the periphery is currently under-served, then
   *observed* travel patterns understate its potential, so a supply-side method that plans to population
   rather than to revealed trips is less biased against the periphery than a demand-driven one would be.
7. **The political feasibility of consolidating permits is not modelled** (see FLAG 7-A).
8. **Two external validation channels are weak.** The operator benchmark fails its band and is not
   independent (V2), and the building-footprint check is limited by OSM completeness (V1). Rural run time
   is unobserved, so the rural fleet in every scenario is as modelled.

---

## Co-author block — "Policy Contribution"

> **[PROVENANCE]** The following is **co-author prose, transcribed verbatim** from the attachment. It is
> reproduced unchanged. It overlaps in purpose with §7.1–§7.2 above; the two have deliberately **not** been
> merged, so that the co-authors can decide what to keep rather than discover their text rewritten. See
> FLAG 7-E.

The main contribution of this study is to look at how Srinagar can move from individual, area-based permit
decisions towards planning the bus network as a whole. At present, detailed passenger-demand information is
not readily available for conventional bus services. The study therefore explores whether available
information on population, important activity locations, the road network and existing bus operations can be
used to make better decisions about routes and fleet requirements. The purpose is not to suggest that open or
proxy data can replace actual passenger data. Rather, it can provide a useful starting point where detailed
data are not available. Such an approach can help identify areas where services overlap, areas that have
limited connectivity and corridors where additional or better-distributed services may be required.

The approach is also relevant because public transport within the Srinagar Municipal Area is not confined to
one permitting authority. Along with city services permitted by the RTA, buses originating from other
districts may enter the Municipal Area under permits issued by the STA. A network-level assessment can
therefore look at the transport services available to passengers across the Municipal Area, without
necessarily requiring any change in the existing statutory powers of the RTA or STA.

Another practical contribution is that route rationalisation can be linked to actual service requirements.
Instead of looking only at the number of routes, the study can help in considering the number of buses
required, the frequency at which they should operate and the maximum time passengers should reasonably have
to wait. This can provide a more useful basis for future decisions relating to route permits, service planning
and, where appropriate, arrangements with bus operators.

The approach should also not be seen as a one-time exercise. As better information becomes available — such as
passenger counts, boarding and alighting data, GPS records, ticketing information and Origin-Destination
patterns — the proposed network can be reviewed and improved. In this way, the present exercise can serve as a
starting point for a more evidence-based public transport planning system.

Finally, the study can help the Transport Department identify what information needs to be collected in the
future and where it would be most useful. Instead of waiting for perfect data before undertaking any route
planning, the authority can begin with the information that is available, identify its limitations and
progressively improve the system as better data are collected. The broader policy contribution, therefore, is
to provide a practical and adaptable way of moving from permit-by-permit decision-making towards integrated
bus-network planning, while recognising the realities and limitations of the data currently available in
Srinagar.

> **[FLAG 7-E — two reconciliations for the co-authors, neither applied.]**
> **(i) Overlap.** This block and §7.1–§7.2 above make substantially the same argument. Merging them is
> straightforward but is an authorial decision, not an editorial one. My recommendation: keep this block's
> voice — it is measured, non-overclaiming and reads as though written by someone who will have to defend it
> to a transport department, which is exactly the right register for *Transport Policy* — and fold the
> specific instruments from §7.2 into it.
> **(ii) Scope.** The block says "Srinagar" and "Srinagar Municipal Area" throughout, while the plan it
> describes covers ten districts. The same reconciliation proposed at FLAG PF-b applies: if the intent is
> that the *institutional* argument is Srinagar-specific while the *plan* is division-wide, one sentence
> resolves it. **No wording has been changed.**

---

## Table call for §7

- **Table 8 — Policy instruments.** Columns per the attachment: instrument · responsible agency · time frame
  · indicator · data required, with transferability conditions beneath. **Status: not built.** The instrument
  rows can be drafted today from §7.2 and §7.5; the "data required" column should be keyed to the
  data-maturity ladder levels, and — once `a09` runs — ordered by the variance reduction each dataset
  delivers (FLAG 7-B).
