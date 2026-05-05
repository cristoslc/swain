---
title: "OpenHands CLI Installation"
url: https://docs.openhands.dev/openhands/usage/cli/installation
hostname: docs.openhands.dev
description: "Install the OpenHands CLI on your system"
date: 2025-01-13
sitename: OpenHands Documentation
type: web-page
---

# Installation

> Install the OpenHands CLI on your system

**Note for Windows Users:** The OpenHands CLI requires WSL (Windows Subsystem for Linux). Native Windows is not officially supported.

## Installation Methods

### Method 1: Using uv (recommended)

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/) installed.

**Install OpenHands:**
```bash
uv tool install openhands --python 3.12
```

**Run OpenHands:**
```bash
openhands
```

**Upgrade OpenHands:**
```bash
uv tool upgrade openhands --python 3.12
```

### Method 2: Executable Binary

Install the OpenHands CLI binary with the install script:
```bash
curl -fsSL https://install.openhands.dev/install.sh | sh
```

Then run:
```bash
openhands
```

**MacOS Security Note:**
When running on Mac, you may get a warning "openhands can't be opened because Apple cannot check it for malicious software."

1. Open `System Settings`
2. Go to `Privacy & Security`
3. Scroll down to `Security` and click `Allow Anyway`
4. Rerun the OpenHands CLI

### Method 3: Using Docker

1. Set `SANDBOX_VOLUMES` environment variable
2. Configure `~/.openhands/settings.json` with LLM settings
3. Run:

```bash
docker run -it \
    --pull=always \
    -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server \
    -e AGENT_SERVER_IMAGE_TAG=1.19.1-python \
    -e SANDBOX_USER_ID=$(id -u) \
    -e SANDBOX_VOLUMES=$SANDBOX_VOLUMES \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands:/root/.openhands \
    --add-host host.docker.internal:host-gateway \
    --name openhands-cli-$(date +%Y%m%d%H%M%S) \
    python:3.12-slim \
    bash -c "pip install uv && uv tool install openhands --python 3.12 && openhands"
```

The `-e SANDBOX_USER_ID=$(id -u)` ensures sandbox user matches host user permissions.

## First Run

The first time you run the CLI, it will guide you through configuring required LLM settings. These are saved to `~/.openhands/settings.json`.

Conversation history is saved in `~/.openhands/conversations`.

**Note:** If upgrading from CLI version before 1.0.0, you'll need to redo settings setup as the configuration format has changed.

## Next Steps

- [Quick Start](/openhands/usage/cli/quick-start) - Learn the basics of using the CLI
- [MCP Servers](/openhands/usage/cli/mcp-servers) - Configure MCP servers
