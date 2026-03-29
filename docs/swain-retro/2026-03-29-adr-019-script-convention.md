---
title: "Retro: ADR-019 Script Convention — Bug to Release in One Session"
artifact: RETRO-2026-03-29-adr-019-script-convention
track: standing
status: Active
created: 2026-03-29
last-updated: 2026-03-29
scope: "ADR-019 two-tier script convention design, implementation, and release"
period: "2026-03-28 — 2026-03-29"
linked-artifacts:
  - ADR-019
  - EPIC-029
  - EPIC-047
  - SPEC-136
  - SPEC-137
  - SPEC-147
  - SPEC-170
  - SPEC-186
  - SPEC-187
  - SPEC-188
  - SPEC-189
  - SPEC-190
---

# Retro: ADR-019 Script Convention — Bug to Release in One Session

## Summary

A bug report from swain-doctor in the Homelab project ("scripts/swain-trunk.sh missing or not executable") led to discovering a distribution gap: agent-facing scripts existed only in swain's source repo with no mechanism to reach consumer projects. Over one session, this escalated from diagnosis → ADR extension → spec alignment → EPIC creation → full implementation → skill-wide migration → release (v0.22.0-alpha).

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| ADR-019 | Project-Root Script Convention | Extended with two-tier model (operator bin/ vs agent .agents/bin/) |
| SPEC-136 | Parameterize Runtime Skills | Updated path to .agents/bin/, implemented |
| SPEC-137 | Doctor Trunk Migration Check | Updated path, preflight code fixed |
| SPEC-147 | swain-trunk Auto-Detection Helper | Script moved to skill tree |
| SPEC-170 | Doctor Trunk Migration Check (dup) | Updated path |
| EPIC-047 | ADR-019 Script Convention Implementation | Created and completed |
| SPEC-186 | Doctor .agents/bin/ auto-repair | Implemented — preflight self-heals |
| SPEC-187 | Init .agents/bin/ bootstrap | Implemented — swain-init creates on onboarding |
| SPEC-188 | Doctor bin/ auto-repair | Implemented — preflight handles operator-facing |
| SPEC-189 | Migrate swain-box to bin/ | Implemented — root symlink migrated |
| SPEC-190 | Migrate all skills to .agents/bin/ | Implemented — ~55 find patterns replaced across 10 skills |

## Reflection

### What went well

**Bug-driven architecture.** The session started with a concrete consumer-project bug and let that drive the design. The operator asked the right scoping questions ("should this go in project root?" → "no, .agents/bin/") that shaped ADR-019 into a better convention than the original root-symlink approach.

**Incremental validation.** Each spec was tested immediately after implementation — preflight run with missing symlinks, second run to verify clean pass. No spec was closed without evidence.

**Parallel agent dispatch.** SPEC-190's 55 replacements across 10 skills were parallelized into 6 agents, completing in ~2 minutes wall time. The mechanical nature of the task made it ideal for dispatch.

**Spec-then-implement rhythm.** Every code change had a spec written first (or an existing spec updated). Even when the operator said "just update the existing specs in-place," the specs were revised before code was touched.

### What was surprising

**The distribution gap was invisible from inside swain.** The script existed, the tests passed, the specs referenced it — but no consumer project could ever find it. The bug was only visible from a consumer's perspective (Homelab). Swain's own test suite couldn't catch this because the script was at `$REPO_ROOT/scripts/` in the swain repo.

**SPEC-135/147 were duplicates** and both described already-completed work. The spec graph had accumulated debt that wasn't visible until the work was traced end-to-end.

**47 agent-facing scripts.** The discovery scan found far more scripts than expected — the skill tree has grown substantially. This validates the convention: manual symlink management would not scale.

### What would change

**The preflight should have been self-healing from the start.** SPEC-137 was written as a "detect and report" check. The operator had to point out that reporting without repairing just changes the error message. Detection-only preflight checks are a pattern to avoid — if the preflight can fix it, it should.

**ADR-019 should have included the agent-facing tier from the beginning.** The original ADR only covered operator-facing scripts with root symlinks. The two-tier model was added reactively. A "who calls this?" analysis during ADR drafting would have surfaced the agent-facing need.

### Patterns observed

**Bug → ADR → EPIC → Release pipeline.** This session demonstrated the full swain lifecycle in a single sitting: a consumer bug surfaced a design gap, the gap was codified as an ADR extension, the ADR drove spec creation, specs were implemented and verified, and the whole thing shipped. The artifact graph was the skeleton that kept it coherent.

**Worktree churn.** Four worktrees were created and destroyed in one session. The session state (bookmarks, focus lane) was lost each time. Worktree-per-task is correct for isolation, but the session state restoration could be smoother.

**Duplicate specs accumulate silently.** SPEC-135/147 and SPEC-137/170 were pairs of duplicates. The spec graph needs a dedup check — possibly a doctor advisory when two specs share the same title and parent epic.

## SPEC candidates

1. **Preflight self-healing convention** — Establish that preflight checks should auto-repair when possible, not just detect and report. Detection-only checks should be the exception (e.g., when repair requires operator judgment). This is a behavioral norm, possibly an ADR.
2. **Duplicate spec detection** — swain-doctor advisory when two Active specs share the same title or very similar titles under the same parent epic. SPEC-135/147 and SPEC-137/170 went unnoticed.
3. **Consumer-perspective testing** — A mechanism to test swain's preflight and doctor behavior from a consumer project's perspective (no `scripts/` directory, no swain source artifacts). Could be a test fixture or a Docker-based integration test.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Preflight self-healing convention | SPEC candidate | Preflight checks should repair, not just report |
| Duplicate spec detection | SPEC candidate | Doctor should flag duplicate-titled Active specs |
| Consumer-perspective testing | SPEC candidate | Test swain behavior from consumer project context |
