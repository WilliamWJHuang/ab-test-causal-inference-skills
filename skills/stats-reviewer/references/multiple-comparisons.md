# Multiple Comparisons Reference

## The Problem

When you test N hypotheses at α = 0.05, the probability of at least one false
positive is: 1 - (1 - 0.05)^N

| N tests | P(at least one false positive) |
|:---:|:---:|
| 1 | 5.0% |
| 5 | 22.6% |
| 10 | 40.1% |
| 20 | 64.2% |
| 100 | 99.4% |

## Correction Methods

### 1. Bonferroni (most conservative)
Adjusted α = α / N

- **Use when**: Tests are independent and you need strong FWER control
- **Problem**: Very conservative; high false negative rate

### 2. Holm (step-down)
Order p-values from smallest to largest. Reject p(i) < α / (N - i + 1)

- **Use when**: You want FWER control but less conservative than Bonferroni
- **Always preferred over Bonferroni** (uniformly more powerful)

### 3. Benjamini-Hochberg (FDR)
Controls the expected proportion of false discoveries among rejections.
Order p-values. Reject p(i) < (i/N) × α

- **Use when**: Many tests, OK with some false discoveries
- **Standard for**: Genomics, large-scale screening, exploratory analyses

```python
from statsmodels.stats.multitest import multipletests

def correct_multiple_tests(p_values, method='fdr_bh', alpha=0.05):
    """
    Apply multiple testing correction.

    Methods: 'bonferroni', 'holm', 'fdr_bh' (Benjamini-Hochberg),
             'fdr_by' (Benjamini-Yekutieli)
    """
    reject, p_adjusted, _, _ = multipletests(p_values, alpha=alpha, method=method)

    return {
        'reject': reject.tolist(),
        'p_adjusted': p_adjusted.tolist(),
        'method': method,
        'n_rejected': sum(reject),
        'n_tests': len(p_values)
    }
```

## Which Method to Use?

| Scenario | Recommended Method |
|:---|:---|
| 2-5 pre-specified comparisons | Holm |
| Many exploratory comparisons | BH-FDR |
| High-stakes, need to avoid ANY false positive | Bonferroni or Holm |
| Primary + secondary metrics in A/B test | No correction for primary; BH-FDR for secondary |

## The "Garden of Forking Paths"

Even with ONE hypothesis test, implicit multiplicity arises from:
- Choosing which variables to include/exclude
- Choosing how to define subgroups
- Choosing outlier exclusion criteria
- Choosing the functional form
- Choosing the time window

**Mitigation**: Pre-registration. Specify all analysis decisions before seeing data.

## When Correction is NOT Needed

- Different research questions analyzed on different datasets
- Purely exploratory/descriptive analyses (clearly labeled as such)
- Pre-specified primary metric in an A/B test (single confirmatory test)
