---
name: swain-helm
description: "Start, stop, and monitor the swain-helm bridge system (VISION-006). The watchdog manages project bridges that route Zulip messages to opencode serve, enabling session control from any device. Triggers on: 'helm', 'bridge', 'untethered', 'start bridge', 'stop bridge', 'helm status', 'helm logs', 'is the bridge running'."
user-invocable: true
license: MIT
allowed-tools: Bash, Read
metadata:
  short-description: Untethered operator bridge management
  version: 2.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: haiku, effort: low -->

# swain-helm

Manages the swain-helm bridge system: starts the watchdog daemon, registers projects, monitors health, and tears down cleanly. The watchdog is a persistent process that reconciles desired state — ensuring project bridges and opencode serve are running.

## Locate the CLI

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HELM="$REPO_ROOT/bin/swain-helm"
```

If not found at that path, glob for `**/bin/swain-helm`.

## Runtime files

| File | Purpose |
|------|---------|
| `~/.config/swain-helm/run/watchdog.pid` | Watchdog process PID. |
| `~/.config/swain-helm/run/bridges/<name>.pid` | Per-project bridge PID. |
| `~/.config/swain-helm/run/opencode-instances.json` | Discovered/tracked opencode serve instances. |
| `~/.config/swain-helm/helm.config.json` | Global config (chat credentials, opencode auth). |
| `~/.config/swain-helm/projects/<name>.json` | Per-project desired state. |

## Commands

### host up ("start bridge" / "helm up" / default)

Start the watchdog daemon. Resolves 1Password credentials at startup (requires biometric unlock):

```bash
swain-helm host up
```

Foreground mode for debugging:

```bash
swain-helm host up --foreground
```

The watchdog discovers project configs, starts bridges, and finds or starts opencode serve. If 1Password is locked, the command fails with a clear error.

### host down ("stop bridge" / "helm down" / "shut down bridge")

```bash
swain-helm host down
```

Stops the watchdog and all project bridges. Use `--project <name>` to stop only one bridge:

```bash
swain-helm host down --project swain
```

### host status ("helm status" / "is the bridge running" / "bridge health")

```bash
swain-helm host status
```

Reports: watchdog PID, each bridge PID and health, opencode serve port/health/auth status.

### host provision ("provision bridge" / "setup bridge")

One-time setup: registers Zulip bot, creates stream, writes `helm.config.json`:

```bash
swain-helm host provision
```

### project add ("add project" / "register project")

Register a project for the watchdog to manage:

```bash
swain-helm project add ./             # current directory (rejects if no .git/)
swain-helm project add ~/code/swain    # absolute path
```

Writes `~/.config/swain-helm/projects/<name>.json`. The watchdog picks it up on the next reconciliation cycle (every 30s).

### project remove ("remove project")

```bash
swain-helm project remove --project swain
```

Removes the project config. The watchdog stops the bridge on the next cycle.

### project list ("list projects")

```bash
swain-helm project list
```

Shows all registered projects with their running status.

### logs ("helm logs" / "show bridge logs" / "what is the bridge doing")

Tail the watchdog log:

```bash
tail -50 /tmp/swain-helm.log
```

For continuous streaming, tell the operator to run `tail -f /tmp/swain-helm.log` in their terminal.

### restart ("restart bridge" / "helm restart")

Stop then start:

```bash
swain-helm host down && swain-helm host up
```

## After starting

Show the operator:
1. Bridge status (from `host status` output).
2. How to attach: `opencode attach http://127.0.0.1:<PORT>`.
3. Zulip stream to use for sending prompts.
4. Log path for monitoring: `/tmp/swain-helm.log`.

## Error handling

- If `bin/swain-helm` is not found, tell the operator the untethered package may not be installed and point to RUNBOOK-004.
- If 1Password is locked at startup, report clearly: "Unlock 1Password and retry."
- If opencode serve fails the health check, show the last 20 lines of `/tmp/opencode-serve.log`.
- Never fail silently — always report what was attempted and what failed.