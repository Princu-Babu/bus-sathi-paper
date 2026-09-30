# Dispatch Log

## 2026-09-03T11:09:44Z

Execute the implementation, analysis, quality assurance, and manuscript drafting plan for E:\kash-paper (Planning What You Cannot Count: An Open-Data Framework for Bus Route Rationalisation and Fleet Sizing under Demand-Data Scarcity, targeting Transport Policy), covering all phases from Phase 0 to Phase 7 with independent checker audits and strict compliance with the non-negotiable research contract.

Strict compliance with the Non-Negotiable Research Contract:
1. Frozen operational baseline: Kashmir Valley v3.4.5 is the active baseline (644 rows: 614 permits + 30 SSCL routes; 186 active services; stated fleet 1,011; WorldPop denominator 6,584,762). Do not invent or imply an engine v4.
2. Correct study area: Kashmir Division (10 districts) only, not Srinagar Metropolitan City. Any legacy SMC framing, 342-permit count, 207-route result, 39% route reduction claim, 95.7% coverage claim, or 1,009-bus headline is obsolete and prohibited from new material.
3. GPS is not ridership: App GPS validates the supply-side chain (geometry, speed, runtime, cycle time, fleet). It cannot validate demand, boarding, latent demand, or ridership. Never claim ridership validation; use "observational GPS validation" or "decision robustness".
4. No invented data: Field enumeration and AHP/Delphi panel were not collected; report V3 plainly as not performed.
5. Circularity disclosed: Disclose CHALO calibration circularity in V2 up front. Mark the 5 GPS-corrected corridors as in-sample for cycle re-anchoring.
6. Population is not demand: Catchment populations overlap; report only the deduplicated union for network totals.
7. Do not modify external repos: E:\kash and E:\bus-sathi-trace are read-only. Large caches (data/cache/) must never be committed to git.
8. No shared-file races: Log active task ownership in logs/WORK_REGISTER.md.

Phase Coverage:
- Phase 0: Baseline Setup, Manifests, Claim Ledger (hygiene files, analysis/run_all.py, data/MANIFEST.md, paper/CLAIM_LEDGER.md).
- Phase 1: Repaired Observational GPS Validation (v04) (rewrite analysis/v04_gps_validation.py, explicit groupings, dwell estimation OLS/WLS, fleet formula self-test, Tables 6a-6d).
- Phase 2: Index Weights and Hierarchy Evidence (analysis/a03_index_weights.py, a04_class_count.py, Tables 3, 5, Fig 6).
- Phase 3: Network Diagnostics, Accessibility, Equity, and Scenarios (a10_network_diagnostics.py, a05_headway_timeofday.py, a11_coverage_accessibility.py, a12_equity_gini.py, a13_transfers.py, a06_deadhead.py, a07_load_factor.py, a14_cost_emissions.py, a15_scenarios.py).
- Phase 4: Uncertainty Analysis and Multi-Channel Validation (a08_sensitivity_oat.py, a09_monte_carlo_sobol.py, validation channels V1-V3, Table 7).
- Phase 5: Reproducible Publication Figures and Tables (Figures 1-8b, Tables 1-8).
- Phase 6: Manuscript Drafting (Prashant-owned sections §4, §5, §6, §8, Abstract; CLAIM_LEDGER mapping).
- Phase 7: Independent Reproducibility & Release Audit (Checkers A-F, verification tests, zero legacy metrics).
