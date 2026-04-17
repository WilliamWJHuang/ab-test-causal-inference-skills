# Effect Size Interpretation Guide

## Why Effect Sizes Matter

P-values tell you IF there's an effect. Effect sizes tell you HOW BIG it is.
A tiny, meaningless effect can be "significant" with enough data.

## Common Effect Size Measures

### Cohen's d (Standardized Mean Difference)
`d = (M₁ - M₂) / SD_pooled`

| d | Interpretation |
|:---|:---|
| 0.2 | Small |
| 0.5 | Medium |
| 0.8 | Large |

### Odds Ratio (OR)
Used for binary outcomes (logistic regression, case-control studies).

| OR | Interpretation |
|:---|:---|
| < 0.5 or > 2.0 | Large |
| 0.5-0.67 or 1.5-2.0 | Medium |
| 0.67-0.83 or 1.2-1.5 | Small |

### Risk Ratio (RR) / Relative Risk
More interpretable than OR for common outcomes.

### R² / Explained Variance
| R² | Interpretation |
|:---|:---|
| 0.02 | Small |
| 0.13 | Medium |
| 0.26 | Large |

### η² (Eta-squared, for ANOVA)
Same guidelines as R².

## Converting Between Effect Sizes

```python
import numpy as np

def cohens_d_to_odds_ratio(d):
    """Convert Cohen's d to odds ratio (approximate)."""
    return np.exp(d * np.pi / np.sqrt(3))

def odds_ratio_to_cohens_d(or_val):
    """Convert odds ratio to Cohen's d (approximate)."""
    return np.log(or_val) * np.sqrt(3) / np.pi

def cohens_d_to_r(d):
    """Convert Cohen's d to Pearson's r."""
    return d / np.sqrt(d**2 + 4)
```

## Practical vs. Statistical Significance

ALWAYS discuss both:
1. **Statistical significance**: Is the effect unlikely to be due to chance?
2. **Practical significance**: Is the effect large enough to matter?

Example:
> "The new checkout flow increased conversion by 0.3 percentage points
> (from 5.0% to 5.3%, p = 0.02, Cohen's d = 0.04). While statistically
> significant, this is a very small effect (d = 0.04). At 10M monthly
> users, this translates to 30,000 additional conversions/month, which
> [is/is not] meaningful for the business."

## Reporting Template

Always report:
```
Effect: [value] [units]
95% CI: [lower, upper]
Effect size: [measure] = [value] ([interpretation])
p-value: [value] (test: [test name])
Practical significance: [assessment]
```
