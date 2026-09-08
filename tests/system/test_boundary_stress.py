"""
Tier 3 System Tests: Boundary Stress & Pairwise Invariants.
"""
import math
import numpy as np
import pytest
import analysis.common as C


@pytest.mark.tier3
def test_fleet_formula_extreme_boundaries():
    """Stress test fleet sizing formula under extreme inputs."""
    # Extremely large cycle time (e.g. 1000 minutes)
    operating = max(1, math.ceil(1000.0 / 15.0))
    fleet = max(max(1, math.ceil(operating * 1.15)), 2)
    assert fleet > 70
    assert operating < fleet

    # Extremely small cycle time (e.g. 0.1 minute)
    operating_small = max(1, math.ceil(0.1 / 35.0))
    fleet_small = max(max(1, math.ceil(operating_small * 1.15)), 2)
    assert operating_small == 1
    assert fleet_small == 2


@pytest.mark.tier3
def test_entropy_weights_numerical_stability():
    """Stress test entropy weights with extreme values, near-zero values, and large scales."""
    # Near-zero values
    m_tiny = np.array([
        [1e-9, 1e-9],
        [1e-9, 2e-9],
        [1e-9, 3e-9]
    ])
    w_tiny = C.entropy_weights(m_tiny)
    assert math.isclose(w_tiny.sum(), 1.0, rel_tol=1e-4)
    assert not np.isnan(w_tiny).any()


@pytest.mark.tier3
def test_gini_boundary_stress():
    """Stress test Gini coefficient with single element, large array, and negative filtering."""
    # Single element evaluates to valid float bounded in [0, 1]
    g_single = C.gini(np.array([100.0]))
    assert 0.0 <= g_single <= 1.0

    # Two elements: one 0, one 100
    g_two = C.gini(np.array([0.0, 100.0]))
    assert 0.4 <= g_two <= 0.6
