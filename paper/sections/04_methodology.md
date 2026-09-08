# 4. Methodology

> **Section owner:** Prashant (sole). **Target length:** ~2,300 words. **Status:** complete draft.
> Every quantitative value in this section cites a Quantitative Claim Ledger identifier `[CL-xx]`
> (`paper/CLAIM_LEDGER.md`) or a Finding `[F-x]` (`paper/FINDINGS.md`); every equation and parameter
> is reproducible from the text alone and, end to end, via `python analysis/run_all.py --full`
> under `RANDOM_SEED = 20260823`. Where the published engine and the reproduction package diverge,
> the divergence is stated and the corrected definition is the one carried forward.

## 4.1 Framework overview

The framework rationalises an inherited stage-carriage permit network into a hierarchy of
frequency-specified, fleet-sized corridors **without any origin–destination, boarding, or
farebox demand feed**. It is deliberately supply-side: every quantity is derived from four open
inputs — a gridded residential population surface (WorldPop 2026, 100 m), OpenStreetMap points of
interest, road, and administrative geometry, a routing engine for road distance and free-flow time
(OSRM), and the digitised permit register — so that the entire pipeline is auditable and portable
to any city with the same open layers. Demand appears at exactly one, quarantined, point (Eq. 8),
and is never used to size the fleet.

The pipeline runs in four phases. **Phase 1 (diagnosis)** conditions the inputs and establishes
what the register actually is. **Phase 2 (accessibility)** delineates a network-based walk
catchment for each candidate route and scores it for resident population and weighted opportunity.
**Phase 3 (consolidation and hierarchy)** collapses duplicate permits, classifies survivors into a
service hierarchy by natural breaks, and assigns service standards. **Phase 4 (sizing and
assurance)** computes cycle time, fleet, and vehicle mix, then subjects the result to a battery of
quality-assurance gates and a sensitivity/uncertainty analysis. Figure 4 gives the flowchart and
Table 3 lists every parameter with its baseline and swept range.

Notation. The study region $\Omega$ is the union of the ten districts of Kashmir Division; the
population raster assigns residents $\rho_c$ to cell $c$ with centroid $x_c$, and
$\sum_{c\in\Omega}\rho_c = 6{,}584{,}763$ `[CL-11]`, the single denominator used for every coverage
share. $G=(V,E)$ is the walkable pedestrian graph extracted from OpenStreetMap, edges weighted by
metric length. A candidate route $r$ has a polyline geometry of length $\ell(r)$.

## 4.2 Data conditioning and network construction

The permit register (`existing-routes.csv`) contains **614 permit records** `[CL-01]`. A permit is
an administrative vehicle authorisation, **not** a route: undirected coordinate hashing of permit
endpoints at 11 m resolution collapses the 614 records to **157 distinct origin–destination
corridors** `[CL-02, F1]` (155 at 100 m, so this is not a rounding artefact), a mean of 3.91 permits
per corridor with a median of one, and a maximum of **42 permits on the single Hazratbal–Lal Ded
corridor** `[CL-03, CL-04]`. This change-of-unit is the dominant fact of the dataset and governs how
"reduction" may be reported (§5.1). The positional join from register row $i$ to engine route
`R{i+1:04d}` is verified at an **80.5 % origin-and-destination name-token match** `[CL-10]`; residual
mismatches are vernacular spelling variants (Rainawari/Rainawara).

The population surface is validated but not rescaled: its zonal sum over the district union is
6,584,763, versus a Census 2011 aggregate of 6,888,475 for the same boundary — ratio 0.956, an
implied −0.30 %/yr `[CL-11, CL-12, CL-13, F2]`. The surface is therefore structurally conservative,
so coverage *shares* are biased slightly upward and absolute *headcounts served* downward; both
directions are stated wherever a coverage figure appears, and the raster is left unscaled to
preserve comparability with the published plan.

The pedestrian graph carries **961,927 nodes / 973,569 edges / 23,323 km** within the padded bounding
box and **18,533 km inside the ten districts** `[CL-22]`. Its use is licensed by a strong district-scale
association between mapped road density and population density (Spearman $\rho = 0.915$, $p = 0.0002$)
`[CL-23, F6]`, which rules out gross peripheral under-mapping and removes the need for an ad-hoc
completeness correction. The opportunity layer is **2,431 points of interest across 63 categories**,
stratified into High (1,030), Medium (1,080), and Seasonal (321) importance tiers `[CL-20]`; its
concentration (65.3 % in Srinagar `[CL-21, F5]`) is the layer most exposed to volunteered-data bias
and is therefore carried explicitly into the weight sensitivity (§4.10).

A faithfulness diagnostic anchors the reproduction to the published plan. On the 142 of 186 active
routes whose declared `Route_KM` agrees with their drawn geometry to within 1 %, the independent
reimplementation reproduces the plan's Euclidean population served to a **median absolute error of
0.245 % with Pearson $r = 0.995$** `[CL-24, CL-25, F7]`. The remaining 44 routes carry externally
substituted road distances patched into the engine without redrawing geometry or recomputing
population; they are quarantined from the faithfulness baseline and named individually rather than
averaged away. One further correction is applied at ingest: an undocumented tourist multiplier that
the published engine folded *into* the population count on 8 routes (§4.4, Eq. 5) is stripped out of
the resident catchment, because a coverage numerator must be a count of residents `[CL-30, F9]`.

## 4.3 Route catchment delineation

Replacing the near-universal straight-line buffer with a **network walk catchment** is the single
methodological commitment the study treats as non-negotiable. Each route geometry is sampled into
virtual stops at 250 m spacing; each stop is snapped to its nearest graph node (of 22,360 virtual
stops, only 46 — 0.21 % — lie beyond the entire 400 m budget from the network; median snap offset
11.0 m `[CL-29]`). A multi-source Dijkstra from all snapped stop-nodes yields, for every node $v$,
the shortest walk distance $d(v)$ to the nearest stop. With a walk budget $W = 400$ m and an
off-network tolerance $\tau = 100$ m (one WorldPop cell — the finest the surface resolves), the
catchment is the union of residual discs

$$A_{\mathrm{net}}(r) \;=\; \bigcup_{\,v\in V:\; d(v)\le W}\; B\!\Big(x_v,\; \min\big(W - d(v),\; \tau\big)\Big), \tag{1}$$

where $B(x,\delta)$ is a geodesic disc of radius $\delta$ about $x$. Because the final residual leg
$W-d(v)$ is permitted to run straight off-graph, $A_{\mathrm{net}}$ is a formal **upper bound** on
the true walkshed, so any overstatement it reveals against a Euclidean buffer is a **lower bound on
the true bias** `[F8]`. The resident catchment population is the zonal sum

$$\Pi(r) \;=\; \sum_{c\,:\,x_c\in A_{\mathrm{net}}(r)} w\big(d_c\big)\,\rho_c, \tag{2}$$

with $w(\cdot)$ a non-increasing distance-decay kernel; the engine uses the hard-cut special case
$w\equiv 1$ inside the budget, evaluated with `rasterstats` zonal statistics in WGS84 honouring the
raster's own nodata. Catchments overlap, so per-route figures may not be summed. A cell $c$ covered
by $n_c$ routes is apportioned by a partition of unity,

$$\pi_c(r) \;=\; \frac{\rho_c}{n_c}\,\mathbf{1}\!\big[x_c\in A_{\mathrm{net}}(r)\big], \qquad \sum_r \pi_c(r)=\rho_c, \tag{3}$$

so that allocated per-route populations sum exactly to the **deduplicated network union** and never
to the inflated raw sum. Applied across all 186 routes, the network catchment reduces measured
population served by a **median of 37.4 % per route** (IQR 30.5–41.7 %, max 56.8 %; 184 of 186 routes
overstated by more than 25 %) `[CL-26]`; on the deduplicated union the overstatement is **31.9 %**
(2,339,394 → 1,592,847 residents) `[CL-27]`, which lowers headline coverage from **35.5 % to 24.2 %**
of the division `[CL-28]`. The finding is invariant to the one free parameter: $\tau = 50/100/150$ m
gives median overstatements of 52.8 % / 37.4 % / 29.2 % `[CL-29]`, same-signed and large across the
whole defensible range.

## 4.4 Weighted opportunity accessibility

Opportunity is the weighted count of points of interest inside the same catchment,

$$O(r) \;=\; \sum_{q\,\in\,Q\,\cap\,A_{\mathrm{net}}(r)} \alpha_{t(q)}, \tag{4}$$

where $t(q)\in\{\text{High},\text{Medium},\text{Seasonal}\}$ and the baseline tier weights are
$\alpha_{\text{High}}=1.00$ (reference), $\alpha_{\text{Medium}}=0.40$, $\alpha_{\text{Seasonal}}=0.60$
(Table 3; all swept in §4.10). Because the composite is min–max normalised (Eq. 6), only relative
weights matter. Visitor demand — which a residential raster cannot see — is represented by a
**seasonality multiplier** $\mu = 1.30$ on the 8 tourist-flagged routes $T$,

$$O^{\ast}(r) \;=\; \begin{cases}\mu\,O(r), & r\in T,\\[2pt] O(r), & r\notin T,\end{cases}\qquad \mu=1.30. \tag{5}$$

Critically, $\mu$ acts on the **opportunity/demand channel only**. The published engine erroneously
applied it inside the population count (Eq. 2), injecting **285,914 synthetic persons** into the
coverage numerator on those routes `[CL-30, F9]`; the reproduction package keeps residents (Eq. 2)
and any demand adjustment (Eq. 5) in separate columns, so a coverage share is always a share of
residents.

## 4.5 Composite demand index

Population and opportunity are converted to per-kilometre densities, min–max normalised across the
active set,

$$\widehat{z}(r) \;=\; \frac{z(r)-\min_{r'}z(r')}{\max_{r'}z(r')-\min_{r'}z(r')}, \tag{6}$$

(population first capped at its own 95th percentile so a few dense urban catchments cannot saturate
the scale), and combined into the length-normalised **Composite Demand Index**

$$\mathrm{CDI}(r) \;=\; \beta\,\widehat{\Big(\tfrac{\Pi(r)}{\ell(r)}\Big)} \;+\; (1-\beta)\,\widehat{\Big(\tfrac{O^{\ast}(r)}{\ell(r)}\Big)}, \qquad \beta = 0.50. \tag{7}$$

The two channels are checked for collinearity: if $\rho(\Pi, O^{\ast}) > 0.85$ the composite adds
little beyond the first principal component and a PCA reduction is substituted. The weight vector is derived three
independent, data-driven ways — **equal weights, Shannon-entropy weights, and PCA first-component
weights** — and the tier assignment (§4.7) is shown stable across all three, so the hierarchy does not
depend on any single weighting choice. An Analytic Hierarchy Process / Delphi elicitation to anchor
these weights against practitioner judgement is earmarked as near-term validation work (§6.4); the
module records `ahp_weights_derived = false` until it is in hand, and no expert weights are fabricated
in the interim.

Demand enters the pipeline once, and under quarantine. A plausibility ridership is defined **for
benchmarking only**,

$$\widetilde{D}(r) \;=\; \kappa \sum_{c\in A_{\mathrm{net}}(r)} \rho_c\, m(c)\, \sigma(r), \qquad \kappa = 0.18, \tag{8}$$

where $m(c)$ is a mode-share prior and $\sigma(r)$ a corridor-share apportionment, and $\kappa$ is the
empirical capture scale anchored to the one published CHALO ridership aggregate. **Equation 8 never
sizes the fleet and is never reported as a forecast**; it exists solely to test order-of-magnitude
plausibility (§6, channel V2, with the circularity disclosed). It is quarantined precisely because
the CDI (Eq. 7) has no established structural relationship to realised travel demand — the claim the
whole design is built to avoid needing.

## 4.6 Permit consolidation

Consolidation operates on the undirected corridor key (rounded endpoints), not on route names. The
spatial overlap of two catchments is the overlap coefficient

$$\phi(r_i,r_j) \;=\; \frac{\big|A_{\mathrm{net}}(r_i)\cap A_{\mathrm{net}}(r_j)\big|}{\min\big(|A_{\mathrm{net}}(r_i)|,\,|A_{\mathrm{net}}(r_j)|\big)}, \tag{9}$$

and two routes are consolidation candidates when $\phi \ge \theta$ with $\theta = 0.65$ (swept
0.50–0.90 in §4.10). Algorithm 1 applies this in two stages — first collapsing duplicate permits on
an identical corridor (the change-of-unit), then contracting genuinely overlapping distinct corridors
— while protecting the synthetic e-bus backbone from being merged away.

> **Algorithm 1 — Permit consolidation**
> **Input:** candidate routes $R$ (644 rows = 614 permits + 30 e-bus `[CL-05]`); threshold $\theta$; undirected 4-dp corridor key $\kappa(\cdot)$.
> 1. Group $R$ by $\kappa$. Within each group, collapse duplicate permits to one representative (longest self-consistent geometry / most complete via-chain). *(change of unit — F1)*
> 2. Over the distinct-corridor representatives, build an overlap graph with an edge $(i,j)$ iff $\phi(i,j)\ge\theta$ **and** the two share a service tier. Exclude e-bus backbone routes from contraction.
> 3. Contract each connected component to one service, retaining the highest-CDI alignment.
> 4. Label survivors `UPGRADED_TO_TRUNK` / `RETAINED_AS_FEEDER`; label absorbed rows `CONSOLIDATED`.
> **Output:** **186 active routes** (32 trunk + 154 feeder), 458 consolidated `[CL-06]`.

Reported honestly, the plan **retains 156 of 157 physical corridors (99.4 %)** `[CL-08]`: of the
apparent 71.1 % row reduction, **71.0 percentage points are the change of unit** and only **0.16 pp
is genuine spatial consolidation** (one corridor, Parimpora–Pantha Chowk) `[CL-07]`. The cost of
corridor-level collapse is counted, not asserted away: **32 alternative via-routings across 20
corridors are suppressed**, 38 corridors lose vehicle-class differentiation and 34 lose service-type
differentiation `[CL-09]`.

## 4.7 Hierarchy and service standards

Survivors are ranked by CDI and partitioned into service tiers by **Jenks natural breaks**, choosing
the class count by the goodness-of-variance-fit elbow

$$\mathrm{GVF}(k) \;=\; 1 - \frac{\sum_{j=1}^{k}\sum_{i\in C_j}\big(y_i-\bar y_{C_j}\big)^2}{\sum_i\big(y_i-\bar y\big)^2}, \qquad k = 2,\dots,7, \tag{10}$$

with the elbow expected at $k=3$; the partition is cross-checked against equal-interval, quantile, and
$k$-means classifications using Cohen's $\kappa$ (module `a04`, method fixed here, result in §5).
Service standards are then assigned by tier: policy headways of **15 / 20 / 35 min** for Urban,
Peri-Urban, and the e-bus backbone, and **demand-responsive rural headways bucketed at 35 / 40 / 45 /
50 min under a hard 50-minute maximum wait**, evaluated across peak, off-peak, and evening bands.

## 4.8 Cycle time and fleet sizing

One-way running time combines a congestion-scaled free-flow drive with dwell and fixed penalties,

$$t_{\mathrm{run}}(r) \;=\; \chi(r)\,t_{\mathrm{OSRM}}(r) \;+\; \delta\,\frac{\ell(r)}{\Delta_{\mathrm{stop}}} \;+\; J(r), \tag{11}$$

where $\chi$ is the congestion multiplier ($\chi_{\mathrm{City\,Core}} = 2.20$, which reproduces the
observed urban moving speed to +1.4 % `[CL-33, F11]`), $\delta/\Delta_{\mathrm{stop}}$ is a dwell rate
of 1.0 min/km ($\delta = 0.50$ min per stop at $\Delta_{\mathrm{stop}} = 500$ m), and $J(r)$ collects
fixed junction and bridge penalties (the Jhelum crossings add 8.0 min). Cycle time applies a per-class
per-kilometre sanity cap,

$$t_{\mathrm{cyc}}(r) \;=\; \min\!\Big(\,2\,t_{\mathrm{run}}(r) + t_{\mathrm{lay}},\;\; 2\,\ell(r)\,\omega_{\mathrm{class}(r)}\Big), \tag{12}$$

with $\omega = 4.0 / 2.5 / 1.5$ min/km for Urban / Peri-Urban / Regional and $t_{\mathrm{lay}}$ terminal
recovery. This intended ceiling is in fact the **binding constraint on 169 of 186 routes (90.9 %)**
`[CL-31, F10]`, and it sits *below* real pace (observed median 4.62 min/km vs the 4.0 Urban cap
`[CL-32]`) — a diagnosis carried into §5.3 and §6.3, where it becomes the argument for an interval
fleet. Fleet per route is

$$N_{\mathrm{op}}(r) = \max\!\Big(1,\big\lceil t_{\mathrm{cyc}}(r)/\max(1,h(r))\big\rceil\Big), \qquad
N(r) = \max\!\Big(\big\lceil \sigma\,N_{\mathrm{op}}(r)\big\rceil,\; N^{\min}_{\mathrm{class}(r)}\Big), \tag{13}$$

with headway $h(r)$ (§4.7), spare ratio $\sigma = 1.15$, and floors $N^{\min} = 2$ (Urban/Peri-Urban)
or $1$ (Regional). Summed over non-backbone routes plus the empirically fixed backbone,

$$N_{\mathrm{total}} \;=\; \sum_{r\notin\mathrm{SSCL}} N(r) \;+\; N^{\mathrm{emp}}_{\mathrm{SSCL}} \;=\; 728 + 283 \;=\; 1{,}011, \tag{14a}$$

a **+68.5 % expansion over the ~600-vehicle operating baseline**, or 43 buses per 100,000 residents
served — within the MoHUA 40–60 benchmark `[CL-36]`. An independent self-test reproduces the
published per-route fleet on all 156 non-backbone routes with **zero mismatches** `[CL-36]`. Fleet is
finally split into High/Medium/Low-priority vehicles subject to a trunk share cap,

$$N_{\mathrm{HPV}}(r) \le \big\lfloor 0.50\,N(r)\big\rfloor \text{ on trunks}, \qquad N_{\mathrm{HPV}}+N_{\mathrm{MPV}}+N_{\mathrm{LPV}} = N(r), \tag{14b}$$

giving network totals of **187 HPV / 754 MPV / 70 LPV** `[CL-36]`; the 0.50 cap ensures neither vehicle
class forms a majority on any trunk.

## 4.9 Quality-assurance gates

Ten gates (Table 3) block export on failure and are enforced by an independent checker suite (53
tests, Checkers A–F): (G1) all active routes inside the ten-district boundary; (G2) the coverage
denominator equals 6,584,762; (G3) zero uncontextualised legacy metrics (none of 342, 207, 39 %,
95.7 %, 1,009, or the Srinagar-metropolitan framing); (G4) fleet-formula reproduction invariance (0
mismatches, Eq. 13); (G5) strict permit(614)/corridor(157)/active(186) accounting; (G6) geocode
non-collapse (no route endpoint on a district centroid); (G7) undirected duplicate-corridor keying;
(G8) route-code uniqueness; (G9) faithfulness reproduction within 1 % on self-consistent routes
(Eq. 2); and (G10) per-row $N_{\mathrm{HPV}}+N_{\mathrm{MPV}}+N_{\mathrm{LPV}} = N(r)$. All are
reproducible via `run_all.py --full` under the fixed seed.

## 4.10 Sensitivity and uncertainty

Robustness is established at two levels. A **one-at-a-time sweep** perturbs each of eleven
pre-declared parameters (Table 3: the 400 m catchment, 250 m stop spacing, 500 m dwell spacing, the
0.50 CDI population weight, the two POI tier weights, the 1.30 tourist multiplier, the 0.65 overlap
threshold, the 2.20 congestion divisor, the 0.50 min stop penalty, and the 1.15 spare ratio) across
its range while holding the rest at baseline. A **Monte Carlo** of 5,000 draws then samples all
eleven jointly from the declared marginal priors, and **Sobol' first- and total-order indices** (with
bootstrap confidence intervals) decompose output variance to attribute it to specific parameters. The
decisive prior is empirical: the GPS-measured ratio of modelled to observed run time (median 0.51
`[CL-17, F3]`) is carried as a run-time-inflation prior, so the deliverable is a **fleet 90 %
confidence interval and a tier-stability rate (target > 80 %)** rather than a point estimate. The
language throughout is *decision-robust*, never "validated against demand": the uncertainty analysis
establishes that the tier and fleet decisions survive plausible parameter and speed variation, which
is the strongest claim a demand-free method can honestly make.
