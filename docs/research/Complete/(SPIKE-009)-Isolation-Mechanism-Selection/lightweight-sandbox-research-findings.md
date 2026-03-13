# Lightweight Sandbox Research Findings for SPIKE-009

**Date**: 2026-03-12
**Scope**: Nix/nix develop, macOS sandbox-exec, Linux namespaces (unshare/bubblewrap/firejail), Landlock, Apple Containers (WWDC 2025), cross-platform story
**Context**: Alternatives to containers/VMs for isolating Claude Code CLI

---

## 1. Nix / nix develop

### What `nix develop` Actually Isolates

`nix develop` starts a bash shell that provides an interactive build environment nearly identical to what Nix would use to build a package. It isolates:

- **PATH**: Replaces the host PATH with one pointing exclusively into `/nix/store` for declared dependencies
- **Environment variables**: Strips most host environment variables; only those explicitly declared in the flake/derivation are set
- **Tool versions**: Hermetic — tools are pinned to exact versions via the flake lockfile

It does **not** isolate:

- **Filesystem access**: The shell has full read/write access to the host filesystem
- **Process isolation**: No PID namespace; can see and signal host processes
- **Network access**: Full host network access
- **IPC**: No isolation of shared memory, sockets, etc.

**Verdict**: `nix develop` is a *dependency isolation* tool, not a *security isolation* tool. It ensures your toolchain is reproducible; it does nothing to prevent a process from accessing `~/.ssh`, deleting files, or exfiltrating data over the network.

### Nix Build Sandbox (`sandbox = true` in nix.conf)

The Nix build sandbox is a completely separate mechanism from `nix develop`. When enabled, builds run with:

**On Linux:**
- Private PID, mount, network, IPC, and UTS namespaces
- Builds see only their Nix store dependencies + `/proc`, `/dev`, `/dev/shm`, `/dev/pts` + configured `sandbox-paths`
- Network access blocked (except for fixed-output derivations, which need to fetch)
- Environment variables stripped
- **Default**: `sandbox = true`

**On macOS:**
- Uses Apple's `sandbox-exec` (Seatbelt) under the hood
- Filesystem restrictions (builds only see declared dependencies)
- Less strict than Linux (no PID/network namespace isolation)
- **Default**: `sandbox = false`

**Critical caveat from the Nix community**: The sandbox "strips environment variables to prevent accidental leakage of the global namespace, and a well-written Nix build references only things in the Nix store, but it does not actually seal the build inside somewhere safe, so whatever is built is free to access the rest of the system if it wants to -- it's sandboxing in the sense that cooperative software becomes easier to manage, but not in the sense that it prevents adversarial software from being up to no good."

### Could a Nix Flake Define an Isolated Environment for Claude Code?

**Nix alone: No.** `nix develop` provides reproducible toolchains but zero security isolation.

**Nix + bubblewrap: Yes, on Linux.** Several projects combine Nix's declarative package management with bubblewrap's runtime sandboxing:

- **[bubblewrap-claude](https://github.com/matgawin/bubblewrap-claude)**: A Nix flake that wraps Claude Code in a bubblewrap sandbox. Uses `--unshare-all` for full namespace separation, read-only mounts except for the project directory and `/tmp`, and HTTP proxy-based domain allowlisting for network access. Includes pre-built profiles for Go, Python, Rust, JavaScript, etc.
- **[NixPak](https://github.com/nixpak/nixpak)**: Declarative wrapper around bubblewrap for Nix-packaged applications. Supports portals integration and runtime configuration.
- **[nixwrap](https://github.com/rti/nixwrap)**: Simpler CLI for ad-hoc bubblewrap sandboxing on NixOS.

These demonstrate the pattern: Nix handles *what* is in the environment; bubblewrap handles *what the environment can access*.

### Startup Time

- **First invocation**: Slow (minutes to hours if packages must be built from source; seconds if binary cache hits)
- **Subsequent invocations**: Near-instant (<1 second) since packages are already in the Nix store
- **With `direnv` + `nix develop`**: Automatic activation on `cd`, cached — effectively zero perceived startup after first use

### Cross-Platform

- Works on **macOS and Linux**
- Build sandbox is weaker on macOS (uses `sandbox-exec` internally, no namespace isolation)
- `bubblewrap` is Linux-only, so the Nix + bwrap pattern does not work on macOS

---

## 2. macOS `sandbox-exec` (Seatbelt)

### What It Is

`sandbox-exec` is a macOS command-line utility that runs a command inside Apple's kernel-level sandbox (Seatbelt). It uses the same underlying mechanism as App Sandbox but is controlled via profile files rather than entitlements.

### Deprecation Status

- Marked `(DEPRECATED)` since approximately 2016
- Apple removed the man page but the binary still exists (confirmed present through macOS 15.4 / Sequoia and macOS 26.x)
- Apple recommends "App Sandbox" instead, but App Sandbox is for GUI apps with entitlements, not CLI tools
- **The sandbox specification language is undocumented for third-party use** — this is the stated reason for deprecation
- Apple uses Seatbelt internally for system services, so the underlying kernel mechanism is unlikely to disappear
- OpenAI Codex CLI, Claude Code's `sandbox-runtime`, and Agent Safehouse all use `sandbox-exec` on macOS today

### What It Can Restrict

- **Filesystem**: Read/write access per path (literal, regex, subpath patterns)
- **Network**: All network operations, or specific host/port pairs
- **Process creation**: Which binaries can be executed
- **IPC**: Mach ports, Unix domain sockets
- **Sysctl**: System information access
- **Signal**: Process signaling

### Profile Language

Scheme-like syntax (LISP dialect). Example:

```scheme
(version 1)
(deny default)                          ; deny everything by default
(allow file-read* (subpath "/usr"))     ; allow reads under /usr
(allow file-read-data file-read-metadata
  (subpath "/path/to/project"))         ; allow project reads
(allow file-write*
  (subpath "/path/to/project")
  (subpath "/tmp"))                     ; allow writes to project + tmp
(deny network*)                         ; block all network
(allow network* (local ip "localhost:*")) ; except localhost
```

Matching patterns:
- `(literal "/exact/path")`
- `(regex "^/System")`
- `(subpath "/Library")` — path and all children

Two philosophies:
- **Deny-by-default** (most secure): `(deny default)` then explicitly allow
- **Allow-by-default** (permissive): `(allow default)` then deny specific operations

### Real-World Usage for AI Agent Isolation

**Agent Safehouse** (March 2026, 403 points on HN): A single shell script that wraps AI coding agents (Claude Code, Codex, Aider, Cline) in `sandbox-exec` with deny-first profiles. Pre-configured policies for each agent. Install via Homebrew or download the script.

**Anthropic's `sandbox-runtime`**: Claude Code's official sandboxing tool uses `sandbox-exec` on macOS with dynamically generated Seatbelt profiles. Supports glob patterns for path matching. Filesystem deny-then-allow for reads, allow-only for writes. Network via proxy with domain allowlisting.

**OpenAI Codex CLI**: Uses `sandbox_init()` system call to apply Seatbelt profiles at runtime before executing commands.

### Known Limitations and Gotchas

1. **Undocumented language**: No official Apple docs on the profile syntax. Developers reverse-engineer from system profiles in `/System/Library/Sandbox/Profiles/` and `/usr/share/sandbox/`
2. **Behavioral changes across macOS versions**: Reports of network blocking silently stopping in some versions
3. **No official API stability guarantees**: Apple can change or remove behavior without notice
4. **Complex applications struggle**: Comprehensive profiles require iterative testing
5. **No user namespace separation**: Process runs as the invoking user with restricted syscalls, not in a separate user context
6. **Kernel-level enforcement**: This is a strength — bypassing requires a kernel exploit — but Apple's deprecation creates long-term risk

### Assessment

Despite deprecation, `sandbox-exec` remains the **only viable kernel-level sandboxing mechanism for CLI tools on macOS**. It is actively used by multiple production AI agent tools. The risk is Apple removing it in a future macOS version, but given that Apple's own system services depend on the underlying mechanism, this is unlikely in the near term.

---

## 3. Linux Namespaces (Without Docker)

### `unshare` Command

`unshare` creates isolated namespaces for a process:

| Namespace | Flag | What It Isolates |
|-----------|------|-----------------|
| Mount | `--mount` | Filesystem mount points |
| PID | `--pid` | Process ID space |
| Network | `--net` | Network interfaces, routing, firewall |
| User | `--user` | UID/GID mapping (enables rootless) |
| UTS | `--uts` | Hostname, domain name |
| IPC | `--ipc` | Shared memory, message queues |
| Cgroup | `--cgroup` | Cgroup hierarchy |
| Time | `--time` | System clocks (Linux 5.6+) |

**Rootless operation**: User namespaces (`--user`) allow unprivileged users to create all other namespace types by mapping the current UID to root inside the namespace. This is the foundation of rootless containers.

**Practical example** for isolating a CLI tool:

```bash
unshare --user --mount --pid --net --fork --map-root-user \
  --mount-proc /bin/bash
```

This creates a process with its own PID space, network stack (no interfaces), and mount table, running as "root" inside the namespace but the original UID outside.

**Limitations**: `unshare` is low-level. You must manually set up bind mounts, network, `/proc`, etc. It is the primitive that higher-level tools build on.

### Bubblewrap (`bwrap`)

Bubblewrap is the unprivileged sandboxing tool used by Flatpak. It is a minimal, auditable wrapper around Linux namespaces.

**Key properties:**
- **Designed for unprivileged users** from the ground up
- Supports PID, mount, network, IPC, UTS, user, and cgroup namespaces
- **seccomp filtering** for syscall restriction
- Minimal setuid surface (or setuid-free with user namespaces)
- ~3,000 lines of C — small, auditable codebase
- Used by Flatpak, GNOME, WebKitGTK, and many other projects

**Example for isolating a CLI tool:**

```bash
bwrap \
  --unshare-all \
  --share-net \                         # keep network (or omit for isolation)
  --ro-bind /usr /usr \                 # read-only system
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /bin /bin \
  --ro-bind /etc /etc \
  --bind /path/to/project /workspace \  # writable project dir
  --tmpfs /tmp \
  --proc /proc \
  --dev /dev \
  --die-with-parent \
  /bin/bash
```

**Caveat from the NixOS community**: "bubblewrap is not a security boundary -- designed for transparency, rather than isolation." This is somewhat overstated; bwrap does enforce kernel-level namespace isolation. The nuance is that it was designed to make Flatpak apps cooperative, not to contain adversarial code. A determined attacker with kernel exploits could escape, but for preventing accidental host damage, it is effective.

### Firejail

Firejail is a SUID-based sandbox for Linux with 1000+ pre-built application profiles.

**Compared to bubblewrap:**
- More user-friendly: pre-built profiles for Firefox, VLC, etc.
- Larger attack surface: SUID root binary, larger codebase
- Has had security vulnerabilities (CVEs related to SUID handling)
- Better for desktop applications, less suitable for programmatic/composable use
- Not commonly used for developer tool isolation

**Verdict**: Bubblewrap is preferred for developer tool sandboxing due to smaller attack surface and better composability. Firejail is better for desktop application sandboxing.

### Landlock

Landlock is a Linux Security Module (since kernel 5.13) that allows **unprivileged** processes to restrict their own filesystem and network access.

**Key features:**
- No special privileges needed — any process can restrict itself
- Filesystem rules: restrict access to file hierarchies (read, write, execute, etc.)
- Network rules (since kernel 6.4 / ABI v4): restrict TCP port binding and connection
- Stackable: layers on top of other LSMs (SELinux, AppArmor)
- Three syscalls: `landlock_create_ruleset`, `landlock_add_rule`, `landlock_restrict_self`
- Process applies rules to itself, then cannot lift them — enforced for all subprocesses

**Tools:**
- **[landrun](https://github.com/Zouuup/landrun)**: "Think firejail, but lightweight, user-friendly, and baked into the kernel"
- **[island](https://github.com/landlock-lsm/island)**: Official high-level wrapper and policy manager

**Relevance**: Anthropic's `sandbox-runtime` uses Landlock as the default on Linux, with bubblewrap as an optional stronger isolation layer. Landlock is lighter weight (no namespaces, no mount setup) but provides only filesystem and network ACLs, not full process isolation.

### Comparison to Docker

| Aspect | Docker (Linux) | bubblewrap | Landlock | unshare (raw) |
|--------|---------------|------------|----------|---------------|
| Filesystem isolation | Yes (overlay, bind mounts) | Yes (bind mounts) | Yes (ACLs only) | Yes (mount namespace) |
| Network isolation | Yes (bridge, none) | Yes (net namespace) | Partial (TCP ports) | Yes (net namespace) |
| PID isolation | Yes | Yes | No | Yes |
| User isolation | Yes (userns) | Yes (userns) | No | Yes |
| Seccomp | Yes | Yes | N/A (LSM) | No (manual) |
| Requires root | No (rootless mode) | No | No | No (with userns) |
| Image management | Yes (OCI, layers) | No | No | No |
| Startup overhead | ~1-2 seconds | ~10 ms | ~0 ms (syscall) | ~10 ms |
| Codebase size | Large (containerd+runc) | ~3k lines C | Kernel-integrated | Kernel utility |
| Ecosystem | Enormous | Flatpak/GNOME | Growing | N/A |

---

## 4. Apple Containers (WWDC 2025)

### Architecture

Apple Containers, announced at WWDC 2025, takes a fundamentally different approach from Docker:

- **1 lightweight VM per container**: Each container runs in its own VM via Apple's Virtualization.framework
- **VM-level isolation**: Each container has its own kernel, filesystem, and network stack
- **Open source**: Swift-based, Apache 2.0 license, [github.com/apple/container](https://github.com/apple/container)
- **Apple Silicon only**: Optimized for M-series chips
- **macOS 26+ (Tahoe)**: Requires the next major macOS release (limited support on macOS 15)

### Performance Claims

- **Startup**: Sub-second (claimed ~200-300ms per container based on benchmarks)
- **Optimizations**: Custom lightweight Linux kernel, EXT4 block devices, Apple Silicon-specific tuning
- **Memory**: "Minimal" per-VM overhead (not yet independently benchmarked)

### OCI Compatibility

- Consumes and produces OCI-compliant container images
- Can pull from Docker Hub and other standard registries
- **No Docker API**: Different CLI (`container` command), no Docker Compose equivalent
- Not a drop-in Docker replacement

### Current Maturity

| Aspect | Status |
|--------|--------|
| Release version | 0.1.0 (early) |
| Docker Compose | Not supported |
| Volume mounts | Limited |
| Bind mounts | Restricted |
| Monitoring/debugging | Basic |
| Production readiness | No |
| Community adoption | Early/experimental |
| Documentation | Minimal |

### Comparison Summary

| Aspect | Apple Containers | Docker Desktop | OrbStack |
|--------|-----------------|----------------|----------|
| Isolation model | VM per container | Namespaces in shared VM | Namespaces in shared VM |
| Security boundary | Hardware (hypervisor) | Kernel (namespaces) | Kernel (namespaces) |
| Startup | ~200-300ms | Seconds (first) | Milliseconds (after VM) |
| macOS only | Yes (Apple Silicon) | No (cross-platform) | Yes |
| OCI images | Yes | Yes | Yes |
| Docker API | No | Yes | Yes |
| Ecosystem | Nascent | Massive | Growing |
| Cost | Free/open source | Freemium | Commercial |

### Assessment

Apple Containers is architecturally compelling — VM-per-container gives hardware-level isolation with container-like startup times. However, it is too early for production use (v0.1.0), macOS-only, Apple Silicon-only, and lacks the ecosystem tooling (Compose, CI integration, debugging) that Docker provides. It is a **future option** worth tracking, not a current solution.

---

## 5. Comparison: Lightweight Approaches vs. Containers/VMs

### What Lightweight Approaches Miss

| Guarantee | sandbox-exec | bubblewrap | Landlock | Nix develop | Docker | VM |
|-----------|-------------|------------|----------|-------------|--------|-----|
| Filesystem isolation | Yes (kernel) | Yes (namespace) | Yes (LSM) | No | Yes | Yes |
| Network isolation | Yes (kernel) | Yes (namespace) | Partial (TCP) | No | Yes | Yes |
| Process isolation | No (same PID ns) | Yes (PID namespace) | No | No | Yes | Yes |
| Kernel isolation | No (shared) | No (shared) | No (shared) | No | No (shared) | **Yes** |
| Resource limits | No | Partial (cgroups) | No | No | Yes (cgroups) | Yes |
| Separate root fs | No | Optional | No | No | Yes (overlay) | Yes |
| Reproducible env | No | No | No | Yes | Yes (image) | Yes (image) |

### "Good Enough" Analysis

**Threat model: Preventing accidental host damage** (not defending against malicious code with kernel exploits):

| Approach | Sufficient? | Why |
|----------|------------|-----|
| `sandbox-exec` (macOS) | **Yes** | Kernel-enforced filesystem and network restrictions. Prevents `rm -rf /`, credential access, data exfiltration. Used by Codex, Claude Code, Agent Safehouse in production. |
| `bubblewrap` (Linux) | **Yes** | Full namespace isolation (PID, mount, net, user). Equivalent to Docker's isolation model minus the image/layer system. |
| `Landlock` (Linux) | **Mostly** | Good filesystem ACLs, TCP port control. Missing PID isolation, full network isolation. Better as a layer than standalone. |
| `nix develop` | **No** | Zero security isolation. Dependency management only. |
| `sandbox-exec` + `bubblewrap` (platform-specific) | **Yes** | This is exactly what Anthropic's `sandbox-runtime` does today. |

### Startup Time

| Mechanism | Startup Time | Notes |
|-----------|-------------|-------|
| Landlock | ~0 ms | Syscall, no process overhead |
| sandbox-exec | ~5-10 ms | Profile compilation + exec |
| bubblewrap | ~10-20 ms | Namespace creation + bind mounts |
| unshare | ~10-20 ms | Similar to bwrap |
| Docker (Linux, warm) | ~500ms-2s | Container creation + overlay mount |
| Docker (macOS, warm) | ~1-3s | Same, through VM layer |
| Docker (macOS, cold) | ~10-30s | VM boot + container |
| Apple Containers | ~200-300ms | VM creation per container |
| Full VM (Lima/QEMU) | ~10-30s | Full kernel boot |

### Filesystem Performance

| Mechanism | Performance vs. Native | Notes |
|-----------|----------------------|-------|
| sandbox-exec | 100% (native) | No filesystem layer; just access control |
| bubblewrap | ~99% (native) | Bind mounts are native speed |
| Landlock | 100% (native) | LSM hook, negligible overhead |
| Docker bind mount (Linux) | ~95-99% | Minimal overlay overhead |
| Docker bind mount (macOS) | ~33% | virtiofs through Linux VM |
| VM virtiofs | 70-90% read, 50-70% write | Cross-VM filesystem protocol |

---

## 6. Cross-Platform Story

### Is There a Single Tool for macOS and Linux?

**No single tool provides equivalent sandboxing on both platforms.** The OS primitives are fundamentally different:

- macOS: Seatbelt / `sandbox-exec` (kernel sandbox profiles)
- Linux: Namespaces + seccomp + Landlock (kernel isolation primitives)

### How Production Tools Handle This

**Anthropic's `sandbox-runtime`** (the canonical example):
- macOS: `sandbox-exec` with dynamically generated Seatbelt profiles; glob pattern support
- Linux: Landlock (default) or bubblewrap (optional, stronger); literal paths only
- Single TypeScript API: `createSandbox({ allowWrite: [...], allowedDomains: [...] })`
- Abstraction layer translates to platform-specific enforcement

**OpenAI Codex CLI**:
- macOS: `sandbox_init()` / Seatbelt
- Linux: Landlock (default), bubblewrap (optional pipeline)
- Same pattern: unified config, platform-specific enforcement

**Agent Safehouse**:
- macOS only (`sandbox-exec`)
- No Linux support

### Can Nix Be the Unifying Layer?

**For dependency management: Yes.** A Nix flake can declare identical toolchains that work on both macOS and Linux. `nix develop` provides the same PATH, env vars, and tool versions on both platforms.

**For security isolation: No.** Nix has no cross-platform sandboxing primitive. On Linux, Nix-based projects like `bubblewrap-claude` combine Nix + bubblewrap. On macOS, this combination does not work because bubblewrap requires Linux namespaces.

**Recommended architecture:**

```
+-----------------------------------+
|   Unified Configuration Layer     |
| (Nix flake or YAML/TOML config)  |
+-----------------------------------+
           |              |
    +------+------+  +----+--------+
    |  macOS Path |  | Linux Path  |
    | sandbox-exec|  | bubblewrap  |
    | (Seatbelt)  |  | + Landlock  |
    +-------------+  +-------------+
```

This is the exact pattern used by `sandbox-runtime` and Codex CLI. The unified layer is a configuration abstraction (allowed paths, allowed domains, denied operations) that compiles down to platform-specific enforcement.

### The `bubblewrap-claude` Nix Flake as a Template

The [bubblewrap-claude](https://github.com/matgawin/bubblewrap-claude) project demonstrates a practical implementation:
- Nix flake declares packages, environment variables, profiles (per-language)
- `mkSandbox` function wraps the sandbox with bubblewrap arguments
- Network access controlled via HTTP proxy with domain allowlist
- Only project directory and `/tmp` are writable
- Everything else mounted read-only

This works well on Linux. A macOS equivalent would need to swap bubblewrap for `sandbox-exec` profile generation — the Nix-based package management layer would remain the same.

---

## 7. Emerging Tools (2025-2026)

### Alcoholless (NTT Labs)

A lightweight macOS sandbox that runs commands as a separate user with access to a copy of the current directory. Simpler than `sandbox-exec` profile authoring but provides weaker isolation (no kernel-level syscall filtering, just Unix permission separation).

### SandVault

Manages a limited macOS user account to sandbox shell commands and AI agents. Uses Unix user isolation rather than kernel sandboxing. Lightweight alternative to VMs.

### Claude Sandbox (hulsman.dev)

Defense-in-depth sandbox with network namespaces, filesystem bind mounts, domain-filtering egress proxy, and cross-platform Nix packaging. Drives bubblewrap on Linux and generates Seatbelt profiles on macOS.

### `landrun`

"Think firejail, but lightweight, user-friendly, and baked into the kernel." A Go binary that wraps Landlock for easy CLI use. No root required.

---

## 8. Recommendations for SPIKE-009

### For Claude Code CLI Isolation

**Immediate / practical now:**

1. **macOS**: Use `sandbox-exec` with deny-first Seatbelt profiles. This is what Anthropic's own `sandbox-runtime` does. Restrict filesystem writes to project directory + temp, proxy network through domain allowlist. Consider adopting Agent Safehouse's profiles or Anthropic's `sandbox-runtime` npm package.

2. **Linux**: Use bubblewrap with `--unshare-all` for full namespace isolation. Mount project directory writable, everything else read-only. Network via proxy or `--unshare-net` + explicit allowlisting. Landlock as an additional layer.

3. **Unified config**: Abstract the platform-specific enforcement behind a configuration layer (allowed write paths, allowed domains, denied operations). The `sandbox-runtime` package from Anthropic already does this.

**Medium-term:**

4. **Nix as the environment layer**: Use a Nix flake to declare the toolchain (reproducible, hermetic dependencies) and combine with platform-specific sandboxing (sandbox-exec on macOS, bubblewrap on Linux). The `bubblewrap-claude` project is a strong reference implementation for the Linux side.

**Future:**

5. **Apple Containers (macOS 26+)**: When mature, this provides VM-level isolation with container ergonomics and sub-second startup. Worth tracking but not ready.

### What NOT to Rely On

- **`nix develop` alone** for isolation — it provides none
- **Firejail** — larger attack surface than bubblewrap, SUID root concerns
- **`sandbox-exec` long-term stability** — works today, but Apple's deprecation is a risk; monitor each macOS release
- **A single cross-platform tool** — the OS primitives are too different; accept the platform-specific split with a unified config layer

---

## Sources

### Nix
- [Nix 2.28 nix.conf Reference Manual](https://nix.dev/manual/nix/2.28/command-ref/conf-file)
- [NixOS Security Wiki](https://nixos.wiki/wiki/Security)
- [NixOS Discourse: Sandboxing Dev Environments](https://discourse.nixos.org/t/looking-for-a-simple-slightly-paranoid-workflow-to-develop-applications-in-a-sandbox-like-environment/38635)
- [NixOS Discourse: What is sandboxing?](https://discourse.nixos.org/t/what-is-sandboxing-and-what-does-it-entail/15533)
- [NixOS Discourse: Claude Code and Security Isolation](https://discourse.nixos.org/t/claude-code-and-security-isolation/71543)
- [Zero to Nix: Explore nix develop](https://zero-to-nix.com/start/nix-develop/)
- [NixPak: Runtime sandboxing for Nix](https://github.com/nixpak/nixpak)
- [bubblewrap-claude: Nix flake for Claude Code sandboxing](https://github.com/matgawin/bubblewrap-claude)
- [nixwrap: Easy Application Sandboxing on NixOS](https://github.com/rti/nixwrap)

### macOS sandbox-exec
- [sandbox-exec: macOS's Little-Known Sandboxing Tool (igorstechnoclub.com)](https://igorstechnoclub.com/sandbox-exec/)
- [A quick glance at macOS' sandbox-exec (jmmv.dev)](https://jmmv.dev/2019/11/macos-sandbox-exec.html)
- [macOS App sandboxing via sandbox-exec (karltarvas.com)](https://www.karltarvas.com/macos-app-sandboxing-via-sandbox-exec/)
- [sandbox-exec deprecated on macOS (Codex issue #215)](https://github.com/openai/codex/issues/215)
- [HN discussion: sandbox-exec (2025)](https://news.ycombinator.com/item?id=47101200)
- [HN discussion: Seatbelt frustrations](https://news.ycombinator.com/item?id=44283454)
- [Agent Safehouse](https://agent-safehouse.dev/)
- [Agent Safehouse GitHub](https://github.com/eugene1g/agent-safehouse)

### Linux Namespaces / bubblewrap / firejail
- [bubblewrap GitHub](https://github.com/containers/bubblewrap)
- [bubblewrap README](https://github.com/containers/bubblewrap/blob/main/README.md)
- [Bubblewrap ArchWiki](https://wiki.archlinux.org/title/Bubblewrap)
- [Sandboxing for the unprivileged (LWN.net)](https://lwn.net/Articles/686113/)
- [How to Sandbox Linux Apps with Firejail and Bubblewrap](https://www.linuxtechi.com/sandbox-linux-apps-firejail-bubblewrap/)
- [unshare(1) man page](https://man7.org/linux/man-pages/man1/unshare.1.html)

### Landlock
- [Landlock kernel documentation](https://docs.kernel.org/userspace-api/landlock.html)
- [Landlock.io](https://landlock.io/)
- [landrun: Unprivileged Landlock sandbox](https://github.com/Zouuup/landrun)
- [island: Official Landlock sandbox tool](https://github.com/landlock-lsm/island)
- [Sandboxing Network Tools with Landlock](https://domcyrus.github.io/systems-programming/security/linux/2025/12/06/landlock-sandboxing-network-tools.html)

### Apple Containers
- [Apple Open Source Containers](https://opensource.apple.com/projects/container/)
- [apple/container GitHub](https://github.com/apple/container)
- [Meet Containerization - WWDC25](https://developer.apple.com/videos/play/wwdc2025/346/)
- [Apple Native Containerization Deep Dive (kevnu.com)](https://www.kevnu.com/en/posts/apple-native-containerization-deep-dive-architecture-comparisons-and-practical-guide)
- [Apple Containerization (InfoQ)](https://www.infoq.com/news/2025/06/apple-container-linux/)
- [OrbStack vs Apple Containers vs Docker (dev.to)](https://dev.to/tuliopc23/orbstack-vs-apple-containers-vs-docker-on-macos-how-they-really-differ-under-the-hood-53fj)
- [Apple Containers vs Docker Desktop (repoflow.io)](https://www.repoflow.io/blog/apple-containers-vs-docker-desktop-vs-orbstack)

### Claude Code / AI Agent Sandboxing
- [Claude Code Sandboxing Docs](https://code.claude.com/docs/en/sandboxing)
- [Making Claude Code More Secure and Autonomous (Anthropic Engineering)](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [sandbox-runtime GitHub (Anthropic)](https://github.com/anthropic-experimental/sandbox-runtime)
- [sandbox-runtime npm package](https://www.npmjs.com/package/@anthropic-ai/sandbox-runtime)
- [cco (Claude Condom)](https://github.com/nikvdp/cco)
- [Codex CLI Sandboxing](https://developers.openai.com/codex/concepts/sandboxing/)
- [Codex Security](https://developers.openai.com/codex/security/)

### General Sandbox Comparison
- [Let's discuss sandbox isolation (shayon.dev)](https://www.shayon.dev/post/2026/52/lets-discuss-sandbox-isolation/)
- [A field guide to sandboxes for AI (luiscardoso.dev)](https://www.luiscardoso.dev/blog/sandboxes-for-ai)
- [How to sandbox AI agents in 2026 (Northflank)](https://northflank.com/blog/how-to-sandbox-ai-agents)
- [Lobsters: How can we sandbox our development machines?](https://lobste.rs/s/rwgado/how_can_we_sandbox_our_development)
