---
title: "Multi-Agent Collision Vectors"
artifact: SPIKE-022
track: container
status: Active
author: cristos
created: 2026-03-14
last-updated: 2026-03-20
question: "What are the collision vectors when multiple agents operate in the same swain project, and what mitigation strategies are appropriate for a solo-operator context?"
gate: Pre-development
risks-addressed:
  - Two agents editing the same file simultaneously, producing corrupted or conflicting state
  - Race conditions on .tickets/ during concurrent claim/close operations
  - Conflicting git commits from agents operating in the same branch
  - Artifact index files (list-*.md) diverging under concurrent updates
  - session.json corruption from concurrent writes
linked-artifacts:
  - EPIC-020
  - EPIC-015
  - EPIC-038
  - SPEC-113
trove: "multi-agent-collision-vectors@3568768"
---

# Multi-Agent Collision Vectors

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

What are the collision vectors when multiple agents operate in the same swain project, and what mitigation strategies are appropriate for a solo-operator context?

## Go / No-Go Criteria

**GO (build mitigations):**
- Real collision vectors exist that can cause data loss or corrupted state
- Mitigations are implementable without adding heavyweight dependencies (no distributed locks, no databases)
- The effort is proportional to the risk — focus on vectors that actually occur in practice

**NO-GO (defer):**
- Collision vectors are theoretical only — current usage patterns don't trigger them
- Git's own merge conflict resolution is sufficient for all practical cases
- Worktree isolation already prevents the dangerous cases

## Investigation Areas

### 1. File-level collision inventory

Map every shared mutable file in a swain project and classify by risk:
- `.tickets/*.md` — task state (claim, close, add-note)
- `docs/*/list-*.md` — artifact index files
- `.agents/session.json` — session state
- `AGENTS.md` — governance (rarely mutated, but cross-referenced)
- `skills-lock.json` — skill registry
- Source code files — during parallel implementation tasks
- Git state (`.git/`) — commits, branches, refs

For each: how likely is concurrent mutation? What happens if two agents write simultaneously?

### 2. tk (ticket) concurrency audit

Audit `tk claim`, `tk close`, `tk add-note` for atomicity:
- Does `tk claim` use atomic file operations (write-then-rename)?
- What happens if two agents `tk claim` the same ticket simultaneously?
- What happens if one agent `tk close` while another `tk add-note` on the same ticket?
- Are there TOCTOU (time-of-check-time-of-use) races?

### 3. Git concurrency under worktrees

When agents operate in separate worktrees sharing the same `.git` directory:
- Can two worktrees commit simultaneously without corruption?
- What happens when both try to push to the same remote branch?
- How do shared refs (tags, remote tracking branches) behave under concurrent access?
- Does `git worktree` provide any built-in locking?

### 3a. Integration atomicity (TOCTOU at merge time)

**Motivated by:** [EPIC-038](../../../epic/Active/(EPIC-038)-Priority-Roadmap-And-Decision-Surface/EPIC-038.md) retro — [SPEC-107](../../../spec/Active/(SPEC-107)-Sibling-Order-Ranking/SPEC-107.md) and [SPEC-108](../../../spec/Active/(SPEC-108)-Roadmap-Data-Model/SPEC-108.md) both modified `roadmap.py` in parallel worktrees. Both agents' tests passed in isolation. After sequential checkout/merge to main, [SPEC-108](../../../spec/Active/(SPEC-108)-Roadmap-Data-Model/SPEC-108.md)'s enrichment fields were missing — the second merge was textually clean but semantically broken.

**Core problem:** Git three-way merge guarantees textual conflict detection, not semantic consistency. Two agents can produce individually-correct, textually-non-overlapping changes that are semantically incompatible. No git mechanism catches this.

**Investigation threads:**
- **Serialized integration with test gates:** Can a local merge queue apply each agent's branch sequentially, running tests between each merge? (Analogous to GitHub merge queue / bors but local)
- **File-overlap analysis at dispatch time:** Read implementation plans, infer which files each task touches, serialize tasks with overlapping file sets instead of running them in parallel
- **Optimistic concurrency (CAS):** Record the base commit hash each agent started from; at integration time, reject if the target file was modified since that hash — forces re-run on the new base
- **Post-merge verification as fallback:** When prevention fails, grep for key deliverables and re-run tests in main context before claiming delivery. This is detection, not prevention — acceptable as a last line of defense but not the primary strategy
- **CI merge queue mechanisms:** Do GitHub merge queue, Mergify, or bors provide useful primitives? Could swain-dispatch integrate with them for remote agent results?

### 4. Artifact index race conditions

When two agents both update a `list-*.md` index file:
- Both read the same version, append a row, write back — last write wins, first entry lost
- Mitigation options: lock files, append-only logs, index regeneration from filesystem state
- How does specgraph handle this? Can it regenerate indexes on demand?

### 5. Mitigation strategy evaluation

For each real collision vector, evaluate:
- **Worktree isolation** — can the operation be moved to an isolated worktree?
- **File locking** (flock/lockfile) — lightweight, local-only, POSIX-standard
- **Atomic file operations** (write-tmp-then-rename) — prevents partial writes
- **Regeneration** — don't protect the file, regenerate it from source of truth (e.g., regenerate indexes from filesystem)
- **Convention** — document which files agents should not touch concurrently, enforce via swain-doctor

### 6. Architecture overview update scope

Determine what needs to be added to the architecture overview:
- Concurrency model diagram (what's isolated, what's shared, how shared state is protected)
- Agent isolation boundaries (worktree = default, shared workdir = exceptional)
- Conventions for swain-dispatch and subagent-driven-development

## Findings

### Evidence: EPIC-038 worktree TOCTOU (2026-03-20)

**Incident:** During [EPIC-038](../../../epic/Active/(EPIC-038)-Priority-Roadmap-And-Decision-Surface/EPIC-038.md) Phase 1, [SPEC-107](../../../spec/Active/(SPEC-107)-Sibling-Order-Ranking/SPEC-107.md) (sort-order) and [SPEC-108](../../../spec/Active/(SPEC-108)-Roadmap-Data-Model/SPEC-108.md) (data model) were dispatched to parallel worktree agents. Both modified `roadmap.py`. Both agents reported success with passing tests.

**Failure mode:** After sequential checkout into main, SPEC-108's enrichment fields were missing from the merged result. The agent tested its worktree copy, not the integrated result. Git merge succeeded textually — no conflict markers — but the semantic result was incomplete.

**Classification:** TOCTOU — Time of Check (agent tests in isolated worktree) vs Time of Use (changes applied to main where another agent already mutated shared files).

**Key insight:** This is not preventable by git's merge machinery. Textually clean merges can be semantically broken. The fix must be at a higher layer — either preventing overlapping dispatch or verifying after integration.

**Source:** [EPIC-038 Phase 1 Retro](../../swain-retro/2026-03-20-epic-038-phase-1.md)

### Evidence: Commit-layer TOCTOU (2026-03-20)

**Observation:** Parallel agent working on [SPEC-113](../../../spec/Active/(SPEC-113)-Sync-Latency-Reduction/SPEC-113.md) (swain-sync latency reduction) noted that `swain-sync` generates commit messages from diffs before invoking the commit shell script. If two agents commit concurrently (even in separate worktrees sharing `.git`), the diff context may shift between message generation and actual commit — producing a commit whose message describes a different changeset than what was committed. SPEC-113's goal of backgrounding sync makes this race more likely — a backgrounded sync could overlap with worktree agents committing to the same branch.

**Proposed mitigation:** A **commit queue** with structured tickets — each ticket specifies the files to stage and the message to use, submitted as a unit. A serialized consumer processes the queue, ensuring each commit is atomic (message matches staged files). This is the same serialization principle as area 3a's "local merge queue," applied at the commit layer rather than the integration layer.

**Relationship to area 3a:** These are two instances of the same pattern — a non-atomic read-decide-act sequence on shared git state. A unified serialization layer (commit queue + merge queue, or a single integration queue that handles both) may be the right abstraction.

### Area 1: File-level collision inventory

**Investigated:** Every shared mutable file type in a swain project, classified by concurrency risk.

| File / Category | Mutation frequency | Concurrent risk | Failure mode |
|---|---|---|---|
| `.tickets/*.md` | High (claim, close, add-note per task) | Medium — parallel agents on different tickets is fine; same ticket is a race | Last-write-wins on YAML frontmatter; note append is append-safe but frontmatter update is not |
| `docs/*/list-*.md` | Medium (rebuilt after artifact transitions) | Low in practice — rebuild-index.sh regenerates from filesystem state | Two simultaneous rebuilds could clobber each other, but idempotent regeneration makes this self-healing |
| `.agents/session.json` | Low-medium (written at session start/end, bookmark updates) | Low — only the main session writes this; worktree agents do not | Corruption if two processes write simultaneously, but current architecture avoids this |
| `AGENTS.md` | Very low (governance changes only) | Negligible | Not mutated by agents during execution |
| `skills-lock.json` | Very low (only during skill install/update) | Negligible — each worktree has its own copy | No practical risk |
| Source code files | High during implementation | **HIGH** — the EPIC-038 failure class | Textually clean merge hides semantic conflicts; this is the primary collision vector |
| `.git/` shared state (refs, objects) | High (every commit, push, fetch) | Medium — git's internal locking handles most cases | See Area 3 for details |

**Risk assessment:** The highest-risk category is source code files modified by parallel worktree agents. All other categories are either low-frequency, self-healing (index regeneration), or architecturally isolated (one writer).

**Key finding:** Most shared mutable files in swain are either (a) rarely mutated concurrently, (b) regenerable from a source of truth, or (c) only written by the main session. Source code under parallel implementation is the exception and the primary risk.

### Area 2: tk (ticket) concurrency audit

**Investigated:** The `tk` binary at `/Users/cristos/.local/bin/tk` (bash script, ~1470 lines). Audited `claim`, `close`, `add-note`, `status`, and `create` for atomicity.

**Findings:**

1. **`tk claim` uses `mkdir` for atomic locking.** Line 317: `if mkdir "$lockdir" 2>/dev/null; then`. This is correct — `mkdir` is atomic on POSIX filesystems. Two simultaneous `tk claim` calls on the same ticket will have exactly one succeed and the other fail with "already claimed." This is the best possible design for a shell-based lock.

2. **`_sed_i` uses write-then-rename.** Line 80-81: `sed "$@" "$file" > "$tmp" && mv "$tmp" "$file"`. The temp file uses PID-based naming (`${file}.tmp.$$`), so parallel invocations on different tickets cannot collide. However, two operations on the *same* ticket file (e.g., simultaneous `add-note` and `close`) would race on the file contents — the second `_sed_i` would read the pre-modification version.

3. **`cmd_add_note` appends directly.** Line 1314: `printf '\n**%s**\n\n%s\n' "$timestamp" "$note" >> "$file"`. Append operations (`>>`) are generally safe on local filesystems for reasonable-sized writes, but the preceding `grep -q '^## Notes'` + conditional `printf '\n## Notes\n' >>` is a classic TOCTOU: two agents adding the first note simultaneously could both see "no Notes section" and both add one.

4. **`cmd_close` has a non-atomic sequence.** Lines 284-291: `cmd_status` (updates YAML) then conditionally `rm -rf "$lockdir"`. If the process is interrupted between status update and lock removal, a stale lock remains. This is a minor issue — `tk claim` will report the ticket as claimed by a dead agent.

5. **`cmd_create` writes atomically.** Line 235: The entire frontmatter is written in a single `{ ... } > "$file"` redirect, which creates the file atomically.

**Risk assessment:** PRACTICAL for same-ticket concurrent operations (e.g., two agents both `add-note` to the same ticket). THEORETICAL for cross-ticket operations (different tickets are independent files). The `mkdir`-based claim lock is well-designed and race-free.

**Recommended mitigation:** For same-ticket operations, the risk is low in practice because swain's dispatch model assigns one agent per ticket. If multi-agent ticket access becomes a pattern, `flock` on the ticket file would be the minimal fix. The existing `mkdir` lock for `claim` is already correct.

### Area 3: Git concurrency under worktrees

**Investigated:** Git's safety guarantees when multiple worktrees share the same `.git` directory, based on [git-worktree documentation](https://git-scm.com/docs/git-worktree), [kernel.org docs](https://www.kernel.org/pub/software/scm/git/docs/git-worktree.html), and concurrent development analysis from [Ken Muse](https://www.kenmuse.com/blog/using-git-worktrees-for-concurrent-development/).

**Findings:**

1. **Per-worktree isolation is well-designed.** Each worktree gets its own HEAD, index, and per-worktree refs (refs/bisect, refs/worktree, refs/rewritten). The shared `.git/` directory stores objects and most refs. Git enforces a "one branch per worktree" rule — two worktrees cannot check out the same branch, preventing the most dangerous class of concurrent mutation.

2. **Concurrent commits from different worktrees are safe.** Each worktree has its own index file, so `git add` and `git commit` in worktree A do not interfere with worktree B, provided they are on different branches (which git enforces). Object creation (writing blobs, trees, commits to `.git/objects/`) uses atomic temp-file-then-rename, so concurrent object writes are safe.

3. **Ref updates use lock files.** Git creates `.git/refs/heads/<branch>.lock` before updating a ref. If two processes try to update the same ref simultaneously, one will fail with "cannot lock ref." This prevents corruption but means concurrent pushes to the same branch will fail — which is the correct behavior since worktrees must be on different branches. Source: [git push documentation](https://git-scm.com/docs/git-push) and [git mailing list discussion on push race conditions](https://git.vger.kernel.narkive.com/9Rkrrepp/push-race-condition).

4. **Concurrent pushes to different remote branches are safe.** Git's push protocol sends objects (lockless, safe for concurrent access to the object store) and then updates the remote ref. Two worktrees pushing different branches will not interfere.

5. **`git worktree lock` is for pruning protection, not concurrency control.** The `lock` subcommand prevents a worktree from being pruned (e.g., on a removable drive), not from concurrent access. It is not relevant to the multi-agent concurrency question.

6. **Shared reflog is a minor risk.** Operations that update shared refs (e.g., `git fetch`) write to the shared reflog. Two concurrent fetches could race on reflog entries, but git handles this with lock files. The practical risk is negligible.

**Risk assessment:** Git's internal concurrency model is well-designed for the worktree use case. The "one branch per worktree" invariant, combined with per-worktree indexes and lock-file-protected ref updates, means that concurrent commits and pushes from different worktrees are safe at the git level. The dangerous case is not git corruption but *semantic* conflicts after merge — which is Area 3a.

### Area 3a: Integration atomicity (TOCTOU at merge time) — PRIMARY INVESTIGATION

**Investigated:** Merge queue mechanisms, optimistic concurrency approaches, file-overlap analysis, and the simplest mechanism that prevents the EPIC-038 failure class. Research sources include [GitHub merge queue docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue), [bors-ng](https://bors.tech/), [Mergify merge queue](https://docs.mergify.com/merge-queue/), and [Aviator's merge queue analysis](https://www.aviator.co/blog/what-is-a-merge-queue/).

#### The problem restated

When two agents work in parallel worktrees on branches that modify overlapping files, each agent's tests pass in isolation. After sequential merge into main, git's three-way merge succeeds textually (no conflict markers) but the merged result may be semantically broken. The second merge sees the first's changes in the base but has no way to know its own changes are now incomplete relative to the new base.

This is structurally identical to the "merge skew" problem that motivated bors, homu, and GitHub's merge queue. As [bors-ng documentation](https://bors.tech/) states: "If the feature branch is out of date with the base branch, then the outcome of running the tests on the feature branch may be different to the outcome of running the tests on the base branch with the feature branch merged in."

#### Mechanism 1: Serialized integration with test gates (local merge queue)

**How it works:** After each agent completes, merge its branch into main and run the full test suite on the integrated result before proceeding to the next merge. If tests fail, the merge is rejected and the agent's work must be rebased and re-validated.

**Feasibility:** Entirely feasible locally. The merge-and-test cycle is:
```
git checkout main
git merge --no-ff agent-branch-1
pytest  # or whatever test suite
# if green, proceed to next
git merge --no-ff agent-branch-2
pytest  # if red, reject and rebase agent-branch-2
```

**Strengths:** Catches semantic conflicts that textual merge cannot. This is exactly what bors/GitHub merge queue do, just locally. It is the *only* mechanism that provides post-integration semantic verification.

**Weaknesses:** Sequential — blocks on test execution. For swain's typical workload (2-4 parallel agents, <60s test suites), this is acceptable. The latency cost is O(N * test_time) where N is the number of agents.

**Assessment:** This is the **recommended primary mitigation** for the EPIC-038 failure class. It is simple, correct, and proportional to the risk.

#### Mechanism 2: File-overlap analysis at dispatch time

**How it works:** Before dispatching parallel agents, read each spec's implementation plan (or infer from the spec's scope) which files each task will touch. If two tasks have overlapping file sets, serialize them rather than running in parallel.

**Feasibility:** Partially feasible. Implementation plans (tk tickets) sometimes describe which files to modify, but this is not reliable — agents may touch files not predicted by the plan. Static analysis of import graphs could help but adds complexity.

**Strengths:** Prevents the problem before it occurs. No post-merge verification needed for non-overlapping tasks.

**Weaknesses:** Imprecise — agents may touch unexpected files. Over-serialization reduces parallelism. Under-serialization misses collisions. Requires implementation plans to be detailed about file targets.

**Assessment:** Useful as a **heuristic pre-filter** to reduce the frequency of merge-queue rejections, but not sufficient as the sole mitigation. Cannot catch cases where agents touch files not predicted at dispatch time.

#### Mechanism 3: Optimistic concurrency / CAS (Compare-and-Swap)

**How it works:** Record the base commit hash each agent starts from. At integration time, for each file the agent modified, check whether that file was also modified on main since the agent's base commit. If so, reject the merge and require the agent to rebase onto the new main.

**Feasibility:** Simple to implement:
```
BASE=$(git merge-base main agent-branch)
MODIFIED_ON_MAIN=$(git diff --name-only $BASE main)
MODIFIED_BY_AGENT=$(git diff --name-only $BASE agent-branch)
OVERLAP=$(comm -12 <(sort <<< "$MODIFIED_ON_MAIN") <(sort <<< "$MODIFIED_BY_AGENT"))
```
If `$OVERLAP` is non-empty, reject and rebase.

**Strengths:** Lightweight, fast (no test execution needed for the check), catches the exact EPIC-038 pattern (two agents modifying the same file).

**Weaknesses:** Still textual — detects *file-level* overlap but not *semantic* overlap across files. If Agent A modifies `models.py` and Agent B modifies `views.py` that imports from `models.py`, the CAS check passes but the semantic conflict remains. However, this class of cross-file semantic conflict is much rarer than same-file conflicts.

**Assessment:** Excellent as a **fast-path check** before running the full test suite. If the CAS check detects file overlap, skip straight to rebase-and-retest. If no overlap, the merge is likely safe (though the test gate in Mechanism 1 should still run as a safety net).

#### Mechanism 4: Post-merge verification

**How it works:** After merging all agent branches, grep for key deliverables (e.g., expected function signatures, class attributes) and run the full test suite on main.

**Feasibility:** Already partially implemented as a convention (retro recommendation from EPIC-038: "verify agent deliverables after merge").

**Strengths:** Catches anything the other mechanisms miss. Defense in depth.

**Weaknesses:** Detection, not prevention — the damage (silent data loss) has already occurred by the time the check runs. Requires knowing what to check for.

**Assessment:** Necessary as a **last line of defense** but not the primary strategy.

#### Mechanism 5: CI merge queue (GitHub merge queue / Mergify / bors)

**How it works:** GitHub merge queue creates a temporary branch containing the target branch + all queued PRs ahead of the current one. Required status checks must pass on this temporary branch before the PR is merged.

**Feasibility:** Available for remote dispatch via swain-dispatch (GitHub Actions). Not applicable for local worktree agents.

**Strengths:** Battle-tested. Handles semantic conflicts by running tests on the integrated result. Bors specifically batches PRs and tests them together.

**Weaknesses:** Requires CI infrastructure. Adds latency (CI run time). Not applicable to the local multi-agent case that caused EPIC-038.

**Assessment:** Relevant for swain-dispatch (remote agents via GitHub Issues/Actions) but **not the solution for local worktree collisions**. When swain-dispatch is used, enabling GitHub merge queue on the repository provides the same guarantees as Mechanism 1 but offloaded to CI.

#### Recommended strategy (revised)

The initial analysis proposed a three-layer approach (pre-dispatch heuristic, CAS check, serialized test gate). On reflection, this is overengineered. The core insight — already proven by GitHub PRs, bors, and every merge queue — is simply: **test the merge commit, not the branch**.

**Single mechanism: serialized merge-then-test**

When agents complete, merge their results into main one at a time, testing after each merge:

```bash
# Agent A finishes
git merge --no-ff agent-A-branch
pytest  # tests run on main with A's changes integrated
# ✅ → keep. ❌ → git revert HEAD, agent must fix and retry

# Agent B finishes (main now includes A's changes)
git merge --no-ff agent-B-branch
pytest  # tests run on main with BOTH A and B integrated
# ✅ → keep. ❌ → git revert HEAD, agent must rebase onto post-A main
```

Each merge is tested on the real integrated state. Serialization ensures each agent merges against the current main, not a stale snapshot.

**How GitHub solves this (for reference):**

GitHub has two mechanisms, and only one actually works:

1. **Branch protection ("require up to date")** — forces a rebase before merge is allowed, but has NO serialization. If two PRs are both "up to date" at the same moment, both can merge concurrently, producing the same TOCTOU we hit in EPIC-038. This is a known gap.

2. **Merge queue** — PRs enter a serialized queue. GitHub creates a temporary merge group (base + all queued PRs), runs CI on that merged state, and only lands the group if green. Failing PRs are ejected and the group re-tests. This IS serialized merge-then-test — the queue is the serialization primitive.

So GitHub's merge queue is exactly this pattern, implemented as a hosted service. We implement the same thing locally: a single coordinator (the operator or main-thread agent) merges and tests one agent result at a time. No temp branches needed — merge directly into main, revert if red.

**Why serialization is the fix, not the testing:**

Testing the merge commit is necessary but not sufficient. Without serialization, two agents can both merge-then-test concurrently against the same main, both pass, and both fast-forward — reproducing the TOCTOU. The serialization ensures each test sees the cumulative state of all previously-accepted merges.

**Is serialization already implicit?** In swain's current architecture, worktree agents return results to the operator's main thread, which merges them. If the main thread merges sequentially (which it naturally does — it's a single process), serialization is automatic. The EPIC-038 failure happened because two agents were dispatched AND integrated without the main thread testing in between. The fix is: always test on main after each merge, before merging the next.

**Why the three-layer approach was overengineered:**
- Layer 1 (pre-dispatch overlap) is a premature optimization that can't catch cross-file semantic conflicts
- Layer 2 (CAS check) is a weaker version of "just run the tests"
- Layer 3 (serialized test gate) is the actual solution, and it's sufficient alone

**Relationship to commit-layer TOCTOU:** The commit-layer TOCTOU ([SPEC-113](../../../spec/Active/(SPEC-113)-Sync-Latency-Reduction/SPEC-113.md) — swain-sync generating messages before committing) is subsumed by this approach. If all agent results are integrated through serialized merge-then-test, the commit message is generated from the verified merge result, not from a potentially-stale diff.

### Area 4: Artifact index race conditions

**Investigated:** `rebuild-index.sh` and how `list-*.md` files are maintained.

**Findings:**

1. **`rebuild-index.sh` regenerates from filesystem state.** The script scans all artifact `.md` files in `docs/<type>/` directories, reads their frontmatter, and writes a complete `list-<type>.md`. It does not read the previous index — it regenerates from scratch every time.

2. **The write is atomic.** Line 82 of `rebuild-index.sh`: `mv "$tmpfile" "$index_file"` — the index is written to a temp file first, then atomically moved into place. Two concurrent rebuilds would both produce correct output (since both read the same filesystem state), and the last `mv` wins. The result is always a correct, complete index.

3. **specgraph.sh also regenerates from filesystem state.** The specgraph cache (`/tmp/agents-specgraph-*.json`) is rebuilt by scanning all `docs/*.md` files. It uses the same pattern: build in memory, write atomically.

**Risk assessment:** NEGLIGIBLE. The "regeneration from source of truth" pattern eliminates the last-write-wins problem. Even if two agents trigger simultaneous index rebuilds, both produce the same correct output. There is no data loss scenario.

**Recommended mitigation:** None needed. The current design is correct. Document this as a pattern to follow for other shared state.

### Area 5: Mitigation strategy evaluation

For each collision vector identified, the following table evaluates mitigation strategies:

| Collision vector | Worktree isolation | flock/lockfile | Atomic file ops | Regeneration | Convention/docs |
|---|---|---|---|---|---|
| **Source code (Area 3a)** | Already used; insufficient alone — isolation causes the TOCTOU | N/A (different worktrees) | N/A | N/A | Pre-dispatch overlap check + post-merge test gate |
| **tk same-ticket ops (Area 2)** | Not applicable | Would fix `add-note` TOCTOU | `_sed_i` already uses write-then-rename | N/A | Document: one agent per ticket |
| **Artifact indexes (Area 4)** | N/A | Unnecessary | Already atomic | **Already implemented** | Already documented |
| **session.json** | Main session only | Unnecessary | Simple JSON write | Could regenerate | Document: worktree agents do not write session.json |
| **skills-lock.json** | Each worktree has own copy | N/A | N/A | N/A | Already isolated |
| **Git refs (Area 3)** | Per-worktree branches | Git uses lock files internally | Git handles this | N/A | Already safe |

**Strategy ranking by effort-to-impact ratio:**

1. **Serialized test gate after merge** (Area 3a, Mechanism 1) — HIGH impact, MEDIUM effort. This is the single most important mitigation. Prevents the entire EPIC-038 failure class.
2. **CAS file-overlap check before merge** (Area 3a, Mechanism 3) — MEDIUM impact, LOW effort. Fast pre-check that catches same-file collisions without running tests.
3. **Pre-dispatch overlap heuristic** (Area 3a, Mechanism 2) — MEDIUM impact, LOW effort. Reduces collision frequency by serializing obviously-overlapping tasks.
4. **Convention documentation** — LOW impact, VERY LOW effort. Document which files are safe to touch concurrently and which are not.
5. **flock for tk same-ticket ops** — LOW impact, LOW effort. Only needed if multi-agent ticket access becomes a pattern.

### Area 6: Architecture overview update scope

**Investigated:** Existing architecture documentation and what concurrency model documentation is needed.

**Findings:**

1. **VISION-002 (Safe Autonomy) has an architecture-overview.md** at `docs/vision/Active/(VISION-002)-Safe-Autonomy/architecture-overview.md` but it focuses on sandbox isolation tiers and credential scoping, not concurrency. The worktree concurrency model is not documented anywhere.

2. **AGENTS.md references worktrees** in the superpowers skill chaining table (subagent-driven-development) and the execution strategy, but does not document the concurrency model or shared state boundaries.

3. **The execution strategy doc** (`swain-do/references/execution-strategy.md`) describes worktree-artifact mapping but not concurrency safety.

**What needs to be documented:**

- **Concurrency model diagram:** What is isolated per-worktree (working tree, index, HEAD, branch) vs. what is shared (object store, remote refs, `.tickets/`, `docs/` artifact files).
- **Agent isolation boundaries:** Each worktree agent operates on its own branch, with its own working tree. Shared mutable state is limited to `.tickets/` (claim locks protect these), artifact indexes (regenerated from filesystem), and the git object store (internally locked).
- **Integration protocol:** How agent branches are merged back to main — the three-layer strategy (pre-dispatch overlap check, post-agent CAS check, serialized test gate).
- **Conventions for swain-dispatch and subagent-driven-development:** Remote dispatch gets CI merge queue guarantees. Local dispatch needs the local merge queue protocol.

This documentation should live in an architecture-overview.md at the EPIC level for whatever epic implements the merge queue, and a summary should be added to AGENTS.md.

### Preliminary Go/No-Go Assessment

**Assessment: GO (build mitigations)**

All three Go criteria are met:

1. **Real collision vectors exist that can cause data loss or corrupted state.** YES — the EPIC-038 incident is concrete evidence of silent data loss from semantically-broken textual merges. This is not theoretical; it happened in production use.

2. **Mitigations are implementable without heavyweight dependencies.** YES — the recommended three-layer strategy uses only git commands, bash, and the existing test suite. No distributed locks, no databases, no external services. The serialized test gate is ~20 lines of shell script. The CAS check is ~5 lines. The pre-dispatch heuristic is a convention enforceable by swain-do.

3. **The effort is proportional to the risk.** YES — the primary mitigation (serialized test gate) prevents the entire EPIC-038 failure class. The secondary mitigations (CAS check, overlap heuristic) reduce collision frequency. Total implementation effort is estimated at 1-2 specs worth of work, which is proportional to the risk of silent data loss in every multi-agent implementation session.

**No-Go criteria are NOT met:**

- Collision vectors are NOT theoretical — EPIC-038 proves they occur in practice.
- Git merge conflict resolution is NOT sufficient — the EPIC-038 merge was textually clean but semantically broken.
- Worktree isolation does NOT prevent the dangerous cases — it *causes* the TOCTOU by creating the illusion of independence while sharing the integration target.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; informs EPIC-020 |
| Active | 2026-03-20 | fa63b5a | Activated by EPIC-038 retro — concrete TOCTOU evidence in area 3a |
