# Causal Data Science Skills

Agent skills for experiment design, causal inference, and statistical review. Built for [Claude Code](https://claude.ai/code), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Cursor](https://cursor.sh), and anything else that reads `SKILL.md` files.

## Why I built this

I've spent years doing experimentation and causal inference work. When I started using AI coding agents for data science, I noticed they make the same mistakes over and over:

- Run a t-test on skewed data without checking assumptions
- No power analysis — just "run it and see"
- Twelve metrics tested, one hits p < 0.05, and suddenly that's the "primary" metric
- Causal claims from an OLS on observational data
- Single-seed model comparisons reported as definitive

None of this would survive a review from anyone who's done this work seriously. But agents don't know that, and most of the people using them for data science don't either.

There are 1000+ agent skills out there for React, DevOps, cloud APIs, marketing — nothing for statistics or causal inference. So I built these.

## Quick start

Copy one folder. That's it.

```bash
# Claude Code
cp -r skills/causal-data-science/ .claude/skills/causal-data-science/

# Gemini CLI
cp -r skills/causal-data-science/ .gemini/skills/causal-data-science/

# Cursor
cp -r skills/causal-data-science/ .cursor/skills/causal-data-science/
```

One skill, one install. No configuration. The agent detects what you need from your question and adapts to your experience level automatically.

## Examples

### "I want to test if a new checkout flow increases purchases"

<details>
<summary>Full conversation →</summary>

**You:** I want to test if a new checkout flow increases purchases. How should I set this up?

**Agent:** Let's design this experiment properly. A few questions first:

1. **What's changing?** The checkout flow (got it).
2. **Who gets randomized?** Individual users, or does this affect entire sessions/devices?
3. **What's the primary metric?** Sounds like purchase conversion rate — is that right, or is it revenue per user?
4. **How much traffic do you have?** Roughly, how many users hit checkout per week?

**You:** Individual users. Purchase conversion rate is the metric. About 50,000 users per week hit checkout.

**Agent:** Good. Now let's figure out how long you need to run this.

**Power analysis:**
- Baseline conversion: what's your current purchase rate? (If you're not sure, I can help you pull it from historical data.)

**You:** Around 3.2%

**Agent:** At 3.2% baseline, here's what you need for different effect sizes:

| Minimum detectable effect | Sample per arm | Duration at 50k/week |
|:---|:---:|:---:|
| 10% relative (3.2% → 3.52%) | ~47,600 | ~2 weeks |
| 5% relative (3.2% → 3.36%) | ~190,000 | ~7.6 weeks |
| 2% relative (3.2% → 3.26%) | ~1,190,000 | ~47.6 weeks |

A 5% relative lift gets you to about 8 weeks. That's typical for checkout experiments. Can you run it that long?

Before we go further — let's set guardrail metrics. These are things that must **not** get worse:
- Page load time
- Error rate
- Revenue per user (in case conversion goes up but order value drops)

I'll generate a pre-analysis plan with all of this documented so nobody changes the rules after the test starts.

</details>

### "Does our pricing change affect revenue?" (observational data)

<details>
<summary>Full conversation →</summary>

**You:** We changed pricing in Germany last quarter. I want to know if it affected revenue.

**Agent:** Important question: was this change **randomly assigned**, or did Germany just get new pricing while other countries didn't?

**You:** Just Germany. Other countries kept old pricing.

**Agent:** OK, this is observational — not a randomized experiment. We can't just compare Germany's revenue before and after, because lots of other things changed too (seasonality, marketing, macro trends).

The standard approach here is **difference-in-differences** (DiD): compare Germany (affected) to similar countries (unaffected), looking at the change before vs. after. The idea is that whatever happened to both groups (seasonality, etc.) cancels out, and what's left is the pricing effect.

For this to work, we need to check one key thing: **were Germany and your comparison countries on the same trajectory before the pricing change?** If Germany was already trending differently, DiD won't give us a clean answer.

Can you pull monthly revenue for Germany and 2-3 similar markets (similar size, same product mix) for at least 6 months before the change?

**You:** I can get France, Netherlands, and Austria. I have 12 months before and 3 months after.

**Agent:** Good choices — similar European markets. Let's proceed:

1. **Parallel trends check** — I'll plot pre-treatment revenue trends for all four countries. If they track together before the change, we're in good shape.
2. **Estimate the effect** — run DiD comparing Germany to the other three, with country and month fixed effects.
3. **Refutation tests** — placebo test (pretend the change happened 6 months earlier — the effect should be zero), and leave-one-out (drop each control country and check stability).

Want me to write the code?

</details>

### "My model gets 94% accuracy, is that good?"

<details>
<summary>Full conversation →</summary>

**You:** I trained a classifier and it gets 94% accuracy. Is that good?

**Agent:** Depends on a few things. Let me check:

1. **What's the class distribution?** If 94% of your data belongs to one class, then a model that predicts the majority class every time also gets 94% — and yours isn't doing anything useful.

**You:** Oh. It's about 90/10 split.

**Agent:** That's the issue. A trivial baseline (always predict the majority class) gets 90%. Your model is only 4 percentage points above that. Not great.

A few more things I'd want to check:

2. **How many seeds did you try?** If you trained once with one random seed and got 94%, that single number might not be stable. Rerun with 5 different seeds and report mean ± standard deviation. The variance might surprise you.

3. **Was the test set used during development at all?** Even indirectly — like checking test accuracy to decide which model or hyperparameters to keep. If yes, the 94% is optimistic.

4. **Better metrics for imbalanced data:** precision, recall, F1, and AUROC will give you a much clearer picture than accuracy. Want me to generate a full evaluation?

**You:** I only used one seed. And yeah, I checked test accuracy to pick between two models.

**Agent:** Then the 94% is likely inflated by both issues. Here's what I'd recommend:

- Retrain your top 2 models with 5 seeds each, report mean ± std on a **held-out** test set neither model has touched
- Report AUROC and F1 alongside accuracy
- If mean accuracy is 93.5% ± 1.2%, your model and the other candidate might not be meaningfully different — the variance from seeds alone could explain the gap

</details>

### "I have data and want to know if X causes Y" (beginner, never done causal inference)

<details>
<summary>Full conversation →</summary>

**You:** I have a dataset of customers and I want to know if signing up for our loyalty program causes them to spend more.

**Agent:** Good question, and an important distinction: customers who sign up for loyalty programs tend to be people who *already* spend a lot. So if loyalty members spend more, it could be because:

**(a)** the program actually makes them spend more, or
**(b)** big spenders are just more likely to sign up in the first place

This is the core challenge of causal inference. To figure out which one it is, I need to understand your data better:

1. **Was enrollment randomized?** Did you randomly offer the program to some customers and not others?
2. **Or did customers choose to enroll?** (Most common case)
3. **Do you have data from before they enrolled?** Like spending history from before they joined?

**You:** Customers chose to enroll. I have 2 years of transaction data for everyone.

**Agent:** OK, since enrollment was self-selected, we need to deal with the "big spenders sign up" problem. Here's the approach I'd recommend:

**Step 1:** Draw a diagram of what causes what. For loyalty programs, it usually looks like:
- Past spending → likelihood of enrolling (big spenders are more likely to join)
- Past spending → future spending (people who spend a lot tend to keep spending a lot)
- Loyalty program → future spending (this is what we want to measure)

Past spending is a **confounder** — it affects both whether someone enrolls AND how much they spend later. If we don't account for it, we'll overestimate the program's effect.

**Step 2:** Find comparison customers. Match each loyalty member with a non-member who had similar spending patterns *before* enrollment. Then compare their spending *after*. This way, we're comparing apples to apples.

**Step 3:** Run a sensitivity check. Ask: "how strong would a hidden factor have to be to explain away our result?" If the answer is "implausibly strong," we can be more confident.

Want me to walk through Step 2 with your data?

</details>

### "Review this analysis for me" (advanced user)

<details>
<summary>Full conversation →</summary>

**You:** Can you review this analysis? I ran a DiD comparing states that adopted a policy to those that didn't. I have a staggered rollout — 12 states adopted between 2018-2021, 38 didn't. Standard TWFE with state and year fixed effects. The coefficient on treatment is 3.2pp (p=0.02).

**Agent:** A few concerns with the TWFE specification under staggered adoption:

1. **Negative weighting problem.** With staggered rollout, TWFE can assign negative weights to some treatment effects — meaning already-treated units act as controls for later-treated units. This can bias the overall estimate, even flip the sign. Have you checked for negative weights? (de Chaisemartin & D'Haultfœuille, 2020)

2. **Heterogeneous treatment effects over time.** If the policy effect grows (or shrinks) over time, TWFE conflates the time-varying effects and the result is hard to interpret. The 3.2pp estimate averages over all post-treatment periods and all adoption cohorts.

**Recommendation:** Re-estimate using Callaway & Sant'Anna (2021) or Sun & Abraham (2021). These give you cohort-specific and time-specific effects that you can aggregate cleanly. The `did` package in R or `csdid` in Stata handles this.

3. **Parallel trends.** Did you check pre-treatment trends? With 12 treatment states, an event study plot showing leads and lags would be informative. Pre-treatment coefficients should be indistinguishable from zero.

4. **Inference.** With 50 state-level clusters, cluster-robust SEs are appropriate but might underreject. Consider the wild cluster bootstrap (Cameron, Gelbach & Miller, 2008), especially with 12 treated clusters.

Want me to write the Callaway-Sant'Anna code, or should we start with the event study diagnostic?

</details>

## What it covers

The skill handles six workflows through a single entry point:

**Experiment design** — Clarify the question, run power analysis, choose randomization strategy (simple, stratified, paired, cluster, geo, switchback), set up CUPED variance reduction, generate a pre-analysis plan. Refuses power below 80%.

**Causal inference** — Decision tree for observational data: DiD, synthetic control, RDD, IV, matching/IPW, doubly robust. Forces assumption checks and mandatory refutation tests.

**Post-experiment analysis** — SRM check, covariate adjustment (Lin estimator), non-compliance (ITT vs. LATE), small-sample inference (permutation tests). The gap most skills miss.

**Statistical review** — Two-pass audit: right method for the question, then correct execution. Catches multiple comparisons, missing effect sizes, causal language from correlations, seed cherry-picking.

**Data quality audit** — Selection bias, survivorship bias, missing data mechanisms, data leakage, outliers, sample representativeness.

**Metric definition** — Primary/secondary/guardrail metrics with exact formulas. Catches Goodhart's Law, vanity metrics, composite metrics.

## Adapts to your level

The skill detects your statistics background from how you talk — not by asking. Four levels:

- **Beginner:** "Is this better?" → Analogies, step-by-step, explains every term
- **Intermediate:** "What's the right sample size?" → Standard terms, skips basics
- **Advanced:** "Should I use AIPW here?" → Abbreviations, straight to code
- **Expert:** "I'm concerned about negative weighting in TWFE" → Peer discussion, cites papers

## What's under the hood

```
skills/causal-data-science/
├── SKILL.md                            ← the one file the agent reads
├── references/
│   ├── experiment-design/
│   │   ├── power-analysis.md           # formulas, code, cluster designs
│   │   ├── sequential-testing.md       # group sequential, always-valid
│   │   ├── variance-reduction.md       # CUPED, CUPAC, stratification
│   │   ├── rct-analysis.md             # Neyman, Lin estimator, ITT/LATE
│   │   ├── small-sample-inference.md   # permutation tests, exact tests
│   │   └── pre-registration.md
│   ├── causal-inference/
│   │   ├── did-guide.md                # includes staggered DiD
│   │   ├── synthetic-control.md
│   │   ├── rdd-guide.md
│   │   ├── iv-late.md
│   │   ├── matching-weighting.md       # PSM, CEM, IPW, AIPW
│   │   ├── hte-estimation.md           # meta-learners, causal forest
│   │   ├── interference-networks.md    # SUTVA violations, spillover
│   │   └── sensitivity-analysis.md     # E-values, Rosenbaum, Oster
│   ├── stats-review/
│   │   ├── methodology-checklist.md
│   │   ├── execution-checklist.md
│   │   ├── ml-specific-checks.md       # seed sensitivity, leakage
│   │   ├── multiple-comparisons.md
│   │   └── effect-size-guide.md
│   ├── data-quality/
│   │   ├── bias-checklist.md
│   │   ├── missing-data.md
│   │   └── leakage-detection.md
│   ├── metrics/
│   │   ├── metric-taxonomy.md
│   │   ├── anti-patterns.md
│   │   └── sensitivity-analysis.md
│   └── adaptive-explainer/
│       └── jargon-glossary.md          # 33 technical-to-plain translations
├── scripts/
│   ├── power_calculator.py             # standalone CLI tool
│   └── refutation_tests.py             # placebo, bootstrap, subset
└── assets/
    ├── pre-analysis-plan-template.md
    └── review-report-template.md
```

The main SKILL.md is ~170 lines. Reference docs load on demand — the agent only reads what it needs.

## Individual skills (advanced)

If you only want one specific domain, each workflow is also available as a standalone skill:

- [`experiment-designer/`](skills/experiment-designer/)
- [`causal-inference-advisor/`](skills/causal-inference-advisor/)
- [`stats-reviewer/`](skills/stats-reviewer/)
- [`data-quality-auditor/`](skills/data-quality-auditor/)
- [`metrics-definer/`](skills/metrics-definer/)
- [`adaptive-explainer/`](skills/adaptive-explainer/)

For most users, just install `causal-data-science/`.

## Skill evaluator

The repo includes [skill-evaluator](skill-evaluator/), a CLI that scores any SKILL.md on structure, security, quality, domain correctness, and maintenance. Like a linter for agent skills. See the [skill-evaluator README](skill-evaluator/README.md).

## Design choices

**The agent will refuse.** Underpowered experiment? No. Causal claims without identification? No. Single-seed ML comparison? No. There's an escape hatch if you explicitly acknowledge the override, but the default is rigor.

**Adapts, doesn't ask.** Never asks "what's your experience level?" — infers it from your language and adjusts in real time.

**One install, not seven.** Single SKILL.md with on-demand reference loading. Minimal context window footprint.

## Background

I work on experimentation and causal inference. The ML-specific checks (seed instability, test-set contamination) draw from established best practices in deep learning evaluation reproducibility.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) has the details. Most useful contributions: reference docs for methods not covered yet, and reports when the guidance is wrong (with a citation).

## License

MIT
