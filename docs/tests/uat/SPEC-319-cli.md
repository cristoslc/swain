# UAT: SPEC-319 — CLI

## Prerequisites

- `bin/swain-helm` on PATH or invoked directly
- Clean state, no running watchdog

---

## UAT-319-01: host up starts watchdog daemon

**Steps:**
1. `swain-helm host up`
2. Check `run/watchdog.pid`

**Expected:** PID file exists, watchdog process running in background
**Actual:**

---

## UAT-319-02: host up --foreground runs in foreground

**Steps:**
1. `swain-helm host up --foreground` (in a subshell with timeout)
2. Check that the process is in the foreground (no daemon fork)

**Expected:** Process blocks in foreground, logging to terminal
**Actual:**

---

## UAT-319-03: host down stops watchdog and bridges

**Steps:**
1. Start watchdog with `host up`
2. Wait for bridge to start
3. `swain-helm host down`
4. Check all processes

**Expected:** Watchdog and all bridge processes terminated
**Actual:**

---

## UAT-319-04: host down --project stops single bridge

**Steps:**
1. Start watchdog with two projects (alpha, beta)
2. `swain-helm host down --project alpha`
3. Check processes

**Expected:** Alpha bridge stopped, beta bridge and watchdog still running
**Actual:**

---

## UAT-319-05: host status shows correct state

**Steps:**
1. Start watchdog, wait for bridge
2. `swain-helm host status`

**Expected:** Shows "watchdog: running" with PID, "bridges: <name> running" with PID, opencode health status
**Actual:**

---

## UAT-319-06: project add registers a git repo

**Steps:**
1. `swain-helm project add /Users/cristos/Documents/code/swain`
2. Check `~/.config/swain-helm/projects/swain.json`

**Expected:** Project config created with name "swain", correct path, stream "swain"
**Actual:**

---

## UAT-319-07: project add rejects non-git directory

**Steps:**
1. `swain-helm project add /tmp` (no .git/)

**Expected:** Error message: "not a git repository", exit code non-zero
**Actual:**

---

## UAT-319-08: project add rejects with idempotency

**Steps:**
1. `swain-helm project add /Users/cristos/Documents/code/swain` (already registered)
2. Run it again

**Expected:** Second invocation reports "already registered" and exits 0 (idempotent)
**Actual:**

---

## UAT-319-09: project remove deletes config

**Steps:**
1. Add a project
2. `swain-helm project remove --project swain`
3. Check `projects/swain.json` does not exist

**Expected:** Config file removed
**Actual:**

---

## UAT-319-10: project list shows all projects

**Steps:**
1. Add two projects
2. `swain-helm project list`

**Expected:** Both projects listed with status (running/stopped)
**Actual:**

---

## UAT-319-11: host provision writes config

**Steps:**
1. `swain-helm host provision` with required flags (using test config dir)
2. Check `helm.config.json`

**Expected:** Config written with `op://` references, permissions 600
**Actual:**

---

## UAT-319-NEG-01: host down when watchdog not running

**Steps:**
1. Ensure watchdog is stopped
2. `swain-helm host down`

**Expected:** Reports "not running", exits gracefully (no crash)
**Actual:**

---

## UAT-319-NEG-02: project remove non-existent project

**Steps:**
1. `swain-helm project remove --project nonexistent`

**Expected:** Reports "not found", exit code non-zero
**Actual:**

---

## UAT-319-NEG-03: project list with no projects

**Steps:**
1. Remove all project configs
2. `swain-helm project list`

**Expected:** Shows "(none)", exits 0
**Actual:**

---

## UAT-319-NEG-04: project add with path containing spaces

**Steps:**
1. Create `/tmp/test project/.git/`
2. `swain-helm project add "/tmp/test project"`

**Expected:** Project registered with correctly-escaped path
**Actual:**

---

## UAT-319-NEG-05: host status when watchdog is down

**Steps:**
1. Stop watchdog
2. `swain-helm host status`

**Expected:** Shows "watchdog: not running", does not crash
**Actual:**