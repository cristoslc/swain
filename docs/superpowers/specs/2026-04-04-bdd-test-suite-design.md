# BDD Test Suite for Swain

## Problem

Swain has 30+ skills, 80+ shell scripts, and 44 ad-hoc test files with no framework, no centralized runner, and no CI integration. Minor regressions in consumer-facing scripts cause friction that compounds across sessions. There is no way to verify behavioral contracts before shipping.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | **bats-core 1.13.0** | Already installed, well-maintained, BDD-style via descriptive `@test` names |
| Helpers | **bats-support + bats-assert + bats-file** | Vendored in `spec/support/lib/` |
| Directory | **`spec/`** | BDD convention; existing `tests/` preserved for legacy |
| Organization | By behavioral domain | `spec/session/`, `spec/worktree/`, `spec/artifact/`, `spec/sync/` |
| Fixture strategy | Temp git repos per test | `create_test_sandbox()` with path canonicalization for macOS |
| Runner | **`spec/run`** | Supports domain filtering and TAP/JUnit output for CI |

## Architecture

```
spec/
  run                          # runner script (domain filter + formatter)
  support/
    setup.bash                 # shared helpers, sandbox creation, artifact scaffolding
    lib/
      bats-support/            # vendored
      bats-assert/             # vendored
      bats-file/               # vendored
  session/
    greeting.bats              # SPEC-194: fast greeting contract
    bookmark.bats              # context + worktree bookmark lifecycle
    focus.bats                 # focus lane set/clear/show
  worktree/
    naming.bats                # worktree name format + uniqueness
    overlap.bats               # SPEC-195: overlap detection
  artifact/
    next_id.bats               # SPEC-193: cross-branch ID allocation
  sync/
    duplicate_detection.bats   # SPEC-158: collision detection
    rebuild_index.bats         # SPEC-047: index regeneration
  fixtures/                    # static test data (future)
```

## Key Design Choices

### Sandbox isolation

Every test that touches git state gets a fresh temporary repo via `create_test_sandbox()`. The function canonicalizes paths with `pwd -P` to handle macOS `/tmp` symlinks — without this, `git rev-parse --show-toplevel` returns `/private/var/...` while `mktemp` returns `/var/...`, causing path mismatches in scripts that compare paths.

### Environment hygiene

Tests unset `SWAIN_REPO_ROOT` and `SWAIN_SESSION_FILE` so scripts under test discover the sandbox via `git rev-parse` rather than inheriting the real repo root.

### Scaffold commits

`scaffold_swain_project()` commits all created files so dirty-state tests have a known baseline. The greeting bootstrap writes to `session.json` on every run, so a scaffolded + committed tree is still dirty after greeting — this is documented as expected behavior.

### Per-test vs per-file sandboxes

Tests that modify state destructively (removing `.agents/`, creating lock files, accumulating artifacts) use per-test sandboxes via `setup()`/`teardown()`. Read-only tests can share a per-file sandbox via `setup_file()`/`teardown_file()` for speed.

## Coverage Summary (Phase 1)

| Domain | File | Tests | Scripts Covered |
|--------|------|-------|-----------------|
| Session | greeting.bats | 14 | swain-session-greeting.sh, swain-session-bootstrap.sh |
| Session | bookmark.bats | 19 | swain-bookmark.sh |
| Session | focus.bats | 10 | swain-focus.sh |
| Worktree | naming.bats | 5 | swain-worktree-name.sh |
| Worktree | overlap.bats | 8 | swain-worktree-overlap.sh |
| Artifact | next_id.bats | 10 | next-artifact-id.sh |
| Sync | duplicate_detection.bats | 9 | detect-duplicate-numbers.sh |
| Sync | rebuild_index.bats | 9 | rebuild-index.sh |
| **Total** | **8 files** | **84** | **8 scripts** |

## Future Phases

Phase 2 targets: `readability-check.sh`, `adr-check.sh`, `design-check.sh`, `specwatch.sh`, `swain-session-state.sh`, `detect-worktree-links.sh`, `resolve-worktree-links.sh`.

Phase 3 targets: end-to-end skill flows (session lifecycle, artifact transitions, sync commit pipeline).
