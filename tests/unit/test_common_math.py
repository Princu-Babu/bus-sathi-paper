"""
Tier 1 Unit Tests: Mathematical and Statistical Functions in analysis/common.py.

Verifies:
1. Gini coefficient: bounds in [0, 1], asymptotic behavior on large samples.
2. Shannon entropy weights: column weights sum to 1.0, uniform inputs receive equal weights.
3. MinMax normalizer: mapped into [0, 1], handles constant arrays without ZeroDivisionError.
4. Goodness of Variance Fit (GVF): bounds, perfect fit = 1.0.
"""
import math
import numpy as np
import pytest
import analysis.common as C


@pytest.mark.tier1
@pytest.mark.quick
def test_gini_perfect_equality():
    """Gini of large uniform distribution approaches 0.0."""
    x = np.ones(1000) * 50.0
    g = C.gini(x)
    assert math.isclose(g, 0.0, abs_tol=1e-4), f"Large uniform Gini should approach 0.0, got {g}"


@pytest.mark.tier1
@pytest.mark.quick
def test_gini_high_inequality():
    """Gini of extreme inequality distribution approaches 1.0."""
    x = np.zeros(1000)
    x[-1] = 1000.0
    g = C.gini(x)
    assert g > 0.95, f"Expected high Gini, got {g}"


@pytest.mark.tier1
@pytest.mark.quick
def test_gini_population_weighted():
    """Gini with population weights."""
    x = np.array([10.0, 20.0, 30.0])
    weights = np.array([1000.0, 2000.0, 3000.0])
    g = C.gini(x, weights=weights)
    assert 0.0 <= g <= 1.0, f"Gini must be bounded in [0, 1], got {g}"


@pytest.mark.tier1
@pytest.mark.quick
def test_gini_empty_or_zero_returns_nan():
    """Gini with empty or all-zero values returns NaN."""
    assert math.isnan(C.gini(np.array([])))
    assert math.isnan(C.gini(np.array([0.0, 0.0, 0.0])))


@pytest.mark.tier1
@pytest.mark.quick
def test_entropy_weights_sum_to_one():
    """Entropy weights across columns must always sum to 1.0."""
    matrix = np.array([
        [1.0, 10.0, 100.0],
        [2.0, 20.0, 50.0],
        [3.0, 15.0, 80.0],
        [4.0, 25.0, 60.0],
    ])
    w = C.entropy_weights(matrix)
    assert len(w) == 3
    assert math.isclose(w.sum(), 1.0, rel_tol=1e-5), f"Weights must sum to 1.0, got {w.sum()}"
    assert (w >= 0.0).all(), "Weights must be non-negative"


@pytest.mark.tier1
@pytest.mark.quick
def test_entropy_weights_uniform_input():
    """Uniform criteria matrix should produce equal weights (1/k)."""
    matrix = np.ones((5, 4))
    w = C.entropy_weights(matrix)
    assert len(w) == 4
    for weight in w:
        assert math.isclose(weight, 0.25, rel_tol=1e-4)


@pytest.mark.tier1
@pytest.mark.quick
def test_minmax_scaling():
    """MinMax scaler maps non-constant series into [0.0, 1.0]."""
    s = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    scaled = C.minmax(s)
    assert math.isclose(scaled[0], 0.0, abs_tol=1e-6)
    assert math.isclose(scaled[-1], 1.0, abs_tol=1e-6)
    assert math.isclose(scaled[2], 0.5, abs_tol=1e-6)


@pytest.mark.tier1
@pytest.mark.quick
def test_minmax_constant_input():
    """MinMax scaling of constant array should safely return zeros without dividing by zero."""
    s = np.array([42.0, 42.0, 42.0])
    scaled = C.minmax(s)
    assert (scaled == 0.0).all()


@pytest.mark.tier1
@pytest.mark.quick
def test_gvf_calculation():
    """Goodness of Variance Fit (GVF) produces valid metric <= 1.0."""
    values = np.array([1.0, 2.0, 2.5, 8.0, 9.0, 10.0])
    breaks = [1.0, 5.0, 10.0]
    gvf = C.goodness_of_variance_fit(values, breaks)
    assert 0.0 <= gvf <= 1.0, f"GVF must be in [0, 1], got {gvf}"
    assert gvf > 0.8, f"GVF should be high for well-separated clusters, got {gvf}"
