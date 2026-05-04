# UAT: SPEC-325 — Chat Adapter Stream Filtering

## Prerequisites

- Two Zulip streams: "swain" and "other-project"
- Bridge for "swain" running
- Valid Zulip bot credentials

---

## UAT-325-01: Chat adapter subscribes to project stream only

**Steps:**
1. Start bridge for project "swain"
2. Check Zulip chat plugin log for narrow filter

**Expected:** Narrow filter is `[["stream", "swain"]]` — only the swain stream
**Actual:**

---

## UAT-325-02: Messages in worktree topic routed to session

**Steps:**
1. Have a session for branch "feature-x"
2. Send a Zulip message to stream "swain", topic "feature-x"
3. Check bridge log

**Expected:** Message routed as `send_prompt` with `session_id` matching the branch session
**Actual:**

---

## UAT-325-03: Messages in control topic routed as control_message

**Steps:**
1. Send a Zulip message to stream "swain", topic "control"
2. Check bridge log

**Expected:** Message routed as `control_message` to the project bridge
**Actual:**

---

## UAT-325-04: /work command in control topic creates session

**Steps:**
1. Send "/work SPEC-001" to stream "swain", topic "control"
2. Check bridge log for session creation

**Expected:** Session started with artifact "SPEC-001"
**Actual:**

---

## UAT-325-05: /cancel command cancels session

**Steps:**
1. Have an active session
2. Send "/cancel" in the session's topic
3. Check bridge log

**Expected:** Session state set to DEAD, runtime plugin stopped
**Actual:**

---

## UAT-325-06: /approve and /deny commands

**Steps:**
1. Session in "waiting_approval" state
2. Send "/approve <call_id>" in the session topic
3. Check session state

**Expected:** Session returns to "active" state, approval sent to runtime
**Actual:**

---

## UAT-325-07: Bot ignores its own messages

**Steps:**
1. Bridge posts a message to Zulip
2. Check that the bridge does not react to its own message

**Expected:** Bot's own messages filtered by `sender_email == client.email`
**Actual:**

---

## UAT-325-08: Deduplication of seen message IDs

**Steps:**
1. Send a Zulip message
2. Bridge reads it twice (if re-polling)
3. Check that the command is only emitted once

**Expected:** Seen IDs tracked, duplicate messages dropped
**Actual:**

---

## UAT-325-NEG-01: Message in unknown topic (no matching session)

**Steps:**
1. Send a regular text message to stream "swain", topic "nonexistent-branch"
2. Check bridge log

**Expected:** Message routed as `send_prompt` with `session_id` = topic name (session may not exist yet, bridge handles gracefully)
**Actual:**

---

## UAT-325-NEG-02: No host-scope command handling in adapter

**Steps:**
1. Send "/clone" or "/init" in control topic
2. Check that chat adapter passes it through rather than handling it

**Expected:** No host-scope handling — command passed to bridge as-is (may result in "unknown command" log)
**Actual:**

---

## UAT-325-NEG-03: Private messages are ignored

**Steps:**
1. Send a private message to the bot
2. Check that bridge does not react

**Expected:** Private messages not received (narrow filter excludes them) or dropped
**Actual:**