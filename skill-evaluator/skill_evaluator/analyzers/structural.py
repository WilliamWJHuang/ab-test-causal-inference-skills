"""
Structural Analyzer — validates SKILL.md schema and metadata completeness.

Checks:
- Valid YAML frontmatter with required fields (name, description, version)
- Proper Markdown structure (headings, sections)
- Recommended fields presence (triggers, domain, compatibility)
- Progressive disclosure structure (L1/L2/L3 tiers)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ── Required and recommended frontmatter fields ──────────────────────────────

REQUIRED_FIELDS = {"name", "description"}
RECOMMENDED_FIELDS = {
    "version",
    "domain",
    "triggers",
    "compatibility",
    "author",
}
OPTIONAL_FIELDS = {
    "tags",
    "license",
    "dependencies",
    "references",
    "do_not_use_for",
    "use_for",
}

# ── Expected Markdown sections ───────────────────────────────────────────────

RECOMMENDED_SECTIONS = [
    "overview",
    "when to use",
    "workflow",
    "decision tree",
    "output format",
    "guardrails",
    "references",
]


@dataclass
class StructuralFinding:
    """A single finding from the structural analysis."""

    severity: str  # "error", "warning", "info"
    code: str  # machine-readable code like "S001"
    message: str
    line: int | None = None


@dataclass
class StructuralResult:
    """Result of a structural analysis."""

    score: float = 0.0  # 0-100
    findings: list[StructuralFinding] = field(default_factory=list)
    frontmatter: dict[str, Any] = field(default_factory=dict)
    sections_found: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warning")


class StructuralAnalyzer:
    """Validates the structural integrity of a SKILL.md file."""

    # ── Regex patterns ────────────────────────────────────────────────────

    FRONTMATTER_PATTERN = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
    )
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def analyze(self, skill_path: Path) -> StructuralResult:
        """Analyze a SKILL.md file or a directory containing one."""
        result = StructuralResult()

        # Resolve path to the actual SKILL.md file
        skill_file = self._resolve_skill_file(skill_path)
        if skill_file is None:
            result.findings.append(
                StructuralFinding(
                    severity="error",
                    code="S001",
                    message=f"No SKILL.md file found at '{skill_path}'",
                )
            )
            result.score = 0.0
            return result

        content = skill_file.read_text(encoding="utf-8")

        # Run all checks
        self._check_frontmatter(content, result)
        self._check_sections(content, result)
        self._check_content_quality(content, result)
        self._check_progressive_disclosure(skill_file.parent, result)

        # Compute score
        result.score = self._compute_score(result)
        return result

    def _resolve_skill_file(self, path: Path) -> Path | None:
        """Find the SKILL.md file from a path (file or directory)."""
        if path.is_file():
            return path if path.name.upper() == "SKILL.MD" else path
        if path.is_dir():
            # Look for SKILL.md (case-insensitive)
            for candidate in path.iterdir():
                if candidate.name.upper() == "SKILL.MD":
                    return candidate
        return None

    def _check_frontmatter(self, content: str, result: StructuralResult) -> None:
        """Validate YAML frontmatter presence and required fields."""
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            result.findings.append(
                StructuralFinding(
                    severity="error",
                    code="S010",
                    message="Missing YAML frontmatter (expected '---' delimited block at file start)",
                    line=1,
                )
            )
            return

        raw_yaml = match.group(1)
        try:
            frontmatter = yaml.safe_load(raw_yaml) or {}
        except yaml.YAMLError as exc:
            result.findings.append(
                StructuralFinding(
                    severity="error",
                    code="S011",
                    message=f"Invalid YAML in frontmatter: {exc}",
                    line=1,
                )
            )
            return

        if not isinstance(frontmatter, dict):
            result.findings.append(
                StructuralFinding(
                    severity="error",
                    code="S012",
                    message="Frontmatter must be a YAML mapping (key: value pairs)",
                    line=1,
                )
            )
            return

        result.frontmatter = frontmatter

        # Check required fields
        for req_field in REQUIRED_FIELDS:
            if req_field not in frontmatter:
                result.findings.append(
                    StructuralFinding(
                        severity="error",
                        code="S020",
                        message=f"Missing required frontmatter field: '{req_field}'",
                    )
                )
            elif not frontmatter[req_field]:
                result.findings.append(
                    StructuralFinding(
                        severity="error",
                        code="S021",
                        message=f"Required field '{req_field}' is empty",
                    )
                )

        # Check recommended fields
        for rec_field in RECOMMENDED_FIELDS:
            if rec_field not in frontmatter:
                result.findings.append(
                    StructuralFinding(
                        severity="warning",
                        code="S030",
                        message=f"Missing recommended field: '{rec_field}'",
                    )
                )

        # Check description length (should be meaningful)
        desc = frontmatter.get("description", "")
        if isinstance(desc, str) and 0 < len(desc) < 20:
            result.findings.append(
                StructuralFinding(
                    severity="warning",
                    code="S031",
                    message=f"Description is very short ({len(desc)} chars). Aim for ≥50 chars for discoverability.",
                )
            )

        # Check for 'use_for' / 'do_not_use_for' triggers
        has_triggers = (
            "triggers" in frontmatter
            or "use_for" in frontmatter
            or "do_not_use_for" in frontmatter
        )
        if not has_triggers:
            result.findings.append(
                StructuralFinding(
                    severity="warning",
                    code="S032",
                    message="No activation triggers defined. Add 'triggers', 'use_for', or 'do_not_use_for' for better agent routing.",
                )
            )

    def _check_sections(self, content: str, result: StructuralResult) -> None:
        """Check for recommended Markdown sections."""
        headings = self.HEADING_PATTERN.findall(content)
        section_names = [h[1].strip().lower() for h in headings]
        result.sections_found = section_names

        for rec_section in RECOMMENDED_SECTIONS:
            # Fuzzy match: check if any heading contains the recommended section name
            found = any(rec_section in s for s in section_names)
            if not found:
                result.findings.append(
                    StructuralFinding(
                        severity="info",
                        code="S040",
                        message=f"Missing recommended section: '{rec_section.title()}'",
                    )
                )

        # Check for at least some structure
        if len(headings) < 2:
            result.findings.append(
                StructuralFinding(
                    severity="warning",
                    code="S041",
                    message=f"Very few headings found ({len(headings)}). Well-structured skills typically have 5+ sections.",
                )
            )

    def _check_content_quality(self, content: str, result: StructuralResult) -> None:
        """Check basic content quality signals."""
        # Strip frontmatter for body analysis
        body = self.FRONTMATTER_PATTERN.sub("", content).strip()
        word_count = len(body.split())

        if word_count < 100:
            result.findings.append(
                StructuralFinding(
                    severity="warning",
                    code="S050",
                    message=f"Skill body is very short ({word_count} words). Effective skills typically have 300+ words.",
                )
            )
        elif word_count < 300:
            result.findings.append(
                StructuralFinding(
                    severity="info",
                    code="S051",
                    message=f"Skill body is somewhat short ({word_count} words). Consider adding more detail.",
                )
            )

        # Check for code blocks (good signal for actionable skills)
        code_blocks = re.findall(r"```[\s\S]*?```", content)
        if not code_blocks:
            result.findings.append(
                StructuralFinding(
                    severity="info",
                    code="S052",
                    message="No code blocks found. Actionable skills benefit from code templates or examples.",
                )
            )

    def _check_progressive_disclosure(
        self, skill_dir: Path, result: StructuralResult
    ) -> None:
        """Check for progressive disclosure structure (references/ directory)."""
        refs_dir = skill_dir / "references"
        if not refs_dir.exists():
            result.findings.append(
                StructuralFinding(
                    severity="info",
                    code="S060",
                    message="No 'references/' directory found. Progressive disclosure (L3 docs) helps manage context window budget.",
                )
            )
        elif refs_dir.is_dir():
            ref_files = list(refs_dir.glob("*.md"))
            if not ref_files:
                result.findings.append(
                    StructuralFinding(
                        severity="info",
                        code="S061",
                        message="'references/' directory exists but contains no .md files.",
                    )
                )

    def _compute_score(self, result: StructuralResult) -> float:
        """Compute a 0-100 structural score."""
        score = 100.0

        for finding in result.findings:
            if finding.severity == "error":
                score -= 20.0
            elif finding.severity == "warning":
                score -= 5.0
            elif finding.severity == "info":
                score -= 1.0

        return max(0.0, min(100.0, score))
