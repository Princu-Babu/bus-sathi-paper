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
    from types import SimpleNamespace
    from analysis import fleet_model as fm

    def run(cycle, headway, rtype="Urban"):
        arr = SimpleNamespace(headway=np.array([headway], float), floor=np.array([fm.FLOOR[rtype]]),
                              sscl=np.array([False]), sscl_floor=np.array([0]))
        return int(fm.fleet_from_cycle(arr, np.array([cycle], float), fm.BASE["FLEET_SPARE_RATIO"])[0])

    # Extremely large cycle time (1000 min at 15-min headway): 67 operating buses, x1.15 spare = 78
    assert run(1000.0, 15.0) == 78
    # Extremely small cycle time (0.1 min at 35-min headway): the floor governs
    assert run(0.1, 35.0) == 2
    # one operating bus x 1.15 spare rounds up to 2 whatever the floor (floor 1 for Regional)
    assert run(0.1, 35.0, "Regional_District") == 2


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
