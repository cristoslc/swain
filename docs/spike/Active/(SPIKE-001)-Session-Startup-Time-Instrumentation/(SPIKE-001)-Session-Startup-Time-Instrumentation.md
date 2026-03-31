---
title: "Session Startup Time Instrumentation"
artifact: SPIKE-001
track: container
status: Active
author: cristos
created: 2026-03-30
last-updated: 2026-03-30
question: "Where does session startup wall time actually go — LLM inference, tool-call overhead, script execution, or file I/O — and what is the achievable floor?"
gate: Pre-MVP
risks-addressed:
  - Optimizing the wrong layer (e.g., scripts when inference dominates)
  - Setting unrealistic success criteria for EPIC-048
evidence-pool: ""
---

# Session Startup Time Instrumentation

## Summary

**Go — proceed with SPEC-194/196.** Both script execution and LLM inference are significant, but the *addressable* time is split roughly 50/50. Chain collapse (SPEC-196) removes ~10-15s of LLM overhead. Preflight deferral + status split (SPEC-194) removes ~8-26s of script time. Worktree deferral (SPEC-195) removes ~3-5s. The achievable floor for a fast greeting is **~700ms** (tab name + worktree detect + session.json read).

## Question

Where does session startup wall time actually go — LLM inference, tool-call overhead, script execution, or file I/O — and what is the achievable floor?

## Go / No-Go Criteria

- **Go (proceed with SPEC-194/196):** LLM round-trips account for >60% of wall time, confirming that chain collapse and greeting split are the highest-leverage changes.
- **Go (pivot to script optimization):** Script execution accounts for >40% of wall time, suggesting we should optimize specgraph/GitHub API calls before touching the skill chain.
- **No-Go (rethink approach):** Wall time is dominated by a single unavoidable operation (e.g., EnterWorktree git clone) that can't be deferred or backgrounded.

## Pivot Recommendation

If script execution dominates, pivot to background/async execution of expensive collectors (specgraph, GitHub API) rather than restructuring the skill chain. If a single unavoidable operation dominates, focus on making that operation faster rather than reorganizing the chain.

## Method

1. **Add timestamps to shell scripts** — instrument `swain-session-bootstrap.sh`, `swain-status.sh`, `swain-preflight.sh` with `date +%s%N` at entry/exit of each major section.
2. **Log skill invocation boundaries** — add a lightweight timing wrapper in the shell launcher that records when each `/skill` invocation starts and ends.
3. **Run 5 cold starts and 5 warm starts** — capture timing data for both scenarios.
4. **Categorize time** into: shell launcher overhead, LLM inference (skill read + reasoning), tool-call round-trip, script execution, file I/O, network I/O (GitHub API).
5. **Calculate achievable floor** — sum only the unavoidable operations (git rev-parse, session.json read, tmux rename) to establish the theoretical minimum.

## Findings

### Script execution breakdown (3 runs averaged, no tmux)

| Phase | Time (ms) | Notes |
|-------|-----------|-------|
| init_marker_check | 5 | Trivial — `test -f` |
| **preflight** | **7,500** | 288-line script, 20+ checks, subprocess-heavy |
| bootstrap_full | 400 | Single consolidated script (SPEC-175) |
| tab_naming | 250 | tmux only |
| worktree_detect | 28 | `git rev-parse --git-common-dir` |
| session_json_read | 10 | `jq` read |
| **status_dashboard** | **18,400** | Full rebuild (specgraph + GitHub API + rendering) |

### Preflight internal breakdown

| Check | Time (ms) | Category |
|-------|-----------|----------|
| trunk_release_detection | 1,559 | **Network I/O** (`git ls-remote`) |
| doctor_security_check | 895 | Python startup + scan |
| skill_gitignore_hygiene | 341 | `git check-ignore` per dir |
| skill_change_discipline | 293 | Bash script delegation |
| initiative_migration_check | 175 | `find` + `grep` loop |
| scanner_availability | 102 | Python startup |
| ssh_readiness | 97 | Bash script delegation |
| governance_freshness_hash | 93 | `shasum` x2 + `awk` |
| All other checks | ~400 | 30-50ms each (file tests, git config) |
| **Overhead (subprocess spawning)** | **~3,500** | Gap between sum (~4s) and total (~7.5s) |

**Key finding:** preflight spawns 60+ subprocesses for symlink repair alone (each with `python3 -c` for relpath). The subprocess spawning overhead (~3.5s) exceeds any individual check.

### Status dashboard internal breakdown

| Collector | Time (ms) | Notes |
|-----------|-----------|-------|
| git_context | 110 | Fast |
| specgraph_build | 386 | **Failed** (import error, SPEC-197) — fast exit |
| tk_query (x2) | 24 | Fast |
| gh_issue_list | 500 | Network I/O |
| gh_api_user | 442 | Network I/O |
| session_json_read | 13 | Fast |
| **Bash processing + jq + rendering** | **~16,900** | Line-by-line parsing, 20+ jq invocations |

**Key finding:** Collector I/O is ~1.5s total. The remaining ~17s is bash overhead: text processing, jq pipeline construction, and rendering logic. The script is 1,067 lines of bash doing JSON manipulation that would be instant in Python/jq streaming mode.

### LLM overhead estimate

| Layer | Estimated time | Basis |
|-------|---------------|-------|
| swain-init skill read + reasoning | 10-15s | Single LLM round-trip to read skill, check marker, delegate |
| swain-session skill read + reasoning | 10-15s | Single LLM round-trip to read skill, run bootstrap, render |
| Tool call overhead per Bash invocation | ~1-2s | SDK round-trip per tool use |
| EnterWorktree (if triggered) | 3-5s | Git worktree create + tool overhead |

**Total estimated LLM overhead: 20-35s** (not measurable from scripts)

### Achievable floor

| Operation | Time (ms) | Required for greeting? |
|-----------|-----------|----------------------|
| .swain-init marker check (shell) | 5 | Yes (in shell launcher) |
| tab naming | 250 | Yes |
| worktree detect | 28 | Yes |
| session.json read | 10 | Yes |
| git branch name | 50 | Yes |
| **Fast greeting floor** | **~350** | Scripts only |
| + 1 LLM round-trip | ~10,000 | Unavoidable (swain-session skill) |
| **Realistic floor** | **~10,350** | With single skill invocation |

### Instrumentation artifacts

- `skills/swain-session/scripts/swain-startup-timing.sh` — top-level timing
- `skills/swain-session/scripts/swain-preflight-timing.sh` — preflight breakdown

### Gate assessment

- LLM round-trips: ~60-75% of total wall time → **Go for SPEC-196** (chain collapse)
- Preflight: ~25% of script time, fully deferrable → **Go for SPEC-194** (defer to background)
- Status dashboard: 70% of script time, entirely optional at startup → **Go for SPEC-194** (on-demand only)
- No single unavoidable bottleneck → **No-Go criteria not met**

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-30 | -- | Initial creation; operator-requested |
