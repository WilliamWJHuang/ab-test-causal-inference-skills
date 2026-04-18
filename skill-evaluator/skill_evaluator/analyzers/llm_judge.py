"""
LLM-as-Judge — semantic domain correctness verifier.

Uses an LLM to re-evaluate domain rules that regex flagged as failing.
This catches false negatives (skill uses different terminology but is
semantically correct) and false positives (keywords match but guidance
is actually wrong).

Design: regex is the fast filter (runs first, free). LLM only fires on
regex failures to verify semantically. This saves ~70% of LLM calls.
Antipattern matches (exact string) are never overridden by the LLM.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skill_evaluator.analyzers.domain import DomainRule


# ── Defaults ─────────────────────────────────────────────────────────────────

PROVIDER_DEFAULTS = {
    "openai": {
        "model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
    },
    "anthropic": {
        "model": "claude-sonnet-4-5-20250514",
        "env_key": "ANTHROPIC_API_KEY",
    },
    "google": {
        "model": "gemini-2.0-flash",
        "env_key": "GOOGLE_API_KEY",
    },
}

CONFIDENCE_THRESHOLD = 0.7  # LLM must be at least this confident to override


# ── Data structures ──────────────────────────────────────────────────────────

@dataclass
class LlmVerdict:
    """LLM's semantic judgment on a single domain rule."""

    rule_name: str
    passed: bool
    confidence: float  # 0.0 to 1.0
    explanation: str
    evidence: str  # Quoted passage from skill
    override_regex: bool = False  # Whether this should override the regex FAIL


# ── Prompt construction ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an expert domain reviewer. Your job is to evaluate whether an AI agent \
skill correctly addresses specific methodological rules. You must judge \
SEMANTICALLY — the skill may use different terminology or phrasing, and that is \
acceptable if the underlying concept is correctly covered.

You will receive a list of rules that the skill was flagged as potentially \
failing. For each rule, determine whether the skill actually satisfies it \
despite using different wording.

Be rigorous but fair. If the concept is genuinely present (even in different \
words), mark it as passed. If the concept is truly absent or incorrectly \
stated, mark it as failed."""


def build_verification_prompt(
    skill_content: str,
    failed_rules: list[DomainRule],
    domain: str,
) -> str:
    """Build the evaluation prompt for a batch of failed rules."""
    rules_section = []
    for i, rule in enumerate(failed_rules, 1):
        # Convert regex patterns to natural language for the LLM
        required_nl = ", ".join(
            p.replace("|", " or ").replace("\\.", ".").replace(".*", " ... ")
            for p in rule.required_patterns
        )
        rules_section.append(
            f"### Rule {i}: {rule.name}\n"
            f"**Description:** {rule.description.strip()}\n"
            f"**What to look for:** {required_nl}\n"
            f"**Failure severity:** {rule.failure_severity}"
        )

    rules_text = "\n\n".join(rules_section)

    # Truncate skill content to ~6000 chars to stay within token limits
    max_content = 6000
    if len(skill_content) > max_content:
        skill_content = skill_content[:max_content] + "\n\n[... content truncated ...]"

    return f"""\
## Domain: {domain}

## Rules to Verify
The following rules were flagged as potentially failing by keyword matching. \
Re-evaluate each one SEMANTICALLY.

{rules_text}

## Skill Content
```
{skill_content}
```

## Instructions
For EACH rule above, determine whether the skill semantically satisfies it. \
Respond with a JSON array — one object per rule, in the same order:

```json
[
  {{
    "rule_name": "rule-name-here",
    "passed": true,
    "confidence": 0.85,
    "explanation": "The skill covers this concept by discussing X in the Y section.",
    "evidence": "direct quote from the skill that supports your judgment"
  }}
]
```

Rules:
- "passed": true if the concept IS present (even in different words), false if truly absent
- "confidence": 0.0 to 1.0, how confident you are in this judgment
- "explanation": brief rationale
- "evidence": exact quote from the skill (or empty string if not found)

Respond ONLY with the JSON array, no other text."""


# ── LLM client abstraction ──────────────────────────────────────────────────

def _call_openai(prompt: str, system: str, model: str) -> str:
    """Call OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "OpenAI package not installed. Run: pip install agent-skill-evaluator[llm]"
        )

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


def _call_anthropic(prompt: str, system: str, model: str) -> str:
    """Call Anthropic API."""
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError(
            "Anthropic package not installed. Run: pip install agent-skill-evaluator[llm]"
        )

    client = Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return response.content[0].text


def _call_google(prompt: str, system: str, model: str) -> str:
    """Call Google Gemini API."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError(
            "Google GenAI package not installed. Run: pip install agent-skill-evaluator[llm]"
        )

    client = genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    return response.text or ""


PROVIDER_CALLERS = {
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "google": _call_google,
}


# ── Response parsing ─────────────────────────────────────────────────────────

def parse_llm_response(raw: str, expected_rules: list[DomainRule]) -> list[LlmVerdict]:
    """Parse the LLM's JSON response into LlmVerdict objects.

    Handles edge cases: markdown fences, extra text, missing fields.
    """
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    # Try to extract JSON array from response
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON array in the text
        import re

        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return _fallback_verdicts(expected_rules)
        else:
            return _fallback_verdicts(expected_rules)

    # Handle case where OpenAI wraps in {"results": [...]}
    if isinstance(data, dict):
        for key in ("results", "rules", "verdicts", "evaluations"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            return _fallback_verdicts(expected_rules)

    if not isinstance(data, list):
        return _fallback_verdicts(expected_rules)

    verdicts = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue

        rule_name = item.get("rule_name", "")
        # Fall back to expected rule name if LLM didn't echo it
        if not rule_name and i < len(expected_rules):
            rule_name = expected_rules[i].name

        passed = bool(item.get("passed", False))
        confidence = float(item.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        verdict = LlmVerdict(
            rule_name=rule_name,
            passed=passed,
            confidence=confidence,
            explanation=str(item.get("explanation", "")),
            evidence=str(item.get("evidence", "")),
            override_regex=passed and confidence >= CONFIDENCE_THRESHOLD,
        )
        verdicts.append(verdict)

    return verdicts


def _fallback_verdicts(rules: list[DomainRule]) -> list[LlmVerdict]:
    """Return conservative fallback verdicts when parsing fails."""
    return [
        LlmVerdict(
            rule_name=rule.name,
            passed=False,
            confidence=0.0,
            explanation="LLM response could not be parsed. Falling back to regex result.",
            evidence="",
            override_regex=False,
        )
        for rule in rules
    ]


# ── Main judge class ─────────────────────────────────────────────────────────

class LlmJudge:
    """Semantic domain correctness verifier using LLM-as-judge.

    Usage:
        judge = LlmJudge(provider="google")
        verdicts = judge.verify_failed_rules(content, failed_rules, "statistics")
    """

    def __init__(self, provider: str, model: str | None = None):
        if provider not in PROVIDER_DEFAULTS:
            raise ValueError(
                f"Unknown LLM provider '{provider}'. "
                f"Supported: {', '.join(PROVIDER_DEFAULTS.keys())}"
            )

        self.provider = provider
        defaults = PROVIDER_DEFAULTS[provider]
        self.model = model or defaults["model"]
        self.env_key = defaults["env_key"]

        # Validate API key is available
        if not os.environ.get(self.env_key):
            raise EnvironmentError(
                f"API key not found. Set the {self.env_key} environment variable.\n"
                f"  Example: export {self.env_key}=your-key-here"
            )

        self._caller = PROVIDER_CALLERS[provider]

    def verify_failed_rules(
        self,
        skill_content: str,
        failed_rules: list[DomainRule],
        domain: str,
    ) -> list[LlmVerdict]:
        """Re-check regex-failed rules semantically using the LLM.

        Args:
            skill_content: Full text of the SKILL.md (+ references).
            failed_rules: Rules that regex flagged as failing.
            domain: Detected domain name.

        Returns:
            List of LlmVerdict objects, one per failed rule.
        """
        if not failed_rules:
            return []

        prompt = build_verification_prompt(skill_content, failed_rules, domain)

        try:
            raw_response = self._caller(prompt, SYSTEM_PROMPT, self.model)
        except Exception as e:
            # Graceful degradation — return conservative verdicts
            print(
                f"  [LLM] Warning: {self.provider} call failed: {e}",
                file=sys.stderr,
            )
            return _fallback_verdicts(failed_rules)

        return parse_llm_response(raw_response, failed_rules)

    def __repr__(self) -> str:
        return f"LlmJudge(provider={self.provider!r}, model={self.model!r})"
