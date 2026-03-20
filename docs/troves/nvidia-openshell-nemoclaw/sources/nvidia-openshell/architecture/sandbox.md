# Sandbox Architecture

The sandbox binary isolates a user-specified command inside a child process with policy-driven enforcement. It combines Linux kernel mechanisms (Landlock, seccomp, network namespaces) with an application-layer HTTP CONNECT proxy to provide filesystem, syscall, and network isolation. An embedded OPA/Rego policy engine evaluates every outbound network connection against per-binary rules, and an optional L7 inspection layer examines individual HTTP requests within allowed tunnels.

## Source File Index

All paths relative to `crates/openshell-sandbox/src/`:

| File | Purpose |
|------|---------|
| `main.rs` | CLI entry point, argument parsing via clap, dual-output logging |
| `lib.rs` | `run_sandbox()` orchestration — the main startup sequence |
| `log_push.rs` | Tracing layer and background log streaming to gateway |
| `policy.rs` | SandboxPolicy, NetworkPolicy, ProxyPolicy, LandlockPolicy, ProcessPolicy structs |
| `opa.rs` | OPA/Rego policy engine using regorus crate |
| `process.rs` | ProcessHandle for spawning child processes, privilege dropping, signal handling |
| `proxy.rs` | HTTP CONNECT proxy with OPA evaluation, process-identity binding, inference interception |
| `ssh.rs` | Embedded SSH server (russh) with PTY support and handshake verification |
| `identity.rs` | BinaryIdentityCache — SHA256 trust-on-first-use binary integrity |
| `procfs.rs` | /proc filesystem reading for TCP peer identity resolution |
| `grpc_client.rs` | gRPC client for policy fetching, provider env, inference bundles, log push |
| `denial_aggregator.rs` | Background deduplication of DenialEvents by (host, port, binary) |
| `mechanistic_mapper.rs` | Deterministic policy recommendation generator — DenialSummary to PolicyChunk proposals |
| `sandbox/linux/landlock.rs` | Filesystem isolation via Landlock LSM (ABI V1) |
| `sandbox/linux/seccomp.rs` | Syscall filtering via BPF on SYS_socket |
| `sandbox/linux/netns.rs` | Network namespace creation, veth pair setup, iptables bypass detection |
| `l7/` | L7 inspection: inference detection, TLS MITM, protocol-aware relay, REST parsing |

## Isolation Stack

Three kernel-level mechanisms applied in order:

1. **Landlock** — filesystem access control (read/write/execute per path)
2. **Seccomp** — syscall filtering (blocks raw socket creation)
3. **Network Namespace** — veth pair isolates agent network; all traffic forced through proxy

## Proxy Architecture

The HTTP CONNECT proxy (10.200.0.1:3128) intercepts all outbound traffic:

1. Agent makes connection request
2. Proxy resolves process identity via /proc (binary path, PID chain)
3. OPA evaluates (host, port, binary) against network policy
4. If allowed: TLS passthrough or L7 inspection depending on policy
5. If inference: routes through InferenceRouter with credential swapping
6. If denied: logs denial, returns 403, feeds DenialAggregator for policy recommendations
