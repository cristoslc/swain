# Quickstart

## Prerequisites

### Hardware

| Resource | Minimum | Recommended |
| --- | --- | --- |
| CPU | 4 vCPU | 4+ vCPU |
| RAM | 8 GB | 16 GB |
| Disk | 20 GB free | 40 GB free |

### Software

| Dependency | Version |
| --- | --- |
| Linux | Ubuntu 22.04 LTS or later |
| Node.js | 20 or later |
| npm | 10 or later |
| Container runtime | Supported runtime installed and running |
| OpenShell | Installed |

### Container Runtime Support

| Platform | Supported runtimes | Notes |
| --- | --- | --- |
| Linux | Docker | Primary supported path |
| macOS (Apple Silicon) | Colima, Docker Desktop | Recommended for macOS |
| macOS | Podman | Not supported yet |
| Windows WSL | Docker Desktop (WSL backend) | Supported target path |

## Install and Onboard

```bash
curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash
```

Installs Node.js if needed, runs guided onboard wizard to create sandbox, configure inference, apply security policies.

Post-install summary:
```
Sandbox      my-assistant (Landlock + seccomp + netns)
Model        nvidia/nemotron-3-super-120b-a12b (NVIDIA Cloud API)

Run:         nemoclaw my-assistant connect
Status:      nemoclaw my-assistant status
Logs:        nemoclaw my-assistant logs --follow
```

## Chat with the Agent

```bash
# Connect to sandbox
nemoclaw my-assistant connect

# Open TUI
openclaw tui

# Or CLI for full response output
openclaw agent --agent main --local -m "hello" --session-id test
```

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/NVIDIA/NemoClaw/refs/heads/main/uninstall.sh | bash
```

Flags: `--yes` (skip prompt), `--keep-openshell`, `--delete-models`
