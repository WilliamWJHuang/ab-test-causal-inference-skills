#!/usr/bin/env python3
"""
Refutation Tests for Causal Inference

Run standard refutation tests to validate causal estimates:
1. Placebo treatment (random treatment assignment)
2. Add random common cause (random confounder)
3. Subset validation (estimate on random subsets)
4. Bootstrap refutation (resample and re-estimate)

These tests check if the causal estimate is robust to alternative explanations.

Usage:
    from refutation_tests import run_all_refutations
    results = run_all_refutations(model, data, treatment, outcome)
"""

import warnings
import numpy as np


def placebo_treatment_test(df, outcome_col, treatment_col, covariate_cols,
                           estimate_func, n_permutations=500, seed=42):
    """
    Placebo treatment test: randomly permute treatment assignment.
    The estimated effect under random treatment should be ~0.

    Parameters
    ----------
    df : DataFrame
    outcome_col : str
    treatment_col : str
    covariate_cols : list
    estimate_func : callable
        Function that takes (df, outcome, treatment, covariates) and returns effect estimate.
    n_permutations : int
    seed : int

    Returns
    -------
    dict with placebo effects distribution and p-value.
    """
    rng = np.random.RandomState(seed)
    original_effect = estimate_func(df, outcome_col, treatment_col, covariate_cols)

    placebo_effects = []
    for _ in range(n_permutations):
        df_permuted = df.copy()
        df_permuted[treatment_col] = rng.permutation(df_permuted[treatment_col].values)
        placebo_effect = estimate_func(df_permuted, outcome_col, treatment_col, covariate_cols)
        placebo_effects.append(placebo_effect)

    placebo_effects = np.array(placebo_effects)
    p_value = np.mean(np.abs(placebo_effects) >= np.abs(original_effect))

    return {
        'test': 'Placebo Treatment',
        'original_effect': round(original_effect, 6),
        'placebo_mean': round(np.mean(placebo_effects), 6),
        'placebo_std': round(np.std(placebo_effects), 6),
        'p_value': round(p_value, 4),
        'passed': p_value < 0.05,  # Original should be extreme vs placebos
        'interpretation': (
            '✅ PASSED: Effect is unlikely under random treatment assignment.'
            if p_value < 0.05 else
            '🔴 FAILED: Effect is consistent with random treatment — causal claim not supported.'
        )
    }


def random_common_cause_test(df, outcome_col, treatment_col, covariate_cols,
                              estimate_func, n_trials=100, seed=42):
    """
    Add a random variable as a confounder. If the estimate changes substantially,
    the original estimate may be sensitive to unmeasured confounding.
    """
    rng = np.random.RandomState(seed)
    original_effect = estimate_func(df, outcome_col, treatment_col, covariate_cols)

    adjusted_effects = []
    for i in range(n_trials):
        df_aug = df.copy()
        df_aug[f'_random_confounder_{i}'] = rng.normal(size=len(df))
        aug_covariates = covariate_cols + [f'_random_confounder_{i}']
        adjusted_effect = estimate_func(df_aug, outcome_col, treatment_col, aug_covariates)
        adjusted_effects.append(adjusted_effect)

    adjusted_effects = np.array(adjusted_effects)
    mean_change = np.mean(np.abs(adjusted_effects - original_effect))
    relative_change = mean_change / abs(original_effect) if original_effect != 0 else float('inf')

    return {
        'test': 'Random Common Cause',
        'original_effect': round(original_effect, 6),
        'mean_adjusted_effect': round(np.mean(adjusted_effects), 6),
        'mean_absolute_change': round(mean_change, 6),
        'relative_change': f'{relative_change:.2%}',
        'passed': relative_change < 0.10,
        'interpretation': (
            '✅ PASSED: Estimate is stable when adding random confounders.'
            if relative_change < 0.10 else
            '🔴 FAILED: Estimate changes substantially with random confounders — may be fragile.'
        )
    }


def subset_validation_test(df, outcome_col, treatment_col, covariate_cols,
                            estimate_func, n_subsets=100, subset_fraction=0.8, seed=42):
    """
    Estimate the effect on random subsets. A robust estimate should be stable.
    """
    rng = np.random.RandomState(seed)
    original_effect = estimate_func(df, outcome_col, treatment_col, covariate_cols)

    subset_effects = []
    n_subset = int(len(df) * subset_fraction)
    for _ in range(n_subsets):
        indices = rng.choice(len(df), size=n_subset, replace=False)
        df_subset = df.iloc[indices]
        subset_effect = estimate_func(df_subset, outcome_col, treatment_col, covariate_cols)
        subset_effects.append(subset_effect)

    subset_effects = np.array(subset_effects)
    cv = np.std(subset_effects) / abs(np.mean(subset_effects)) if np.mean(subset_effects) != 0 else float('inf')

    return {
        'test': 'Subset Validation',
        'original_effect': round(original_effect, 6),
        'subset_mean': round(np.mean(subset_effects), 6),
        'subset_std': round(np.std(subset_effects), 6),
        'coefficient_of_variation': f'{cv:.2%}',
        'passed': cv < 0.30,
        'interpretation': (
            '✅ PASSED: Estimate is stable across random subsets.'
            if cv < 0.30 else
            '🔴 FAILED: Estimate varies substantially across subsets — may be driven by outliers.'
        )
    }


def bootstrap_refutation_test(df, outcome_col, treatment_col, covariate_cols,
                               estimate_func, n_bootstrap=1000, seed=42):
    """
    Bootstrap the estimate to assess stability and construct confidence intervals.
    """
    rng = np.random.RandomState(seed)
    original_effect = estimate_func(df, outcome_col, treatment_col, covariate_cols)

    bootstrap_effects = []
    for _ in range(n_bootstrap):
        indices = rng.choice(len(df), size=len(df), replace=True)
        df_boot = df.iloc[indices]
        try:
            boot_effect = estimate_func(df_boot, outcome_col, treatment_col, covariate_cols)
            bootstrap_effects.append(boot_effect)
        except Exception:
            continue

    bootstrap_effects = np.array(bootstrap_effects)
    ci_lower = np.percentile(bootstrap_effects, 2.5)
    ci_upper = np.percentile(bootstrap_effects, 97.5)
    includes_zero = ci_lower <= 0 <= ci_upper

    return {
        'test': 'Bootstrap Refutation',
        'original_effect': round(original_effect, 6),
        'bootstrap_mean': round(np.mean(bootstrap_effects), 6),
        'bootstrap_std': round(np.std(bootstrap_effects), 6),
        'ci_95_lower': round(ci_lower, 6),
        'ci_95_upper': round(ci_upper, 6),
        'includes_zero': includes_zero,
        'interpretation': (
            f'95% Bootstrap CI: [{ci_lower:.4f}, {ci_upper:.4f}]. '
            f'{"Includes zero — effect may not be significant." if includes_zero else "Does not include zero."}'
        )
    }


def run_all_refutations(df, outcome_col, treatment_col, covariate_cols, estimate_func,
                        seed=42, verbose=True):
    """
    Run all refutation tests and return a summary.
    """
    tests = [
        ('Placebo Treatment', placebo_treatment_test),
        ('Random Common Cause', random_common_cause_test),
        ('Subset Validation', subset_validation_test),
        ('Bootstrap', bootstrap_refutation_test),
    ]

    results = []
    for name, test_func in tests:
        if verbose:
            print(f'\nRunning {name} test...')
        try:
            result = test_func(df, outcome_col, treatment_col, covariate_cols,
                              estimate_func, seed=seed)
            results.append(result)
            if verbose:
                print(f'  {result["interpretation"]}')
        except Exception as e:
            warnings.warn(f'{name} test failed: {e}')
            results.append({
                'test': name,
                'passed': None,
                'interpretation': f'⚠️ Test failed: {e}'
            })

    # Summary
    n_passed = sum(1 for r in results if r.get('passed') is True)
    n_failed = sum(1 for r in results if r.get('passed') is False)
    n_error = sum(1 for r in results if r.get('passed') is None)

    summary = {
        'total_tests': len(results),
        'passed': n_passed,
        'failed': n_failed,
        'errors': n_error,
        'overall': '✅ All tests passed' if n_failed == 0 else f'🔴 {n_failed} test(s) failed',
        'details': results
    }

    if verbose:
        print(f'\n{"=" * 50}')
        print(f'REFUTATION SUMMARY: {summary["overall"]}')
        print(f'  Passed: {n_passed} | Failed: {n_failed} | Errors: {n_error}')
        print(f'{"=" * 50}')

    return summary


if __name__ == '__main__':
    # Example usage with a simple OLS estimator
    print('Refutation Tests Module')
    print('Import and use: from refutation_tests import run_all_refutations')
    print('See docstrings for usage examples.')
