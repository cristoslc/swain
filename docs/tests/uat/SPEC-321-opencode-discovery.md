# UAT: SPEC-321 — OpenCode Serve Discovery and Auth

## Prerequisites

- opencode installed and on PATH
- Port 4098 available (not in use by real opencode server)
- swain-helm configured with `default_port: 4098`

---

## UAT-321-01: Discovery finds running opencode instance

**Steps:**
1. Start `opencode serve --port 4098` in background
2. Run discovery scanner
3. Check instance state

**Expected:** Instance on port 4098 marked as healthy and auth-tested
**Actual:**

---

## UAT-321-02: Discovery starts opencode when none running

**Steps:**
1. Ensure no opencode serve on port 4098
2. Run discovery scanner with `start_if_needed=True`
3. Check that opencode was started

**Expected:** `opencode serve` spawned on port 4098, marked as `started_by_bridge=true`
**Actual:**

---

## UAT-321-03: Auth mismatch detected

**Steps:**
1. Start opencode serve on port 4098 with different auth credentials
2. Run discovery with mismatched credentials in config

**Expected:** Instance marked as `auth_mismatch`, no alternative credentials attempted on that port
**Actual:**

---

## UAT-321-04: Unconfigured port is never authenticated against

**Steps:**
1. Start opencode serve on port 5000 (not in config)
2. Run discovery with config only listing port 4098

**Expected:** Port 5000 is not probed for auth
**Actual:**

---

## UAT-321-05: Health check works via HTTP

**Steps:**
1. Start opencode serve on port 4098
2. Call `health_check_async()` on port 4098

**Expected:** Returns True
**Actual:**

---

## UAT-321-06: Auth test succeeds with valid credentials

**Steps:**
1. Start opencode serve on port 4098
2. Call `auth_test_async()` with correct credentials

**Expected:** Returns True
**Actual:**

---

## UAT-321-NEG-01: opencode serve fails to start (binary missing)

**Steps:**
1. Remove opencode from PATH
2. Run discovery with `start_if_needed=True` on an empty port

**Expected:** Error logged, bridge continues without a runtime instance
**Actual:**

---

## UAT-321-NEG-02: Port already in use by non-opencode process

**Steps:**
1. Start a simple HTTP server on port 4098 (`python -m http.server 4098`)
2. Run discovery

**Expected:** Health check fails (wrong response format), instance not used
**Actual:**

---

## UAT-321-NEG-03: opencode serve crashes immediately after start

**Steps:**
1. Mock opencode to exit immediately after starting
2. Run discovery with `start_if_needed=True`

**Expected:** Start attempted, failure detected and logged, instance not used
**Actual:**

---

## UAT-321-NEG-04: Loopback URL validation

**Steps:**
1. Try to scan a non-loopback URL (e.g., `http://192.168.1.1:4098`)
2. Check `_validate_loopback_url` result

**Expected:** Non-loopback URL rejected
**Actual:**