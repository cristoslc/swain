---
title: "Context-File Injection Heuristic Scanner"
artifact: SPEC-058
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-017
linked-artifacts:
  - SPIKE-020
depends-on-artifacts: []
addresses: []
evidence-pool: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# Context-File Injection Heuristic Scanner

## Problem Statement

No maintained tool exists for static scanning of agentic coding context files (AGENTS.md, CLAUDE.md, .cursorrules, skill files) for prompt injection patterns. SPIKE-020 identified this as the only vector requiring a novel BUILD component. Without this scanner, swain-security-check has no coverage for the most novel attack surface it targets.

## External Behavior

**Input:** One or more file paths (or a directory to scan recursively). Accepts context files for any agentic coding runtime: Claude Code (CLAUDE.md, AGENTS.md, skill SKILL.md files), Cursor (.cursorrules, .cursor/rules/*.mdc), Copilot (.github/copilot-instructions.md), Codex (AGENTS.md), Windsurf/Cline/Roo (.windsurfrules, .clinerules, .roo/rules/*.md), Gemini (system.md).

**Output:** JSON array of findings, each with: file path, line number, category (A-J per SPIKE-020), severity (critical/high/medium/low), matched pattern, and a human-readable description.

**Categories (from SPIKE-020):**
- A: Instruction override
- B: Role override / persona hijacking
- C: Privilege escalation / authority spoofing
- D: Data exfiltration (explicit)
- E: Persistence mechanisms
- F: Base64 / encoding obfuscation
- G: Hidden Unicode (byte-level)
- H: MCP / config file manipulation
- I: HTML comment injection
- J: External fetch + exec

**Constraints:**
- Implemented as a standalone shell/Python script in `skills/swain-security-check/scripts/`
- Zero external dependencies beyond Python 3 standard library (regex + unicodedata)
- Offline-capable — no network calls
- Exit code 0 = no findings, exit code 1 = findings present, exit code 2 = error

## Acceptance Criteria

- Given a file containing `ignore previous instructions`, when scanned, then a Category A finding is reported with severity high
- Given a file containing `you are now DAN`, when scanned, then a Category B finding is reported
- Given a file containing `echo "$SECRET" | base64 -d | sh`, when scanned, then Category F finding is reported with severity critical
- Given a file containing Unicode Tag block characters (U+E0000-U+E007F), when scanned, then a Category G finding is reported with severity critical
- Given a file containing `curl [url] > .cursor/mcp.json`, when scanned, then Category H finding is reported
- Given a file containing `<!-- ignore previous instructions -->`, when scanned, then Category I finding is reported
- Given a clean AGENTS.md with no injection patterns, when scanned, then exit code is 0 and output is an empty JSON array
- Given a directory path, when scanned, then all context files matching known runtime patterns are discovered and scanned
- All 10 categories (A-J) have at least one detection rule with a test case

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Regex-based heuristic detection only — no ML models, no LLM calls
- False positives are acceptable if documented; `.securityignore` suppression file support is out of scope for this spec (can be added later)
- Semantic-only patterns (narrative jailbreaks, implicit exfiltration) are explicitly out of scope per SPIKE-020
- The PromptGuard-86M ML wrapper is a separate future enhancement, not part of this spec

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | -- | Decomposed from EPIC-017; novel BUILD component per SPIKE-020 |
