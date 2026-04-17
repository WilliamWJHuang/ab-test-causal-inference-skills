# Bias Checklist

## Selection Bias Types

### 1. Self-Selection Bias
- **Definition**: Units choose whether to be treated
- **Example**: Users who opt into a feature are different from those who don't
- **Mitigation**: RCT, matching, IV

### 2. Survivorship Bias
- **Definition**: Observing only units that "survived" a process
- **Example**: Analyzing only companies that still exist; analyzing only users who didn't churn
- **Mitigation**: Include failed/dropped units, use intent-to-treat analysis

### 3. Attrition Bias
- **Definition**: Differential dropout between groups
- **Example**: Sicker patients drop out of treatment arm → treatment looks better
- **Mitigation**: Intent-to-treat analysis, inverse probability of censoring weighting

### 4. Berkson's Bias
- **Definition**: Sampling from a conditioned population
- **Example**: Hospital-based study → patients are sicker than population
- **Mitigation**: Population-based sampling

### 5. Collider Bias
- **Definition**: Conditioning on a consequence of both treatment and outcome
- **Example**: Analyzing only published studies (publication depends on significance and effect size)
- **Mitigation**: Don't condition on post-treatment variables

### 6. Healthy Worker Effect
- **Definition**: Workers are healthier than the general population
- **Example**: Occupational health studies underestimate risk
- **Mitigation**: Use internal comparisons within worker populations

## Bias Assessment Template

For each variable/sample:
1. Who is INCLUDED in the data? Who is EXCLUDED?
2. Is the inclusion/exclusion related to the treatment?
3. Is the inclusion/exclusion related to the outcome?
4. If both → potential bias. Estimate direction and magnitude.
