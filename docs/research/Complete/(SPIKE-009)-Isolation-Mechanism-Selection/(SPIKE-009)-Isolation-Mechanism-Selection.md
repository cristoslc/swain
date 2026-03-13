---
title: "Isolation Mechanism Selection"
artifact: SPIKE-009
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-13
question: "Should Claude Code be isolated via Docker containers, microVMs, or another mechanism — and what are the tradeoffs?"
gate: Pre-MVP
risks-addressed:
  - Containers share the host kernel — may not provide sufficient isolation for arbitrary agent tool execution
  - MicroVMs (Firecracker, QEMU) add startup latency and complexity that may not be justified for an interactive CLI
  - Must work on both macOS and Linux; Windows assumed via WSL (Linux path)
  - macOS and Linux have different virtualization stacks — mechanisms that work natively on one may need shims on the other
depends-on: []
evidence-pool:
  - microvm-research-findings.md
  - lightweight-sandbox-research-findings.md
---

# Isolation Mechanism Selection

## Question

Should Claude Code be isolated via Docker containers, microVMs, or another mechanism — and what are the tradeoffs for an interactive, ephemeral developer tool that must work on both macOS and Linux?

Sub-questions:
1. **Containers (Docker)**: What isolation guarantees does Docker provide on each platform? On macOS, Docker Desktop runs a Linux VM under the hood — is the container-in-VM model sufficient? On Linux, containers share the host kernel — is that acceptable? What is startup time from cold and warm on each?
2. **MicroVMs (Firecracker, QEMU via Lima/Orbstack)**: What is the startup latency? Can filesystem sharing (virtiofs, 9p, sshfs) match bind-mount performance for interactive use? Firecracker is Linux-only — what's the macOS equivalent?
3. **Dev Containers**: Does the `.devcontainer/` spec provide a useful abstraction layer that works across Docker and other runtimes on both platforms? Would it give IDE integration for free?
4. **Orbstack**: macOS-only — does it simplify the macOS story enough to justify a platform-specific path?
5. **Nix/sandbox**: Could `nix develop` or platform-native sandboxing (`sandbox-exec` on macOS, namespaces on Linux) provide sufficient isolation without a full VM/container?
6. What level of isolation is actually needed? Claude Code runs shell commands — is kernel-level isolation (VM) necessary, or is filesystem/process namespace isolation (container) sufficient?
7. **Cross-platform parity**: Which mechanisms have identical or near-identical behavior on macOS and Linux? Where do we accept platform-specific divergence vs. requiring a single mechanism?

## Go / No-Go Criteria

- **Go**: A clear recommendation for one mechanism (or one per platform with a shared launcher interface) with documented rationale, startup time under 5 seconds for interactive use, filesystem sharing that supports real-time read/write of project files, and works on both macOS and Linux. Windows covered via WSL (Linux path).
- **No-Go**: All mechanisms have deal-breaking tradeoffs on one or both platforms (e.g., >30s startup, broken filesystem sharing, unacceptable complexity). In that case, recommend running Claude Code on host with sandboxing flags instead.

## Pivot Recommendation

If no single mechanism wins clearly:
1. Support Docker as the default (already installed, widely understood) with the option to swap in a microVM backend later
2. Abstract the launcher script to be runtime-agnostic — `./claude-isolated` dispatches to whichever runtime is available

## Findings

### 1. Docker Containers

**Isolation model:**
- **macOS**: Strong. Docker Desktop runs all containers inside a LinuxKit VM (Apple Virtualization.framework). A container escape only reaches the VM, not the macOS host. Enhanced Container Isolation (ECI, paid) adds Sysbox runtime with user namespace remapping.
- **Linux**: Moderate. Containers share the host kernel via namespaces/cgroups/seccomp. Three runc escape CVEs disclosed Nov 2025 (CVE-2025-31133, CVE-2025-52565, CVE-2025-52881) — all require custom mount configs, mitigated by rootless Docker. Rootless mode reduces attack surface 60-80%.

**Startup time:**
- Warm (daemon running, image cached): 0.5-0.6s Linux, 1.5-1.9s macOS. **Meets <5s target.**
- Cold (daemon not running): 2-5s Linux, 10-30s macOS (VM boot). **macOS exceeds target; mitigate by keeping daemon running.**

**Filesystem performance:**
- Linux bind mounts: **zero overhead** (kernel path remapping). inotify works natively.
- macOS VirtioFS (default since Docker Desktop 4.6): **~3x slower** than native. Synchronized File Shares (paid) brings this to ~1.5-2x. **Known bug: DELETE file events not propagated** (docker/for-mac#7246).

**Resource overhead:** <3% CPU, ~150MB daemon memory on Linux. macOS: 1-2GB for the Docker Desktop VM.

### 2. MicroVMs

**Firecracker:** Linux-only (requires KVM), <125ms VM boot, ~4ms snapshot restore. **No virtiofs support** (deliberate design choice). Only block devices. No interactive filesystem sharing — designed for serverless (Lambda, Fly.io), not interactive development. **Not viable for our use case.**

**Lima/Colima (macOS):** Lima with `vz` (Virtualization.framework) boots in 3-5s on Apple Silicon. virtiofs filesystem sharing: 70-90% native read, 50-70% native write. 9p is **7x slower than virtiofs** — unusable for large projects. Colima provides full Docker API compatibility as a drop-in. ~400MB memory vs Docker Desktop's 2GB+.

**Cloud Hypervisor / crosvm:** No macOS support. No developer tooling. Not practical for desktop use.

**Docker Sandboxes (Docker Desktop 4.58+):** Purpose-built for AI agent sandboxing (Claude Code is first supported agent). Each sandbox gets a dedicated microVM with private Docker daemon. Uses **file sync, not volume mounts** (paths preserved). Network filtering via HTTP/HTTPS proxy with allow/deny lists. Independent evaluation scored 8.1/10. **Linux: container-only fallback, no microVM isolation.** Requires Docker Desktop license.

**Apple Containers (macOS 26, WWDC 2025):** 1 VM per container, sub-second startup, open source Swift, OCI-compatible. v0.1.0 — no Docker API, no Compose, nascent ecosystem. **Future option, not current solution.** Apple Silicon only.

**libkrun:** Unlike Firecracker, runs on macOS ARM64 via Hypervisor.framework. Lima supports it as a VM type. Interesting as an implementation detail, not a direct tool.

### 3. Dev Containers Specification

Microsoft-maintained open spec (`.devcontainer/devcontainer.json`). Anthropic publishes a reference Claude Code devcontainer with firewall rules (iptables, domain allowlisting, `--dangerously-skip-permissions`).

**Strengths:** Declarative, version-controllable. Handles credential forwarding (env vars, mounts), filesystem binding, lifecycle hooks. IDE integration (VS Code, JetBrains). Works on both macOS and Linux.

**Weaknesses:** Docker-centric despite "runtime-agnostic" goal. **CLI is incomplete** — missing stop/down commands, no SSH agent forwarding (VS Code extension feature only). Cannot target microVMs. Podman works but is second-class.

**Assessment:** Use `devcontainer.json` as the **configuration format** but invoke Docker directly via a launcher script rather than depending on the devcontainer CLI.

### 4. OrbStack (macOS only)

Closed-source macOS Docker/Linux runtime. 2s cold start (vs Docker Desktop's 30s), ~60% less memory, 75-95% native filesystem performance. Docker API drop-in compatible. Free for personal use.

**Critical gap:** No `docker sandbox` support (GitHub issue #2295, 144+ upvotes). Cannot use Docker's official AI agent sandboxing feature.

**Vendor risk:** Apple Containers (macOS 26) may supersede it within 12-18 months. No data lock-in — all Docker commands are portable.

**Assessment:** Optional performance optimization for developers who prefer it over Docker Desktop. Not a required dependency.

### 5. Lightweight Sandboxing (sandbox-exec / bubblewrap / Landlock)

**macOS — sandbox-exec (Seatbelt):** Deprecated since ~2016 but still present through macOS 26. **Actively used by Anthropic (sandbox-runtime), OpenAI (Codex CLI), and Agent Safehouse.** Kernel-level enforcement of filesystem, network, process restrictions. Scheme-like profile language. The **only viable kernel-level sandboxing mechanism for CLI tools on macOS**.

**Linux — bubblewrap (bwrap):** Unprivileged namespace isolation (PID, mount, net, user, IPC). ~3,000 lines of C. ~10ms startup. Full namespace isolation equivalent to Docker minus the image/layer system. Used by Flatpak, GNOME, WebKitGTK.

**Linux — Landlock (kernel 5.13+):** Unprivileged filesystem and network ACLs. Zero overhead (LSM hook). Process restricts itself, cannot lift restrictions. Anthropic's sandbox-runtime uses Landlock as default on Linux. Lighter than bubblewrap but no PID/network namespace isolation.

**Nix:** Dependency isolation only (PATH, env vars, tool versions). **Zero security isolation.** Useful as the environment layer combined with platform-specific sandboxing.

**Performance:** sandbox-exec ~5-10ms startup, 100% native filesystem. bubblewrap ~10-20ms, ~99% native. Landlock ~0ms overhead.

### 6. Isolation Level Needed

| Threat | sandbox-exec/bwrap | Container (Docker) | MicroVM |
|--------|-------------------|-------------------|---------|
| Accidental `rm -rf /` | Sufficient | Sufficient | Overkill |
| Untrusted npm packages | Sufficient | Sufficient | Recommended |
| Arbitrary agent shell commands | Sufficient | Sufficient | Recommended |
| Credential protection | Sufficient (if paths restricted) | Sufficient (if volumes controlled) | Better |
| Kernel exploits | Insufficient | Insufficient | Required |

For an interactive developer CLI where the operator has consented to running an AI agent, the primary threat is **accidental host damage**, not adversarial kernel exploitation. Process-level sandboxing (sandbox-exec/bubblewrap) is sufficient. Container-level isolation (Docker) adds image management and reproducibility. VM-level isolation (microVM) is strongest but adds filesystem sharing friction.

### 7. Cross-Platform Parity Analysis

**No single mechanism provides identical behavior on macOS and Linux.** The OS primitives are fundamentally different:
- macOS: Seatbelt/sandbox-exec (kernel sandbox profiles), Virtualization.framework (VMs)
- Linux: Namespaces + seccomp + Landlock + cgroups (kernel isolation primitives), KVM (VMs)

**Parity matrix:**

| Mechanism | macOS | Linux | Parity |
|-----------|-------|-------|--------|
| Docker (containers) | Via VM (Docker Desktop/Colima/OrbStack) | Native | Near-identical API, different isolation models |
| Docker Sandboxes | MicroVM (strong) | Container fallback (weaker) | **Divergent isolation guarantees** |
| sandbox-exec / bubblewrap | sandbox-exec | bubblewrap | Platform-specific tools, same goal |
| Landlock | Not available | Native (kernel 5.13+) | macOS gap |
| Firecracker | Not available | Native (KVM) | macOS gap |
| Lima/Colima | Via Virtualization.framework | Experimental | macOS-first |
| OrbStack | Native | Not available | Linux gap |
| Apple Containers | Future (macOS 26) | Not available | macOS-only |
| Nix develop | Both | Both | Full parity (but no security isolation) |
| Dev Containers spec | Both (via Docker) | Both (via Docker) | Full parity |

**The proven production pattern:** A unified configuration layer that compiles down to platform-specific enforcement. This is exactly what Anthropic's `sandbox-runtime` and OpenAI's Codex CLI do:
- macOS: sandbox-exec (Seatbelt) with dynamically generated profiles
- Linux: Landlock (default) or bubblewrap (stronger)
- Single API: `createSandbox({ allowWrite: [...], allowedDomains: [...] })`

## Recommendation

**Go.** A clear two-tier recommendation with a shared launcher interface.

### Tier 1: Lightweight sandboxing (default, zero-install)

Use Anthropic's existing `sandbox-runtime` pattern:
- **macOS**: `sandbox-exec` with deny-first Seatbelt profiles
- **Linux**: Landlock (default) + bubblewrap (optional stronger mode)
- Startup: <20ms on both platforms
- Filesystem: 100% native performance
- Isolation: Sufficient for accidental damage prevention

This is what Claude Code already supports via `claude --sandbox`. No additional runtime dependencies (Docker, VMs) needed. Works offline. Near-instant startup.

### Tier 2: Docker containers (opt-in, stronger isolation + reproducibility)

For operators who want reproducible environments or stronger isolation:
- Use `devcontainer.json` as the configuration format (Anthropic's reference config)
- Launcher script invokes Docker directly (not the devcontainer CLI)
- **macOS**: Docker Desktop, Colima, or OrbStack as the runtime
- **Linux**: Docker Engine with rootless mode
- Startup: 0.5-2s warm
- Filesystem: 95-100% native on Linux, ~33% on macOS (acceptable for agent workloads)

### Tier 3: Docker Sandboxes (opt-in, strongest isolation)

For operators running Claude Code unattended with `--dangerously-skip-permissions`:
- Docker Sandboxes provide microVM-per-session isolation
- Best on macOS (Virtualization.framework); container-only fallback on Linux
- Requires Docker Desktop license
- File sync, not volume mounts — some latency for large workspaces

### Architecture

```
+---------------------------------------+
|   claude-isolated launcher script     |
| (detects available runtime, applies   |
|  user preference from config)         |
+---------------------------------------+
         |            |           |
    +----+----+  +----+----+ +---+-------+
    | sandbox |  | Docker  | | Docker    |
    | (T1)    |  | (T2)    | | Sandbox   |
    |         |  |         | | (T3)      |
    +---------+  +---------+ +-----------+
    sandbox-exec  docker run  docker sandbox
    + bwrap       + devcontainer.json
```

### What SPIKE-007 and SPIKE-008 should assume

- **SPIKE-007 (Container Image)**: Proceed with Docker as the Tier 2 mechanism. Build a minimal Dockerfile for Claude Code. The container path is opt-in, not default.
- **SPIKE-008 (Credentials)**: Must solve credential forwarding for both Tier 1 (sandbox-exec/bwrap — paths are restricted, credentials need explicit allowlisting) and Tier 2 (Docker — env vars, volume mounts, socket forwarding).

### Future watch

- **Apple Containers (macOS 26, late 2026)**: VM-per-container with sub-second startup. Could replace Docker on macOS entirely. Monitor maturity.
- **Docker Sandboxes on Linux**: Currently container-only fallback. If Docker adds microVM support on Linux, this becomes the unified Tier 3 across platforms.
- **sandbox-exec deprecation**: Monitor each macOS release. If Apple removes it, fall back to Apple Containers or Docker.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
| Active | 2026-03-12 | — | Research conducted across 5 parallel investigations |
| Complete | 2026-03-12 | 8ab71ab | Findings and recommendation written; operator approved 2026-03-13 |
