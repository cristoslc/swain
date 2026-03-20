# Retro: Spike Findings Not Back-Propagated to Dependent Artifacts

**Date:** 2026-03-19
**Scope:** VISION-002 session — INITIATIVE-011 and INITIATIVE-012 completion
**Period:** 2026-03-19 (single session)

## Summary

During rapid execution of VISION-002, SPIKE-032 (Docker Sandboxes OAuth Limitation) completed with a critical finding: OAuth/Max subscription auth is fundamentally broken in Docker Sandboxes. This finding directly invalidated SPEC-067 AC-8, which claimed OAuth works via `/login` inside the sandbox. Despite SPIKE-032 completing before implementation began, its findings were never propagated back to SPEC-067, were not incorporated into SPEC-068's detection logic, and the resulting runbook (RUNBOOK-002) gave users a Quick Start that would fail on first use for Max subscribers.

The operator discovered this during manual testing when `./swain-box` hung indefinitely (detection bug) and would have launched a broken Claude sandbox (no API key gate).

## Artifacts

| Artifact | Title | Role in failure |
|----------|-------|-----------------|
| SPIKE-032 | Docker Sandboxes OAuth Limitation Workaround | Finding source — completed correctly |
| SPEC-067 | swain-box: Docker Sandboxes Launcher | AC-8 invalidated by SPIKE-032 but never updated |
| SPEC-068 | Agent Runtime Detection & Selection Menu | No reference to SPIKE-032; no API key gate for Claude |
| SPEC-071 | Credential-Scoped Sandbox Launcher | Correctly references SPIKE-032 (only artifact that does) |
| RUNBOOK-002 | Sandbox Launcher Operations | Quick Start doesn't gate on API key availability |
| swain-box (code) | The script itself | Warns but doesn't block when no API key detected |

## Failure chain

```
SPIKE-032 completes → "Conditional Go: API key works, OAuth broken"
    ↓
Agent creates SPEC-071 → correctly links SPIKE-032 as dependency ✓
    ↓
Agent implements SPEC-068 → does NOT reference SPIKE-032 ✗
    (detection logic shows Claude as "available" without checking auth viability)
    ↓
Agent implements swain-box code → warns about missing API key but doesn't block ✗
    (SPEC-067 AC-8 still claims OAuth works, so warning is advisory not blocking)
    ↓
Agent writes RUNBOOK-002 → Quick Start says "just launch" ✗
    (because the spec says OAuth is a valid path)
    ↓
Operator tests → hangs on detection probe, then would get auth failure inside sandbox
```

## Root cause analysis

### 1. No back-propagation mechanism for spike findings

When SPIKE-032 completed, swain had no process to ask: "Which existing artifacts assumed the opposite of what this spike found?" The spike's `linked-artifacts` field connects forward (to artifacts that depend on the spike), but there's no reverse scan for artifacts whose assumptions are *invalidated* by the findings.

**SPEC-067 was already Complete** when SPIKE-032 ran. The current alignment checking system (alignment-checking.md) only runs during artifact *creation* — it doesn't re-evaluate completed artifacts when new evidence arrives.

### 2. Alignment checking is creation-time only

The `STALE_ALIGNMENT` finding type exists in alignment-checking.md and describes exactly this scenario: "The artifact was aligned when created, but its parent changed since." But it's only evaluated during `chart.sh scope` at creation time. There's no periodic or event-driven re-evaluation.

### 3. xref checks are structural, not semantic

specwatch/xref checks for missing reciprocal references and undeclared body references — structural graph integrity. It does not check for semantic conflicts like "SPIKE-032 says OAuth is broken but SPEC-067 AC-8 says OAuth works." This would require reading the content, not just the frontmatter.

### 4. Speed over rigor during autonomous execution

The operator said "keep going autonomously until initiative-012 is completed." The agent optimized for throughput — creating, implementing, and transitioning artifacts in rapid succession. The brainstorming step was skipped for SPEC-068 (the conversation *was* the brainstorm, but the formal skill invocation with its structured exploration would have forced re-reading SPIKE-032's findings against each AC).

### 5. Detection probe was never tested

`docker sandbox run <name> --version` was assumed to behave like a version check. It actually starts a full sandbox session and hangs. This was specified in SPEC-068 without validation, and implemented verbatim.

## Reflection

### What went well

- SPIKE-031 and SPIKE-032 research quality was high — thorough, well-sourced, correct verdicts
- SPEC-071 correctly linked both spikes and incorporated findings into implementation
- The `env -i` credential scoping and multi-runtime detection architecture are sound
- The operator caught the bug immediately during testing

### What was surprising

- `docker sandbox run <name> --version` hangs forever — the Docker Sandboxes CLI has no lightweight "is this runtime available?" query besides parsing help text
- A single invalidated acceptance criterion (SPEC-067 AC-8) cascaded into three downstream artifacts being wrong

### What would change

1. **Spike completion should trigger reverse-impact scan.** When a spike completes, scan all artifacts that share the same parent-vision or linked-artifacts for assumptions that contradict the findings.
2. **Alignment checking should run on spike completion, not just artifact creation.** The `STALE_ALIGNMENT` and `IMPLICIT_CONFLICT` finding types already describe this failure mode — they just aren't triggered at the right time.
3. **"Autonomous until done" should still gate on verification.** The superpowers chain requires `verification-before-completion` before any success claim. This was skipped during the rapid execution.
4. **Detection probes should be tested before the spec is marked Complete.** SPEC-068 specified `docker sandbox run <name> --version` without testing whether it actually works as a probe.

### Patterns observed

- **Velocity vs. integrity tradeoff**: Autonomous execution produced 8 artifacts in one session but missed a semantic conflict that a slower, deliberate process would have caught.
- **Forward-linking is natural, back-propagation is not**: The agent naturally linked new artifacts to their dependencies but never went back to update old artifacts with new findings.
- **Structural validation ≠ semantic validation**: xref and alignment checks work on graph edges and frontmatter — they don't read content for contradictions.

## Proposed process changes

### 1. Spike completion hook (new)

When swain-design transitions a SPIKE to Complete, it should:
- Read the spike's verdict and key findings
- Query `chart.sh` for all artifacts sharing the same `parent-vision` or `parent-initiative`
- For each, check if any acceptance criteria or assumptions are contradicted by the findings
- Surface contradictions as `IMPLICIT_CONFLICT` findings before proceeding

### 2. Extend alignment checking to spike-triggered events

Add a new trigger in alignment-checking.md:

| Trigger | What to check |
|---------|---------------|
| Artifact creation (existing) | Parent-child alignment, sibling conflicts |
| **Spike completion (new)** | All artifacts in the same vision/initiative scope — do any assumptions contradict the spike's verdict? |
| **Runbook creation (new)** | All referenced specs — are the documented behaviors still valid given completed spikes? |

### 3. Require `verification-before-completion` even in autonomous mode

The AGENTS.md chaining table says "Claiming work is complete → verification-before-completion." This was skipped. The chain should be mandatory regardless of execution speed.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_spike_back_propagation.md | feedback | Spike completion must trigger reverse-impact scan on sibling artifacts |
| feedback_autonomous_verification.md | feedback | Autonomous execution must still invoke verification-before-completion |

