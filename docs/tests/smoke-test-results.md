# Smoke Test Results — 2026-04-20

## Summary

Full end-to-end pipeline verified with real Zulip instance (cristoslc.zulipchat.com).

## Tests Passed

### Watchdog Core (SPEC-318)
- **UAT-318-01**: Two project configs → two bridges started ✅
- **UAT-318-02**: auto_start=false → bridge not started ✅
- **UAT-318-03**: Stale PID file → bridge restarted ✅
- **UAT-318-08**: Zero configs → no crash ✅
- **UAT-318-09**: Malformed config → skipped with error log ✅
- **UAT-318-10**: Bridge log file populated ✅

### CLI (SPEC-319)
- **UAT-319-05**: host status when watchdog down ✅
- **UAT-319-06**: project add with git repo ✅
- **UAT-319-07**: project add rejects non-git ✅
- **UAT-319-08**: project add idempotent ✅
- **UAT-319-09**: project remove ✅
- **UAT-319-10**: project list ✅
- **UAT-319-NEG-02**: project remove nonexistent ✅
- **UAT-319-NEG-03**: project list with no projects ✅

### Config & Credentials (SPEC-320)
- **UAT-320-04**: Plaintext key not in on-disk config ✅
- **UAT-320-06**: Mixed op:// and plaintext resolved correctly ✅
- **UAT-320-07**: Project config validation rejects missing keys ✅

### Session Registry (SPEC-324)
- **UAT-324-NEG-01**: Missing registry → empty dict ✅
- **UAT-324-NEG-02**: Corrupted JSON → recovered as empty ✅
- **UAT-324-NEG-03**: Path traversal via branch name → dict key (harmless) ✅
- **UAT-324-08**: File permissions 0600 ✅

### End-to-End (ADR-046/047)
- **E2E**: Watchdog → Bridge → Zulip chat plugin connected ✅
- **E2E**: Worktree discovery (no auto-spawn sessions — fixed) ✅
- **E2E**: Plugin crash detection (Zulip plugin killed, bridge detected) ✅
- **E2E**: Message sent to Zulip stream ✅
- **E2E**: Plugin stderr forwarded to bridge log at INFO level ✅

## Bugs Found and Fixed

1. **Bridge subprocess had no `__main__` guard** — `python -m` executed silently
2. **Worktree discovery auto-spawned runtime sessions** — changed to emit events only, sessions created on `/work`
3. **Plugin subprocess commands used bare entry point names** — changed to `sys.executable -m <module>`
4. **Bridge log was empty** — stdout/stderr redirected to log file instead of PIPE
5. **CLI `read_pid_file` read entire file** — changed to `head -1` for new PID format
6. **Plugin stderr logged at DEBUG** — changed to INFO so plugin output visible in logs
7. **Watchdog didn't resolve `op://` credentials** — added `load_helm_config()` to resolve once at startup
8. **Bridge had no `run()` method** — added `run()` method that awaits chat plugin reader

## Not Yet Tested (Requires Live Zulip Interaction)

- UAT-325-02 through UAT-325-08 (chat message routing, /work, /cancel, /approve, /deny)
- UAT-318-04 (PID reuse detection)
- UAT-318-05 (config removal stops bridge)
- UAT-318-06 (SIGINT graceful shutdown — partially tested)
- UAT-318-07 (daemon mode)
- UAT-320-01 through UAT-320-03 (op:// live resolution)
- UAT-321 (opencode discovery — needs opencode on port 4098)
- UAT-322-03 through UAT-322-09 (plugin protocol, scoped config)
- ADR acceptance tests ACC-046-01 through ACC-047-07

## Known Gaps

- **Session auto-restart on death**: ADR-047 says dead sessions should restart; only detection is implemented
- **SHA-256 hash pinning** (ADR-038): Not implemented, deferred to v2
- **Config file permissions check** (ADR-038): Not enforced, deferred
- **Watchdog detects already-running bridge on restart**: Needs verification (ACC-047-05)