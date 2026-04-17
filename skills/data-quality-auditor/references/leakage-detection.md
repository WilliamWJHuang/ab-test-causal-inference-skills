# Data Leakage Detection Guide

## Types of Leakage

### 1. Temporal (Time Travel) Leakage
Using information from the future to predict the past.

**How to detect:**
- Check if any feature has a timestamp AFTER the prediction target date
- Check if rolling averages include future data
- Check if labels were assigned using future information

**Example:** Predicting customer churn using their cancellation date as a feature.

### 2. Target Leakage
Features that are proxies for (or derived from) the outcome variable.

**How to detect:**
- Check for features with suspiciously high correlation to the target (>0.9)
- Check if any feature is computed from the target
- Check if features are only available BECAUSE of the outcome

**Example:** Using "number of insurance claims paid" to predict "whether a claim will be paid."

### 3. Train-Test Leakage
Preprocessing steps that use information from the test set.

**How to detect:**
- Was normalization/scaling fitted on all data or only training data?
- Was feature selection done using all data?
- Were imputation values computed from all data?

**Prevention:**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# CORRECT: Scale inside pipeline (fits only on training data)
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
pipeline.fit(X_train, y_train)

# WRONG: Scale before split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)  # Leaks test info!
X_train, X_test = split(X_scaled)
```

### 4. Group Leakage
Related observations appearing in both train and test sets.

**How to detect:**
- Are there repeated user IDs across train/test?
- Are there related entities (same household, same clinic)?
- Are there temporal dependencies (sequential observations from same subject)?

**Prevention:** Use `GroupKFold` or `TimeSeriesSplit` instead of random splits.

## Leakage Detection Checklist

- [ ] No features computed from future data
- [ ] No features derived from the target variable
- [ ] All preprocessing fitted ONLY on training data
- [ ] No related observations across train/test
- [ ] Features represent information available at prediction time
- [ ] Model performance is not "too good to be true" (suspiciously high accuracy → investigate)
