# Original User Request

## 2026-09-03T11:08:24Z

Execute the implementation, analysis, quality assurance, and manuscript drafting plan for the paper companion repository E:\kash-paper (*Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity*, targeting *Transport Policy*), covering all phases from Phase 0 to Phase 7 with independent checker audits and strict compliance with the non-negotiable research contract.

Working directory: E:\kash-paper
Integrity mode: development

## Non-Negotiable Research Contract
1. **Frozen operational baseline:** Kashmir Valley v3.4.5 is the active baseline (644 rows: 614 permits + 30 SSCL routes; 186 active services; stated fleet 1,011; WorldPop denominator 6,584,762). Do not invent or imply an engine v4.
2. **Correct study area:** Kashmir Division (10 districts) only, not Srinagar Metropolitan City. Any legacy SMC framing, 342-permit count, 207-route result, 39% route reduction claim, 95.7% coverage claim, or 1,009-bus headline is obsolete and prohibited from new material.
3. **GPS is not ridership:** App GPS validates the supply-side chain (geometry, speed, runtime, cycle time, fleet). It cannot validate demand, boarding, latent demand, or ridership. Never claim ridership validation; use observational GPS validation or decision robustness.
4. **No invented data:** Field enumeration and AHP/Delphi panel were not collected; report V3 plainly as not performed.
5. **Circularity disclosed:** Disclose CHALO calibration circularity in V2 up front. Mark the 5 GPS-corrected corridors as in-sample for cycle re-anchoring.
6. **Population is not demand:** Catchment populations overlap; report only the deduplicated union for network totals.
7. **Do not modify external repos:** E:\kash and E:\bus-sathi-trace are read-only. Large caches (data/cache/) must never be committed to git.
8. **No shared-file races:** Log active task ownership in logs/WORK_REGISTER.md.

## Requirements

### R1. Phase 0 — Baseline Setup, Manifests, and Claim Ledger
- Initialize paper companion repository hygiene: README.md, equirements.txt, .gitignore, LICENSE, CITATION.cff, DATA_AVAILABILITY.md, REPRODUCIBILITY.md, and logs/WORK_REGISTER.md.
- Implement nalysis/run_all.py supporting --stage, --module, --quick, and --full without invoking the engine or redownloading data.
- Build data/MANIFEST.md with source, licensing, filenames, and checksums for all raw staged data. Ensure large caches are excluded from git.
- Build paper/CLAIM_LEDGER.md registering every quantitative claim, statistic, denominator, universe, caveat, and manuscript location.

### R2. Phase 1 — Repaired Observational GPS Validation (v04)
- Rewrite nalysis/v04_gps_validation.py to evaluate the supply-side time and fleet chain under explicit groupings: matched_in_sample (5 corridors), partial_out_of_sample (9 corridors), and ll_corridors_descriptive (18 rows).
- Preserve both pre-v3.4.5 snapshot runtime and post-v3.4.5 cycle time without conflating them into single error calculations.
- Restrict route-length error evaluation strictly to the 5 matched corridors.
- Estimate dwell time using both OLS and WLS (weighted by 
_runs), reporting coefficients, CIs, R², corridor counts, total runs, and C17 influence.
- Implement the mandatory fleet-formula self-test:
  operating = max(1, ceil(cycle_min / max(1, headway_min)))
  leet = max(max(1, ceil(operating * 1.15)), 1 if route_type == Regional_District else 2)
  Reproduce every non-SSCL published fleet count with zero mismatches before conducting bounded fleet sensitivity illustrations.
- Produce derived datasets (04_corridor_comparison.csv, 04_gps_validation.json) and Tables 6a, 6b, 6c, and 6d with complete notes on GPS scope limits.

### R3. Phase 2 — Index Weights and Hierarchy Evidence
- Execute nalysis/a03_index_weights.py preserving predeclared parameter ranges; report resident population and POIs separately before CDI.
- Compare equal, entropy, and PCA first-component weights; explicitly record hp_weights_derived=false.
- Implement nalysis/a04_class_count.py to evaluate 2–7 classes using Jenks GVF, determine the elbow objectively, and assess tier agreement with Cohen's kappa across Jenks, quantiles, and k-means.
- Produce inputs for Table 3, Table 5, and Figure 6.

### R4. Phase 3 — Network Diagnostics, Accessibility, Equity, and Scenarios
- Implement 10_network_diagnostics.py and 05_headway_timeofday.py (parsing Hourly_Passenger_Count.csv with skiprows=1), distinguishing permits from distinct corridors and active services.
- Implement 11_coverage_accessibility.py, 12_equity_gini.py, and 13_transfers.py using deduplicated network catchments only, Moran's I on uncovered populations, and zero-centred diverging loss/gain maps.
- Implement operational plausibility modules (06_deadhead.py, 07_load_factor.py, 14_cost_emissions.py, 15_scenarios.py), strictly distinguishing proxy demand from observed occupancy.

### R5. Phase 4 — Uncertainty Analysis and Multi-Channel Validation
- Conduct One-At-a-Time (OAT) sensitivity sweeps (08_sensitivity_oat.py) across all 10 predeclared parameters.
- Run Monte Carlo simulation (09_monte_carlo_sobol.py) with 5,000 deterministic draws using the repaired GPS measured pace prior.
- Perform Sobol global sensitivity analysis reporting first- and total-order indices with confidence intervals.
- Execute validation channels: V1 spatial cross-validation against independent building footprint density, V2 benchmark consistency check (with circularity disclosure), and document V3 as not performed. Compile Table 7.

### R6. Phase 5 — Reproducible Publication Figures and Tables
- Programmatically generate Figures 1–8b using scripts (nalysis/figXX_*.py) reading exclusively from derived datasets.
- Produce manuscript Tables 1–8 in Markdown and CSV matching source data to exact rounding specifications.

### R7. Phase 6 — Manuscript Drafting (Prashant-Owned Sections)
- Draft §4 Methodology (2,300 words, sole owner: Equations 1–14, Algorithm 1, network walk catchments, consolidation, Jenks tiers, cycle/fleet formulas, reproducible from text alone).
- Draft §5 Results (2,400 words, shared with Misti: network diagnosis, design outcomes, accessibility/equity evaluation, stress tests, adverse findings).
- Draft §6 Validation (900 words, shared with Avny and Krishnan: convergent-validity framework, V1–V6 findings, explicit circularity disclosures, GPS supply-side limits).
- Draft §8 Conclusions (400 words: 6 structured paragraphs, no new citations or statistics) and Abstract (250 words, written last, eliminating legacy route-reduction claims).
- Map every quantitative statement to CLAIM_LEDGER.md.

### R8. Phase 7 — Independent Reproducibility & Release Audit
- Enforce Checker Checklists A–F across repository baseline, numerical consistency, GPS validity, statistical rigour, manuscript claims, and clean reproduction.
- Ensure total elimination of legacy numbers: no 342 permits, 207 routes, 39% reduction, 95.7% coverage, 1,009 fleet, or Srinagar Metropolitan City framing.

## Acceptance Criteria

### Data & Scope Integrity (Checker A)
- [ ] Exactly 10 districts in Kashmir Division; denominator 6,584,762/3.
- [ ] Zero uncontextualized occurrences of obsolete metrics (342, 207, 39%, 95.7%, 1,009, SMC).
- [ ] Raw inputs in data/raw/ untouched; git ignores large caches (walk_graph.gpickle, catchments_network.gpkg).

### Numerical & GPS Validation Reproducibility (Checkers B & C)
- [ ] Fixed random seed 20260823 applied across all stochastic runs.
- [ ] Fleet formula self-test produces exactly 0 mismatches across all eligible non-SSCL routes.
- [ ] Five GPS-corrected corridors explicitly labelled in_sample; partial matches excluded from whole-route length MAPE.
- [ ] All tables and figure source CSVs reproduce byte-identically or within declared floating tolerance.

### Methodological & Drafting Rigour (Checkers D & E)
- [ ] Weight alternatives sum to 1.0; no AHP or boarding survey fabricated; V3 marked not performed.
- [ ] Monte Carlo draws equal 5,000 accepted samples with GPS pace prior; Sobol indices include confidence intervals.
- [ ] All manuscript statements in Prashant's sections cite specific Claim Ledger IDs and derived outputs.
- [ ] Abstract, Results, and Conclusions contain zero claims of validated against ridership or false consolidation.

### Clean Reproduction (Checker F)
- [ ] python analysis/run_all.py --quick runs cleanly from E:\kash-paper\.venv.
- [ ] Unit tests for Euclidean catchment faithfulness and fleet reproduction pass with 0 errors.
