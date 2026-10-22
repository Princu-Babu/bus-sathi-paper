# 4. Methodology

> **Section owner:** Prashant. **Status:** final short version, 22 October 2026 (about 1,950 words of prose).
> Built from `paper/word_build/section4_final_content.js` by `content_to_md.js`; edit the content file, not this one.
> Line-by-line reasons and evidence: `paper/Section4_v6_Line_Justification.docx`. Equation numbers follow v6.

## 4.1 Overview

Route planning usually starts from observed travel, but Kashmir Division has no origin-destination survey, fare-card records or passenger counts for its private and state-run buses; its only electronic ticketing is on the Srinagar Smart City e-bus service. The method therefore starts from the services already licensed and timetabled and returns a network in which every route has a service tier, a headway and a fleet.

It has four stages (Fig. 4): records to corridors (Sections 4.2 and 4.3), what each route reaches (4.4 and 4.5), merging and ranking (4.5 to 4.7), and headways and fleets (4.7 and 4.8). Sections 4.9 to 4.11 describe where the e-bus operator's figures enter, the changes made before publication, and how the plan's decisions were tested.

> **[FIGURE 4 HERE]** The four stages of the method with the equations that implement them. The dashed box lists the inputs that come from the e-bus operator, from driver GPS or from a desk review rather than from open data.

## 4.2 Data

Table 3 lists the inputs; the existing services enter as 614 rows. The 445 private permits come from the Srinagar Regional Transport Office, whose register is far more complete than those of the other nine Kashmir offices (453 of its 1,259 rows name both ends of a route, against 133 of 1,742 elsewhere). Of its 548 heavy-bus permits, 544 record no route, so the private input is almost all minibuses. The other 169 rows are scheduled services of the Jammu and Kashmir Road Transport Corporation, typed in from a scanned timetable. Permits were used whether or not still in force; in June 2026 only 96 of the 453 route-bearing Srinagar permits were valid.

**Table 3.** Inputs to the method (detail in Table 2).

| Input | Source and date | Use |
|---|---|---|
| Private stage-carriage permits, 445 rows | Srinagar Regional Transport Office register; not open | Existing route set |
| Scheduled services, 169 rows | Jammu and Kashmir Road Transport Corporation, Kashmir Division timetable, transcribed by hand; not open | Existing route set |
| E-bus routes, fleet and boardings: 30 routes, 98 buses, 11,632,326 boardings | Srinagar Smart City operator, May 2025 to April 2026; not open | Section 4.9 |
| Residents per 100 m cell | WorldPop constrained estimate, release R2025A (alpha) | Catchments, coverage |
| Walking network, 2,431 points of interest, district boundaries | OpenStreetMap extract of 6 January 2026 | Catchments, destinations, study region |
| Road distance and free-flow time | OSRM routing engine on the same extract | Cycle time |
| Bus positions: 2,526 service runs by 157 driver accounts | Driver smartphone application, 6 February to 29 June 2026; not open | Sections 4.10 and 4.11 |

Running times come from a driver smartphone application recording positions about every 5 seconds; sessions were split into service runs, map-matched with OSRM and grouped into corridors. The runs lie mostly in and around Srinagar and carry no passenger information, so they are used only for running time.

The population surface, an alpha release used as published, totals 95.6% of the 2011 Census count, but districts differ from the Census by up to 29%. Of the 2,431 points of interest, 65% lie in Srinagar district, partly reflecting how thoroughly each area has been mapped.

The study region Ω is the union of the ten districts. Raster cell *c*, centred at $x_{c}$, holds $\rho_{c}$ residents; the region holds 6,584,762, the denominator of every coverage share. *G* = (*V*, *E*) is the walking network and route *r* a line of length ℓ(*r*). The open sources are WorldPop [@stevens2015disaggregating; @tatem2017worldpop], OpenStreetMap [@osm2024planet] and OSRM [@luxen2011realtime], built on the same map extract as the walking network.

## 4.3 From permit rows to corridors

Place names were geocoded with Nominatim within the district named in each record; the rest came from a gazetteer of 103 entries, in which 37 villages that no source could locate sit at their district's centre, so routes ending there have approximate distances and catchments.

A permit licenses a vehicle, so several rows often describe one route. Rows whose end points match within 11 m, in either direction, form one corridor; the 614 rows describe 157 corridors. The busiest, Hazratbal to Lal Ded, has 42 rows, so any reduction in route numbers depends on the unit counted, which Section 5 states each time.

## 4.4 Walking catchments

Straight-line buffers [@murray2001strategic] count people across rivers, lakes and walls as served, an error measured in several cities [@gutierrez2008distance; @biba2010new; @elgeneidy2014new]. Srinagar is divided by the Jhelum and its lakes, so catchments were measured on the walking network.

Notional stops were placed every 250 m along each route and attached to the nearest node (median offset 11 m). A shortest-path search from all stops gives each node *v* its walking distance *d*(*v*). With budget *W* = 400 m and an off-network allowance τ = 100 m, one raster cell, the catchment is

$$A_{net}(r) = \bigcup_{v \in V :\, d(v) \leq W} B\left(x_v,\ \min(W - d(v),\ \tau)\right) \tag{1}$$

where *B*(*x*, δ) is the disc of radius δ centred on *x*. Its residents are

$$\Pi(r) = \sum_{c :\, x_c \in A_{net}(r)} \rho_c \tag{2}$$

Neighbouring routes share residents, so for network totals each cell is split equally among the $n_{c}$ routes reaching it:

$$\pi_c(r) = \frac{\rho_c}{n_c}\,\mathbf{1}[x_c \in A_{net}(r)], \qquad \sum_r \pi_c(r) = \rho_c \tag{3}$$

*W* is varied from 300 to 800 m (Section 4.11). The quality of the walking environment, which also affects willingness to walk [@bivina2019influence], is not modelled.

## 4.5 Destinations and the composite index

Destinations were counted as cumulative opportunities [@geurs2004accessibility]: point *q* counts towards route *r* when its walking distance to the nearest stop, $d_{q}(r)$, is at most 250 m, weighted by its tier *t*(*q*):

$$O(r) = \sum_{q \in Q :\, d_q(r) \leq 250\,\mathrm{m}} \alpha_{t(q)} \tag{4}$$

Tiers come from OpenStreetMap tags and 67 name rules, with α = 1.00 for major destinations (1,030 points), 0.40 for others (1,080) and 0.60 for seasonal sites (321). They are coarse: every place of worship is in the top tier (547 points). The weights and tiers are our assumptions; the plan itself measured the 250 m in a straight line.

Because a residential surface misses visitors, the plan raised the resident count of the eight tourist routes, the set *T*:

$$\Pi^{*}(r) = \mu\, \Pi(r)\ \ \mathrm{if}\ r \in T, \qquad \Pi^{*}(r) = \Pi(r)\ \ \mathrm{otherwise}, \qquad \mu = 1.30 \tag{5}$$

This changes their index but not network coverage. Both measures were divided by route length, density was capped at its 95th percentile, and each was rescaled,

$$\hat{z}(r) = \frac{z(r) - \min_{r'} z(r')}{\max_{r'} z(r') - \min_{r'} z(r')} \tag{6}$$

and combined with weight β on residents [@oecd2008handbook]:

$$CDI(r) = \beta\, \hat{z}_{\Pi}(r) + (1 - \beta)\, \hat{z}_{O}(r), \qquad \beta = 0.50 \tag{7}$$

where $\hat{z}_{\Pi}$ and $\hat{z}_{O}$ rescale $\Pi^{*}(r)/\ell(r)$ and $O(r)/\ell(r)$. The components correlate strongly (Pearson's *r* = 0.89), so the index is close to a density ranking with a destination adjustment. Section 5 compares equal weights, to which principal-component weights [@jolliffe2002principal] reduce here, with entropy weights [@shannon1948mathematical; @zou2006entropy] and β from 0.2 to 0.8. The index indicates where demand is likely; it does not measure it.

## 4.6 Merging overlapping routes

Overlap is measured on 80 m buffers *S*(*r*):

$$\phi(r_i, r_j) = \frac{|S(r_i) \cap S(r_j)|}{\min(|S(r_i)|,\ |S(r_j)|)} \tag{8}$$

A trunk is the highest-ranked route of its overlap group; a member joins it only when φ ≥ θ = 0.65 and their start points lie within 2.5 km. Members never merge with each other, and e-bus routes are never absorbed (Algorithm 1). These values are our assumptions.

```algorithm
Algorithm 1. Merging overlapping routes
Input: 644 candidate routes (614 permit and timetable rows and 30 e-bus routes); threshold $\theta$.
Group routes whose 80 m buffers overlap by at least $\theta$.
In each group, take the route with the highest index as trunk if it is at least 5 km long and above the 30th percentile of the index.
Absorb a member into the trunk if $\phi \geq$ $\theta$ and the two start points are within 2.5 km; otherwise keep the member as a feeder.
Never absorb an e-bus route, and never merge two members with each other.
Collapse routes on the same corridor, in either direction, into one service.
Output: 186 active routes (32 trunks and 154 feeders); 458 routes absorbed.
```

The rule is conservative: the 186 active routes keep 156 of the 157 corridors. It is not sampled in the uncertainty analysis; scenario S4 (Section 5) is its only test.

## 4.7 Service tiers and headways

Routes are typed by length as urban (under 15 km), peri-urban (15 to 40 km) or regional (over 40 km), unless their permit category says otherwise. Tiers were set by Jenks natural breaks on the index [@fisher1958grouping; @jenks1967data], judged by the goodness of variance fit:

$$GVF(k) = 1 - \frac{\sum_{j=1}^{k}\;\;\sum_{i \in C_j} (y_i - \bar{y}_{C_j})^2}{\sum_i (y_i - \bar{y})^2}, \qquad k = 2, \ldots, 7 \tag{9}$$

Three tiers give 0.90 against 0.79 for two; the 0.80 threshold separating them is our choice. Published tiers carry three overrides: e-bus routes are always in the top tier, routes within 250 m of 11 listed social destinations (four migrant townships and seven hospitals) rise from the lowest tier to the middle, and routes within 5% of the gap between breaks can move one tier by road role.

Headways are service standards, set independently of the index: 15 minutes on e-bus routes, 20 on other top-tier routes and 35 on other urban and peri-urban routes. Regional routes outside the e-bus network start at 35 minutes and, when estimated load (Section 4.9) is below 55%, are lengthened in proportion and rounded to 40, 45 or 50; in practice 62 of these 67 routes run at 50 and 5 at 35. Such standards pursue a coverage goal [@walker2008purpose]. Each route has one headway all day.

## 4.8 Cycle time and fleet

One-way running time is congested free-flow time plus stop time [@vuchic2005urban; @ceder2007public]:

$$t_{run}(r) = \chi(r)\left(t_{free}(r) + J(r)\right) + \delta\, \frac{\ell(r)}{\Delta} \tag{10}$$

where χ is 2.2 in the city core, a zone bounded by one line of latitude that contains 170 of 186 routes, and 1.4 elsewhere; *J* adds 8 minutes for a Jhelum crossing; and stops cost δ = 0.5 minutes every Δ = 500 m. These values are assumptions. Cycle time is capped per kilometre:

$$t_{cyc}(r) = \min\left(2 \lambda\, t_{run}(r),\ 2\, \ell(r)\, \omega_{type(r)}\right) \tag{11}$$

with λ = 1.10 for layover and ω = 4.0, 2.5 and 1.5 min/km for urban, peri-urban and regional routes. The cap binds on 169 of 186 routes, where Eq. (10) has no effect, and the urban cap is faster than the median pace observed in driver GPS, 4.62 min/km; Section 4.11 therefore also sizes the fleet from observed pace. With headway *h*(*r*),

$$N_{op}(r) = \left\lceil \frac{t_{cyc}(r)}{h(r)} \right\rceil, \qquad N(r) = \max\left(\lceil \sigma N_{op}(r) \rceil,\ N^{min}_{type(r)}\right) \tag{12}$$

where σ = 1.15 is an assumed spare allowance and $N^{min}$ is two buses (one on regional routes). The operator's deployed fleet $N^{emp}$ is a floor on the e-bus routes *E*:

$$N_{total} = \sum_{r \notin E} N(r) + \sum_{r \in E} \max\left(N(r),\ N^{emp}(r)\right) = 728 + 283 = 1{,}011 \tag{13}$$

Of these, 187 are heavy (about 12 m), 754 medium (about 9 m) and 70 light: routes under 12 km get no heavy buses, and heavy buses are at most half the fleet of longer routes. An independent re-implementation of Eqs. (10) to (12) reproduces the published fleet on all 186 routes.

## 4.9 Where the e-bus operator's figures enter

The method needs no observed demand for the routes it plans, but it uses the e-bus operator's figures at five points: the 30 e-bus routes are never absorbed; they are in the top tier at 15-minute headways; their fleet is at least the deployed fleet; the urban bus share and the scale of the ridership estimate come from their boardings; and that estimate can lengthen regional headways. It does not affect the route set or the tiers. For route *r*,

$$\tilde{D}(r) = \kappa\, g\, m_{type(r)}\, s(r) \sum_{c \in A(r)} \rho_c, \qquad \kappa = 0.33 \tag{14}$$

where *g* = 1.6 trips per person per day is assumed, *m* is the bus share for the route type, *A*(*r*) the catchment and *s*(*r*) the route's share of its corridor's residents. The urban share, 0.090, was backed out of e-bus boardings for an assumed served population of about 222,000; the peri-urban and regional shares are 0.8 and 0.6 of it by assumption. κ was fitted to the operator's 11.63 million boardings (May 2025 to April 2026). Only the product κ*gm* is identified, and comparison with the operator's data (Section 6) is circular. The demand-sized fleet in Section 5 holds demand fixed, although demand responds to service [@holmgren2007meta].

## 4.10 Changes made before publication

Three changes were made to the model's output before publication. First, all 186 routes were reviewed at a desk with an AI research assistant, which compared modelled road distances with distances published online and recorded the websites consulted. It passed 93, flagged 88 and failed 5. Where distances differed by more than 15% and place names were confirmed, the midpoint of the published range replaced the modelled distance and the fleet was recomputed; 49 routes changed, needing 207 buses instead of 247. No replacement distance was measured on the ground.

Second, five routes matched to GPS corridors with 40 to 211 runs each were re-timed from measured moving speed, raising the fleet from 1,004 to 1,011; they are excluded from the out-of-sample test in Section 6. Third, the headway standards were revised over about fifteen versions of the plan during review, with fleets ranging from 855 to 1,144 buses.

## 4.11 Sensitivity and uncertainty

A one-at-a-time sweep varies each parameter with the others fixed. A Monte Carlo analysis draws twelve inputs together 5,000 times, and Sobol' indices [@sobol2001global; @saltelli2008global; @saltelli2010variance] from a Saltelli design of 1,024 base samples (14,336 model runs) apportion the variance of each output. Catchment settings are evaluated on a grid of walking budgets (300 to 800 m) and stop spacings (150 to 400 m).

Because the cap hides the running-time parameters, the fleet is computed in two regimes: A, the plan as specified; and B, in which urban and peri-urban routes outside the e-bus network take cycle times from the pace observed on 16 GPS corridors around Srinagar (5 routes from their own corridors, 84 from their type's median), computed from overall pace and from moving pace plus modelled stop time. E-bus and regional routes keep their modelled cycles, as no usable pace was observed for them.

We report medians and 5th to 95th percentile ranges. They depend on our chosen input distributions, are not confidence intervals, and exclude uncertainty in the route set. The analysis tests whether decisions survive plausible changes in parameters and speeds, not the plan against demand. Analyses run from frozen inputs in Python 3.14 (seed 20260823) with SALib 1.5.2 and jenkspy 0.4.1.
