"""
Domain Correctness Analyzer — verifies domain-specific claims against rule sets.

This is the novel differentiator. Unlike structural/security analyzers that any
tool can implement, domain correctness checks whether the skill's *guidance*
is actually correct for its stated domain.

Supports YAML-based domain rule definitions for:
- Statistics (correct test selection, power analysis, effect sizes)
- Causal inference (identification strategies, refutation tests)
- Data science (leakage detection, cross-validation anti-patterns)
- Custom domains (user-extensible)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class DomainFinding:
    """A single domain correctness finding."""

    severity: str  # "correct", "suspicious", "incorrect", "missing"
    code: str
    message: str
    rule_name: str = ""
    detail: str = ""


@dataclass
class DomainResult:
    """Result of a domain correctness analysis."""

    score: float = 0.0
    domain: str = "unknown"
    findings: list[DomainFinding] = field(default_factory=list)
    rules_checked: int = 0
    rules_passed: int = 0
    rules_failed: int = 0
    rules_not_applicable: int = 0


@dataclass
class DomainRule:
    """A single domain correctness rule."""

    name: str
    description: str
    # If these patterns are found, the rule is applicable
    applicability_patterns: list[str]
    # Patterns that SHOULD be present if the rule is applicable (correct behavior)
    required_patterns: list[str]
    # Patterns that SHOULD NOT be present (anti-patterns / incorrect behavior)
    antipatterns: list[str] = field(default_factory=list)
    # Severity if the rule fails
    failure_severity: str = "suspicious"
    # Helpful message on failure
    failure_message: str = ""
    # Helpful message on success
    success_message: str = ""


# ── Built-in domain rules (loaded from YAML or defined inline) ───────────────

DOMAINS_DIR = Path(__file__).parent.parent / "domains"


class DomainCorrectnessAnalyzer:
    """Verifies domain-specific correctness of skill guidance."""

    def __init__(self, custom_domains_dir: Path | None = None):
        self.domains_dir = custom_domains_dir or DOMAINS_DIR
        self._rule_cache: dict[str, list[DomainRule]] = {}

    def analyze(
        self, skill_path: Path, domain: str | None = None
    ) -> DomainResult:
        """Analyze a skill for domain correctness."""
        result = DomainResult()

        # Read skill content
        skill_file = self._resolve_skill_file(skill_path)
        if skill_file is None:
            result.findings.append(
                DomainFinding(
                    severity="missing",
                    code="D001",
                    message="No SKILL.md file found for domain analysis.",
                )
            )
            result.score = 0.0
            return result

        content = skill_file.read_text(encoding="utf-8")

        # Also read reference files if they exist
        refs_dir = skill_file.parent / "references"
        full_content = content
        if refs_dir.is_dir():
            for ref_file in refs_dir.glob("*.md"):
                try:
                    full_content += "\n\n" + ref_file.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue

        # Detect or use specified domain
        detected_domain = domain or self._detect_domain(content)
        result.domain = detected_domain

        if detected_domain == "unknown":
            result.findings.append(
                DomainFinding(
                    severity="missing",
                    code="D010",
                    message="Could not detect skill domain. Specify a domain for correctness checking.",
                )
            )
            result.score = 50.0  # Neutral score if domain is unknown
            return result

        # Load domain rules
        rules = self._load_rules(detected_domain)
        if not rules:
            result.findings.append(
                DomainFinding(
                    severity="missing",
                    code="D011",
                    message=f"No domain rules found for '{detected_domain}'. Only built-in domains are supported.",
                )
            )
            result.score = 50.0
            return result

        # Check each rule
        for rule in rules:
            self._check_rule(rule, full_content, result)

        result.score = self._compute_score(result)
        return result

    def _resolve_skill_file(self, path: Path) -> Path | None:
        """Find the SKILL.md file from a path."""
        if path.is_file():
            return path
        if path.is_dir():
            for candidate in path.iterdir():
                if candidate.name.upper() == "SKILL.MD":
                    return candidate
        return None

    def _detect_domain(self, content: str) -> str:
        """Auto-detect the domain from skill content."""
        content_lower = content.lower()

        domain_signals: dict[str, list[str]] = {
            "statistics": [
                "statistical", "hypothesis test", "p-value", "confidence interval",
                "effect size", "power analysis", "t-test", "anova", "regression",
                "bootstrap", "bayesian", "frequentist",
            ],
            "causal-inference": [
                "causal", "treatment effect", "counterfactual", "instrumental variable",
                "difference-in-difference", "regression discontinuity", "propensity score",
                "synthetic control", "dowhy", "econml", "identification strategy",
            ],
            "data-science": [
                "data quality", "missing data", "imputation", "outlier",
                "feature engineering", "cross-validation", "data leakage",
                "train.*test.*split",
            ],
            "experiment-design": [
                "a/b test", "experiment design", "randomization", "sample size",
                "power analysis", "cuped", "variance reduction", "pre-registration",
            ],
            "digital-marketing": [
                "attribution", "marketing mix", "CLV", "customer lifetime value",
                "SEO", "SEM", "PPC", "pay per click", "ad spend", "ROAS",
                "return on ad spend", "conversion rate optimization", "CRO",
                "email marketing", "landing page", "funnel",
                "programmatic", "retargeting", "remarketing", "digital advertising",
                "google ads", "facebook ads", "meta ads", "social media marketing",
                "content marketing", "CTR", "click.through rate", "CPM", "CPC",
                "cost per click", "ad creative", "marketing automation",
            ],
        }

        scores: dict[str, int] = {}
        for domain, signals in domain_signals.items():
            score = 0
            for signal in signals:
                if re.search(signal, content_lower):
                    score += 1
            if score > 0:
                scores[domain] = score

        if not scores:
            return "unknown"

        return max(scores, key=scores.get)  # type: ignore[arg-type]

    def _load_rules(self, domain: str) -> list[DomainRule]:
        """Load rules for a given domain from YAML files.

        Supports two layouts:
          1. Single file:  domains/{domain}.yaml  (or with underscores)
          2. Directory:    domains/{domain}/*.yaml  (for multi-file domains)
        Both can coexist — rules are merged when both are present.
        """
        if domain in self._rule_cache:
            return self._rule_cache[domain]

        yaml_sources: list[Path] = []

        # --- Single-file lookup ---
        for name_variant in (domain, domain.replace("-", "_")):
            candidate = self.domains_dir / f"{name_variant}.yaml"
            if candidate.exists():
                yaml_sources.append(candidate)
                break  # Use first match

        # --- Directory lookup (multi-file domains) ---
        for name_variant in (domain, domain.replace("-", "_")):
            candidate_dir = self.domains_dir / name_variant
            if candidate_dir.is_dir():
                yaml_sources.extend(sorted(candidate_dir.glob("*.yaml")))
                break  # Use first match

        if not yaml_sources:
            self._rule_cache[domain] = []
            return []

        rules: list[DomainRule] = []
        for yaml_file in yaml_sources:
            try:
                raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            except (yaml.YAMLError, OSError):
                continue

            for rule_data in raw.get("rules", []):
                rules.append(
                    DomainRule(
                        name=rule_data.get("name", "unnamed"),
                        description=rule_data.get("description", ""),
                        applicability_patterns=rule_data.get("applicability_patterns", []),
                        required_patterns=rule_data.get("required_patterns", []),
                        antipatterns=rule_data.get("antipatterns", []),
                        failure_severity=rule_data.get("failure_severity", "suspicious"),
                        failure_message=rule_data.get("failure_message", ""),
                        success_message=rule_data.get("success_message", ""),
                    )
                )

        self._rule_cache[domain] = rules
        return rules

    def _check_rule(
        self, rule: DomainRule, content: str, result: DomainResult
    ) -> None:
        """Check a single domain rule against the content."""
        result.rules_checked += 1

        # First check: is this rule applicable?
        applicable = False
        for pattern in rule.applicability_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                applicable = True
                break

        if not applicable:
            result.rules_not_applicable += 1
            return

        # Check required patterns
        all_required_found = True
        missing_patterns = []
        for pattern in rule.required_patterns:
            if not re.search(pattern, content, re.IGNORECASE):
                all_required_found = False
                missing_patterns.append(pattern)

        # Check antipatterns
        antipattern_found = False
        matched_antipatterns = []
        for pattern in rule.antipatterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                antipattern_found = True
                matched_antipatterns.append(match.group(0)[:60])

        # Generate findings
        if antipattern_found:
            result.rules_failed += 1
            result.findings.append(
                DomainFinding(
                    severity="incorrect",
                    code="D100",
                    message=rule.failure_message or f"Anti-pattern detected for rule '{rule.name}'",
                    rule_name=rule.name,
                    detail=f"Matched: {', '.join(matched_antipatterns)}",
                )
            )
        elif not all_required_found:
            result.rules_failed += 1
            result.findings.append(
                DomainFinding(
                    severity=rule.failure_severity,
                    code="D101",
                    message=rule.failure_message or f"Missing required content for rule '{rule.name}'",
                    rule_name=rule.name,
                    detail=f"Rule: {rule.description}",
                )
            )
        else:
            result.rules_passed += 1
            result.findings.append(
                DomainFinding(
                    severity="correct",
                    code="D200",
                    message=rule.success_message or f"Passed: {rule.name}",
                    rule_name=rule.name,
                )
            )

    def _compute_score(self, result: DomainResult) -> float:
        """Compute a 0-100 domain correctness score."""
        applicable = result.rules_passed + result.rules_failed
        if applicable == 0:
            return 50.0  # No applicable rules → neutral score

        base_score = (result.rules_passed / applicable) * 100.0

        # Extra penalty for "incorrect" (vs "suspicious") findings
        incorrect_count = sum(
            1 for f in result.findings if f.severity == "incorrect"
        )
        penalty = incorrect_count * 10.0

        return max(0.0, min(100.0, base_score - penalty))
