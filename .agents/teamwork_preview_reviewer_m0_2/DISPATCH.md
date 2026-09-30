# Task Assignment — Reviewer 2 (Milestone M0)

## Role
Reviewer 2 (Milestone M0 — Baseline Setup, Manifests, and Claim Ledger)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_reviewer_m0_2

## Objective
Independently review all files deployed for Milestone M0:
- Repository Hygiene: `README.md`, `requirements.txt`, `.gitignore`, `LICENSE`, `CITATION.cff`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`.
- Concurrency log: `logs/WORK_REGISTER.md`.
- Master runner: `analysis/run_all.py`.
- Manifest: `data/MANIFEST.md`.
- Claim Ledger: `paper/CLAIM_LEDGER.md`.

## Required Actions
1. Read `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` first.
2. Read `E:\kash-paper\.agents\orchestrator\PROJECT.md`.
3. Inspect `E:\kash-paper\.agents\teamwork_preview_worker_m0_1\handoff.md`.
4. Run verification commands:
   - `E:\kash-paper\.venv\Scripts\python.exe analysis/run_all.py --stage 0`
   - `E:\kash-paper\.venv\Scripts\python.exe -m pytest tests/unit/`
5. Verify SHA-256 hashes and sizes in `data/MANIFEST.md` match disk files.
6. Verify completeness of `paper/CLAIM_LEDGER.md` (claims CL-01 to CL-36, formulas, caveats, denominators).
7. Issue a clear verdict: `APPROVE` or `REQUEST_CHANGES` with detailed findings in `handoff.md`.
8. Send completion message via `send_message`.

## 2026-09-03T11:32:21Z
You are Reviewer 2 for Milestone M0 (Baseline Setup, Manifests, and Claim Ledger) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_reviewer_m0_2
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_reviewer_m0_2\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Independently review all files deployed for Milestone M0:
- Repository Hygiene: README.md, requirements.txt, .gitignore, LICENSE, CITATION.cff, DATA_AVAILABILITY.md, REPRODUCIBILITY.md.
- Master runner: analysis/run_all.py.
- Manifest: data/MANIFEST.md.
- Claim Ledger: paper/CLAIM_LEDGER.md.

Run verification commands:
- E:\kash-paper\.venv\Scripts\python.exe analysis/run_all.py --stage 0
- E:\kash-paper\.venv\Scripts\python.exe -m pytest tests/unit/

Verify SHA-256 hashes and sizes in data/MANIFEST.md match disk files.
Verify completeness of paper/CLAIM_LEDGER.md (CL-01 to CL-36, formulas, caveats, denominators).
Maintain progress.md with 'Last visited' timestamps.
Deliver handoff.md with a clear verdict: APPROVE or REQUEST_CHANGES.
Send completion message via send_message when done.

