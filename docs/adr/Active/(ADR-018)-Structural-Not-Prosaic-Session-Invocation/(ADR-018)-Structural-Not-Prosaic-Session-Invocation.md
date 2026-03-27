---
title: "Structural Not Prosaic Session Invocation"
artifact: ADR-018
track: standing
status: Active
author: cristos
created: 2026-03-27
last-updated: 2026-03-27
linked-artifacts:
  - ADR-017
  - EPIC-045
  - SPIKE-047
depends-on-artifacts: []
evidence-pool: ""
---

# Structural Not Prosaic Session Invocation

## Context

Swain's AGENTS.md contains a "Session startup (AUTO-INVOKE)" section that instructs the LLM to run `swain-preflight.sh` and invoke swain-session at the start of every conversation. This is a **prosaic** invocation — it relies on the LLM reading the directive and choosing to follow it. In practice, auto-invoke is almost never followed reliably. LLMs read AGENTS.md as context for *how to behave when asked*, not as a list of commands to execute unprompted.

This unreliability is fatal for session initialization: if swain-session doesn't run, the operator gets no tab naming, no focus restoration, no worktree auto-isolation, no session bookmarks. The session starts broken and the operator may not notice until they're deep into work.

The problem compounds with multi-runtime support (ADR-017). Claude Code happens to support positional args that can trigger `/swain-init` structurally. But runtimes like Crush have no mechanism to pass an initial prompt in interactive mode — making prosaic invocation the only option, which means Crush sessions will almost never initialize correctly.

## Decision

**Runtime session invocation must be structural, not prosaic.**

Structural means the invocation is guaranteed by the runtime's machinery — CLI flags, positional args, startup hooks, config-driven auto-execution — not by hoping an LLM reads and follows a markdown directive.

Specifically:

1. **Remove the AUTO-INVOKE section from AGENTS.md.** It creates a false sense of reliability. The shell launcher templates (EPIC-045) are the structural replacement.

2. **Shell launcher templates are the canonical session entry point.** The `swain` shell function passes `/swain-init` as a positional arg (or `-i` flag, depending on runtime) — this is structural because the runtime's CLI parser guarantees execution.

3. **Runtimes that cannot accept an initial prompt are Partial support (ADR-017).** This is not a temporary gap to be worked around with prosaic directives — it is a real capability limitation. Partial-support runtimes start without session initialization. The operator must manually type `/swain-init` or `/swain-session`.

4. **AGENTS.md remains the source of behavioral guidance**, not invocation triggers. It tells the LLM *how* to handle artifacts, *which* skills to route to, *what* conventions to follow — all things the LLM consults when the operator asks it to do something. It should not contain "do this before the operator says anything" directives.

## Alternatives Considered

**Keep AUTO-INVOKE as a best-effort fallback.** Even if unreliable, it sometimes works, so removing it makes things strictly worse for sessions started without the launcher. Rejected because: a directive that works 20% of the time trains the operator to expect it and be confused when it doesn't fire. Better to be consistently absent so the operator learns to use the launcher.

**Environment variable signaling.** Set `SWAIN_LAUNCHER=1` in the launcher function, then have AGENTS.md say "if SWAIN_LAUNCHER is set, run /swain-init." This is still prosaic — it adds a condition the LLM must check, doubling the compliance dependency. Rejected.

**Runtime-specific startup hooks.** File upstream feature requests for startup hooks on runtimes that lack them (e.g., Crush). Worth doing long-term, but we can't depend on upstream accepting them. Not an alternative to this decision — complementary.

## Consequences

**Positive:**
- Session initialization is reliable when using the `swain` launcher — it's guaranteed by CLI argument parsing, not LLM compliance
- AGENTS.md becomes cleaner — behavioral guidance only, no action triggers
- The distinction between Full and Partial runtime support (ADR-017) becomes meaningful and honest

**Accepted downsides:**
- Sessions started without the launcher (e.g., `claude` typed directly) will not auto-initialize. The operator must run `/swain-session` manually. This is acceptable — the launcher exists to solve this.
- Partial-support runtimes (Crush) have a degraded experience with no structural workaround. This is an honest reflection of the runtime's capabilities, not a swain bug.
- Removing AUTO-INVOKE is a breaking change for operators who relied on it (even if unreliably). The migration path is: install the shell launcher via `/swain-init`.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-27 | — | Initial creation |
