# Docker Sandboxes

**Availability:** Experimental  
**Requires:** Docker Desktop 4.58 or later

Docker Sandboxes lets you run AI coding agents in isolated environments on your machine. The docs frame it as a way to give agents enough autonomy to install tools, run commands, and build containers without exposing the host system directly.

## Why use Docker Sandboxes

AI coding agents often need to:

- execute shell commands
- install packages
- run tests
- build or run containers

Running those agents on the host means they can access host files, processes, and network resources. Docker Sandboxes instead isolates each agent in a microVM with its own Docker daemon.

Documented benefits:

- agent autonomy without host-system risk
- YOLO mode by default, without permission prompts on every action
- a private Docker daemon for test containers
- file sharing between host and sandbox
- network access control

The overview points readers to the architecture page for a direct comparison with other isolation approaches.

> MicroVM-based sandboxes require macOS or Windows (experimental). Linux users are directed to legacy container-based sandboxes in Docker Desktop 4.57.

## How to use sandboxes

Create and run a sandbox for an agent from a workspace directory:

```console
$ cd ~/my-project
$ docker sandbox run claude
```

Replace `claude` with another supported agent. The command creates a sandbox for the workspace and starts the selected agent inside it.

## How it works

Sandboxes run in lightweight microVMs with private Docker daemons.

- the agent runs inside the VM, not on the host
- the agent cannot access the host Docker daemon
- the agent cannot access host files outside the shared workspace
- sandboxes are managed with `docker sandbox ...`, not `docker ps`

The workspace directory is synchronized between host and sandbox at the same absolute path so diagnostics and file paths line up across environments.

### Multiple sandboxes

Create isolated sandboxes for multiple workspaces:

```console
$ docker sandbox run claude ~/project-a
$ docker sandbox run claude ~/project-b
```

Each sandbox persists until it is explicitly removed, so installed packages and configuration survive reconnects for that workspace.

## Supported agents

The overview page lists these agents:

- Claude Code
- Codex
- Copilot
- Gemini
- OpenCode
- Docker Agent
- Kiro
- Shell

Claude Code is labeled production-ready; the others are described as in development on the overview page.

## Get started

The overview sends operators to the dedicated get-started guide for the first end-to-end workflow:

- configure credentials
- create a sandbox
- reconnect to existing sandboxes
- inspect or remove sandboxes

## Troubleshooting

The overview points to the troubleshooting page for CLI plugin issues, credential conflicts, file-sharing errors, and reset procedures.
