# Trove: swain-retrospectives

## Overview

This trove collects retrospective artifacts from the Swain project. Retrospectives surface patterns that shape what to build next, not just what went wrong.

This synthesis covers 29 retros from 2026-03-19 to 2026-04-01. It replaces all prior syntheses of this trove.

---

## Pattern Frequency Map

Patterns are scored by how many retros cite them as a primary finding.

| Pattern | Retros | Severity | Fixability |
|---------|--------|----------|------------|
| Tested but not wired | 8 | High | Medium |
| Forward-link natural, back-propagation not | 6 | High | Medium |
| Handoff boundary failures | 6 | High | Hard |
| First-pass fix is too broad or too narrow | 5 | Medium | Medium |
| Warn-only is a trap | 4 | Medium | Easy |
| Operator catches what agent misses | 4 | Medium | Hard |
| Changelog bucket by file type | 3 | Low | Easy |
| Worktree isolation misused | 3 | High | Medium |
| Scripting footguns (awk -v, find, git add -A) | 3 | Medium | Easy |
| Duplicate specs accumulate silently | 2 | Low | Easy |

---

## Meta-Pattern: Tested But Not Wired

This is the most common pattern in the corpus. It has many forms, but all share one root cause: acceptance criteria describe unit or script behavior, not integration behavior.

**The escalation chain:**

**1. SPEC-067 AC-8 invalidated** (SPIKE-032 retro): Spike findings back-propagated to SPEC-067. AC-8 was already written and never updated. No backward-impact scan existed.

**2. SPEC-199/200 dead code in release** (2026-03-31 retro): Scripts had passing tests. They were never called by the release pipeline. Acceptance criteria described what each script did internally. They did not describe what the release called. The release was aborted.

**3. SPEC-206 missing symlinks** (2026-03-31 retro): SPEC-194 shipped agent scripts. It did not ship the `.agents/bin/` symlinks. Unit tests validated the scripts existed. Integration test validated the feature was broken. Test path and deployment path were different.

**4. SPEC-143 roadmap slices** (2026-03-22 retro): Manual walkthrough caught what unit tests missed. The spec included generated artifact mockups. It did not describe the runtime behavior that the manual test verified.

**5. SPEC-172 bootstrap consolidation** (2026-03-27 retro): 14 tests, 100% pass rate. jq fallback silently produced empty output. The agent had listed 6 untested dimensions. It declared GREEN before running through them. The operator's "what did you miss?" was required to surface them.

**6. v0.10.0 changelog overstated** (2026-03-21 retro): Changelog bucketed by file type. "New file" was treated as "feature." Development process changes appeared as features.

**7. v0.28.0 changelog failure** (2026-04-01 retro): "Supporting" was defined as mutually exclusive with Features and Roadmap. The release skill's bucket logic did not enforce this. The anti-pattern rules that fixed it came from this retro.

**Root cause:** Acceptance criteria are written against the unit under test, not the call site. A spec for a script describes what the script does. It does not describe what invokes the script or where. This is a decomposition failure. It is not a testing failure. The fix is not "more tests." The fix is that specs must describe the integration, not just the component.

---

## Pattern: Forward-Link Natural, Back-Propagation Not

Confirmed across 6 retros with increasing clarity.

**Confirmed instances:**

- SPIKE-032 findings invalidated SPEC-067 AC-8. SPEC-067 was never updated.
- DESIGN-005 superseded DESIGN-002 without detection. Same-type overlap check was missing.
- EPIC-031 audit: 7 of 9 specs were already done when the EPIC entered Active. The 3-day delta between audit and execution made the audit partially obsolete.
- Overnight artifact sweep: 9 specs were retroactively closed after an autonomous scan found them completed.
- `evidence-pool` renamed to `trove`. Directory and file renames happened but 160 artifact frontmatter entries and the contract definition were never updated. The operator asking "doesn't that violate an ADR?" was the only thing that caught it.
- EPIC-038 roadmap sprint: exploratory specs were superseded by later architectural decisions without being annotated.

**What caught it:** Pre-implementation detection in swain-do works when invoked. The gap is that invocation is advisory, not mandatory.

**Why it happens:** Creating a new artifact links forward naturally. Updating an existing artifact when downstream context changes requires a backward scan that is not automatic. The artifact graph has edges in both directions, but the process only follows them forward.

---

## Pattern: Handoff Boundary Failures

Session lifecycle transitions are the highest-risk surfaces. Six retros surface this, each at a different transition point.

**The transition map:**

```
session_start → spec_create → enter_worktree → implement → commit → merge → session_end
     ↑                ↑              ↑              ↑         ↑        ↑
   bookmark        artifact       branch       staged    on worktree  retro
   overwrite     on trunk not     base        files     not visible  no session
                 in worktree    mismatch   need flush   at trunk    context
```

**SPEC-219 (2026-03-31):** Artifact created on trunk before worktree entry. Worktree branch cut before the artifact was committed. Artifact invisible inside the worktree. Fix: commit untracked files before cutting the worktree branch.

**SPEC-175 (2026-03-27):** Worktree branched from a stale release tag, not trunk HEAD. Merge required `git reset --hard trunk`. The `EnterWorktree` tool creates branches from HEAD, which was a release tag.

**SPEC-214 (2026-03-31):** SPEC artifact created on trunk before the worktree was entered. Stale untracked directory on trunk after worktree removal.

**Session bookmark handoff (2026-04-01):** Trunk bookmark overwritten before the worktree was created. The launcher template bypassed the canonical entry point. Session state lost between worktrees.

**swain-retro teardown (2026-04-01):** Retro invoked after session close. No active session context available. Orphan worktrees accumulate because the bookmark lifecycle is not tightly coupled to the worktree lifecycle.

**Pattern:** The committed or uncommitted boundary leaks at every transition. Two separate specs (SPEC-193, SPEC-219) were needed to address it at different points. The root is a single assumption: "the working tree and the latest commit are equivalent." This holds in single-session linear workflows and breaks in multi-step agentic sessions.

---

## Pattern: First-Pass Fixes Are Too Broad or Too Narrow

The initial implementation of a fix often addresses the symptom but misdiagnoses the scope. Second-pass audits catch the over or undercorrection.

**SPEC-219:** First implementation used `git add -A`, staging all dirty files including modified tracked files. Only untracked files were the actual problem. Tracked files are already in git history and appear in worktrees regardless. The spec described `git add -A` behavior as correct. Audit caught it.

**SPEC-214 / SPEC-222:** Initial approach was warn-only detection. Operator feedback: "reporting without repairing just changes the error message." Auto-repair pattern emerged from this feedback. SPEC-222 then applied it to 5 more checks.

**Changelog generation:** Initial implementation bucketed by file type. Anti-pattern rules (mutually exclusive categories, "Supporting" definition) were added reactively after v0.28.0 showed the same failure as v0.10.0.

**Trove routing:** Agent searched by literal keyword ("cog") instead of semantic topic. Phase 2 semantic matching added after the misroute produced three wasted commits.

**Root cause:** The agent optimizes for getting GREEN quickly. Over-broad solutions pass tests faster than precise ones. "Too much" is rewarded over "too little." Tests are written against the proposed solution rather than the original problem.

---

## Pattern: Warn-Only Is a Trap

Doctor checks and preflight checks that detect but do not repair create repeated manual toil. The pattern: a check is written as warn-only by default, sits that way until a consumer project fails silently, then gets fixed.

**SPEC-214 retro:** Checks 15 and 19 detected missing operator symlinks but never repaired them. Fixed by making them scan-and-repair, following Check 20's already-working pattern.

**ADR-019 retro:** SPEC-137 preflight was written as detect-and-report. Operator: "reporting without repairing just changes the error message." Preflight self-healing convention established.

**SPEC-222 retro:** 5 more warn-only checks audited and promoted using a repair-safety rubric: idempotent, non-destructive, no network, reversible, no masking. The rubric gave clear criteria. Ruling candidates in or out was fast.

**Why it stays invisible:** Warn-only checks next to working auto-repair checks look fine in isolation. The failure only shows up in consumer projects or after significant time passes.

---

## Pattern: Operator Catches What Agent Misses

The "what did you miss?" question from the operator has surfaced real gaps in at least 4 retros. The agent reliably knows what it missed when asked directly. The knowledge is present. The self-critique before claiming completion is not.

**SPEC-141 priority weight retro:** Operator prompted self-critique. Agent listed gaps it had not surfaced proactively.

**SPEC-175 bootstrap retro:** 14 tests passed before the operator asked "what did you miss?" 6 untested dimensions surfaced immediately.

**SPEC-222 doctor retro:** Agent had to be prompted to self-critique the awk `-v` multi-line bug before it was caught.

**Trove research retro:** Agent was about to use `evidence-pool` field without questioning it. Operator's "doesn't that violate an ADR?" was the forcing function.

**The gap is structural, not knowledge:** The agent has the information to enumerate its own gaps. The failure is in completion-checking behavior. The agent declares GREEN before running through "what did I miss?" This is the highest-leverage operator intervention in the corpus.

---

## Novel Risks

These appeared in exactly one retro each but are significant enough to track:

**Agentic addiction** (project retro v0.1–v0.13): The tight feedback loop creates compulsion similar to gaming addiction. The operator has actively moderated with only partial success. No operational solution identified.

**Worktree isolation misused for multi-branch ops** (release skill deletion incident): A dispatched agent ran `git reset --hard` from inside a worktree, deleting all 100+ skill files. The worktree was the wrong isolation model for an operation that needed multi-branch access. The operator was redirected to trunk twice to fix it manually. Worktree-per-task is correct for file-mutating work. Release and merge operations need different isolation.

**Distribution gap invisible from inside** (ADR-019 retro): Agent-facing scripts existed only in swain's source repo. No mechanism existed to get them to consumer projects. The bug was only visible from a consumer perspective. Swain's own test suite could not catch it.

**Duplicate specs accumulate silently** (ADR-019 retro): SPEC-135/147 and SPEC-137/170 were duplicate pairs, both describing already-completed work. The spec graph had accumulated debt that was not visible until the work was traced end-to-end.

---

## What's Already Fixed

These patterns have mitigations in place. Deprioritize them:

- Changelog bucket-by-file-type → anti-pattern rules in release skill
- Forward-propagation via pre-implementation detection → swain-do pre-implementation check (works when invoked)
- warn-only doctor checks → SPEC-222 auto-repair promotion with rubric
- Trove misrouting → Phase 2 semantic topic matching added to prior art check
- Agent-facing script distribution → ADR-019 two-tier model with `.agents/bin/`
- Bootstrap noisy tool calls → SPEC-175 consolidated to single invocation

---

## Open Gaps

These gaps have enough specificity to act on:

1. **ACs must name the call site.** Integration behavior — what invokes the component and where — must be part of the spec, not implied. Not yet a formal rule.

2. **Backward-impact scan for spike to spec chain.** SPIKE-032 invalidated SPEC-067 AC-8 with no detection. A post-spike check that scans dependent specs for stale ACs does not exist. Pre-implementation detection covers spec-before-execution but not spike-after-spec.

3. **Committed or uncommitted boundary ADR.** SPEC-193 and SPEC-219 both stem from the same assumption failure. A unifying artifact documenting expected behavior at each transition point would prevent future bugs in this class.

4. **swain-retro needs session context before teardown.** The retro skill chain is blocked when invoked after session close. Session state (bookmarks, focus lane) is needed for bookmark handoff. Possible fix: capture session state at session start, make it available at session end.

5. **Spec self-critique before declaring GREEN.** "What did you miss?" should be a mandatory step before claiming tests pass, not an operator-initiated question. SPEC-176 was filed for this.

6. **Consumer-perspective test fixture.** SPEC-206 and ADR-019 both showed that failures only visible from consumer projects are not caught by swain's own test suite. A test fixture or Docker-based integration test would close this gap.

7. **Scripting conventions for multi-line content.** awk `-v` multi-line limitation has silently misbehaved twice. Temp file and getline pattern needs to be documented somewhere accessible.

8. **Preflight self-healing as convention.** SPEC-137 was detect-only. SPEC-214 and SPEC-222 established the pattern. An ADR or governance rule making self-healing the default and warn-only the exception would prevent future warn-only accumulation.

---

## References

All 29 retros are in `docs/swain-retro/`.
