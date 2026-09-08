"""
Tier 2 Integration Tests: v04_gps_validation.py -> a09_monte_carlo_sobol.py.

Contract:
- v04_gps_validation.json exports empirical speed / pace prior distribution parameters:
  moving_speed_kmh, effective_speed_kmh, dwell_min_per_km, one_way_pace_min_per_km.
- Consumer a09_monte_carlo_sobol.py samples from these empirical priors.
"""
import json
from pathlib import Path
import pytest
from tests.conftest import DERIVED_DIR


@pytest.mark.tier2
def test_gps_validation_exports_monte_carlo_priors():
    """Verify v04_gps_validation.json exports triangular distribution priors for Monte Carlo."""
    v04_json = DERIVED_DIR / "v04_gps_validation.json"
    if not v04_json.exists():
        pytest.skip("v04_gps_validation.json not yet generated")
        
    with v04_json.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
        
    assert "monte_carlo_priors" in data, "Must export 'monte_carlo_priors' key"
    priors = data["monte_carlo_priors"]
    
    required_prior_keys = [
        "moving_speed_kmh",
        "effective_speed_kmh",
        "dwell_min_per_km",
        "one_way_pace_min_per_km"
    ]
    for k in required_prior_keys:
        assert k in priors, f"Missing prior {k} in monte_carlo_priors"
        dist = priors[k]
        assert "low" in dist and "mode" in dist and "high" in dist, f"Malformed triangular prior {k}: {dist}"
        assert dist["low"] <= dist["mode"] <= dist["high"], f"Triangular prior ordering invalid: {dist}"
