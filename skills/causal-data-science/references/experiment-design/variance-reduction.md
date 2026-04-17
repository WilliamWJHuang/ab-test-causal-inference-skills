# Variance Reduction Reference Guide

## When to Read This

Read when the user needs to reduce experiment duration by reducing metric variance,
or when the experiment-designer Step 6 recommends variance reduction.

## CUPED (Controlled-experiment Using Pre-Experiment Data)

### Concept

Use pre-experiment values of the metric to reduce post-experiment variance.
If Y is the post-experiment metric and X is the pre-experiment metric:

```
Y_cuped = Y - θ × (X - E[X])
```

Where `θ = Cov(Y, X) / Var(X)` (the regression coefficient of Y on X).

### Variance Reduction

```
Var(Y_cuped) = Var(Y) × (1 - ρ²)
```

Where ρ is the correlation between pre- and post-experiment metric values.

| ρ (correlation) | Variance reduction | Sample size reduction |
|:---:|:---:|:---:|
| 0.3 | 9% | 9% |
| 0.5 | 25% | 25% |
| 0.7 | 51% | 51% |
| 0.9 | 81% | 81% |

### Implementation

```python
import numpy as np
import pandas as pd

def cuped_adjustment(df, metric_col, pre_metric_col, group_col):
    """
    Apply CUPED adjustment to an A/B test metric.

    Parameters
    ----------
    df : DataFrame
        Must contain columns for metric, pre-metric, and group assignment.
    metric_col : str
        Name of the post-experiment metric column.
    pre_metric_col : str
        Name of the pre-experiment metric column.
    group_col : str
        Name of the group assignment column (e.g., 'control', 'treatment').

    Returns
    -------
    DataFrame with adjusted metric and variance reduction estimate.
    """
    # Compute theta (regression coefficient)
    cov = np.cov(df[metric_col], df[pre_metric_col])
    theta = cov[0, 1] / cov[1, 1]

    # Adjust metric
    pre_mean = df[pre_metric_col].mean()
    df['metric_cuped'] = df[metric_col] - theta * (df[pre_metric_col] - pre_mean)

    # Compute correlation for reporting
    rho = np.corrcoef(df[metric_col], df[pre_metric_col])[0, 1]
    variance_reduction = rho ** 2

    # Compare original vs. CUPED variance
    original_var = df.groupby(group_col)[metric_col].var()
    cuped_var = df.groupby(group_col)['metric_cuped'].var()

    return {
        'theta': round(theta, 4),
        'correlation': round(rho, 4),
        'theoretical_variance_reduction': f"{variance_reduction:.1%}",
        'original_variance': original_var.to_dict(),
        'cuped_variance': cuped_var.to_dict(),
        'dataframe': df
    }
```

### Best Practices for CUPED

1. **Choice of covariate**: Use the SAME metric from the pre-experiment period.
   The higher the autocorrelation, the better the reduction.
2. **Pre-experiment window**: Use 1-4 weeks of pre-experiment data.
   Too short → noisy covariate. Too long → less relevant.
3. **New users**: CUPED doesn't work for users with no pre-experiment data.
   Analyze new and existing users separately.
4. **Multiple covariates**: Use regression adjustment with multiple pre-experiment features (CUPAC).

## CUPAC (Controlled-experiment Using Pre-experiment data to Adjust Currents)

An extension of CUPED that uses a machine learning model to predict the metric,
then uses the residual as the adjusted metric.

```python
from sklearn.ensemble import GradientBoostingRegressor

def cupac_adjustment(df, metric_col, feature_cols, group_col):
    """
    Apply CUPAC adjustment using ML-predicted control values.

    Parameters
    ----------
    df : DataFrame
    metric_col : str
        Post-experiment metric.
    feature_cols : list
        Pre-experiment features for prediction.
    group_col : str
        Group assignment column.
    """
    # Fit model on control group only
    control = df[df[group_col] == 'control']
    model = GradientBoostingRegressor(n_estimators=100, max_depth=3)
    model.fit(control[feature_cols], control[metric_col])

    # Predict for all users
    df['predicted'] = model.predict(df[feature_cols])
    df['metric_cupac'] = df[metric_col] - df['predicted']

    return df
```

## Stratified Randomization

Reduce variance by blocking on high-variance covariates before randomization.

**Variables to stratify on** (in order of impact):
1. Pre-experiment metric value (quintiles)
2. Platform (iOS / Android / Web)
3. Country or region
4. User tenure (new / returning)

```python
def stratified_analysis(df, metric_col, group_col, strata_cols):
    """
    Run stratified analysis (post-stratification).
    """
    from scipy.stats import ttest_ind
    import numpy as np

    results = []
    for name, stratum in df.groupby(strata_cols):
        control = stratum[stratum[group_col] == 'control'][metric_col]
        treatment = stratum[stratum[group_col] == 'treatment'][metric_col]
        if len(control) > 1 and len(treatment) > 1:
            t_stat, p_val = ttest_ind(treatment, control, equal_var=False)
            results.append({
                'stratum': name,
                'n_control': len(control),
                'n_treatment': len(treatment),
                'mean_control': control.mean(),
                'mean_treatment': treatment.mean(),
                'effect': treatment.mean() - control.mean(),
                't_stat': t_stat,
                'p_value': p_val
            })

    # Weighted average effect (population-weighted)
    total_n = sum(r['n_control'] + r['n_treatment'] for r in results)
    weighted_effect = sum(
        r['effect'] * (r['n_control'] + r['n_treatment']) / total_n
        for r in results
    )

    return {
        'strata_results': results,
        'overall_weighted_effect': weighted_effect
    }
```

## When NOT to Use Variance Reduction

- When you have plenty of traffic and a short experiment is fine
- When the pre-experiment covariate has low correlation with the metric (ρ < 0.2)
- When the metric is a rate with very low base rate (variance is already low)
- When you're running a Bayesian test (priors serve a similar purpose)
