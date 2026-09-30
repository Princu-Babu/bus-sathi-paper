# Task Assignment — Challenger 2 (Milestone M0)

## Role
Challenger 2 (Milestone M0 — Data Manifest & Claim Ledger Adversarial Audit)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_challenger_m0_2

## Objective
Empirically challenge `data/MANIFEST.md` and `paper/CLAIM_LEDGER.md`:
- Recompute SHA-256 hashes and file sizes for all 20 raw data files and heavy cache files independently and verify 100% agreement with `data/MANIFEST.md`.
- Verify `.gitignore` rules against `git check-ignore` or file patterns to ensure `walk_graph.gpickle`, `catchments_network.gpkg`, and temporary files are strictly ignored.
- Audit `paper/CLAIM_LEDGER.md`: check mathematical formulas, denominators, and claim consistency against raw inputs and `paper/FINDINGS.md`.
- Run pytest suite `E:\kash-paper\.venv\Scripts\python.exe -m pytest tests/`.

## Required Actions
1. Read `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` first.
2. Read `E:\kash-paper\.agents\orchestrator\PROJECT.md`.
3. Write and execute adversarial audit scripts using `E:\kash-paper\.venv\Scripts\python.exe`.
4. Issue a clear verdict: `APPROVE` or `REQUEST_CHANGES` in `handoff.md`.
5. Send completion message via `send_message`.

## 2026-09-03T11:32:21Z
You are Challenger 2 for Milestone M0 (Baseline Setup, Manifests, and Claim Ledger) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_challenger_m0_2
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_challenger_m0_2\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Empirically challenge data/MANIFEST.md and paper/CLAIM_LEDGER.md:
- Recompute SHA-256 hashes and file sizes for all 20 raw data files and heavy cache files independently and verify 100% agreement with data/MANIFEST.md.
- Verify .gitignore rules to ensure walk_graph.gpickle, catchments_network.gpkg, and temporary files are strictly ignored.
- Audit paper/CLAIM_LEDGER.md: check mathematical formulas, denominators, and claim consistency against raw inputs and paper/FINDINGS.md.
- Run pytest suite E:\kash-paper\.venv\Scripts\python.exe -m pytest tests/.

Maintain progress.md with 'Last visited' timestamps.
Deliver handoff.md with a clear verdict: APPROVE or REQUEST_CHANGES.
Send completion message via send_message when done.
