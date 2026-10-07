# 4. Methodology

> **Section owner:** Prashant. **Status:** rewritten on the corrected analysis and trimmed to the 2,300 words of
> Prof. Kathuria's brief (7 October 2026). Bracketed tags such as `[CL-31]` point to the claim ledger and are
> stripped from the submitted version. Shaded boxes are notes to the authors: **Author note** explains what
> was cut or where detail now lives; **TO CONFIRM** marks an open point. None of the boxes is text for the
> journal.

## 4.1 Framework overview

The framework turns an inherited stage-carriage permit register into a tiered network with a headway and a
fleet for every route, without an origin–destination matrix, boarding counts or fare data for the routes
being planned. Its main inputs are open: a gridded population surface (WorldPop, 100 m, release R2025A,
constrained) [@tatem2017worldpop; @stevens2015disaggregating], OpenStreetMap roads, footpaths, points of
interest and district boundaries [@osm2024planet], and a routing engine for road distance and free-flow time
[@luxen2011realtime]. Two inputs are not open: the permit register, obtained from the transport regulator,
and ridership aggregates for the one operator with electronic ticketing, the Srinagar Smart City e-bus
service. Section 4.5 lists every point at which the latter enters.

The pipeline has four phases (Figure 4): diagnosis of the inputs; accessibility, in which each route receives
a walking catchment scored for residents and opportunities; consolidation and hierarchy; and sizing, in
which cycle time, fleet and vehicle mix are computed and their uncertainty quantified. Table 3 lists every
parameter with its value, tested range and source.

The study region $\Omega$ is the union of the ten districts of Kashmir Division. The population raster
assigns $\rho_c$ residents to cell $c$ with centroid $x_c$; $\sum_{c \in \Omega} \rho_c = 6{,}584{,}762$
`[CL-11]` is the denominator of every coverage share. $G = (V, E)$ is the pedestrian graph from
OpenStreetMap, with edges weighted by length. A route $r$ has a polyline of length $\ell(r)$.

## 4.2 Data conditioning and network construction

The permit register holds 614 records `[CL-01]`. A permit authorises a vehicle; it is not a route. Hashing
the two endpoints of each permit, direction ignored, at 11 m resolution reduces the 614 records to 157
distinct corridors `[CL-02]`. The median corridor has one permit, and one corridor, Hazratbal to Lal Ded,
has 42 `[CL-03]`. Any statement about "reduction" must therefore say which unit it counts (§5.1).

The population surface is used as published. Its total over the ten districts is 95.6 % of the 2011 Census
total `[CL-13]`, but district ratios range from 0.71 to 1.20 `[CL-14]`, so coverage shares for single
districts carry that error. The pedestrian graph has 18,533 km of edges inside the ten districts
`[CL-22]`. The opportunity layer is 2,431 points of interest in three importance tiers `[CL-20]`; two thirds
are in Srinagar district `[CL-21]`, which makes it the input most exposed to uneven volunteer mapping.

> **Author note.** Cut from here and moved to Table 2 / the supplement: graph node and edge counts, the
> road-density check (Spearman 0.915 across ten districts), the 99.8 % permit-to-route name match, the
> point-of-interest tier counts, and the dataset dates (OpenStreetMap northern-India extract of 6 January
> 2026).

*Provenance of the plan.* The plan evaluated here was not produced in one pass, and four facts about its
production bear on every result. First, place names were geocoded against a gazetteer of 103 names; for 37
villages that no geocoder could place, the centre of the village's district was used, and 19 of the 186
routes (93 buses) end at such a point. Second, after routing, the road distances of 49 routes were replaced
with values from an AI-assisted desk check, in which a language model researched each route's endpoints and
road distance from web sources. No person verified these values and the record keeps no source links; the
change lowered the fleet on those routes from 247 to 207. Third, the cycle times of five routes were re-timed
from driver GPS (§6), raising the total from 1,004 to 1,011. Fourth, the headway rules of §4.7 were fixed
over about fifteen revisions reviewed with the transport regulator, during which the total ranged from 855
to 1,144 buses. The plan is the output of the method below together with these adjustments; §4.10 and §6
test how far its decisions survive them.

> **TO CONFIRM (Avny ma'am).** Whether the paper may say the headway rules were set in review with the
> transport regulator. If not, the fourth point becomes "policy constraints supplied to the study".

## 4.3 Route catchment delineation

Straight-line buffers count residents who cannot reach a route on foot, a known bias
[@gutierrez2008distance; @biba2010new; @elgeneidy2014new]. We use a network walking catchment. Each route
is sampled into stops at 250 m spacing, each snapped to its nearest graph node (median snap distance 11 m
`[CL-29]`). A multi-source shortest-path search gives every node $v$ its walking distance $d(v)$ to the
nearest stop. With walk budget $W = 400$ m and off-network tolerance $\tau = 100$ m (one raster cell), the
catchment is

$$A_{net}(r) = \bigcup_{v \in V :\, d(v) \le W} B\left(x_v,\ \min(W - d(v),\ \tau)\right) \tag{1}$$

where $B(x, \delta)$ is a disc of radius $\delta$ about $x$. Its population is

$$\Pi(r) = \sum_{c :\, x_c \in A_{net}(r)} \rho_c \tag{2}$$

Catchments overlap, so per-route figures cannot be added. For network totals, a cell covered by $n_c$
routes is shared equally,

$$\pi_c(r) = \frac{\rho_c}{n_c}\,\mathbf{1}[x_c \in A_{net}(r)], \qquad \sum_r \pi_c(r) = \rho_c \tag{3}$$

so allocated populations sum to the population of the union. The difference from a straight-line buffer
depends on $W$, $\tau$, the stop spacing and the cell-counting rule, so §5.2 reports it across those settings.

> **Author note.** The earlier claim that Eq. 1 gives "a lower bound on the true bias" is removed: at other
> settings the measured difference is smaller than the headline (range 28.7–52.8 %).

## 4.4 Weighted opportunity accessibility

Opportunity is the weighted count of points of interest in the same catchment,

$$O(r) = \sum_{q \in Q \cap A_{net}(r)} \alpha_{t(q)} \tag{4}$$

where $t(q)$ is the tier of point $q$, with $\alpha_{High} = 1.00$, $\alpha_{Medium} = 0.40$ and
$\alpha_{Seasonal} = 0.60$. Visitors are invisible to a residential raster, so the 8 active routes flagged as
tourist corridors, the set $T$, receive a multiplier:

$$O^{*}(r) = \begin{cases} \mu\, O(r), & r \in T \\ O(r), & r \notin T \end{cases} \qquad \mu = 1.30 \tag{5}$$

The weights and $\mu$ are assumptions. In the plan as produced, $\mu$ was applied to the per-route resident
count of those routes and so raised their index; it did not enter network coverage, which is computed over
the union of catchments `[CL-30]`.

> **Author note.** The earlier sentence that the multiplier "injected 285,914 synthetic persons into the
> coverage numerator" was wrong and is gone. That number summed overlapping per-route figures, and the
> coverage total never used the multiplied column.

## 4.5 Composite demand index

Population and opportunity are divided by route length, population density is capped at its 95th percentile,
and each is scaled across active routes,

$$\hat{z}(r) = \frac{z(r) - \min_{r'} z(r')}{\max_{r'} z(r') - \min_{r'} z(r')} \tag{6}$$

and combined [@oecd2008handbook]:

$$CDI(r) = \beta\, \hat{z}_{\Pi}(r) + (1 - \beta)\, \hat{z}_{O}(r), \qquad \beta = 0.50 \tag{7}$$

where $\hat{z}_{\Pi}$ and $\hat{z}_{O}$ are the scaled values of $\Pi(r)/\ell(r)$ and $O^{*}(r)/\ell(r)$. The
two components are strongly correlated (Pearson 0.88 to 0.89), so the composite adds little beyond either
alone. We report equal and Shannon-entropy weights [@shannon1948mathematical; @zou2006entropy] and a sweep
of $\beta$ (§5.4). No expert-elicited weights were obtained.

The index is a proxy for where demand is likely to be. Observed ridership enters the plan only through the
e-bus operator's aggregates, at five points:

1. The 30 e-bus routes are taken as given and never merged (§4.6).
2. Their headway is the operator's 15-minute design target, and they are placed in the highest tier whatever
   their index value (§4.7).
3. Their fleet is the larger of the computed fleet and the operator's deployed fleet (§4.8).
4. The scale, mode share and trip rate of the ridership estimate in Eq. 8 are set from those aggregates
   `[CL-59]`.
5. On the 67 rural routes outside the e-bus network, the headway is lengthened where Eq. 8 implies low load
   (§4.7).

The ridership estimate, used to check plausibility, is

$$\tilde{D}(r) = \kappa \sum_{c \in A(r)} \rho_c\, m\, \sigma(r), \qquad \kappa = 0.33 \tag{8}$$

where $m$ is a mode share and $\sigma(r)$ shares a corridor's residents among its routes. It is not a
forecast. The claim is therefore limited: the method needs no observed demand for the routes it plans, but it
uses an operator's aggregates where they exist, and validation against that operator (§6) is circular.

> **Author note.** This replaces "demand-free" and "no demand feed". Cut: the principal-component weighting
> (with two components it equals equal weights) and the remark about an expert panel planned for later.

## 4.6 Permit consolidation

Overlap between two routes is measured on 80 m buffers $S(r)$ of the route lines,

$$\phi(r_i, r_j) = \frac{|S(r_i) \cap S(r_j)|}{\min(|S(r_i)|,\ |S(r_j)|)} \tag{9}$$

and a route is merged into a trunk only if $\phi \ge \theta$, with $\theta = 0.65$, and the two start points
lie within 2.5 km. Overlap alone is not sufficient, which is why few distinct corridors merge.

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

The result keeps 156 of the 157 corridors `[CL-08]`. The merge rule is not varied in the uncertainty
analysis; scenario S4 (§5.13), which merges on overlap alone, is the only measure of how different the route
set could be.

## 4.7 Hierarchy and service standards

Routes are ranked by the index and divided into tiers by Jenks natural breaks
[@jenks1967data; @fisher1958grouping]. The number of classes is the smallest $k$ whose goodness of variance
fit reaches 0.80, a threshold we adopt as an assumption:

$$GVF(k) = 1 - \frac{\sum_{j=1}^{k} \sum_{i \in C_j} (y_i - \bar{y}_{C_j})^2}{\sum_i (y_i - \bar{y})^2}, \qquad k = 2, \ldots, 7 \tag{10}$$

Headways are policy values, not outputs of the index: 15 minutes on the e-bus routes, 20 minutes on other
high-priority routes, 35 minutes on the remaining urban and peri-urban routes, and 35 to 50 minutes on rural
routes according to the load implied by Eq. 8, with 50 minutes the longest permitted wait. The published tier
of a route reflects the index and also overrides for the e-bus routes, district headquarters and socially
designated routes; §5.6 reports how far published tiers agree with the index-only partition. The plan gives
one headway per route for the whole service day.

> **Author note.** Cut: "evaluated across peak, off-peak and evening bands". The plan has no time-of-day
> headways; that analysis is ours and sits in §5.11. Also cut: the comparison with other classifiers
> (reported in §5.8).

## 4.8 Cycle time and fleet sizing

One-way running time is the free-flow time scaled for congestion, plus dwell [@vuchic2005urban;
@ceder2007public]:

$$t_{run}(r) = \chi(r)\left(t_{free}(r) + J(r)\right) + \delta\, \frac{\ell(r)}{\Delta} \tag{11}$$

where $\chi$ is 2.2 in the zone treated as city core (170 of the 186 routes) and 1.4 elsewhere, $J(r)$ is 8
minutes for a route crossing the Jhelum, and $\delta / \Delta$ is 0.5 minutes per stop at one stop per 500 m.
These values are assumptions. Cycle time is capped per kilometre,

$$t_{cyc}(r) = \min\left(2 \lambda\, t_{run}(r),\ 2\, \ell(r)\, \omega_{class(r)}\right) \tag{12}$$

with layover factor $\lambda = 1.10$ and cap $\omega$ of 4.0, 2.5 and 1.5 minutes per kilometre for urban,
peri-urban and regional routes. The cap was meant as a ceiling on implausible values but is the binding term
on 169 of the 186 routes `[CL-31]`. On those routes Eq. 11 has no effect on the fleet, and the urban cap is
faster than the median pace observed in driver GPS, 4.62 minutes per kilometre `[CL-32]`. Section 4.10
therefore sizes the fleet a second way, from observed pace. Fleet per route is

$$N_{op}(r) = \left\lceil \frac{t_{cyc}(r)}{h(r)} \right\rceil, \qquad N(r) = \max\left(\lceil \sigma N_{op}(r) \rceil,\ N^{min}_{class(r)}\right) \tag{13}$$

with headway $h(r)$, spare ratio $\sigma = 1.15$ (an assumption) and a minimum of two vehicles on urban and
peri-urban routes and one on regional routes. On the e-bus routes, the set $E$, the operator's deployed fleet
$N^{emp}(r)$ is a floor:

$$N_{total} = \sum_{r \notin E} N(r) + \sum_{r \in E} \max\left(N(r),\ N^{emp}(r)\right) = 728 + 283 = 1{,}011 \tag{14}$$

Vehicles are assigned to the register's three size classes, heavy (full-size bus), medium (minibus) and
light, by route length and by the class of the permits a route replaces, with heavy vehicles limited to half
the fleet of any trunk. The totals are 187 heavy, 754 medium and 70 light.

Eqs. 11 to 13 were re-implemented independently of the planning code. Given the plan's headways, the five
GPS-timed cycles and the e-bus floors, the re-implementation returns the published fleet on all 186 routes;
without the last two it matches 180 routes and totals 1,000 `[CL-55]`. Because headways are policy values,
capacity is not tied to demand, so we also compute the fleet the same routes would need if each headway were
set to reach a target peak load on the estimate of Eq. 8 (§5.7).

> **Author note.** Moved to §5.7: the current fleet of 777 (679 buses with a valid permit plus 98 e-buses)
> and the +30 % comparison, buses per 100,000 residents, and the vehicle mix on trunks (medium buses are
> the majority on 29 of 32). The claim that the cap "ensures neither class is a majority on any trunk" was
> false and is gone.

## 4.9 Quality assurance gates

Automated checks stop the pipeline on failure: every route lies inside the study area; one population
denominator is used throughout; no superseded figure appears in the outputs; the fleet model reproduces the
published fleet; permits, corridors and routes reconcile; route codes are unique; and vehicle classes sum to
the fleet on every route. Two quantities are reported but not enforced: agreement of the recomputed
straight-line catchment with the plan's own figure, and the number of route ends placed at a district centre.

> **TO CONFIRM (Prashant, before submission).** Check this list against the test suite line by line, so
> every gate named has a test that can fail.

## 4.10 Sensitivity and uncertainty

A one-at-a-time sweep varies each parameter of Table 3 over its range. A Monte Carlo analysis of 5,000 draws
then samples twelve parameters jointly, and Sobol' first-order and total-order indices [@sobol2001global;
@saltelli2008global; @saltelli2010variance] attribute the variance of each output to them. Catchment
parameters are evaluated on a grid of walk budgets from 300 to 800 m and stop spacings from 150 to 400 m.

Because the cap of Eq. 12 hides the running-time parameters on most routes, the fleet is computed under two
regimes. Regime A is the plan as specified. In regime B, urban and peri-urban routes outside the e-bus
network take their cycle time from the one-way pace observed in driver GPS on 16 corridors around Srinagar:
five routes are measured directly, 84 take the pooled pace, and the 30 e-bus and 67 regional routes are
unchanged because no pace was observed for them. Regime B is computed from overall observed pace and,
separately, from moving pace with the model's own dwell.

Results are the median and the 5th to 95th percentile range of the draws. The ranges are conditional on the
stated distributions and are not confidence intervals. The merge threshold is not sampled, so uncertainty in
the route set lies outside them. The analysis supports a statement about robustness, that is, whether tier
and fleet decisions survive plausible variation in parameters and speed. It is not a validation against
demand.
