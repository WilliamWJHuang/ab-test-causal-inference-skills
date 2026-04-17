# Matching and Weighting Methods Guide

## Matching Methods

### Propensity Score Matching (PSM)
1. Estimate propensity score: P(T=1|X) using logistic regression
2. Match treated to control units with similar propensity scores
3. Estimate effect on matched sample

### Coarsened Exact Matching (CEM)
1. Coarsen continuous covariates into bins
2. Exact match on coarsened values
3. Drop unmatched units
4. Use original (uncoarsened) data for analysis

### Nearest Neighbor Matching
Match each treated unit to the k closest control units (in covariate space).

## Weighting Methods

### Inverse Probability Weighting (IPW)
Weight observations by inverse of propensity score:
- Treated: w = 1/e(X)
- Control: w = 1/(1-e(X))

### Augmented IPW (AIPW / Doubly Robust)
Combines outcome regression + IPW. Consistent if EITHER model is correct.

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

def ipw_estimate(df, outcome_col, treatment_col, covariate_cols):
    """Estimate ATE using IPW."""
    # Estimate propensity score
    ps_model = LogisticRegression(max_iter=1000)
    ps_model.fit(df[covariate_cols], df[treatment_col])
    ps = ps_model.predict_proba(df[covariate_cols])[:, 1]

    # Trim extreme propensity scores
    ps = np.clip(ps, 0.01, 0.99)

    T = df[treatment_col].values
    Y = df[outcome_col].values

    # IPW estimator
    ate = np.mean(T * Y / ps - (1 - T) * Y / (1 - ps))

    return {'ate_ipw': ate, 'propensity_scores': ps}
```

## Mandatory Balance Checks

After matching/weighting, ALWAYS check covariate balance:
1. **Standardized mean differences** (SMD): Should be < 0.1 for all covariates
2. **Overlap/common support**: Trim non-overlapping regions
3. **Variance ratios**: Should be 0.5-2.0

## When Matching/Weighting Fails
- If balance cannot be achieved → the causal effect is not identifiable from this data
- If propensity scores cluster near 0 or 1 → positivity violation
- If key confounders are unmeasured → results are biased
