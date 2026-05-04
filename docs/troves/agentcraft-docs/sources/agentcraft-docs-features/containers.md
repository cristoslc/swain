---
title: Isolated Agent Containers
url: https://www.getagentcraft.com/docs/features/containers
fetched: 2026-05-04
type: documentation
---

# Isolated Agent Containers

Run agents in Docker or Apple Containers with full network isolation.

AgentCraft can run agents inside isolated containers for full network, filesystem, and browser separation. Multiple agents can run dev servers on the same port simultaneously without conflicts.

## Enabling Containers

Toggle container isolation in the Spawn Modal when creating a new hero. Select the container runtime (Docker or Apple Containers) and spawn — the agent runs inside an isolated environment.

## How It Works

Each containerized agent gets:

- Network isolation — Agents cannot access each other's network stack. Multiple agents can bind to the same port (e.g., localhost:3000) without conflicts.
- Filesystem isolation — Each container has its own filesystem. Project files are mounted into the container.
- Browser isolation — Each agent gets a separate browser session for live preview, preventing cookie/state conflicts.

## Container Runtimes

| Runtime | Platform | Notes |
| --- | --- | --- |
| Docker | macOS, Linux, Windows | Requires Docker Desktop or Docker Engine |
| Apple Containers | macOS | Native macOS containerization (macOS 26+) |

AgentCraft auto-detects available runtimes and shows only the ones installed on your system.

## UI Indicators

Containerized heroes display a container badge in the hero roster and info panel, showing which runtime they're using. The 3D map also shows a visual indicator for isolated agents.

## Use Cases

- Port conflicts — Run multiple agents developing web apps on the same port
- Security — Prevent agents from accessing sensitive host files or network resources
- Clean environments — Each agent starts with a fresh environment, avoiding dependency conflicts