---
source-id: "rtk-ai-homepage"
title: "RTK — Rust Token Killer"
type: web
url: "https://www.rtk-ai.app/"
fetched: 2026-04-03T22:03:00Z
hash: "9b92d91b4263537a05fed180a2a6b8c7b6bf03da9abda145689645bf80e392ae"
---

# RTK — Rust Token Killer

Open-source (MIT), Rust-based CLI proxy that compresses command outputs before they reach an AI agent's context window. Claims 89% average noise removal, enabling 3x longer sessions and lower token costs. v0.15.2 as of fetch date. 450+ GitHub stars.

## Problem statement

Every CLI command an AI agent runs pollutes the context window with boilerplate: test runner headers, git stat lines, directory listings with metadata, full file dumps. On a 200K-token context window, this noise crowds out reasoning capacity. On pay-per-token setups, it inflates costs. On flat-rate plans, it triggers rate limits faster.

## How it works

RTK installs as a CLI prefix or auto-rewrite hook. It intercepts standard shell commands and compresses their output using command-specific filters before the output reaches the AI agent.

### Installation

```bash
# One-liner
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# Or Homebrew
brew install rtk

# Activate auto-rewrite hook (Claude Code PreToolUse hook)
rtk init --global
```

### Supported commands (30+)

RTK wraps common CLI tools with compressed output:
- **Test runners:** `rtk cargo test`, `rtk test "pytest -v"`, `rtk test "go test ./... -v"`
- **Git:** `rtk git status`, `rtk git diff`, `rtk git log`
- **File operations:** `rtk read`, `rtk grep`, `rtk find`, `rtk ls`
- **Dependencies:** `rtk deps`
- **Other:** docker, kubectl, curl, npm, and more

### Compression examples (from the site)

| Command | Raw tokens | RTK tokens | Savings |
|---------|-----------|------------|---------|
| `cargo test` (262 tests) | ~4,823 | ~11 | 99% |
| `pytest -v` (33 tests) | ~756 | ~24 | 96% |
| `git diff HEAD~1` | ~21,500 | ~1,259 | 94% |
| `cat src/main.rs` (1,295 lines) | ~10,176 | ~504 | 95% |
| `grep -rn "pub fn" src/` | ~2,108 | ~940 | 55% |
| `git status` | ~120 | ~30 | 75% |
| `find . -name "*.rs"` | ~276 | ~149 | 46% |
| `ls -la src/` | ~3,200 | ~640 | 80% |
| `git log --stat -10` | ~1,430 | ~194 | 86% |
| `Cargo.toml` (deps) | ~368 | ~55 | 85% |
| `go test` | ~592 | ~246 | 58% |

### Compression strategies by command type

- **Test runners:** Strip per-test PASS lines, retain summary + failures only. `cargo test` 262 passes -> single summary line.
- **Git diff:** Condense to diffstat + key changed hunks. Strip boilerplate context.
- **Git status:** Structured emoji-based output (modified, untracked counts).
- **Git log:** One-line-per-commit format, strip author/date/stats.
- **File read:** Skeleton mode — preserve structure declarations (`struct`, `fn`, `class`), elide bodies.
- **Grep:** Group by file, show line numbers + signatures, truncate long matches.
- **Find/ls:** Compact tree format, group by directory, show sizes.
- **Dependencies:** Summary format with counts.

### Architecture

- Written in Rust (Cargo-based project)
- ~49 source files, 262 tests
- SQLite for persistent gain tracking (`rtk gain` command)
- Filter levels: normal, aggressive (configurable per-read via `-l aggressive`)
- Auto-rewrite via Claude Code `PreToolUse` hook

## Token savings tracking

RTK tracks cumulative savings in a local SQLite database. The `rtk gain` command shows per-command breakdowns:

```
Total commands:    2,927
Input tokens:      11.6M
Output tokens:     1.4M
Tokens saved:      10.3M (89.2%)
```

A user testimonial shows 15,720 commands processed, 138M tokens saved at 88.9% efficiency over several weeks.

## Pricing and tool comparison

RTK is free and open-source. The site positions it against AI coding tool pricing:

| Tool | Price | Limits | RTK benefit |
|------|-------|--------|-------------|
| Claude Code | $20-$200/mo | 45 msgs/5h (Pro), 5-20x Max | Sessions ~3x longer |
| Cursor | $20-$200/mo | Credits/mo | Credits go ~2x further |
| Gemini CLI | Free + pay-per-token | 1,000 req/day free | ~70% less token bill |
| Aider | Free + API costs | Per API provider | ~70% less API cost |
| OpenAI Codex | $20-$200/mo | 30-1,500 msgs/5h | More iterations per cap |
| Windsurf | $15-$60/mo | 500-1,000 credits/mo | Credits last ~2x |
| Cline/Roo | Free + API costs | Per provider | ~70% less API cost |
| GitHub Copilot | Free-$39/mo | 50-1,500 premium req/mo | Better context quality |

## RTK Cloud (upcoming)

SaaS offering for teams:
- Token analytics dashboard per dev, per project, per tool
- Team savings reports
- Rate limit alerts and monitoring
- Enterprise controls (SSO, audit logs, compliance)
- Pricing: free for open-source, $15/dev/month for teams

## Adoption

Starred by developers at Apple, AWS, Barclays, Bosch, Canva, Cisco, Datadog, Deloitte, ENI, Google, Hitachi, HPE, IBM, Meta, Microsoft, OVHcloud, Zendesk.

## Technical details

- Author: Patrick Szymkowiak
- Repo: https://github.com/rtk-ai/rtk
- License: MIT
- Language: Rust
- v0.15.2 (as of fetch date)
- Platforms: macOS, Linux, Windows
- Distribution: curl installer, Homebrew, pre-built binaries, Cargo
