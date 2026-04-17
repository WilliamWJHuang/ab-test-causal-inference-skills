"""
Quality Analyzer — assesses the depth, rigor, and completeness of a skill.

Heuristic checks for:
- Decision tree presence and depth
- Guardrail / refusal language
- Edge case handling
- "When NOT to use" documentation
- Output format specification
- Code template presence and quality
- Reference material depth
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QualityFinding:
    """A single quality finding."""

    severity: str  # "strength", "warning", "suggestion"
    code: str
    message: str
    detail: str = ""


@dataclass
class QualityResult:
    """Result of a quality analysis."""

    score: float = 0.0
    findings: list[QualityFinding] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    @property
    def strength_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "strength")


# ── Quality signal patterns ──────────────────────────────────────────────────

DECISION_TREE_PATTERNS = [
    r"if\s+.*(?:then|→|->|:)",
    r"(?:when|use)\s+.*(?:if|when|for)",
    r"├──|└──|│",  # ASCII tree characters
    r"decision\s+tree",
    r"flowchart|graph\s+(?:TD|LR|TB)",  # Mermaid diagrams
]

GUARDRAIL_PATTERNS = [
    r"(?:REFUSE|REJECT|STOP|HALT|ABORT|BLOCK|PROHIBIT)",
    r"(?:do\s+not|never|must\s+not|shall\s+not|MUST\s+NOT)",
    r"(?:WARN|WARNING|CAUTION|⚠️|🚫|❌)",
    r"(?:mandatory|required|enforced|non-negotiable)",
    r"power\s*<\s*\d+%",  # Specific statistical guardrails
]

EDGE_CASE_PATTERNS = [
    r"(?:edge\s+case|corner\s+case|special\s+case|exception)",
    r"(?:what\s+if|watch\s+out|pitfall|gotcha|caveat)",
    r"(?:limitation|known\s+issue|does\s+not\s+(?:handle|support))",
    r"(?:do\s+not\s+use\s+(?:for|when|if))",
    r"(?:anti-pattern|common\s+mistake|frequent\s+error)",
]

OUTPUT_FORMAT_PATTERNS = [
    r"(?:output\s+format|report\s+(?:format|template|structure))",
    r"(?:must\s+include|always\s+report|required\s+fields)",
    r"(?:\|\s*[\w\s]+\s*\|){2,}",  # Table structures
    r"```(?:json|yaml|python|r|markdown)",  # Typed code blocks
]

ESCAPE_HATCH_PATTERNS = [
    r"(?:override|escape\s+hatch|opt[- ]?out|skip\s+(?:this|check))",
    r"(?:experienced\s+users?|expert\s+mode|advanced)",
    r"(?:acknowledge|confirm|explicitly\s+(?:state|confirm))",
]


class QualityAnalyzer:
    """Assesses the depth and rigor of skill instructions."""

    def analyze(self, skill_path: Path) -> QualityResult:
        """Analyze a skill for quality signals."""
        result = QualityResult()

        # Read the main skill file
        skill_file = self._resolve_skill_file(skill_path)
        if skill_file is None:
            result.findings.append(
                QualityFinding(
                    severity="warning",
                    code="Q001",
                    message="No SKILL.md file found to analyze.",
                )
            )
            result.score = 0.0
            return result

        content = skill_file.read_text(encoding="utf-8")

        # Run all quality checks
        self._check_decision_trees(content, result)
        self._check_guardrails(content, result)
        self._check_edge_cases(content, result)
        self._check_output_format(content, result)
        self._check_escape_hatches(content, result)
        self._check_code_templates(content, result)
        self._check_references(skill_file.parent, result)
        self._check_specificity(content, result)

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

    def _check_decision_trees(self, content: str, result: QualityResult) -> None:
        """Check for structured decision logic."""
        total_matches = 0
        for pattern in DECISION_TREE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_matches += len(matches)

        result.metrics["decision_tree_signals"] = total_matches

        if total_matches >= 5:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q010",
                    message=f"Strong decision tree structure detected ({total_matches} routing signals).",
                )
            )
        elif total_matches >= 2:
            result.findings.append(
                QualityFinding(
                    severity="suggestion",
                    code="Q011",
                    message="Some decision logic found but could be more structured. Consider adding explicit if/then routing.",
                )
            )
        else:
            result.findings.append(
                QualityFinding(
                    severity="warning",
                    code="Q012",
                    message="No decision tree or routing logic detected. Skills without structured routing rely on agent judgment.",
                )
            )

    def _check_guardrails(self, content: str, result: QualityResult) -> None:
        """Check for guardrail / enforcement language."""
        total_matches = 0
        for pattern in GUARDRAIL_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_matches += len(matches)

        result.metrics["guardrail_signals"] = total_matches

        if total_matches >= 5:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q020",
                    message=f"Strong guardrail language ({total_matches} enforcement signals). This skill actively prevents misuse.",
                )
            )
        elif total_matches >= 1:
            result.findings.append(
                QualityFinding(
                    severity="suggestion",
                    code="Q021",
                    message="Some guardrail language found. Consider adding explicit REFUSE conditions for critical violations.",
                )
            )
        else:
            result.findings.append(
                QualityFinding(
                    severity="warning",
                    code="Q022",
                    message="No guardrail or enforcement language detected. The skill never refuses or warns — this may lead to silent misuse.",
                )
            )

    def _check_edge_cases(self, content: str, result: QualityResult) -> None:
        """Check for edge case documentation."""
        total_matches = 0
        for pattern in EDGE_CASE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_matches += len(matches)

        result.metrics["edge_case_signals"] = total_matches

        if total_matches >= 3:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q030",
                    message=f"Good edge case coverage ({total_matches} signals). Documents limitations and anti-patterns.",
                )
            )
        elif total_matches == 0:
            result.findings.append(
                QualityFinding(
                    severity="warning",
                    code="Q031",
                    message="No edge case documentation found. Consider adding 'When NOT to use' and 'Common mistakes' sections.",
                )
            )

    def _check_output_format(self, content: str, result: QualityResult) -> None:
        """Check for output format specification."""
        total_matches = 0
        for pattern in OUTPUT_FORMAT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_matches += len(matches)

        result.metrics["output_format_signals"] = total_matches

        if total_matches >= 3:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q040",
                    message="Well-specified output format with templates and structured fields.",
                )
            )
        elif total_matches == 0:
            result.findings.append(
                QualityFinding(
                    severity="suggestion",
                    code="Q041",
                    message="No explicit output format specified. Skills with structured output templates produce more consistent results.",
                )
            )

    def _check_escape_hatches(self, content: str, result: QualityResult) -> None:
        """Check for expert override mechanisms."""
        total_matches = 0
        for pattern in ESCAPE_HATCH_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_matches += len(matches)

        result.metrics["escape_hatch_signals"] = total_matches

        if total_matches >= 1:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q050",
                    message="Escape hatch mechanism found. Experienced users can override guardrails when justified.",
                )
            )

    def _check_code_templates(self, content: str, result: QualityResult) -> None:
        """Check for code templates and examples."""
        code_blocks = re.findall(r"```(\w*)\n(.*?)```", content, re.DOTALL)
        result.metrics["code_block_count"] = len(code_blocks)

        # Check for language-specific blocks
        languages = {lang for lang, _ in code_blocks if lang}
        result.metrics["code_languages"] = len(languages)

        if len(code_blocks) >= 3:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q060",
                    message=f"Rich code templates ({len(code_blocks)} blocks across {len(languages)} language(s)).",
                )
            )
        elif len(code_blocks) == 0:
            result.findings.append(
                QualityFinding(
                    severity="suggestion",
                    code="Q061",
                    message="No code templates found. Actionable skills benefit from copy-paste code examples.",
                )
            )

    def _check_references(self, skill_dir: Path, result: QualityResult) -> None:
        """Check for reference material depth."""
        refs_dir = skill_dir / "references"
        if not refs_dir.exists():
            result.metrics["reference_file_count"] = 0
            return

        ref_files = list(refs_dir.glob("*.md"))
        result.metrics["reference_file_count"] = len(ref_files)

        total_ref_words = 0
        for rf in ref_files:
            try:
                total_ref_words += len(rf.read_text(encoding="utf-8").split())
            except (OSError, UnicodeDecodeError):
                continue

        result.metrics["reference_total_words"] = total_ref_words

        if len(ref_files) >= 3 and total_ref_words >= 2000:
            result.findings.append(
                QualityFinding(
                    severity="strength",
                    code="Q070",
                    message=f"Deep reference library ({len(ref_files)} files, ~{total_ref_words} words). Supports progressive disclosure.",
                )
            )
        elif len(ref_files) >= 1:
            result.findings.append(
                QualityFinding(
                    severity="suggestion",
                    code="Q071",
                    message=f"Some references found ({len(ref_files)} files). Consider expanding for complex domains.",
                )
            )

    def _check_specificity(self, content: str, result: QualityResult) -> None:
        """Check if the skill is specific or dangerously generic."""
        # Generic filler phrases that indicate low-value content
        generic_patterns = [
            r"consider\s+(?:the|your)\s+(?:options|needs|requirements)",
            r"it\s+depends\s+on\s+(?:the|your)\s+(?:context|situation|use\s+case)",
            r"there\s+are\s+many\s+(?:ways|approaches|methods)\s+to",
            r"you\s+(?:may|might|could)\s+want\s+to\s+consider",
        ]
        generic_count = 0
        for pattern in generic_patterns:
            generic_count += len(re.findall(pattern, content, re.IGNORECASE))

        result.metrics["generic_filler_count"] = generic_count

        if generic_count >= 5:
            result.findings.append(
                QualityFinding(
                    severity="warning",
                    code="Q080",
                    message=f"High generic filler language ({generic_count} instances). Opinionated skills outperform generic advice.",
                    detail="SkillsBench (Feb 2026) found curated, opinionated skills outperform generic ones by +16.2pp.",
                )
            )

    def _compute_score(self, result: QualityResult) -> float:
        """Compute a 0-100 quality score.

        Normalized by number of applicable checks rather than raw pattern
        counts. Each check that produced a finding is one applicable item.
        Strengths count as a full pass, suggestions as partial (0.4), and
        warnings as a fail (0).
        """
        if not result.findings:
            return 50.0  # No checks fired — neutral

        applicable = len(result.findings)
        passes = sum(
            1.0 for f in result.findings if f.severity == "strength"
        )
        partial = sum(
            0.4 for f in result.findings if f.severity == "suggestion"
        )
        # warnings contribute 0

        score = ((passes + partial) / applicable) * 100
        return max(0.0, min(100.0, score))
