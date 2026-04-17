# Execution Checklist

## Use this checklist in Phase 2 of the stats-reviewer audit.

### 1. Assumptions Verification
- [ ] Were distributional assumptions tested (normality, homoscedasticity)?
- [ ] Were violations addressed (transformations, robust methods, non-parametric alternatives)?
- [ ] Is independence of observations justified?
- [ ] For regression: multicollinearity checked (VIF < 5)?

### 2. Statistical Testing
- [ ] Is the correct test used? (parametric vs. non-parametric, one-sided vs. two-sided)
- [ ] Is the significance level (α) pre-specified?
- [ ] Are test statistics, degrees of freedom, and exact p-values reported?
- [ ] Is the test two-sided unless there's a strong prior reason for one-sided?

### 3. Effect Sizes & CIs
- [ ] Are effect sizes reported alongside p-values?
- [ ] Are 95% confidence intervals provided for all key estimates?
- [ ] Is practical significance discussed (not just statistical significance)?

### 4. Multiple Comparisons
- [ ] How many hypothesis tests were run in total?
- [ ] Was multiplicity correction applied? Which method?
- [ ] Were subgroup analyses pre-specified or exploratory?
- [ ] Is there a risk of "garden of forking paths"?

### 5. Robustness
- [ ] Were sensitivity analyses conducted?
- [ ] Do results hold across reasonable alternative specifications?
- [ ] Were outliers assessed for their influence on results?

### 6. Reporting Quality
- [ ] Are all necessary statistics reported (test stat, df, p, effect size, CI)?
- [ ] Are figures clearly labeled with units, axes, error bars?
- [ ] Are limitations acknowledged?

## Severity Guide
- Wrong test, no effect sizes → 🔴 CRITICAL
- Missing CI or uncorrected multiple comparisons → 🟡 WARNING
- Minor reporting improvements → 🟢 SUGGESTION
