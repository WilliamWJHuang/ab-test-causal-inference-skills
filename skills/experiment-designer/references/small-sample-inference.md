# Small-Sample and Randomization-Based Inference

## When to Read This

Read when:
- The experiment has fewer than ~200 units per arm
- The metric distribution is heavily skewed or non-normal
- The user wants exact p-values rather than asymptotic approximations
- Standard large-sample methods may not be reliable

## Randomization-Based (Fisherian) Inference

### The Key Idea

In a randomized experiment, the randomization itself generates the reference
distribution for inference. You don't need to assume the data come from a
normal distribution or invoke the CLT.

**Fisher's sharp null**: H₀ says treatment has NO effect on ANY unit.
Under this null, every unit's outcome is fixed no matter what treatment it received.
This means you can simulate what WOULD have happened under every possible
randomization and compare the actual result to that distribution.

### Permutation Test (the workhorse)

```python
import numpy as np

def permutation_test(y_treated, y_control, n_permutations=10000, seed=42):
    """
    Permutation test for difference in means.
    Valid for ANY sample size, ANY distribution.
    No normality assumption required.

    Returns exact (Monte Carlo) p-value.
    """
    rng = np.random.RandomState(seed)
    observed_diff = np.mean(y_treated) - np.mean(y_control)

    combined = np.concatenate([y_treated, y_control])
    n_t = len(y_treated)
    count_extreme = 0

    for _ in range(n_permutations):
        perm = rng.permutation(combined)
        perm_diff = np.mean(perm[:n_t]) - np.mean(perm[n_t:])
        if abs(perm_diff) >= abs(observed_diff):
            count_extreme += 1

    p_value = count_extreme / n_permutations
    return {
        'observed_difference': round(observed_diff, 6),
        'p_value': round(p_value, 4),
        'n_permutations': n_permutations,
        'method': 'Two-sided permutation test',
        'note': 'Exact test — no distributional assumptions'
    }
```

### Fisher Exact Test (for 2x2 tables)

When the outcome is binary and both groups are small:

```python
from scipy.stats import fisher_exact

def binary_outcome_test(successes_t, n_t, successes_c, n_c):
    """
    Fisher exact test for binary outcomes in small samples.
    Use instead of chi-squared when any expected cell < 5.
    """
    table = [[successes_t, n_t - successes_t],
             [successes_c, n_c - successes_c]]
    odds_ratio, p_value = fisher_exact(table, alternative='two-sided')
    return {
        'odds_ratio': round(odds_ratio, 4),
        'p_value': round(p_value, 6),
        'method': 'Fisher exact test'
    }
```

### Wilcoxon Rank-Sum (Mann-Whitney U)

For continuous outcomes when the distribution is skewed or has outliers:

```python
from scipy.stats import mannwhitneyu

def rank_test(y_treated, y_control):
    """
    Non-parametric test comparing distributions.
    Robust to outliers and skew. Works well with small samples.
    Tests: P(Y_treated > Y_control) ≠ 0.5
    """
    stat, p_value = mannwhitneyu(y_treated, y_control, alternative='two-sided')
    n_t, n_c = len(y_treated), len(y_control)
    # Rank-biserial correlation as effect size
    r = 1 - (2 * stat) / (n_t * n_c)
    return {
        'u_statistic': stat,
        'p_value': round(p_value, 6),
        'rank_biserial_r': round(r, 4),
        'method': 'Mann-Whitney U (Wilcoxon rank-sum)'
    }
```

## When to Use What

| Situation | Recommended Test |
|:---|:---|
| Small sample, continuous outcome, roughly symmetric | Permutation test |
| Small sample, continuous outcome, heavily skewed | Wilcoxon rank-sum |
| Small sample, binary outcome | Fisher exact test |
| Small sample, count outcome | Permutation test on counts |
| Large sample (n > 200/arm), any distribution | Standard t-test or z-test (CLT kicks in) |

## Confidence Intervals for Small Samples

### Bootstrap CI (works for any sample size)
```python
def bootstrap_ci(y_treated, y_control, n_bootstrap=10000, alpha=0.05, seed=42):
    """Bootstrap confidence interval for difference in means."""
    rng = np.random.RandomState(seed)
    diffs = []
    for _ in range(n_bootstrap):
        boot_t = rng.choice(y_treated, size=len(y_treated), replace=True)
        boot_c = rng.choice(y_control, size=len(y_control), replace=True)
        diffs.append(np.mean(boot_t) - np.mean(boot_c))

    diffs = np.array(diffs)
    return {
        'ci_lower': round(np.percentile(diffs, 100 * alpha / 2), 6),
        'ci_upper': round(np.percentile(diffs, 100 * (1 - alpha / 2)), 6),
        'point_estimate': round(np.mean(y_treated) - np.mean(y_control), 6)
    }
```

## Power Considerations for Small Samples

With small samples:
- Power is likely LOW — you can only detect large effects
- Be honest about minimum detectable effects
- Consider pooling data from multiple small experiments (meta-analysis)
- Paired or crossover designs can dramatically improve power
- Don't run an experiment you can't adequately power
