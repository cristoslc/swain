# UAT: SPEC-322 — Project Bridge Microkernel Refactor

## Prerequisites

- swain-helm installed with all entry points
- Valid Zulip credentials in helm config
- Project configured

---

## UAT-322-01: Bridge spawns chat plugin as subprocess

**Steps:**
1. Start bridge process (manually via stdin config or through watchdog)
2. Check running processes

**Expected:** `swain_helm.plugins.zulip_chat` subprocess is running (or `swain-helm-zulip-chat`)
**Actual:**

---

## UAT-322-02: Chat plugin receives ConfigMessage on stdin

**Steps:**
1. Start bridge
2. Check bridge log for "Plugin started: chat:<name>"

**Expected:** Chat plugin started and received config via ConfigMessage
**Actual:**

---

## UAT-322-03: ConfigMessage contains only scoped credentials

**Steps:**
1. Start bridge with multiple projects configured
2. Check chat plugin config sent via ConfigMessage

**Expected:** Chat plugin receives only its own stream + bot credentials, not other projects' configs
**Actual:**

---

## UAT-322-04: Runtime adapter spawned as subprocess on /work

**Steps:**
1. Start bridge with Zulip connection active
2. Send `/work` command to control topic
3. Check bridge log for "Plugin started: runtime:sess-*"

**Expected:** Runtime adapter subprocess spawned
**Actual:**

---

## UAT-322-05: Runtime adapter receives scoped config

**Steps:**
1. Start a session via `/work`
2. Check runtime adapter config in bridge log

**Expected:** Runtime adapter receives only session-specific config (session_id, project_dir, base_url)
**Actual:**

---

## UAT-322-06: Adapter crash detected by PluginProcess

**Steps:**
1. Start bridge
2. Kill chat plugin subprocess manually
3. Check bridge log

**Expected:** Bridge detects "stdout closed" or process exit, logs warning
**Actual:**

---

## UAT-322-07: Non-NDJSON from adapter handled gracefully

**Steps:**
1. Start bridge with a mock adapter that writes invalid JSON
2. Check bridge log

**Expected:** Invalid line is logged as warning, bridge does not crash
**Actual:**

---

## UAT-322-08: Old kernel files are deleted

**Steps:**
1. Search for `kernel.py`, `bridges/host.py`, `main.py`, `runtime_state.py`, `plugins/project_bridge.py`
2. None should exist in src/

**Expected:** All old architecture files deleted
**Actual:**

---

## UAT-322-09: Console scripts registered in pyproject.toml

**Steps:**
1. `uv run python -c "import importlib.metadata; ..."`
2. Check that `swain-helm-zulip-chat`, `swain-helm-opencode`, `swain-helm-claude`, `swain-helm-tmux` are registered

**Expected:** All four console_scripts entry points present
**Actual:**

---

## UAT-322-NEG-01: Bridge receives malformed ConfigMessage

**Steps:**
1. Start bridge subprocess
2. Send non-ConfigMessage JSON on stdin

**Expected:** Bridge exits with error "Expected ConfigMessage on stdin"
**Actual:**

---

## UAT-322-NEG-02: Bridge receives empty stdin

**Steps:**
1. Start bridge subprocess
2. Close stdin immediately without sending config

**Expected:** Bridge exits with error "No config received on stdin"
**Actual:**