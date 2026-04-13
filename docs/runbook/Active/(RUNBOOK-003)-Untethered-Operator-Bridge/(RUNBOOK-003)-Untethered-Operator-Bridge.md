---
title: "Untethered Operator Bridge"
artifact: RUNBOOK-003
track: standing
status: Active
mode: manual
trigger: on-demand
author: cristos
created: 2026-04-07
last-updated: 2026-04-07
validates:
  - SPEC-291
  - SPEC-292
parent-epic: ""
depends-on-artifacts:
  - DESIGN-025
linked-artifacts:
  - VISION-006
  - ADR-037
  - ADR-038
---

# Untethered Operator Bridge

## Purpose

Start the untethered operator bridge so you can interact with swain from Zulip. The bridge connects your Zulip channel to an opencode session running on your machine. You can also attach a local TUI to the same session.

## Prerequisites

- `opencode` CLI installed (`brew install opencode` or see opencode.ai).
- `uv` installed for Python dependency management.
- A Zulip account with a bot configured (see Security Domain Setup below).
- The swain project checked out.

---

## Quick Start

### 1. Start the opencode server

```bash
opencode serve --port 4097
```

Leave this running. It manages LLM sessions and persists chat history.

### 2. Start the bridge

```bash
cd /path/to/swain
uv run untethered-host --domain personal --verbose
```

The bridge connects to Zulip and routes messages to the opencode server. You should see:

```
Host kernel running — domain: personal, projects: ['swain']
Starting Zulip message poll...
```

### 3. Send a message in Zulip

Go to your Zulip instance, open the `#swain > control` topic, and type a message. The bridge picks it up, sends it to opencode, and posts the response back.

### 4. Attach locally (optional)

While the bridge is running, you can connect a full TUI to the same session:

```bash
opencode attach http://127.0.0.1:4097
```

You see the same conversation the bot is having. You can type directly.

---

## Quick Start (Daemon Mode)

To run the bridge in the background so you can keep using the terminal:

```bash
# Start in daemon mode
./bin/swain-bridge --daemon

# Check status anytime
./bin/swain-bridge --status

# Stop when done
./bin/swain-bridge --stop
```

Logs are written to `/tmp/swain-bridge.log`.

---

## Security Domain Setup

The bridge reads credentials from `~/.config/swain/domains/<name>.json`. Create one:

```bash
mkdir -p ~/.config/swain/domains
cat > ~/.config/swain/domains/personal.json << 'EOF'
{
  "domain": "personal",
  "chat": {
    "server_url": "https://YOUR-ORG.zulipchat.com",
    "bot_email": "your-bot@YOUR-ORG.zulipchat.com",
    "bot_api_key": "YOUR_BOT_API_KEY",
    "operator_email": "you@YOUR-ORG.zulipchat.com",
    "control_topic": "control"
  },
  "projects": [
    {
      "name": "your-project",
      "path": "/path/to/your/project",
      "stream": "your-zulip-stream",
      "runtime": "opencode"
    }
  ]
}
EOF
chmod 600 ~/.config/swain/domains/personal.json
```

The bot must be subscribed to the Zulip stream. Subscribe it in your Zulip admin panel or via the API.

---

## OpenCode Provider Setup

Configure the LLM provider in `~/.config/opencode/opencode.json`. Example for Ollama Cloud:

```json
{
  "model": "ollama-cloud/gemma4:31b-cloud",
  "provider": {
    "ollama-cloud": {
      "name": "Ollama Cloud",
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "https://ollama.com/v1" },
      "models": {
        "gemma4:31b-cloud": { "name": "Gemma 4 31B" }
      }
    }
  }
}
```

---

## Slash Commands

In the Zulip `control` topic:

| Command | Effect |
|---------|--------|
| Plain text | Sends to the current opencode session. Response posts back to control. |
| `/work <text>` | Starts the launcher interview flow. Creates a dedicated thread after setup. |
| `/session <text>` | Same as `/work`. |
| `/cancel` | Stops the current session. |
| `/kill <session>` | Stops a named session. |

## Options

| Option | Effect |
|--------|--------|
| `--daemon` | Run in background (detached from terminal) |
| `--stop` | Stop running daemon |
| `--status` | Show daemon status and health |
| `--domain NAME` | Security domain (default: personal) |
| `--port N` | opencode serve port (default: 4097) |
| `--verbose` | Enable debug logging |

---

## Troubleshooting

### Bridge starts but no messages come through

- Check that the bot is subscribed to the Zulip stream.
- Messages sent before the bridge starts are lost. Send a new one.
- Check `cat /tmp/untethered.log` for errors.

### "opencode serve not reachable"

- Start the server: `opencode serve --port 4097`.
- Check `curl http://127.0.0.1:4097/global/health`.

### Typing indicator stays on

- It auto-expires after 15 seconds if the bridge crashes.
- If the session is still processing, wait for the response.

### Responses are slow

- The LLM provider determines speed. Ollama Cloud models vary.
- The bridge adds a 2-second batching delay to coalesce output lines.

### Daemon won't start

- Check if already running: `swain-bridge --status`
- Check logs: `tail -f /tmp/swain-bridge.log`
- Stale PID file: `rm /tmp/swain-bridge.pid` and try again

### Daemon stops unexpectedly

- Check logs: `tail -f /tmp/swain-bridge.log`
- Verify opencode serve is installed: `which opencode`
- Verify domain config exists: `cat ~/.config/swain/domains/personal.json`

---

## Stopping

1. Stop the bridge: `Ctrl-C` in the bridge terminal, or `kill $(pgrep -f untethered-host)`.
2. Stop the opencode server: `Ctrl-C` in the server terminal, or `curl -X POST http://127.0.0.1:4097/global/dispose`.
3. Sessions persist on disk. Restarting the server recovers prior sessions.
