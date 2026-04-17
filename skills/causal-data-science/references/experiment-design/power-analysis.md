# Power Analysis Reference Guide

## When to Read This

Read when `experiment-designer` reaches Step 4 (Power Analysis) and the user needs
detailed formulas, advanced scenarios, or implementation guidance.

## Standard Two-Sample Test (Means)

### Formula

```
n = ((z_α/2 + z_β)² × 2σ²) / δ²
```

Where:
- `n` = sample size per arm
- `z_α/2` = critical value for significance level (1.96 for α=0.05 two-sided)
- `z_β` = critical value for power (0.84 for 80% power)
- `σ²` = variance of the metric
- `δ` = minimum detectable effect (MDE)

### Python Implementation

```python
from scipy import stats
import numpy as np

def sample_size_two_means(baseline_mean, baseline_std, mde_relative,
                          alpha=0.05, power=0.80, two_sided=True):
    """
    Calculate sample size for a two-sample t-test.

    Parameters
    ----------
    baseline_mean : float
        Historical mean of the metric.
    baseline_std : float
        Historical standard deviation of the metric.
    mde_relative : float
        Minimum detectable effect as relative change (e.g., 0.05 for 5%).
    alpha : float
        Significance level (default 0.05).
    power : float
        Statistical power (default 0.80).
    two_sided : bool
        Whether to use a two-sided test (default True).

    Returns
    -------
    dict with n_per_arm, total_n, mde_absolute, and duration estimate.
    """
    mde_absolute = baseline_mean * mde_relative
    effect_size = mde_absolute / baseline_std  # Cohen's d

    from statsmodels.stats.power import TTestIndPower
    analysis = TTestIndPower()
    n_per_arm = analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative='two-sided' if two_sided else 'larger'
    )

    return {
        'n_per_arm': int(np.ceil(n_per_arm)),
        'total_n': int(np.ceil(n_per_arm)) * 2,
        'mde_absolute': mde_absolute,
        'mde_relative': mde_relative,
        'cohens_d': effect_size,
        'alpha': alpha,
        'power': power
    }
```

## Two-Sample Test (Proportions)

### Formula

```
n = ((z_α/2 + z_β)² × (p₁(1-p₁) + p₂(1-p₂))) / (p₁ - p₂)²
```

### Python Implementation

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
import numpy as np

def sample_size_two_proportions(baseline_rate, mde_relative,
                                 alpha=0.05, power=0.80):
    """
    Calculate sample size for a two-proportion z-test.

    Parameters
    ----------
    baseline_rate : float
        Baseline conversion rate (e.g., 0.10 for 10%).
    mde_relative : float
        Minimum detectable relative change (e.g., 0.05 for 5% relative lift).
    """
    new_rate = baseline_rate * (1 + mde_relative)
    effect_size = proportion_effectsize(new_rate, baseline_rate)

    analysis = NormalIndPower()
    n_per_arm = analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative='two-sided'
    )

    return {
        'n_per_arm': int(np.ceil(n_per_arm)),
        'total_n': int(np.ceil(n_per_arm)) * 2,
        'baseline_rate': baseline_rate,
        'expected_rate': new_rate,
        'mde_relative': mde_relative,
        'mde_absolute': new_rate - baseline_rate
    }
```

## Cluster Randomized Designs

When units are clustered (e.g., geo-randomization, classroom experiments):

```
n_effective = n / (1 + (m-1) × ICC)
```

Where:
- `n` = total observations
- `m` = average cluster size
- `ICC` = intra-cluster correlation coefficient

The design effect `(1 + (m-1) × ICC)` inflates the required sample size.
Typical ICC values: 0.01-0.05 for online experiments, 0.10-0.30 for educational studies.

## CUPED-Adjusted Power

With CUPED (Controlled-experiment Using Pre-Experiment Data), the effective variance is:

```
σ²_cuped = σ² × (1 - ρ²)
```

Where `ρ` is the correlation between pre- and post-experiment metric values.

This reduces required sample size by factor `(1 - ρ²)`.
Typical values: ρ = 0.5 → 25% reduction, ρ = 0.7 → 51% reduction.

## Duration Estimation

```python
def experiment_duration(n_total, daily_traffic, allocation_fraction=1.0):
    """
    Estimate how long an experiment needs to run.

    Parameters
    ----------
    n_total : int
        Total required sample size (both arms).
    daily_traffic : int
        Number of eligible users per day.
    allocation_fraction : float
        Fraction of traffic in the experiment (default 1.0 = 100%).
    """
    effective_daily = daily_traffic * allocation_fraction
    days = int(np.ceil(n_total / effective_daily))

    return {
        'days': days,
        'weeks': round(days / 7, 1),
        'warning': '⚠️ >90 days — consider increasing MDE or using CUPED' if days > 90 else None
    }
```

## Common Pitfalls

1. **Using sample standard deviation when you should use the standard error**: SD measures variability in the data, SE measures variability in the estimate.
2. **Forgetting to account for clustering**: Ignoring ICC in clustered designs dramatically underestimates required sample size.
3. **Powering for the wrong metric**: Power the PRIMARY metric only. Secondary metrics are exploratory.
4. **Post-hoc power**: Computing power AFTER seeing the results is meaningless. Power is a design-stage tool.
