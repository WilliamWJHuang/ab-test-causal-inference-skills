# Metric Taxonomy Reference

## Metric Types by Domain

### E-commerce / Marketplace
| Metric | Type | Formula |
|:---|:---|:---|
| Conversion rate | Primary | Orders / Visitors |
| Revenue per visitor | Primary | Total revenue / Visitors |
| Average order value | Diagnostic | Revenue / Orders |
| Cart abandonment rate | Guardrail | Abandoned carts / Started carts |
| Page load time | Guardrail | p50 or p95 latency |
| Return rate | Guardrail | Returns / Orders |

**Decomposition**: Revenue = Visitors × Conversion Rate × AOV

### SaaS / Subscription
| Metric | Type | Formula |
|:---|:---|:---|
| Activation rate | Primary | Activated / Signed up |
| 7-day retention | Primary | Returned day 7 / Signed up |
| Monthly churn rate | Guardrail | Churned / Start-of-month subscribers |
| NPS | Secondary | % Promoters - % Detractors |
| Time to value | Diagnostic | Time from signup to first key action |

**Decomposition**: MRR = Subscribers × ARPU

### Content / Media
| Metric | Type | Formula |
|:---|:---|:---|
| DAU/MAU ratio | Primary | Daily active / Monthly active |
| Session duration | Secondary | Total time / Sessions |
| Content completion | Diagnostic | Completed / Started |
| Ad load time | Guardrail | Time to first ad render |

## Metric Decomposition Templates

### Multiplicative Decomposition
Revenue = Traffic × Conversion × ARPU

To diagnose a revenue change:
1. Did traffic change? (External factors, SEO)
2. Did conversion change? (UX, pricing)
3. Did ARPU change? (Mix shift, pricing)

### Funnel Decomposition
Overall conversion = Step1 rate × Step2 rate × Step3 rate × ...

To diagnose a conversion change:
1. Which funnel step changed?
2. Is it the same across segments?

### Cohort Decomposition
Metric = f(Cohort_age) × f(Cohort_size)

Distinguish genuine improvement from mix shift (newer cohorts being larger).
