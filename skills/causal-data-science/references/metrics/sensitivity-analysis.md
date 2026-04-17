# Metric Sensitivity Analysis

## Purpose

Before running an experiment, assess whether your chosen metric is
sensitive enough to detect the expected effect at your sample size.

## Pre-Experiment Sensitivity Check

### Step 1: Estimate Metric Variance
Pull 4-8 weeks of historical data. Compute the standard deviation per user.

### Step 2: Compute MDE at Available Traffic
```
MDE = (z_α/2 + z_β) × √(2σ²/n)
```

### Step 3: Compare MDE to Expected Effect
- If MDE < expected effect → metric is sensitive enough
- If MDE > expected effect → metric is too noisy, consider alternatives

### Step 4: Consider Alternatives
1. **Reduce variance**: CUPED, stratification
2. **More sensitive metric**: Rate metrics often have lower variance than counts
3. **Longer experiment**: More data → smaller MDE
4. **Different aggregation**: Per-user-day vs. per-user-week

## Metric Velocity

How quickly does the metric stabilize for a given user?

- **Fast metrics**: Click-through rate (stable within 1 day)
- **Medium metrics**: Purchase rate (stable within 1-2 weeks)
- **Slow metrics**: Retention, LTV (need weeks/months)

Rule of thumb: Run the experiment for at least 2× the metric stabilization time.

## Sensitivity vs. Specificity Trade-off

- **Highly sensitive metrics** (e.g., page views) move easily but may not reflect real value
- **Highly specific metrics** (e.g., revenue) are meaningful but noisy
- Best practice: Use a hierarchy — sensitive leading indicator + specific lagging indicator
