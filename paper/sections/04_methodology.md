# 4. Methodology

> **Section owner:** Prashant. **Status:** revised 15 October 2026, about 2,450 words with the new §4.11.
> Bracketed tags such as `[CL-31]` point to the claim ledger and are stripped from the submitted version.
> Shaded boxes are notes to the authors: **Author note** explains a change or where detail now lives;
> **TO CONFIRM** marks an open point. None of the boxes is text for the journal.

## 4.1 Framework overview

The framework takes an inherited register of stage-carriage permits and produces a tiered network in which
every route has a headway and a fleet. It uses no origin-destination matrix, boarding counts or fare data for
the routes it plans. Most of its inputs are open: a gridded population surface (WorldPop, 100 m, release
R2025A, constrained) [@tatem2017worldpop; @stevens2015disaggregating], OpenStreetMap roads, footpaths, points
of interest and district boundaries [@osm2024planet], and a routing engine for road distance and free-flow
time [@luxen2011realtime]. Two inputs are not open. The permit register came from the transport regulator,
and ridership totals came from the one operator with electronic ticketing, the Srinagar Smart City e-bus
service. Section 4.5 lists each point at which the operator's data enter.

The pipeline runs in four phases (Figure 4). The first checks the inputs. The second gives each route a
walking catchment and scores it for residents and destinations. The third merges overlapping permits and
ranks the routes. The fourth computes cycle time, fleet and vehicle mix, and measures how uncertain they are.
Table 3 gives every parameter with its value, the range over which it was tested and its source.

The study region $\Omega$ is the union of the ten districts of Kashmir Division. The population raster
assigns $\rho_c$ residents to cell $c$ with centroid $x_c$, and $\sum_{c \in \Omega} \rho_c = 6{,}584{,}762$
`[CL-11]` is the denominator of every coverage share. $G = (V, E)$ is the pedestrian graph from
OpenStreetMap, with edges weighted by length. A route $r$ has a polyline of length $\ell(r)$.

## 4.2 Data conditioning and network construction

The permit register holds 614 records `[CL-01]`. Each permit authorises a vehicle to ply between named
places, and many permits cover the same road. We matched the two end points of each permit at 11 m,
ignoring direction, and the 614 records reduce to 157 distinct corridors `[CL-02]`. The median corridor has
one permit; the busiest, Hazratbal to Lal Ded, has 42 `[CL-03]`. A "reduction" in this setting therefore has
to name its unit (§5.1).

We used the population surface as published. Its total for the ten districts is 95.6 % of the 2011 Census
total `[CL-13]`, but the district ratios run from 0.71 to 1.20 `[CL-14]`, and coverage shares for a single
district carry that error. The release is an alpha version. The pedestrian graph has 18,533 km of edges
inside the ten districts `[CL-22]`. The destination layer holds 2,431 points of interest in three tiers
`[CL-20]`. Two thirds of them lie in Srinagar district `[CL-21]`, so this layer depends more than any other
on how thoroughly volunteers have mapped each place.

> **Author note.** In Table 2 or the supplement: graph node and edge counts, the road-density check
> (Spearman 0.915 across ten districts), the 99.8 % match between permit and route names, the tier counts of
> destinations, and the dataset dates (OpenStreetMap northern-India extract of 6 January 2026).

*Provenance of the plan.* The plan evaluated here was built in stages, and four of them affect every result.
Place names were geocoded against a gazetteer of 103 names. For 37 villages that no geocoder could place, we
used the centre of the village's district, and 19 of the 186 routes (93 buses) end at such a point. After
routing, a route-by-route desk review of all 186 routes, carried out with an AI research assistant, compared
each modelled road distance with distances published on the web and recorded the websites consulted for every
route, though not the specific pages (93 passed, 88 marked for review, 5 failed). Where the reviewed distance
differed by more than 15% and the place names could be confirmed, it replaced the modelled one, and cycle time
and fleet were recomputed with the plan's formulas. This changed 49 routes and cut their fleet from 247 to 207.
None of the replacement distances was measured on the ground. The cycle
times of five routes were then re-timed from driver GPS (§6), which raised the total from 1,004 to 1,011.
Finally, the headway rules of §4.7 were settled over about fifteen revisions reviewed with the transport
regulator, and the total moved between 855 and 1,144 buses along the way. The plan is therefore the method
below plus these adjustments. Sections 4.10 and 6 test how far its decisions survive them.

> **TO CONFIRM (Avny ma'am).** Whether the paper may say the headway rules were set in review with the
> transport regulator. If not, the last adjustment becomes "policy constraints supplied to the study".

## 4.3 Route catchment delineation

A straight-line buffer counts residents who cannot reach the route on foot, and the error is well documented
[@gutierrez2008distance; @biba2010new; @elgeneidy2014new]. In Srinagar the lakes and the Jhelum make it
larger. We measured catchments on the walking network instead. Each route was sampled into stops 250 m
apart, and each stop was snapped to its nearest graph node (median snap distance 11 m `[CL-29]`). A
multi-source shortest-path search then gave every node $v$ its walking distance $d(v)$ to the nearest stop.
With a walking budget $W = 400$ m, the usual bus catchment [@trb2013transit], and an off-network tolerance
$\tau = 100$ m (one raster cell), the catchment is

$$A_{net}(r) = \bigcup_{v \in V :\, d(v) \le W} B\left(x_v,\ \min(W - d(v),\ \tau)\right) \tag{1}$$

where $B(x, \delta)$ is a disc of radius $\delta$ about $x$. Its population is

$$\Pi(r) = \sum_{c :\, x_c \in A_{net}(r)} \rho_c \tag{2}$$

Catchments overlap, so per-route populations cannot be added. For network totals we shared each cell equally
among the $n_c$ routes that cover it,

$$\pi_c(r) = \frac{\rho_c}{n_c}\,\mathbf{1}[x_c \in A_{net}(r)], \qquad \sum_r \pi_c(r) = \rho_c \tag{3}$$

and the allocated populations then sum to the population of the union. How far the network catchment differs
from a straight-line buffer depends on $W$, $\tau$, the stop spacing and the rule for counting a cell, so §5.2
reports the difference across those settings.

> **Author note.** Eq. 1 is no longer called "a lower bound on the true bias": at other settings the measured
> difference is smaller than the headline (range 28.7 to 52.8 %). The TCQSM citation for 400 m needs a page
> number from someone who has the manual open.

## 4.4 Weighted opportunity accessibility

The destination score of a route is the weighted count of points of interest within 250 m of walking along
the network from its stops, a shorter distance than the 400 m used for residents. The plan itself used a
250 m straight-line buffer. With $d_q(r)$ the walking distance from point $q$ to the nearest stop of $r$,

$$O(r) = \sum_{q \in Q :\, d_q(r) \le 250} \alpha_{t(q)} \tag{4}$$

where $t(q)$ is the tier of point $q$ and $\alpha_{High} = 1.00$, $\alpha_{Medium} = 0.40$ and
$\alpha_{Seasonal} = 0.60$. Tiers were assigned from OpenStreetMap tags, with name rules for a few dozen
known landmarks. The assignment is coarse: every place of worship and every facility tagged as a hospital
falls in the top tier. A residential population grid does not see visitors, so the 8 active routes flagged
as tourist corridors, the set $T$, receive a multiplier:

$$O^{*}(r) = \begin{cases} \mu\, O(r), & r \in T \\ O(r), & r \notin T \end{cases} \qquad \mu = 1.30 \tag{5}$$

The tier weights, the tier assignment and $\mu$ are our assumptions; no expert-elicited weights were
obtained. In the plan as produced, $\mu$ multiplied the resident count of those 8 routes and so raised their
index. It never entered network coverage, which is computed over the union of catchments `[CL-30]`.

> **Author note.** The old text said destinations were counted "in the same catchment" as residents. They are
> counted within 250 m, as Eq. 4 now says. A one-off check (`analysis/checks/poi_retier_check.py`) re-tiers
> places of worship, shops and hotels and moves at most 4 of 186 routes; add it to §5.4 and the ledger before
> quoting it.

## 4.5 Composite demand index

Both components were divided by route length, population density was capped at its 95th percentile, and
each was scaled across active routes,

$$\hat{z}(r) = \frac{z(r) - \min_{r'} z(r')}{\max_{r'} z(r') - \min_{r'} z(r')} \tag{6}$$

then combined [@oecd2008handbook]:

$$CDI(r) = \beta\, \hat{z}_{\Pi}(r) + (1 - \beta)\, \hat{z}_{O}(r), \qquad \beta = 0.50 \tag{7}$$

where $\hat{z}_{\Pi}$ and $\hat{z}_{O}$ are the scaled values of $\Pi(r)/\ell(r)$ and $O^{*}(r)/\ell(r)$. The
two components are strongly correlated (Pearson 0.88 to 0.89), and the composite adds little to either
alone. We report equal weights, Shannon-entropy weights [@shannon1948mathematical; @zou2006entropy] and a
sweep of $\beta$ (§5.4).

The index indicates where demand is likely to be; it does not measure demand. Observed ridership reaches the
plan only through the e-bus operator's totals, at five points:

1. The 30 e-bus routes are taken as given and never merged (§4.6).
2. Their headway is the operator's 15-minute design target, and they sit in the top tier whatever their
   index (§4.7).
3. Their fleet is the larger of the computed fleet and the operator's deployed fleet (§4.8).
4. The scale, mode share and trip rate of the ridership estimate in Eq. 8 are set from the operator's totals
   `[CL-59]`.
5. On the 67 rural routes outside the e-bus network, the headway is lengthened where Eq. 8 implies a low
   load (§4.7).

The ridership estimate, which serves only as a plausibility check, is

$$\tilde{D}(r) = \kappa\, g\, m_{type(r)} \sum_{c \in A(r)} \rho_c\, \sigma(r), \qquad \kappa = 0.33 \tag{8}$$

where $g = 1.6$ trips per person per day, $m$ is a bus mode share by route type (0.090 urban, 0.072
peri-urban, 0.054 regional), and $\sigma(r)$ shares a corridor's residents among the routes on it. The three
constants multiply, so the operator's totals fix only their product. Eq. 8 is an order-of-magnitude check and
we do not use it as a forecast. The claim we make is accordingly narrow: the method needs no observed demand
for the routes it plans, it does use one operator's totals where they exist, and any comparison with that
operator (§6) is circular.

> **Author note.** Eq. 8 now shows the trip rate, which the earlier version left out. The mode shares and the
> trip rate have no source; Table 3 marks them as assumptions.

## 4.6 Permit consolidation

Overlap between two routes is measured on 80 m buffers $S(r)$ of their lines,

$$\phi(r_i, r_j) = \frac{|S(r_i) \cap S(r_j)|}{\min(|S(r_i)|,\ |S(r_j)|)} \tag{9}$$

A route is merged into a trunk only when $\phi \ge \theta$, with $\theta = 0.65$, its start point lies within
2.5 km of the trunk's, and the trunk is the lead route of its group. Routes in a group are never merged into
one another. The last two conditions explain why few distinct corridors merge. The values 80 m, 0.65 and
2.5 km are our assumptions.

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

The plan keeps 156 of the 157 corridors `[CL-08]`. The uncertainty analysis holds the merge rule fixed.
Scenario S4 (§5.13) lowers the threshold to 0.50 and merges connected groups of routes, and it is the only
measure we have of how different the route set could be.

## 4.7 Hierarchy and service standards

Routes were ranked by the index and divided into tiers by Jenks natural breaks [@jenks1967data;
@fisher1958grouping]. We took the number of classes as the smallest $k$ whose goodness of variance fit
reaches 0.80, a threshold we chose:

$$GVF(k) = 1 - \frac{\sum_{j=1}^{k} \sum_{i \in C_j} (y_i - \bar{y}_{C_j})^2}{\sum_i (y_i - \bar{y})^2}, \qquad k = 2, \ldots, 7 \tag{10}$$

The headways are policy values. E-bus routes run every 15 minutes, other high-priority routes every 20, and
the remaining urban and peri-urban routes every 35. Rural routes run every 35 to 50 minutes depending on the
load implied by Eq. 8, and 50 minutes is the longest permitted wait. A route's published tier reflects its
index and three overrides, for e-bus routes, district headquarters and routes designated for social reasons.
Section 5.6 reports how far the published tiers agree with the partition by index alone. Each route has one
headway for the whole service day.

> **Author note.** The plan has no time-of-day headways; the time-of-day analysis is ours and sits in §5.11.
> The comparison with other classifiers is in §5.8. In the published plan 62 of the 67 rural routes sit at
> the 50-minute maximum and 5 at 35; add a ledger row before saying so in the text.

## 4.8 Cycle time and fleet sizing

One-way running time is the free-flow time scaled for congestion, plus dwell [@vuchic2005urban;
@ceder2007public]:

$$t_{run}(r) = \chi(r)\left(t_{free}(r) + J(r)\right) + \delta\, \frac{\ell(r)}{\Delta} \tag{11}$$

Here $\chi$ is 2.2 in the zone treated as the city core and 1.4 elsewhere. The core is defined by a line of
latitude and covers 170 of the 186 routes. $J(r)$ adds 8 minutes for a route that crosses the Jhelum, and
$\delta / \Delta$ is 0.5 minutes per stop at one stop every 500 m. All of these values are assumptions. Cycle
time is capped per kilometre,

$$t_{cyc}(r) = \min\left(2 \lambda\, t_{run}(r),\ 2\, \ell(r)\, \omega_{class(r)}\right) \tag{12}$$

with layover factor $\lambda = 1.10$ and cap $\omega$ of 4.0, 2.5 and 1.5 minutes per kilometre for urban,
peri-urban and regional routes. The cap was meant to catch implausible values. In practice it binds on 169
of the 186 routes `[CL-31]`, so on those routes Eq. 11 has no effect on the fleet. The urban cap is also
faster than the median pace in driver GPS, 4.62 minutes per kilometre `[CL-32]`, and §4.10 therefore sizes
the fleet a second time from observed pace. The fleet on a route is

$$N_{op}(r) = \left\lceil \frac{t_{cyc}(r)}{h(r)} \right\rceil, \qquad N(r) = \max\left(\lceil \sigma N_{op}(r) \rceil,\ N^{min}_{class(r)}\right) \tag{13}$$

with headway $h(r)$, an assumed spare ratio $\sigma = 1.15$, and at least two vehicles on urban and peri-urban
routes and one on regional routes. On the e-bus routes, the set $E$, the operator's deployed fleet
$N^{emp}(r)$ acts as a floor:

$$N_{total} = \sum_{r \notin E} N(r) + \sum_{r \in E} \max\left(N(r),\ N^{emp}(r)\right) = 728 + 283 = 1{,}011 \tag{14}$$

Vehicles fall into the register's three size classes: heavy (full-size bus), medium (minibus) and light. The
class depends on route length and on the class of the permits a route replaces, and heavy vehicles may be at
most half the fleet of a trunk. The plan has 187 heavy, 754 medium and 70 light vehicles.

We re-implemented Eqs. 11 to 13 independently of the planning code. With the plan's headways, the five
GPS-timed cycles and the e-bus floors, the re-implementation returns the published fleet on all 186 routes.
Without the last two it matches 180 routes and gives a total of 1,000 `[CL-55]`. Since the headways are
policy values, the fleet they produce is not tied to demand, and demand itself responds to the level of
service [@holmgren2007meta]. We therefore also compute the fleet the same routes would need if each headway
were set to reach a target peak load on the estimate of Eq. 8, with demand held fixed (§5.7).

> **Author note.** In §5.7: the current fleet of 777 (679 buses with a valid permit and 98 e-buses), the
> 30 % comparison, buses per 100,000 residents, and the vehicle mix on trunks, where medium buses are the
> majority on 29 of 32.

## 4.9 Quality assurance gates

Automated checks stop the pipeline when any of the following fails: every route lies inside the study area;
one population denominator is used throughout; no superseded figure appears in the outputs; the fleet model
reproduces the published fleet; permits, corridors and routes reconcile; route codes are unique; and vehicle
classes sum to the fleet on every route. Two quantities are reported without a pass mark: the agreement of
the recomputed straight-line catchment with the plan's own figure, and the number of route ends placed at a
district centre.

> **TO CONFIRM (Prashant, before submission).** Check this list against the test suite line by line, so
> that every gate named has a test that can fail.

## 4.10 Sensitivity and uncertainty

A one-at-a-time sweep varies each parameter in Table 3 over its range. A Monte Carlo analysis of 5,000 draws
then samples twelve parameters together, and Sobol' first-order and total-order indices [@sobol2001global;
@saltelli2008global; @saltelli2010variance] apportion the variance of each output among them. Catchment
parameters are evaluated on a grid of walking budgets from 300 to 800 m and stop spacings from 150 to 400 m.

The cap in Eq. 12 hides the running-time parameters on most routes, so the fleet is computed under two
regimes. Regime A is the plan as specified. In regime B, urban and peri-urban routes outside the e-bus
network take their cycle time from the one-way pace observed in driver GPS on 16 corridors around Srinagar.
Five routes are measured directly and 84 take the pooled pace. The 30 e-bus routes and 67 regional routes
keep their modelled cycle, because no pace was observed for them. Regime B is computed twice, once from
overall observed pace and once from moving pace with the model's own dwell.

We report the median and the 5th to 95th percentile range of the draws. These ranges depend on the input
distributions we chose, and they are not confidence intervals. The merge threshold is not sampled, so
uncertainty in the route set falls outside them. The analysis shows whether tier and fleet decisions
survive plausible changes in parameters and speed. Whether the plan matches demand is a separate question,
which the passenger survey in §4.11 and §6 begins to address.

## 4.11 Passenger survey

> **Author note.** New subsection drafted from the questionnaire supplied on 14 October 2026. Prof. Kathuria
> to confirm or rewrite; it may sit better in §6.

To see how the changes are felt by passengers, a before-and-after survey of city bus users in Srinagar is
being carried out, following the design used for network reforms elsewhere [@allen2019effect]. The
questionnaire, in English, Hindi and Urdu, follows the structure of earlier satisfaction work by the same
group [@singh2023heterogeneity]. It records the respondent and their usual bus trip, six facts about that
trip (walking time to the stop, waiting time, number of changes, total travel time, fare and trips per
week), and ratings of ten service attributes on a five-point scale, drawn from the bus service quality
literature [@eboli2007service]. A final question asks whether the trip is now better or worse than before.
Participation is voluntary and anonymous, and only adults are surveyed. Each respondent answers for the
service before the route changes, after them, or both, and the surveyor records which. The target sample is
348, from the finite-population formula used in Singh and Kathuria (2023) [@johnson2007applied;
@tyrinopoulos2008public] at 95 % confidence and a 5 % margin of error.

> **TO CONFIRM (Prof. Kathuria).** (1) The population figure behind 348: at 95 % and ± 5 % the formula gives
> 348 for a population of about 3,700, so the basis should be stated. (2) Which routes had changed, and when.
> (3) Sampling: which stops, days and hours, and how respondents were approached. (4) How many of the 348
> answer before only, after only, or both in one visit, since recall of "before" in the same visit is weaker
> evidence. (5) The planned test (paired or independent samples) and the treatment of "cannot recall".
> (6) Ethics approval or exemption.
