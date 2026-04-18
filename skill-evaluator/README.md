<p align="center">
  <h1 align="center">🔍 agent-skill-evaluator</h1>
  <p align="center">
    <strong>Evaluate agent skills before you install them.</strong><br>
    Think <code>npm audit</code> + <code>eslint</code> for <code>SKILL.md</code> files.
  </p>
</p>

---

## Why This Exists

There are **1,000+ agent skills** on GitHub. Most have no quality signal beyond stars and recency. Before installing a skill into your agent:

- Is it **structurally sound**? (valid SKILL.md, proper metadata)
- Is it **safe**? (no prompt injection, credential harvesting, data exfiltration)
- Is it **high quality**? (decision trees, guardrails, edge cases)
- Is it **domain-correct**? (does it follow best practices for its domain — statistics, marketing, experiment design, etc.?)
- Is it **maintained**? (recent updates, tests, documentation)

`skill-evaluator` answers all five questions with a single command.

---

## Quick Start

```bash
# Install
cd skill-evaluator
pip install -e .

# Evaluate a local skill
skill-eval ../skills/experiment-designer/

# Evaluate with Markdown output (for CI/READMEs)
skill-eval ../skills/stats-reviewer/ --format md

# Evaluate with JSON output (for pipelines)
skill-eval ../skills/causal-inference-advisor/ --format json

# Force a specific domain for correctness checking
skill-eval ./some-skill/ --domain statistics
skill-eval ./some-skill/ --domain digital-marketing

# CI mode: fail if score is below threshold
skill-eval ./some-skill/ --fail-below 70
```

---

## What You Get

### Terminal Output

```
╭──────────────────────────────────────────────────────────╮
│ Skill Evaluation Report: experiment-designer — A (91/100)│
╰──────────────────────────────────────────────────────────╯

  📋 Excellent — high quality, well-maintained.

  ┌────────────────────┬─────────┬───────┬────────┐
  │ Dimension          │ Score   │ Grade │ Weight │
  ├────────────────────┼─────────┼───────┼────────┤
  │ Structure          │ 95/100  │ A+    │ 15%    │
  │ Security           │ 100/100 │ A+    │ 20%    │
  │ Quality            │ 90/100  │ A     │ 15%    │
  │ Domain Correctness │ 85/100  │ A-    │ 25%    │
  │ Maintenance        │ 80/100  │ B+    │ 15%    │
  └────────────────────┴─────────┴───────┴────────┘
```

### Scoring Dimensions

Each dimension produces a 0–100 score. These are combined into a weighted composite:

| Dimension | Weight | What It Checks |
|:---|:---:|:---|
| **Structure** | 15% | YAML frontmatter, required fields (`name`, `description`, `triggers`), section organization |
| **Security** | 20% | Shell injection, credential exfiltration, prompt injection, obfuscation |
| **Quality** | 15% | Decision trees, guardrails, edge cases, escape hatches, code templates |
| **Domain Correctness** | 25% | Rule-based verification of domain-specific methodology and best practices |
| **Maintenance** | 15% | File freshness, documentation, tests, CI config, auxiliary files |

> **Note:** Weights are normalized at runtime so they don't need to sum to exactly 100%. If you override weights via `--weights`, any missing dimensions default to 10%.

### Grading Scale

| Grade | Score Range | Meaning |
|:---:|:---:|:---|
| A+ | 95–100 | Exceptional — install with confidence |
| A | 90–94 | Excellent — high quality, well-maintained |
| A- | 85–89 | Very good — minor improvements possible |
| B+ | 80–84 | Good — solid skill with some gaps |
| B | 75–79 | Above average — usable but review findings |
| B- | 70–74 | Decent — has notable weaknesses |
| C+ | 65–69 | Fair — significant gaps, use with caution |
| C | 60–64 | Below average — consider alternatives |
| C- | 50–59 | Poor — major issues present |
| D | 40–49 | Very poor — not recommended |
| F | 0–39 | Failing — critical issues, do not install |

---

## Domain Correctness Rules

The **novel differentiator**. Unlike security/structure checks that any tool can do, domain correctness verifies the *guidance itself* is correct for its stated domain.

### Built-in Domains

| Domain | Rules | Checks |
|:---|:---:|:---|
| **Statistics** | 8 | Normality assumptions, effect sizes, multiple comparisons, power analysis, seed sensitivity, regression assumptions |
| **Causal Inference** | 8 | Identification strategies, parallel trends, IV assumptions, RDD bandwidth, matching balance, HTE |
| **Experiment Design** | 8 | Power analysis, randomization, variance reduction (CUPED), pre-registration, SRM checks, sequential testing |
| **Data Science** | 5 | Data leakage, missing data mechanisms, cross-validation, metric selection, outlier handling |
| **Digital Marketing** | 28 | Attribution modeling, marketing mix modeling, CLV/churn methodology, SEO/SEM, email deliverability, ad tech, privacy compliance |
| **Finance** | 28 | VaR/risk management, portfolio optimization, backtesting biases, DCF valuation, regulatory compliance, time series, market efficiency |

The digital marketing domain is organized into 7 sub-domain files:

| Sub-domain | Rules | Focus |
|:---|:---:|:---|
| Attribution & Measurement | 4 | Model awareness, incrementality testing, view-through caveats, cross-device |
| Marketing Mix Modeling | 4 | Adstock/carryover, diminishing returns, channel interactions, MMM validation |
| Customer Analytics | 4 | CLV methodology, churn definition, segmentation, cohort analysis |
| SEO / SEM | 5 | Technical SEO, bidding strategy, keyword research, E-E-A-T, AI search impact |
| Email / CRM | 4 | Deliverability (SPF/DKIM/DMARC), list hygiene, consent compliance, personalization |
| Ad Tech / Programmatic | 3 | Auction mechanics, frequency capping, viewability and fraud |
| General Marketing | 4 | Funnel understanding, privacy compliance, tracking infrastructure, KPI alignment |

The finance domain is organized into 7 sub-domain files:

| Sub-domain | Rules | Focus |
|:---|:---:|:---|
| Risk Management | 3 | VaR tail-risk assumptions, stress testing, risk-adjusted metrics (Sharpe/Sortino) |
| Portfolio & Allocation | 4 | MPT limitations, benchmark selection, diversification depth, rebalancing methodology |
| Backtesting | 5 | Look-ahead bias, survivorship bias, transaction costs, overfitting, multiple testing bias |
| Valuation & Pricing | 3 | DCF sensitivity analysis, relative valuation pitfalls, option pricing model selection |
| Regulatory & Compliance | 3 | Regulatory awareness (SEC/FCA/ESMA), KYC/AML, financial data privacy |
| Time Series & Forecasting | 3 | Stationarity requirements, regime changes, return distribution assumptions |
| General Finance | 4 | Return calculation methodology, inflation adjustment, tax implications, market efficiency |

### Domain Auto-Detection

When you run `skill-eval` without `--domain`, the analyzer auto-detects the most likely domain by counting keyword signals in the skill content. For example, a skill mentioning "attribution," "ROAS," and "landing page" detects as `digital-marketing`, while one mentioning "p-value," "effect size," and "t-test" detects as `statistics`.

### Adding Custom Domains

Create a YAML file in `skill_evaluator/domains/`:

```yaml
domain: my-domain
version: "1.0.0"
rules:
  - name: my-rule
    description: "What this rule checks"
    applicability_patterns:
      - "pattern that makes this rule relevant"
    required_patterns:
      - "pattern that SHOULD be present"
    antipatterns:
      - "pattern that SHOULD NOT be present"
    failure_severity: suspicious  # or "incorrect"
    failure_message: "What went wrong"
    success_message: "What went right"
```

For domains with many rules, you can organize them into a **directory** instead of a single file. Create `skill_evaluator/domains/my-domain/` and place multiple `.yaml` files inside — all rules are automatically merged at load time.

We currently ship with Statistics, Causal Inference, Experiment Design, Data Science, and Digital Marketing. This is meant to be extensible. If you have domain expertise in another area (e.g., finance, healthcare, NLP evaluation, survey design, product management) and want to contribute a rule set, open a PR and we'll review it. The more domains covered, the more useful this tool becomes for everyone.

---

## CI Integration

### GitHub Actions

```yaml
- name: Evaluate Skills
  run: |
    pip install -e ./skill-evaluator
    skill-eval ./skills/my-skill/ --fail-below 70 --format json
```

### As a Pre-commit Hook

```bash
skill-eval ./skills/ --fail-below 60
```

---

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run against your own skills
skill-eval ../skills/experiment-designer/
skill-eval ../skills/stats-reviewer/
```

---

## How Scoring Works

Each dimension (Structure, Security, Quality, Domain Correctness, Maintenance) produces a 0–100 score. These are combined into a weighted composite, normalized by the total weight of applicable dimensions.

A few things worth knowing:

**Security is a gate, not just a weight.** If the security analyzer finds critical risks (prompt injection, credential harvesting, destructive shell commands), the overall score is hard-capped regardless of how well the skill scores on other dimensions. A skill with a prompt injection vulnerability gets an F even if the content is otherwise excellent.

**Domain correctness uses a two-tier severity model.** Rules flagged as `incorrect` (e.g., recommending last-click attribution as the only model, or computing CLV without a proper probabilistic framework) carry heavier penalties than those flagged as `suspicious` (best-practice recommendations that may vary by context). This lets the evaluator distinguish hard errors from soft guidance.

**Scores are normalized by applicable checks.** Quality and maintenance scores are computed as the ratio of passed checks to applicable checks. A concise, well-written skill won't score lower than a verbose one just because it has fewer regex matches. Each check that fires gets an equal vote.

**Structural penalties are weighted by severity.** Missing your SKILL.md entirely costs more than missing a recommended field. The penalty for each finding reflects how much it actually impacts usability.

**What the scores don't tell you.** The current system is a static linter — it checks patterns in text. It can't tell you whether the skill actually makes an agent perform better, or whether the domain guidance is semantically correct beyond keyword matching. Those are harder problems (see below).

---

## Future Research

These are directions we'd like to explore. Contributions welcome.

**Empirical weight calibration.** The dimension weights (Security 20%, Domain 25%, etc.) are based on informed judgment, not data. The right approach is to score a labeled corpus of known-good vs. known-bad skills and use the results to find weights that best predict the label. If you have a labeled skill corpus or want to help build one, open an issue.

**Semantic domain checks.** The domain correctness analyzer currently uses regex patterns — it checks whether certain keywords appear, not whether the guidance is actually correct. Replacing this with embedding-based or lightweight LLM checks (e.g., "does this skill enforce power analysis, or just mention it?") would substantially improve accuracy.

**Behavioral evaluation.** The ultimate test of a skill is: does an agent using it produce better outputs? A test harness with known-correct answers (e.g., "given this dataset, should the agent refuse to run the test?") would let us score skills by downstream impact rather than surface patterns. This is the direction taken by SkillsBench-style evaluations and would make this tool a performance predictor, not just a linter.

**More domains.** We're actively expanding domain coverage. Next candidates include finance, healthcare, software engineering, and product management. Contributions welcome — each new domain just requires a YAML rule set and test fixtures.

---

## License

[MIT](LICENSE) — Use freely, attribute kindly.
