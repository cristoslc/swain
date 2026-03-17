"""External security skill hook interface (SPEC-065).

Provides three hook points for external security skills to plug into
swain-do's security gates:

1. **Pre-claim** — external skills contribute additional security guidance
2. **During-implementation** — security co-pilot context for file paths
3. **Completion** — differential review of git diffs

Skills are discovered by checking for known SKILL.md paths in
.claude/skills/ and .agents/skills/. All hooks are no-ops when no
external skills are installed — built-in guidance (SPEC-063) always runs.

Adding a new external skill requires only a call to register_skill()
with the detection pattern and hook capabilities — no core code changes.
"""

from __future__ import annotations

import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Skill registry
# ---------------------------------------------------------------------------
# Each entry maps a detection pattern to the hook capabilities it supports.
# Capabilities: "security-briefing" (pre-claim), "security-context" (impl),
#               "security-review" (completion)

_SKILL_REGISTRY: list[dict[str, Any]] = [
    {
        "name": "trailofbits-sharp-edges",
        "detection_pattern": "trailofbits-sharp-edges",
        "hook_capabilities": ["security-briefing"],
    },
    {
        "name": "trailofbits-insecure-defaults",
        "detection_pattern": "trailofbits-insecure-defaults",
        "hook_capabilities": ["security-briefing"],
    },
    {
        "name": "trailofbits-differential-review",
        "detection_pattern": "trailofbits-differential-review",
        "hook_capabilities": ["security-review"],
    },
    {
        "name": "owasp-security",
        "detection_pattern": "owasp-security",
        "hook_capabilities": ["security-briefing", "security-context"],
    },
]

# Glob-style patterns registered via register_skill()
_GLOB_REGISTRY: list[dict[str, Any]] = []

# Standard skill directory prefixes (relative to a search dir)
_SKILL_PREFIXES = [
    os.path.join(".claude", "skills"),
    os.path.join(".agents", "skills"),
]


def register_skill(
    name: str,
    detection_pattern: str,
    hook_capabilities: list[str],
) -> None:
    """Register a new external skill detection pattern.

    After registration, detect_installed_skills() will discover skills
    matching the given detection_pattern in the standard skill directories.

    Args:
        name: Human-readable skill name (used as registry key).
        detection_pattern: Directory name or glob pattern to match
            (e.g., "snyk-security" or "snyk-*").
        hook_capabilities: List of supported hook types:
            "security-briefing", "security-context", "security-review".
    """
    entry = {
        "name": name,
        "detection_pattern": detection_pattern,
        "hook_capabilities": hook_capabilities,
    }
    # If the pattern contains glob characters, add to glob registry
    if "*" in detection_pattern or "?" in detection_pattern:
        _GLOB_REGISTRY.append(entry)
    else:
        _SKILL_REGISTRY.append(entry)


def _get_capabilities_for_skill(skill_name: str) -> list[str]:
    """Look up the hook capabilities for a detected skill name.

    Checks the static registry first, then glob registry entries.
    Returns a default set of all capabilities if the skill isn't
    in any registry (shouldn't normally happen).
    """
    for entry in _SKILL_REGISTRY:
        if entry["detection_pattern"] == skill_name or entry["name"] == skill_name:
            return entry["hook_capabilities"]
    for entry in _GLOB_REGISTRY:
        if fnmatch(skill_name, entry["detection_pattern"]):
            return entry["hook_capabilities"]
    # Default: all capabilities (permissive fallback)
    return ["security-briefing", "security-context", "security-review"]


# ---------------------------------------------------------------------------
# Skill detection
# ---------------------------------------------------------------------------


def detect_installed_skills(
    search_dirs: list[str] | None = None,
) -> dict[str, str]:
    """Detect installed external security skills.

    Scans known skill directory locations for SKILL.md files matching
    registered detection patterns.

    Args:
        search_dirs: List of root directories to search. Defaults to [cwd].

    Returns:
        Dict mapping skill_name -> skill_directory_path for all detected skills.
    """
    if search_dirs is None:
        search_dirs = [os.getcwd()]

    detected: dict[str, str] = {}

    for search_dir in search_dirs:
        for prefix in _SKILL_PREFIXES:
            skills_root = Path(search_dir) / prefix
            if not skills_root.is_dir():
                continue

            # Check each subdirectory against known patterns
            for child in skills_root.iterdir():
                if not child.is_dir():
                    continue

                skill_md = child / "SKILL.md"
                if not skill_md.is_file():
                    continue

                dir_name = child.name

                # Check static registry (exact match)
                for entry in _SKILL_REGISTRY:
                    pattern = entry["detection_pattern"]
                    if "*" not in pattern and "?" not in pattern:
                        if dir_name == pattern:
                            detected[dir_name] = str(child)
                            break
                    elif fnmatch(dir_name, pattern):
                        detected[dir_name] = str(child)
                        break
                else:
                    # Check glob registry
                    for entry in _GLOB_REGISTRY:
                        if fnmatch(dir_name, entry["detection_pattern"]):
                            detected[dir_name] = str(child)
                            break

    return detected


# ---------------------------------------------------------------------------
# Hook dispatch
# ---------------------------------------------------------------------------


def _dispatch_hook(
    hook_type: str,
    installed_skills: dict[str, str],
    context_label: str,
    context_data: str,
) -> list[str]:
    """Internal dispatcher for all hook types.

    Filters installed skills by capability, then generates a markdown
    guidance block for each matching skill. The actual guidance content
    comes from the skill's SKILL.md metadata — this interface provides
    the structured invocation surface.

    Args:
        hook_type: One of "security-briefing", "security-context", "security-review".
        installed_skills: Dict of skill_name -> skill_path.
        context_label: Label for the context data (e.g., "Task metadata", "File paths").
        context_data: The context data to pass to the skill.

    Returns:
        List of markdown-formatted guidance blocks, one per matching skill.
    """
    if not installed_skills:
        return []

    results: list[str] = []

    for skill_name, skill_path in installed_skills.items():
        capabilities = _get_capabilities_for_skill(skill_name)
        if hook_type not in capabilities:
            continue

        # Read the skill's SKILL.md for metadata
        skill_md_path = Path(skill_path) / "SKILL.md"
        skill_description = ""
        if skill_md_path.is_file():
            try:
                content = skill_md_path.read_text()
                # Extract the first heading as description
                for line in content.splitlines():
                    if line.startswith("# "):
                        skill_description = line[2:].strip()
                        break
            except OSError:
                pass

        # Build the guidance block
        block_lines = [
            f"### External: {skill_name}",
            "",
        ]
        if skill_description:
            block_lines.append(f"*{skill_description}*")
            block_lines.append("")

        block_lines.extend([
            f"- **Skill path**: `{skill_path}`",
            f"- **Hook**: `{hook_type}`",
            f"- **{context_label}**: {context_data}",
            "",
            f"Invoke `{skill_name}` for detailed {hook_type.replace('-', ' ')} analysis.",
        ])

        results.append("\n".join(block_lines))

    return results


def run_pre_claim_hooks(
    task_metadata: dict[str, Any],
    installed_skills: dict[str, str],
) -> list[str]:
    """Run pre-claim hooks on all installed skills that support it.

    Pre-claim hooks provide additional security guidance before a task
    is claimed. The guidance is additive — it never replaces built-in
    SPEC-063 guidance.

    Args:
        task_metadata: Dict with keys: title, tags, categories.
        installed_skills: Dict of skill_name -> skill_path from detect_installed_skills().

    Returns:
        List of markdown guidance blocks, one per matching skill.
        Empty list when no skills are installed or none support pre-claim.
    """
    context_parts = []
    if task_metadata.get("title"):
        context_parts.append(f"title='{task_metadata['title']}'")
    if task_metadata.get("tags"):
        context_parts.append(f"tags={task_metadata['tags']}")
    if task_metadata.get("categories"):
        context_parts.append(f"categories={task_metadata['categories']}")

    context_str = ", ".join(context_parts) if context_parts else "(empty)"

    return _dispatch_hook(
        hook_type="security-briefing",
        installed_skills=installed_skills,
        context_label="Task metadata",
        context_data=context_str,
    )


def run_implementation_hooks(
    file_paths: list[str],
    installed_skills: dict[str, str],
) -> list[str]:
    """Run during-implementation hooks on all installed skills that support it.

    Implementation hooks provide security co-pilot context for the files
    being edited. The notes are additive — they supplement, not replace,
    built-in guidance.

    Args:
        file_paths: List of file paths being edited.
        installed_skills: Dict of skill_name -> skill_path from detect_installed_skills().

    Returns:
        List of markdown security note blocks, one per matching skill.
        Empty list when no skills are installed or none support implementation hooks.
    """
    context_str = ", ".join(f"`{p}`" for p in file_paths) if file_paths else "(none)"

    return _dispatch_hook(
        hook_type="security-context",
        installed_skills=installed_skills,
        context_label="File paths",
        context_data=context_str,
    )


def run_completion_hooks(
    git_diff: str,
    installed_skills: dict[str, str],
) -> list[str]:
    """Run completion hooks on all installed skills that support it.

    Completion hooks provide differential review of the git diff after
    implementation. Findings are additive — they supplement, not replace,
    built-in security checks.

    Args:
        git_diff: Git diff string to review.
        installed_skills: Dict of skill_name -> skill_path from detect_installed_skills().

    Returns:
        List of markdown finding blocks, one per matching skill.
        Empty list when no skills are installed or none support completion hooks.
    """
    # Truncate long diffs for the context display
    diff_preview = git_diff[:200] + "..." if len(git_diff) > 200 else git_diff
    diff_display = diff_preview.replace("\n", " ")[:100]

    return _dispatch_hook(
        hook_type="security-review",
        installed_skills=installed_skills,
        context_label="Diff preview",
        context_data=diff_display if diff_display else "(empty)",
    )
