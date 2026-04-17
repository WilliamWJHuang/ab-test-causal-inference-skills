#!/usr/bin/env python3
"""
Power Calculator for Experiment Design

Standalone script for calculating sample sizes, power, and experiment duration.
Supports two-sample tests for means and proportions, with CUPED adjustment.

Usage:
    python power_calculator.py --baseline-mean 10.0 --baseline-std 5.0 --mde 0.05
    python power_calculator.py --baseline-rate 0.10 --mde 0.05 --type proportion
    python power_calculator.py --baseline-mean 10.0 --baseline-std 5.0 --mde 0.05 --cuped-rho 0.7
"""

import argparse
import math
import sys

try:
    from scipy import stats as scipy_stats
    import numpy as np
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from statsmodels.stats.power import TTestIndPower, NormalIndPower
    from statsmodels.stats.proportion import proportion_effectsize
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False


# Lookup table for z-values (pure math fallback when scipy is unavailable)
_Z_TABLE = {0.01: 2.576, 0.025: 1.960, 0.05: 1.645, 0.10: 1.282}
_POWER_Z = {0.80: 0.842, 0.85: 1.036, 0.90: 1.282, 0.95: 1.645}


def _z_alpha(alpha, two_sided):
    """Get z critical value, using scipy if available, else lookup table."""
    tail_alpha = alpha / (2 if two_sided else 1)
    if HAS_SCIPY:
        return scipy_stats.norm.ppf(1 - tail_alpha)
    return _Z_TABLE.get(tail_alpha, 1.96)


def _z_beta(power):
    """Get z value for power, using scipy if available, else lookup table."""
    if HAS_SCIPY:
        return scipy_stats.norm.ppf(power)
    return _POWER_Z.get(power, 0.842)


def sample_size_two_means(baseline_mean, baseline_std, mde_relative,
                          alpha=0.05, power=0.80, two_sided=True):
    """Calculate sample size for a two-sample t-test on means."""
    mde_absolute = baseline_mean * mde_relative
    cohens_d = mde_absolute / baseline_std

    if HAS_STATSMODELS:
        analysis = TTestIndPower()
        n_per_arm = analysis.solve_power(
            effect_size=cohens_d,
            alpha=alpha,
            power=power,
            alternative='two-sided' if two_sided else 'larger'
        )
    else:
        # Normal approximation (works without any dependencies)
        z_a = _z_alpha(alpha, two_sided)
        z_b = _z_beta(power)
        n_per_arm = 2 * ((z_a + z_b) / cohens_d) ** 2

    n_per_arm = int(math.ceil(n_per_arm))

    return {
        'test_type': 'two-sample t-test (means)',
        'n_per_arm': n_per_arm,
        'total_n': n_per_arm * 2,
        'baseline_mean': baseline_mean,
        'baseline_std': baseline_std,
        'mde_relative': f'{mde_relative:.1%}',
        'mde_absolute': round(mde_absolute, 4),
        'cohens_d': round(cohens_d, 4),
        'alpha': alpha,
        'power': power,
    }


def sample_size_two_proportions(baseline_rate, mde_relative,
                                 alpha=0.05, power=0.80, two_sided=True):
    """Calculate sample size for a two-sample z-test on proportions."""
    new_rate = baseline_rate * (1 + mde_relative)

    if HAS_STATSMODELS:
        effect_size = proportion_effectsize(new_rate, baseline_rate)
        analysis = NormalIndPower()
        n_per_arm = analysis.solve_power(
            effect_size=abs(effect_size),
            alpha=alpha,
            power=power,
            alternative='two-sided' if two_sided else 'larger'
        )
    else:
        # Fallback: Fleiss formula (works without any dependencies)
        p_bar = (baseline_rate + new_rate) / 2
        z_a = _z_alpha(alpha, two_sided)
        z_b = _z_beta(power)
        n_per_arm = ((z_a * math.sqrt(2 * p_bar * (1 - p_bar)) +
                       z_b * math.sqrt(baseline_rate * (1 - baseline_rate) +
                                          new_rate * (1 - new_rate))) ** 2) / \
                     (new_rate - baseline_rate) ** 2

    n_per_arm = int(math.ceil(n_per_arm))

    return {
        'test_type': 'two-sample z-test (proportions)',
        'n_per_arm': n_per_arm,
        'total_n': n_per_arm * 2,
        'baseline_rate': f'{baseline_rate:.4f}',
        'expected_rate': f'{new_rate:.4f}',
        'mde_relative': f'{mde_relative:.1%}',
        'mde_absolute': f'{new_rate - baseline_rate:.4f}',
        'alpha': alpha,
        'power': power,
    }


def adjust_for_cuped(result, cuped_rho):
    """Reduce sample size based on CUPED correlation."""
    variance_reduction = cuped_rho ** 2
    adjusted_n = int(math.ceil(result['n_per_arm'] * (1 - variance_reduction)))

    result['cuped_rho'] = cuped_rho
    result['variance_reduction'] = f'{variance_reduction:.1%}'
    result['n_per_arm_cuped'] = adjusted_n
    result['total_n_cuped'] = adjusted_n * 2
    result['sample_size_savings'] = f'{variance_reduction:.1%}'

    return result


def estimate_duration(total_n, daily_traffic, allocation=1.0):
    """Estimate experiment duration in days."""
    effective_daily = daily_traffic * allocation
    if effective_daily <= 0:
        return {'days': float('inf'), 'weeks': float('inf')}

    days = int(math.ceil(total_n / effective_daily))
    return {
        'days': days,
        'weeks': round(days / 7, 1),
        'daily_traffic': daily_traffic,
        'allocation': f'{allocation:.0%}',
    }


def format_results(result, duration=None):
    """Pretty-print results."""
    print('\n' + '=' * 60)
    print('POWER ANALYSIS RESULTS')
    print('=' * 60)

    for key, value in result.items():
        label = key.replace('_', ' ').title()
        print(f'  {label:.<35} {value}')

    if duration:
        print('\n  --- Duration Estimate ---')
        for key, value in duration.items():
            label = key.replace('_', ' ').title()
            print(f'  {label:.<35} {value}')

        if duration['days'] > 90:
            print('\n  ⚠️  WARNING: Experiment needs >90 days.')
            print('     Consider: increasing MDE, using CUPED, or a more sensitive metric.')

    print('=' * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Power Calculator for Experiment Design',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--type', choices=['mean', 'proportion'], default='mean',
                       help='Type of test (default: mean)')
    parser.add_argument('--baseline-mean', type=float,
                       help='Baseline mean of the metric')
    parser.add_argument('--baseline-std', type=float,
                       help='Baseline standard deviation')
    parser.add_argument('--baseline-rate', type=float,
                       help='Baseline rate (for proportion test)')
    parser.add_argument('--mde', type=float, required=True,
                       help='Minimum detectable effect (relative, e.g., 0.05 for 5%%)')
    parser.add_argument('--alpha', type=float, default=0.05,
                       help='Significance level (default: 0.05)')
    parser.add_argument('--power', type=float, default=0.80,
                       help='Statistical power (default: 0.80)')
    parser.add_argument('--cuped-rho', type=float, default=None,
                       help='CUPED correlation for variance reduction')
    parser.add_argument('--daily-traffic', type=int, default=None,
                       help='Daily eligible traffic for duration estimate')
    parser.add_argument('--allocation', type=float, default=1.0,
                       help='Fraction of traffic allocated to experiment (default: 1.0)')

    args = parser.parse_args()

    if args.power < 0.80:
        print('⚠️  WARNING: Power < 80%% is not recommended. Proceeding anyway.')

    # Calculate sample size
    if args.type == 'mean':
        if not args.baseline_mean or not args.baseline_std:
            parser.error('--baseline-mean and --baseline-std required for mean test')
        result = sample_size_two_means(
            args.baseline_mean, args.baseline_std, args.mde,
            args.alpha, args.power
        )
    else:
        if not args.baseline_rate:
            parser.error('--baseline-rate required for proportion test')
        result = sample_size_two_proportions(
            args.baseline_rate, args.mde, args.alpha, args.power
        )

    # Apply CUPED if specified
    if args.cuped_rho is not None:
        result = adjust_for_cuped(result, args.cuped_rho)

    # Estimate duration if traffic specified
    duration = None
    if args.daily_traffic:
        total = result.get('total_n_cuped', result['total_n'])
        duration = estimate_duration(total, args.daily_traffic, args.allocation)

    format_results(result, duration)


if __name__ == '__main__':
    main()
