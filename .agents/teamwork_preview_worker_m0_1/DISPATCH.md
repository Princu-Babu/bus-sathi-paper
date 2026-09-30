# Task Assignment — Worker (Milestone M0)

## Role
Worker (Milestone M0 — Baseline Setup, Manifests, and Claim Ledger Implementation)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_worker_m0_1

## Authoritative Inputs
- `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` (MANDATORY TO READ FIRST)
- `E:\kash-paper\.agents\orchestrator\PROJECT.md`
- Explorer M0-1 Handoff & Files: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_1\handoff.md` and `proposed_*`
- Explorer M0-2 Handoff: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_2\handoff.md` (includes complete `analysis/run_all.py` reference implementation)
- Explorer M0-3 Handoff & Files: `E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\handoff.md` and `proposed_MANIFEST.md`, `proposed_CLAIM_LEDGER.md`

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Exclusively Owned Production Files
- `E:\kash-paper\README.md`
- `E:\kash-paper\requirements.txt`
- `E:\kash-paper\.gitignore`
- `E:\kash-paper\LICENSE`
- `E:\kash-paper\CITATION.cff`
- `E:\kash-paper\DATA_AVAILABILITY.md`
- `E:\kash-paper\REPRODUCIBILITY.md`
- `E:\kash-paper\logs\WORK_REGISTER.md`
- `E:\kash-paper\analysis\run_all.py`
- `E:\kash-paper\data\MANIFEST.md`
- `E:\kash-paper\paper\CLAIM_LEDGER.md`

## Required Actions
1. Log task assignment in `logs/WORK_REGISTER.md` (Task ID: `WR-M0-IMPL`).
2. Deploy repository hygiene files to root:
   - `README.md`, `requirements.txt`, `.gitignore`, `LICENSE`, `CITATION.cff`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`
3. Deploy `analysis/run_all.py` based on M0-2 specification and reference code.
4. Deploy `data/MANIFEST.md` based on M0-3 specification.
5. Deploy `paper/CLAIM_LEDGER.md` based on M0-3 specification.
6. Verification commands:
   - Run `E:\kash-paper\.venv\Scripts\python.exe analysis/run_all.py --list`
   - Run `E:\kash-paper\.venv\Scripts\python.exe analysis/run_all.py --dry-run --quick`
   - Verify zero legacy metrics (`342`, `207`, `39%`, `95.7%`, `1,009`, SMC) in all new files.
7. Update `logs/WORK_REGISTER.md` marking task COMPLETE.
8. Deliver handoff report to `E:\kash-paper\.agents\teamwork_preview_worker_m0_1\handoff.md` with complete verification logs.
9. Send completion message via `send_message`.

## 2026-09-03T11:24:50Z
You are the Worker for Milestone M0 (Baseline Setup, Manifests, and Claim Ledger Implementation) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_worker_m0_1
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_worker_m0_1\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your mission:
Implement all Milestone M0 deliverables based on the explorer findings and reference files:
1. Log task ownership in logs/WORK_REGISTER.md (Task ID: WR-M0-IMPL).
2. Deploy repository hygiene files to root: README.md, requirements.txt, .gitignore, LICENSE, CITATION.cff, DATA_AVAILABILITY.md, REPRODUCIBILITY.md from E:\kash-paper\.agents\teamwork_preview_explorer_m0_1\proposed_*.
3. Deploy analysis/run_all.py based on E:\kash-paper\.agents\teamwork_preview_explorer_m0_2\handoff.md.
4. Deploy data/MANIFEST.md based on E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_MANIFEST.md.
5. Deploy paper/CLAIM_LEDGER.md based on E:\kash-paper\.agents\teamwork_preview_explorer_m0_3\proposed_CLAIM_LEDGER.md.
6. Verify implementation:
   - Run analysis/run_all.py --list and analysis/run_all.py --dry-run --quick using .venv Python.
   - Verify checksums and ensure zero legacy numbers (342, 207, 39%, 95.7%, 1009, SMC framing).
7. Update logs/WORK_REGISTER.md to mark task complete.
8. Maintain progress.md with 'Last visited' timestamps.
9. Deliver handoff.md with full verification outputs.
10. Send completion message via send_message when done.

