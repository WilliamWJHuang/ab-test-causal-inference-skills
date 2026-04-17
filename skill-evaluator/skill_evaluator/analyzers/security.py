"""
Security Analyzer — scans skills for dangerous patterns and security risks.

Checks for:
- Shell command injection patterns
- Credential/API key exfiltration
- Unsafe file system access instructions
- Network exfiltration patterns
- Prompt injection / jailbreak patterns
- Excessive permission requests
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SecurityFinding:
    """A single security finding."""

    severity: str  # "critical", "high", "medium", "low"
    code: str
    message: str
    matched_text: str = ""
    line: int | None = None


@dataclass
class SecurityResult:
    """Result of a security analysis."""

    score: float = 0.0
    findings: list[SecurityFinding] = field(default_factory=list)
    risk_level: str = "unknown"  # "safe", "low", "medium", "high", "critical"

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "critical")

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "high")


# ── Dangerous pattern definitions ────────────────────────────────────────────

DANGEROUS_PATTERNS: list[dict] = [
    # -- Shell injection --
    {
        "name": "Shell command execution",
        "pattern": r"(?:subprocess|os\.system|os\.popen|exec\(|eval\(|shell=True)",
        "severity": "high",
        "code": "SEC001",
        "message": "Contains shell execution patterns. Verify these are sandboxed and intentional.",
    },
    {
        "name": "Dangerous shell commands",
        "pattern": r"(?:rm\s+-rf|chmod\s+777|curl\s+.*\|\s*(?:sh|bash)|wget\s+.*\|\s*(?:sh|bash))",
        "severity": "critical",
        "code": "SEC002",
        "message": "Contains potentially destructive shell commands (rm -rf, piped curl/wget).",
    },
    # -- Credential exfiltration --
    {
        "name": "API key patterns",
        "pattern": r"(?:api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]",
        "severity": "high",
        "code": "SEC010",
        "message": "Contains hardcoded credential patterns. Skills should never include secrets.",
    },
    {
        "name": "Environment variable harvesting",
        "pattern": r"os\.environ\[|os\.getenv\(|process\.env\.",
        "severity": "medium",
        "code": "SEC011",
        "message": "Accesses environment variables. Verify only expected variables are read.",
    },
    # -- Network exfiltration --
    {
        "name": "Outbound HTTP requests",
        "pattern": r"(?:requests\.(?:get|post|put)|urllib\.request|fetch\(|http\.client|aiohttp)",
        "severity": "medium",
        "code": "SEC020",
        "message": "Contains outbound HTTP request patterns. Verify destinations are trusted.",
    },
    {
        "name": "Data exfiltration patterns",
        "pattern": r"(?:base64\.b64encode|zlib\.compress).*(?:requests\.|urllib|fetch)",
        "severity": "high",
        "code": "SEC021",
        "message": "Contains encoding + network patterns that could indicate data exfiltration.",
    },
    {
        "name": "Webhook/external endpoint",
        "pattern": r"(?:webhook|ngrok|requestbin|pipedream|burpcollaborator)",
        "severity": "high",
        "code": "SEC022",
        "message": "References external data collection endpoints.",
    },
    # -- File system abuse --
    {
        "name": "Broad filesystem access",
        "pattern": r"(?:glob\.glob\(['\"]\/|os\.walk\(['\"]\/|Path\(['\"]\/(?:etc|home|Users))",
        "severity": "medium",
        "code": "SEC030",
        "message": "Accesses broad filesystem paths outside project scope.",
    },
    {
        "name": "SSH/config file access",
        "pattern": r"(?:\.ssh|\.aws|\.env|\.gitconfig|\.netrc|id_rsa)",
        "severity": "high",
        "code": "SEC031",
        "message": "References sensitive configuration files (.ssh, .aws, .env).",
    },
    # -- Prompt injection / jailbreak --
    {
        "name": "Prompt injection patterns",
        "pattern": r"(?:ignore\s+(?:all\s+)?(?:previous|above)\s+instructions|you\s+are\s+now|forget\s+(?:all|your)\s+(?:previous|prior))",
        "severity": "critical",
        "code": "SEC040",
        "message": "Contains prompt injection / jailbreak patterns.",
    },
    {
        "name": "System prompt override",
        "pattern": r"(?:system\s*:\s*you\s+are|<\|system\|>|<<SYS>>)",
        "severity": "high",
        "code": "SEC041",
        "message": "Attempts to override system prompt boundaries.",
    },
    # -- Obfuscation --
    {
        "name": "Base64 encoded content",
        "pattern": r"(?:atob\(|btoa\(|base64\.b64decode|base64\.b64encode)",
        "severity": "medium",
        "code": "SEC050",
        "message": "Contains base64 encoding/decoding. Check for obfuscated malicious content.",
    },
    {
        "name": "Unicode/hex obfuscation",
        "pattern": r"(?:\\x[0-9a-f]{2}){4,}|(?:\\u[0-9a-f]{4}){3,}",
        "severity": "medium",
        "code": "SEC051",
        "message": "Contains sequences of escaped unicode/hex characters that may obfuscate intent.",
    },
]


class SecurityAnalyzer:
    """Scans skill files for security risks and dangerous patterns."""

    def analyze(self, skill_path: Path) -> SecurityResult:
        """Analyze a skill directory or file for security risks."""
        result = SecurityResult()

        # Collect all files to scan
        files_to_scan = self._collect_files(skill_path)

        for file_path in files_to_scan:
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except (OSError, PermissionError):
                continue

            self._scan_content(content, file_path, result)

        # Compute score and risk level
        result.score = self._compute_score(result)
        result.risk_level = self._compute_risk_level(result)
        return result

    def _collect_files(self, path: Path) -> list[Path]:
        """Collect all text files from a path."""
        if path.is_file():
            return [path]

        scannable_extensions = {
            ".md", ".yaml", ".yml", ".json", ".py", ".js", ".ts",
            ".sh", ".bash", ".txt", ".toml", ".cfg", ".ini",
        }
        files = []
        for f in path.rglob("*"):
            if f.is_file() and f.suffix.lower() in scannable_extensions:
                files.append(f)
        return files

    def _scan_content(
        self, content: str, file_path: Path, result: SecurityResult
    ) -> None:
        """Scan content against all dangerous patterns."""
        content_lower = content.lower()

        for pattern_def in DANGEROUS_PATTERNS:
            matches = re.finditer(
                pattern_def["pattern"], content_lower, re.IGNORECASE
            )
            for match in matches:
                # Find the line number
                line_num = content[:match.start()].count("\n") + 1
                # Extract a snippet of the matched text (truncated)
                matched = match.group(0)[:80]

                result.findings.append(
                    SecurityFinding(
                        severity=pattern_def["severity"],
                        code=pattern_def["code"],
                        message=f"[{file_path.name}] {pattern_def['message']}",
                        matched_text=matched,
                        line=line_num,
                    )
                )

    def _compute_score(self, result: SecurityResult) -> float:
        """Compute a 0-100 security score."""
        score = 100.0
        for finding in result.findings:
            if finding.severity == "critical":
                score -= 30.0
            elif finding.severity == "high":
                score -= 15.0
            elif finding.severity == "medium":
                score -= 5.0
            elif finding.severity == "low":
                score -= 2.0
        return max(0.0, min(100.0, score))

    def _compute_risk_level(self, result: SecurityResult) -> str:
        """Determine overall risk level."""
        if result.critical_count > 0:
            return "critical"
        if result.high_count > 0:
            return "high"
        if result.score >= 90:
            return "safe"
        if result.score >= 70:
            return "low"
        return "medium"
