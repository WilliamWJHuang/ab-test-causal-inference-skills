# Methodology Checklist

## Use this checklist in Phase 1 of the stats-reviewer audit.

### 1. Research Question Clarity
- [ ] Is the research question clearly stated?
- [ ] Is the question answerable with the available data?
- [ ] Is the question causal or associational? Does the language match?

### 2. Study Design → Method Match
- [ ] Does the statistical method match the study design?
- [ ] Is the variable type (continuous, binary, ordinal, count) appropriate for the chosen test?
- [ ] If causal claims are made, is there a valid identification strategy?

### 3. Variable Specification
- [ ] Are dependent and independent variables correctly identified?
- [ ] Are control variables included? Are they pre-treatment? (Never control for post-treatment variables)
- [ ] Are there omitted variables that could confound the results?

### 4. Sample Selection
- [ ] Is the sample representative of the target population?
- [ ] Are there selection bias concerns?
- [ ] Is the sample size adequate? (Power analysis conducted?)

### 5. Temporal Validity
- [ ] Is the time period of the data appropriate for the question?
- [ ] Could the results be driven by a specific time period (pandemic, holiday, etc.)?
- [ ] Is there a risk of reverse causation?

## Severity Guide
- Missing or wrong method for the question → 🔴 CRITICAL
- Method is defensible but not optimal → 🟡 WARNING
- Alternative method could strengthen the analysis → 🟢 SUGGESTION
