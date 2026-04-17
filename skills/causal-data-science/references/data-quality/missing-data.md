# Missing Data Guide

## Classification

### MCAR (Missing Completely At Random)
- Missingness is independent of both observed and unobserved data
- Example: Lab sample randomly lost
- Test: Little's MCAR test
- Safe to: listwise delete (but loses power)

### MAR (Missing At Random)
- Missingness depends on OBSERVED variables
- Example: Younger users less likely to report income (age is observed)
- Cannot test directly — requires domain knowledge
- Solution: Multiple imputation (MICE), IPW

### MNAR (Missing Not At Random)
- Missingness depends on the MISSING VALUE itself
- Example: High earners less likely to report income
- Cannot test — requires sensitivity analysis
- Solution: Heckman correction, pattern-mixture models, bounds

## Recommended Imputation Methods

| Method | When to Use | Limitations |
|:---|:---|:---|
| **Listwise deletion** | MCAR + small % missing | Loses data; biased if not MCAR |
| **Mean/median imputation** | NEVER use for analysis | Biases variance, correlations |
| **MICE (Multiple Imputation)** | MAR, moderate missing | Requires correct model specification |
| **KNN imputation** | Moderate missing, non-linear relationships | Sensitive to k and distance metric |
| **Maximum likelihood** | MAR, multivariate normal data | Requires distributional assumption |

## Implementation

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import pandas as pd

def impute_missing(df, columns, method='mice', n_imputations=5):
    """
    Multiple imputation using MICE (iterative imputer).
    """
    if method == 'mice':
        imputer = IterativeImputer(max_iter=10, random_state=42,
                                    sample_posterior=True)
        imputed_datasets = []
        for i in range(n_imputations):
            imputer.set_params(random_state=42 + i)
            imputed = pd.DataFrame(
                imputer.fit_transform(df[columns]),
                columns=columns, index=df.index
            )
            imputed_datasets.append(imputed)

        return imputed_datasets

    raise ValueError(f"Unknown method: {method}")
```

## Reporting Missing Data

Always report:
1. Percentage missing per variable
2. Missing data mechanism (MCAR/MAR/MNAR) with justification
3. Method used to handle missing data
4. Sensitivity analysis (do conclusions change under different assumptions?)
