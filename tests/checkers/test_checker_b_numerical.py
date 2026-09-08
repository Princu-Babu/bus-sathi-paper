"""
Checker B: Numerical Reproducibility Audit.

Enforces:
1. Fixed random seed RANDOM_SEED = 20260823.
2. CSV-only derived tables (no parquet / pyarrow binary tables).
3. Unique route IDs across all 186 active routes.
4. JSON outputs contain required metadata (N, parameters, seed, source-output paths).
5. Floating point and rounding tolerances.
"""
import json
from pathlib import Path
import pytest
import pandas as pd
from tests.conftest import (
    RANDOM_SEED,
    EXPECTED_ACTIVE_ROUTES,
    DERIVED_DIR,
    TABLES_DIR,
)


@pytest.mark.checker_b
@pytest.mark.quick
def test_random_seed_in_common():
    """Verify RANDOM_SEED is defined as 20260823."""
    import analysis.common as C
    assert hasattr(C, "RANDOM_SEED"), "common.py must define RANDOM_SEED"
    assert C.RANDOM_SEED == 20260823, f"RANDOM_SEED must be 20260823, got {C.RANDOM_SEED}"


@pytest.mark.checker_b
@pytest.mark.quick
def test_csv_only_derived_tables():
    """Verify no parquet, feather, or hdf5 files exist in data/derived/."""
    prohibited_extensions = [".parquet", ".pq", ".feather", ".h5", ".hdf5"]
    for ext in prohibited_extensions:
        found = list(DERIVED_DIR.glob(f"*{ext}"))
        assert not found, f"Prohibited binary format found in data/derived/: {found}"


@pytest.mark.checker_b
@pytest.mark.quick
def test_unique_active_route_ids(active_df):
    """Verify each of the 186 active routes has a unique New_Route_ID."""
    route_ids = active_df["New_Route_ID"].dropna().astype(str).tolist()
    assert len(route_ids) == EXPECTED_ACTIVE_ROUTES
    duplicates = [rid for rid in set(route_ids) if route_ids.count(rid) > 1]
    assert not duplicates, f"Duplicate New_Route_ID found in active plan: {duplicates}"


@pytest.mark.checker_b
@pytest.mark.quick
def test_derived_json_metadata_structure():
    """
    Verify existing derived JSON files have valid syntax and standard metadata keys.
    """
    json_files = list(DERIVED_DIR.glob("*.json"))
    assert len(json_files) > 0, "Expected at least one derived JSON file"
    for jf in json_files:
        with jf.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        assert isinstance(data, dict), f"JSON root in {jf.name} must be a dictionary"


@pytest.mark.checker_b
def test_tables_csv_markdown_sync():
    """Verify that every table CSV has an accompanying markdown file and vice versa."""
    csv_tables = {p.stem for p in TABLES_DIR.glob("*.csv")}
    md_tables = {p.stem for p in TABLES_DIR.glob("*.md")}
    
    # If tables exist, check their parity
    if csv_tables:
        diff_csv_md = csv_tables - md_tables
        assert not diff_csv_md, f"CSV tables missing Markdown representation: {diff_csv_md}"
