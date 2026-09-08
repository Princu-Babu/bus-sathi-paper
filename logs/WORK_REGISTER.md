# Multi-Worker Work Register & File Lock Ledger

**Purpose:** This document prevents concurrent write races across multiple agents and human researchers working within `E:\kash-paper`. It serves as the authoritative active file ownership log mandated by Item 8 of the Non-Negotiable Research Contract.

---

## 1. Multi-Worker Concurrency Protocol

Every worker (agent or human) must adhere to these rules before reading or modifying repository files:

1. **Check for Active Locks:**  
   Before claiming any file, inspect the register table below. If any file you intend to modify is currently listed under an `ACTIVE` status entry, **STOP**. Do not proceed until that entry is marked `COMPLETE` or `ABORTED`.
2. **Claim Exclusive Ownership:**  
   Append a new row to the table with status `ACTIVE`, listing your worker ID, task ID, specific files claimed for modification, expected outputs, start timestamp (UTC), and estimated duration.
3. **Strict Scope Discipline:**  
   Modify *only* the files declared in `Files_Claimed`. Never edit shared foundational files (`analysis/common.py`, `paper/FINDINGS.md`, `STATUS.md`, `paper/CLAIM_LEDGER.md`) without exclusive single-worker ownership.
4. **Log Command & Execution:**  
   Direct execution stdout/stderr to `logs/<Task_ID>.log`.
5. **Release Ownership Upon Completion:**  
   Immediately upon completing work and passing the task-specific acceptance gates, update the status to `COMPLETE`, record `Completed_UTC`, and state any residual limitations in `Notes_Limitations`.

---

## 2. Work Register Table

| Entry_ID | Timestamp_UTC | Worker | Task_ID | Milestone | Files_Claimed | Expected_Outputs | Status | Duration_Est | Completed_UTC | Notes_Limitations |
|---|---|---|---|---|---|---|---|---|---|---|
| `WR-001` | `2026-09-03T11:18:27Z` | `explorer_m0_1` | `M0.1-REPO-HYGIENE-EXPLORER` | `M0` | `.agents/teamwork_preview_explorer_m0_1/*` | `handoff.md`, `proposed_*` specifications | **COMPLETE** | 30m | `2026-09-03T11:25:00Z` | Complete design and specifications for all 8 repository hygiene files delivered; read-only exploration. |
| `WR-M0-IMPL` | `2026-09-03T11:28:00Z` | `teamwork_preview_worker_m0_1` | `WR-M0-IMPL` | `M0` | `README.md`, `requirements.txt`, `.gitignore`, `LICENSE`, `CITATION.cff`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`, `logs/WORK_REGISTER.md`, `analysis/run_all.py`, `data/MANIFEST.md`, `paper/CLAIM_LEDGER.md` | Production deployment of all M0 deliverables; verified run_all.py; zero legacy numbers | **COMPLETE** | 45m | `2026-09-03T11:32:00Z` | All 11 files deployed, checksums verified against 20 raw + 3 cache assets, run_all.py tested, zero legacy metrics confirmed. |

---

## 3. Active Lock Checklist (for Implementers)

Before editing production files:
- [x] Confirm no existing entry has status `ACTIVE` with overlapping `Files_Claimed`.
- [x] Claim the task in a new row with status `ACTIVE`.
- [x] Execute edits and verify against Acceptance Criteria.
- [x] Update row to `COMPLETE`.
