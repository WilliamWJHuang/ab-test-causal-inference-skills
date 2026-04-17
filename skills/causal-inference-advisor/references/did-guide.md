# Difference-in-Differences (DiD) Guide

## Setup

DiD requires panel data with:
- **Treatment group**: Units exposed to the intervention
- **Control group**: Units NOT exposed
- **Pre-period**: Observations before the intervention
- **Post-period**: Observations after the intervention

## The DiD Estimator

```
τ_DiD = (Ȳ_treatment_post - Ȳ_treatment_pre) - (Ȳ_control_post - Ȳ_control_pre)
```

### Regression Implementation

```python
import statsmodels.formula.api as smf

def did_regression(df, outcome, treatment_col, post_col, covariates=None):
    """
    Run a Difference-in-Differences regression.

    Parameters
    ----------
    df : DataFrame
    outcome : str - name of the outcome variable
    treatment_col : str - binary indicator (1 = treated unit)
    post_col : str - binary indicator (1 = post-treatment period)
    covariates : list - optional control variables
    """
    formula = f'{outcome} ~ {treatment_col} * {post_col}'
    if covariates:
        formula += ' + ' + ' + '.join(covariates)

    model = smf.ols(formula, data=df).fit(cov_type='cluster',
                                           cov_kwds={'groups': df['unit_id']})
    print(model.summary())

    did_effect = model.params[f'{treatment_col}:{post_col}']
    did_se = model.bse[f'{treatment_col}:{post_col}']
    did_p = model.pvalues[f'{treatment_col}:{post_col}']

    return {
        'effect': did_effect,
        'se': did_se,
        'p_value': did_p,
        'ci_lower': did_effect - 1.96 * did_se,
        'ci_upper': did_effect + 1.96 * did_se
    }
```

## Assumption Checks

### 1. Parallel Trends (CRITICAL)

Plot pre-treatment trends for treatment and control groups. They should move together.

```python
import matplotlib.pyplot as plt

def plot_parallel_trends(df, time_col, outcome, treatment_col, treatment_time):
    """Plot pre-treatment trends to visually assess parallel trends assumption."""
    for group in [0, 1]:
        group_data = df[df[treatment_col] == group].groupby(time_col)[outcome].mean()
        label = 'Treatment' if group == 1 else 'Control'
        plt.plot(group_data.index, group_data.values, label=label, marker='o')

    plt.axvline(x=treatment_time, color='red', linestyle='--', label='Treatment')
    plt.xlabel('Time')
    plt.ylabel(outcome)
    plt.legend()
    plt.title('Parallel Trends Check')
    plt.show()
```

**Formal test**: Run a regression with leads (pre-treatment treatment-time interactions).
All lead coefficients should be ~0 and non-significant.

### 2. No Anticipation

Units should not change behavior in anticipation of treatment.
Check: Are there effects in the periods just before treatment?

### 3. SUTVA (Stable Unit Treatment Value Assumption)

Treatment of one unit should not affect outcomes of other units.
Violations: spillover effects, network effects, market-level effects.

### 4. No Compositional Changes

The composition of treatment/control groups should not change over time.

## Staggered DiD

When different units adopt treatment at different times:

```python
# Use the Callaway-Sant'Anna estimator for staggered adoption
# pip install csdid
# Or use the Sun-Abraham interaction-weighted estimator

def staggered_did_warning():
    """
    WARNING: Standard two-way fixed effects (TWFE) with staggered adoption
    produces BIASED estimates due to negative weighting of already-treated units.

    Use one of these modern estimators instead:
    - Callaway & Sant'Anna (2021): Group-time ATTs
    - Sun & Abraham (2021): Interaction-weighted estimator
    - de Chaisemartin & D'Haultfoeuille (2020): Fuzzy DiD
    - Borusyak, Jaravel & Spiess (2024): Imputation estimator
    """
    pass
```

## Common Mistakes

- NEVER use TWFE with staggered adoption — use modern estimators
- NEVER skip the parallel trends plot
- NEVER claim causal effects if pre-trends are not parallel
- ALWAYS cluster standard errors at the unit level (not observation level)
