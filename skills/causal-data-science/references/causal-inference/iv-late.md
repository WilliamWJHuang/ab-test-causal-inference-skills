# Instrumental Variables (IV) and LATE Guide

## When to Use
- Treatment assignment is NOT random (endogeneity)
- BUT you have a variable (instrument Z) that affects treatment but not the outcome directly

## The IV Setup
- **Z (Instrument)** → affects **D (Treatment)** → affects **Y (Outcome)**
- Z must NOT directly affect Y (exclusion restriction)

## Three Key Assumptions
1. **Relevance**: Z is correlated with D (first-stage F > 10)
2. **Exclusion restriction**: Z affects Y ONLY through D (untestable — requires theory)
3. **Monotonicity**: Z doesn't make anyone LESS likely to take treatment (for LATE)

## Implementation (2SLS)

```python
from linearmodels.iv import IV2SLS
import pandas as pd

def two_stage_least_squares(df, outcome, treatment, instrument, controls=None):
    """Run 2SLS IV regression."""
    exog = ['const']
    if controls:
        exog += controls

    df['const'] = 1

    model = IV2SLS(
        dependent=df[outcome],
        exog=df[exog],
        endog=df[treatment],
        instruments=df[instrument]
    )
    result = model.fit(cov_type='robust')
    print(result.summary)
    return result
```

## Diagnostics
1. **First-stage F-statistic**: Must be > 10 (Staiger & Stock rule)
2. **Weak instrument test**: If F < 10, IV estimates are unreliable and biased
3. **Overidentification test** (Sargan/Hansen): If >1 instrument, test exclusion restriction
4. **Hausman test**: Compare OLS vs. IV — if different, endogeneity is present

## What IV Estimates: LATE
IV estimates the Local Average Treatment Effect — the effect for COMPLIERS only
(those whose treatment changes because of the instrument).

LATE ≠ ATE. It is LIMITED to the compliant subpopulation.

## Common Applications
- **RCT with non-compliance**: Random assignment as instrument for actual treatment
- **Distance as instrument**: Distance to facility as instrument for facility use
- **Policy variation**: Regulatory changes as instrument for firm behavior

## RDD as a Special Case of IV

Regression Discontinuity Design (RDD) can be viewed as IV where the instrument
is the indicator for being above/below the cutoff.

See `references/rdd-guide.md` for dedicated RDD guidance.
