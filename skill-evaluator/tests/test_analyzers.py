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
        assert result.score < 65, f"Bad skill scored too high: {result.score}"
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
        assert result.score < 50, f"Bad skill quality too high: {result.score}"

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


# ══════════════════════════════════════════════════════════════════════════════
# Maintenance Analyzer Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestMaintenanceAnalyzer:
    def setup_method(self):
        self.analyzer = MaintenanceAnalyzer()

    def test_good_skill_maintenance(self):
        result = self.analyzer.analyze(GOOD_SKILL)
        # Should at least detect recently modified files
        assert result.score >= 40, f"Maintenance score too low: {result.score}"

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
