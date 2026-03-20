---
trove-id: multi-agent-collision-vectors
synthesized: 2026-03-20
sources: 16
---

# Multi-Agent Collision Vectors: Research Synthesis

This synthesis addresses the five questions posed by SPIKE-022, organized by theme rather than by source.

## 1. Git Worktree Safety — Are there edge cases the spike missed?

**Verdict: SPIKE-022 findings are accurate and complete for the relevant scope.**

The git-worktree documentation confirms the spike's analysis: per-worktree isolation (HEAD, index, working tree) is well-designed, concurrent commits on different branches are safe, and ref updates use lock files that fail cleanly rather than corrupt. The "one branch per worktree" invariant is the key safety property.

### Edge cases not covered by the spike

- **Submodule support is explicitly incomplete.** The git docs state: "Multiple checkout in general is still experimental, and the support for submodules is incomplete. It is NOT recommended to make multiple checkouts of a superproject." If swain projects ever use git submodules, worktree-based parallelism would be unsafe.

- **Shared configuration can cause subtle issues.** The repository `config` file is shared by default across all worktrees. If an agent modifies git configuration (e.g., setting `core.autocrlf` or hooks paths), the change affects all worktrees. This is not a data corruption risk but could cause behavioral divergence. The `extensions.worktreeConfig` option (Git 2.20+) enables per-worktree config if needed.

- **Shared hooks directory.** All worktrees share `.git/hooks/`. If an agent modifies a hook, it affects all worktrees. This is relevant if swain-sync or other tools use git hooks.

- **Port and service conflicts.** The Upsun article identifies a practical edge case: worktrees share the host's port space, Docker daemon, and database connections. Two agents running test servers will collide on default ports. This is not a git issue per se, but it is a worktree-based parallelism issue that swain should address if agents run services during testing.

### Assessment

The spike correctly identifies that the dangerous case is not git-level corruption but semantic conflicts after merge. The additional edge cases (submodules, shared config, port conflicts) are worth noting but do not change the fundamental analysis.

## 2. Merge Queue Patterns — Does the three-layer strategy align with industry practice?

**Verdict: The three-layer strategy is well-aligned with industry practice and represents the correct local adaptation of established patterns.**

### Industry alignment

The spike's three-layer strategy maps directly to established merge queue patterns:

| Spike Layer | Industry Equivalent | Source |
|---|---|---|
| Pre-dispatch file-overlap heuristic | Task decomposition with file boundaries | Augment, Superset guides |
| Post-agent CAS file-overlap check | Merge skew detection (base commit drift) | Bors staging branch, GitHub merge groups |
| Serialized test gate after merge | Test-then-merge (the "not rocket science rule") | Bors, Google TAP, all merge queue implementations |

The "not rocket science rule" — automatically maintain a repository that always passes all tests — is precisely what the serialized test gate implements locally.

### What merge queues do that the spike is not considering

1. **Batching and bisection.** Bors and Google TAP batch multiple changes and test them together, then bisect on failure. The spike's strategy tests each agent's merge individually, which is simpler but slower. For swain's scale (2-4 agents), individual testing is appropriate. At larger scale, batching would reduce the O(N * test_time) latency.

2. **Optimistic parallel testing.** GitHub merge queue and Mergify create merge groups that test multiple PRs simultaneously against their combined state. If swain's test suite is fast (<60s), this optimization is unnecessary. If tests grow longer, testing the next agent's merge optimistically (assuming the current one passes) could halve latency.

3. **Automated revert on failure.** Google TAP automatically reverts failing changes. The spike's strategy rejects the merge and requires rebase, but does not discuss automated revert of a merge that passed the CAS check but failed the test gate. Adding automatic revert capability would make the recovery path cleaner.

4. **"Post-queue is post-merge" insight.** Aviator's article describes running traditionally post-merge tests (regression, performance) within the queue before mainline integration. The spike focuses on unit/integration tests but could extend the test gate to include broader verification.

### Assessment

The three-layer strategy is the correct local implementation of the bors/merge-queue pattern. The main gap is recovery strategy: what happens when layer 3 (test gate) fails? The spike says "reject and rebase" but should specify whether the failed merge is reverted automatically or requires operator intervention.

## 3. TOCTOU Mitigation — Are there better patterns than CAS + serialized test gate?

**Verdict: CAS + serialized test gate is the correct pattern. Alternative approaches exist but are not better for swain's context.**

### CWE-367 perspective

The TOCTOU pattern (CWE-367) is well-studied in security contexts. The standard mitigations are:
1. Eliminate the check-before-use pattern (make the operation atomic)
2. Use locking mechanisms around the check-use sequence
3. Recheck after operations to confirm success
4. Limit time between check and use

The spike's three-layer strategy maps to these:
- Layer 2 (CAS check) = recheck at use time
- Layer 3 (test gate) = recheck after operation
- The combination = minimizing the window between check and use

### Alternative patterns considered

**Content-addressed storage (Bazel pattern).** Bazel avoids TOCTOU by content-addressing all artifacts: each build action's output is keyed by a hash of its inputs. If inputs change during execution, the output is invalidated. Bazel also has `--experimental_guard_against_concurrent_changes` to detect input changes during builds. This maps to the CAS check: record the base commit hash, detect if the base changed. Swain's CAS check is effectively the same pattern.

**Reducer-based state merging (LangGraph pattern).** LangGraph requires explicit "reducer" functions when parallel nodes update shared state. The reducer defines how concurrent updates merge. This is more sophisticated than git's three-way merge but requires semantic knowledge of the state being merged. For source code, no general-purpose semantic reducer exists — this is why the test gate (empirical verification) is necessary.

**Exclusive locking (tick-md pattern).** tick-md locks the shared file when an agent claims a task, preventing concurrent modifications entirely. This is pessimistic concurrency control: correct but serializing. It eliminates the TOCTOU but sacrifices all parallelism on shared resources. For swain, this is appropriate for task state (.tickets/) but not for source code (where parallelism is the point).

**EAFP over LBYL.** The "easier to ask forgiveness than permission" approach — skip the check, try the operation, handle failures. This is what the test gate does: merge first, test after, revert on failure. Combined with the CAS fast-path check, this gives the best of both worlds.

### Assessment

No better pattern exists for swain's context. The CAS check is the lightest possible pre-check (fast-path reject on file overlap). The test gate is the only mechanism that catches semantic conflicts. The combination provides both speed and correctness. The key insight from CWE-367 is to minimize the window between check and use — which the spike's strategy does by running tests immediately after merge rather than allowing time to elapse.

## 4. Multi-Agent Coordination — How do other frameworks solve this?

**Verdict: No existing framework fully solves the semantic integration problem. Most rely on task-level isolation and accept merge conflicts as a cost of parallelism.**

### Framework comparison

| Framework | Isolation | Coordination | Semantic Verification |
|---|---|---|---|
| **Claude Code Agent Teams** | Worktrees (optional) | Shared task list + messaging | None — "break work so each teammate owns different files" |
| **tick-md** | Not specified | File locking on task state | None — task-level only |
| **Augment (multi-agent guide)** | Worktrees | Coordinator/specialist/verifier | Verification gates before merge, but "human judgment mandatory for semantic conflicts" |
| **Superset** | Worktrees | Task allocation planning | None — assumes allocation prevents conflicts |
| **LangGraph** | In-memory state isolation | Reducers for state merging | Superstep atomicity (all-or-nothing) |
| **CrewAI** | In-memory state | Centralized state catalog | Single source of truth prevents drift |
| **Intility (blog post)** | Worktrees | Team lead coordination | None — "embraces conflicts as inevitable" |

### Key patterns observed

1. **Task-level isolation is universal.** Every framework assigns agents to non-overlapping tasks. This is the spike's Layer 1 (pre-dispatch overlap heuristic).

2. **No framework implements post-merge semantic verification for file-based agents.** Claude Code Agent Teams, Superset, and the Intility approach all rely on task allocation to prevent conflicts and standard git merge for integration. None runs tests on the integrated result before declaring success.

3. **In-memory frameworks have better primitives.** LangGraph's reducer-based merging and CrewAI's centralized state catalog provide semantic merge capabilities that file-based systems lack. The insight: when state is structured data with defined merge semantics, concurrent updates can be merged correctly. When state is source code, no such semantic merger exists.

4. **The "accept conflicts, resolve with AI" approach is emerging.** The Intility blog explicitly embraces merge conflicts as a cost of parallelism and uses Claude to resolve them. This handles textual conflicts but not semantic ones.

5. **Verification gates are rare and manual.** Only the Augment guide mentions verification gates, and even then notes that human judgment is mandatory for semantic conflicts.

### Assessment

Swain's three-layer strategy is more rigorous than any existing AI agent coordination framework. The serialized test gate (Layer 3) provides the semantic verification that no other framework implements. This is a genuine differentiator — most frameworks stop at task-level isolation and accept the risk of semantic conflicts.

## 5. Gaps — What is not covered by the spike or the sources?

### Gap 1: Cross-file semantic conflicts without file overlap

The spike's CAS check (Layer 2) detects same-file modifications. But the spike itself notes: "If Agent A modifies `models.py` and Agent B modifies `views.py` that imports from `models.py`, the CAS check passes but the semantic conflict remains." The test gate (Layer 3) catches this, but there is no fast-path detection for cross-file semantic dependencies.

**Potential mitigation:** Static analysis of import/dependency graphs at dispatch time. If Agent A's task touches `models.py`, also flag `views.py` (and all importers) as "potentially affected." This extends the CAS check from file-level to dependency-level overlap. The cost is false positives (over-serialization), but for swain's scale this is likely acceptable.

### Gap 2: Recovery strategy after test gate failure

The spike says "reject the merge and require the agent to rebase and re-validate." But the details are unspecified:
- Is the failed merge automatically reverted, or does the operator intervene?
- Does the agent re-run from scratch, or does it rebase its existing branch?
- If multiple agents have queued merges, does a failure in agent 2 invalidate agent 3's merge?

Google TAP's approach (automatic revert + notification) and bors's approach (simply not updating master + notification) both provide models. For swain's local context, the simplest approach is: revert the merge on main, rebase the agent's branch onto the new main, re-run the agent's tests, and re-attempt the merge.

### Gap 3: Non-code shared resources

The Upsun article identifies shared resources beyond git: ports, databases, Docker daemon, caches. The spike's file-level collision inventory (Area 1) covers git-tracked files but not runtime resources. If agents run services during testing (e.g., database migrations, local servers), port and state conflicts could cause test failures unrelated to code correctness.

**Potential mitigation:** Per-worktree environment configuration (unique ports, isolated test databases). This is out of scope for the merge queue but should be documented as a convention.

### Gap 4: Scaling beyond 2-4 agents

The spike's analysis assumes 2-4 parallel agents with <60s test suites. Multiple sources (Augment, Superset) identify a practical ceiling of 5-7 agents. At larger scale:
- The serialized test gate becomes a bottleneck (O(N * test_time))
- Batching strategies (as in Google TAP) become necessary
- Review bottleneck compounds the integration bottleneck

This is not an immediate concern for swain's solo-operator context but should be considered in the architecture to avoid painting into a corner.

### Gap 5: Flaky tests

Bors documentation explicitly warns: "if your test suite is not deterministic, bors will not help." A flaky test that passes in the agent's worktree but fails in the merge queue creates a false rejection. The spike does not discuss test suite reliability as a prerequisite for the test gate.

### Gap 6: Commit message fidelity during concurrent sync

The spike identifies the commit-layer TOCTOU (swain-sync generates messages from diffs before committing) but the sources do not address this specific pattern. This appears to be a novel problem specific to AI agent orchestration — no existing framework generates commit messages from pre-commit state. The proposed commit queue (structured tickets with files + message as a unit) is the right approach and has no direct precedent in the sources.
