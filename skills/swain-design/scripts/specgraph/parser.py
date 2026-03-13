"""Frontmatter extraction from artifact markdown files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ArtifactFrontmatter:
    """Parsed frontmatter from an artifact markdown file."""

    artifact: str
    title: str
    status: str
    type: str  # derived from artifact ID prefix
    file: str  # relative path from repo root
    description: str  # first ~120 chars of description/question/body
    raw_fields: dict = field(default_factory=dict)  # all parsed fields


# Regex to match the YAML frontmatter block (between --- delimiters)
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Regex to extract a scalar field: "key: value"
_SCALAR_RE = re.compile(r"^([a-z][a-z0-9-]*):\s*(.*)$", re.MULTILINE)

# Regex to extract list items under a field: "  - value"
_LIST_ITEM_RE = re.compile(r"^\s+-\s+(.+)$", re.MULTILINE)

# Regex for artifact IDs
_ARTIFACT_ID_RE = re.compile(r"[A-Z]+-\d+")


def _extract_type(artifact_id: str) -> str:
    """Derive artifact type from ID prefix (e.g., 'EPIC-005' -> 'EPIC')."""
    return re.sub(r"-\d+$", "", artifact_id)


def _extract_description(
    raw_fields: dict, body: str, max_len: int = 120
) -> str:
    """Extract a one-line description for an artifact.

    Priority: question (spikes) > description (frontmatter) > first body paragraph.
    """
    # Try question field first (SPIKEs use this)
    question = raw_fields.get("question", "")
    if question:
        return question[:max_len]

    # Try description field
    desc = raw_fields.get("description", "")
    if desc:
        return desc[:max_len]

    # Fall back to first non-heading, non-empty body line
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "[", "|", ">", "!", "-", "```")):
            return line[:max_len]

    return ""


def parse_frontmatter(content: str) -> Optional[dict]:
    """Parse YAML frontmatter from markdown content into a dict.

    Returns None if no frontmatter block is found.
    Handles scalar fields, list fields, and quoted values.
    """
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return None

    fm_text = match.group(1)
    fields: dict = {}
    current_list_key: Optional[str] = None

    for line in fm_text.splitlines():
        # Check for list item continuation
        list_match = re.match(r"^\s+-\s+(.+)$", line)
        if list_match and current_list_key is not None:
            val = list_match.group(1).strip()
            # Strip quotes
            val = re.sub(r'^["\']|["\']$', "", val)
            fields[current_list_key].append(val)
            continue

        # Check for scalar field
        scalar_match = re.match(r"^([a-z][a-z0-9-]*):\s*(.*)$", line)
        if scalar_match:
            key = scalar_match.group(1)
            val = scalar_match.group(2).strip()
            # Strip quotes
            val = re.sub(r'^["\']|["\']$', "", val)

            if not val or val in ("[]", "~", "null"):
                # Empty value or explicit empty list — start as list
                fields[key] = [] if not val or val == "[]" else val
                current_list_key = key if not val or val == "[]" else None
            else:
                fields[key] = val
                current_list_key = None
        else:
            # Not a recognized line, stop list accumulation
            current_list_key = None

    return fields


def get_body(content: str) -> str:
    """Extract the body text (everything after the closing --- of frontmatter)."""
    match = _FRONTMATTER_RE.match(content)
    if not match:
        return content
    return content[match.end() :]


def parse_artifact(filepath: Path, repo_root: Path) -> Optional[ArtifactFrontmatter]:
    """Parse an artifact markdown file and return structured frontmatter.

    Returns None if the file has no artifact: field in frontmatter.
    """
    content = filepath.read_text(encoding="utf-8")
    fields = parse_frontmatter(content)

    if fields is None or "artifact" not in fields:
        return None

    artifact_id = fields["artifact"]
    title = fields.get("title", "")
    # Strip leading "TYPE-NNN: " prefix from title if present
    prefix = f"{artifact_id}: "
    if title.startswith(prefix):
        title = title[len(prefix) :]

    status = fields.get("status", "")
    atype = _extract_type(artifact_id)
    file_rel = str(filepath.relative_to(repo_root))

    body = get_body(content)
    description = _extract_description(fields, body)

    return ArtifactFrontmatter(
        artifact=artifact_id,
        title=title,
        status=status,
        type=atype,
        file=file_rel,
        description=description,
        raw_fields=fields,
    )


def extract_list_ids(fields: dict, key: str) -> list[str]:
    """Extract artifact IDs (TYPE-NNN) from a frontmatter list field."""
    val = fields.get(key, [])
    if isinstance(val, str):
        return _ARTIFACT_ID_RE.findall(val)
    if isinstance(val, list):
        ids = []
        for item in val:
            ids.extend(_ARTIFACT_ID_RE.findall(str(item)))
        return ids
    return []


def extract_scalar_id(fields: dict, key: str) -> Optional[str]:
    """Extract a single artifact ID from a scalar frontmatter field."""
    val = fields.get(key, "")
    if isinstance(val, str):
        match = _ARTIFACT_ID_RE.search(val)
        return match.group(0) if match else None
    return None
