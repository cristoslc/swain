# Architecture

**Availability:** Experimental  
**Requires:** Docker Desktop 4.58 or later

This page explains why Docker Sandboxes uses microVMs rather than host execution, socket-mounted containers, or Docker-in-Docker.

## Why microVMs

The docs argue that AI coding agents need full Docker capabilities:

- build images
- run containers
- use Docker Compose

Giving that power to an agent through the host Docker daemon exposes host containers, images, and workloads. Running the agent in a normal container does not fix the problem because the container still shares the host kernel or Docker Desktop VM. Docker-in-Docker adds nested-daemon complexity and often requires privileged mode.

Docker's stated conclusion is that each sandbox needs its own VM and its own Docker daemon.

## Isolation model

Each sandbox gets:

- a private Docker daemon inside the VM
- an isolated agent container
- isolated test containers created by that agent

Consequences called out in the docs:

- the agent sees only containers it creates
- the agent cannot access host containers, images, or volumes
- one sandbox cannot see another sandbox's Docker state

### Hypervisor-level isolation

Sandboxes use native host virtualization:

- macOS: `virtualization.framework`
- Windows: `Hyper-V` (experimental)

The docs emphasize that this gives a stronger isolation boundary than container namespaces because the sandbox has its own kernel.

### Security implications

The architecture page explicitly frames the VM boundary as providing:

- process isolation
- filesystem isolation
- network isolation between sandboxes
- Docker isolation from the host daemon

Network filtering is presented as an additional control layer, not the primary isolation mechanism.

## Workspace syncing

Workspace synchronization is bidirectional and path-preserving:

```text
Host:    /Users/alice/projects/myapp
Sandbox: /Users/alice/projects/myapp
```

The docs describe this as file synchronization rather than volume mounting. The goal is to keep:

- file paths in errors consistent
- hard-coded configuration paths usable
- host and guest views of the tree aligned

## Storage and persistence

A sandbox persists until `docker sandbox rm` removes it.

State that persists between runs:

- Docker images and containers created inside the sandbox
- packages installed in the sandbox
- agent credentials, configuration, and history
- workspace file changes that sync back to the host

State is isolated per sandbox. Images and layers are not shared across sandboxes.

## Networking

Sandboxes have outbound internet access through the host network.

The docs describe a host-side HTTP/HTTPS filtering proxy reachable from the sandbox at:

```text
host.docker.internal:3128
```

Key claims on this page:

- outbound web traffic goes through the proxy
- credentials for supported AI providers can be injected by the proxy
- credentials stay on the host rather than inside the sandbox
- sandboxes cannot communicate with each other
- sandboxes cannot access host `localhost` services directly

## Lifecycle

Two commands define the main lifecycle split:

```console
$ docker sandbox run ...
$ docker sandbox create ...
```

`run` initializes a VM and starts the agent. `create` initializes the VM and workspace without starting the agent automatically. Both preserve sandbox state until removal.

## Comparison to alternatives

The architecture page contrasts four approaches:

| Approach | Isolation | Agent Docker access | Host impact | Primary use case |
| --- | --- | --- | --- | --- |
| Sandboxes (microVMs) | Hypervisor-level | Private daemon | None on host Docker state | Autonomous agents that need to build and run containers |
| Container with socket mount | Kernel namespaces | Shared host daemon | Agent can see host Docker state | Trusted tools needing Docker CLI access |
| Docker-in-Docker | Nested containers | Private daemon with complexity | Requires privileged setup | CI-style isolated daemon workflows |
| Host execution | None | Host daemon or host shell | Full host impact | Manual local development |

The page's design argument is that autonomous agents need the Docker power of host execution without its trust assumptions.
