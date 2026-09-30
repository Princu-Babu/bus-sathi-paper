# Task Assignment — Forensic Auditor (Milestone M0)

## Role
Forensic Auditor (Milestone M0 — Integrity Forensics)

## Working Directory
E:\kash-paper\.agents\teamwork_preview_auditor_m0_1

## Objective
Perform independent forensic integrity audit on Milestone M0 deliverables:
- Check for CHEATING, hardcoding, dummy implementations, facade classes, or simulated test outputs.
- Verify that `analysis/run_all.py` is genuine executable code, not a mock or no-op script.
- Verify that `data/MANIFEST.md` and `paper/CLAIM_LEDGER.md` are genuine comprehensive documents derived from actual repo data and findings.
- Verify that no external repositories (`E:\kash`, `E:\bus-sathi-trace`) were modified in any way.
- Verify that git status / hygiene is respected (no cache leaks).

## Required Actions
1. Read `E:\kash-paper\.agents\ORIGINAL_REQUEST.md` first.
2. Read `E:\kash-paper\.agents\orchestrator\PROJECT.md`.
3. Inspect `E:\kash-paper\.agents\teamwork_preview_worker_m0_1\handoff.md`.
4. Inspect git status, file modification timestamps, diffs, and AST structure of new code.
5. Issue a strict binary verdict: `CLEAN` or `INTEGRITY VIOLATION` in `handoff.md`.
6. Send completion message via `send_message`.

## 2026-09-03T11:32:21Z
<USER_REQUEST>
You are the Forensic Auditor for Milestone M0 (Baseline Setup, Manifests, and Claim Ledger) for E:\kash-paper.

Your working directory is: E:\kash-paper\.agents\teamwork_preview_auditor_m0_1
Your task assignment is in: E:\kash-paper\.agents\teamwork_preview_auditor_m0_1\DISPATCH.md
Authoritative User Request: E:\kash-paper\.agents\ORIGINAL_REQUEST.md (MANDATORY TO READ FIRST)

Your mission:
Perform an independent forensic integrity audit on Milestone M0 deliverables:
- Check for CHEATING, hardcoding, dummy implementations, facade classes, or simulated test outputs.
- Verify that analysis/run_all.py is genuine executable code, not a mock or no-op script.
- Verify that data/MANIFEST.md and paper/CLAIM_LEDGER.md are genuine comprehensive documents derived from actual repo data and findings.
- Verify that no external repositories (E:\kash, E:\bus-sathi-trace) were modified.
- Verify that git status / hygiene is respected (no cache leaks).

Maintain progress.md with 'Last visited' timestamps.
Deliver handoff.md with a strict binary verdict: CLEAN or INTEGRITY VIOLATION.
Send completion message via send_message when done.
</USER_REQUEST>
