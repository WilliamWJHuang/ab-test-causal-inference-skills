# Heterogeneous Treatment Effect (HTE) Estimation Guide

## Purpose

HTE/CATE estimation answers: "For WHOM does the treatment work best?"
instead of just "Does the treatment work on average?"

## Meta-Learner Approaches

### S-Learner (Single Model)
Train ONE model on all data with treatment as a feature.
CATE(x) = μ(x, T=1) - μ(x, T=0)

- **Pro**: Simple, uses all data
- **Con**: Tends to shrink HTEs toward zero (regularization bias)
- **Use when**: You expect few effect modifiers

### T-Learner (Two Models)
Train SEPARATE models for treatment and control.
CATE(x) = μ₁(x) - μ₀(x)

- **Pro**: No regularization bias on treatment effect
- **Con**: Doubles variance; poor with small samples in one group
- **Use when**: Treatment and control have different relationships with X

### X-Learner (Cross)
1. Train separate models (like T-learner)
2. Impute individual treatment effects
3. Train final CATE model on imputed effects, weighted by propensity

- **Pro**: Best with imbalanced treatment/control sizes
- **Con**: More complex, requires propensity score estimation
- **Use when**: Treatment group is much smaller than control

### DR-Learner (Doubly Robust)
Combines outcome modeling + propensity scoring for robustness.
Most robust to model misspecification.

- **Pro**: Doubly robust — consistent if EITHER model is correct
- **Con**: Can be unstable with extreme propensity scores
- **Use when**: You want the most defensible estimates

```python
from econml.dml import CausalForestDML
from econml.dr import DRLearner
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier

def estimate_cate(df, outcome_col, treatment_col, feature_cols, method='dr_learner'):
    """
    Estimate Conditional Average Treatment Effects (CATE).
    """
    Y = df[outcome_col].values
    T = df[treatment_col].values
    X = df[feature_cols].values

    if method == 'causal_forest':
        model = CausalForestDML(
            model_y=GradientBoostingRegressor(n_estimators=100),
            model_t=GradientBoostingClassifier(n_estimators=100),
            n_estimators=1000,
            random_state=42
        )
    elif method == 'dr_learner':
        model = DRLearner(
            model_regression=GradientBoostingRegressor(n_estimators=100),
            model_propensity=GradientBoostingClassifier(n_estimators=100),
            model_final=GradientBoostingRegressor(n_estimators=100)
        )

    model.fit(Y, T, X=X)

    # Get CATE estimates
    cate_estimates = model.effect(X)
    cate_intervals = model.effect_interval(X, alpha=0.05)

    return {
        'cate_mean': cate_estimates.mean(),
        'cate_std': cate_estimates.std(),
        'cate_by_observation': cate_estimates,
        'ci_lower': cate_intervals[0],
        'ci_upper': cate_intervals[1]
    }
```

## Causal Forest (Generalized Random Forest)

Non-parametric approach that adapts to the data structure.

- **Pro**: Adaptive, handles non-linearity, provides valid confidence intervals
- **Con**: Requires larger samples, can be slow
- **Use when**: You have many potential effect modifiers and no strong prior

## Best Practices

1. **Always report ATE alongside HTE** — HTE is meaningless without the overall effect
2. **Pre-specify subgroups** — Don't fish for heterogeneity after seeing data
3. **Use honest estimation** — Split data into estimation and inference sets
4. **Report confidence intervals** for CATE estimates
5. **Validate with held-out data** — Do subgroup effects replicate?
