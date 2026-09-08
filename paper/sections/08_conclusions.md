# 8. Conclusions

> **Section owners:** Ankit, Prashant, Sharvesh. **Target length:** ~400 words. **Status:** complete draft.

This study rationalised an inherited stage-carriage network **entirely from open data and with no
demand feed**. Spatial analysis of the register showed it to be a **permit** register, not a route
register: 614 permits `[CL-01]` describe 157 distinct corridors `[CL-02]`, which the plan reorganises
into **186 active routes** (32 trunk, 154 feeder) sized at a **1,011-vehicle fleet** (187/754/70
HPV/MPV/LPV; +68.5 % over the operating baseline) `[CL-06, CL-36]`. The pipeline is reproducible end to
end under a fixed seed.

The central methodological contribution is to measure catchments on a walkable pedestrian network
rather than as straight-line buffers. This single change lowers measured population served by a
**median of 37.4 % per route** and cuts headline division coverage from **35.5 % to 24.2 %**
`[CL-26, CL-28]` — because network catchments are the exception, not the rule, in the rationalisation
literature, the correction is roughly a third of the benefit that Euclidean methods report.

The study's other contributions are contributions of honesty. It shows the apparent 71 % "route
reduction" is **99.4 % corridor retention** plus a change of unit `[CL-07, CL-08]`; it recovers an
undocumented tourist multiplier that had injected 285,914 synthetic residents into a coverage
numerator `[CL-30]`; and it demonstrates that an intended sanity cap silently governs cycle time on
**90.9 % of routes** while sitting below real pace `[CL-31, CL-32]`, which is why fleet is reported as
an interval, not a point.

On validation we are deliberately narrow. Supply-side GPS reproduces the geometry and urban moving
speed `[CL-33, CL-35]` and the fleet arithmetic self-tests exactly `[CL-36]`, but driver GPS carries no
ridership signal, so the demand-side channels — an expert weight elicitation and an on-street boarding
survey — remain near-term work (§6.4). The plan is therefore **decision-robust, not demand-validated**
— the strongest honest claim available to a demand-free method, and one we intend to strengthen with
the field corroboration set out above.

Because the four inputs — a gridded population surface, OpenStreetMap, a routing engine, and a permit
list — exist for the roughly 400 Class-I Indian cities without an organised bus network, the framework
transfers directly, with data maturity treated as a ladder rather than a prerequisite.

The sentence the whole design works to keep unwriteable is that *the composite index bears no
established relationship to travel demand*. Four directions would close the gap: (i) a stratified
boarding-count survey to test the index-demand link directly; (ii) the deferred Delphi/AHP elicitation
to ground the weights; (iii) wider GPS instrumentation to replace the binding cap with measured pace;
and (iv) explicit seasonal and dynamic demand modelling for the tourist economy the resident raster
cannot see.
