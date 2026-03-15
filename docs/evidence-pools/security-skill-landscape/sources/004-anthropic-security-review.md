---
source-id: "004"
title: "Claude Code Security Reviewer (anthropics/claude-code-security-review)"
type: web
url: "https://github.com/anthropics/claude-code-security-review"
fetched: 2026-03-14T00:00:00Z
hash: "sha256:pending"
---

# Claude Code Security Reviewer

An AI-powered security review GitHub Action using Claude to analyze code changes for security vulnerabilities. Also ships the built-in `/security-review` slash command in Claude Code.

## Key Points

- **Built-in**: Claude Code ships `/security-review` by default — no installation needed
- **GitHub Action**: `anthropics/claude-code-security-review@main` for PR-level automated review
- **Diff-aware**: For PRs, only analyzes changed files
- **Model**: Defaults to `claude-opus-4-1` (configurable)
- **Customizable**: Drop a custom `security-review.md` in `.claude/commands/` to override

## Vulnerability Types Detected

- Injection: SQL, command, LDAP, XPath, NoSQL, XXE
- Auth & authz: broken authentication, privilege escalation, IDOR, bypass logic, session flaws
- Data exposure: hardcoded secrets, sensitive data logging, PII violations
- Crypto: weak algorithms, improper key management, insecure random
- Input validation: missing validation, improper sanitization, buffer overflows
- Business logic: race conditions, TOCTOU
- Configuration: insecure defaults, missing security headers, permissive CORS
- Supply chain: vulnerable dependencies, typosquatting
- Code execution: RCE via deserialization, pickle injection, eval injection
- XSS: reflected, stored, DOM-based

## False Positive Filtering

Auto-excludes:
- DoS vulnerabilities
- Rate limiting concerns
- Memory/CPU exhaustion
- Generic input validation without proven impact
- Open redirects

Filtering is configurable via `false-positive-filtering-instructions` input.

## Security Limitation

Not hardened against prompt injection. Recommended for trusted PRs only (configure "Require approval for all external contributors").

## Architecture

```
claudecode/
├── github_action_audit.py   # Main audit script
├── prompts.py               # Security audit prompt templates
├── findings_filter.py       # False positive filtering logic
├── claude_api_client.py     # Claude API client
└── evals/                   # Eval tooling for arbitrary PRs
```
