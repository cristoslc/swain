# TESTING

## Prerequisites

- Docker
- 1Password CLI (`op`) — only for E2E tests with real Zulip credentials

## Quick Start

Build the test image and run unit tests:

```bash
docker build -f Dockerfile.test -t swain-helm:test .
docker run --rm swain-helm:test python -m pytest tests/unit/ -v --tb=short
```

## Test Categories

| Category | Path | Count | What it tests |
|----------|------|-------|---------------|
| Unit | `tests/unit/` | 174 | Pure logic, no I/O, no processes |
| Integration | `tests/integration/` | 32 | ADR constraint verification, module interfaces |
| UAT | `tests/uat/` | ~116 | Spec-level acceptance: process spawning, CLI commands, config, bridges |
| Acceptance | `tests/acceptance/` | 22 | ADR-038/046/047 architectural constraints |
| E2E | `tests/e2e/` | 7 | Full pipeline: watchdog lifecycle, Zulip integration |
| Smoke | `tests/external/` | ~20 | Container health checks from host |

**Total: ~351 tests**

## Running Tests

### All tests in Docker

```bash
docker compose -f docker-compose.test.yml up test
```

### Individual suites

```bash
# Unit (fast, no processes)
docker compose -f docker-compose.test.yml up test-unit

# Integration (fast, no processes)
docker compose -f docker-compose.test.yml up test-integration

# UAT (spawns real watchdog processes)
docker compose -f docker-compose.test.yml up test-uat

# Acceptance (ADR constraints)
docker compose -f docker-compose.test.yml up test-acceptance

# E2E (full pipeline, needs Zulip credentials)
docker compose -f docker-compose.test.yml up test-e2e
```

### Direct docker run

```bash
docker run --rm swain-helm:test python -m pytest tests/unit/ -v --tb=short
docker run --rm swain-helm:test python -m pytest tests/acceptance/ -v --tb=short
```

## External Testing (from outside the container)

The UAT, E2E, and smoke tests can be run against containerized services from the host machine instead of spawning local processes. This is useful for:

- Testing production-like container configurations
- CI/CD pipelines that need to verify deployed containers
- Running tests without installing Python dependencies locally

### Quick start for external testing

```bash
# Start the external test containers
docker compose -f docker-compose.external-tests.yml up -d smoke-test-target uat-test-target

# Run smoke tests against container from host
python -m pytest tests/external/test_smoke.py -v

# Run UAT tests against container from host
SWAIN_HELM_EXTERNAL_TEST=1 python -m pytest tests/uat/test_watchdog_core.py -v

# Cleanup
docker compose -f docker-compose.external-tests.yml down
```

### External test targets

| Service | Container | Health Port | Opencode Port | Purpose |
|---------|-----------|-------------|---------------|---------|
| smoke-test-target | swain-helm-smoke-test | 18081 | 14099 | Basic container health |
| uat-test-target | swain-helm-uat-test | 18082 | 14100 | Pre-configured projects |
| e2e-test-target | swain-helm-e2e-test | 18083 | 14101 | Full Zulip integration |

### Environment variable

Set `SWAIN_HELM_EXTERNAL_TEST=1` to run tests against external containers:

```bash
# Run all UAT tests against external container
SWAIN_HELM_EXTERNAL_TEST=1 pytest tests/uat/ -v

# Run specific test file
SWAIN_HELM_EXTERNAL_TEST=1 pytest tests/uat/test_watchdog_core.py -v
```

### External test compose services

```bash
# Start specific test targets
docker compose -f docker-compose.external-tests.yml up -d smoke-test-target
docker compose -f docker-compose.external-tests.yml up -d uat-test-target
docker compose -f docker-compose.external-tests.yml up -d e2e-test-target

# With Zulip credentials (for e2e)
op run --env-file=.env.test -- docker compose -f docker-compose.external-tests.yml up -d e2e-test-target
```

## 1Password Credential Injection

Tests that require real Zulip credentials (E2E, some UAT) use environment variables resolved from 1Password. The `.env.test` file contains `op://` secret references, not plaintext secrets.

### One-time setup

1. Install [1Password CLI](https://developer.1password.com/docs/cli/get-started/)
2. Sign in: `op account add --address my.1password.com --email you@example.com`
3. Unlock: `eval $(op signin)`

### Running with credentials

```bash
# op run resolves op:// references in .env.test before launching docker
op run --env-file=.env.test -- docker compose -f docker-compose.test.yml up test-e2e
```

This prompts for 1Password unlock once at startup. All `op://` references in `.env.test` are resolved and injected as environment variables into the container.

### Without 1Password

Tests that need Zulip credentials are automatically skipped when `ZULIP_BOT_API_KEY` is not set. You can still run unit, integration, and acceptance tests without any credentials:

```bash
docker compose -f docker-compose.test.yml up test-unit test-acceptance
```

## Interactive Development

The `opencode-server` service publishes port 4098 so you can attach an opencode client from the host:

```bash
docker compose -f docker-compose.test.yml up opencode-server
# Then connect from host:
opencode serve --port 4098 --remote http://localhost:4098
```

## Docker Test Image

The test image (`Dockerfile.test`) includes:

- Python 3.12
- git
- opencode CLI v1.14.19 (SHA512-verified from npm registry)
- swain-helm package with dev dependencies
- `SWAIN_HELM_TEST_MODE=1` environment variable (enables process-level tests)

### Rebuilding

```bash
docker build -f Dockerfile.test -t swain-helm:test .
```

Rebuild after any change to `Dockerfile.test`, `pyproject.toml`, or source code.

## Test Architecture

### Why Docker?

Process-level tests (UAT, E2E) spawn real watchdog and bridge processes. Running these on the host is dangerous — an integration test previously killed a real opencode server on port 4096. Docker provides:

- **Port isolation** — test processes cannot conflict with host services
- **Clean filesystem** — each test run starts fresh
- **Process cleanup** — container stop kills all child processes
- **Reproducibility** — same Python, git, opencode versions every run

### Test Markers

- `skip_if_not_docker` — skips unless running inside Docker or in EXTERNAL_TEST_MODE
- `skip_if_no_zulip` — skips unless `ZULIP_BOT_API_KEY` is set
- `xfail` — expected failure (e.g., CLI `--config-dir` not yet implemented)
- `smoke` — smoke tests for container health

### UAT Test Coverage by SPEC

| SPEC | File | Tests | Coverage |
|------|------|-------|----------|
| SPEC-318 | `test_watchdog_core.py` | 12 | Watchdog process lifecycle |
| SPEC-319 | `test_cli.py` | 16 | CLI host/project commands |
| SPEC-320 | `test_config_credential_resolution.py` | 12 | op:// references, security |
| SPEC-321 | `test_opencode_discovery.py` | 9 | Port scanning, health checks |
| SPEC-322 | `test_project_bridge_microkernel.py` | 13 | Plugin spawning, NDJSON protocol |
| SPEC-323 | `test_worktree_discovery.py` | 15 | Git worktree scanning, diff |
| SPEC-324 | `test_session_registry.py` | 14 | Persistent state, atomic writes |
| SPEC-325 | `test_chat_stream_filtering.py` | 11 | Stream filtering, commands |
| SPEC-326/327 | `test_provision_registration.py` | 14 | Zulip provisioning, multi-project |

### Acceptance Test Coverage by ADR

| ADR | File | Tests | Coverage |
|-----|------|-------|----------|
| ADR-038 | `test_adr_038_plugin_architecture.py` | 8 | Subprocess plugins, NDJSON, excisability |
| ADR-046 | `test_adr_046_microkernel_topology.py` | 7 | No hub routing, one session per worktree, polling |
| ADR-047 | `test_adr_047_watchdog_architecture.py` | 7 | Credential resolution, reconciliation, per-port auth |

## Known Gaps

1. **CLI `--config-dir`** — Not yet implemented; 1 test marked `xfail`
2. **1Password locked** — Test requires `op` CLI; skipped without it
3. **Zulip E2E** — Requires real credentials; skipped without `ZULIP_BOT_API_KEY`
4. **SIGINT graceful shutdown** — Bridge process cleanup timing; investigation needed

## Adding New Tests

1. Unit tests: `tests/unit/test_*.py` — no I/O, mock everything
2. Integration tests: `tests/integration/test_*.py` — module interfaces, no processes
3. UAT tests: `tests/uat/test_*.py` — process-level, mark with `skip_if_not_docker`
4. Acceptance tests: `tests/acceptance/test_adr_*.py` — ADR constraint verification
5. E2E tests: `tests/e2e/test_*.py` — full pipeline, mark with `skip_if_no_zulip`
6. Smoke tests: `tests/external/test_smoke.py` — container health from outside

All tests must pass inside the Docker test container. Run locally at your own risk.