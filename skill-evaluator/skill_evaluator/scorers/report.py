"""
Report Generator — produces human-readable evaluation reports.

Supports two output formats:
- Terminal (rich-formatted with colors and tables)
- Markdown (for CI pipelines, GitHub comments, READMEs)
"""

from __future__ import annotations

import os
import sys
from io import StringIO
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from skill_evaluator.analyzers.domain import DomainResult
    from skill_evaluator.analyzers.maintenance import MaintenanceResult
    from skill_evaluator.analyzers.quality import QualityResult
    from skill_evaluator.analyzers.security import SecurityResult
    from skill_evaluator.analyzers.structural import StructuralResult
    from skill_evaluator.scorers.composite import CompositeResult


def _safe_str(text: str) -> str:
    """Replace emoji with ASCII fallbacks if the console can't handle UTF-8."""
    try:
        text.encode(sys.stdout.encoding or "utf-8")
        return text
    except (UnicodeEncodeError, LookupError):
        replacements = {
            "📋": "[Report]",
            "❌": "[X]",
            "⚠️": "[!]",
            "ℹ️": "[i]",
            "🔴": "[!!]",
            "🟠": "[!]",
            "🟡": "[~]",
            "🟢": "[ok]",
            "✅": "[ok]",
            "💡": "[tip]",
            "❓": "[?]",
        }
        for emoji, ascii_alt in replacements.items():
            text = text.replace(emoji, ascii_alt)
        return text


# ── Grade colors ─────────────────────────────────────────────────────────────

GRADE_COLORS = {
    "A+": "bold green",
    "A": "bold green",
    "A-": "green",
    "B+": "green",
    "B": "yellow",
    "B-": "yellow",
    "C+": "dark_orange",
    "C": "dark_orange",
    "C-": "red",
    "D": "bold red",
    "F": "bold red",
}

SEVERITY_ICONS = {
    # Structural
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    # Security
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
    # Quality
    "strength": "✅",
    "suggestion": "💡",
    # Domain
    "correct": "✅",
    "suspicious": "⚠️",
    "incorrect": "❌",
    "missing": "❓",
}


class ReportGenerator:
    """Generates human-readable evaluation reports."""

    def generate_terminal(
        self,
        skill_name: str,
        composite: CompositeResult,
        structural: StructuralResult,
        security: SecurityResult,
        quality: QualityResult,
        domain: DomainResult,
        maintenance: MaintenanceResult,
    ) -> None:
        """Print a rich-formatted report to the terminal."""
        console = Console(force_terminal=True)

        # ── Header ────────────────────────────────────────────────────────
        grade_color = GRADE_COLORS.get(composite.overall_grade, "white")
        grade_text = Text(composite.overall_grade, style=grade_color)

        header = Text.assemble(
            ("Skill Evaluation Report: ", "bold"),
            (skill_name, "bold cyan"),
            (" — ", ""),
            grade_text,
            (f" ({composite.overall_score:.0f}/100)", "dim"),
        )
        console.print()
        console.print(Panel(header, expand=False, border_style="cyan"))
        console.print()

        # ── Recommendation ────────────────────────────────────────────────
        console.print(_safe_str(f"  [Report] {composite.recommendation}"))
        console.print()

        # ── Dimension scores table ────────────────────────────────────────
        table = Table(title="Dimension Scores", border_style="dim")
        table.add_column("Dimension", style="bold", min_width=20)
        table.add_column("Score", justify="center", min_width=8)
        table.add_column("Grade", justify="center", min_width=6)
        table.add_column("Weight", justify="center", min_width=8)

        for dim in composite.dimensions:
            dim_color = GRADE_COLORS.get(dim.grade, "white")
            table.add_row(
                dim.name.replace("_", " ").title(),
                f"{dim.score:.0f}/100",
                Text(dim.grade, style=dim_color),
                f"{dim.weight:.0%}",
            )

        console.print(table)
        console.print()

        # ── Detailed findings ─────────────────────────────────────────────
        self._print_section(console, "Structure", structural.findings)
        self._print_section(console, "Security", security.findings,
                           extra=f"Risk Level: {security.risk_level.upper()}")
        self._print_section(console, "Quality", quality.findings)
        self._print_section(console, "Domain Correctness", domain.findings,
                           extra=f"Domain: {domain.domain} | Rules: {domain.rules_passed}/{domain.rules_checked} passed")
        self._print_section(console, "Maintenance", maintenance.findings)

    def _print_section(
        self,
        console: Console,
        title: str,
        findings: list,
        extra: str = "",
    ) -> None:
        """Print a findings section."""
        console.print(f"  [bold]{'─' * 50}[/bold]")
        header = f"  [bold]{title}[/bold]"
        if extra:
            header += f"  [dim]({extra})[/dim]"
        console.print(header)

        if not findings:
            console.print("  [dim]  No findings.[/dim]")
            console.print()
            return

        for finding in findings:
            severity = getattr(finding, "severity", "info")
            icon = SEVERITY_ICONS.get(severity, "*")
            message = getattr(finding, "message", str(finding))
            code = getattr(finding, "code", "")
            code_str = f"[dim]\[{code}][/dim] " if code else ""

            console.print(_safe_str(f"    {icon} {code_str}{message}"))

            # Print detail if available
            detail = getattr(finding, "detail", "")
            if detail:
                console.print(f"       [dim]{detail}[/dim]")

        console.print()

    def generate_markdown(
        self,
        skill_name: str,
        composite: CompositeResult,
        structural: StructuralResult,
        security: SecurityResult,
        quality: QualityResult,
        domain: DomainResult,
        maintenance: MaintenanceResult,
    ) -> str:
        """Generate a Markdown-formatted report string."""
        lines: list[str] = []

        # Header
        lines.append(f"# Skill Evaluation: {skill_name}")
        lines.append("")
        lines.append(f"**Overall Score:** {composite.overall_score:.0f}/100 ({composite.overall_grade})")
        lines.append(f"**Recommendation:** {composite.recommendation}")
        lines.append("")

        # Dimension table
        lines.append("## Dimension Scores")
        lines.append("")
        lines.append("| Dimension | Score | Grade | Weight |")
        lines.append("|:---|:---:|:---:|:---:|")

        for dim in composite.dimensions:
            name = dim.name.replace("_", " ").title()
            lines.append(f"| {name} | {dim.score:.0f}/100 | {dim.grade} | {dim.weight:.0%} |")

        lines.append("")

        # Findings sections
        sections = [
            ("Structure", structural.findings),
            ("Security", security.findings),
            ("Quality", quality.findings),
            ("Domain Correctness", domain.findings),
            ("Maintenance", maintenance.findings),
        ]

        for title, findings in sections:
            lines.append(f"## {title}")
            lines.append("")
            if not findings:
                lines.append("_No findings._")
            else:
                for f in findings:
                    severity = getattr(f, "severity", "info")
                    icon = SEVERITY_ICONS.get(severity, "•")
                    message = getattr(f, "message", str(f))
                    code = getattr(f, "code", "")
                    code_str = f"[{code}] " if code else ""
                    lines.append(f"- {icon} {code_str}{message}")

                    detail = getattr(f, "detail", "")
                    if detail:
                        lines.append(f"  - _{detail}_")
            lines.append("")

        return "\n".join(lines)
