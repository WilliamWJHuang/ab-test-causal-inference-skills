# ML-Specific Statistical Checks

## Seed Sensitivity

Based on established findings on seed instability in deep learning evaluation:
- Model performance can vary significantly across random seeds
- Reporting a single seed result is MISLEADING

### Required Practice
- Report mean ± std across at least 5 random seeds
- For close comparisons (< 1% difference), use ≥ 20 seeds
- Use paired comparisons (same seed across models) to reduce variance
- Consider adjusting for pre-experiment covariates to reduce noise

### Check
```
🔴 CRITICAL if: Results reported for a single seed only
🟡 WARNING if: Results averaged over < 5 seeds without std
🟢 OK if: mean ± std over ≥ 5 seeds, with paired comparison
```

## Best-of-N Reporting

Selecting the best result from N runs inflates performance. The expected maximum
of N draws from N(μ, σ) is approximately μ + σ × √(2 ln N).

### Check
- Was the final model selected as the best of multiple training runs?
- If yes, was this selection process accounted for in the comparison?
- Report all N runs, not just the best one

## Test Set Contamination

### Types
1. Using test data for hyperparameter tuning
2. Using test data for model selection
3. Using test performance to decide when to stop training
4. Using test data for feature engineering

### Check
- Is there a clear train/validation/test split?
- Was validation used for tuning, test used ONLY for final evaluation?
- Was the test set touched more than once?

## Data Leakage in ML Pipelines

### Common Sources
1. **Preprocessing before split**: Normalizing on full data, then splitting
2. **Feature selection before split**: Selecting features using full data
3. **Temporal leakage**: Using future information to predict past events
4. **Group leakage**: Same patient/user in both train and test

### Check
- Is preprocessing (scaling, imputation, feature selection) fitted ONLY on training data?
- Is the split done before any data-dependent operations?

## Fair Baseline Comparisons

### Requirements
- Same dataset, same splits, same preprocessing
- Same compute budget (or explicitly stated)
- Same hyperparameter tuning budget
- Separate hyperparameter tuning for each method (not just the proposed one)

### Check
- Were baselines run by the authors or taken from papers (potentially different settings)?
- Were baselines given the same tuning effort?
- Are the comparison numbers verifiable?

## Evaluation Metric Appropriateness

| Scenario | Bad Metric | Good Metric |
|:---|:---|:---|
| Class imbalance (1:100) | Accuracy | AUROC, AUPRC, F1 |
| Regression with outliers | MSE | MAE, Median AE |
| Ranking task | Accuracy | NDCG, MAP |
| Calibration matters | Accuracy | Brier score, calibration plot |
