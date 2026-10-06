# 4. Methodology

> **Section owner:** Prashant. **Status:** rewritten 2026-10-06 on the corrected analysis (Phase 1). Length
> follows Prof. Kathuria's brief (about 2,300 words) until the limit is confirmed. Bracketed tags such as
> `[CL-31]` point to the claim ledger and are stripped from the submitted version. Boxes marked
> **TO CONFIRM** are open points, not text for the journal.

## 4.1 Framework overview

The framework turns an inherited stage-carriage permit register into a tiered network with a headway and a
fleet for every route, without using an origin–destination matrix, boarding counts or fare data for the
routes being planned. Its main inputs are open: a gridded population surface (WorldPop, 100 m, release
R2025A, constrained) [@tatem2017worldpop; @stevens2015disaggregating], OpenStreetMap roads, footpaths,
points of interest and district boundaries [@osm2024planet], and a routing engine for road distance and
free-flow time [@luxen2011realtime]. Two inputs are not open data: the permit register, obtained from the
transport regulator, and ridership aggregates for the one operator that has electronic ticketing, the
Srinagar Smart City e-bus service. Section 4.5 lists every point at which the second of these enters.

The pipeline has four phases (Figure 4): diagnosis of the inputs; accessibility, in which each route receives
a walking catchment scored for residents and opportunities; consolidation and hierarchy; and sizing, in
which cycle time, fleet and vehicle mix are computed and their uncertainty is quantified. Table 3 lists every
parameter with its value, tested range and source.

The study region $\Omega$ is the union of the ten districts of Kashmir Division. The population raster
assigns $\rho_c$ residents to cell $c$ with centroid $x_c$, and $\sum_{c \in \Omega} \rho_c = 6{,}584{,}762$
`[CL-11]`, the denominator of every coverage share. $G = (V, E)$ is the pedestrian graph extracted from
OpenStreetMap with edges weighted by length in metres. A route $r$ has a polyline of length $\ell(r)$.

## 4.2 Data conditioning and network construction

The permit register holds 614 records `[CL-01]`. A permit authorises a vehicle; it is not a route. Hashing
the two endpoints of each permit, direction ignored, at 11 m resolution reduces the 614 records to 157
distinct corridors `[CL-02]` (155 at 100 m, so the count does not depend on the rounding). The mean is 3.9
permits per corridor, the median is one, and a single corridor, Hazratbal to Lal Ded, carries 42
`[CL-03, CL-04]`. Any statement about "reduction" therefore has to say which unit it counts (§5.1). The
register rows join to the plan's route records with a 99.8 % match on origin and destination names (613 of
614) `[CL-10]`.

The population surface is used as published and is not rescaled. Its total over the ten districts is 95.6 %
of the 2011 Census total for the same boundary `[CL-13]`, but the agreement is uneven: district ratios range
from 0.71 to 1.20, and only two of the ten districts fall inside the growth band we set for the comparison
`[CL-14]`. Coverage shares for individual districts carry that error. The surface is also modelled from
building footprints and other settlement layers, which matters for the validation in §6.

The pedestrian graph has 961,927 nodes and 973,569 edges; 18,533 km of it lies inside the ten districts
`[CL-22]`. It was built from the Geofabrik extract for northern India dated 6 January 2026. Mapped road
density and population density agree in rank across the ten districts (Spearman $\rho = 0.915$)
`[CL-23]`, which is consistent with adequate mapping at district scale but, with ten observations, cannot
exclude local gaps. The opportunity layer is 2,431 points of interest in 63 categories, grouped into three
importance tiers: High (1,030), Medium (1,080) and Seasonal (321) `[CL-20]`. Two thirds of them are in
Srinagar district `[CL-21]`, so the layer is the input most exposed to uneven volunteer mapping, and its
weights are varied in §4.10.

*Provenance of the plan analysed.* The plan this paper evaluates was not produced in one pass, and four
facts about how it was produced bear on every result. First, place names in the register were geocoded
against a gazetteer of 103 names assembled from open geocoders, a commercial geocoder and manual
placement; for 37 villages that no geocoder could place, the centre of the village's district was used, and
19 of the 186 routes (93 buses) end at such an approximated point. Second, after the routing engine had
measured every route, road distances on 49 routes were replaced with values from an AI-assisted desk check
in which a language model researched each route's endpoints and road distance from web sources; this
lowered the fleet on those routes from 247 to 207. The research record does not retain source links, and the
map geometry was redrawn afterwards for 15 of the 18 routes where it no longer matched. Third, the cycle
times of five routes were re-timed from driver GPS (§6), raising the total from 1,004 to 1,011 buses.
Fourth, the headway rules in §4.7 were fixed in successive reviews of the plan with the transport regulator,
over about fifteen revisions in which the total fleet ranged from 855 to 1,144. The plan is therefore the
output of the method below together with these adjustments, and §4.10 and §6 test how far its decisions
survive them.

> **TO CONFIRM.** (a) Whether the regulator may be named as the body that set the headway rules (question
> for Avny ma'am); the sentence above says "the transport regulator" and can be made more general.
> (b) Whether any of the 49 researched distances were checked by a person; if so, say how many.

## 4.3 Route catchment delineation

Straight-line buffers around routes count residents who cannot reach the route on foot, a known bias
[@gutierrez2008distance; @biba2010new; @elgeneidy2014new]. We use a network walking catchment instead.
Each route is sampled into stops at 250 m spacing and each stop is snapped to its nearest graph node; of
22,360 stops, 46 lie farther than 400 m from the graph, and the median snap distance is 11 m `[CL-29]`. A
multi-source shortest-path search from all stops of a route gives every node $v$ its walking distance
$d(v)$ to the nearest stop. With a walk budget $W = 400$ m and an off-network tolerance $\tau = 100$ m
(one raster cell), the catchment is the union of discs

$$A_{net}(r) = \bigcup_{v \in V :\, d(v) \le W} B\left(x_v,\ \min(W - d(v),\ \tau)\right) \tag{1}$$

where $B(x, \delta)$ is a disc of radius $\delta$ about $x$. The residual leg of length at most $\tau$ is
allowed to leave the graph, which enlarges the catchment relative to a strict network walk. The measured
difference from a straight-line buffer depends on $W$, $\tau$, the stop spacing and the rule for counting
raster cells, so §5.2 reports it across those settings and not as a bound. The population of a catchment is

$$\Pi(r) = \sum_{c :\, x_c \in A_{net}(r)} \rho_c \tag{2}$$

counted over cells whose centre lies inside the catchment. Catchments of different routes overlap, so
per-route figures cannot be added. Where a network total is needed, a cell covered by $n_c$ routes is
shared equally among them,

$$\pi_c(r) = \frac{\rho_c}{n_c}\,\mathbf{1}[x_c \in A_{net}(r)], \qquad \sum_r \pi_c(r) = \rho_c \tag{3}$$

so that the allocated populations sum to the population of the union of all catchments.

## 4.4 Weighted opportunity accessibility

Opportunity is the weighted count of points of interest in the same catchment,

$$O(r) = \sum_{q \in Q \cap A_{net}(r)} \alpha_{t(q)} \tag{4}$$

where $t(q)$ is the tier of point $q$ and the weights are $\alpha_{High} = 1.00$, $\alpha_{Medium} = 0.40$
and $\alpha_{Seasonal} = 0.60$. These weights are assumptions; only their ratios matter, because the index is
normalised (Eq. 6). Visitors are invisible to a residential population raster, so routes flagged as tourist
corridors receive a multiplier,

$$O^{*}(r) = \begin{cases} \mu\, O(r), & r \in T \\ O(r), & r \notin T \end{cases} \qquad \mu = 1.30 \tag{5}$$

where $T$ is the set of flagged routes (8 of the 186 active ones). The value of $\mu$ is an assumption. In the
plan as produced, the multiplier was applied to the per-route resident count of those eight routes and so
raised their index. It did not enter the network coverage total, which is computed from the raster over the
union of catchments. We keep residents (Eq. 2) and the visitor adjustment (Eq. 5) in separate quantities
`[CL-30]`.

## 4.5 Composite demand index

Population and opportunity are divided by route length, the population density is capped at its 95th
percentile, and each is scaled to the unit interval across active routes,

$$\hat{z}(r) = \frac{z(r) - \min_{r'} z(r')}{\max_{r'} z(r') - \min_{r'} z(r')} \tag{6}$$

and the two are combined into a composite index [@oecd2008handbook],

$$CDI(r) = \beta\, \hat{z}_{\Pi}(r) + (1 - \beta)\, \hat{z}_{O}(r), \qquad \beta = 0.50 \tag{7}$$

where $\hat{z}_{\Pi}$ and $\hat{z}_{O}$ are the scaled values of $\Pi(r)/\ell(r)$ and $O^{*}(r)/\ell(r)$. The
two components are strongly correlated (Pearson 0.88 to 0.89), above the 0.85 level at which we had said a
principal-component weighting would replace Eq. 7. With two components that weighting is identical to equal
weights, so the substitution changes nothing, and the composite adds little beyond either component alone.
We report two distinct weightings, equal and Shannon-entropy
[@shannon1948mathematical; @zou2006entropy], and a sweep of $\beta$ (§5.4). No expert-elicited weights were
obtained.

The index is a proxy for where demand is likely to be, built without observed demand. Observed ridership
enters the plan at the following points, all from the e-bus operator's aggregates, and nowhere else:

1. The 30 e-bus routes are taken as given and are never merged (§4.6).
2. Their headway is the operator's 15-minute design target, and they are assigned to the highest tier
   regardless of their index value (§4.7).
3. On those routes the fleet is the larger of the computed fleet and the operator's deployed fleet (§4.8).
4. The scale $\kappa$, the mode share and the trip rate of the ridership estimate in Eq. 8 below are set
   from the same aggregates `[CL-59]`.
5. On the 67 rural routes outside the e-bus network, the headway is lengthened where Eq. 8 implies low load
   (§4.7), so the rural fleet depends on Eq. 8.

The ridership estimate, used to check plausibility, is

$$\tilde{D}(r) = \kappa \sum_{c \in A(r)} \rho_c\, m\, \sigma(r), \qquad \kappa = 0.33 \tag{8}$$

where $m$ is a mode share and $\sigma(r)$ shares a corridor's residents among the routes on it.
Eq. 8 is not a forecast. The paper's claim is accordingly limited: the method needs no observed demand for
the routes it plans, but where an operator's aggregates exist it uses them, and the validation against that
operator (§6) is circular for that reason.

## 4.6 Permit consolidation

Consolidation first removes duplicate permits on the same corridor and then merges corridors that largely
overlap. Overlap between two routes is measured on 80 m buffers $S(r)$ of the route lines,

$$\phi(r_i, r_j) = \frac{|S(r_i) \cap S(r_j)|}{\min(|S(r_i)|,\ |S(r_j)|)} \tag{9}$$

and a route is merged into a trunk only if $\phi \ge \theta$, with $\theta = 0.65$, and the two start points
lie within 2.5 km of each other. Overlap alone is not sufficient, which is why few distinct corridors merge.

```algorithm
Algorithm 1. Permit consolidation
Input: 644 candidate rows (614 permits and 30 e-bus routes); threshold theta
1. Cluster rows whose 80 m line buffers overlap by at least theta.
2. In each cluster, the route with the highest index that is at least 5 km long and above the 30th percentile of the index becomes the trunk.
3. Merge a member into the trunk only if at least theta of its buffer lies inside the trunk's and their start points are within 2.5 km. Otherwise it remains a feeder.
4. Never merge an e-bus route. Members are not merged into one another.
5. Collapse rows that share the same corridor, direction ignored, into one service.
Output: 186 active routes (32 trunks, 154 feeders); 458 rows absorbed
```

Duplicate permits are collapsed last, so the index percentiles in step 2 are computed over rows that still
include duplicates. The result keeps 156 of the 157 corridors `[CL-06, CL-08]`. Scenario S4 in §5.13 shows
what consolidation on overlap alone would do; because the merge rule is not varied in the uncertainty
analysis, that scenario is the only measure of how much the route set itself could differ.

## 4.7 Hierarchy and service standards

Routes are ranked by the index and divided into tiers by Jenks natural breaks
[@jenks1967data; @fisher1958grouping]. The number of classes is chosen from the goodness of variance fit,

$$GVF(k) = 1 - \frac{\sum_{j=1}^{k} \sum_{i \in C_j} (y_i - \bar{y}_{C_j})^2}{\sum_i (y_i - \bar{y})^2}, \qquad k = 2, \ldots, 7 \tag{10}$$

taking the smallest $k$ with $GVF \ge 0.80$, a threshold we adopt as an assumption. The partition is
compared with quantile and equal-interval classifications using Cohen's $\kappa$ [@cohen1960coefficient].

Headways are policy values, not outputs of the index: 15 minutes on the e-bus routes, 20 minutes on other
high-priority routes, 35 minutes on the remaining urban and peri-urban routes, and on rural routes 35, 40, 45
or 50 minutes according to the load implied by Eq. 8, with 50 minutes as the longest permitted wait. These
values, and the 35- and 50-minute ceilings in particular, were set in review with the transport regulator.
The published tier of a route therefore reflects both the index and overrides (the e-bus routes, district
headquarters and socially designated routes), and §5.6 reports how far the published tiers agree with the
index-only partition. The plan specifies one headway per route for the whole service day; variation by time
of day is examined separately in §5.11 and is not part of the plan.

## 4.8 Cycle time and fleet sizing

One-way running time is the routing engine's free-flow time scaled for congestion, plus dwell and fixed
delays [@vuchic2005urban; @ceder2007public],

$$t_{run}(r) = \chi(r)\left(t_{free}(r) + J(r)\right) + \delta\, \frac{\ell(r)}{\Delta} \tag{11}$$

where $\chi$ is 2.2 in the zone the plan treats as city core and 1.4 elsewhere, $J(r)$ is 8 minutes for a
route that crosses the Jhelum, and $\delta / \Delta$ is a dwell of 0.5 minutes per stop at one stop per
500 m. The city-core value applies to 170 of the 186 routes, because the zone is defined by terminal
latitude and takes in most rural routes; these three values are assumptions. Cycle time is then capped per
kilometre,

$$t_{cyc}(r) = \min\left(2 \lambda\, t_{run}(r),\ 2\, \ell(r)\, \omega_{class(r)}\right) \tag{12}$$

with layover factor $\lambda = 1.10$ and cap $\omega$ of 4.0, 2.5 and 1.5 minutes per kilometre for urban,
peri-urban and regional routes. The cap was intended as a ceiling on implausible values. It is in fact the
binding term on 169 of the 186 routes `[CL-31]`, so on those routes the cycle time is the cap, and Eq. 11
with its congestion assumptions has no effect on the published fleet. The urban cap of 4.0 minutes per
kilometre is also faster than the median pace observed in driver GPS, 4.62 `[CL-32]`. Section 4.10 therefore
sizes the fleet a second way, from observed pace. Fleet per route is

$$N_{op}(r) = \left\lceil \frac{t_{cyc}(r)}{h(r)} \right\rceil, \qquad N(r) = \max\left(\lceil \sigma N_{op}(r) \rceil,\ N^{min}_{class(r)}\right) \tag{13}$$

with headway $h(r)$ from §4.7, spare ratio $\sigma = 1.15$ (an assumption), and a minimum of two vehicles on
urban and peri-urban routes and one on regional routes. On the 30 e-bus routes the fleet is the larger of
Eq. 13 and the operator's deployed fleet $N^{emp}(r)$, which binds on two routes:

$$N_{total} = \sum_{r \notin E} N(r) + \sum_{r \in E} \max\left(N(r),\ N^{emp}(r)\right) = 728 + 283 = 1{,}011 \tag{14}$$

where $E$ is the set of e-bus routes. The register counts 679 buses with a valid permit in the ten districts
in March 2026, and the e-bus operator deploys 98, a current fleet of 777; the plan is 30 % above that
`[CL-36]`. Buses of the state road transport corporation are not in the register and are not counted in the
777, although the plan's routes include its former services.

Vehicles are assigned to the register's three size classes, heavy (full-size bus), medium (minibus) and light,
by route length and by the class of the permits the route replaces, with heavy vehicles limited to half the
fleet of any trunk. The totals are 187 heavy, 754 medium and 70 light. On 29 of the 32 trunks the medium
class is the majority, and 25 have no heavy vehicle.

Eqs. 11 to 13 were re-implemented independently of the planning code. The re-implementation returns the
published cycle time and fleet on all 186 routes when it is given the plan's headways, the five GPS-timed
cycles and the two e-bus fleet floors; without the last two it matches 180 routes and totals 1,000 `[CL-55]`.
That is the model on which §4.10 runs.

Because headways are policy values, the plan's capacity is not tied to demand. As a check on what the
service standards cost, we also compute the fleet that the same routes would need if each headway were set
so that peak load on the estimate of Eq. 8 reached a target, with and without a longest permitted wait
(§5.7).

## 4.9 Quality assurance gates

The analysis is released with automated checks that stop the pipeline on failure: every route lies inside the
study area; the population denominator is the single value above; no superseded figure appears in the
outputs; the fleet model reproduces the published fleet; permits, corridors and routes reconcile; corridor
keys ignore direction; route codes are unique; and the three vehicle classes sum to the fleet on every
route. Two further checks are reported and not enforced: agreement of the re-computed straight-line
catchment with the plan's own figure (136 of 142 comparable routes within 1 %), and the count of route ends
placed at a district centre (§4.2).

> **TO CONFIRM.** The list above must be checked line by line against the test suite before submission, so
> that every gate named here has a test that can fail.

## 4.10 Sensitivity and uncertainty

Three analyses are run. A one-at-a-time sweep varies each parameter of Table 3 over its range with the
others at their base values. A Monte Carlo analysis of 5,000 draws samples twelve parameters jointly from
stated distributions, and Sobol' first-order and total-order indices [@sobol2001global;
@saltelli2008global; @saltelli2010variance] attribute the variance of each output to the parameters. The
catchment parameters are evaluated on a grid of walk budgets from 300 to 800 m and stop spacings from 150
to 400 m.

Because the cap of Eq. 12 hides the running-time parameters on most routes, the fleet is computed under two
regimes. Regime A is the plan as specified, cap included. In regime B, urban and peri-urban routes outside
the e-bus network take their cycle time from the one-way pace observed in driver GPS, drawn from the
distribution of the median across 16 corridors around Srinagar. Five routes are measured directly, 84 take
the pooled pace, and the 30 e-bus and 67 regional routes are unchanged because no pace was observed for
them. We compute regime B twice, once from overall observed pace with layover and once from moving pace
with the model's own dwell and delays, which is how the five GPS-timed routes were treated in the plan.

Results are reported as the median and the 5th to 95th percentile range of the draws. These ranges are
conditional on the stated distributions and are not confidence intervals. The merge threshold $\theta$ is
not sampled, so uncertainty in the set of routes is outside these ranges; scenario S4 bounds it. What this
analysis supports is a statement about robustness, that is, whether tier and fleet decisions survive
plausible variation in the parameters and in speed. It is not a validation against demand.
