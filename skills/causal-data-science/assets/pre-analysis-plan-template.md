# Pre-Analysis Plan Template

## Experiment: [Title]
**Date created**: [Date]
**Author**: [Name]

---

## 1. Research Question
[What question is this experiment designed to answer?]

## 2. Hypothesis
- **H₀ (Null)**: [The treatment has no effect on [primary metric]]
- **H₁ (Alternative)**: [The treatment [increases/decreases] [primary metric] by at least [MDE]]

## 3. Treatment Description
- **Control**: [Description of control condition]
- **Treatment**: [Description of treatment condition]
- **Number of variants**: [2 for A/B, more for multivariate]

## 4. Metrics

### Primary Metric (powers the experiment)
| Field | Value |
|:---|:---|
| Name | [metric name] |
| Definition | [exact formula] |
| Direction | [higher/lower is better] |
| Baseline value | [mean] |
| Baseline std | [standard deviation] |
| MDE (relative) | [X%] |
| MDE (absolute) | [value] |

### Secondary Metrics
1. [Name]: [Definition]
2. [Name]: [Definition]

### Guardrail Metrics
1. [Name]: Must not [increase/decrease] by more than [X%]
2. [Name]: Must not [increase/decrease] by more than [X%]

## 5. Sample Size and Power
| Parameter | Value |
|:---|:---|
| Significance level (α) | [0.05] |
| Power (1-β) | [0.80] |
| Sample size per arm | [N] |
| Total sample size | [2N] |
| Expected duration | [X days] |
| Test type | [two-sided / one-sided] |

## 6. Randomization
- **Unit**: [user / session / page / geo]
- **Strategy**: [simple / stratified / cluster]
- **Allocation ratio**: [50/50]
- **Stratification variables**: [if applicable]

## 7. Analysis Plan
- **Statistical test**: [t-test / z-test / Mann-Whitney / etc.]
- **Variance reduction**: [CUPED / stratification / none]
- **Covariate adjustment**: [list covariates, if any]
- **Multiple comparison correction**: [Bonferroni / BH-FDR / none]

## 8. Decision Criteria
- **Ship treatment if**: Primary metric [increases/decreases] significantly at α=[X]
  AND all guardrail metrics are within bounds
- **Keep control if**: Primary metric is not significant OR guardrail violations
- **Extend experiment if**: [conditions for extension, if any]

## 9. Timeline
- **Experiment start**: [Date]
- **Experiment end**: [Date]
- **Analysis deadline**: [Date]
- **Decision meeting**: [Date]

## 10. Risks and Limitations
- [List known risks, potential confounds, limitations]

---

*This pre-analysis plan was locked on [Date]. Any deviations must be documented
as post-hoc modifications in the final analysis report.*
