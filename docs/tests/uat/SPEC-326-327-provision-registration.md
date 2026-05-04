# UAT: SPEC-326 — Host Provision Command / SPEC-327 — Multi-Project Registration

---

## SPEC-326 Tests

### UAT-326-01: Provision writes helm.config.json

**Steps:**
1. `swain-helm host provision --zulip-site https://cristoslc.zulipchat.com --zulip-email swain-bot@cristoslc.zulipchat.com --zulip-api-key <KEY> --operator-email cristos@cristoslc.com --project swain --project-path /path/to/swain`
2. Check `helm.config.json` exists

**Expected:** `helm.config.json` written with correct structure
**Actual:**

---

### UAT-326-02: Credentials stored as op:// references

**Steps:**
1. Check `helm.config.json` content

**Expected:** `bot_api_key` value is `op://...` reference, not plaintext
**Actual:**

---

### UAT-326-03: Zulip stream created with welcome message

**Steps:**
1. Run provision with valid Zulip credentials
2. Check Zulip stream for the welcome message

**Expected:** Stream exists, welcome message posted to "control" topic listing available commands
**Actual:**

---

### UAT-326-04: Config file permissions are 600

**Steps:**
1. Check `helm.config.json` permissions

**Expected:** File mode 0o600
**Actual:**

---

### UAT-326-05: Per-project config written under projects/

**Steps:**
1. Run provision
2. Check `~/.config/swain-helm/projects/swain.json`

**Expected:** Project config file written with name, path, stream, runtime, auto_start, worktree_poll_interval_s
**Actual:**

---

### UAT-326-06: --config-dir flag overrides default location

**Steps:**
1. `swain-helm host provision --config-dir /tmp/test-config ...`
2. Check `/tmp/test-config/helm.config.json`

**Expected:** Config written to custom directory
**Actual:**

---

### UAT-326-NEG-01: Invalid Zulip credentials

**Steps:**
1. Run provision with wrong API key

**Expected:** "Zulip auth failed" error, process exits with non-zero code, no config files written
**Actual:**

---

### UAT-326-NEG-02: Missing required flags

**Steps:**
1. Run provision with `--project` missing

**Expected:** argparse error listing required arguments
**Actual:**

---

### UAT-326-NEG-03: Stream already exists

**Steps:**
1. Run provision when stream "swain" already exists

**Expected:** Idempotent — `add_subscriptions` succeeds even for existing stream
**Actual:**

---

## SPEC-327 Tests

### UAT-327-01: Second project added without affecting first

**Steps:**
1. Provision "swain" project
2. Provision "other-project" project
3. Check first project's bridge still runs

**Expected:** Both project configs exist, first bridge unaffected
**Actual:**

---

### UAT-327-02: New project bridge connects to same Zulip server

**Steps:**
1. Add second project "other" via `project add`
2. Start watchdog
3. Check second bridge connects to Zulip with its own stream

**Expected:** Two bridges running, each subscribed to its own stream with narrow filter
**Actual:**

---

### UAT-327-NEG-01: Duplicate project name

**Steps:**
1. `swain-helm project add /path/to/swain` (already registered)
2. Run again

**Expected:** Second attempt reports "already registered", exits 0
**Actual:**

---

### UAT-327-NEG-02: Project add without .git/ directory

**Steps:**
1. `swain-helm project add /tmp` (no .git/)

**Expected:** Rejected with error message
**Actual:**

---

### UAT-327-NEG-03: Zulip API unreachable during provision

**Steps:**
1. Run provision with unreachable Zulip server URL

**Expected:** Auth fails, process exits with error before writing config
**Actual:**