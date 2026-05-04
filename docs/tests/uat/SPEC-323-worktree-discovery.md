# UAT: SPEC-323 — Continuous Worktree Discovery

## Prerequisites

- Project with git worktrees
- Bridge running with worktree scanner active

---

## UAT-323-01: Scanner polls every 15 seconds

**Steps:**
1. Start bridge with `worktree_poll_interval_s=15`
2. Add a new worktree
3. Time how long before bridge detects it

**Expected:** New worktree detected within 15-20 seconds
**Actual:**

---

## UAT-323-02: New worktree emits worktree_added event

**Steps:**
1. Create a new worktree: `git worktree add .worktrees/test-branch`
2. Wait for next scan cycle
3. Check bridge log for "worktree_added" or session creation

**Expected:** Event emitted with correct path and branch name
**Actual:**

---

## UAT-323-03: Removed worktree emits worktree_removed event

**Steps:**
1. Remove a worktree: `git worktree remove .worktrees/test-branch`
2. Wait for scan cycle
3. Check bridge log

**Expected:** Event emitted, session marked dead
**Actual:**

---

## UAT-323-04: Existing worktree detected on startup

**Steps:**
1. Have 2 existing worktrees
2. Start bridge
3. Check initial scan results

**Expected:** Both worktrees detected in first scan, events emitted
**Actual:**

---

## UAT-323-05: No-op when worktree list unchanged

**Steps:**
1. Start bridge with stable worktree list
2. Wait 2 scan cycles (30s)
3. Check logs for unnecessary actions

**Expected:** No session creation or removal events on subsequent cycles
**Actual:**

---

## UAT-323-06: Configurable poll interval

**Steps:**
1. Set `worktree_poll_interval_s=5` in project config
2. Start bridge
3. Time scan intervals

**Expected:** Scans occur approximately every 5 seconds
**Actual:**

---

## UAT-323-NEG-01: git worktree list fails (not a git repo)

**Steps:**
1. Configure project with `path: /tmp` (no git repo)
2. Start bridge

**Expected:** Scanner logs error but bridge continues running (graceful degradation)
**Actual:**

---

## UAT-323-NEG-02: git not on PATH

**Steps:**
1. Remove git from PATH temporarily
2. Start bridge with valid project path

**Expected:** Scanner fails gracefully, bridge continues without worktree tracking
**Actual:**

---

## UAT-323-NEG-03: Worktree with detached HEAD

**Steps:**
1. Create a worktree in detached HEAD state (`git worktree add --detach`)
2. Wait for scan

**Expected:** Worktree detected, branch name may be empty or "detached" — bridge should not crash
**Actual:**

---

## UAT-323-NEG-04: Branch name with special characters

**Steps:**
1. Create worktree with branch name `feature/fix-#123`
2. Wait for scan

**Expected:** Worktree detected, branch name captured correctly (slashes, hash handled)
**Actual:**

---

## UAT-323-NEG-05: Worktree created and removed within scan interval

**Steps:**
1. Create worktree
2. Immediately remove it (< 15s)
3. Wait for next scan

**Expected:** Worktree never appears in scan results, no session created, no error
**Actual:**

---

## UAT-323-NEG-06: Scanner returns last-known on failure

**Steps:**
1. Start bridge with valid git project
2. After initial scan, make `git worktree list` fail (e.g., corrupt .git/HEAD)
3. Wait for scan cycle

**Expected:** Scanner returns last-known worktree set instead of empty set, sessions preserved
**Actual:**