# How NemoClaw Works

NemoClaw combines a lightweight CLI plugin with a versioned blueprint to move OpenClaw into a controlled sandbox.

## How It Fits Together

```
nemoclaw onboard → nemoclaw plugin → blueprint runner → openshell CLI (sandbox · gateway · inference · policy)
                                                              ↓
                                              OpenShell Sandbox:
                                                OpenClaw agent
                                                NVIDIA inference (routed)
                                                strict network policy
                                                filesystem isolation
```

## Design Principles

- **Thin plugin, versioned blueprint**: Plugin stays small and stable. Orchestration logic in blueprint, evolves on own release cadence.
- **Respect CLI boundaries**: `nemoclaw` CLI is primary interface. Plugin commands under `openclaw nemoclaw` don't override built-in OpenClaw commands.
- **Supply chain safety**: Blueprint artifacts are immutable, versioned, and digest-verified before execution.
- **OpenShell-native for new installs**: Recommends `openshell sandbox create` directly rather than forcing plugin-driven bootstrap.
- **Reproducible setup**: Running setup again recreates sandbox from same blueprint and policy definitions.

## Plugin and Blueprint

- **Plugin**: TypeScript package powering `nemoclaw` CLI and `openclaw nemoclaw` commands. Handles user interaction, delegates orchestration to blueprint.
- **Blueprint**: Versioned Python artifact containing all logic for creating sandboxes, applying policies, configuring inference. Plugin resolves, verifies, and executes as subprocess.

## Sandbox Creation

`nemoclaw onboard` process:
1. Plugin downloads blueprint artifact, checks version compatibility, verifies digest
2. Blueprint determines which OpenShell resources to create/update (gateway, inference providers, sandbox, network policy)
3. Blueprint calls OpenShell CLI commands to create sandbox and configure each resource

## Inference Routing

Inference requests never leave the sandbox directly. OpenShell intercepts every inference call and routes to the configured provider. NemoClaw routes to NVIDIA cloud (Nemotron 3 Super 120B via build.nvidia.com). Models switchable at runtime without sandbox restart.

## Network and Filesystem Policy

Strict baseline policy in `openclaw-sandbox.yaml`:
- **Network**: Only explicitly listed endpoints allowed. Unlisted hosts blocked and surfaced in TUI for operator approval.
- **Filesystem**: Agent can write to `/sandbox` and `/tmp`. All other system paths read-only.
- Approved endpoints persist for session but not saved to baseline policy file.
