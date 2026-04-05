---
source-id: "paulduvall-ai-development-patterns"
title: "AI Development Patterns — PaulDuvall"
type: repository
url: "https://github.com/PaulDuvall/ai-development-patterns"
fetched: 2026-04-03T21:30:00Z
hash: "f198796b736ae4a29d304aac291162bde75b74787d80a57e20eb4c8fae250c02"
highlights:
  - "README-patterns.md"
  - "patterns.yaml"
  - "CLAUDE.md"
  - "AGENTS.md"
  - "pattern-spec.md"
  - "experiments-README.md"
selective: true
---

# AI Development Patterns — PaulDuvall

A comprehensive, open-source collection of 27 patterns for building software with AI assistance. Organized by implementation maturity (Beginner / Intermediate / Advanced) and development lifecycle phase (Foundation, Development, Operations). Created by Paul Duvall based on hands-on experience.

## Repository structure

```
.ai/                          # AI configuration (rules, prompts, knowledge)
.beads/                       # Issue tracking via bd (beads)
.github/workflows/            # CI: pattern validation, Claude review, deploy
docs/                         # Blog posts, examples, specs
examples/                     # Working implementations of stable patterns
experiments/                  # Advanced/experimental patterns
scripts/                      # Repo automation (validation, rename, updates)
tests/                        # Pytest validation suite
AGENTS.md                     # Agent instructions (bd issue tracker workflow)
CLAUDE.md                     # Claude Code session context
pattern-spec.md               # Pattern creation spec and naming rules
patterns.yaml                 # Machine-readable pattern catalog
README.md                     # Main documentation — all 27 patterns
```

## Pattern catalog (27 patterns)

### Foundation (6 patterns)

| Pattern | Maturity | Description |
|---------|----------|-------------|
| Readiness Assessment | Beginner | Evaluate codebase and team readiness for AI integration |
| Codified Rules | Beginner | Version AI coding standards as config files (CLAUDE.md, .cursorrules) |
| Security Sandbox | Beginner | Isolate AI tools from secrets and sensitive data |
| Developer Lifecycle | Intermediate | 9-stage process: problem definition through deployment |
| Tool Integration | Intermediate | Connect AI to external data sources, APIs, and tools |
| Issue Generation | Intermediate | Generate Kanban-optimized work items (4-8 hours) from requirements |

### Development (17 patterns)

| Pattern | Maturity | Description |
|---------|----------|-------------|
| Spec-Driven Development | Intermediate | Executable specs with authority levels guide AI code generation |
| Image Spec | Intermediate | Use diagrams/mockups as primary specs for AI implementation |
| Planned Implementation | Beginner | Generate implementation plans before writing code |
| Progressive Enhancement | Beginner | Build features through small, deployable iterations |
| Choice Generation | Intermediate | Generate multiple implementation options for comparison |
| Atomic Decomposition | Intermediate | Break features into 1-2 hour tasks for parallel AI agents |
| Parallel Agents | Advanced | Run multiple AI agents concurrently on isolated tasks |
| Context Persistence | Intermediate | Structured memory schemas and session continuity protocols |
| Constrained Generation | Beginner | Specific constraints prevent over-engineering |
| Event Automation | Intermediate | Custom commands at assistant lifecycle events |
| Custom Commands | Intermediate | Extend built-in command vocabularies with domain expertise |
| Progressive Disclosure | Intermediate | Load rules incrementally by task context |
| Observable Development | Intermediate | Strategic logging that makes system behavior visible to AI |
| Guided Refactoring | Intermediate | AI-detected code smells with measurable quality metrics |
| Guided Architecture | Intermediate | Apply DDD, Well-Architected, 12-Factor via AI |
| Automated Traceability | Intermediate | Automated links: requirements, specs, tests, code, docs |
| Error Resolution | Intermediate | Collect error context, AI diagnoses root causes |

### Operations (4 patterns)

| Pattern | Maturity | Description |
|---------|----------|-------------|
| Policy Generation | Advanced | Transform compliance requirements into executable Cedar/OPA policies |
| Security Orchestration | Intermediate | Aggregate security tools, AI summarizes for actionable insights |
| Centralized Rules | Advanced | Org-wide AI rules via central Git repo with language auto-detection |
| Baseline Management | Advanced | Intelligent performance baselines and threshold automation |

### Experimental (18+ patterns)

In `experiments/` — includes Handoff Protocols, Testing Orchestration, Workflow Orchestration, Review Automation, Debt Forecasting, Pipeline Synthesis, Deployment Synthesis, Drift Remediation, Test Promotion, Asynchronous Research, and more.

## Key architectural concepts

### Three-tier pattern organization
Foundation enables Development enables Operations. Each pattern lists dependencies; maturity levels (Beginner -> Intermediate -> Advanced) indicate a learning progression, not a waterfall gate.

### Pattern spec rules
- Names must be exactly two words, Title Case
- Every pattern requires: Maturity, Description, Related Patterns, Implementation, Anti-pattern
- Categories: Foundation, Development, Operations
- Naming uses concrete, AI-native engineering terms

### Task sizing hierarchy
- Issue Generation: 4-8 hour Kanban work items for human teams
- Atomic Decomposition: 1-2 hour tasks for parallel AI agents
- Progressive Enhancement: daily deployment cycles for rapid feedback

### Anti-pattern inclusion
Every pattern documents what NOT to do. A separate Anti-Patterns Reference section catalogs common failures across Foundation, Development, and Operations.

### Implementation phasing
- Phase 1 (Weeks 1-2): Readiness Assessment, Codified Rules, Security Sandbox, Developer Lifecycle
- Phase 2 (Weeks 3-4): Spec-Driven Development, Progressive Enhancement, Atomic Decomposition
- Phase 3 (Weeks 5-6): Policy Generation, Security Orchestration, Baseline Management

Teams practicing continuous delivery should implement security and deployment patterns from week 1.

## Related context

- Author: Paul Duvall
- License: MIT
- Uses `bd` (beads) for issue tracking
- CI: GitHub Actions for pattern validation, Claude Code review
- Repo includes `.ai/knowledge/` with documented successes and failures
