# Regression Discontinuity Design (RDD) Guide

## When to Use
- Treatment is assigned based on whether a "running variable" exceeds a threshold
- Examples: scholarship if GPA > 3.5, subsidy if income < $50k, policy if age > 18

## Types
- **Sharp RDD**: Treatment switches from 0 to 1 exactly at the cutoff
- **Fuzzy RDD**: Probability of treatment changes at the cutoff (→ use IV at cutoff)

## Implementation

```python
from rdrobust import rdrobust

def run_rdd(df, outcome_col, running_var_col, cutoff=0):
    """Run RDD using local polynomial regression."""
    result = rdrobust(
        y=df[outcome_col],
        x=df[running_var_col],
        c=cutoff
    )
    print(result)
    return result
```

## Key Checks
1. **McCrary density test**: Test for manipulation of running variable near cutoff
2. **Covariate balance at cutoff**: Pre-treatment covariates should be smooth at cutoff
3. **Bandwidth sensitivity**: Results should be robust to different bandwidths
4. **Placebo cutoffs**: No effect at fake cutoffs away from the true one

## Limitations
- Estimates are LOCAL to the cutoff — may not generalize
- Requires sufficient density of observations near the cutoff
- Cannot handle manipulation of the running variable
