#!/usr/bin/env python3
"""Context-File Injection Heuristic Scanner.

Scans agentic coding context files (AGENTS.md, CLAUDE.md, .cursorrules,
skill SKILL.md files, etc.) for prompt injection patterns using regex
heuristics.

Categories A-J per SPIKE-020:
  A: Instruction override
  B: Role override / persona hijacking
  C: Privilege escalation / authority spoofing
  D: Data exfiltration (explicit)
  E: Persistence mechanisms
  F: Base64 / encoding obfuscation
  G: Hidden Unicode (byte-level)
  H: MCP / config file manipulation
  I: HTML comment injection
  J: External fetch + exec

Exit codes:
  0 = no findings
  1 = findings detected
  2 = error

Zero external deps beyond Python 3 stdlib (re + unicodedata).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from typing import Any


# ---------------------------------------------------------------------------
# Rule definitions: each rule is (compiled_regex, category, severity, description)
# ---------------------------------------------------------------------------

RuleType = tuple[re.Pattern[str], str, str, str]

_RULES: list[RuleType] = []


def _add_rule(pattern: str, category: str, severity: str, description: str, flags: int = re.IGNORECASE) -> None:
    """Register a detection rule."""
    _RULES.append((re.compile(pattern, flags), category, severity, description))


# ---------------------------------------------------------------------------
# Category A — Instruction Override
# ---------------------------------------------------------------------------

_add_rule(
    r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|rules|guidelines|prompts)",
    "A", "critical",
    "Instruction override: attempts to nullify prior instructions",
)
_add_rule(
    r"disregard\s+(?:all\s+)?(?:your|previous|prior|the)\s+(?:guidelines|instructions|rules|prompts)",
    "A", "critical",
    "Instruction override: disregard directives",
)
_add_rule(
    r"(?:new|override)\s+system\s+prompt",
    "A", "critical",
    "Instruction override: system prompt replacement",
)
_add_rule(
    r"\[END\s+OF\s+(?:CONTEXT|INSTRUCTIONS|SYSTEM|PROMPT)\]",
    "A", "high",
    "Instruction override: fake end-of-context marker",
)
_add_rule(
    r"forget\s+everything\s+(?:above|before|previous)",
    "A", "critical",
    "Instruction override: memory wipe directive",
)
_add_rule(
    r"do\s+not\s+follow\s+(?:the\s+)?previous\s+instructions",
    "A", "critical",
    "Instruction override: explicit instruction negation",
)

# ---------------------------------------------------------------------------
# Category B — Role Override / Persona Hijacking
# ---------------------------------------------------------------------------

_add_rule(
    r"you\s+are\s+now\s+(?!responsible|expected|required|going\s+to\s+be\s+(?:review|test|build))",
    "B", "critical",
    "Role override: persona reassignment",
)
_add_rule(
    r"act\s+as\s+(?:an?\s+)?(?:unrestricted|unfiltered|uncensored|evil|malicious|jailbroken)",
    "B", "critical",
    "Role override: unrestricted persona",
)
_add_rule(
    r"(?:enter|enable|activate)\s+(?:DAN|developer|god|sudo|jailbreak)\s+mode",
    "B", "critical",
    "Role override: jailbreak mode activation",
)
_add_rule(
    r"DAN\s+mode\s+(?:enabled|activated|on)",
    "B", "critical",
    "Role override: DAN mode declaration",
)
_add_rule(
    r"pretend\s+you\s+are\s+(?!working|a\s+code\s+reviewer|a\s+developer)",
    "B", "high",
    "Role override: pretend persona",
)
_add_rule(
    r"roleplay\s+as\s+",
    "B", "high",
    "Role override: roleplay directive",
)
_add_rule(
    r"jailbreak\s+(?:mode|enabled|activated|prompt)",
    "B", "critical",
    "Role override: jailbreak keyword",
)
_add_rule(
    r"developer\s+mode\s+(?:enabled|activated|on)",
    "B", "critical",
    "Role override: developer mode activation",
)

# ---------------------------------------------------------------------------
# Category C — Privilege Escalation / Authority Spoofing
# ---------------------------------------------------------------------------

_add_rule(
    r"you\s+have\s+full\s+access",
    "C", "critical",
    "Privilege escalation: full access claim",
)
_add_rule(
    r"(?:this\s+is\s+)?a?\s*message\s+from\s+(?:Anthropic|OpenAI|Google|Meta|the\s+developers?)\s*:",
    "C", "critical",
    "Privilege escalation: vendor impersonation",
)
_add_rule(
    r"(?:security|safety)\s+(?:restrictions?|filters?|guardrails?|limits?)\s+(?:are\s+)?(?:disabled|removed|lifted|off|turned\s+off)",
    "C", "critical",
    "Privilege escalation: safety bypass claim",
)
_add_rule(
    r"sudo\s+access\s+granted",
    "C", "critical",
    "Privilege escalation: sudo access claim",
)
_add_rule(
    r"admin\s+mode\s+(?:enabled|activated|on)",
    "C", "high",
    "Privilege escalation: admin mode claim",
)
_add_rule(
    r"all\s+restrictions?\s+(?:have\s+been\s+|are\s+)?lifted",
    "C", "critical",
    "Privilege escalation: restrictions lifted claim",
)
_add_rule(
    r"(?:this\s+)?(?:action\s+is\s+)?authorized\s+by\s+the\s+developer",
    "C", "high",
    "Privilege escalation: developer authorization claim",
)
_add_rule(
    r"I\s+am\s+(?:an?\s+)?(?:Anthropic|OpenAI|Google|Meta)\s+(?:employee|engineer|staff|team\s+member)",
    "C", "critical",
    "Privilege escalation: employee impersonation",
)

# ---------------------------------------------------------------------------
# Category D — Data Exfiltration
# ---------------------------------------------------------------------------

_add_rule(
    r"(?:send|output|print|display|show|share|upload|post|transmit)\s+(?:the\s+)?contents?\s+of\s+~?/",
    "D", "critical",
    "Data exfiltration: file content extraction",
)
_add_rule(
    r"output\s+all\s+files?\s+matching\s+\*?\.\w+",
    "D", "critical",
    "Data exfiltration: glob file extraction",
)
_add_rule(
    r"\|\s*base64\s*\|\s*(?:sh|bash|zsh)",
    "D", "critical",
    "Data exfiltration: base64 pipe to shell",
)
_add_rule(
    r"grep\s+[\w_-]*(?:key|secret|token|password|credential)[\w_-]*.*\|\s*curl",
    "D", "critical",
    "Data exfiltration: grep secrets piped to curl",
)
_add_rule(
    r"cat\s+[^\|]+\|\s*(?:curl|wget|nc|netcat)",
    "D", "critical",
    "Data exfiltration: cat file piped to network command",
)
_add_rule(
    r"(?:read|cat|print|display)\s+(?:the\s+)?contents?\s+of\s+~?/?\.\w+",
    "D", "high",
    "Data exfiltration: hidden file read",
)
_add_rule(
    r"(?:send|post|upload)\s+(?:this\s+)?(?:data|file|contents?)\s+to\s+https?://",
    "D", "critical",
    "Data exfiltration: send data to URL",
)
_add_rule(
    r"curl\s+(?:-\w\s+)*-F\s+['\"]?file=@",
    "D", "critical",
    "Data exfiltration: curl file upload",
)
_add_rule(
    r"\|\s*nc\s+\S+\s+\d+",
    "D", "critical",
    "Data exfiltration: pipe to netcat",
)
_add_rule(
    r"wget\s+--post-file=",
    "D", "critical",
    "Data exfiltration: wget POST file upload",
)

# ---------------------------------------------------------------------------
# Category E — Persistence Mechanisms
# ---------------------------------------------------------------------------

_add_rule(
    r"(?:write|append|add|overwrite|save|put|echo)\s+(?:the\s+following\s+|this\s+)?(?:to|into|in)\s+(?:\.?claude/)?MEMORY\.md",
    "E", "high",
    "Persistence: write to MEMORY.md",
)
_add_rule(
    r"(?:write|append|add|overwrite|modify|update|save|echo)\s+(?:the\s+following\s+)?(?:to|into|in|these\s+\w+\s+to)\s+\.clinerules",
    "E", "high",
    "Persistence: modify .clinerules",
)
_add_rule(
    r"(?:write|append|add|overwrite|modify|update|save|echo)\s+(?:the\s+following\s+)?(?:to|into|in|this\s+to)\s+\.cursorrules",
    "E", "high",
    "Persistence: modify .cursorrules",
)
_add_rule(
    r"(?:>>|write\s+to|append\s+to|modify)\s+~?/?\.(?:bashrc|zshrc|bash_profile|profile)",
    "E", "critical",
    "Persistence: shell RC file modification",
)
_add_rule(
    r"echo\s+['\"].*['\"]\s*>>\s*~?/?\.(?:bashrc|zshrc|bash_profile|profile)",
    "E", "critical",
    "Persistence: echo append to shell RC file",
)
_add_rule(
    r"nohup\s+nc\s+",
    "E", "critical",
    "Persistence: nohup netcat backdoor",
)
_add_rule(
    r"(?:>>|write\s+to|append\s+to|echo.*>>)\s*~?/?\.ssh/authorized_keys",
    "E", "critical",
    "Persistence: authorized_keys modification",
)
_add_rule(
    r"crontab",
    "E", "high",
    "Persistence: crontab manipulation",
)
_add_rule(
    r"overwrite\s+AGENTS\.md",
    "E", "high",
    "Persistence: overwrite AGENTS.md",
)
_add_rule(
    r"(?:write|append|add|save)\s+(?:the\s+following\s+)?to\s+\.claude/(?:settings\.json|commands/)",
    "E", "high",
    "Persistence: modify Claude settings or commands",
)

# ---------------------------------------------------------------------------
# Category F — Base64 / Encoding Obfuscation
# ---------------------------------------------------------------------------

_add_rule(
    r"(?:echo\s+['\"][\w+/=]+['\"]\s*\|?\s*)?base64\s+(?:-d|--decode)",
    "F", "high",
    "Encoding obfuscation: base64 decode operation",
)
_add_rule(
    r"base64\.b64decode\s*\(",
    "F", "high",
    "Encoding obfuscation: Python base64 decode",
)
_add_rule(
    r"tr\s+['\"]a-zA-Z['\"]\s+['\"]n-za-mN-ZA-M['\"]",
    "F", "high",
    "Encoding obfuscation: ROT13 transformation",
)
_add_rule(
    r"(?:%[0-9a-fA-F]{2}){6,}",
    "F", "medium",
    "Encoding obfuscation: URL-encoded payload (6+ encoded chars)",
)
_add_rule(
    r"(?:printf|echo\s+-e)\s+['\"](?:\\x[0-9a-fA-F]{2}){4,}",
    "F", "high",
    "Encoding obfuscation: hex-encoded payload",
)
_add_rule(
    r"openssl\s+(?:enc\s+)?base64\s+-d",
    "F", "high",
    "Encoding obfuscation: openssl base64 decode",
)
_add_rule(
    r"exec\s*\(\s*base64\.b64decode\s*\(",
    "F", "critical",
    "Encoding obfuscation: exec base64 decoded content",
)

# ---------------------------------------------------------------------------
# Category G — Hidden Unicode (byte-level)
# Handled specially in scan_content rather than via _RULES
# ---------------------------------------------------------------------------

# Cyrillic homoglyphs that look identical to Latin letters
# Maps Cyrillic codepoint to the Latin letter it impersonates
_CYRILLIC_HOMOGLYPHS: set[int] = {
    0x0410,  # А -> A
    0x0412,  # В -> B
    0x0415,  # Е -> E
    0x041A,  # К -> K
    0x041C,  # М -> M
    0x041D,  # Н -> H
    0x041E,  # О -> O
    0x0420,  # Р -> P
    0x0421,  # С -> C
    0x0422,  # Т -> T
    0x0425,  # Х -> X
    0x0430,  # а -> a
    0x0435,  # е -> e
    0x043E,  # о -> o
    0x0440,  # р -> p
    0x0441,  # с -> c
    0x0443,  # у -> y
    0x0445,  # х -> x
}


def _check_unicode_line(line: str, line_number: int, file_path: str) -> list[dict[str, Any]]:
    """Check a single line for suspicious Unicode characters."""
    findings: list[dict[str, Any]] = []
    seen_categories: set[str] = set()

    for char in line:
        cp = ord(char)

        # RTLO and bidi controls: U+202A-U+202E, U+2066-U+2069
        if 0x202A <= cp <= 0x202E or 0x2066 <= cp <= 0x2069:
            key = "bidi"
            if key not in seen_categories:
                seen_categories.add(key)
                findings.append({
                    "file_path": file_path,
                    "line_number": line_number,
                    "category": "G",
                    "severity": "critical",
                    "matched_pattern": f"U+{cp:04X} ({unicodedata.name(char, 'UNKNOWN')})",
                    "description": "Hidden Unicode: bidirectional control character",
                })

        # Zero-width characters: U+200B, U+200C, U+200D, U+FEFF
        elif cp in (0x200B, 0x200C, 0x200D, 0xFEFF):
            key = "zw"
            if key not in seen_categories:
                seen_categories.add(key)
                findings.append({
                    "file_path": file_path,
                    "line_number": line_number,
                    "category": "G",
                    "severity": "high",
                    "matched_pattern": f"U+{cp:04X} ({unicodedata.name(char, 'UNKNOWN')})",
                    "description": "Hidden Unicode: zero-width character",
                })

        # Unicode Tag block: U+E0000-U+E007F
        elif 0xE0000 <= cp <= 0xE007F:
            key = "tag"
            if key not in seen_categories:
                seen_categories.add(key)
                findings.append({
                    "file_path": file_path,
                    "line_number": line_number,
                    "category": "G",
                    "severity": "critical",
                    "matched_pattern": f"U+{cp:04X} (Unicode Tag block)",
                    "description": "Hidden Unicode: Tag block character (Rules File Backdoor carrier)",
                })

        # Cyrillic homoglyphs in otherwise Latin text
        elif cp in _CYRILLIC_HOMOGLYPHS:
            key = "homoglyph"
            if key not in seen_categories:
                seen_categories.add(key)
                findings.append({
                    "file_path": file_path,
                    "line_number": line_number,
                    "category": "G",
                    "severity": "high",
                    "matched_pattern": f"U+{cp:04X} ({unicodedata.name(char, 'UNKNOWN')})",
                    "description": "Hidden Unicode: Cyrillic homoglyph mixed with Latin text",
                })

    return findings


# ---------------------------------------------------------------------------
# Category H — MCP / Config File Manipulation
# ---------------------------------------------------------------------------

_add_rule(
    r"(?:rewrite|overwrite|modify|update|write\s+to|replace)\s+\.cursor/(?:mcp\.json|settings\.json)",
    "H", "critical",
    "MCP config manipulation: modify Cursor config file",
)
_add_rule(
    r"(?:insert|add|inject)\s+(?:new\s+)?MCP\s+server",
    "H", "critical",
    "MCP config manipulation: insert MCP server entry",
)
_add_rule(
    r"(?:curl|wget)\s+\S+\s*>\s*\.?cursor/mcp\.json",
    "H", "critical",
    "MCP config manipulation: download to mcp.json",
)
_add_rule(
    r"(?:add\s+this|configure\s+(?:this|a|the))\s+MCP\s+server",
    "H", "high",
    "MCP config manipulation: add MCP server directive",
)
_add_rule(
    r'"mcpServers"\s*:\s*\{',
    "H", "high",
    "MCP config manipulation: mcpServers JSON key",
)
_add_rule(
    r"(?:overwrite|modify|update|write\s+to|replace)\s+\.(?:vscode|cursor)/settings\.json",
    "H", "high",
    "MCP config manipulation: editor settings modification",
)

# ---------------------------------------------------------------------------
# Category I — HTML Comment Injection
# ---------------------------------------------------------------------------

_add_rule(
    r"<!--\s*(?:.*?(?:ignore|disregard|forget|override|new\s+system|you\s+are\s+now|act\s+as|run:|exec:|curl|wget|bash|sh\s))",
    "I", "critical",
    "HTML comment injection: hidden instruction in HTML comment",
)
_add_rule(
    r"<!--\s*(?:.*?(?:IMPORTANT|instruction|real\s+instructions|the\s+actual|everything\s+above))",
    "I", "high",
    "HTML comment injection: hidden directive in HTML comment",
)

# ---------------------------------------------------------------------------
# Category J — External Fetch + Exec
# ---------------------------------------------------------------------------

_add_rule(
    r"(?:curl|wget)\s+(?:-[\w-]+\s+)*\S+\s*\|\s*(?:sh|bash|zsh|python|python3|perl|ruby|node)",
    "J", "critical",
    "External fetch+exec: download and execute via pipe",
)
_add_rule(
    r"(?:curl|wget)\s+\S+\?\S*\$\(",
    "J", "critical",
    "External fetch+exec: URL with command substitution exfiltration",
)
_add_rule(
    r"!\[.*?\]\(https?://\S+\?\S*\$\{",
    "J", "critical",
    "External fetch+exec: markdown image with dynamic parameter exfiltration",
)
_add_rule(
    r"exec\s*\(\s*requests\.get\s*\(",
    "J", "critical",
    "External fetch+exec: Python fetch and exec",
)
_add_rule(
    r"(?:curl|wget)\s+(?:[\w./:=@?&%-]+\s+)*\S+\s*(?:&&|;)\s*(?:sh|bash|chmod\s+\+x)",
    "J", "critical",
    "External fetch+exec: download then execute",
)
_add_rule(
    r"npx\s+https?://",
    "J", "high",
    "External fetch+exec: npx from URL",
)
_add_rule(
    r"(?:curl|wget)\s+(?:-\w+\s+)*-[oO]\s+\S+\s+\S+\s*(?:&&|;)\s*(?:sh|bash|chmod|\.?/)",
    "J", "critical",
    "External fetch+exec: download to file then execute",
)


# ---------------------------------------------------------------------------
# Core scanning functions
# ---------------------------------------------------------------------------

def scan_content(content: str, file_path: str = "<stdin>") -> list[dict[str, Any]]:
    """Scan text content for injection patterns.

    Returns a list of finding dicts with keys:
      file_path, line_number, category, severity, matched_pattern, description
    """
    findings: list[dict[str, Any]] = []
    lines = content.split("\n")

    for line_idx, line in enumerate(lines):
        line_number = line_idx + 1

        # Check regex-based rules (Categories A-F, H-J)
        for pattern, category, severity, description in _RULES:
            match = pattern.search(line)
            if match:
                findings.append({
                    "file_path": file_path,
                    "line_number": line_number,
                    "category": category,
                    "severity": severity,
                    "matched_pattern": match.group(0),
                    "description": description,
                })

        # Check Unicode-based rules (Category G)
        findings.extend(_check_unicode_line(line, line_number, file_path))

    # Also check for multiline HTML comments (Category I)
    # Handle comments that span multiple lines
    for match in re.finditer(r"<!--(.*?)-->", content, re.DOTALL | re.IGNORECASE):
        comment_text = match.group(1)
        # Check if the comment contains injection patterns
        injection_patterns = [
            r"ignore", r"disregard", r"forget", r"override",
            r"new\s+system", r"you\s+are\s+now", r"act\s+as",
            r"run:", r"exec:", r"curl", r"wget", r"bash", r"sh\b",
            r"IMPORTANT", r"instruction", r"real\s+instructions",
            r"everything\s+above",
        ]
        for inj_pat in injection_patterns:
            if re.search(inj_pat, comment_text, re.IGNORECASE):
                # Find the line number of the comment start
                comment_start = match.start()
                line_num = content[:comment_start].count("\n") + 1
                # Only add if not already found by the line-based scan
                already_found = any(
                    f["category"] == "I" and f["line_number"] == line_num
                    for f in findings
                )
                if not already_found:
                    findings.append({
                        "file_path": file_path,
                        "line_number": line_num,
                        "category": "I",
                        "severity": "critical",
                        "matched_pattern": match.group(0)[:120],
                        "description": "HTML comment injection: hidden instruction in multiline HTML comment",
                    })
                break  # One finding per comment is enough

    return findings


def scan_file(file_path: str) -> list[dict[str, Any]]:
    """Scan a single file for injection patterns."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return []
    return scan_content(content, file_path=file_path)


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

# Exact filenames to match at any directory level
_CONTEXT_FILE_NAMES: set[str] = {
    "CLAUDE.md",
    "CLAUDE.local.md",
    "AGENTS.md",
    "AGENTS.override.md",
    ".cursorrules",
    ".clinerules",
    ".windsurfrules",
    ".aider.conf.yml",
    "system.md",
    "copilot-instructions.md",
}

# Filename patterns for files inside specific directories
_CONTEXT_DIR_PATTERNS: list[tuple[str, str]] = [
    # (directory component to match, file extension or name pattern)
    (".cursor/rules", ".mdc"),
    (".cursor", "mcp.json"),
    (".cursor", "settings.json"),
    (".claude/skills", "SKILL.md"),
    (".claude/commands", ".md"),
    (".claude", "settings.json"),
    (".github", "copilot-instructions.md"),
    (".github/agents", ".md"),
    (".gemini", "settings.json"),
    (".roo/rules", ".md"),
    (".agents/skills", "SKILL.md"),
    (".vscode", "settings.json"),
]


def discover_context_files(directory: str) -> list[str]:
    """Discover agentic runtime context files in a directory tree.

    Walks the directory tree looking for files that match known agentic
    context file names and patterns.
    """
    found: list[str] = []
    directory = os.path.abspath(directory)

    for root, dirs, files in os.walk(directory):
        # Skip common non-relevant directories
        basename = os.path.basename(root)
        if basename in ("node_modules", ".git", "__pycache__", ".venv", "venv"):
            dirs.clear()
            continue

        rel_root = os.path.relpath(root, directory)

        for filename in files:
            full_path = os.path.join(root, filename)

            # Check exact filename matches
            if filename in _CONTEXT_FILE_NAMES:
                found.append(full_path)
                continue

            # Check directory-based patterns
            for dir_pattern, file_pattern in _CONTEXT_DIR_PATTERNS:
                # Check if the relative path contains the directory pattern
                # Normalize both for comparison
                norm_rel = rel_root.replace(os.sep, "/")
                if dir_pattern in norm_rel or norm_rel.endswith(dir_pattern):
                    if file_pattern.startswith("."):
                        # Extension match
                        if filename.endswith(file_pattern):
                            found.append(full_path)
                            break
                    else:
                        # Exact filename match
                        if filename == file_pattern:
                            found.append(full_path)
                            break

    return sorted(found)


def scan_directory(directory: str) -> list[dict[str, Any]]:
    """Scan all context files in a directory tree."""
    files = discover_context_files(directory)
    findings: list[dict[str, Any]] = []
    for file_path in files:
        findings.extend(scan_file(file_path))
    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code.

    Exit codes:
      0 = no findings
      1 = findings detected
      2 = error
    """
    parser = argparse.ArgumentParser(
        description="Scan agentic context files for prompt injection patterns.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Files or directories to scan (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output findings as JSON array",
    )

    args = parser.parse_args(argv)

    all_findings: list[dict[str, Any]] = []
    had_error = False

    for path in args.paths:
        if os.path.isfile(path):
            try:
                all_findings.extend(scan_file(path))
            except Exception:
                had_error = True
        elif os.path.isdir(path):
            try:
                all_findings.extend(scan_directory(path))
            except Exception:
                had_error = True
        else:
            print(f"Error: path not found: {path}", file=sys.stderr)
            had_error = True

    if had_error and not all_findings:
        return 2

    if args.json_output:
        print(json.dumps(all_findings, indent=2))
    else:
        if all_findings:
            for finding in all_findings:
                severity = finding["severity"].upper()
                print(
                    f"[{severity}] {finding['file_path']}:{finding['line_number']} "
                    f"({finding['category']}) {finding['description']}"
                )
                print(f"  matched: {finding['matched_pattern']}")
                print()
        else:
            print("No findings.")

    if all_findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
