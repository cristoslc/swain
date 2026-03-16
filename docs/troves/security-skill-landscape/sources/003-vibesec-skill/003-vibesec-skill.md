---
source-id: "003"
title: "VibeSec-Skill (BehiSecc/VibeSec-Skill)"
type: web
url: "https://github.com/BehiSecc/VibeSec-Skill"
fetched: 2026-03-14T00:00:00Z
hash: "sha256:pending"
---

# VibeSec-Skill

> Stop vibe coding vulnerabilities into production. An AI skill that brings 5+ years of bug bounty hunting experience directly into your AI coding workflow — so LLM models write secure code from the start.

## Philosophy

VibeSec acts as a security-first co-pilot. It teaches the model to approach code from a bug hunter's perspective, catching vulnerabilities before they ship. The SKILL.md is openly available; a "more robust version with more vulnerability coverage" exists at vibesec.sh (commercial).

**Self-described coverage:** 60-70% of common vulnerabilities.

## Covered Vulnerabilities

| Category | Covered Vulnerabilities |
|----------|------------------------|
| Access Control | IDOR, Privilege Escalation, Horizontal/Vertical Access, Mass Assignment, Token Revocation |
| Client-Side | XSS (Stored, Reflected, DOM), CSRF, Secret Key Exposure, Open Redirect |
| Server-Side | SSRF, SQL Injection, XXE, Path Traversal, Insecure File Upload |
| Authentication | Weak Passwords, Session Management, Account Lifecycle, JWT Security |
| API Security | Mass Assignment, GraphQL Security |

## Deep Coverage Features

- Bypass techniques — not just "sanitize input" but specific bypasses attackers use
- Edge cases — URL fragments, DNS rebinding, polyglot files, Unicode tricks
- Framework-aware — React, Vue, Node.js, Python, Java, .NET patterns
- Cloud-aware — metadata endpoint protection for AWS, GCP, Azure
- Checklists — actionable verification steps for each vulnerability class

## Installation

Compatible with Claude Code, Cursor, Codex, GitHub Copilot, and Antigravity. Install by cloning and placing `SKILL.md` in the appropriate skills directory for each platform.

## Notes

- Free tier is the SKILL.md (open source)
- Premium tier at vibesec.sh claims broader coverage
- Authored from bug bounty hunting background, not formal security research
