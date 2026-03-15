---
source-id: "001"
title: "Trail of Bits Skills Marketplace"
type: web
url: "https://github.com/trailofbits/skills"
fetched: 2026-03-14T00:00:00Z
hash: "sha256:pending"
---

# Trail of Bits Skills Marketplace

A Claude Code plugin marketplace from Trail of Bits providing skills to enhance AI-assisted security analysis, testing, and development workflows.

> Also see: [claude-code-config](https://github.com/trailofbits/claude-code-config) · [skills-curated](https://github.com/trailofbits/skills-curated) · [claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer) · [dropkit](https://github.com/trailofbits/dropkit)

## Installation

```
/plugin marketplace add trailofbits/skills
/plugin menu
```

## Available Plugins

### Smart Contract Security

| Plugin | Description |
|--------|-------------|
| building-secure-contracts | Smart contract security toolkit with vulnerability scanners for 6 blockchains |
| entry-point-analyzer | Identify state-changing entry points in smart contracts for security auditing |

### Code Auditing

| Plugin | Description |
|--------|-------------|
| agentic-actions-auditor | Audit GitHub Actions workflows for AI agent security vulnerabilities |
| audit-context-building | Build deep architectural context through ultra-granular code analysis |
| burpsuite-project-parser | Search and extract data from Burp Suite project files |
| differential-review | Security-focused differential review of code changes with git history analysis |
| fp-check | Systematic false positive verification for security bug analysis with mandatory gate reviews |
| insecure-defaults | Detect insecure default configurations, hardcoded credentials, and fail-open security patterns |
| semgrep-rule-creator | Create and refine Semgrep rules for custom vulnerability detection |
| semgrep-rule-variant-creator | Port existing Semgrep rules to new target languages with test-driven validation |
| sharp-edges | Identify error-prone APIs, dangerous configurations, and footgun designs |
| static-analysis | Static analysis toolkit with CodeQL, Semgrep, and SARIF parsing |
| supply-chain-risk-auditor | Audit supply-chain threat landscape of project dependencies |
| testing-handbook-skills | Skills from the Testing Handbook: fuzzers, static analysis, sanitizers, coverage |
| variant-analysis | Find similar vulnerabilities across codebases using pattern-based analysis |

### Malware Analysis

| Plugin | Description |
|--------|-------------|
| yara-authoring | YARA detection rule authoring with linting, atom analysis, and best practices |

### Verification

| Plugin | Description |
|--------|-------------|
| constant-time-analysis | Detect compiler-induced timing side-channels in cryptographic code |
| property-based-testing | Property-based testing guidance for multiple languages and smart contracts |
| spec-to-code-compliance | Specification-to-code compliance checker for blockchain audits |
| zeroize-audit | Detect missing or compiler-eliminated zeroization of secrets in C/C++ and Rust |

### Reverse Engineering / Mobile / Infrastructure

| Plugin | Description |
|--------|-------------|
| dwarf-expert | Interact with and understand the DWARF debugging format |
| firebase-apk-scanner | Scan Android APKs for Firebase security misconfigurations |

## Trophy Case

Bugs discovered using Trail of Bits Skills:

| Skill | Bug |
|-------|-----|
| constant-time-analysis | Timing side-channel in ML-DSA signing (RustCrypto/signatures#1144) |

## License

Creative Commons Attribution-ShareAlike 4.0 International. Made by Trail of Bits.
