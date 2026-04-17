"""
Composite Scorer — computes a weighted overall skill quality score.

Combines scores from all analyzers into a single 0-100 composite score
with a letter grade and actionable recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DimensionScore:
    """Score for a single evaluation dimension."""

    name: str
    score: float  # 0-100
    weight: float  # 0-1
    weighted_score: float = 0.0
    grade: str = ""


@dataclass
class CompositeResult:
    """Final composite evaluation result."""

    overall_score: float = 0.0
    overall_grade: str = ""
    recommendation: str = ""
    dimensions: list[DimensionScore] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)


# ── Default weights ──────────────────────────────────────────────────────────

DEFAULT_WEIGHTS = {
    "structure": 0.15,
    "security": 0.20,
    "quality": 0.15,
    "domain_correctness": 0.25,
    "maintenance": 0.15,
    "completeness": 0.10,
}

# ── Grading scale ────────────────────────────────────────────────────────────

GRADE_THRESHOLDS = [
    (95, "A+", "Exceptional — install with confidence"),
    (90, "A", "Excellent — high quality, well-maintained"),
    (85, "A-", "Very good — minor improvements possible"),
    (80, "B+", "Good — solid skill with some gaps"),
    (75, "B", "Above average — usable but review findings"),
    (70, "B-", "Decent — has notable weaknesses"),
    (65, "C+", "Fair — significant gaps, use with caution"),
    (60, "C", "Below average — consider alternatives"),
    (50, "C-", "Poor — major issues present"),
    (40, "D", "Very poor — not recommended for use"),
    (0, "F", "Failing — critical issues, do not install"),
]


class CompositeScorer:
    """Computes a weighted composite quality score from all analyzers."""

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or DEFAULT_WEIGHTS

    def compute(
        self,
        structure_score: float = 50.0,
        security_score: float = 50.0,
        quality_score: float = 50.0,
        domain_score: float = 50.0,
        maintenance_score: float = 50.0,
    ) -> CompositeResult:
        """Compute the composite score from individual dimension scores."""
        result = CompositeResult()

        # Build dimension scores
        dimensions_input = {
            "structure": structure_score,
            "security": security_score,
            "quality": quality_score,
            "domain_correctness": domain_score,
            "maintenance": maintenance_score,
        }

        total_weight = 0.0
        weighted_sum = 0.0

        for dim_name, raw_score in dimensions_input.items():
            weight = self.weights.get(dim_name, 0.1)
            w_score = raw_score * weight

            dim = DimensionScore(
                name=dim_name,
                score=raw_score,
                weight=weight,
                weighted_score=w_score,
                grade=self._score_to_grade(raw_score),
            )
            result.dimensions.append(dim)

            weighted_sum += w_score
            total_weight += weight

        # Normalize to account for potentially missing dimensions
        if total_weight > 0:
            result.overall_score = weighted_sum / total_weight
        else:
            result.overall_score = 0.0

        result.overall_grade = self._score_to_grade(result.overall_score)
        result.recommendation = self._generate_recommendation(result)

        return result

    def _score_to_grade(self, score: float) -> str:
        """Convert a numeric score to a letter grade."""
        for threshold, grade, _ in GRADE_THRESHOLDS:
            if score >= threshold:
                return grade
        return "F"

    def _generate_recommendation(self, result: CompositeResult) -> str:
        """Generate an actionable recommendation based on the composite result."""
        score = result.overall_score

        # Find the weakest dimension
        weakest = min(result.dimensions, key=lambda d: d.score)

        for threshold, grade, desc in GRADE_THRESHOLDS:
            if score >= threshold:
                base = desc
                break
        else:
            base = "Critical issues detected"

        if weakest.score < 40:
            return f"{base}. ⚠️ Critical weakness in '{weakest.name}' ({weakest.score:.0f}/100) — address before installing."
        elif weakest.score < 60:
            return f"{base}. Note: '{weakest.name}' is below average ({weakest.score:.0f}/100)."
        else:
            return base + "."
