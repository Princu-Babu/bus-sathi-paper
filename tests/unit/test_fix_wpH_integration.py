"""wpH integration: runner determinism/registry, figure rules, table hygiene, a14 provenance."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "analysis"
TABLES = ROOT / "paper" / "tables"
FIGS = ROOT / "paper" / "figures"
LOGS = ROOT / "logs"


def _registry():
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("run_all_under_test", ANALYSIS / "run_all.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_all_under_test"] = mod        # dataclasses needs the module registered
    spec.loader.exec_module(mod)
    return mod


def test_runner_registry_has_q02_a02_summary_and_a04_after_a09():
    m = _registry()
    by = m.REGISTRY_BY_NAME
    assert by["q02_fleet_baseline"].depends_on == ("q01_data_quality",)
    assert by["a02_summary"].args == ("--summary-only",) and not by["a02_summary"].is_heavy
    assert by["a02_network_catchments"].is_heavy and not by["a02_network_catchments"].args
    assert "a09_monte_carlo_sobol" in by["a04_class_count"].depends_on
    quick = [s.name for s in m.topological_sort([x for x in m.MODULE_REGISTRY if not x.is_heavy])]
    assert quick.index("a09_monte_carlo_sobol") < quick.index("a04_class_count") < quick.index("a08_sensitivity_oat")
    assert quick.index("a02_summary") < quick.index("a02b_faithfulness")
    # every registered script exists
    for s in m.MODULE_REGISTRY:
        assert (ANALYSIS / s.script).exists(), s.script


def test_tracked_run_logs_carry_no_volatile_fields():
    latest = json.loads((LOGS / "LATEST_RUN.json").read_text(encoding="utf-8"))
    flat = json.dumps(latest)
    for key in ("timestamp_utc", "total_elapsed_sec", "duration", "started_utc", "python"):
        assert key not in flat, key
    for log in LOGS.glob("*.log"):
        head = log.read_text(encoding="utf-8", errors="ignore")
        for tag in ("STARTED:", "FINISHED:", "DURATION:", "PYTHON:"):
            assert tag not in head, f"{log.name} still has {tag}"


def test_gitignore_covers_volatile_run_metadata():
    assert "logs/volatile/" in (ROOT / ".gitignore").read_text(encoding="utf-8")


def test_v01_keeps_recorded_pbf_hash_and_flags_presence():
    j = json.loads((ROOT / "data" / "derived" / "v01_spatial_crossval.json").read_text(encoding="utf-8"))
    prov = j["provenance"]
    assert re.fullmatch(r"[0-9a-f]{64}", prov["osm_pbf_sha256"] or "")
    assert isinstance(prov["pbf_present"], bool)


def test_figures_have_no_baked_titles_and_no_typed_counts():
    src = (ANALYSIS / "fig_generate_all.py").read_text(encoding="utf-8")
    assert "set_title(" not in src and "suptitle(" not in src
    body = src.split("def have(")[1]
    for typed in ("614", "644", "157", "30% of fleet", "n = 186", "GVF 0.80"):
        assert typed not in body.replace('"gvf_threshold"', ""), f"typed literal {typed!r} in a figure function"
    assert "budget_buses" not in body                      # figS2 marks buses_allocated
    assert "buses_allocated" in body
    assert "percentile(both, [0.2, 99.8])" not in body     # fig09 no longer clips tails
    for stem in ("fig03_study_area", "fig06_catchment_bias", "fig08_coverage", "fig09_fleet_interval",
                 "figS2_funding_curve"):
        assert (FIGS / f"{stem}.pdf").stat().st_size > 1000
        assert (FIGS / f"{stem}.png").stat().st_size > 1000
    assert "OpenStreetMap contributors; population: WorldPop (CC BY 4.0)" in src
    assert src.count("map_furniture(ax, 25, projected") == 2              # fig03 and fig08


def test_figS2_marker_is_buses_allocated():
    a15 = json.loads((ROOT / "data" / "derived" / "a15_scenarios.json").read_text(encoding="utf-8"))["funding_sequence"]
    assert a15["buses_allocated"] == 299 and a15["buses_allocated"] < a15["budget_buses"]


def _md_tables():
    return sorted(TABLES.glob("*.md"))


@pytest.mark.parametrize("path", _md_tables(), ids=lambda p: p.name)
def test_markdown_tables_have_no_nan_cells_and_consistent_columns(path):
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    if not lines:
        pytest.skip("no pipe table")
    widths = {len(ln.strip().strip("|").split("|")) for ln in lines if not set(ln.strip()) <= set("|-: ")}
    # a '|' inside a cell would change the count; the separator row defines the true width
    sep = [ln for ln in lines if set(ln.strip()) <= set("|-: ")][0]
    n = len(sep.strip().strip("|").split("|"))
    assert widths == {n}, f"{path.name}: column counts {widths}, header has {n}"
    for ln in lines:
        cells = [c.strip().lower() for c in ln.strip().strip("|").split("|")]
        assert "nan" not in cells, f"{path.name}: literal nan cell"
