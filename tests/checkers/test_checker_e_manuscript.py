"""
Checker E: Manuscript Claims and Ledger Audit.

Enforces:
1. Every quantitative claim maps to paper/CLAIM_LEDGER.md or FINDINGS.md.
2. Zero occurrences of 'validated against ridership' in draft prose.
3. Zero claims of route reduction without the change-of-unit distinction (Finding F1).
4. No false consolidation claims.
"""
import re
from pathlib import Path
import pytest
from tests.conftest import (
    REPO_ROOT,
    PAPER_DIR,
    check_no_legacy_strings,
)


@pytest.mark.checker_e
def test_findings_document_integrity():
    """Verify paper/FINDINGS.md adheres to the non-negotiable contract."""
    findings = PAPER_DIR / "FINDINGS.md"
    assert findings.exists(), "paper/FINDINGS.md must exist"
    text = findings.read_text(encoding="utf-8").lower()
    
    # Must mention change of unit
    assert "change-of-unit" in text or "change of unit" in text, (
        "FINDINGS.md must document the change-of-unit distinction (F1)"
    )
    # Must mention Euclidean catchment overstatement
    assert "euclidean" in text and "overstate" in text, (
        "FINDINGS.md must document Euclidean overstatement (F8)"
    )


@pytest.mark.checker_e
def test_manuscript_draft_integrity():
    """Verify any drafted sections under paper/draft/ have no forbidden claims."""
    draft_dir = PAPER_DIR / "draft"
    if not draft_dir.exists():
        pytest.skip("Draft directory does not exist yet (M6)")
        
    draft_files = list(draft_dir.glob("*.md"))
    if not draft_files:
        pytest.skip("No draft files written yet")
        
    violations = []
    for f in draft_files:
        text = f.read_text(encoding="utf-8")
        violations.extend(check_no_legacy_strings(text, context=f.name))
        
    assert not violations, f"Manuscript draft violations found:\n" + "\n".join(violations)
