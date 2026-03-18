"""Pre-claim security briefing generator (SPEC-063).

Generates markdown-formatted security guidance based on threat surface
detection categories. When a task is security-sensitive, the agent receives
relevant OWASP and swain-specific guidance before writing code.

Uses detect_threat_surface() from SPEC-062 for classification.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure sibling modules are importable
_SCRIPT_DIR = str(Path(__file__).parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from threat_surface import detect_threat_surface

# ---------------------------------------------------------------------------
# OWASP category-to-guidance mapping
# ---------------------------------------------------------------------------
# Each entry maps a threat_surface category to a dict with:
#   - owasp_id: OWASP Top 10 2021 identifier
#   - owasp_name: Full OWASP category name
#   - guidance: List of actionable guidance bullet points

CATEGORY_GUIDANCE: dict[str, dict] = {
    "auth": {
        "owasp_id": "A07:2021",
        "owasp_name": "Identification and Authentication Failures",
        "guidance": [
            "Never store passwords in plaintext; use bcrypt, scrypt, or argon2 with appropriate work factors",
            "Session tokens must be regenerated on privilege change (login, role elevation)",
            "Implement account lockout or rate limiting after repeated failed authentication attempts",
            "Use constant-time comparison for token and credential validation to prevent timing attacks",
            "Ensure multi-factor authentication is supported where applicable",
        ],
    },
    "input-validation": {
        "owasp_id": "A03:2021",
        "owasp_name": "Injection",
        "guidance": [
            "Validate and sanitize all user input at system boundaries",
            "Use parameterized queries for database access; never use string concatenation for SQL",
            "Apply output encoding appropriate to the context (HTML, URL, JavaScript, CSS)",
            "Implement allowlist validation where possible rather than blocklist filtering",
            "Treat all data from external sources as untrusted until validated",
        ],
    },
    "crypto": {
        "owasp_id": "A02:2021",
        "owasp_name": "Cryptographic Failures",
        "guidance": [
            "Use standard, well-vetted cryptographic algorithms (AES-256, RSA-2048+, SHA-256+)",
            "Never implement custom cryptographic algorithms or protocols",
            "Ensure deprecated or weak algorithms (MD5, SHA-1, DES, RC4) are not used",
            "Manage cryptographic keys securely; never hardcode keys in source code",
            "Use TLS 1.2+ for all data in transit; disable older protocol versions",
        ],
    },
    "external-data": {
        "owasp_id": "A08:2021",
        "owasp_name": "Software and Data Integrity Failures",
        "guidance": [
            "Verify the integrity of all external data using signatures or checksums",
            "Do not deserialize untrusted data without validation; use safe deserialization methods",
            "Validate that CI/CD pipelines have proper access controls and integrity checks",
            "Ensure software updates and patches come from verified, trusted sources",
            "Review and validate all data from third-party APIs before processing",
        ],
    },
    "agent-context": {
        "owasp_id": None,  # swain-specific, no OWASP mapping
        "owasp_name": None,
        "guidance": [
            "Agent context files (AGENTS.md, CLAUDE.md) are trust boundaries — do not write user-controlled data into them",
            "Never embed secrets, credentials, or API keys in context files",
            "Validate any data that flows from task descriptions into agent instructions",
            "Treat context file modifications as privileged operations requiring review",
            "Ensure agent context does not leak sensitive information across task boundaries",
        ],
    },
    "dependency-change": {
        "owasp_id": "A06:2021",
        "owasp_name": "Vulnerable and Outdated Components",
        "guidance": [
            "Audit new dependencies for known vulnerabilities before adding them (npm audit, pip-audit, etc.)",
            "Pin dependency versions and review lockfile changes carefully",
            "Remove unused dependencies to reduce attack surface",
            "Prefer well-maintained packages with active security response teams",
            "Check that transitive dependencies are not introducing known vulnerabilities",
        ],
    },
    "secrets": {
        "owasp_id": "A07:2021",
        "owasp_name": "Identification and Authentication Failures",
        "guidance": [
            "Never commit secrets, credentials, or API keys to version control",
            "Use environment variables or a dedicated secrets manager for sensitive values",
            "Ensure .env files and credential stores are listed in .gitignore",
            "Rotate secrets immediately if they are suspected of being exposed",
            "Use short-lived tokens and credentials where possible to limit blast radius",
        ],
    },
}


def _format_category_section(category: str) -> str:
    """Format a single category's guidance as a markdown section."""
    info = CATEGORY_GUIDANCE.get(category)
    if info is None:
        return ""

    lines: list[str] = []

    if info["owasp_id"] is not None:
        lines.append(f"### OWASP {info['owasp_id']} — {info['owasp_name']}")
    else:
        # swain-specific category (e.g., agent-context)
        lines.append(f"### swain guidance — {category}")

    lines.append("")
    for point in info["guidance"]:
        lines.append(f"- {point}")

    return "\n".join(lines)


def generate_security_briefing(
    title: str = "",
    description: str = "",
    tags: list[str] | None = None,
    spec_criteria: str = "",
    file_paths: list[str] | None = None,
) -> str:
    """Generate a markdown-formatted security briefing for a task.

    Delegates to detect_threat_surface() for classification, then maps
    detected categories to OWASP and swain-specific guidance.

    Args:
        title: Task title text.
        description: Task description text.
        tags: List of task tags.
        spec_criteria: SPEC acceptance criteria text.
        file_paths: List of file paths touched by the task.

    Returns:
        Markdown-formatted security briefing string, or empty string
        if the task is not security-sensitive.
    """
    result = detect_threat_surface(
        title=title,
        description=description,
        tags=tags,
        spec_criteria=spec_criteria,
        file_paths=file_paths,
    )

    if not result.is_security_sensitive:
        return ""

    sections: list[str] = []

    # Header with detected categories
    if result.categories:
        cat_list = ", ".join(result.categories)
        sections.append(f"## Security Briefing (categories: {cat_list})")
    else:
        # Triggered by generic 'security' tag with no specific category
        sections.append("## Security Briefing")

    sections.append("")

    if result.categories:
        # Emit guidance for each detected category
        for category in result.categories:
            section = _format_category_section(category)
            if section:
                sections.append(section)
                sections.append("")
    else:
        # Generic security tag with no specific category — emit general guidance
        sections.append("### General Security Guidance")
        sections.append("")
        sections.append("- Review code changes for common security anti-patterns")
        sections.append("- Validate all inputs and sanitize all outputs")
        sections.append("- Ensure no secrets or credentials are exposed")
        sections.append("- Check for proper error handling that does not leak sensitive information")
        sections.append("")

    return "\n".join(sections).rstrip("\n") + "\n"
