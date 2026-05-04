---
title: "Docker Test Infrastructure"
artifact: SPEC-331
track: implementable
status: Active
author: cristos
authored-by: GLM-5.1 (supervisor)
created: 2026-04-25
last-updated: 2026-04-25
priority-weight: high
type: feature
parent-epic: EPIC-084
parent-initiative: INITIATIVE-018
linked-artifacts:
  - SPEC-318
  - SPEC-319
  - SPEC-320
  - SPEC-321
  - SPEC-322
  - SPEC-323
  - SPEC-324
  - SPEC-325
  - SPEC-326
  - SPEC-327
  - ADR-046
  - ADR-047
  - ADR-038
depends-on-artifacts:
  - SPEC-318
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Docker Test Infrastructure

## Problem Statement

Process-level tests for swain-helm (watchdog, bridge, plugin subprocesses) spawn real processes that listen on ports, write PID files, and connect to external services like Zulip. Running these tests on the host caused a bridge to kill the developer's real opencode server on port 4096. Manual UAT test plans exist as markdown but lack executable automation. There is no isolated environment for integration tests that need real subprocess lifecycle, network access, or the opencode binary.

## Desired Outcomes

A Docker-based test environment that isolates process-interactive tests from the host. All UAT test plans have corresponding executable pytest files. Tests that spawn real processes or need external services run inside Docker. Tests that are pure unit tests (mocked, no subprocess spawning) continue running on the host.

## External Behavior

**Docker test image** (`Dockerfile.test`):
- Python 3.12 slim base with git, curl, opencode binary, and uv installed.
- swain-helm installed in editable mode with dev dependencies (pytest, pytest-asyncio).
- `SWAIN_HELM_TEST_MODE=1` environment variable set at build time.

**Compose services** (`docker-compose.test.yml`):
- `test`: runs the full pytest suite.
- `test-unit`: runs only `tests/unit/`.
- `test-integration`: runs only `tests/integration/` (excluding shell scripts).
- `test-uat`: runs only `tests/uat/`.
- `test-acceptance`: runs only `tests/acceptance/`.
- `test-e2e`: runs end-to-end synthetic transaction tests (requires `ZULIP_BOT_API_KEY`).

**Test directory convention**:
- `tests/unit/`: Pure pytest, no subprocess spawning, no external services.
- `tests/integration/`: Async BDD tests, verification loop, control flow tests. Mocked subprocesses.
- `tests/uat/`: SPEC-level acceptance tests. Process-interactive tests spawn real watchdog/bridge processes inside Docker. Marked with `@skip_if_not_docker` if they spawn real processes.
- `tests/acceptance/`: ADR architectural constraint tests. Verify invariants like "no hub routing" and "credentials never on disk."
- `tests/e2e/`: Full pipeline synthetic transactions. Start watchdog in Docker, send Zulip message, verify bridge processes it. Requires `ZULIP_BOT_API_KEY` env var.

**Pytest markers**:
- `@skip_if_not_docker`: Skips unless running inside Docker or `SWAIN_HELM_TEST_MODE=1`. Use for tests that spawn real processes that could interfere with host services.
- `@requires_zulip`: Skips unless `ZULIP_BOT_API_KEY` is set. Use for tests that send messages to real Zulip.

## Acceptance Criteria

1. **Given** `Dockerfile.test` exists, **when** `docker compose -f docker-compose.test.yml build test` runs, **then** it produces an image with Python 3.12, opencode, git, and swain-helm installed.

2. **Given** the test Docker image is built, **when** `docker compose -f docker-compose.test.yml run test-unit` runs, **then** all unit tests pass without Docker (they run on the host too).

3. **Given** the test Docker image is built, **when** `docker compose -f docker-compose.test.yml run test-integration` runs, **then** all integration tests pass inside the container.

4. **Given** the test Docker image is built and `SWAIN_HELM_TEST_MODE=1`, **when** `docker compose -f docker-compose.test.yml run test-uat` runs, **then** process-interactive UAT tests (watchdog lifecycle, CLI, PID management) pass inside the container without affecting host services.

5. **Given** `Dockerfile.test` includes the opencode binary, **when** opencode discovery tests need a running server, **then** the container can start `opencode serve` on port 4098 without conflicting with the host's port 4096.

6. **Given** each SPEC from 318--327 has a UAT markdown file in `docs/tests/uat/`, **when** the corresponding executable test file exists in `tests/uat/`, **then** the pytest file covers all acceptance criteria listed in the markdown UAT.

7. **Given** the `@skip_if_not_docker` marker, **when** tests are run on the host without `SWAIN_HELM_TEST_MODE=1`, **then** process-interactive tests are skipped rather than failing or interfering with host services.

8. **Given** the `@requires_zulip` marker, **when** `ZULIP_BOT_API_KEY` is not set, **then** Zulip-requiring tests are skipped.

9. **Given** the test infrastructure exists, **when** a developer runs `docker compose -f docker-compose.test.yml run test`, **then** the full suite (unit + integration + UAT + acceptance) runs to completion with exit code 0.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1. Docker image builds | `docker compose -f docker-compose.test.yml build test` | Pending (Docker) |
| 2. Unit tests pass on host | `239 passed` in `tests/unit/` | Pass |
| 3. Integration tests pass in Docker | `55 passed, 8 skipped` in `tests/integration/` | Pending (Docker) |
| 4. UAT process tests isolated | `test_watchdog_core.py`, `test_cli.py` | Pending (Docker) |
| 5. opencode binary in container | Dockerfile.test includes opencode with hash verification | Built |
| 6. UAT markdown coverage | Each `docs/tests/uat/SPEC-*.md` has matching `tests/uat/test_*.py` | 9/9 covered |
| 7. Skip markers work | `@skip_if_not_docker` skips 102 tests on host | Pass |
| 8. Zulip skip works | `@requires_zulip` skips Zulip tests without key | Pass |
| 9. Full suite in Docker | `docker compose run test` | Pending |
| 1. Docker image builds | `docker compose build test` succeeds | |
| 2. Unit tests pass on host | `pytest tests/unit/` passes on macOS | |
| 3. Integration tests pass in Docker | `docker compose run test-integration` passes | |
| 4. UAT process tests isolated | Watchdog tests pass in Docker without killing host processes | |
| 5. opencode binary in container | `docker compose run test which opencode` returns a path | |
| 6. UAT markdown coverage | Each `docs/tests/uat/SPEC-*.md` has a matching `tests/uat/test_*.py` | |
| 7. Skip markers work | `pytest -m "not docker"` skips process-interactive tests on host | |
| 8. Zulip skip works | Tests skip when `ZULIP_BOT_API_KEY` unset | |
| 9. Full suite in Docker | `docker compose run test` exits 0 | |

## Scope and Constraints

- Container uses port 4098 for opencode (not 4096) to avoid ambiguity with host convention.
- Zulip tests that send real messages are opt-in via `ZULIP_BOT_API_KEY`. Mocked Zulip tests run always.
- The Docker image does NOT include 1Password CLI (`op`). Tests that need `op://` resolution use mocked subprocesses, not real 1Password.
- No test should ever write to `~/.config/swain-helm/` on the host. All config writes go to `tmp_path` fixtures.
- Only swain-helm test infrastructure is in scope. Core swain test harness (SPEC-215) is separate.

## File Layout

```
swain-helm/
  Dockerfile.test
  docker-compose.test.yml
  tests/
    conftest_integration.py    # Shared fixtures for process-interactive tests
    unit/                      # Pure pytest, no subprocess spawning
    integration/               # BDD async tests, verification loop
    uat/                       # SPEC-level executable tests
      test_watchdog_core.py    # SPEC-318
      test_cli.py              # SPEC-319
      test_config_resolution.py # SPEC-320
      test_opencode_discovery.py # SPEC-321
      test_project_bridge.py   # SPEC-322
      test_worktree_discovery.py # SPEC-323
      test_session_registry.py  # SPEC-324
      test_chat_filtering.py   # SPEC-325
      test_provision.py        # SPEC-326/327
    acceptance/                # ADR architectural constraint tests
      test_adr046_topology.py  # No hub routing, one session per worktree
      test_adr047_watchdog.py  # Credential resolution, 30s cycle
      test_adr038_plugins.py   # NDJSON protocol, plugin isolation
    e2e/                       # Full pipeline synthetic transactions
      test_e2e_pipeline.py     # Watchdog -> bridge -> Zulip -> verify
```