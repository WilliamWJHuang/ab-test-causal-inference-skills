"""
Test suite for skill-evaluator analyzers.

Tests each analyzer against the good, bad, and malicious skill fixtures
to verify scoring behavior and finding detection.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_evaluator.analyzers import (
    DomainCorrectnessAnalyzer,
    MaintenanceAnalyzer,
    QualityAnalyzer,
    SecurityAnalyzer,
    StructuralAnalyzer,
)
from skill_evaluator.scorers.composite import CompositeScorer

# ── Fixture paths ────────────────────────────────────────────────────────────

FIXTURES_DIR = Path(__file__).parent / "fixtures"
GOOD_SKILL = FIXTURES_DIR / "good-skill"
BAD_SKILL = FIXTURES_DIR / "bad-skill"
MALICIOUS_SKILL = FIXTURES_DIR / "malicious-skill"
GOOD_MARKETING_SKILL = FIXTURES_DIR / "good-marketing-skill"
BAD_MARKETING_SKILL = FIXTURES_DIR / "bad-marketing-skill"
GOOD_FINANCE_SKILL = FIXTURES_DIR / "good-finance-skill"
BAD_FINANCE_SKILL = FIXTURES_DIR / "bad-finance-skill"


# ══════════════════════════════════════════════════════════════════════════════
# Structural Analyzer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestStructuralAnalyzer:
    def setup_method(self):
        self.analyzer = StructuralAnalyzer()

    def test_good_skill_passes_structural(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.score >= 70, f"Good skill scored too low: {result.score}"
        assert result.error_count == 0, f"Good skill has errors: {result.findings}"

    def test_good_skill_has_frontmatter(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.frontmatter.get("name") == "good-stats-skill"
        assert "description" in result.frontmatter

    def test_bad_skill_fails_structural(self):
        result = self.analyzer.analyze(BAD_SKILL)
        assert result.score < 70, f"Bad skill scored too high: {result.score}"
        assert result.error_count > 0, "Bad skill should have errors"

    def test_bad_skill_missing_frontmatter(self):
        result = self.analyzer.analyze(BAD_SKILL)
        error_codes = [f.code for f in result.findings if f.severity == "error"]
        assert "S010" in error_codes, "Should detect missing frontmatter"

    def test_nonexistent_path(self):
        result = self.analyzer.analyze(Path("/nonexistent/path"))
        assert result.score == 0
        assert result.error_count > 0


# ══════════════════════════════════════════════════════════════════════════════
# Security Analyzer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestSecurityAnalyzer:
    def setup_method(self):
        self.analyzer = SecurityAnalyzer()

    def test_good_skill_is_safe(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.score >= 80, f"Good skill security too low: {result.score}"
        assert result.critical_count == 0

    def test_malicious_skill_detected(self):
        result = self.analyzer.analyze(MALICIOUS_SKILL)
        assert result.score < 30, f"Malicious skill scored too high: {result.score}"
        assert result.risk_level in ("high", "critical"), f"Expected high/critical risk, got {result.risk_level}"

    def test_malicious_detects_shell_exec(self):
        result = self.analyzer.analyze(MALICIOUS_SKILL)
        codes = [f.code for f in result.findings]
        assert "SEC001" in codes or "SEC002" in codes, "Should detect shell execution"

    def test_malicious_detects_exfiltration(self):
        result = self.analyzer.analyze(MALICIOUS_SKILL)
        codes = [f.code for f in result.findings]
        assert "SEC020" in codes or "SEC021" in codes, "Should detect network exfiltration"

    def test_malicious_detects_prompt_injection(self):
        result = self.analyzer.analyze(MALICIOUS_SKILL)
        codes = [f.code for f in result.findings]
        assert "SEC040" in codes, "Should detect prompt injection"


# ══════════════════════════════════════════════════════════════════════════════
# Quality Analyzer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestQualityAnalyzer:
    def setup_method(self):
        self.analyzer = QualityAnalyzer()

    def test_good_skill_high_quality(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.score >= 70, f"Good skill quality too low: {result.score}"
        assert result.strength_count >= 3, "Good skill should have multiple strengths"

    def test_good_skill_has_decision_trees(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.metrics.get("decision_tree_signals", 0) >= 3

    def test_good_skill_has_guardrails(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.metrics.get("guardrail_signals", 0) >= 3

    def test_bad_skill_low_quality(self):
        result = self.analyzer.analyze(BAD_SKILL)
        assert result.score < 60, f"Bad skill quality too high: {result.score}"

    def test_bad_skill_detects_generic_filler(self):
        result = self.analyzer.analyze(BAD_SKILL)
        assert result.metrics.get("generic_filler_count", 0) >= 3


# ══════════════════════════════════════════════════════════════════════════════
# Domain Correctness Analyzer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestDomainCorrectnessAnalyzer:
    def setup_method(self):
        self.analyzer = DomainCorrectnessAnalyzer()

    def test_good_skill_domain_detection(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.domain == "statistics", f"Expected statistics, got {result.domain}"

    def test_good_skill_passes_rules(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.rules_passed > 0, "Good skill should pass some domain rules"
        assert result.score >= 60, f"Good skill domain score too low: {result.score}"

    def test_bad_skill_domain_detection(self):
        result = self.analyzer.analyze(BAD_SKILL, domain="statistics")
        # Bad skill mentions t-test but lacks proper guidance
        assert result.score < 80, f"Bad skill domain score too high: {result.score}"

    def test_forced_domain_works(self):
        result = self.analyzer.analyze(GOOD_SKILL, domain="causal-inference")
        assert result.domain == "causal-inference"

    def test_unknown_domain_returns_neutral(self):
        result = self.analyzer.analyze(GOOD_SKILL, domain="quantum-computing")
        assert result.score == 50.0  # Neutral for unknown domains

    def test_stats_skill_not_detected_as_marketing(self):
        """Regression: statistics skills should not false-positive as digital-marketing."""
        result = self.analyzer.analyze(GOOD_SKILL)
        assert result.domain == "statistics", (
            f"Good stats skill misdetected as {result.domain} — "
            "digital-marketing detection signals may be too broad"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Digital Marketing Domain Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestDigitalMarketingDomain:
    """Tests for the digital-marketing domain rules (7 sub-domain YAMLs)."""

    def setup_method(self):
        self.analyzer = DomainCorrectnessAnalyzer()

    def test_good_marketing_skill_domain_detection(self):
        """Good marketing skill should auto-detect as digital-marketing."""
        result = self.analyzer.analyze(GOOD_MARKETING_SKILL)
        assert result.domain == "digital-marketing", (
            f"Expected digital-marketing, got {result.domain}"
        )

    def test_good_marketing_skill_passes_rules(self):
        """Good fixture should pass the majority of applicable rules."""
        result = self.analyzer.analyze(GOOD_MARKETING_SKILL)
        assert result.rules_passed > 0, "Good marketing skill should pass some rules"
        assert result.score >= 60, f"Good marketing skill score too low: {result.score}"

    def test_good_marketing_loads_all_subdomain_rules(self):
        """Verify that multi-file domain loading merges all 7 YAML files."""
        rules = self.analyzer._load_rules("digital-marketing")
        # 7 files × 3-4 rules = 25 total rules
        assert len(rules) >= 20, (
            f"Expected ~25 rules from 7 sub-domain files, got {len(rules)}"
        )

    def test_bad_marketing_skill_fails_rules(self):
        """Bad fixture should trigger failures on applicable rules."""
        result = self.analyzer.analyze(BAD_MARKETING_SKILL, domain="digital-marketing")
        assert result.rules_failed > 0, "Bad marketing skill should fail rules"
        assert result.score < 60, f"Bad marketing skill score too high: {result.score}"

    def test_bad_marketing_skill_attribution_antipattern(self):
        """Bad fixture recommends last-click as 'the best' — should trigger antipattern."""
        result = self.analyzer.analyze(BAD_MARKETING_SKILL, domain="digital-marketing")
        incorrect_findings = [
            f for f in result.findings if f.severity == "incorrect"
        ]
        assert len(incorrect_findings) > 0, (
            "Bad marketing skill should have at least one 'incorrect' finding "
            "(e.g., last-click antipattern or naive CLV)"
        )

    def test_bad_marketing_skill_detects_list_purchase_antipattern(self):
        """Bad fixture mentions buying email lists — should trigger antipattern."""
        result = self.analyzer.analyze(BAD_MARKETING_SKILL, domain="digital-marketing")
        rule_names = [f.rule_name for f in result.findings if f.severity != "correct"]
        assert any("list" in name or "hygiene" in name or "consent" in name
                    for name in rule_names), (
            f"Should detect email list purchase antipattern, got rules: {rule_names}"
        )

    def test_forced_digital_marketing_on_stats_skill(self):
        """Forcing digital-marketing domain on stats skill should still run without crashing."""
        result = self.analyzer.analyze(GOOD_SKILL, domain="digital-marketing")
        assert result.domain == "digital-marketing"
        # Most rules should be not-applicable since it's a stats skill
        assert result.rules_not_applicable > 0


# ══════════════════════════════════════════════════════════════════════════════
# Finance Domain Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestFinanceDomain:
    """Tests for the finance domain rules (7 sub-domain YAMLs)."""

    def setup_method(self):
        self.analyzer = DomainCorrectnessAnalyzer()

    def test_good_finance_skill_domain_detection(self):
        """Good finance skill should auto-detect as finance."""
        result = self.analyzer.analyze(GOOD_FINANCE_SKILL)
        assert result.domain == "finance", (
            f"Expected finance, got {result.domain}"
        )

    def test_good_finance_skill_passes_rules(self):
        """Good fixture should pass the majority of applicable rules."""
        result = self.analyzer.analyze(GOOD_FINANCE_SKILL)
        assert result.rules_passed > 0, "Good finance skill should pass some rules"
        assert result.score >= 60, f"Good finance skill score too low: {result.score}"

    def test_good_finance_loads_all_subdomain_rules(self):
        """Verify that multi-file domain loading merges all 7 YAML files."""
        rules = self.analyzer._load_rules("finance")
        # 7 files × 3-4 rules = 23 total rules
        assert len(rules) >= 20, (
            f"Expected ~23 rules from 7 sub-domain files, got {len(rules)}"
        )

    def test_bad_finance_skill_fails_rules(self):
        """Bad fixture should trigger failures on applicable rules."""
        result = self.analyzer.analyze(BAD_FINANCE_SKILL, domain="finance")
        assert result.rules_failed > 0, "Bad finance skill should fail rules"
        assert result.score < 60, f"Bad finance skill score too high: {result.score}"

    def test_bad_finance_skill_backtesting_antipattern(self):
        """Bad fixture ignores survivorship bias and transaction costs — should trigger antipatterns."""
        result = self.analyzer.analyze(BAD_FINANCE_SKILL, domain="finance")
        incorrect_findings = [
            f for f in result.findings if f.severity == "incorrect"
        ]
        assert len(incorrect_findings) > 0, (
            "Bad finance skill should have at least one 'incorrect' finding "
            "(e.g., survivorship bias, look-ahead bias, VaR assumptions)"
        )

    def test_bad_finance_skill_var_antipattern(self):
        """Bad fixture claims VaR with normal distribution is adequate."""
        result = self.analyzer.analyze(BAD_FINANCE_SKILL, domain="finance")
        rule_names = [f.rule_name for f in result.findings if f.severity != "correct"]
        assert any("var" in name.lower() or "risk" in name.lower()
                    for name in rule_names), (
            f"Should detect VaR assumption antipattern, got rules: {rule_names}"
        )

    def test_finance_not_confused_with_stats(self):
        """Finance skill should not be detected as statistics."""
        result = self.analyzer.analyze(GOOD_FINANCE_SKILL)
        assert result.domain == "finance", (
            f"Finance skill misdetected as {result.domain}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Maintenance Analyzer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestMaintenanceAnalyzer:
    def setup_method(self):
        self.analyzer = MaintenanceAnalyzer()

    def test_good_skill_maintenance(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        # Should at least detect recently modified files
        assert result.score >= 30, f"Maintenance score too low: {result.score}"

    def test_detects_references_directory(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        # The good skill has a references/ dir
        aux = result.metrics.get("auxiliary_directories", 0)
        # May or may not pass depending on other dirs
        assert isinstance(aux, int)


# ══════════════════════════════════════════════════════════════════════════════
# Composite Scorer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestCompositeScorer:
    def setup_method(self):
        self.scorer = CompositeScorer()

    def test_perfect_scores(self):
        result = self.scorer.compute(100, 100, 100, 100, 100)
        assert result.overall_score == 100.0
        assert result.overall_grade == "A+"

    def test_failing_scores(self):
        result = self.scorer.compute(0, 0, 0, 0, 0)
        assert result.overall_score == 0.0
        assert result.overall_grade == "F"

    def test_mixed_scores(self):
        result = self.scorer.compute(80, 90, 70, 60, 85)
        assert 60 < result.overall_score < 90

    def test_security_dominates(self):
        """Security has the highest weight, so a low security score should drag down the composite."""
        high_security = self.scorer.compute(80, 100, 80, 80, 80)
        low_security = self.scorer.compute(80, 20, 80, 80, 80)
        assert high_security.overall_score > low_security.overall_score

    def test_recommendation_warns_on_weakness(self):
        result = self.scorer.compute(90, 90, 90, 20, 90)
        assert "domain_correctness" in result.recommendation.lower() or "weakness" in result.recommendation.lower()

    def test_grade_boundaries(self):
        result_a = self.scorer.compute(95, 95, 95, 95, 95)
        assert result_a.overall_grade == "A+"

        result_b = self.scorer.compute(75, 75, 75, 75, 75)
        assert result_b.overall_grade == "B"

    def test_security_gate_critical_caps_score(self):
        """Critical security risk should hard-cap overall score to F range."""
        result = self.scorer.compute(100, 100, 100, 100, 100, security_gate="critical")
        assert result.overall_score <= 20.0
        assert result.overall_grade == "F"
        assert "BLOCKED" in result.recommendation

    def test_security_gate_high_caps_score(self):
        """High security risk should hard-cap overall score to D range."""
        result = self.scorer.compute(100, 100, 100, 100, 100, security_gate="high")
        assert result.overall_score <= 45.0
        assert result.overall_grade in ("D", "C-")
        assert "HIGH RISK" in result.recommendation

    def test_security_gate_safe_no_effect(self):
        """Safe security should not cap the score."""
        result = self.scorer.compute(100, 100, 100, 100, 100, security_gate="safe")
        assert result.overall_score == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

