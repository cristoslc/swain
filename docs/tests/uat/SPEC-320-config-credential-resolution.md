# UAT: SPEC-320 — Config and Credential Resolution

## Prerequisites

- 1Password CLI (`op`) installed and authenticated
- Test vault with known `op://` reference
- swain-helm installed in venv

---

## UAT-320-01: op:// references resolved to plaintext

**Steps:**
1. Write `helm.config.json` with `bot_api_key: "op://Homelab/Zulip Bot - swain-helm/password"`
2. Start watchdog (which calls `load_helm_config`)
3. Check bridge subprocess receives resolved API key in config

**Expected:** Bridge logs show the resolved key, not the `op://` reference
**Actual:**

---

## UAT-320-02: Each op:// reference resolved exactly once

**Steps:**
1. Write config with the same `op://` reference in two places
2. Start watchdog with debug logging
3. Count `op read` invocations in logs

**Expected:** Only one `op read` call per unique reference (cached on second use)
**Actual:**

---

## UAT-320-03: Failed op:// reference causes exit

**Steps:**
1. Write config with invalid reference: `op://Nonexistent/item/field`
2. Start watchdog

**Expected:** Process exits with error naming the failed reference
**Actual:**

---

## UAT-320-04: Resolved credentials never written to disk

**Steps:**
1. Start watchdog with valid `op://` config
2. Search all files under `~/.config/swain-helm/` for the resolved API key string
3. Check bridge log files for the resolved key

**Expected:** Resolved key not found in any on-disk file (only in process memory)
**Actual:**

---

## UAT-320-05: Resolved credentials not in log output

**Steps:**
1. Start watchdog with valid `op://` references
2. Grep all log files for the resolved secret value

**Expected:** No resolved secret value appears in any log
**Actual:**

---

## UAT-320-06: Mixed plaintext and op:// values

**Steps:**
1. Write config where `server_url` is plaintext and `bot_api_key` is `op://`
2. Load config via `load_helm_config`

**Expected:** `server_url` unchanged, `bot_api_key` resolved from 1Password
**Actual:**

---

## UAT-320-07: Project config validation rejects missing required keys

**Steps:**
1. Write project config missing `stream` key
2. Attempt to load via `load_project_config`

**Expected:** `ValueError` raised naming the missing key
**Actual:**

---

## UAT-320-08: Helm config validation rejects missing required keys

**Steps:**
1. Write `helm.config.json` missing `chat` key
2. Attempt to load via `load_helm_config`

**Expected:** `ValueError` raised naming the missing key
**Actual:**

---

## UAT-320-NEG-01: op CLI not on PATH

**Steps:**
1. Temporarily remove `op` from PATH
2. Start watchdog with `op://` in config

**Expected:** `ResolutionError` raised with clear message about op not being available
**Actual:**

---

## UAT-320-NEG-02: 1Password locked

**Steps:**
1. Sign out of 1Password (`op signout`)
2. Start watchdog with `op://` in config

**Expected:** Process exits with error indicating 1Password is locked
**Actual:**

---

## UAT-320-NEG-03: op read returns empty string

**Steps:**
1. Create a 1Password item with an empty field
2. Reference it in config
3. Load config

**Expected:** Empty string is returned (valid resolution, just empty value). Bridge may fail later if the credential is required.
**Actual:**

---

## UAT-320-NEG-04: Nested op:// in list values

**Steps:**
1. Write config with `scan_paths: ["op://vault/item/field"]`
2. Load config

**Expected:** The `op://` reference inside the list is resolved (walker handles lists)
**Actual:**