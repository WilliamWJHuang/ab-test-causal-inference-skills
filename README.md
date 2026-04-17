# A/B Test & Causal Inference Agent Skills

Agent skills for A/B testing, causal inference, and stats review — works with [Claude Code](https://claude.ai/code), [Gemini CLI](https://github.com/google-gemini/gemini-cli), [Cursor](https://cursor.sh), or any agent that reads `SKILL.md` files.

## What this is for

AI agents are pretty good at writing code. They're not good at statistics. Without guardrails, they'll do things like:

- Skip power analysis entirely ("just run the test and see")
- Test a dozen metrics, find one with p < 0.05, and call that the primary result
- Make causal claims from a basic regression on observational data
- Report model accuracy from a single random seed as if it's reliable

These are the kind of mistakes that get caught in peer review or by a careful statistician — but agents don't have that filter built in.

This skill gives them one. It enforces power analysis, forces assumption checks before estimation, requires identification for causal claims, and flags common statistical pitfalls. There are over 1000 agent skills for things like React, DevOps, and cloud APIs. As far as I know, this is the first one focused on experimentation and causal inference.

## Who this is for

**Data scientists** running A/B tests who want the agent to enforce rigor without being told to. 
**Product managers and analysts** who work with experiments but don't have a stats background — the skill adjusts its explanations to your level. 
**Causal inference folks** using DiD, RDD, IV, matching, etc. who want the agent to follow a proper identify → estimate → refute pipeline. 
**ML engineers** who need to catch things like seed cherry-picking and test set contamination. 
**Students and researchers** who are still learning — the skill explains its reasoning as it goes. 
Or really anyone using an agent for data work who'd rather it act like a careful statistician than a code autocomplete.

## Quick start

Copy one folder into your agent's skills directory:

```bash
# Claude Code
cp -r skills/causal-data-science/ .claude/skills/causal-data-science/

# Gemini CLI
cp -r skills/causal-data-science/ .gemini/skills/causal-data-science/

# Cursor
cp -r skills/causal-data-science/ .cursor/skills/causal-data-science/
```

That's it. No config needed. Ask it something like "help me design an A/B test" or "does X cause Y in my data" and it takes over from there.

## Examples

### "I want to test if a new checkout flow increases purchases"

<details>
<summary>See the conversation →</summary>

**You:** I want to test if a new checkout flow increases purchases. How should I set this up?

**Agent:** Let's design this properly. A few questions first:

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
<summary>See the conversation →</summary>

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
<summary>See the conversation →</summary>

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

### "I have data and want to know if X causes Y" (beginner)

<details>
<summary>See the conversation →</summary>

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

### "Review this analysis for me" (advanced)

<details>
<summary>See the conversation →</summary>

**You:** Can you review this analysis? I ran a DiD comparing states that adopted a policy to those that didn't. I have a staggered rollout — 12 states adopted between 2018-2021, 38 didn't. Standard TWFE with state and year fixed effects. The coefficient on treatment is 3.2pp (p=0.02).

**Agent:** A few concerns with the TWFE specification under staggered adoption:

1. **Negative weighting problem.** With staggered rollout, TWFE can assign negative weights to some treatment effects — meaning already-treated units act as controls for later-treated units. This can bias the overall estimate, even flip the sign. Have you checked for negative weights? (de Chaisemartin & D'Haultfœuille, 2020)

2. **Heterogeneous treatment effects over time.** If the policy effect grows (or shrinks) over time, TWFE conflates the time-varying effects and the result is hard to interpret. The 3.2pp estimate averages over all post-treatment periods and all adoption cohorts.

**Recommendation:** Re-estimate using Callaway & Sant'Anna (2021) or Sun & Abraham (2021). These give you cohort-specific and time-specific effects that you can aggregate cleanly. The `did` package in R or `csdid` in Stata handles this.

3. **Parallel trends.** Did you check pre-treatment trends? With 12 treatment states, an event study plot showing leads and lags would be informative. Pre-treatment coefficients should be indistinguishable from zero.

4. **Inference.** With 50 state-level clusters, cluster-robust SEs are appropriate but might underreject. Consider the wild cluster bootstrap (Cameron, Gelbach & Miller, 2008), especially with 12 treated clusters.

Want me to write the Callaway-Sant'Anna code, or should we start with the event study diagnostic?

</details>

## What's inside

Six workflows, one entry point:

**Experiment design** — power analysis, randomization strategy (simple, stratified, cluster, geo, switchback), CUPED variance reduction, pre-analysis plan generation. Won't let you run an experiment with power below 80%.

**Causal inference** — for when you can't randomize. Routes to DiD, synthetic control, RDD, IV, matching/IPW, or doubly robust based on your data. Checks assumptions first, runs refutation tests after.

**Post-experiment analysis** — SRM checks, covariate adjustment via Lin estimator, non-compliance handling (ITT vs. LATE), small-sample inference with permutation tests.

**Stats review** — two-pass audit (right method? done correctly?). Catches things like multiple comparisons without correction, causal language from observational data, seed cherry-picking.

**Data quality** — selection bias, survivorship bias, missing data patterns, data leakage, outlier assessment.

**Metrics** — helps define primary/secondary/guardrail metrics with exact formulas. Flags Goodhart's Law, vanity metrics, and poorly specified composites.

## Adapts to your level

The skill picks up on how you talk and adjusts accordingly. It doesn't ask "what's your experience level?" — just listens.

If you say "is this better?" it'll walk you through the basics with analogies. If you say "should I use AIPW here?" it'll skip the intro and get into implementation. Four levels, adjusts mid-conversation, never locks in.

## Under the hood

```
skills/causal-data-science/
├── SKILL.md                            ← the one file the agent loads
├── references/
│   ├── experiment-design/              # power analysis, sequential testing, CUPED, etc.
│   ├── causal-inference/               # DiD, RDD, IV, matching, sensitivity analysis
│   ├── stats-review/                   # methodology and execution checklists
│   ├── data-quality/                   # bias, missing data, leakage detection
│   ├── metrics/                        # taxonomy, anti-patterns
│   └── adaptive-explainer/             # jargon glossary (33 terms)
├── scripts/
│   ├── power_calculator.py             # works standalone
│   └── refutation_tests.py
└── assets/
    ├── pre-analysis-plan-template.md
    └── review-report-template.md
```

~170 lines in the main SKILL.md. Reference docs load only when needed.

## Individual skills

If you just want one piece (say, only experiment design), each workflow also exists as a standalone skill:

- [`experiment-designer/`](skills/experiment-designer/)
- [`causal-inference-advisor/`](skills/causal-inference-advisor/)
- [`stats-reviewer/`](skills/stats-reviewer/)
- [`data-quality-auditor/`](skills/data-quality-auditor/)
- [`metrics-definer/`](skills/metrics-definer/)
- [`adaptive-explainer/`](skills/adaptive-explainer/)

Most people should just install `causal-data-science/` and get everything.

## Skill evaluator

The repo also has a [skill-evaluator](skill-evaluator/) CLI that scores any SKILL.md on structure, security, quality, and domain correctness. Basically a linter for agent skills. More details in the [skill-evaluator README](skill-evaluator/README.md).

## Design philosophy

The agent will say no. If you try to run an underpowered experiment, skip refutation tests, or claim causation without a proper identification strategy, it refuses. You can override it if you know what you're doing, but you have to acknowledge it explicitly.

It figures out your level from context instead of asking. And it's one install instead of seven separate skills — the routing happens inside the SKILL.md automatically.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) has the full details. The most useful contributions are reference docs for methods I haven't covered yet, and corrections when the existing guidance is wrong (ideally with a citation).

## License

MIT
