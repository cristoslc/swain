# INITIATIVE-018 Teardown Report

## Implementation Summary

Replaced the hub-and-spoke architecture (ADR-039) with a project-level microkernel topology (ADR-046) plus watchdog process manager (ADR-047). 8 SPECs implemented across 6 EPICs, plus 2 EPIC-074 provisioning specs.

### Commits (7 implementation + 1 verification)

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

### Test Results

- **260 unit/integration tests pass**, 8 skipped (launcher flow superseded by worktree scanner)
- **32 verification loop tests pass** — alignment with ADR-046, ADR-047, ADR-038

### Files Created

- `src/swain_helm/config.py` — SPEC-320 config and credential resolution
- `src/swain_helm/watchdog.py` — SPEC-318 watchdog core
- `src/swain_helm/opencode_discovery.py` — SPEC-321 opencode discovery and auth
- `src/swain_helm/plugin_process.py` — extracted PluginProcess class
- `src/swain_helm/worktree_scanner.py` — SPEC-323 continuous worktree discovery
- `src/swain_helm/session_registry.py` — SPEC-324 session registry persistence
- `bin/swain-helm` — SPEC-319 CLI

### Files Modified

- `src/swain_helm/bridges/project.py` — rewritten as microkernel (237 → 333 lines with scanner/registry wiring)
- `src/swain_helm/protocol.py` — added worktree/session event types
- `src/swain_helm/plugins/zulip_chat.py` — narrow stream filter, worktree topic naming
- `src/swain_helm/adapters/opencode_server.py` — subprocess entry point
- `src/swain_helm/adapters/claude_code.py` — subprocess entry point
- `src/swain_helm/adapters/tmux_pane.py` — subprocess entry point
- `src/swain_helm/provision.py` — branding update (swain-helm, not Untethered Operator)
- `pyproject.toml` — package name, 4 console scripts

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
| 1 | Operator can steer, monitor, and approve agent work from phone or messaging app | PASS | Zulip chat adapter provides bidirectional command/event flow. Operators can send /work, /approve, /deny and text prompts from the Zulip mobile app. Sessions run locally with full filesystem access. |
| 2 | Approval prompts forwarded to a remote surface so unattended sessions don't stall | PASS | approval_needed event flows through chat plugin to Zulip. Operator can approve/deny from mobile. ProjectBridge tracks state transitions from WAITING_APPROVAL → ACTIVE on approval. |
| 3 | Status dashboard information accessible outside the terminal | PARTIAL | Chat bridge surfaces status through Zulip control topic. swain-helm host status requires CLI access. Dedicated web dashboard is v2 (explicitly deferred in INITIATIVE scope). |
| 4 | At least one channel integration delivering notifications and accepting commands | PASS | Zulip integration fully implemented: narrow stream filtering, worktree topic naming, command parsing (control_message, send_prompt, launch_session, approve, cancel). |

**Overall: 3/4 fully met, 1/4 partial (web dashboard deferred to v2 per design).**

## Verification Loop Results

- **Cycle 1**: 9 mismatches between verification tests and actual API signatures. Root cause: verification tests were written against plan-time API assumptions, not the actual implementation.
- **Cycle 2**: All 9 fixed, 32 verification tests pass. No further issues found.
- **Alignment confirmed**: ADR-046 (no hub, one session per worktree, 15s polling), ADR-047 (credential resolution, 30s reconciliation, per-port auth), ADR-038 (subprocess plugins, NDJSON protocol), excisable software constraint (zero swain-specific coupling in core runtime).

## Architectural Decisions Log

1. **WorktreeScanner uses `git worktree list --porcelain`** — per SPEC-323. No debouncing. 15s default poll.
2. **SessionRegistry keyed by branch name, not session_id** — per SPEC-324. Enables lookups by Zulip topic.
3. **PluginProcess extracted from kernel.py** — per ADR-038. Both chat and runtime adapters are subprocess plugins.
4. **Old architecture fully deleted** — kernel.py, host.py, main.py, runtime_state.py all removed. No fallback path.
5. **Trunk detection: refs/heads/main OR refs/heads/master** → topic "trunk". This is a broader match than some might expect but matches real-world usage.
6. **SPEC-293/SPEC-294 (output shaping, Mermaid rendering) deferred** — not in scope for the core architecture refactor. These are chat UX features that can be added to the chat adapter later.

## Known Gaps

- **SPEC-326/SPEC-327** (EPIC-074 provisioning specs) are written but not yet implemented. The provision.py branding update is done, but `swain-helm host provision` CLI wiring and `project add --stream` Zulip stream creation are pending.
- **SPEC-293/SPEC-294** (output shaping, Mermaid rendering) deferred to future work.
- **Watchdog bridge start command** uses `python -m swain_helm.bridges.project` instead of the proper CLI entry point. Should be updated when project bridge gets a subprocess entry point.
- **Session restart on death** (ADR-047: "If a worktree's session dies, it is restarted") is not yet implemented. The worktree scanner creates sessions on discovery but does not auto-restart dead ones.

## Agent Decisions

- Chose to implement SPEC-323/324 sequentially (scanner first, then registry) due to dependency.
- Chose to create EPIC-074 specs (SPEC-326/327) as minimal placeholders rather than skip them — the user chose this approach during planning.
- Chose to defer SPEC-293/294 (output shaping/Mermaid) from Phase 2 — these are not architecture-critical.
- Verification loop cycle 1 found API mismatches — fixed in cycle 2. No implementation gaps required code changes.