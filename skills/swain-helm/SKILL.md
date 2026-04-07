---
name: swain-helm
description: "Start, stop, and monitor the untethered operator bridge (VISION-006). Routes Zulip messages to opencode serve so the operator can steer sessions from any device. Triggers on: 'helm', 'bridge', 'untethered', 'start bridge', 'stop bridge', 'helm status', 'helm logs', 'is the bridge running'."
user-invocable: true
license: MIT
allowed-tools: Bash, Read
metadata:
  short-description: Untethered operator bridge management
  version: 1.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# swain-helm

Manages the untethered operator bridge: starts opencode serve and the Zulip→opencode host bridge, monitors health, and tears it down cleanly.

## Locate the launcher

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
BRIDGE="$REPO_ROOT/bin/swain-bridge"
```

If not found at that path, glob for `**/bin/swain-bridge`.

## Runtime files

| File | Purpose |
|------|---------|
| `/tmp/swain-bridge.pid` | Two-line PID file: line 1 = opencode serve PID, line 2 = untethered-host PID. |
| `/tmp/swain-bridge.log` | Combined stdout/stderr from both processes in daemon mode. |
| `/tmp/opencode-serve.log` | opencode serve log in foreground mode (separate from bridge log). |

## Commands

### start (default / "start bridge" / "helm up")

Start the bridge in daemon mode so it survives terminal close:

```bash
bash "$BRIDGE" --daemon
```

Output confirms PIDs, log path, and the Zulip stream to use. If the bridge is already running, `--status` will show it — do not start a second instance.

### stop ("stop bridge" / "helm down" / "shut down bridge")

```bash
bash "$BRIDGE" --stop
```

Kills both the opencode serve process and the host bridge. Removes the PID file.

### status ("helm status" / "is the bridge running" / "bridge health")

```bash
bash "$BRIDGE" --status
```

Reports whether opencode serve and the host bridge are running, including the HTTP health check result.

### logs ("helm logs" / "show bridge logs" / "what is the bridge doing")

Tail the live log:

```bash
tail -50 /tmp/swain-bridge.log
```

For continuous streaming, tell the operator to run `tail -f /tmp/swain-bridge.log` in their terminal — this skill does not block on streaming output.

### restart ("restart bridge" / "helm restart")

Stop then start:

```bash
bash "$BRIDGE" --stop && bash "$BRIDGE" --daemon
```

### foreground ("helm foreground" / "bridge in foreground" / "interactive bridge")

The default mode when no flags are given — backward compatible. Start attached to the terminal; Ctrl-C stops both processes cleanly:

```bash
bash "$BRIDGE"
```

Logs go to `/tmp/opencode-serve.log` (opencode) and stdout (bridge). Use this for debugging or first-run verification.

## Options

Pass through any supported flags from the operator:

| Flag | Default | Purpose |
|------|---------|---------|
| `--domain NAME` | `personal` | Security domain for the kernel. |
| `--port N` | `4097` | opencode serve port. |
| `--verbose` | off | Enable debug logging in the host bridge. |

Example: `helm start --domain work --port 4098`

## After starting

Show the operator:
1. Bridge status (from `--status` output).
2. How to attach: `opencode attach http://127.0.0.1:<PORT>`.
3. Zulip stream to use for sending prompts.
4. Log path for monitoring: `/tmp/swain-bridge.log`.

## Error handling

- If `bin/swain-bridge` is not found, tell the operator the untethered package may not be installed and point to RUNBOOK-003.
- If opencode serve fails the health check after start, show the last 20 lines of `/tmp/opencode-serve.log`.
- Never fail silently — always report what was attempted and what failed.
