"""
skill-eval CLI — Evaluate agent skills before you install them.

Usage:
    skill-eval <path>                 Evaluate a local skill
    skill-eval <path> --format md     Output as Markdown
    skill-eval <path> --domain stats  Force a specific domain
    skill-eval <path> --json          Output raw JSON scores
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from skill_evaluator.analyzers import (
    DomainCorrectnessAnalyzer,
    MaintenanceAnalyzer,
    QualityAnalyzer,
    SecurityAnalyzer,
    StructuralAnalyzer,
)
from skill_evaluator.scorers import CompositeScorer, ReportGenerator


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--format", "-f",
    "output_format",
    type=click.Choice(["terminal", "md", "json"]),
    default="terminal",
    help="Output format.",
)
@click.option(
    "--domain", "-d",
    "forced_domain",
    type=str,
    default=None,
    help="Force a specific domain for correctness checking (e.g., 'statistics', 'causal-inference', 'digital-marketing').",
)
@click.option(
    "--weights",
    type=str,
    default=None,
    help="Custom weights as JSON string, e.g., '{\"security\": 0.3, \"quality\": 0.2}'",
)
@click.option(
    "--fail-below",
    type=float,
    default=None,
    help="Exit with code 1 if overall score is below this threshold (for CI).",
)
def main(
    path: str,
    output_format: str,
    forced_domain: str | None,
    weights: str | None,
    fail_below: float | None,
) -> None:
    """Evaluate an agent skill before installing it.

    PATH can be a directory containing a SKILL.md file or the SKILL.md file itself.
    """
    skill_path = Path(path).resolve()

    # Parse custom weights if provided
    custom_weights = None
    if weights:
        try:
            custom_weights = json.loads(weights)
        except json.JSONDecodeError:
            click.echo("Error: --weights must be valid JSON.", err=True)
            sys.exit(2)

    # Determine skill name
    skill_name = _detect_skill_name(skill_path)

    # ── Run all analyzers ─────────────────────────────────────────────────
    click.echo(f"Evaluating skill: {skill_name}...", err=True) if output_format != "terminal" else None

    structural_analyzer = StructuralAnalyzer()
    security_analyzer = SecurityAnalyzer()
    quality_analyzer = QualityAnalyzer()
    domain_analyzer = DomainCorrectnessAnalyzer()
    maintenance_analyzer = MaintenanceAnalyzer()

    structural_result = structural_analyzer.analyze(skill_path)
    security_result = security_analyzer.analyze(skill_path)
    quality_result = quality_analyzer.analyze(skill_path)
    domain_result = domain_analyzer.analyze(skill_path, domain=forced_domain)
    maintenance_result = maintenance_analyzer.analyze(skill_path)

    # ── Compute composite ─────────────────────────────────────────────────
    scorer = CompositeScorer(weights=custom_weights)
    composite = scorer.compute(
        structure_score=structural_result.score,
        security_score=security_result.score,
        quality_score=quality_result.score,
        domain_score=domain_result.score,
        maintenance_score=maintenance_result.score,
        security_gate=security_result.risk_level,
    )

    # ── Output ────────────────────────────────────────────────────────────
    reporter = ReportGenerator()

    if output_format == "terminal":
        reporter.generate_terminal(
            skill_name=skill_name,
            composite=composite,
            structural=structural_result,
            security=security_result,
            quality=quality_result,
            domain=domain_result,
            maintenance=maintenance_result,
        )
    elif output_format == "md":
        md_report = reporter.generate_markdown(
            skill_name=skill_name,
            composite=composite,
            structural=structural_result,
            security=security_result,
            quality=quality_result,
            domain=domain_result,
            maintenance=maintenance_result,
        )
        click.echo(md_report)
    elif output_format == "json":
        json_output = {
            "skill_name": skill_name,
            "overall_score": round(composite.overall_score, 1),
            "overall_grade": composite.overall_grade,
            "recommendation": composite.recommendation,
            "dimensions": {
                dim.name: {
                    "score": round(dim.score, 1),
                    "grade": dim.grade,
                    "weight": dim.weight,
                }
                for dim in composite.dimensions
            },
            "security_risk_level": security_result.risk_level,
            "domain_detected": domain_result.domain,
            "domain_rules_passed": domain_result.rules_passed,
            "domain_rules_checked": domain_result.rules_checked,
        }
        click.echo(json.dumps(json_output, indent=2))

    # ── CI gate ───────────────────────────────────────────────────────────
    if fail_below is not None and composite.overall_score < fail_below:
        click.echo(
            f"\n❌ Score {composite.overall_score:.0f} is below threshold {fail_below}.",
            err=True,
        )
        sys.exit(1)


def _detect_skill_name(path: Path) -> str:
    """Detect a human-readable skill name from the path or frontmatter."""
    # Try to read from frontmatter
    import yaml

    skill_file = path if path.is_file() else None
    if path.is_dir():
        for candidate in path.iterdir():
            if candidate.name.upper() == "SKILL.MD":
                skill_file = candidate
                break

    if skill_file:
        try:
            content = skill_file.read_text(encoding="utf-8")
            import re
            match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if match:
                fm = yaml.safe_load(match.group(1))
                if isinstance(fm, dict) and "name" in fm:
                    return fm["name"]
        except Exception:
            pass

    # Fall back to directory name
    if path.is_dir():
        return path.name
    return path.stem


if __name__ == "__main__":
    main()
