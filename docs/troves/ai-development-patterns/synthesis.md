# AI Development Patterns — Synthesis

## Overview

Paul Duvall's AI Development Patterns is an open-source catalog of 27 patterns for building software with AI assistance, organized into a three-tier progression: Foundation (6), Development (17), and Operations (4), plus 18+ experimental patterns. The repo represents a practitioner-driven effort to codify emerging practices in a field where terminology itself is still unsettled (AI-native development? agentic coding? vibe coding?).

## Key findings

### Structured progression over ad-hoc adoption
The catalog is organized as a dependency graph, not a flat list. Foundation patterns (Readiness Assessment, Codified Rules, Security Sandbox) are prerequisites for Development patterns, which in turn enable Operations patterns. Each pattern lists explicit dependencies. This mirrors swain's own Vision -> Initiative -> Epic -> Spec hierarchy — both impose a directed graph over work that teams would otherwise approach ad-hoc.

### Rules-as-code is foundational
The Codified Rules pattern treats AI coding standards as version-controlled config files (CLAUDE.md, .cursorrules, .windsurf/rules.md). This is the single most interconnected pattern — it feeds into Context Persistence, Progressive Disclosure, Event Automation, Custom Commands, and Centralized Rules. Swain's AGENTS.md + skill files serve the same function, but Duvall's approach is multi-tool (Claude, Cursor, Windsurf, Gemini) while swain's is deep-single-tool.

### Context is a finite resource
Context Persistence explicitly treats the AI context window as a limited resource requiring structured management: TODO.md, DECISIONS.log, NOTES.md, scratchpad.md. The compaction and session resume protocols are directly comparable to swain-session's bookmark/walkaway/session-state lifecycle. The key difference: Duvall's approach is file-schema-based (markdown files with conventions); swain's is tool-integrated (scripts that read and write session state).

### Parallel agents need isolation and coordination
The Parallel Agents pattern (Advanced) uses Docker containers or git worktrees for isolation, shared memory for coordination, and conflict scanners for merge safety. This aligns closely with swain's worktree isolation model (AGENTS.md: "All file-mutating work happens in a worktree") and the multi-agent-collision-vectors trove's findings on TOCTOU and merge-skew risks.

### Anti-patterns are first-class
Every pattern includes a documented anti-pattern. The repo also maintains `.ai/knowledge/failures.md` — a running log of what goes wrong (HS256 defaults, missing input validation, flaky test generation). This is structurally similar to swain's retrospective system, but less formal (no retro IDs, no EPIC scoping).

### Spec-driven development with authority levels
The Spec-Driven Development pattern introduces an authority-level system (system > platform > feature) for resolving conflicting requirements. Specs are machine-readable with traceability footnotes linking to tests. Swain's SPEC artifacts serve a similar role but without authority-level precedence — swain uses the Vision hierarchy for precedence instead.

### Event Automation maps to hooks
The Event Automation pattern attaches shell commands to assistant lifecycle events (pre-tool-use, post-tool-use, session start). This maps directly to Claude Code hooks and swain's pre-commit/validation infrastructure. Duvall documents security hooks (blocking .env edits, gitleaks scanning) as a primary use case.

## Points of agreement with swain

1. **Isolation-first for agents** — both mandate worktree or container isolation for file-mutating work
2. **Rules as code** — both version-control AI behavioral rules (AGENTS.md vs CLAUDE.md + .ai/rules/)
3. **Session continuity** — both persist context across sessions via structured files
4. **Anti-pattern documentation** — both treat "what not to do" as a first-class artifact
5. **Progressive decomposition** — both break work into small, independently verifiable units

## Points of divergence from swain

1. **Multi-tool vs. deep-single-tool** — Duvall is tool-agnostic (Claude, Cursor, Windsurf, Gemini); swain is deep in Claude Code with skill-level integration
2. **Team-oriented vs. solo-oriented** — Duvall targets teams (Centralized Rules, Kanban workflows, two-pizza team sizing); swain targets a solo developer with operator sustainability
3. **Maturity-gated progression** — Duvall gates patterns by team maturity (Beginner/Intermediate/Advanced); swain gates by artifact lifecycle (Proposed -> Active -> Completed)
4. **No artifact hierarchy** — Duvall's patterns are flat (no Vision/Initiative/Epic/Spec tree); swain's hierarchy provides strategic context that Duvall's doesn't
5. **Broader scope, shallower depth** — 27 patterns with examples; swain has fewer named patterns but deeper tooling (scripts, state machines, chart rendering)

## Gaps

1. **No retrospective system** — the repo captures failures in `.ai/knowledge/failures.md` but has no structured retro process
2. **No artifact lifecycle** — patterns have maturity levels but no transition workflow (Proposed -> Active -> Completed)
3. **No traceability tooling** — the Automated Traceability pattern describes the concept but the examples are lightweight
4. **Limited observability** — Observable Development pattern exists but no dashboards, metrics, or session digests
5. **No decision budgeting** — no mechanism for limiting decision fatigue within a session

## Relevance to swain

High relevance as a comparable-systems reference. Duvall's catalog validates several of swain's architectural choices (isolation, rules-as-code, session persistence) while showing alternative approaches (multi-tool breadth, team scaling, authority-level specs) that could inform future swain design decisions.

The pattern naming spec (exactly two words, Title Case, concrete AI-native terms) is a useful convention swain could adopt for artifact naming consistency.

The Centralized Rules pattern (org-wide rule sync via Git) could inform a future swain feature for sharing skill configurations across projects.
