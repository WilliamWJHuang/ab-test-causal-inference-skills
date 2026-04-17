# Causal Method Selection Guide

## Decision Framework

Use this guide when the user needs help choosing a causal inference method.
The choice depends on: (1) data structure, (2) identification strategy, (3) available assumptions.

## Method Comparison Table

| Method | Data Structure | Key Assumption | Estimand | Best For |
|:---|:---|:---|:---|:---|
| **RCT Analysis** | Cross-sectional/panel | Random assignment | ATE | Experiments |
| **DiD** | Panel (pre/post, treated/control) | Parallel trends | ATT | Policy changes |
| **Synthetic Control** | Panel (few treated units) | Good pre-fit | ATT | Aggregate interventions |
| **Synthetic DiD** | Panel | Parallel trends + weights | ATT | Combines DiD + SC |
| **RDD** | Cross-sectional + running variable | Continuity at cutoff | LATE (at cutoff) | Threshold policies |
| **IV/2SLS** | Cross-sectional/panel + instrument | Exclusion restriction | LATE | Non-compliance |
| **Matching** | Cross-sectional | Conditional independence | ATT | Selection on observables |
| **IPW** | Cross-sectional | Conditional independence | ATE or ATT | Selection on observables |
| **AIPW/DR** | Cross-sectional | Either model correct | ATE | Robustness |

## Estimand Definitions

- **ATE** (Average Treatment Effect): E[Y(1) - Y(0)] — effect across entire population
- **ATT** (Average Treatment Effect on the Treated): E[Y(1) - Y(0) | D=1] — effect on those who received treatment
- **LATE** (Local Average Treatment Effect): Effect for compliers (those who change treatment due to instrument/cutoff)
- **CATE** (Conditional ATE): E[Y(1) - Y(0) | X=x] — effect for subgroups

## When to Use Each Method

### DiD: "Something changed at a known time for some units"
- Example: A new law was enacted in some states but not others
- Requires: Pre/post data for treatment and control groups
- Key check: Parallel pre-treatment trends

### Synthetic Control: "One or few units received the treatment"
- Example: California passed a tobacco tax — no other state did
- Requires: Panel data with many control units
- Key check: Good pre-treatment fit using weighted combination of controls

### RDD: "There's a clear threshold that determines treatment"
- Example: Students above a GPA cutoff get a scholarship
- Requires: Running variable with a known cutoff
- Key check: No manipulation of the running variable around the cutoff

### IV: "There's something that affects treatment but not the outcome"
- Example: Being assigned to a treatment group (even if you don't comply)
- Requires: A valid instrument (relevant, exogenous, exclusion restriction)
- Key check: First-stage F-statistic > 10

### Matching/IPW: "We can control for all confounders"
- Example: Compare outcomes for patients who chose drug A vs. drug B, adjusting for health status
- Requires: All confounders observed and measured
- Key check: Balance after matching/weighting, overlap in propensity scores
