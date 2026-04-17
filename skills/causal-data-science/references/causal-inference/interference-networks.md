# Interference and Network Effects in Experiments

## When to Read This

Read when units in the experiment can affect each other — social networks,
marketplaces, shared resources, geographic proximity, or any setting where
one user's treatment might change another user's outcome.

## What is Interference?

The Stable Unit Treatment Value Assumption (SUTVA) says: a unit's outcome depends
only on its OWN treatment assignment, not on anyone else's. When SUTVA is violated,
standard analysis is biased.

### Common Interference Scenarios

| Setting | How Interference Happens |
|:---|:---|
| Social network | Treated user shares content with control user |
| Marketplace | More sellers discounted → fewer buyers for control sellers |
| Rideshare | Surge pricing in treatment area redirects drivers from control area |
| Shared infrastructure | Treatment group consumes resources, slowing control group |
| Geographic | New store location draws customers away from nearby control stores |
| Within-household | One family member gets treatment, affects another's behavior |

## Detection

### Signs that interference is present:
1. Treatment effect CHANGES when you vary the fraction treated
2. Control group outcomes shift compared to pre-experiment baseline
3. Effect estimates differ between geographically concentrated vs. dispersed units
4. The "no treatment" outcome in the experiment differs from historical baseline

### Diagnostic test:
Compare control group mean during experiment to pre-experiment baseline.
If they differ significantly beyond normal variation, interference is likely.

## Design Solutions

### 1. Cluster Randomization
Randomize at a level where interference is contained within clusters.

- **Social networks**: Randomize at the community/neighborhood level
- **Marketplaces**: Randomize at the market level (city, region)
- **Shared resources**: Randomize at the resource-pool level

**Cost**: Need more units (clusters), not just more users. Power drops
substantially — see `power-analysis.md` for the design effect formula.

### 2. Switchback (Time-Based) Designs
Alternate treatment on/off over time periods for all users.

- Works when interference is within a time period, not across periods
- Need enough periods to average out time effects
- Common for marketplace experiments (surge pricing, matching algorithms)

### 3. Geo-Randomization
Randomize at geographic level (cities, DMAs, countries).

- Good when interference is local
- Very few units → use synthetic control methods for inference
- See `references/synthetic-control.md`

### 4. Ego-Network Randomization
For social network experiments: randomize the target user AND measure
outcomes on their neighbors.

## Analysis Under Interference

### Exposure Mapping
Define each unit's "exposure" based on the treatment assignments in their network:

```python
def compute_exposure(adj_matrix, treatment_vector):
    """
    For each unit, compute fraction of neighbors treated.

    adj_matrix: n x n binary adjacency matrix
    treatment_vector: n-length binary vector
    """
    import numpy as np
    neighbor_counts = adj_matrix.sum(axis=1)
    treated_neighbor_counts = adj_matrix @ treatment_vector
    exposure = np.where(neighbor_counts > 0,
                        treated_neighbor_counts / neighbor_counts, 0)
    return exposure
```

### Estimands Under Interference

| Estimand | Meaning |
|:---|:---|
| Direct effect | Effect of YOUR treatment on YOUR outcome |
| Spillover effect | Effect of NEIGHBORS' treatment on YOUR outcome |
| Total effect | Direct + spillover combined |
| Overall effect | Average effect across the population |

### Horvitz-Thompson Under Interference
When you know the randomization probabilities (which you do in an RCT),
you can use inverse-probability weighted estimators that account for
the exposure structure.

## Common Mistakes

- NEVER ignore interference and run a standard analysis — the bias can be large and in EITHER direction
- NEVER assume that cluster randomization eliminates all interference — it only contains interference WITHIN clusters
- NEVER use individual-level randomization when you suspect interference — the treatment effect estimate is meaningless
- ALWAYS report whether interference was considered and how it was addressed
