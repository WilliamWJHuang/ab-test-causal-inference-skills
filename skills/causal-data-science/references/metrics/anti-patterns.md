# Metric Anti-Patterns

## 1. Goodhart's Law
> "When a measure becomes a target, it ceases to be a good measure."

**Example**: Optimizing for "time spent in app" → team adds infinite scroll
that increases engagement but decreases satisfaction.

**Fix**: Pair with guardrail metrics (satisfaction, retention).

## 2. Vanity Metrics
Metrics that look impressive but don't drive decisions.

- Total registered users (most are inactive)
- Total page views (bots, accidental clicks)
- App downloads (without activation check)

**Fix**: Use actionable metrics tied to user value.

## 3. Composite Metrics (Kitchen Sink)
Combining unrelated signals into one number.

score = 0.3 × engagement + 0.4 × revenue + 0.3 × retention

**Problems**: Weights are arbitrary; hard to interpret changes; masks
underlying dynamics.

**Fix**: Track components separately. Use composite only as a tiebreaker.

## 4. Ratio Metrics with Small Denominators
When the denominator is small, the ratio becomes unstable.

**Example**: 2/3 = 67% conversion, but add one failure → 2/4 = 50%

**Fix**: Set a minimum denominator threshold (e.g., exclude users with < 5 sessions).

## 5. Surrogate Metric Drift
Using a proxy metric that gradually disconnects from the true goal.

**Example**: Optimizing click-through rate as proxy for revenue, but CTR
increases while revenue decreases (attracting low-quality clicks).

**Fix**: Periodically validate the proxy against the true metric.

## 6. Simpson's Paradox in Metrics
A trend that appears in several groups reverses when the groups are combined.

**Example**: Treatment improves metric in EVERY segment, but overall metric
goes down (because treatment shifts users into lower-performing segments).

**Fix**: Always segment by key dimensions before aggregating.

## 7. Metric Cannibalization
Improving one metric at the expense of another.

**Example**: Increasing email send frequency → higher short-term engagement
but higher unsubscribe rate.

**Fix**: Define guardrail metrics that capture downstream harm.
