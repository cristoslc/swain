# Acceptance Tests: ADR-046, ADR-047, ADR-038 Architecture Constraints

These tests verify architectural constraints from the ADRs that transcend individual SPECs.

---

## ADR-046: Project-Level Microkernel Topology

### ACC-046-01: No hub routing of events

**Test:** Start two project bridges. Send a message to project A's stream. Verify project B's bridge does not receive it.

**Pass:** Cross-project isolation confirmed — bridges only see their own stream.

---

### ACC-046-02: One session per worktree (not auto-spawned)

**Test:** Start bridge with 3 existing worktrees. Check that NO runtime sessions are auto-spawned. Send `/work` for one branch, verify exactly one session starts.

**Pass:** Worktree tracking happens, but sessions only created on explicit operator command.

---

### ACC-046-03: Continuous worktree discovery runs in bridge, not watchdog

**Test:** Start watchdog and bridge. Check that `git worktree list` is called by the bridge process (pid matches bridge), not the watchdog.

**Pass:** Worktree polling is a bridge responsibility.

---

### ACC-046-04: Watchdog does not route events

**Test:** Start watchdog with bridge. Subscribe to Zulip events. Verify events flow bridge → chat plugin, not through watchdog.

**Pass:** Watchdog manages only process lifecycle (start/stop/restart), never sits in the event path.

---

### ACC-046-05: Watchdog crash does not kill bridges

**Test:**
1. Start watchdog with active bridge
2. `kill -9 <watchdog_pid>`
3. Check bridge still running
4. Restart watchdog
5. Verify watchdog detects existing bridge (PID file valid) and does not restart it

**Pass:** Bridges survive watchdog crash. Watchdog reconciles on restart.

---

### ACC-046-NEG-01: Two projects sharing one bot — no cross-talk

**Test:** Two bridges with same bot account, different streams. Send message to stream A. Verify bridge B does not emit a command.

**Pass:** Narrow stream filtering prevents cross-project message leakage.

---

## ADR-047: Watchdog Architecture

### ACC-047-01: Credential resolution once at startup

**Test:** Start watchdog with `op://` reference. Monitor `op read` calls. Verify exactly one invocation per unique reference.

**Pass:** One resolution per reference, cached for lifetime of process.

---

### ACC-047-02: Fail-fast if 1Password locked

**Test:** Sign out of 1Password. Start watchdog with `op://` references.

**Pass:** Watchdog exits immediately with clear error. No bridges started.

---

### ACC-047-03: Resolved secrets never on disk

**Test:** Start watchdog. Grep all files in `~/.config/swain-helm/` and log files for the resolved API key value.

**Pass:** No resolved secrets found on disk. Only op:// references in config files.

---

### ACC-047-04: 30-second reconciliation cycle

**Test:** Start watchdog. Time reconciliation cycles from log timestamps.

**Pass:** Cycles occur approximately every 30 seconds.

---

### ACC-047-05: Bridge survives watchdog restart

**Test:**
1. Start watchdog, wait for bridge
2. Stop watchdog gracefully
3. Check bridge still alive
4. Start watchdog again
5. Verify watchdog detects running bridge and does NOT double-start

**Pass:** No duplicate bridges. Watchdog reconciles existing state.

---

### ACC-047-06: Config change between cycles reconciled

**Test:**
1. Start watchdog with project A
2. Add project B config while watchdog is running
3. Wait for next cycle

**Pass:** Bridge B started within one cycle after config appears.

---

### ACC-047-07: Removed config between cycles reconciled

**Test:**
1. Start watchdog with projects A and B
2. Delete project A config
3. Wait for next cycle

**Pass:** Bridge A stopped within one cycle after config disappears.

---

### ACC-047-NEG-01: Per-port auth — no credential spraying

**Test:** Configure opencode discovery with credentials for port 4098 only. Start an opencode instance on port 5000.

**Pass:** Port 5000 is NOT authenticated against. Only port 4098 is probed.

---

## ADR-038: Microkernel Plugin Architecture

### ACC-038-01: NDJSON protocol on stdio

**Test:** Start a plugin subprocess. Verify ConfigMessage is first line on stdin (valid JSON). Subsequent lines are NDJSON Events or Commands.

**Pass:** Protocol conformance verified.

---

### ACC-038-02: Plugin receives scoped config only

**Test:** Start bridge with chat + runtime plugins. Intercept ConfigMessage sent to each. Verify chat plugin receives only `chat.*` config, runtime receives only `runtime.*` config.

**Pass:** No credential leakage across plugin boundaries.

---

### ACC-038-03: Plugin crash does not kill bridge

**Test:** Start bridge with chat plugin. Kill chat plugin subprocess. Verify bridge logs the crash and continues running (does not exit).

**Pass:** Bridge handles plugin death gracefully.

---

### ACC-038-04: stderr from plugin is logged, not mixed into stdout

**Test:** Start bridge with a plugin that writes to stderr. Check that stderr content appears in bridge DEBUG logs, not in the NDJSON protocol stream.

**Pass:** No protocol contamination from stderr output.

---

### ACC-038-05: BrokenPipeError handled on write

**Test:** Start bridge. Write to a plugin whose stdin is already closed. Verify BrokenPipeError is caught and logged, bridge does not crash.

**Pass:** Graceful degradation on pipe break.

---

### ACC-038-NEG-01: Config file permissions too open

**Test:** Create `helm.config.json` with permissions 644. Start watchdog.

**Pass:** (Spec says kernel should refuse — currently NOT implemented, should be noted as gap)

---

### ACC-038-NEG-02: SHA-256 content hash pinning

**Test:** (Spec says kernel checks content hash — currently NOT implemented, noted as v2 feature gap)