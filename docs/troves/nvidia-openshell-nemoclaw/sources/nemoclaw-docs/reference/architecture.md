# Architecture

NemoClaw has two main components: a TypeScript plugin that integrates with the OpenClaw CLI, and a Python blueprint that orchestrates OpenShell resources.

## NemoClaw Plugin

Thin TypeScript package registering commands under `openclaw nemoclaw`. Runs in-process with OpenClaw gateway, handles user-facing CLI interactions.

```
nemoclaw/
├── src/
│   ├── index.ts                    Plugin entry — registers all commands
│   ├── cli.ts                      Commander.js subcommand wiring
│   ├── commands/
│   │   ├── launch.ts               Fresh install into OpenShell
│   │   ├── connect.ts              Interactive shell into sandbox
│   │   ├── status.ts               Blueprint run state + sandbox health
│   │   ├── logs.ts                 Stream blueprint and sandbox logs
│   │   └── slash.ts                /nemoclaw chat command handler
│   └── blueprint/
│       ├── resolve.ts              Version resolution, cache management
│       ├── fetch.ts                Download blueprint from OCI registry
│       ├── verify.ts               Digest verification, compatibility checks
│       ├── exec.ts                 Subprocess execution of blueprint runner
│       └── state.ts                Persistent state (run IDs)
├── openclaw.plugin.json            Plugin manifest
└── package.json
```

## NemoClaw Blueprint

Versioned Python artifact with own release stream. Plugin resolves, verifies, executes as subprocess. Drives all interactions with OpenShell CLI.

```
nemoclaw-blueprint/
├── blueprint.yaml                  Manifest — version, profiles, compatibility
├── orchestrator/
│   └── runner.py                   CLI runner — plan / apply / status
├── policies/
│   └── openclaw-sandbox.yaml       Strict baseline network + filesystem policy
```

### Blueprint Lifecycle

1. **Resolve** — locate artifact, check version constraints
2. **Verify** — check artifact digest
3. **Plan** — determine OpenShell resources to create/update
4. **Apply** — execute plan via `openshell` CLI commands
5. **Status** — report current state

## Sandbox Environment

Container image: `ghcr.io/nvidia/openshell-community/sandboxes/openclaw`

- OpenClaw runs with NemoClaw plugin pre-installed
- Inference calls routed through OpenShell to configured provider
- Network egress restricted by baseline policy
- Filesystem: `/sandbox` and `/tmp` read-write, system paths read-only

## Inference Routing

```
Agent (sandbox) → OpenShell gateway → NVIDIA cloud (build.nvidia.com)
```
