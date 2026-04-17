# Pre-Registration Reference Guide

## Purpose

Pre-registration commits to the analysis plan BEFORE seeing the data.
This prevents:
- HARKing (Hypothesizing After Results are Known)
- Garden of forking paths (trying many analyses, reporting the one that "works")
- Outcome switching (changing the primary metric after seeing results)

## When to Create a Pre-Registration

- ALWAYS before an A/B test or experiment
- Before any confirmatory analysis (not exploratory)
- When results will be used for decision-making

## Template Location

Use `assets/pre-analysis-plan-template.md` to generate the plan.

## Key Sections

1. **Hypothesis**: State H₀ and H₁ before any data
2. **Primary metric**: ONE metric, precisely defined
3. **Sample size**: Justified by power analysis
4. **Analysis plan**: Statistical test, covariates, corrections
5. **Decision criteria**: What result = ship? What result = don't ship?
6. **Timeline**: Start date, end date, no peeking (unless sequential)

## Rules

- The plan is written BEFORE data collection
- Changes after data collection must be clearly marked as "post-hoc"
- Exploratory analyses are fine but must be labeled as such
- The pre-registration is the contract — honor it
