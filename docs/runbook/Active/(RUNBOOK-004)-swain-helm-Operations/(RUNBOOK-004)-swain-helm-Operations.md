---
title: "swain-helm Operations"
artifact: RUNBOOK-004
track: standing
status: Active
mode: manual
trigger: on-demand
author: cristos
created: 2026-04-18
last-updated: 2026-04-24
validates:
  - SPEC-318
  - SPEC-319
  - SPEC-329
parent-epic: EPIC-084
depends-on-artifacts:
  - ADR-047
linked-artifacts:
  - VISION-006
  - ADR-046
  - ADR-047
  - TRAIN-001
---

## Purpose

Start and manage the swain-helm bridge system so you can interact with agent sessions from Zulip on any device.

## Prerequisites

- Docker and Docker Compose installed.
- opencode CLI installed (bundled in the Docker image).
- A Zulip organization with a bot account and API key.
- The `swain-test-config` Docker volume containing `helm.config.json`.
- Projects registered in `helm.config.json` under `~/.config/swain-helm/`.

## Steps

### 1. Start the bridge

**Action:** Run docker compose with required environment variables:

```bash
PROJECT_PATH="$(pwd)" \
PROJECT_NAME=swain \
ZULIP_BOT_EMAIL="swain-helm-bot@cristoslc.zulipchat.com" \
ZULIP_BOT_API_KEY="<your-api-key>" \
ZULIP_SITE="https://cristoslc.zulipchat.com" \
ZULIP_OPERATOR_EMAIL="operator@example.com" \
docker compose up -d
```

**Expected:** Container `swain-helm-watchdog` starts. Logs show: "OpenCode server healthy on port 4098" then "Bridge swain-test started (pid XX)".

**Pass criteria:** `docker ps` shows container status `Up (healthy)`.

### 2. Verify Zulip connectivity

**Action:** Send a message in Zulip #\<project\> > trunk topic.

**Expected:** Bot processes the message. `docker logs swain-helm-watchdog` shows "Zulip message → send_prompt (bridge=swain)".

**Pass criteria:** Message appears in container logs as a received command.

### 3. Check status

**Action:** `docker ps --filter name=swain-helm-watchdog` and `docker logs swain-helm-watchdog --tail 50`.

**Expected:** Container healthy, bridge PID active, opencode server on port 4098.

### 4. Rebuild after code changes

**Action:** Stop, rebuild, and relaunch:

```bash
docker stop swain-helm-watchdog && docker rm swain-helm-watchdog

PROJECT_PATH="$(pwd)" \
PROJECT_NAME=swain \
ZULIP_BOT_EMAIL="swain-helm-bot@cristoslc.zulipchat.com" \
ZULIP_BOT_API_KEY="<your-api-key>" \
ZULIP_SITE="https://cristoslc.zulipchat.com" \
ZULIP_OPERATOR_EMAIL="operator@example.com" \
docker compose build --no-cache

PROJECT_PATH="$(pwd)" \
PROJECT_NAME=swain \
ZULIP_BOT_EMAIL="swain-helm-bot@cristoslc.zulipchat.com" \
ZULIP_BOT_API_KEY="<your-api-key>" \
ZULIP_SITE="https://cristoslc.zulipchat.com" \
ZULIP_OPERATOR_EMAIL="operator@example.com" \
docker compose up -d
```

**Expected:** Fresh image built from local code, container restarts healthy.

**Pass criteria:** `docker logs` shows the new code (check log timestamps or new log messages).

### 5. Approve or deny a permission request

**Action:** When the bot posts a permission request in Zulip, reply with `/approve <call_id>` or `/deny <call_id>`.

**Expected:** The permission is resolved. The runtime continues (approve) or stops (deny).

**Pass criteria:** Bot acknowledges the approval/denial in the Zulip topic.

### 6. Shut down

**Action:** `docker stop swain-helm-watchdog && docker rm swain-helm-watchdog`.

**Expected:** Bridge processes stopped, container removed. Session data persists in project `.swain` directories on the host.

## Teardown

`docker compose down` stops and removes the container. The `swain-test-config` volume is preserved (contains `helm.config.json`). To destroy the volume too, add `--volumes`.

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| "No messages in Zulip" | Check bot is subscribed to stream. Verify `ZULIP_BOT_API_KEY` env var matches the bot's active key. Check `docker logs` for auth errors. |
| "Bridge goes silent after a few minutes" | Zulip event queue expired. The reconnection loop should recover automatically. If not, check logs for "Zulip poll failed after 10 attempts" and restart the container. |
| "Typing indicator not showing" | Verify `TypingIndicator` is the real implementation (has `_pulse` and `_send_typing`), not the no-op stub. Check logs for "Typing indicator error". |
| "Permission requests not appearing" | Check `docker logs` for `approval_needed` events. Verify the bot has permission to post in the stream. |
| "opencode serve not found" | Check opencode is bundled in the Docker image. Verify port 4098 is accessible: `curl localhost:4098/healthz`. |
| "Config not found inside container" | Check `swain-test-config` volume exists: `docker volume inspect swain-test-config`. The volume must contain `helm.config.json` under `/root/.config/swain-helm/`. |
| "1Password vault reference not resolving" | Inside Docker, `op` CLI is unavailable. Config falls back to env vars like `SWAIN_HELM_CHAT_BOT_API_KEY`. Use vault UUID instead of name in `op://` references for host-side resolution. |

## Known Issues

- **Zulip queue expiration**: The Zulip SDK's `call_on_each_event` does not auto-reconnect when the event queue expires. The reconnection loop in `_poll_zulip` handles this with exponential backoff (up to 10 attempts, max 60s delay).
- **Watchdog doesn't restart dead bridges (SPEC-330)**: If a bridge subprocess dies, the watchdog does not currently restart it. Restart the container manually.

## Run Log

| Date | Operator | Result | Duration | Notes |
|------|----------|--------|----------|-------|
| 2026-04-24 | cristos | Pass | 5m | Docker rebuild with reconnection fix, permission surfacing, typing indicator restoration |
| 2026-04-18 | cristos | - | - | Template created |

## Lifecycle

| Status | Date | Until | Note |
|--------|------|-------|------|
| Active | 2026-04-18 | -- | Replaces RUNBOOK-003. Updated 2026-04-24 for Docker workflow, SPEC-329, typing indicator. |