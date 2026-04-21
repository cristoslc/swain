# swain-helm Runbook

Operational procedures for running and troubleshooting swain-helm.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Starting the Service](#starting-the-service)
5. [Stopping the Service](#stopping-the-service)
6. [Docker Deployment](#docker-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Common Operations](#common-operations)

---

## Quick Start

```bash
# 1. Provision (one-time setup)
swain-helm host provision \
  --zulip-site https://yourorg.zulipchat.com \
  --zulip-email bot@yourorg.zulipchat.com \
  --zulip-api-key your-key \
  --operator-email you@example.com \
  --project my-project \
  --project-path /path/to/project

# 2. Start watchdog
swain-helm host up

# 3. Verify
swain-helm host status
```

---

## Installation

### Prerequisites

- Python 3.11+
- git
- 1Password CLI (`op`) — for credential resolution
- Zulip bot account with API key

### Install from source

```bash
cd /path/to/swain-helm
uv pip install -e ".[dev]"
```

### Verify installation

```bash
swain-helm --help
python -m swain_helm.watchdog --help
```

---

## Configuration

### File locations

| File | Purpose |
|------|---------|
| `~/.config/swain-helm/helm.config.json` | Global helm configuration |
| `~/.config/swain-helm/projects/*.json` | Per-project configurations |
| `~/.config/swain-helm/run/watchdog.pid` | Watchdog process ID |
| `~/.config/swain-helm/run/bridges/*.pid` | Bridge process IDs |
| `<project>/.swain/swain-helm/session-registry.json` | Session state |

### helm.config.json structure

```json
{
  "domain": "personal",
  "chat": {
    "server_url": "https://yourorg.zulipchat.com",
    "bot_email": "bot@yourorg.zulipchat.com",
    "bot_api_key": "op://Private/Bot/credential",
    "operator_email": "you@example.com",
    "control_topic": "control"
  },
  "opencode": {
    "default_port": 4096
  },
  "scan_paths": ["/path/to/project"]
}
```

### Project config structure

```json
{
  "name": "my-project",
  "path": "/path/to/project",
  "stream": "my-project",
  "runtime": "claude",
  "auto_start": true,
  "worktree_poll_interval_s": 15
}
```

---

## Starting the Service

### Native (host)

```bash
# Start watchdog daemon
swain-helm host up

# Start in foreground (for debugging)
swain-helm host up --foreground
```

### Docker

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your values

# Start services
docker compose up -d

# Or with 1Password
op run --env-file=.env -- docker compose up -d
```

### Verify startup

```bash
# Check watchdog status
swain-helm host status

# Check processes
ps aux | grep swain_helm

# Check logs
tail -f ~/.config/swain-helm/run/watchdog.log
```

---

## Stopping the Service

### Native

```bash
# Stop all bridges and watchdog
swain-helm host down

# Stop specific project bridge
swain-helm host down --project my-project
```

### Docker

```bash
docker compose down
```

---

## Docker Deployment

### Build image

```bash
docker build -f Dockerfile.test -t swain-helm:latest .
```

### Run with docker run

```bash
docker run -d \
  --name swain-helm \
  -v /path/to/project:/path/to/project:ro \
  -v swain-config:/root/.config/swain-helm \
  -e ZULIP_BOT_EMAIL=bot@example.com \
  -e ZULIP_BOT_API_KEY=secret \
  -e ZULIP_OPERATOR_EMAIL=you@example.com \
  -e PROJECT_NAME=my-project \
  swain-helm:latest \
  python -m swain_helm.watchdog
```

### Docker Compose services

| Service | Purpose | Port |
|---------|---------|------|
| `watchdog` | Main orchestrator | — |
| `opencode-server` | Opencode runtime | 4098 |

---

## Troubleshooting

### Watchdog not starting

**Symptoms:** `swain-helm host up` fails silently or PID file not created.

**Check:**
```bash
# Check for existing watchdog
ps aux | grep swain_helm.watchdog

# Check PID file
cat ~/.config/swain-helm/run/watchdog.pid

# Check logs
tail -50 ~/.config/swain-helm/run/watchdog.log
```

**Fix:**
```bash
# Kill stale processes
pkill -f swain_helm.watchdog
rm -f ~/.config/swain-helm/run/watchdog.pid

# Restart
swain-helm host up
```

### Bridge not connecting to Zulip

**Symptoms:** No messages appearing in Zulip stream.

**Check:**
```bash
# Verify Zulip credentials
op read op://Private/Bot/credential

# Check bridge log
ls ~/.config/swain-helm/run/bridges/*.log
tail -f ~/.config/swain-helm/run/bridges/my-project.log
```

**Common causes:**
- Invalid API key
- Bot not subscribed to stream
- Network connectivity issues

### 1Password credential resolution failing

**Symptoms:** "ResolutionError" or "op not found".

**Check:**
```bash
# Verify op CLI installed
which op
op --version

# Verify signed in
op account list
op signin
```

**Fix:**
```bash
# Sign in to 1Password
eval $(op signin)

# Test credential read
op read op://Vault/Item/field
```

### Worktree discovery not working

**Symptoms:** New worktrees not detected, no sessions created.

**Check:**
```bash
# Verify git repository
cd /path/to/project
git worktree list --porcelain

# Check bridge logs for scanner errors
tail -f ~/.config/swain-helm/run/bridges/*.log | grep -i worktree
```

### Session registry corruption

**Symptoms:** Sessions showing wrong state or missing.

**Check:**
```bash
# View registry
cat /path/to/project/.swain/swain-helm/session-registry.json | jq
```

**Fix:**
```bash
# Delete corrupted registry (sessions will be recreated)
rm /path/to/project/.swain/swain-helm/session-registry.json

# Restart bridge
swain-helm host down --project my-project
swain-helm host up
```

### Port 4096 already in use

**Symptoms:** "Address already in use" errors.

**Check:**
```bash
lsof -i :4096
netstat -tlnp | grep 4096
```

**Fix:**
```bash
# Kill process using port
kill $(lsof -t -i:4096)

# Or use different port in config
```

---

## Common Operations

### Add a new project

```bash
swain-helm project add /path/to/new-project
swain-helm host up  # Starts bridge for new project
```

### Remove a project

```bash
swain-helm project remove --project old-project
swain-helm host down --project old-project
```

### List all projects

```bash
swain-helm project list
```

### View all running processes

```bash
# Watchdog and bridges
ps aux | grep swain_helm

# Opencode instances
ps aux | grep opencode

# Zulip chat plugins
ps aux | grep zulip_chat
```

### Check health of all components

```bash
# Script to check all PIDs
echo "=== Watchdog ==="
if [ -f ~/.config/swain-helm/run/watchdog.pid ]; then
  pid=$(cat ~/.config/swain-helm/run/watchdog.pid)
  kill -0 $pid 2>/dev/null && echo "Watchdog running (PID $pid)" || echo "Watchdog NOT running"
fi

echo "=== Bridges ==="
for pidfile in ~/.config/swain-helm/run/bridges/*.pid; do
  [ -f "$pidfile" ] || continue
  name=$(basename "$pidfile" .pid)
  pid=$(cat "$pidfile")
  kill -0 $pid 2>/dev/null && echo "$name: running (PID $pid)" || echo "$name: NOT running"
done
```

### Force cleanup after crash

```bash
# Kill all swain-helm processes
pkill -9 -f swain_helm

# Remove all PID files
rm -f ~/.config/swain-helm/run/watchdog.pid
rm -f ~/.config/swain-helm/run/bridges/*.pid

# Clear session registries
find ~/.config/swain-helm/projects -name "*.json" -exec rm {} \;

# Restart
swain-helm host up
```

### Debug mode (verbose logging)

```bash
# Set log level
export SWAIN_HELM_LOG_LEVEL=DEBUG

# Run in foreground
swain-helm host up --foreground
```

---

## Testing

See [TESTING.md](TESTING.md) for comprehensive test documentation.

Quick test:
```bash
# Run all tests in Docker
docker compose -f docker-compose.test.yml up test

# Run specific suite
docker compose -f docker-compose.test.yml up test-unit
docker compose -f docker-compose.test.yml up test-uat
```

---

## See Also

- [TESTING.md](TESTING.md) — Test documentation
- [README.md](README.md) — Project overview
- `swain-helm --help` — CLI help
- `docs/tests/uat/SPEC-*.md` — Specification test plans