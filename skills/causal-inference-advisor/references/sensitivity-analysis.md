# Sensitivity Analysis for Unmeasured Confounding

## Purpose

No observational study can rule out unmeasured confounding.
Sensitivity analysis quantifies: "How strong would hidden bias need to be to
explain away the observed effect?"

## Methods

### 1. E-value (VanderWeele & Ding, 2017)

The E-value is the minimum strength of association (on the risk ratio scale)
that an unmeasured confounder would need to have with BOTH the treatment AND
the outcome to fully explain away the observed effect.

```python
import numpy as np

def compute_e_value(point_estimate, ci_lower=None, estimate_type='risk_ratio'):
    """
    Compute the E-value for sensitivity analysis.

    Parameters
    ----------
    point_estimate : float
        The observed effect estimate.
    ci_lower : float, optional
        Lower bound of CI (for E-value of CI bound).
    estimate_type : str
        'risk_ratio', 'odds_ratio', 'hazard_ratio', or 'cohens_d'
    """
    # Convert to risk ratio scale if needed
    if estimate_type == 'odds_ratio':
        rr = odds_ratio_to_rr_approx(point_estimate)
    elif estimate_type == 'cohens_d':
        rr = np.exp(0.91 * point_estimate)
    elif estimate_type == 'hazard_ratio':
        rr = point_estimate  # Approximate
    else:
        rr = point_estimate

    # Ensure RR > 1 (flip if protective)
    if rr < 1:
        rr = 1 / rr

    e_value = rr + np.sqrt(rr * (rr - 1))

    result = {'e_value_point': round(e_value, 2)}

    if ci_lower is not None:
        ci_rr = ci_lower if ci_lower > 1 else 1 / ci_lower
        if ci_rr <= 1:
            result['e_value_ci'] = 1.0  # CI includes null
        else:
            result['e_value_ci'] = round(ci_rr + np.sqrt(ci_rr * (ci_rr - 1)), 2)

    return result

def odds_ratio_to_rr_approx(or_val, baseline_risk=0.1):
    """Convert odds ratio to approximate risk ratio (rare disease assumption)."""
    return or_val / (1 - baseline_risk + baseline_risk * or_val)
```

**Interpretation**: An E-value of 3.5 means an unmeasured confounder would need
to be associated with both treatment and outcome by a risk ratio of at least 3.5
to explain away the effect. If no known confounder has this strength, the result
is robust.

### 2. Rosenbaum Bounds (for matched studies)

Quantifies sensitivity to hidden bias in matched observational studies.

The sensitivity parameter Γ represents the maximum ratio of treatment odds
for two matched subjects:

```python
def rosenbaum_bounds(matched_data, outcome_col, gamma_range=None):
    """
    Compute Rosenbaum bounds for a matched-pair study.

    Parameters
    ----------
    matched_data : DataFrame
        Must have columns: pair_id, treated (0/1), outcome.
    gamma_range : list
        Range of Gamma values to test (default [1.0, 1.5, 2.0, 2.5, 3.0]).
    """
    if gamma_range is None:
        gamma_range = [1.0, 1.5, 2.0, 2.5, 3.0]

    from scipy.stats import norm
    import numpy as np

    results = []
    for gamma in gamma_range:
        # Compute upper bound p-value under gamma
        # (simplified; for exact implementation use the sensitivity2x2xk or rbounds package)
        results.append({
            'gamma': gamma,
            'interpretation': (
                f"If hidden bias could make one matched subject "
                f"{gamma}x more likely to be treated, the p-value "
                f"upper bound is [compute]"
            )
        })

    return results
```

### 3. Bias-Adjusted Estimates (Oster, 2019)

For linear regression, estimate how much selection on unobservables relative to
observables would be needed to explain away the result.

The key parameter is δ (delta): the ratio of selection on unobservables to
selection on observables. δ = 1 means equal selection.

```python
def oster_bound(beta_unrestricted, r_sq_unrestricted,
                beta_restricted, r_sq_restricted, r_sq_max=1.0):
    """
    Compute Oster (2019) bias-adjusted treatment effect.

    Parameters
    ----------
    beta_unrestricted : float
        Coefficient from regression WITH controls.
    r_sq_unrestricted : float
        R² from regression WITH controls.
    beta_restricted : float
        Coefficient from regression WITHOUT controls.
    r_sq_restricted : float
        R² from regression WITHOUT controls.
    r_sq_max : float
        Maximum possible R² (default 1.0; Oster recommends 1.3 × R²_full).
    """
    # Bias-adjusted beta at delta = 1
    numerator = (beta_unrestricted * (r_sq_max - r_sq_unrestricted) -
                 beta_restricted * (r_sq_max - r_sq_restricted))
    denominator = r_sq_unrestricted - r_sq_restricted

    if denominator == 0:
        return {'error': 'R² values are identical; cannot compute bound'}

    beta_adjusted = beta_unrestricted - numerator / denominator

    # Compute delta that would make beta = 0
    if beta_unrestricted != 0:
        delta_zero = (beta_unrestricted * (r_sq_max - r_sq_unrestricted)) / (
            (beta_restricted - beta_unrestricted) * (r_sq_unrestricted - r_sq_restricted)
        )
    else:
        delta_zero = 0

    return {
        'beta_adjusted_delta1': round(beta_adjusted, 4),
        'delta_to_zero': round(delta_zero, 4),
        'interpretation': (
            f"At δ=1 (equal selection), adjusted β = {beta_adjusted:.4f}. "
            f"δ would need to be {delta_zero:.2f} to explain away the effect."
        )
    }
```

## Reporting Sensitivity Analysis

Always report:
1. The method used (E-value, Rosenbaum, Oster)
2. The threshold value (how strong would confounding need to be?)
3. Comparison to known confounders (is this plausible?)
4. Conclusion about robustness

Example:
> "The E-value for the point estimate is 3.2, and for the confidence interval
> lower bound is 1.8. The strongest known confounder (age) has an association
> of RR = 1.5 with both treatment and outcome. Since 1.5 < 1.8, our estimate
> is robust to confounding as strong as age."
