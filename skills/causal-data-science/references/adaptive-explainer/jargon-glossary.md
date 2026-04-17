# Jargon Glossary

When explaining to beginner users, translate these terms.

| Technical Term | Plain Language |
|:---|:---|
| Statistical significance | The result is unlikely to be due to chance alone |
| p-value | The probability of seeing this result (or more extreme) if the treatment actually did nothing |
| Confidence interval | A range that likely contains the true effect — narrower means more precise |
| Power | Your chance of detecting a real improvement if one actually exists |
| Type I error / false positive | Concluding something works when it doesn't |
| Type II error / false negative | Missing a real effect because you didn't have enough data |
| MDE / minimum detectable effect | The smallest improvement you'd care about detecting |
| Variance / standard deviation | How much the metric bounces around day to day |
| Treatment / control | The group that gets the change vs. the group that doesn't |
| Randomization | Randomly deciding who gets the change, so the groups are fairly comparable |
| Confounder | A factor that affects both the treatment and the outcome, making it look like one causes the other when it might not |
| Causal inference | Figuring out whether X actually causes Y, not just whether they happen together |
| Observational data | Data where nobody controlled who got treated — it just happened naturally |
| Selection bias | Your sample isn't representative because of how people ended up in it |
| Effect size | How big the difference actually is — not just whether it exists |
| Regression to the mean | Extreme values naturally drift back toward average when measured again |
| DAG (directed acyclic graph) | A diagram showing which variables cause which — helps figure out what to adjust for |
| Identification strategy | Your argument for why this analysis measures a real causal effect, not just a correlation |
| Parallel trends | Both groups were heading in the same direction before the change happened — required for DiD |
| SUTVA | The assumption that one person's treatment doesn't spill over and affect someone else's outcome |
| Instrumental variable | Something that affects whether someone gets treated, but doesn't directly affect the outcome itself |
| DiD (difference-in-differences) | Compare an affected group to a similar unaffected group, looking at the change before and after |
| RDD (regression discontinuity) | Compare people just above and just below a cutoff that determines treatment |
| Matching / IPW | Find similar people in both groups and compare them, or reweight data to simulate a fair experiment |
| AIPW / doubly robust | Combines two estimation approaches for extra protection — if one is wrong, the other compensates |
| ATE | Average treatment effect — the average effect across everyone |
| ATT | Average treatment effect on the treated — the effect specifically on those who received it |
| HTE / CATE | Heterogeneous / conditional treatment effect — how the effect differs across subgroups |
| ITT (intention-to-treat) | The effect of being assigned to treatment, whether or not you actually used it |
| LATE | The effect specifically on compliers — people who actually took the treatment when assigned to it |
| SRM (sample ratio mismatch) | When the actual split between groups doesn't match what was intended — a sign of broken randomization |
| Multiple comparison correction | An adjustment needed when testing many hypotheses to prevent false discoveries from stacking up |
| Garden of forking paths | The many small analysis decisions (which variables, which subgroups, which cutoffs) that inflate false positives even without formal multiple testing |
