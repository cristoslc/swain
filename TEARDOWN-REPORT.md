# INITIATIVE-018 Teardown Report

## Implementation Summary

Replaced the hub-and-spoke architecture (ADR-039) with a project-level microkernel topology (ADR-046) plus watchdog process manager (ADR-047). 8 SPECs implemented across 6 EPICs, plus 2 EPIC-074 provisioning specs. All prism review findings resolved. Provisioning end-to-end wired.

### Commits (implementation + bug fixes + provision)

| Commit | Description |
|--------|-------------|
| d56d39d3 | Package rename: untethered → swain_helm |
| 48e4a760 | Extract PluginProcess, add worktree/session protocol events |
| d8b31287 | Phase 1: watchdog, CLI, config, opencode discovery |
| 18151c97 | Phase 2: adapter entry points + stream filtering |
| 1e1f0cd1 | Phase 2: microkernel refactor, delete old architecture |
| a9faa37a | Phase 3: worktree scanner + session registry |
| 4a651a44 | Phase 4: worktree session integration tests |
| 95903dd9 | Phase 4: EPIC-074 specs, provision.py branding |
| c97192b3 | Phase 5: verification loop (32 tests pass) |
| 2728ae92 | Fix: all prism review findings — critical, high, medium, style |
| f01fddae | Fix: remaining prism review style/security issues, PID reuse protection |
| 7e3710ec | Feat: SPEC-326/327 provision + project registration, fix hanging tests |

### Test Results

- **271 unit/integration tests pass**, 8 skipped (tmux-dependent)
- **173 unit tests** (including 9 new provision tests, 2 fixed StartIfNeeded tests)
- **97 integration tests** (including 32 verification loop tests)
- **0 failures** across the full suite

### Files Created

- `src/swain_helm/config.py` — SPEC-320 config, credential resolution, shared constants
- `src/swain_helm/watchdog.py` — SPEC-318 watchdog core with PID reuse protection
- `src/swain_helm/opencode_discovery.py` — SPEC-321 opencode discovery and async auth
- `src/swain_helm/plugin_process.py` — extracted PluginProcess class with error handling
- `src/swain_helm/worktree_scanner.py` — SPEC-323 continuous worktree discovery
- `src/swain_helm/session_registry.py` — SPEC-324 session registry with path validation
- `src/swain_helm/adapters/__init__.py` — shared run_adapter() for adapter boilerplate
- `bin/swain-helm` — SPEC-319 CLI with safe JSON generation
- `tests/unit/test_provision.py` — 9 provision tests (mocked Zulip)

### Files Modified

- `src/swain_helm/bridges/project.py` — microkernel with registry persistence, DRY session lookup
- `src/swain_helm/protocol.py` — worktree/session events, docstrings
- `src/swain_helm/plugins/zulip_chat.py` — narrow stream filter, worktree topic naming
- `src/swain_helm/adapters/opencode_server.py` — shared run_adapter entry point
- `src/swain_helm/adapters/claude_code.py` — shared run_adapter entry point
- `src/swain_helm/adapters/tmux_pane.py` — shared run_adapter entry point
- `src/swain_helm/provision.py` — writes helm.config.json + project config, op:// keys, 0600 perms

### Files Deleted

- `src/swain_helm/kernel.py` — HostKernel hub
- `src/swain_helm/bridges/host.py` — HostBridge hub
- `src/swain_helm/main.py` — host kernel entry point
- `src/swain_helm/runtime_state.py` — replaced by PID files
- `src/swain_helm/plugins/project_bridge.py` — 74-line stub
- `bin/swain-bridge` — replaced by bin/swain-helm
- `tests/unit/test_host_bridge.py` — dead code

## Success Criteria Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Operator can steer, monitor, and approve agent work from phone | PASS | Zulip chat adapter provides bidirectional command/event flow. /work, /approve, /deny from mobile. |
| 2 | Approval prompts forwarded so unattended sessions don't stall | PASS | approval_needed event flows through chat to Zulip. State transitions persisted to registry. |
| 3 | Status dashboard accessible outside the terminal | PARTIAL | Chat bridge surfaces status through Zulip control topic. Web dashboard deferred to v2. |
| 4 | At least one channel integration delivering notifications and commands | PASS | Zulip integration: narrow stream filtering, worktree topic naming, full command set. |

**Overall: 3/4 fully met, 1/4 partial (web dashboard deferred by design).**

## Prism Review Resolution

All 32 findings from 4-agent PR review resolved:

- **3 critical**: Shell injection (heredoc→python JSON), scan failure false-death (return last-known), session state not persisted (call update_entry)
- **5 high**: Sync urllib (async wrappers), on_message error handling, fire-and-forget start (done callback), lost Popen ref (self._procs dict), plaintext API key (op:// reference)
- **6 medium**: Path traversal (resolve+validate), non-localhost auth guard, PID reuse (start-time validation), daemonize fd leak + /tmp log, BrokenPipeError handler, file permissions 0600
- **8 style**: Frozen dataclass redundant __eq__/__hash__, dispatch dict for _runtime_cmd, top-level imports, DRY session lookup, shared constants, shared run_adapter(), import base64 at top-level
- **10 documentation**: Module/class/method docstrings added to opencode_discovery.py, project.py, protocol.py, plugin_process.py

## Verification Loop Results

- **Cycle 1**: 9 mismatches between verification tests and API signatures. Fixed.
- **Cycle 2**: 32 verification tests pass. Full alignment with ADR-046, 047, 038.
- **Post-fix re-run**: 271 total tests pass, 0 failures.

## Production Readiness Assessment

### Ready for production

- **Watchdog process manager**: starts, stops, and reconciles bridge processes on a 30s cycle. PID reuse protection via start-time validation. Graceful shutdown on SIGTERM.
- **Project bridge microkernel**: routes chat↔runtime via subprocess plugins. Worktree-driven session management with 15s polling. Session state persisted to registry.
- **Zulip integration**: stream filtering, worktree topic naming, command parsing, approval flow.
- **Provisioning**: `swain-helm host provision` creates Zulip bot, stream, writes helm.config.json + per-project config with op:// credential references.
- **CLI**: `swain-helm host up/down/status`, `swain-helm project add/remove/list`. Safe JSON generation, .git validation.
- **Credential safety**: 1Password op:// references resolved once at startup, cached in process-locked memory, never in stdout or config files.
- **Error handling**: PluginProcess catches on_message exceptions and BrokenPipeError. Start tasks have done callbacks. Scan failures return last-known state.

### Known gaps (non-blocking for initial deploy)

1. **Session auto-restart on death** — ADR-047 says dead sessions should restart; currently only detected, not respawned. Operator can manually restart via /work.
2. **No web dashboard** — status accessible only via CLI and Zulip control topic. Explicitly deferred to v2.
3. **SPEC-293/294** (output shaping, Mermaid rendering) — deferred, not architecture-critical.
4. **No end-to-end smoke test against real Zulip** — adapter unit tests use mocks. First deploy will be the first real integration test.

### Deployment prerequisites

1. `op` (1Password CLI) must be installed and authenticated for op:// resolution.
2. `zulip` Python package must be installed (`pip install zulip`).
3. An opencode-serve instance must be running (or the bridge will attempt to start one).
4. The Zulip bot must have stream creation permissions.

### Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PID reuse after system restart | Low | Sessions attach to wrong process | Start-time validation in watchdog |
| Zulip API rate limiting | Low | Commands delayed | Zulip client handles backoff |
| opencode-serve port conflict | Medium | Bridge can't connect | Per-port auth, auto-discovery |
| Credential leak in logs | Low | Auth compromise | op:// refs never resolved to stdout; 0600 file perms |
| Plugin crash kills reader | Low | Bridge loses chat contact | on_message error handling, done callbacks |

## Architectural Decisions Log

1. **WorktreeScanner uses `git worktree list --porcelain`** — per SPEC-323. 15s default poll. On scan failure, returns last-known set.
2. **SessionRegistry keyed by branch name** — per SPEC-324. Enables lookups by Zulip topic.
3. **PluginProcess extracted from kernel.py** — per ADR-038. Both chat and runtime adapters are subprocesses.
4. **Old architecture fully deleted** — no fallback path.
5. **Trunk detection: refs/heads/main OR refs/heads/master** → topic "trunk".
6. **SPEC-293/294 deferred** — not architecture-critical.
7. **Shared constants in config.py** — DEFAULT_OPENCODE_PORT (4096), DEFAULT_WORKTREE_POLL_INTERVAL_S (15.0), DEFAULT_OPENCODE_BASE_URL.
8. **Shared run_adapter() in adapters/__init__.py** — eliminates duplicated _amain pattern across all 3 adapter files.
9. **PID files store start time** — format "pid\nstart_ts\n" enables PID reuse detection.

## Agent Decisions

- Chose to implement SPEC-323/324 sequentially (scanner first, then registry) due to dependency.
- Chose to resolve all 32 prism review findings before merging rather than defer low-priority ones — the fixes were small and the review was fresh.
- Chose to wire provision to write BOTH helm.config.json and per-project config — the watchdog reads projects/, not helm.config.json, so both are needed.
- Chose to use asyncio.to_thread() for HTTP calls rather than switch to aiohttp — minimal change, same safety.
- Chose PID start-time validation rather than /proc/cmdline checks — more portable, works on macOS via `ps`.

Co-Authored-By: GLM-5.1 (supervisor)