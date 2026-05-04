# UAT: SPEC-318 — Watchdog Core

## Prerequisites

- swain-helm installed in venv (`uv pip install -e .`)
- `helm.config.json` at `~/.config/swain-helm/` with valid Zulip creds (port 4098)
- At least one project config in `~/.config/swain-helm/projects/`
- Clean state: no running watchdog or bridges

---

## UAT-318-01: Watchdog reads project configs on startup

**Steps:**
1. Write two project configs to `~/.config/swain-helm/projects/` (alpha.json, beta.json) with `auto_start: true`
2. Start watchdog in foreground: `uv run python -m swain_helm.watchdog`
3. Wait 5 seconds, check bridge PID files

**Expected:** Two bridge PID files exist: `run/bridges/alpha.pid` and `run/bridges/beta.pid`
**Actual:**

---

## UAT-318-02: Watchdog skips auto_start=false projects

**Steps:**
1. Write one project config with `auto_start: false` (manual.json)
2. Start watchdog, wait one cycle

**Expected:** No `run/bridges/manual.pid` file created
**Actual:**

---

## UAT-318-03: Stale PID file triggers bridge restart

**Steps:**
1. Write a project config for "stale" with `auto_start: true`
2. Manually create `run/bridges/stale.pid` with a PID that does not exist (e.g., "999999\n0.0\n")
3. Start watchdog, wait one reconciliation cycle

**Expected:** Stale PID file is unlinked and replaced with a valid PID for the new bridge process
**Actual:**

---

## UAT-318-04: PID reuse detection

**Steps:**
1. Find a long-running process PID (e.g., `ps -p 1 -o pid=`)
2. Write `run/bridges/reused.pid` with that PID but a wrong start time (e.g., "1\n1000000000.0\n")
3. Start watchdog, wait one cycle

**Expected:** PID file is detected as reused (start time mismatch), unlinked, and bridge is restarted
**Actual:**

---

## UAT-318-05: Removing project config stops bridge

**Steps:**
1. Start watchdog with project "alpha" active
2. Wait for bridge to start (PID file exists, process alive)
3. Delete `~/.config/swain-helm/projects/alpha.json`
4. Wait for next reconciliation cycle (30s)

**Expected:** Bridge process is terminated, PID file removed
**Actual:**

---

## UAT-318-06: Graceful shutdown on SIGINT

**Steps:**
1. Start watchdog in foreground with an active bridge
2. Send SIGINT (Ctrl-C)
3. Check processes after shutdown

**Expected:** All bridge subprocesses terminated, watchdog PID file removed
**Actual:**

---

## UAT-318-07: Daemon mode writes watchdog.pid

**Steps:**
1. Start watchdog with `--daemon` flag
2. Check `run/watchdog.pid` exists and PID is alive
3. Kill watchdog via PID file

**Expected:** Daemon forks to background, PID file written, process alive until killed
**Actual:**

---

## UAT-318-08: Zero project configs — no crash

**Steps:**
1. Remove all project configs from `projects/`
2. Start watchdog, wait one cycle

**Expected:** Watchdog cycles harmlessly, no bridges started, no errors
**Actual:**

---

## UAT-318-09: Malformed project config is skipped

**Steps:**
1. Write `projects/bad.json` with content `not json{}`
2. Write `projects/good.json` with valid config
3. Start watchdog, wait one cycle

**Expected:** "good" bridge starts, "bad" is skipped with error log, watchdog does not crash
**Actual:**

---

## UAT-318-10: Bridge subprocess output goes to log file

**Steps:**
1. Start watchdog with an active project
2. Wait for bridge to start
3. Check `run/bridges/<name>.log`

**Expected:** Log file contains bridge startup messages (non-empty)
**Actual:**

---

## UAT-318-NEG-01: Watchdog start when already running

**Steps:**
1. Start watchdog
2. Attempt to start a second watchdog instance

**Expected:** Second instance detects existing PID file, reports "already running" or exits gracefully
**Actual:**

---

## UAT-318-NEG-02: Bridge process exits immediately

**Steps:**
1. Temporarily move `swain_helm/bridges/project.py` to make it non-executable
2. Start watchdog, wait one cycle

**Expected:** Bridge fails to start, error logged, watchdog continues cycling
**Actual:**

---

## UAT-318-NEG-03: Config dir does not exist

**Steps:**
1. Set `--config-dir` to a non-existent path
2. Start watchdog

**Expected:** Watchdog creates config dir structure on startup, does not crash
**Actual:**