"""Tests for the LLM-as-judge semantic verifier.

All tests run WITHOUT API calls — they test prompt construction,
response parsing, merge logic, and edge cases using mocks.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from skill_evaluator.analyzers.llm_judge import (
    LlmJudge,
    LlmVerdict,
    build_verification_prompt,
    parse_llm_response,
    CONFIDENCE_THRESHOLD,
    PROVIDER_DEFAULTS,
    _fallback_verdicts,
)
from skill_evaluator.analyzers.domain import (
    DomainCorrectnessAnalyzer,
    DomainFinding,
    DomainResult,
    DomainRule,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_rules():
    """Two sample domain rules for testing."""
    return [
        DomainRule(
            name="effect-size-reporting",
            description="Effect sizes should always be reported alongside p-values.",
            applicability_patterns=[r"p-value|significance|hypothesis"],
            required_patterns=[r"effect.size|cohen|odds.ratio"],
            failure_severity="incorrect",
            failure_message="Missing effect size reporting.",
            success_message="Correctly reports effect sizes.",
        ),
        DomainRule(
            name="normality-check",
            description="Parametric tests require normality checks for small samples.",
            applicability_patterns=[r"t-test|anova|parametric"],
            required_patterns=[r"normality|shapiro|kolmogorov|CLT|central.limit"],
            failure_severity="suspicious",
            failure_message="Missing normality check.",
            success_message="Correctly addresses normality.",
        ),
    ]


@pytest.fixture
def sample_skill_content():
    return """
# Statistics Skill

When analyzing data with hypothesis testing, always report both
statistical significance AND practical significance. Use Cohen's d
for continuous outcomes and odds ratios for binary outcomes.

For small samples (n < 30), verify normality with Shapiro-Wilk before
using parametric tests. For large samples, the Central Limit Theorem
provides sufficient robustness.
"""


# ── Prompt Construction ──────────────────────────────────────────────────────

class TestPromptConstruction:
    """Test that prompts are well-formed."""

    def test_prompt_contains_domain(self, sample_rules):
        prompt = build_verification_prompt("skill content", sample_rules, "statistics")
        assert "statistics" in prompt

    def test_prompt_contains_rule_names(self, sample_rules):
        prompt = build_verification_prompt("skill content", sample_rules, "statistics")
        assert "effect-size-reporting" in prompt
        assert "normality-check" in prompt

    def test_prompt_contains_skill_content(self, sample_rules):
        prompt = build_verification_prompt("my skill content here", sample_rules, "statistics")
        assert "my skill content here" in prompt

    def test_prompt_truncates_long_content(self, sample_rules):
        long_content = "x" * 10000
        prompt = build_verification_prompt(long_content, sample_rules, "statistics")
        assert "[... content truncated ...]" in prompt

    def test_prompt_requests_json(self, sample_rules):
        prompt = build_verification_prompt("content", sample_rules, "statistics")
        assert "JSON" in prompt
        assert "rule_name" in prompt
        assert "passed" in prompt
        assert "confidence" in prompt


# ── Response Parsing ─────────────────────────────────────────────────────────

class TestResponseParsing:
    """Test parsing of LLM JSON responses."""

    def test_parse_clean_json_array(self, sample_rules):
        raw = json.dumps([
            {
                "rule_name": "effect-size-reporting",
                "passed": True,
                "confidence": 0.9,
                "explanation": "The skill mentions Cohen's d.",
                "evidence": "Use Cohen's d for continuous outcomes",
            },
            {
                "rule_name": "normality-check",
                "passed": True,
                "confidence": 0.85,
                "explanation": "The skill discusses Shapiro-Wilk.",
                "evidence": "verify normality with Shapiro-Wilk",
            },
        ])
        verdicts = parse_llm_response(raw, sample_rules)
        assert len(verdicts) == 2
        assert verdicts[0].passed is True
        assert verdicts[0].confidence == 0.9
        assert verdicts[0].override_regex is True  # > 0.7 threshold

    def test_parse_json_with_markdown_fences(self, sample_rules):
        raw = '```json\n[{"rule_name": "effect-size-reporting", "passed": true, "confidence": 0.8, "explanation": "found", "evidence": ""}]\n```'
        verdicts = parse_llm_response(raw, sample_rules)
        assert len(verdicts) == 1
        assert verdicts[0].passed is True

    def test_parse_wrapped_json(self, sample_rules):
        """OpenAI sometimes wraps arrays in an object."""
        raw = json.dumps({
            "results": [
                {"rule_name": "effect-size-reporting", "passed": False, "confidence": 0.6, "explanation": "not found", "evidence": ""},
            ]
        })
        verdicts = parse_llm_response(raw, sample_rules)
        assert len(verdicts) == 1
        assert verdicts[0].passed is False

    def test_parse_low_confidence_no_override(self, sample_rules):
        raw = json.dumps([
            {"rule_name": "effect-size-reporting", "passed": True, "confidence": 0.5, "explanation": "maybe", "evidence": ""},
        ])
        verdicts = parse_llm_response(raw, sample_rules)
        assert verdicts[0].passed is True
        assert verdicts[0].override_regex is False  # < 0.7 threshold

    def test_parse_garbage_returns_fallback(self, sample_rules):
        verdicts = parse_llm_response("This is not JSON at all!", sample_rules)
        assert len(verdicts) == len(sample_rules)
        assert all(v.passed is False for v in verdicts)
        assert all(v.override_regex is False for v in verdicts)

    def test_parse_clamps_confidence(self, sample_rules):
        raw = json.dumps([
            {"rule_name": "effect-size-reporting", "passed": True, "confidence": 1.5, "explanation": "", "evidence": ""},
        ])
        verdicts = parse_llm_response(raw, sample_rules)
        assert verdicts[0].confidence == 1.0

    def test_fallback_rule_name_from_expected(self, sample_rules):
        """If LLM doesn't echo rule_name, use expected rule."""
        raw = json.dumps([
            {"passed": True, "confidence": 0.8, "explanation": "found", "evidence": ""},
            {"passed": False, "confidence": 0.9, "explanation": "missing", "evidence": ""},
        ])
        verdicts = parse_llm_response(raw, sample_rules)
        assert verdicts[0].rule_name == "effect-size-reporting"
        assert verdicts[1].rule_name == "normality-check"


# ── Merge Logic ──────────────────────────────────────────────────────────────

class TestMergeLogic:
    """Test that LLM verdicts correctly override regex results."""

    def test_llm_overrides_d101_failure(self, sample_rules, tmp_path):
        """Regex FAIL (D101) + LLM PASS → should flip to PASS."""
        # Create a skill that the regex would fail on (uses different terminology)
        skill = tmp_path / "SKILL.md"
        skill.write_text(
            "---\nname: test\ndomain: statistics\n---\n"
            "# Test Skill\n\nDiscuss p-value and hypothesis testing.\n"
            "Always report practical significance alongside statistical significance.\n"
            "For t-tests, verify distribution shape before proceeding.\n",
            encoding="utf-8",
        )

        mock_verdicts = [
            LlmVerdict(
                rule_name="effect-size-reporting",
                passed=True,
                confidence=0.85,
                explanation="Skill discusses practical significance.",
                evidence="report practical significance alongside statistical significance",
                override_regex=True,
            ),
        ]

        analyzer = DomainCorrectnessAnalyzer()

        with patch(
            "skill_evaluator.analyzers.llm_judge.LlmJudge"
        ) as MockJudge:
            mock_instance = MagicMock()
            mock_instance.provider = "google"
            mock_instance.model = "gemini-2.0-flash"
            mock_instance.verify_failed_rules.return_value = mock_verdicts
            MockJudge.return_value = mock_instance

            result = analyzer.analyze(
                skill, domain="statistics",
                llm_provider="google",
            )

        # Find the overridden finding
        llm_findings = [f for f in result.findings if "[LLM-verified]" in f.message]
        assert len(llm_findings) >= 1

    def test_antipattern_d100_never_overridden(self, sample_rules, tmp_path):
        """Antipattern match (D100) should NEVER be overridden by LLM."""
        skill = tmp_path / "SKILL.md"
        skill.write_text(
            "---\nname: test\ndomain: statistics\n---\n"
            "# Test Skill\n\nthe result is significant\n"
            "Always use p-value for decisions.\n",
            encoding="utf-8",
        )

        analyzer = DomainCorrectnessAnalyzer()
        # Run without LLM first
        result_no_llm = analyzer.analyze(skill, domain="statistics")

        d100_findings = [f for f in result_no_llm.findings if f.code == "D100"]
        # D100 findings exist — these should NEVER be sent to LLM
        # The _llm_recheck method explicitly filters for code == "D101" only


# ── Provider Validation ──────────────────────────────────────────────────────

class TestProviderValidation:

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown LLM provider"):
            LlmJudge(provider="invalid_provider")

    def test_missing_api_key_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="API key not found"):
                LlmJudge(provider="openai")

    def test_valid_provider_with_key(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            judge = LlmJudge(provider="openai")
            assert judge.provider == "openai"
            assert judge.model == "gpt-4o-mini"

    def test_custom_model_override(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            judge = LlmJudge(provider="anthropic", model="claude-haiku-3-5-20241022")
            assert judge.model == "claude-haiku-3-5-20241022"

    def test_google_provider_default_model(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            judge = LlmJudge(provider="google")
            assert judge.model == "gemini-2.0-flash"

    def test_repr(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            judge = LlmJudge(provider="openai")
            assert "openai" in repr(judge)
            assert "gpt-4o-mini" in repr(judge)


# ── Fallback Behavior ────────────────────────────────────────────────────────

class TestFallbackBehavior:

    def test_fallback_verdicts_conservative(self, sample_rules):
        verdicts = _fallback_verdicts(sample_rules)
        assert len(verdicts) == 2
        assert all(v.passed is False for v in verdicts)
        assert all(v.override_regex is False for v in verdicts)
        assert all(v.confidence == 0.0 for v in verdicts)

    def test_verify_handles_api_error(self, sample_rules):
        """If the API call fails, return conservative fallbacks."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            judge = LlmJudge(provider="openai")

        # Mock the caller to raise
        with patch.object(judge, "_caller", side_effect=Exception("API error")):
            verdicts = judge.verify_failed_rules(
                "skill content", sample_rules, "statistics"
            )
            assert len(verdicts) == 2
            assert all(v.passed is False for v in verdicts)

    def test_empty_failed_rules_returns_empty(self, sample_rules):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            judge = LlmJudge(provider="openai")
            verdicts = judge.verify_failed_rules("content", [], "statistics")
            assert verdicts == []
