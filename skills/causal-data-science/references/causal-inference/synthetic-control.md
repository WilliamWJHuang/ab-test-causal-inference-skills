# Synthetic Control Method Guide

## When to Use
- ONE (or very few) treated units received an intervention
- Many untreated "donor" units available for comparison
- Panel data with multiple pre-treatment periods

## Concept
Construct a "synthetic" version of the treated unit as a weighted combination
of untreated units that best matches pre-treatment outcomes.

```python
# Using the SparseSC or SyntheticControlMethods package
# pip install SyntheticControlMethods

def synthetic_control_example():
    """
    Synthetic Control requires:
    1. Pre-treatment outcome data for treated + donor units
    2. Weights that minimize pre-treatment prediction error
    3. Post-treatment comparison: treated vs. synthetic
    """
    pass
```

## Key Assumptions
1. **Pre-treatment fit**: Synthetic unit closely matches treated unit pre-treatment
2. **No spillover**: Treatment doesn't affect donor units
3. **No anticipation**: Treated unit didn't change behavior before treatment
4. **Convex hull**: Treated unit lies within the range of donor units

## Inference
- **Placebo test in space**: Apply the method to each donor unit (as if it were treated). The treated unit's effect should be extreme relative to placebos.
- **Placebo test in time**: Apply the method to a fake treatment date. Should show no effect.
- **Pre-treatment MSPE ratio**: Effect / pre-treatment fit. Higher = more credible.

## Synthetic Difference-in-Differences (SDID)
Combines the best of DiD and Synthetic Control:
- Uses synthetic control weights for units
- Uses DiD-style time weights
- Generally more efficient than either method alone

Reference: Arkhangelsky et al. (2021)
