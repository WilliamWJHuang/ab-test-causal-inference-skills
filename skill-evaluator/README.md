<p align="center">
  <h1 align="center">🔍 skill-evaluator</h1>
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
- Is it **domain-correct**? (does it recommend the right statistical test? the right causal method?)
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

| Dimension | Weight | What It Checks |
|:---|:---:|:---|
| **Structure** | 15% | YAML frontmatter, required fields, section organization |
| **Security** | 20% | Shell injection, credential exfil, prompt injection, obfuscation |
| **Quality** | 15% | Decision trees, guardrails, edge cases, escape hatches, code templates |
| **Domain Correctness** | 25% | Rule-based verification of domain-specific methodology |
| **Maintenance** | 15% | File freshness, docs, tests, CI config, git signals |

### Grading Scale

| Grade | Score Range | Meaning |
|:---:|:---:|:---|
| A+ | 95–100 | Exceptional — install with confidence |
| A | 90–94 | Excellent — high quality, well-maintained |
| B+ | 80–84 | Good — solid skill with some gaps |
| B | 75–79 | Above average — usable but review findings |
| C+ | 65–69 | Fair — significant gaps, use with caution |
| D | 40–49 | Very poor — not recommended |
| F | 0–39 | Failing — critical issues, do not install |

---

## Domain Correctness Rules

The **novel differentiator**. Unlike security/structure checks that any tool can do, domain correctness verifies the *guidance itself* is correct.

### Built-in Domains

| Domain | Rules | Checks |
|:---|:---:|:---|
| **Statistics** | 8 | Normality assumptions, effect sizes, multiple comparisons, power analysis, seed sensitivity |
| **Causal Inference** | 8 | Identification strategies, parallel trends, IV assumptions, RDD bandwidth, matching balance |
| **Data Science** | 5 | Data leakage, missing data mechanisms, cross-validation, metric selection, outlier handling |

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

We ship with Statistics, Causal Inference, and Data Science domains, but this is meant to be extensible. If you have domain expertise in another area (e.g., epidemiology, finance, NLP evaluation, survey design) and want to contribute a rule set, open a PR with your YAML file and we'll review it. The more domains covered, the more useful this tool becomes for everyone.

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

## License

[MIT](../LICENSE) — Use freely, attribute kindly.
