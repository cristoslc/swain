# Synthesis: Intercom's Claude Code Plugin System

**Trove:** intercom-claude-code-plugins
**Sources:** 1 (twitter thread by @brian_scanlan)
**Date:** 2026-03-17

---

## Key Findings

Intercom has built a production Claude Code skill/plugin ecosystem: 13 plugins, 100+ skills, deployed company-wide via JAMF. The system spans engineering, data, QA, and non-technical users (design managers, PMs, customer support). The architecture has 5 recurring design patterns worth studying.

---

## Theme 1: Safety-gated production access

The most striking finding is giving Claude direct access to production systems while engineering meaningful safety rails rather than blanket blocks.

- **Rails production console via MCP** — read-replica only, blocked critical tables, mandatory model verification before every query, Okta auth, DynamoDB audit trail. Top-5 users are non-engineers.
- **Admin Tools MCP** — customer/feature flag/admin lookups. A *skill-level gate* blocks all tools until Claude loads the safety reference docs first — no cowboy queries.
- **Pattern**: permissive access + mandatory safety loading + immutable audit trail is more useful and just as safe as blocking access entirely. [brian-scanlan-intercom-claude-code]

---

## Theme 2: Closing the feedback loop from session data

Intercom treats session data as a first-class product signal that drives skill improvement automatically.

- 14 OpenTelemetry event types → Honeycomb (never capturing user prompts/messages — privacy first)
- Session transcripts → S3 (username SHA256-hashed)
- On SessionEnd: Claude Haiku analyzes the transcript and auto-classifies gaps: `missing_skill`, `missing_tool`, `repeated_failure`, `wrong_info` → posts to Slack with pre-filled GitHub issue URL
- Loop: real sessions → detected gaps → GitHub issues → new skills → better sessions [brian-scanlan-intercom-claude-code]
- Weekly GitHub Action fact-checks all CLAUDE.md files and referenced docs — keeps the knowledge base honest over time

**Relevance for swain**: swain has no equivalent session retrospective loop. SessionEnd hook → Haiku analysis is a high-leverage pattern worth adopting.

---

## Theme 3: Hooks as workflow enforcement, not just convenience

Hooks aren't optional helpers — they're used as hard enforcement mechanisms at the shell level.

- **PreToolUse**: Intercepts raw `gh pr create`, blocks unless the create-pr skill was activated first. Forces extraction of business *intent* before the mechanical PR action.
- **Branch protection hook**: Blocks ALL modifications to merged PR branches (push, commit, rebase, edit).
- **Permission analyzer trigger**: After 5 permission prompts, suggests running the transcript-based permissions analyzer. Evidence-based permissions (GREEN/YELLOW/RED classification of approved commands), written to settings.json.
- **Tool miss detector** (PostToolUse): Detects "command not found" and BSD/GNU incompatibilities in real-time (e.g., `grep -P` on MacOS). Once per session, suggests fix + updates CLAUDE.md.
- **CI monitor**: After PR creation, a background agent polls CI using ETag-based polling (zero rate-limit cost). [brian-scanlan-intercom-claude-code]

**Pattern**: hooks at lifecycle boundaries (PreToolUse, PostToolUse, SessionEnd) enforce workflow discipline that relies on humans otherwise.

---

## Theme 4: Domain-specific investigation workflows

Complex engineering problems are encoded as multi-step forensic workflows with explicit guardrails, not open-ended prompts.

- **Flaky test fixer**: 9-step forensic workflow, 20-category taxonomy of flakiness patterns. Hard rules: NEVER skip a spec, NEVER guess without CI error data. Downloads failure data from S3, sweeps for sibling instances of the same antipattern. [brian-scanlan-intercom-claude-code]
- **Incident/troubleshooting skills**: Progressive disclosure in a solid core skill that routes to specific issue handlers. Goal: all runbooks followable by Claude.
- **Log precision**: Snowflake-ingested logs with highly tuned skill (with evals) for precise log retrieval during incidents. Integrated with Honeycomb traces and Datadog metrics.
- **QA follow-up**: 7-stage pipeline — identify issues → investigate codebase → filter for quality → create GitHub issues.

**Pattern**: evals are necessary for investigative skills where "good enough" is dangerous (wrong root cause = wrong fix).

---

## Theme 5: Non-engineer access as a design constraint

Claude Code as a platform for non-engineers is a deliberate goal, not a side effect.

- Top-5 production console users: design managers, customer support engineers, PM leaders
- Claude4Data: 30+ analytics skills for Snowflake queries, Gong call analysis, finance metrics, customer health — used by sales reps, PMs, data scientists
- Local dev environment setup/troubleshooting: explicit acknowledgment that more non-engineers use developer environments now
- Skill marketplace distribution via JAMF — automated, company-wide [brian-scanlan-intercom-claude-code]

**Pattern**: the skill safety gate (load reference docs before access) is the key enabler — it lets non-engineers use powerful tools without needing to understand the underlying systems.

---

## Points of Agreement (across implied industry context)

- Skills need evals for high-stakes workflows
- Privacy-first instrumentation is non-negotiable (never log prompts)
- Hooks at lifecycle boundaries are more reliable than relying on Claude to remember workflow rules
- LSP servers meaningfully speed up code search

---

## Gaps

- No detail on skill versioning or rollback strategy when a skill regresses
- No mention of how conflicts between skills are resolved (13 plugins — what happens when two want to handle the same event?)
- Evaluation methodology for the analytics/data skills not described
- No detail on how the JAMF marketplace handles skill updates without disrupting ongoing sessions
- Non-engineer UX specifics (how do they discover which skills exist?) not described
