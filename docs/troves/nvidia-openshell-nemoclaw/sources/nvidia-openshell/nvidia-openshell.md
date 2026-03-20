---
source-id: "nvidia-openshell"
title: "NVIDIA OpenShell — Safe, Private Runtime for Autonomous AI Agents"
type: repository
url: "https://github.com/NVIDIA/OpenShell"
fetched: 2026-03-20T00:00:00Z
hash: "--"
selective: true
highlights:
  - "architecture/system-architecture.md"
  - "architecture/sandbox.md"
  - "architecture/security-policy.md"
  - "architecture/gateway.md"
  - "architecture/inference-routing.md"
---

# NVIDIA OpenShell

OpenShell is the safe, private runtime for autonomous AI agents. It provides sandboxed execution environments that protect your data, credentials, and infrastructure — governed by declarative YAML policies that prevent unauthorized file access, data exfiltration, and uncontrolled network activity.

OpenShell is built agent-first. The project ships with agent skills for everything from cluster debugging to policy generation.

> **Alpha software — single-player mode.** One developer, one environment, one gateway. Building toward multi-tenant enterprise deployments.

## Quickstart

### Prerequisites

- **Docker** — Docker Desktop (or a Docker daemon) must be running.

### Install

**Binary (recommended):**

```bash
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
```

**From PyPI (requires uv):**

```bash
uv tool install -U openshell
```

### Create a sandbox

```bash
openshell sandbox create -- claude  # or opencode, codex, copilot, ollama
```

A gateway is created automatically on first use. To deploy on a remote host, pass `--remote user@host`.

The sandbox container includes the following tools by default:

| Category   | Tools                                                    |
| ---------- | -------------------------------------------------------- |
| Agent      | `claude`, `opencode`, `codex`, `copilot`                 |
| Language   | `python` (3.13), `node` (22)                             |
| Developer  | `gh`, `git`, `vim`, `nano`                               |
| Networking | `ping`, `dig`, `nslookup`, `nc`, `traceroute`, `netstat` |

### Network policy in action

Every sandbox starts with **minimal outbound access**. You open additional access with a short YAML policy that the proxy enforces at the HTTP method and path level, without restarting anything.

```bash
# 1. Create a sandbox (starts with minimal outbound access)
openshell sandbox create

# 2. Inside the sandbox — blocked
sandbox$ curl -sS https://api.github.com/zen
curl: (56) Received HTTP code 403 from proxy after CONNECT

# 3. Apply a read-only GitHub API policy
sandbox$ exit
openshell policy set demo --policy examples/sandbox-policy-quickstart/policy.yaml --wait

# 4. Reconnect — GET allowed, POST blocked by L7
openshell sandbox connect demo
sandbox$ curl -sS https://api.github.com/zen
Anything added dilutes everything else.

sandbox$ curl -sS -X POST https://api.github.com/repos/octocat/hello-world/issues -d '{"title":"oops"}'
{"error":"policy_denied","detail":"POST /repos/octocat/hello-world/issues not permitted by policy"}
```

## How It Works

OpenShell isolates each sandbox in its own container with policy-enforced egress routing. A lightweight gateway coordinates sandbox lifecycle, and every outbound connection is intercepted by the policy engine:

- **Allows** — the destination and binary match a policy block.
- **Routes for inference** — strips caller credentials, injects backend credentials, and forwards to the managed model.
- **Denies** — blocks the request and logs it.

| Component          | Role                                                                                         |
| ------------------ | -------------------------------------------------------------------------------------------- |
| **Gateway**        | Control-plane API that coordinates sandbox lifecycle and acts as the auth boundary.          |
| **Sandbox**        | Isolated runtime with container supervision and policy-enforced egress routing.              |
| **Policy Engine**  | Enforces filesystem, network, and process constraints from application layer down to kernel. |
| **Privacy Router** | Privacy-aware LLM routing that keeps sensitive context on sandbox compute.                   |

Under the hood, all these components run as a K3s Kubernetes cluster inside a single Docker container — no separate K8s install required.

## Protection Layers

OpenShell applies defense in depth across four policy domains:

| Layer      | What it protects                                    | When it applies             |
| ---------- | --------------------------------------------------- | --------------------------- |
| Filesystem | Prevents reads/writes outside allowed paths.        | Locked at sandbox creation. |
| Network    | Blocks unauthorized outbound connections.           | Hot-reloadable at runtime.  |
| Process    | Blocks privilege escalation and dangerous syscalls. | Locked at sandbox creation. |
| Inference  | Reroutes model API calls to controlled backends.    | Hot-reloadable at runtime.  |

Policies are declarative YAML files. Static sections (filesystem, process) are locked at creation; dynamic sections (network, inference) are hot-reloadable.

## Repository Structure (selective)

```
crates/
  openshell-bootstrap/     # Bootstrap and image management
  openshell-cli/           # CLI entry point (openshell command)
  openshell-core/          # Core types, proto definitions, config
  openshell-policy/        # Policy types
  openshell-providers/     # Inference provider integrations (Anthropic, OpenAI, NVIDIA, etc.)
  openshell-router/        # Inference routing engine
  openshell-sandbox/       # Sandbox supervisor, proxy, OPA engine, Landlock/seccomp/netns
architecture/              # Architecture documentation
  system-architecture.md
  sandbox.md
  security-policy.md
  gateway.md
  inference-routing.md
  tui.md
.agents/skills/            # Agent skills for development
```
