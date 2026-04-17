"""
Maintenance Analyzer — assesses repository health and maintenance signals.

Checks:
- File recency (last modified dates)
- Presence of tests, CI configuration, changelogs
- Documentation completeness (README, LICENSE, CONTRIBUTING)
- Directory structure hygiene
- Git metadata (if available)
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MaintenanceFinding:
    """A single maintenance finding."""

    severity: str  # "strength", "warning", "info"
    code: str
    message: str


@dataclass
class MaintenanceResult:
    """Result of a maintenance analysis."""

    score: float = 0.0
    findings: list[MaintenanceFinding] = field(default_factory=list)
    metrics: dict[str, object] = field(default_factory=dict)


# Days thresholds for freshness assessment
FRESH_DAYS = 90
STALE_DAYS = 365
ABANDONED_DAYS = 730


class MaintenanceAnalyzer:
    """Assesses repository health and maintenance signals."""

    def analyze(self, skill_path: Path) -> MaintenanceResult:
        """Analyze maintenance signals for a skill."""
        result = MaintenanceResult()

        # Determine the root directory to analyze
        root = skill_path if skill_path.is_dir() else skill_path.parent

        self._check_file_freshness(root, result)
        self._check_documentation(root, result)
        self._check_testing(root, result)
        self._check_ci(root, result)
        self._check_structure(root, result)
        self._check_git(root, result)

        result.score = self._compute_score(result)
        return result

    def _check_file_freshness(self, root: Path, result: MaintenanceResult) -> None:
        """Check how recently files were modified."""
        now = time.time()
        most_recent = 0.0
        file_count = 0

        for f in root.rglob("*"):
            if f.is_file() and not any(
                part.startswith(".") for part in f.parts
            ):
                try:
                    mtime = f.stat().st_mtime
                    most_recent = max(most_recent, mtime)
                    file_count += 1
                except OSError:
                    continue

        result.metrics["file_count"] = file_count

        if most_recent == 0:
            result.findings.append(
                MaintenanceFinding(
                    severity="warning",
                    code="M010",
                    message="Could not determine file modification dates.",
                )
            )
            return

        days_since_update = (now - most_recent) / 86400
        result.metrics["days_since_last_update"] = round(days_since_update, 1)

        if days_since_update <= FRESH_DAYS:
            result.findings.append(
                MaintenanceFinding(
                    severity="strength",
                    code="M011",
                    message=f"Recently updated ({int(days_since_update)} days ago). Actively maintained.",
                )
            )
        elif days_since_update <= STALE_DAYS:
            result.findings.append(
                MaintenanceFinding(
                    severity="info",
                    code="M012",
                    message=f"Last updated {int(days_since_update)} days ago. May be stable or becoming stale.",
                )
            )
        elif days_since_update <= ABANDONED_DAYS:
            result.findings.append(
                MaintenanceFinding(
                    severity="warning",
                    code="M013",
                    message=f"Last updated {int(days_since_update)} days ago. Appears stale.",
                )
            )
        else:
            result.findings.append(
                MaintenanceFinding(
                    severity="warning",
                    code="M014",
                    message=f"Last updated {int(days_since_update)} days ago. Appears abandoned.",
                )
            )

    def _check_documentation(self, root: Path, result: MaintenanceResult) -> None:
        """Check for documentation files."""
        # Check in root and parent (in case skill is a subdirectory)
        search_dirs = [root]
        if root.parent != root:
            search_dirs.append(root.parent)

        doc_files = {
            "README": False,
            "LICENSE": False,
            "CONTRIBUTING": False,
            "CHANGELOG": False,
        }

        for search_dir in search_dirs:
            for f in search_dir.iterdir():
                name_upper = f.stem.upper()
                for doc_name in doc_files:
                    if name_upper == doc_name or name_upper.startswith(doc_name):
                        doc_files[doc_name] = True

        found_count = sum(1 for v in doc_files.values() if v)
        result.metrics["documentation_files"] = found_count

        if doc_files["README"]:
            result.findings.append(
                MaintenanceFinding(
                    severity="strength",
                    code="M020",
                    message="README found. Basic documentation present.",
                )
            )
        else:
            result.findings.append(
                MaintenanceFinding(
                    severity="warning",
                    code="M021",
                    message="No README found. Essential documentation is missing.",
                )
            )

        if doc_files["LICENSE"]:
            result.findings.append(
                MaintenanceFinding(
                    severity="strength",
                    code="M022",
                    message="LICENSE found. Usage terms are clear.",
                )
            )
        else:
            result.findings.append(
                MaintenanceFinding(
                    severity="info",
                    code="M023",
                    message="No LICENSE file found. Usage terms may be unclear.",
                )
            )

    def _check_testing(self, root: Path, result: MaintenanceResult) -> None:
        """Check for test files or evaluation harnesses."""
        test_patterns = ["test_*", "*_test.*", "tests/", "evals/", "eval_*"]
        has_tests = False

        for pattern in ["test_*", "*_test.py", "*_test.md"]:
            if list(root.rglob(pattern)):
                has_tests = True
                break

        for dirname in ["tests", "test", "evals", "eval"]:
            if (root / dirname).is_dir():
                has_tests = True
                break

        result.metrics["has_tests"] = has_tests

        if has_tests:
            result.findings.append(
                MaintenanceFinding(
                    severity="strength",
                    code="M030",
                    message="Test or evaluation files found. Skill has been verified.",
                )
            )
        else:
            result.findings.append(
                MaintenanceFinding(
                    severity="warning",
                    code="M031",
                    message="No tests or evaluation harness found. Skill has not been systematically verified.",
                )
            )

    def _check_ci(self, root: Path, result: MaintenanceResult) -> None:
        """Check for CI/CD configuration."""
        ci_dirs = [".github/workflows", ".gitlab-ci.yml", ".circleci"]
        has_ci = False

        for ci_path in ci_dirs:
            full_path = root / ci_path
            if full_path.exists():
                has_ci = True
                break
            # Also check parent
            parent_path = root.parent / ci_path
            if parent_path.exists():
                has_ci = True
                break

        result.metrics["has_ci"] = has_ci

        if has_ci:
            result.findings.append(
                MaintenanceFinding(
                    severity="strength",
                    code="M040",
                    message="CI/CD configuration found. Automated quality checks are in place.",
                )
            )

    def _check_structure(self, root: Path, result: MaintenanceResult) -> None:
        """Check for well-organized directory structure."""
        # Look for references/ directory (progressive disclosure)
        has_refs = (root / "references").is_dir()
        # Look for scripts/ directory
        has_scripts = (root / "scripts").is_dir()
        # Look for examples/ directory
        has_examples = (root / "examples").is_dir()

        well_structured = sum([has_refs, has_scripts, has_examples])
        result.metrics["auxiliary_directories"] = well_structured

        if well_structured >= 2:
            result.findings.append(
                MaintenanceFinding(
                    severity="strength",
                    code="M050",
                    message="Well-organized directory structure with auxiliary content (references, scripts, examples).",
                )
            )

    def _check_git(self, root: Path, result: MaintenanceResult) -> None:
        """Check for git repository signals."""
        # Walk up to find .git
        current = root
        has_git = False
        for _ in range(5):
            if (current / ".git").is_dir():
                has_git = True
                break
            parent = current.parent
            if parent == current:
                break
            current = parent

        result.metrics["has_git"] = has_git

        if has_git:
            result.findings.append(
                MaintenanceFinding(
                    severity="info",
                    code="M060",
                    message="Git repository detected. Version history is available.",
                )
            )

    def _compute_score(self, result: MaintenanceResult) -> float:
        """Compute a 0-100 maintenance score.

        Normalized by number of applicable checks. Strengths count as a full
        pass, info as partial (0.4), and warnings as a fail (0).
        """
        if not result.findings:
            return 50.0  # No checks fired — neutral

        applicable = len(result.findings)
        passes = sum(
            1.0 for f in result.findings if f.severity == "strength"
        )
        partial = sum(
            0.4 for f in result.findings if f.severity == "info"
        )
        # warnings contribute 0

        score = ((passes + partial) / applicable) * 100
        return max(0.0, min(100.0, score))
