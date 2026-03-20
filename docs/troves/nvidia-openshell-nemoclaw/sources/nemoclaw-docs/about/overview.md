# Overview

NVIDIA NemoClaw is an open source reference stack that simplifies running OpenClaw always-on assistants safely. It incorporates policy-based privacy and security guardrails, giving users control over their agents' behavior and data handling. This enables self-evolving claws to run more safely in clouds, on prem, RTX PCs, and DGX Spark.

NemoClaw uses open source models (NVIDIA Nemotron) alongside the NVIDIA OpenShell runtime (part of NVIDIA Agent Toolkit), a secure environment designed for executing claws more safely.

| Capability | Description |
| --- | --- |
| Sandbox OpenClaw | Creates an OpenShell sandbox pre-configured for OpenClaw, with strict filesystem and network policies from first boot. |
| Route inference | Configures OpenShell inference routing so agent traffic flows through cloud-hosted Nemotron 3 Super 120B via build.nvidia.com. |
| Manage the lifecycle | Handles blueprint versioning, digest verification, and sandbox setup. |

## Challenge

Autonomous AI agents like OpenClaw can make arbitrary network requests, access the host filesystem, and call any inference endpoint. Without guardrails, this creates security, cost, and compliance risks that grow as agents run unattended.

## Benefits

| Benefit | Description |
| --- | --- |
| Sandboxed execution | Every agent runs inside an OpenShell sandbox with Landlock, seccomp, and network namespace isolation. No access granted by default. |
| NVIDIA cloud inference | Agent traffic routes through cloud-hosted Nemotron 3 Super 120B via build.nvidia.com, transparent to the agent. |
| Declarative network policy | Egress rules defined in YAML. Unknown hosts blocked and surfaced to operator for approval. |
| Single CLI | `nemoclaw` command orchestrates full stack: gateway, sandbox, inference provider, network policy. |
| Blueprint lifecycle | Versioned blueprints handle sandbox creation, digest verification, reproducible setup. |

## Use Cases

| Use Case | Description |
| --- | --- |
| Always-on assistant | Run an OpenClaw assistant with controlled network access and operator-approved egress. |
| Sandboxed testing | Test agent behavior in a locked-down environment before granting broader permissions. |
| Remote GPU deployment | Deploy a sandboxed agent to a remote GPU instance for persistent operation. |
