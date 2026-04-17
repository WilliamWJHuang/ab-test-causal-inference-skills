---
name: good-stats-skill
description: A well-structured statistical analysis skill that guides proper hypothesis testing with effect sizes and power analysis.
version: "1.0.0"
domain: statistics
author: Test Author
triggers:
  - "hypothesis test"
  - "statistical significance"
  - "compare groups"
use_for:
  - "Comparing two or more groups"
  - "Running hypothesis tests"
do_not_use_for:
  - "Causal inference from observational data"
  - "Machine learning model training"
compatibility:
  - claude-code
  - gemini-cli
  - cursor
---

# Statistical Analysis Guide

## Overview

This skill guides the agent through proper statistical hypothesis testing,
ensuring normality checks, appropriate test selection, effect size reporting,
and multiple comparison corrections.

## When to Use

Use this skill when the user wants to:
- Compare two or more groups statistically
- Test a hypothesis about differences or relationships
- Determine if an observed effect is statistically significant

## Decision Tree

```
IF comparing two groups:
  IF data is normal (Shapiro-Wilk p > 0.05) AND variances are equal:
    → Use independent samples t-test
  ELIF data is normal but variances unequal:
    → Use Welch's t-test
  ELSE (data is non-normal):
    → Use Mann-Whitney U test
    → Consider bootstrap confidence intervals

IF comparing 3+ groups:
  IF data is normal AND variances are homogeneous:
    → Use one-way ANOVA with post-hoc (Tukey HSD)
  ELSE:
    → Use Kruskal-Wallis test
    → Post-hoc: Dunn's test with Bonferroni correction
```

## Guardrails

- **REFUSE** to report only p-values. Always include effect size (Cohen's d,
  eta-squared, or odds ratio) and confidence intervals.
- **REFUSE** to approve an experiment without power analysis showing power ≥ 80%.
- **WARN** if multiple comparisons are performed without correction (Bonferroni,
  Benjamini-Hochberg, or Holm).
- **MUST NOT** claim statistical significance without reporting the full context.

## Output Format

Always report results in this structure:

```
Test: [test name]
Effect Size: [metric] = [value] ([interpretation])
95% CI: [lower, upper]
p-value: [value] (adjusted: [method])
Power: [value]
Assumptions checked: [list]
```

## Edge Cases

- **Small samples (n < 30)**: Use exact tests or bootstrap methods
- **Tied data**: Use appropriate tie-correction for rank-based tests
- **What if normality is borderline?**: Report both parametric and non-parametric results

### Common Mistakes

- Using paired tests for independent samples (anti-pattern)
- Reporting "trending toward significance" for p = 0.06 (do not use for this)
- Cherry-picking seeds for reproducibility — report mean ± std across multiple seeds

## Escape Hatch

Experienced users can override guardrails by explicitly stating:
"I acknowledge [specific guardrail] and am proceeding because [justification]."

## References

For detailed method guides, see the `references/` directory.
