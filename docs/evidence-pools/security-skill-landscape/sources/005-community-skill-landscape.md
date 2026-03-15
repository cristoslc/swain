---
source-id: "005"
title: "Community Security Skills Landscape (awesome-claude-skills, VoltAgent/awesome-agent-skills)"
type: web
url: "https://github.com/travisvn/awesome-claude-skills"
fetched: 2026-03-14T00:00:00Z
hash: "sha256:pending"
notes: "Aggregated from multiple community skill directories"
---

# Community Security Skills Landscape

A survey of security-related skills across community repositories as of March 2026.

## Key Registries

- **travisvn/awesome-claude-skills** — curated list, includes Trail of Bits and VibeSec
- **VoltAgent/awesome-agent-skills** — 500+ skills, compatible with Claude Code, Codex, Cursor, Gemini CLI
- **BehiSecc/awesome-claude-skills** — security-focused curation
- **girikunche/claude-skills-directory** — 97 validated skills, 12 categories
- **sickn33/antigravity-awesome-skills** — 1,259+ skills including zebbern/claude-code-guide (security suite, ~60 skills)

## Security Skills Catalogued

| Skill | Source | Focus |
|-------|--------|-------|
| Trail of Bits Skills | trailofbits/skills | Professional security research: CodeQL, Semgrep, variant analysis, supply chain, smart contracts, malware, mobile |
| owasp-security | agamm/claude-code-owasp | OWASP Top 10:2025, ASVS 5.0, Agentic AI 2026, 20+ language quirks |
| VibeSec-Skill | BehiSecc/VibeSec-Skill | Bug-bounty perspective secure coding (60-70% common vulns, free) |
| defense-in-depth | obra/superpowers | Multi-layered security approaches (part of superpowers) |
| varlock-claude-skill | community | Secure env var management — prevents secrets from appearing in sessions/logs/git |
| ffuf_claude_skill | community | Integrate Claude with FFUF fuzzing, analyze results for vulnerabilities |
| security-patterns | Eyadkelleh/awesome-claude-skills-security | CTF/pentest toolkit: SecLists wordlists, injection payloads, expert agents |
| alinaqi/claude-bootstrap | community | Opinionated project init with security-first guardrails |

## obra/defense-in-depth (superpowers built-in)

From search snippets: "Implement multi-layered testing and security best practices." Listed at `github.com/obra/superpowers/blob/main/skills/defense-in-depth`. Part of the superpowers base library — already present in any superpowers installation. Focused on testing + security layering, not dedicated security analysis.

## Observations from Directory Scan

1. **No single dominant "security superpowers"** equivalent has emerged — the space is fragmented
2. Trail of Bits is the closest to an authoritative, professional-grade library
3. Most community skills are append-your-SKILL.md style guidance, not interactive workflow orchestration
4. The `/security-review` command ships built-in with Claude Code from Anthropic — baseline coverage already exists
5. Security skill categories cluster into: (a) static analysis tooling (ToB), (b) secure coding guidance (OWASP, VibeSec), (c) pentest/offensive tools (ffuf, SecLists), (d) built-in review (Anthropic)
