# UAT: SPEC-324 — Session Registry Persistence

## Prerequisites

- Project with `.swain/swain-helm/` directory writable
- Bridge running with sessions

---

## UAT-324-01: State transition writes to registry

**Steps:**
1. Start bridge, create a session via `/work`
2. Check `<project>/.swain/swain-helm/session-registry.json`

**Expected:** Entry written with correct `opencode_session_id`, `state`, `topic`, `worktree_path`
**Actual:**

---

## UAT-324-02: Registry keyed by branch name

**Steps:**
1. Create session for branch "feature-x"
2. Read registry file

**Expected:** Key is "feature-x" (the branch/topic), not the session UUID
**Actual:**

---

## UAT-324-03: All required fields present

**Steps:**
1. Write a session to registry
2. Read registry file and check entry schema

**Expected:** Entry contains: `opencode_session_id`, `state`, `topic`, `worktree_path`, `artifact`, `started_at`, `last_activity`
**Actual:**

---

## UAT-324-04: Bridge reads registry on startup

**Steps:**
1. Write a registry file with a pre-existing entry
2. Start bridge
3. Check bridge log for registry read

**Expected:** Bridge reads existing entries, sessions are aware of prior state
**Actual:**

---

## UAT-324-05: Orphaned entries cleaned on startup reconciliation

**Steps:**
1. Write registry with an entry referencing a non-existent session ID
2. Start bridge with `reconcile()` called

**Expected:** Orphaned entry marked as "dead"
**Actual:**

---

## UAT-324-06: Dead entries cleaned up

**Steps:**
1. Write registry with entries where `state=dead` and worktree path no longer exists
2. Call `cleanup_dead()`

**Expected:** Dead/orphaned entries removed from registry
**Actual:**

---

## UAT-324-07: Atomic write via tmp+rename

**Steps:**
1. Create many rapid state transitions
2. Check registry file is never partially written (no `.tmp` files left)

**Expected:** Registry always contains valid JSON, no corrupted intermediate state
**Actual:**

---

## UAT-324-08: File permissions are 0600

**Steps:**
1. Trigger a registry write
2. Check file permissions

**Expected:** Registry file has permissions 0o600
**Actual:**

---

## UAT-324-NEG-01: Registry file is missing on first run

**Steps:**
1. Delete registry file
2. Start bridge

**Expected:** Bridge creates empty registry, no crash
**Actual:**

---

## UAT-324-NEG-02: Registry file is corrupted JSON

**Steps:**
1. Write garbage to registry file
2. Start bridge

**Expected:** Bridge logs warning, recovers with empty dict, continues running
**Actual:**

---

## UAT-324-NEG-03: Branch name with path traversal characters (dict key, not file path)

**Steps:**
1. Call `update_entry("../../etc/passwd", state="active")`
2. Read registry file and check key

**Expected:** Entry stored with `../../etc/passwd` as dict key — harmless since it's just a JSON key, not a file path. Actual file path is always `<project_dir>/.swain/swain-helm/session-registry.json`.
**Actual:** PASS

---

## UAT-324-NEG-04: Concurrent write (process killed mid-write)

**Steps:**
1. Start bridge writing registry
2. Kill bridge mid-write (SIGKILL)
3. Check registry file integrity

**Expected:** Either old or new content (atomic rename), never a partial write. `.tmp` file may exist but registry.json is intact.
**Actual:**