---
title: "External Security Skill Hook Interface"
artifact: SPEC-065
track: implementable
status: Proposed
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
type: feature
parent-epic: EPIC-023
linked-artifacts:
  - SPIKE-020
depends-on-artifacts:
  - SPEC-062
  - SPEC-063
  - SPEC-064
addresses: []
evidence-pool: "security-skill-landscape"
source-issue: ""
swain-do: required
---

# External Security Skill Hook Interface

## Problem Statement

EPIC-023's security gates should integrate with external security skills (Trail of Bits `trailofbits/skills`, `agamm/claude-code-owasp`) as optional additive hooks. Without a defined interface, integrating these skills requires ad-hoc wiring that breaks when skill APIs change. A stable hook interface lets the community build security skills that plug into swain-do's execution flow.

## External Behavior

**Hook points (matching EPIC-023's three integration points):**

1. **Pre-claim hook:** After threat surface detection, before briefing — external skills can contribute additional guidance
   - Interface: skill provides a `security-briefing` command that accepts task metadata (title, tags, categories) and returns markdown guidance
   - Candidates: Trail of Bits `sharp-edges`, `insecure-defaults`; `agamm/owasp-security`

2. **During-implementation hook:** For security-sensitive tasks, external skills can provide always-on co-pilot guidance
   - Interface: skill provides a `security-context` command that accepts file paths and returns relevant security notes
   - Candidate: `agamm/owasp-security` (language-specific quirks, ASVS 5.0)

3. **Completion hook:** After swain-security-check runs, external skills can add differential review
   - Interface: skill provides a `security-review` command that accepts a git diff and returns findings
   - Candidate: Trail of Bits `differential-review`

**Detection:** Skills are discovered by checking for known SKILL.md paths:
```
.claude/skills/trailofbits-*/SKILL.md
.agents/skills/trailofbits-*/SKILL.md
.claude/skills/owasp-security/SKILL.md
.agents/skills/owasp-security/SKILL.md
```

**Fallback:** When no external skills are installed, all hooks are no-ops. Built-in guidance (SPEC-063) always runs.

## Acceptance Criteria

- Given `trailofbits/skills` is installed, when a security-sensitive task is claimed, then Trail of Bits `sharp-edges` guidance is included in the pre-claim briefing
- Given `agamm/owasp-security` is installed, when a security-sensitive task is being implemented, then OWASP guidance is available
- Given no external security skills are installed, when any security gate runs, then only built-in guidance is used (no errors, no degradation)
- The hook interface is documented in the swain-security-check skill file so external skill authors can build compatible skills
- Adding a new external skill requires no changes to swain-do or swain-security-check core code — only detection path registration

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

- Interface definition only — does not vendor or install external skills
- External skills remain optional; swain never depends on them
- The interface is intentionally simple (command-based) to avoid tight coupling
- Depends on all three preceding EPIC-023 specs (SPEC-062, 063, 064) being at least designed

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-17 | -- | Decomposed from EPIC-023; defines the external skill integration surface |
