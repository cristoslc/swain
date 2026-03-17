"""Threat surface detection heuristic for tk tasks.

Determines if a task touches a security-sensitive surface based on
task metadata: title, description, tags, SPEC acceptance criteria text,
and file paths touched.

Part of SPEC-062: Threat Surface Detection Heuristic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Category constants
# ---------------------------------------------------------------------------
CAT_AUTH = "auth"
CAT_INPUT_VALIDATION = "input-validation"
CAT_CRYPTO = "crypto"
CAT_EXTERNAL_DATA = "external-data"
CAT_AGENT_CONTEXT = "agent-context"
CAT_DEPENDENCY_CHANGE = "dependency-change"
CAT_SECRETS = "secrets"

VALID_CATEGORIES = frozenset({
    CAT_AUTH, CAT_INPUT_VALIDATION, CAT_CRYPTO, CAT_EXTERNAL_DATA,
    CAT_AGENT_CONTEXT, CAT_DEPENDENCY_CHANGE, CAT_SECRETS,
})

# ---------------------------------------------------------------------------
# Keyword -> category mapping
# ---------------------------------------------------------------------------
# Keywords are split into two groups:
#   - STEM keywords: longer, specific terms where suffix variants are valid
#     (e.g., "encrypt" matches "encrypted", "encryption")
#   - EXACT keywords: shorter or ambiguous terms that require word-boundary
#     matching to avoid false positives (e.g., "key" must not match "keyboard")
_STEM_KEYWORDS: dict[str, str] = {
    "auth": CAT_AUTH,
    "login": CAT_AUTH,
    "password": CAT_AUTH,
    "token": CAT_AUTH,
    "permission": CAT_AUTH,
    "encrypt": CAT_CRYPTO,
    "certificate": CAT_CRYPTO,
    "sanitize": CAT_INPUT_VALIDATION,
    "validat": CAT_INPUT_VALIDATION,     # matches validate, validation, validating
    "secret": CAT_SECRETS,
}

_EXACT_KEYWORDS: dict[str, str] = {
    "role": CAT_AUTH,
    "escape": CAT_INPUT_VALIDATION,
    "key": CAT_AUTH,
}

# Combined lookup for category resolution
KEYWORD_CATEGORIES: dict[str, str] = {**_STEM_KEYWORDS, **_EXACT_KEYWORDS}

# Two compiled patterns: stem-matching (no trailing \b) and exact (with trailing \b)
_STEM_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in _STEM_KEYWORDS) + r")",
    re.IGNORECASE,
)
_EXACT_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(kw) for kw in _EXACT_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Tag -> category mapping
# ---------------------------------------------------------------------------
SECURITY_TAGS: dict[str, str | None] = {
    "security": None,       # triggers is_security_sensitive but no specific category
    "auth": CAT_AUTH,
    "crypto": CAT_CRYPTO,
    "input-validation": CAT_INPUT_VALIDATION,
}

# ---------------------------------------------------------------------------
# File path patterns -> category
# ---------------------------------------------------------------------------
FILE_PATH_RULES: list[tuple[re.Pattern[str], str]] = [
    # Directory-based patterns
    (re.compile(r"(^|/)auth/"), CAT_AUTH),
    (re.compile(r"(^|/)crypto/"), CAT_CRYPTO),
    (re.compile(r"(^|/)middleware/auth"), CAT_AUTH),

    # Secret / env files
    (re.compile(r"(^|/)\.env(\b|$)"), CAT_SECRETS),
    (re.compile(r"credential", re.IGNORECASE), CAT_SECRETS),
    (re.compile(r"secret", re.IGNORECASE), CAT_SECRETS),

    # Dependency manifest files
    (re.compile(r"(^|/)package\.json$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)package-lock\.json$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)requirements\.txt$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)pyproject\.toml$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)go\.mod$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)go\.sum$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)Gemfile(\.lock)?$"), CAT_DEPENDENCY_CHANGE),
    (re.compile(r"(^|/)Cargo\.(toml|lock)$"), CAT_DEPENDENCY_CHANGE),
]


@dataclass
class ThreatSurfaceResult:
    """Result of threat surface detection."""
    is_security_sensitive: bool = False
    categories: list[str] = field(default_factory=list)


def _add_category(categories: set[str], category: str | None) -> None:
    """Add a category to the set if it is not None."""
    if category is not None:
        categories.add(category)


def _scan_text_for_keywords(text: str, categories: set[str]) -> bool:
    """Scan text for security keywords, adding matched categories.

    Uses stem matching for longer keywords and exact matching for short
    or ambiguous keywords to minimize false positives.

    Returns True if any keyword was found.
    """
    found = False
    for pattern in (_STEM_PATTERN, _EXACT_PATTERN):
        for match in pattern.finditer(text):
            keyword = match.group(1).lower()
            _add_category(categories, KEYWORD_CATEGORIES.get(keyword))
            found = True
    return found


def detect_threat_surface(
    title: str = "",
    description: str = "",
    tags: list[str] | None = None,
    spec_criteria: str = "",
    file_paths: list[str] | None = None,
) -> ThreatSurfaceResult:
    """Detect if a task touches a security-sensitive surface.

    Checks signals in this order:
      1. Task tags (security, auth, crypto, input-validation)
      2. Title keywords
      3. Description keywords
      4. SPEC acceptance criteria keywords
      5. File paths

    Args:
        title: Task title text.
        description: Task description text.
        tags: List of task tags.
        spec_criteria: SPEC acceptance criteria text.
        file_paths: List of file paths touched by the task.

    Returns:
        ThreatSurfaceResult with is_security_sensitive flag and matched categories.
    """
    categories: set[str] = set()
    is_sensitive = False

    # 1. Tag-based detection
    if tags:
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in SECURITY_TAGS:
                is_sensitive = True
                _add_category(categories, SECURITY_TAGS[tag_lower])

    # 2. Title keyword detection
    if _scan_text_for_keywords(title, categories):
        is_sensitive = True

    # 3. Description keyword detection
    if _scan_text_for_keywords(description, categories):
        is_sensitive = True

    # 4. SPEC acceptance criteria keyword detection
    if _scan_text_for_keywords(spec_criteria, categories):
        is_sensitive = True

    # 5. File path detection
    if file_paths:
        for fpath in file_paths:
            for pattern, category in FILE_PATH_RULES:
                if pattern.search(fpath):
                    is_sensitive = True
                    _add_category(categories, category)
                    break  # one match per file is enough

    return ThreatSurfaceResult(
        is_security_sensitive=is_sensitive,
        categories=sorted(categories),
    )
