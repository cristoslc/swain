"""Architecture overview diagram validation."""

from __future__ import annotations

import re
from pathlib import Path


# Patterns that indicate a diagram is present
_MERMAID_RE = re.compile(r"```\s*mermaid", re.IGNORECASE)
_IMAGE_MD_RE = re.compile(r"!\[.*?\]\(.*?\)")
_IMAGE_HTML_RE = re.compile(r"<img\s+", re.IGNORECASE)
_DIAGRAM_HEADING_RE = re.compile(
    r"^#{1,3}\s+.*\b(diagram|c4)\b", re.IGNORECASE | re.MULTILINE
)

# Pattern to extract artifact ID from directory name like (EPIC-001)-Foo
_ARTIFACT_DIR_RE = re.compile(r"\(([A-Z]+-\d+)\)")


def has_diagram(content: str) -> bool:
    """Check if an architecture overview contains at least one diagram.

    Accepts: mermaid code blocks, markdown image refs, HTML img tags,
    or section headings containing 'diagram' or 'C4'.
    """
    if not content:
        return False
    if _MERMAID_RE.search(content):
        return True
    if _IMAGE_MD_RE.search(content):
        return True
    if _IMAGE_HTML_RE.search(content):
        return True
    if _DIAGRAM_HEADING_RE.search(content):
        return True
    return False


def find_architecture_overviews(repo_root: Path) -> list[dict]:
    """Find all architecture-overview.md files and check for diagrams.

    Searches both Vision and Epic directories.
    Returns a list of dicts with path, parent_artifact, and has_diagram.
    """
    results = []
    docs = repo_root / "docs"

    for search_dir in ("vision", "epic"):
        parent_dir = docs / search_dir
        if not parent_dir.exists():
            continue

        for arch_file in sorted(parent_dir.rglob("architecture-overview.md")):
            # Determine parent artifact from directory name
            parent_artifact = "unknown"
            for part in arch_file.parts:
                match = _ARTIFACT_DIR_RE.search(part)
                if match:
                    parent_artifact = match.group(1)

            content = arch_file.read_text(encoding="utf-8")
            rel_path = str(arch_file.relative_to(repo_root))

            results.append(
                {
                    "path": rel_path,
                    "parent_artifact": parent_artifact,
                    "has_diagram": has_diagram(content),
                }
            )

    return results
