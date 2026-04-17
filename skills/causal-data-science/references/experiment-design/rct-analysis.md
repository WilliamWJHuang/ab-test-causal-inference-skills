# Analyzing Randomized Experiments

## When to Read This

Read when the user has COMPLETED a randomized experiment and needs to analyze the results,
or when the causal-inference-advisor decision tree reaches the "YES, randomly assigned" branch.

## Step 1: Check Data Integrity First

Before any analysis, run these checks:

### Sample Ratio Mismatch (SRM)
Compare actual vs. expected allocation using a chi-squared test:

```python
from scipy.stats import chisquare

def check_srm(n_control, n_treatment, expected_ratio=0.5):
    """
    Check for Sample Ratio Mismatch.
    If p < 0.001, the randomization may be broken — do NOT trust results.
    """
    total = n_control + n_treatment
    expected = [total * (1 - expected_ratio), total * expected_ratio]
    observed = [n_control, n_treatment]
    stat, p_value = chisquare(observed, expected)

    if p_value < 0.001:
        return {
            'status': 'FAIL',
            'message': f'SRM detected (p={p_value:.6f}). DO NOT analyze — investigate the pipeline.',
            'observed_ratio': n_treatment / total,
            'expected_ratio': expected_ratio
        }
    return {'status': 'PASS', 'p_value': p_value}
```

Common SRM causes: bot filtering applied unevenly, triggered experiment (users who never saw treatment are excluded from one arm), bucketing bugs.

### Covariate Balance
Even in an RCT, check that pre-treatment covariates are balanced:
```python
def check_balance(df, covariates, treatment_col):
    """Check standardized mean differences for each covariate."""
    from scipy.stats import ttest_ind
    results = []
    for cov in covariates:
        treated = df[df[treatment_col] == 1][cov]
        control = df[df[treatment_col] == 0][cov]
        pooled_std = ((treated.std()**2 + control.std()**2) / 2) ** 0.5
        smd = (treated.mean() - control.mean()) / pooled_std if pooled_std > 0 else 0
        results.append({'covariate': cov, 'smd': round(smd, 4), 'balanced': abs(smd) < 0.1})
    return results
```

If any covariate has SMD > 0.1, investigate. It's not necessarily wrong (randomization has variance), but large imbalances can reduce precision.

## Step 2: Choose the Estimator

### Simple Difference in Means (Neyman estimator)
The default. Unbiased for ATE under randomization.

```python
import numpy as np
from scipy.stats import ttest_ind

def neyman_estimator(y_treated, y_control):
    """
    Simple difference in means with Neyman (conservative) variance.
    Valid without any distributional assumptions in an RCT.
    """
    tau_hat = np.mean(y_treated) - np.mean(y_control)
    se = np.sqrt(np.var(y_treated, ddof=1) / len(y_treated) +
                 np.var(y_control, ddof=1) / len(y_control))
    ci_lower = tau_hat - 1.96 * se
    ci_upper = tau_hat + 1.96 * se

    return {
        'ate': round(tau_hat, 6),
        'se': round(se, 6),
        'ci_95': (round(ci_lower, 6), round(ci_upper, 6)),
        'relative_effect': round(tau_hat / np.mean(y_control), 4) if np.mean(y_control) != 0 else None
    }
```

### Regression with Covariates (Lin, 2013 estimator)
Adds pre-treatment covariates to improve precision. The Lin estimator interacts
all covariates with the treatment indicator, which ensures unbiased estimation
even if the model is misspecified:

```python
import statsmodels.formula.api as smf
import pandas as pd

def lin_estimator(df, outcome, treatment_col, covariates):
    """
    Lin (2013) estimator: fully interacted regression.
    More efficient than simple difference-in-means when covariates are predictive.

    Model: Y = a + tau*T + beta*X_centered + gamma*(T * X_centered) + e

    The coefficient on T gives the covariate-adjusted ATE.
    Use HC2 robust standard errors.
    """
    df = df.copy()
    # Center covariates (required for Lin estimator to be unbiased)
    for cov in covariates:
        df[f'{cov}_c'] = df[cov] - df[cov].mean()

    centered_covs = [f'{cov}_c' for cov in covariates]
    interactions = [f'{treatment_col}:{cov}_c' for cov in covariates]

    formula = f'{outcome} ~ {treatment_col} + {" + ".join(centered_covs)} + {" + ".join(interactions)}'
    model = smf.ols(formula, data=df).fit(cov_type='HC2')  # HC2 for RCT

    ate = model.params[treatment_col]
    se = model.bse[treatment_col]
    ci = model.conf_int().loc[treatment_col]

    return {
        'ate': round(ate, 6),
        'se': round(se, 6),
        'ci_95': (round(ci[0], 6), round(ci[1], 6)),
        'p_value': round(model.pvalues[treatment_col], 6),
        'precision_gain': 'Compare SE to Neyman SE to see improvement'
    }
```

**When to use which:**
- Simple difference: always valid, easy to explain, good default
- Lin estimator: when you have predictive pre-treatment covariates and want tighter CIs. Never hurts asymptotically, can help a lot.
- CUPED: operationally similar to Lin; see `variance-reduction.md`

## Step 3: Handle Non-Compliance

If some users assigned to treatment didn't actually receive it (or vice versa):

### Intention-to-Treat (ITT)
Analyze based on ASSIGNMENT, not actual treatment received.
- Always valid (preserves randomization)
- Underestimates the effect of actually receiving treatment
- Standard for regulatory/clinical settings

### Per-Protocol Analysis
Analyze only users who complied — BIASED because compliance is self-selected.
Only use as a sensitivity check, never as the primary analysis.

### LATE / Complier Average Causal Effect
Use assignment as an INSTRUMENT for actual treatment received:
```python
def late_estimator(df, outcome, assignment_col, treatment_col):
    """
    LATE: Local Average Treatment Effect for compliers.
    Uses random assignment as IV for actual treatment.
    """
    from linearmodels.iv import IV2SLS

    df['const'] = 1
    model = IV2SLS(
        dependent=df[outcome],
        exog=df[['const']],
        endog=df[treatment_col],
        instruments=df[assignment_col]
    )
    result = model.fit(cov_type='robust')

    return {
        'late': result.params[treatment_col],
        'se': result.std_errors[treatment_col],
        'interpretation': 'Effect on COMPLIERS only (those who take treatment when assigned)'
    }
```

**Decision rule:**
- Report ITT as primary (always valid)
- Report LATE as secondary if non-compliance is substantial (>5%)
- Mention the compliance rate and which population LATE applies to

## Step 4: Report Results

### Required elements:
1. **Point estimate** (absolute and relative)
2. **95% confidence interval**
3. **Standard error** and test used
4. **Sample sizes** per arm
5. **SRM check** result
6. **Whether covariates were used** and which ones
7. **Non-compliance rate** if applicable
8. **Practical significance** — is the effect large enough to matter?

### Template:
```
Treatment increased [metric] by [X] units ([Y]% relative change).
95% CI: [lower, upper]. p = [value] (Lin estimator with HC2 SEs).
N_control = [n], N_treatment = [n]. SRM check: passed.
Covariate adjustment: [covariates used].
Non-compliance: [X]% of assigned users did not receive treatment.
ITT effect: [Z]. LATE (complier effect): [W].
```
