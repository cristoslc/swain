# Synthesis: NVIDIA OpenShell & NemoClaw

## Key Findings

### Agent Sandboxing as a First-Class Concern

Both OpenShell and NemoClaw treat agent isolation as the primary design goal, not an afterthought. OpenShell provides the runtime kernel — Landlock filesystem isolation, seccomp syscall filtering, network namespaces with forced proxy routing, and an OPA-based policy engine — while NemoClaw packages this into a turnkey stack for OpenClaw agents with NVIDIA inference.

### Defense-in-Depth Security Model

The isolation stack applies four enforcement layers (cited: `nvidia-openshell`, `nemoclaw-docs`):

1. **Filesystem** (Landlock LSM) — locked at sandbox creation, immutable
2. **Network** (HTTP CONNECT proxy + OPA) — hot-reloadable, per-binary rules at method/path level
3. **Process** (seccomp BPF) — locked at creation, blocks privilege escalation
4. **Inference** (router with credential swapping) — hot-reloadable, transparent to agent

The split between static (locked at creation) and dynamic (hot-reloadable) policies is a deliberate design choice enabling runtime adaptation without compromising baseline security.

### Declarative YAML Policy Language

Network policies are expressed as declarative YAML with per-binary, per-endpoint, per-HTTP-method granularity (cited: `nemoclaw-docs`). This goes beyond simple allow/deny — the policy engine can restrict which *binary* can reach which *endpoint* using which *HTTP methods* on which *URL paths*. This is significantly more expressive than typical container network policies.

### Operator-in-the-Loop for Unknown Requests

When an agent attempts to reach an unlisted endpoint, the request is blocked and surfaced to the operator via TUI for real-time approval (cited: `nemoclaw-docs`). Approved endpoints persist only for the session. This pattern balances agent autonomy with human oversight.

### Architecture: K3s-in-Docker

OpenShell runs its entire control plane — gateway, sandbox pods, CRD controller — as a K3s Kubernetes cluster inside a single Docker container (cited: `nvidia-openshell`). No separate K8s install required. This is an unusual but effective approach for single-player mode that simplifies deployment while retaining Kubernetes primitives internally.

### Inference Routing with Privacy

The inference router intercepts all LLM API calls, strips caller credentials, injects backend credentials, and forwards to the managed model (cited: `nvidia-openshell`). This "privacy router" pattern ensures sensitive context stays on sandbox compute and agents can't exfiltrate credentials via inference calls.

### Blueprint Lifecycle (NemoClaw-specific)

NemoClaw separates its thin TypeScript CLI plugin from a versioned Python blueprint artifact (cited: `nemoclaw-docs`). The blueprint is immutable, digest-verified, and contains all orchestration logic. This separation enables independent versioning and supply-chain safety for the orchestration layer.

## Points of Agreement

- Both sources emphasize strict-by-default networking (deny all, approve explicitly)
- Both describe the same isolation mechanisms: Landlock + seccomp + netns
- Both position the work as alpha/early-stage with single-player scope
- Both use the same inference routing architecture (transparent proxy with credential management)

## Points of Disagreement

None identified — NemoClaw is an opinionated packaging layer on top of OpenShell, not a competing approach. The sources are complementary.

## Gaps

- **Multi-tenant / team deployment**: Both sources acknowledge this is future work. No details on isolation between tenants or shared gateway architectures.
- **Performance overhead**: No benchmarks on proxy latency, TLS MITM overhead, or OPA evaluation cost per request.
- **Policy authoring UX**: The mechanistic mapper (auto-generating policy recommendations from denials) is mentioned in OpenShell code but not documented in NemoClaw's user-facing docs.
- **Windows/macOS native support**: Landlock and seccomp are Linux-only. macOS support depends on Docker/Colima. No native sandbox isolation on non-Linux hosts.
- **Audit trail persistence**: Session-approved endpoints aren't saved to baseline. No documented approach for promoting session approvals to persistent policy.
- **OpenClaw itself**: Neither source explains what OpenClaw is beyond "always-on assistant" — understanding the full stack requires separate research into openclaw.ai.
