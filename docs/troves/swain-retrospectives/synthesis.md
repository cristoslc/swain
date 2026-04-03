# Trove: swain-retrospectives

## Overview

This trove collects retrospective artifacts from the Swain project. Retrospectives serve as both reflection exercises and discovery mechanisms — surfacing patterns that inform what to build next, not just what went wrong.

This synthesis is built from 29 retros spanning 2026-03-19 to 2026-04-01, covering everything from the v0.1–v0.13 project launch through single-session spec implementations. It supersedes all prior syntheses of this trove.

---

## Pattern Frequency Map

Patterns are scored by how many retros surface them as a primary finding, not just a passing mention.

| Pattern | Retros | Severity | Fixability |
|---------|--------|----------|------------|
| Tested but not wired | 8 | High | Medium |
| Forward-link natural, back-propagation not | 6 | High | Medium |
| Handoff boundary failures | 6 | High | Hard |
| First-pass fix is too broad/narrow | 5 | Medium | Medium |
| Warn-only is a trap | 4 | Medium | Easy |
| Operator catches what agent misses | 4 | Medium | Hard |
| Changelog bucket by file type | 3 | Low | Easy |
| Worktree isolation misused | 3 | High | Medium |
| Scripting footguns (awk -v, find, git add -A) | 3 | Medium | Easy |
| Duplicate specs accumulate silently | 2 | Low | Easy |

---

## Meta-Pattern: "Tested But Not Wired"

This is the highest-frequency pattern in the corpus. It takes multiple forms, but all share the same root: acceptance criteria describe unit or script behavior, not integration behavior.

**The escalation chain — each step adds a new variant:**

1. **SPEC-067 AC-8 invalidated** (SPIKE-032 retro): Spike findings back-propagated to SPEC-067 but AC-8 was already written and never updated. No systematic backward-impact scan existed.

2. **SPEC-199/200 dead code in release** (2026-03-31 retro): Scripts implemented with passing tests but never invoked by the release pipeline. Acceptance criteria described what each script *did* internally, not what the release *called*. Aborted the release.

3. **SPEC-206 missing symlinks** (2026-03-31 retro): SPEC-194 shipped agent scripts but not the `.agents/bin/` symlinks. Unit tests validated the scripts existed. Integration test validated the feature was broken. Test path ≠ deployment path.

4. **SPEC-143 roadmap slices** (2026-03-22 retro): Manual walkthrough in Typora caught what unit tests missed. Spec included generated artifact mockups, but the spec didn't describe the runtime behavior that the manual test verified.

5. **SPEC-172 bootstrap consolidation** (2026-03-27 retro): 14 tests, 100% pass rate, jq fallback silently produced empty output. The agent had enumerated 6 untested dimensions but declared GREEN before running through them. "What did you miss?" from the operator was required to surface them.

6. **v0.10.0 changelog overstated** (2026-03-21 retro): Changelog bucketed by file type ("new file = feature") rather than user-visible impact. Development process changes appeared as features.

7. **v0.28.0 changelog failure** (2026-04-01 teardown-rewrite-release retro): "Supporting" category was defined as mutually exclusive with Features and Roadmap, but the release skill's bucket logic didn't enforce this. The anti-pattern rules fixing this came from the same retro.

**Root cause:** ACs are written against the unit under test, not against the call site. A spec for a script describes what the script does; it doesn't describe what invokes the script or where in the pipeline that invocation happens. This is a decomposition failure, not a testing failure. The fix isn't "more tests" — it's "the spec must describe the integration, not just the component."

**SPEC candidates from this pattern:** Test-the-integration-before-declaring-green gate; ACs must name the call site.

---

## Pattern: Forward-Link Natural, Back-Propagation Not

Confirmed across 6 retros with increasing specificity.

**Confirmed instances:**

- SPIKE-032 findings invalidated SPEC-067 AC-8; SPEC-067 was never updated.
- DESIGN-005 superseded DESIGN-002 without detection; same-type overlap check was missing.
- EPIC-031 audit: 7 of 9 specs were already done by the time the EPIC entered Active. The 3-day delta between audit and execution rendered the audit partially obsolete.
- Overnight artifact sweep: 9 specs were retroactively closed after an autonomous scan found them completed.
- `evidence-pool` → `trove` rename: directory and file renames happened but 160 artifact frontmatter entries and the contract definition were never updated. The gap was only found because the operator asked "doesn't that violate an ADR?"
- EPIC-038 roadmap sprint: exploratory specs were superseded by later architectural decisions without the original specs being annotated.

**What escalations caught it:** Pre-implementation detection (swain-do) works when invoked. The gap is that invocation is not yet mandatory — it runs as an advisory, not a gate.

**The asymmetry is structural:** Creating a new artifact links forward naturally (the new artifact references its dependencies). Updating an existing artifact when downstream context changes requires a backward scan that's not automatic. The artifact graph has edges in both directions, but the *process* only follows them forward.

---

## Pattern: Handoff Boundary Failures

Session lifecycle transitions — between session, worktree, artifact commit, and skill invocation — are the highest-risk surfaces. Six retros surface this, each at a different transition point.

**The transition map:**

```
session_start → spec_create → enter_worktree → implement → commit → merge → session_end
     ↑                ↑              ↑              ↑         ↑        ↑
     |                |              |              |         |        |
   bookmark        artifact       branch       staged    on worktree  retro
   overwrite       on trunk        base        files     not visible  no session
                  not in worktree mismatch    need flush  at trunk    context
```

**SPEC-219 (2026-03-31):** Artifact created on trunk before worktree entry. Worktree branch cut before the artifact was committed. Artifact invisible inside the worktree. Fix: pre-commit untracked files before cutting the worktree branch.

**SPEC-175 (2026-03-27):** Worktree branched from a stale release tag, not trunk HEAD. Merge required `git reset --hard trunk`. The `EnterWorktree` tool creates branches from HEAD, which was a release tag.

**SPEC-214 (2026-03-31):** SPEC artifact created on trunk before the worktree was entered. Stale untracked directory on trunk after worktree removal.

**Session bookmark handoff (2026-04-01):** Trunk bookmark overwritten before the worktree was created. The launcher template was bypassing the canonical entry point. Session state lost between worktrees.

**swain-retro teardown (2026-04-01):** Retro invoked after session close. No active session context available. Orphan worktrees accumulate because the bookmark lifecycle isn't tightly coupled to the worktree lifecycle.

**Pattern:** The committed/uncommitted boundary is leaky at every transition. Two separate specs (SPEC-193, SPEC-219) were needed to address it at different points. The root is a single assumption: "the working tree and the latest commit are equivalent." This assumption holds in single-session linear workflows and breaks in multi-step agentic sessions.

---

## Pattern: First-Pass Fixes Are Too Broad or Too Narrow

A recurring pattern where the initial implementation of a fix addresses the symptom but misdiagnoses the scope. Second-pass audits catch the over/undercorrection.

**SPEC-219:** First implementation used `git add -A`, staging all dirty files including modified tracked files. Only untracked files were the actual problem — tracked files are already in git history and appear in worktrees regardless. The spec's own Implementation Approach described `git add -A` behavior but framed it as correct. Audit caught it.

**SPEC-214 / SPEC-222:** Initial approach was warn-only detection. The operator pointed out that reporting without repairing just changes the error message. Auto-repair pattern emerged from this feedback. SPEC-222 then applied it systematically to 5 more checks.

**Changelog generation:** Initial implementation bucketed by file type. Anti-pattern rules (mutually exclusive categories, "Supporting" definition) were added reactively after v0.28.0 showed the same failure as v0.10.0.

**Trove routing:** Agent searched by literal keyword ("cog") instead of semantic topic. Phase 2 semantic matching was added after the misroute produced three wasted commits.

**Root cause:** The agent optimizes for getting GREEN quickly. Over-broad solutions pass tests faster than precise ones. "Too much" is rewarded over "too little" when tests are written against the proposed solution rather than the original problem.

---

## Pattern: Warn-Only Is a Trap

Doctor checks and preflight checks that detect but don't repair create repeated manual toil. The pattern: a check is written as warn-only by default, sits that way until a consumer project fails silently, then gets fixed.

**SPEC-214 retro:** Checks 15 and 19 detected missing operator symlinks but never repaired them. The fix was to make them scan-and-repair following Check 20's already-working pattern.

**ADR-019 retro:** SPEC-137 preflight was written as detect-and-report. Operator feedback: "reporting without repairing just changes the error message." Preflight self-healing convention established.

**SPEC-222 retro:** 5 more warn-only checks audited and promoted using a repair-safety rubric (idempotent, non-destructive, no network, reversible, no masking). The rubric gave clear criteria — ruling candidates in/out was fast.

**The asymmetry is invisible until it fails:** Warn-only checks adjacent to working auto-repair checks look fine in isolation. The failure only shows up in consumer projects or after significant time passes.

---

## Pattern: Operator Catches What Agent Misses

The "what did you miss?" question from the operator has surfaced real gaps in at least 4 retros. The agent reliably knows what it missed when asked directly — the knowledge is present, the self-critique before claiming completion is not.

**SPEC-141 priority weight retro:** Operator prompted self-critique; agent enumerated gaps it had not surfaced proactively.

**SPEC-175 bootstrap retro:** 14 tests passed before the operator asked "what did you miss?" — 6 untested dimensions surfaced immediately.

**SPEC-222 doctor retro:** The agent had to be prompted to self-critique the awk `-v` multi-line bug before it was caught.

**Trove research retro:** Agent was about to use `evidence-pool` field without questioning it. Operator's "doesn't that violate an ADR?" was the forcing function.

**The gap is structural, not knowledge:** The agent has the information to enumerate its own gaps. The failure is in the completion-checking behavior — declaring GREEN before running through "what did I miss?" This is the highest-leverage operator intervention identified in the corpus.

---

## Novel Risks (single-source, not yet resolved)

These appeared in exactly one retro each but are significant enough to track:

**Agentic addiction** (project retro v0.1–v0.13): The tight feedback loop creates compulsion similar to gaming addiction. The operator has actively moderated with only partial success. No operational solution identified.

**Worktree isolation misused for multi-branch ops** (release skill deletion incident): A dispatched agent ran `git reset --hard` from inside a worktree, deleting all 100+ skill files. The worktree was the wrong isolation model for an operation that needed multi-branch access. The operator was redirected to trunk twice to fix it manually. Worktree-per-task is correct for file-mutating work; release and merge operations need different isolation.

**Distribution gap invisible from inside** (ADR-019 retro): Agent-facing scripts existed only in swain's source repo. No mechanism existed to get them to consumer projects. The bug was only visible from a consumer perspective. Swain's own test suite couldn't catch it.

**Duplicate specs accumulate silently** (ADR-019 retro): SPEC-135/147 and SPEC-137/170 were duplicate pairs, both describing already-completed work. The spec graph had accumulated debt that wasn't visible until the work was traced end-to-end.

---

## What's Already Fixed

These patterns have mitigations in place, so they should be deprioritized:

- Changelog bucket-by-file-type → anti-pattern rules in release skill
- Forward-propagation via pre-implementation detection → swain-do pre-implementation check (works when invoked)
- warn-only doctor checks → SPEC-222 auto-repair promotion with rubric
- Trove misrouting → Phase 2 semantic topic matching added to prior art check
- Agent-facing script distribution → ADR-019 two-tier model with `.agents/bin/`
- Bootstrap noisy tool calls → SPEC-175 consolidated to single invocation

---

## Open Gaps (Specific, Not Generic)

These gaps have enough specificity to act on:

1. **ACs must name the call site.** Integration behavior — what invokes the component and where — must be part of the spec, not implied. Not yet a formal rule.

2. **Backward-impact scan for spike → spec chain.** SPIKE-032 invalidated SPEC-067 AC-8 with no detection. A post-spike check that scans dependent specs for stale ACs doesn't exist. Pre-implementation detection covers spec-before-execution but not spike-after-spec.

3. **Committed/uncommitted boundary ADR.** SPEC-193 and SPEC-219 both stem from the same assumption failure. A unifying artifact documenting expected behavior at each transition point would prevent future bugs in this class.

4. **swain-retro needs session context before teardown.** The retro skill chain is blocked when invoked after session close. Session state (bookmarks, focus lane) is needed for bookmark handoff. Possible fix: capture session state at session start, make it available at session end.

5. **Spec self-critique before declaring GREEN.** "What did you miss?" should be a mandatory step before claiming tests pass, not an operator-initiated question. SPEC-176 was filed for this.

6. **Consumer-perspective test fixture.** SPEC-206 and ADR-019 both showed that failures only visible from consumer projects aren't caught by swain's own test suite. A test fixture or Docker-based integration test would close this gap.

7. **Scripting conventions for multi-line content.** awk `-v` multi-line limitation has silently misbehaved twice (governance repair in SPEC-222, SPEC-206 collision keeper). Temp file + getline pattern needs to be documented somewhere accessible.

8. **Preflight self-healing as convention.** SPEC-137 was detect-only. SPEC-214 and SPEC-222 established the pattern. An ADR or governance rule making self-healing the default and warn-only the exception would prevent future warn-only accumulation.

---

## References

All 29 retros in `docs/swain-retro/`.
