---
title: "Retro: TDD Self-Critique Gate and Behavioral Eval"
artifact: RETRO-2026-03-27-tdd-self-critique
track: standing
status: Active
created: 2026-03-27
last-updated: 2026-03-27
scope: "SPEC-176 implementation, ADR-017 decision, and the process of turning a retro learning into a verified skill change"
period: "2026-03-27"
linked-artifacts:
  - SPEC-175
  - SPEC-176
  - SPIKE-048
  - ADR-017
---

# Retro: TDD Self-Critique Gate and Behavioral Eval

## Summary

Turned a retro learning (from SPEC-175's session) into a verified behavioral instruction in swain-do's TDD enforcement. The session surfaced three process insights: (1) behavioral skill instructions need a different verification strategy than code, (2) the operator's correction "NEVER SAVE TO MEMORY — it MUST be in the relevant SKILL" reinforced that learnings belong in artifacts, and (3) A/B subagent evals are a cheap, effective way to verify behavioral instructions before merge.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| SPEC-176 | TDD Coverage Self-Critique Gate | Implemented — added to tdd-enforcement.md |
| ADR-017 | A/B Subagent Eval for Behavioral Skill Instructions | Active — methodology decision recorded |
| SPIKE-048 | Noisy Tool-Call Pattern Audit | Filed, not yet investigated |

## Reflection

### What went well

- **Retro-to-artifact pipeline worked end-to-end.** SPEC-175 retro identified the self-critique gap → SPEC-176 created → implemented in tdd-enforcement.md → behaviorally verified via A/B eval → ADR captured the eval methodology. The whole loop from "observation" to "verified skill change" completed in one session.
- **A/B subagent eval was decisive.** Two parallel haiku agents, same scenario, one with the instruction and one without. Control agent moved straight to next cycle. Treatment agent paused and enumerated 5 specific untested dimensions. 10 seconds, zero ambiguity. This pattern is reusable for any behavioral instruction change.
- **Operator correction improved the process.** "NEVER SAVE TO MEMORY — it MUST be in the relevant SKILL" caught the agent falling back to memory when the existing feedback memory (`feedback_behaviors_into_artifacts.md`) already said to do the opposite. The correction was sharp and immediately actionable.

### What was surprising

- **The agent violated its own memory.** The feedback memory `feedback_behaviors_into_artifacts.md` explicitly says behavioral changes go into artifacts, not memory. The agent created a memory file anyway during the SPEC-175 retro. This suggests memory files are read but not reliably cross-checked against each other during write operations.
- **Superpowers skills are read-only** — this wasn't obvious until the operator pointed out that test-driven-development SKILL.md would be overwritten on update. The fix (targeting swain-do's enforcement wrapper instead) was the right call but required a mid-session retarget of SPEC-176.
- **Artifact number collisions from concurrent work.** EPIC-045 (Shell Launcher Onboarding) landed on trunk while this session worked in a worktree. Three collisions (SPEC-172/173, SPIKE-046) required renumbering. The fix-collisions.sh script handled it cleanly, but the collision itself shows that concurrent worktree work on trunk is a known friction source.

### What would change

- **Check superpowers ownership before targeting a skill file.** The retarget from TDD SKILL.md to tdd-enforcement.md was avoidable — the agent should have known superpowers skills are external dependencies.
- **Run the behavioral eval before committing the skill change, not after.** The implementation was committed, then the operator asked "how did you test it?" — the eval should have been part of the implementation task, not a post-hoc response to operator skepticism.

### Patterns observed

- **Recurring: operator asks "what did you miss?" and the agent can answer.** This happened in both the SPEC-175 session (test coverage gaps) and this session (behavioral verification). The self-critique gate (SPEC-176) addresses the first pattern. ADR-017 addresses the second. Both are symptoms of the same root: the agent doesn't audit its own work before declaring done.
- **Learnings that become artifacts have higher fidelity than memory files.** A SPEC with ACs and a behavioral eval is more actionable than a memory file with "Why" and "How to apply" fields. The artifact forces structure; the memory allows drift.

## Learnings captured

| Artifact | Type | Summary |
|----------|------|---------|
| SPEC-176 | enhancement | Post-GREEN self-critique gate in tdd-enforcement.md |
| ADR-017 | decision | A/B subagent eval methodology for behavioral instructions |
