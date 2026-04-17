# Sequential Testing Reference Guide

## When to Read This

Read when the user chooses "sequential testing" in Step 2 of `experiment-designer`,
or says they want to "peek at results early" or "stop early if winning."

## Why Sequential Testing?

Fixed-horizon tests require waiting until the full sample size is collected.
Sequential tests allow **valid early stopping** while controlling Type I error.

## Methods

### 1. Group Sequential Testing (GST)

The classical approach. Pre-specify K interim analyses and adjust critical values.

**Spending functions:**
- **O'Brien-Fleming**: Conservative early, aggressive late (recommended default)
- **Pocock**: Equal alpha at each look (more aggressive early)
- **α-spending**: Customize alpha allocation across looks

```python
from statsmodels.stats.proportion import proportions_ztest
import numpy as np

def obrien_fleming_boundaries(alpha, n_looks):
    """
    Compute O'Brien-Fleming critical values for K equally-spaced looks.

    Returns z-critical values for each interim analysis.
    """
    from scipy.stats import norm
    boundaries = []
    for k in range(1, n_looks + 1):
        info_fraction = k / n_looks
        z_crit = norm.ppf(1 - alpha / 2) / np.sqrt(info_fraction)
        boundaries.append({
            'look': k,
            'info_fraction': round(info_fraction, 2),
            'z_critical': round(z_crit, 3),
            'p_critical': round(2 * (1 - norm.cdf(z_crit)), 6)
        })
    return boundaries
```

**Key rule**: You MUST pre-specify the number of looks and the spending function
BEFORE the experiment starts. You cannot decide to add more looks mid-experiment.

### 2. Always-Valid P-values / Anytime-Valid Inference

Modern approach that allows **continuous monitoring** without pre-specifying looks.

**Methods:**
- **mSPRT (mixture Sequential Probability Ratio Test)**
- **Confidence sequences** (always-valid confidence intervals)
- **E-values** (safe testing)

```python
def always_valid_p_value(z_stat, n, n_min=100, mixing_rate=None):
    """
    Compute an always-valid p-value using the mSPRT approach.

    Parameters
    ----------
    z_stat : float
        Current z-statistic.
    n : int
        Current sample size per arm.
    n_min : int
        Minimum sample size before monitoring begins.
    mixing_rate : float
        Variance of the mixing distribution (default: auto-calibrated).
    """
    if n < n_min:
        return 1.0  # Not enough data yet

    if mixing_rate is None:
        mixing_rate = 1 / n_min  # Auto-calibrate

    # mSPRT likelihood ratio
    from scipy.stats import norm
    import numpy as np
    lambda_stat = np.sqrt(1 / (1 + n * mixing_rate)) * np.exp(
        (n * mixing_rate * z_stat**2) / (2 * (1 + n * mixing_rate))
    )

    p_value = min(1.0, 1 / lambda_stat)
    return p_value
```

**Advantages over GST:**
- No need to pre-specify number of looks
- Can monitor continuously
- Valid at any stopping time

**Disadvantages:**
- Slightly less powerful than GST for a fixed number of looks
- Less intuitive to explain to stakeholders

### 3. Bayesian Stopping Rules

Use posterior probabilities to make decisions.

**Decision rule**: Stop when P(treatment > control | data) > threshold (e.g., 0.95)
or P(treatment > control | data) < 1 - threshold (futility).

```python
def bayesian_ab_test(successes_a, total_a, successes_b, total_b,
                     prior_alpha=1, prior_beta=1, n_simulations=100000):
    """
    Bayesian A/B test using Beta-Binomial model.

    Returns probability that B is better than A.
    """
    import numpy as np

    # Posterior distributions (Beta)
    alpha_a = prior_alpha + successes_a
    beta_a = prior_beta + total_a - successes_a
    alpha_b = prior_alpha + successes_b
    beta_b = prior_beta + total_b - successes_b

    # Monte Carlo simulation
    samples_a = np.random.beta(alpha_a, beta_a, n_simulations)
    samples_b = np.random.beta(alpha_b, beta_b, n_simulations)

    prob_b_better = np.mean(samples_b > samples_a)
    expected_lift = np.mean((samples_b - samples_a) / samples_a)

    return {
        'prob_b_better': round(prob_b_better, 4),
        'expected_lift': round(expected_lift, 4),
        'credible_interval_lift': (
            round(np.percentile((samples_b - samples_a) / samples_a, 2.5), 4),
            round(np.percentile((samples_b - samples_a) / samples_a, 97.5), 4)
        ),
        'recommendation': (
            '✅ Ship B' if prob_b_better > 0.95 else
            '❌ Keep A' if prob_b_better < 0.05 else
            '⏳ Continue experiment'
        )
    }
```

## Choosing a Method

| Criterion | Fixed-Horizon | GST | Always-Valid | Bayesian |
|:---|:---:|:---:|:---:|:---:|
| Pre-specify # looks | N/A | ✅ Required | ❌ Not needed | ❌ Not needed |
| Continuous monitoring | ❌ | ❌ | ✅ | ✅ |
| Frequentist guarantees | ✅ | ✅ | ✅ | ❌ |
| Interpretability | High | Medium | Low | High |
| Statistical power | Best | Good | Good | Good |

**Default recommendation**: Start with **fixed-horizon** for simple experiments.
Use **GST** (O'Brien-Fleming) if you need 2-5 planned interim looks.
Use **always-valid** if you need continuous monitoring.
Use **Bayesian** if stakeholders prefer probability statements over p-values.
