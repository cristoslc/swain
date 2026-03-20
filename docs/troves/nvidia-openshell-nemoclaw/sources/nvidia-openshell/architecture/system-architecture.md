# OpenShell System Architecture

The system architecture consists of:

- **User's Machine**: CLI (`openshell`), TUI (`openshell term`), Python SDK, local config (`~/.config/openshell/`)
- **Kubernetes Cluster** (single Docker container running K3s):
  - **Gateway StatefulSet**: gRPC+HTTP server with mTLS on :8080, SQLite DB, SandboxWatcher, KubeEventTailer
  - **Sandbox Pods** (1 per sandbox):
    - Supervisor (privileged user): Embedded SSH server (russh, :2222), HTTP CONNECT proxy (10.200.0.1:3128), OPA policy engine (regorus, in-process), Inference Router, TLS MITM cert cache
    - Agent Process (restricted user): AI agent (Claude/OpenCode/Codex/Openclaw), Landlock FS isolation, Seccomp BPF filtering
    - Network Namespace: veth pair (10.200.0.1 <-> 10.200.0.2)
  - **CRD Controller** in agent-sandbox-system namespace
- **External Systems**: AI Provider APIs (Anthropic, OpenAI, NVIDIA NIM), Code Hosting (GitHub, GitLab), Self-hosted inference (LM Studio, vLLM), Package registries (PyPI, npm), Container registry (GHCR)

## Connection Flow

1. CLI/TUI/SDK connect to Gateway via gRPC over HTTPS (mTLS) on :30051 NodePort
2. Gateway manages Sandbox CRDs via Kubernetes API
3. Gateway connects to sandbox SSH server via NSSH1 handshake (HMAC-SHA256)
4. Agent traffic routes through Network Namespace -> HTTP CONNECT Proxy -> OPA evaluation -> External or Inference Router
5. Sandbox supervisor fetches policy, provider env, inference bundles, and pushes logs to Gateway via gRPC (mTLS)
