---
title: "Retro: BDD test suite foundation"
artifact: RETRO-2026-04-04-bdd-test-suite
track: standing
status: Active
created: 2026-04-04
last-updated: 2026-04-04
scope: "First bats-core BDD test suite — framework setup, 84 behavioral specs across 4 domains"
period: "2026-04-04"
linked-artifacts: []
---

# Retro: BDD test suite foundation

## Summary

Built swain's first framework-backed test suite. Moved from 44 ad-hoc bash test scripts (hand-rolled assertions, no runner, no CI) to bats-core with vendored helpers, domain-organized specs, and a unified runner. 84 tests cover 8 consumer-facing scripts across session, worktree, artifact, and sync domains. All green.

## What was accomplished

| Item | Detail |
|------|--------|
| Framework | bats-core 1.13.0 with bats-support, bats-assert, bats-file |
| Structure | `spec/` directory, organized by domain |
| Runner | `spec/run` with domain filtering and TAP/JUnit output |
| Tests | 84 behavioral specs in 8 files |
| Scripts covered | 8 of ~63 consumer-facing scripts in `.agents/bin/` |
| Design doc | `docs/superpowers/specs/2026-04-04-bdd-test-suite-design.md` |

## Reflection

### What went well

- **bats-core was already installed** — zero framework-selection friction. The vendored helpers (bats-assert, bats-file) added clean assertion syntax without dependency management overhead.
- **Domain organization** — grouping specs by behavioral domain (session, worktree, artifact, sync) maps cleanly to the skill boundaries. Each `.bats` file reads like a contract for a single script.
- **Sandbox isolation pattern** — disposable git repos per test via `create_test_sandbox()` eliminated state leakage. The macOS path canonicalization fix (`pwd -P`) solved a class of bugs in one place.
- **The operator delegated fully** — "make good decisions in my absence" enabled rapid iteration without ceremony overhead. Brainstorming, framework selection, and implementation all happened in one pass.

### What was surprising

- **macOS `/tmp` symlink mismatch** — `mktemp` returns `/var/folders/...` but `git rev-parse --show-toplevel` returns `/private/var/folders/...`. This caused 18 test failures on the first run. Scripts that compare paths (like `swain-bookmark.sh`'s trunk detection) silently fail when paths differ. This is a latent bug class across all swain scripts that do path comparison.
- **Bootstrap writes make tree dirty** — the greeting script's bootstrap modifies `.agents/session.json` on every run, so a freshly-committed tree is always dirty after session start. This is architecturally correct but undocumented, and could mislead agents checking dirty state.
- **Environment variable leakage** — tests initially inherited `SWAIN_REPO_ROOT` from the real repo, causing scripts to read/write the real `session.json` instead of the sandbox's. The fix (unsetting env vars in `setup.bash`) is simple but easy to forget when adding new scripts that honor env overrides.

### What would change

- **Per-test sandboxes are slow for read-only tests** — tests that only read state (focus lane show, worktree name format) don't need full git init. A lighter fixture would speed up the suite.
- **No CI integration yet** — the runner supports TAP output but no GitHub Actions workflow was created. This is the obvious next step.

### Patterns observed

- **Path comparison is fragile on macOS** — any script that compares filesystem paths needs to canonicalize both sides. This is a cross-cutting concern that should be addressed with a shared helper.
- **State-modifying scripts are hard to test in isolation** — the greeting script calls bootstrap, which calls tab-name, which calls session.json writes. Testing the greeting tests the entire chain. Integration tests are natural here but true unit tests would require refactoring the scripts.
- **Coverage is bottom-heavy** — 8 of ~63 scripts covered (13%). The untested scripts include the most complex ones: `specgraph.sh`, `chart.sh`, `swain-status.sh`, `design-check.sh`. These have the most consumer-facing friction but also the most complex fixture requirements.

## SPEC candidates

1. **macOS path canonicalization helper** — add a `swain-realpath.sh` utility that all scripts use for path comparison, preventing the `/tmp` vs `/private/tmp` mismatch class of bugs
2. **CI workflow for BDD suite** — GitHub Actions workflow that runs `spec/run --tap` on PR and push to trunk
3. **Bootstrap dirty-state documentation** — document in ADR or SPEC that session bootstrap intentionally modifies session.json, so agents should check dirty state BEFORE bootstrap, not after
4. **Phase 2 test coverage** — specs for `readability-check.sh`, `adr-check.sh`, `design-check.sh`, `swain-session-state.sh`, `detect-worktree-links.sh`, `resolve-worktree-links.sh`
5. **Phase 3 end-to-end flows** — integration specs for session lifecycle (start → work → close → resume), artifact transitions, and sync commit pipeline
