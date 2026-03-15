---
source-id: "002"
title: "OWASP Security Skill for Claude Code (agamm/claude-code-owasp)"
type: web
url: "https://github.com/agamm/claude-code-owasp"
fetched: 2026-03-14T00:00:00Z
hash: "sha256:pending"
---

# OWASP Security Skill for Claude Code

A Claude Code skill providing the latest OWASP security best practices (2025-2026) for developers building secure applications.

## What's Included

### Claude Code Skill (`owasp-security/SKILL.md`)

- **OWASP Top 10:2025** quick reference table
- **Security code review checklists** for input handling, auth, access control, data protection, and error handling
- **Secure code patterns** with unsafe/safe examples
- **OWASP Agentic AI Security (2026)** — ASI01-ASI10 risks for AI agent systems
- **ASVS 5.0** key requirements by verification level
- **Language-specific security quirks** for 20+ languages with deep analysis guidance

## Covered Standards

| Standard | Version | Focus |
|----------|---------|-------|
| OWASP Top 10 | 2025 | Web application vulnerabilities |
| OWASP ASVS | 5.0.0 | Security verification requirements |
| OWASP Agentic | 2026 | AI agent security risks (ASI01–ASI10) |

## Language Coverage

Security quirks for 20+ languages including JavaScript/TypeScript, PHP, Java, C#, C/C++, Rust, Go, Swift, Kotlin, Python, Ruby, Perl, Shell, and more. Each section includes common vulnerabilities, unsafe/safe code patterns, and key functions to watch for.

## Activation

Automatically activates when Claude Code:
- Reviews code for security vulnerabilities
- Implements authentication or authorization
- Handles user input or external data
- Works with cryptography or password storage
- Designs API endpoints
- Builds AI agent systems

## Installation

```bash
# Project-level
curl -sL https://raw.githubusercontent.com/agamm/claude-code-owasp/main/.claude/skills/owasp-security/SKILL.md \
  -o .claude/skills/owasp-security/SKILL.md --create-dirs

# Global
curl -sL https://raw.githubusercontent.com/agamm/claude-code-owasp/main/.claude/skills/owasp-security/SKILL.md \
  -o ~/.claude/skills/owasp-security/SKILL.md --create-dirs
```

## License

MIT
