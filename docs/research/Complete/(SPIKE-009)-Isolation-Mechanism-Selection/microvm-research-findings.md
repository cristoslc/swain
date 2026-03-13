# MicroVM Research Findings for SPIKE-009

**Date**: 2026-03-12
**Scope**: Firecracker, QEMU/Lima/Colima, Cloud Hypervisor/crosvm, filesystem sharing, Apple Virtualization, Docker Sandboxes, libkrun, resource overhead

---

## 1. Firecracker

### Platform Support

**Linux-only, confirmed.** Firecracker requires KVM (Linux Kernel-based Virtual Machine) and cannot run natively on macOS. There is no macOS port and no plan for one.

**macOS workaround**: Run Firecracker inside a Linux VM on macOS. This works with UTM, VMware Fusion, or Lima — but it means nesting: macOS -> Linux VM -> Firecracker microVM -> workload. This adds latency and complexity, and requires nested virtualization support. On Apple Silicon, nested KVM inside an ARM64 Linux guest is possible but fragile.

**Verdict for SPIKE-009**: Firecracker is not viable as a direct isolation mechanism on macOS. It could only participate in a Linux-only path or as a nested option.

### Startup Time

| Scenario | Time |
|----------|------|
| Cold boot (VM only) | <125 ms |
| Snapshot restore | ~4-10 ms |
| Cold boot + app init (Lambda-scale) | 100-200 ms for simple workloads |
| Cold boot + heavy runtime init | 1-7 seconds (dominated by app, not VM) |

The 125ms figure is real and well-documented. However, that measures only the VMM boot — not filesystem mount, networking setup, or application initialization. In AWS Lambda, the total cold start includes runtime init and is typically 1-3 seconds for interpreted languages, 100-200ms for Rust/Go.

Snapshot restore (used by Lambda SnapStart) brings restore to ~4ms for the VM, plus lazy page-fault loading of memory. This is the mechanism that makes Lambda cold starts feel fast.

### Filesystem Sharing

**Firecracker does NOT support virtiofs.** This is a deliberate design choice. The maintainers closed the feature request (issue #1180) and a WIP pull request (#1351) has never been merged. Firecracker supports only **virtio block devices**.

**Workarounds for file sharing**:
- **OverlayFS pattern**: Mount a squashfs base image read-only, overlay with a writable ext4 block device (CoW). Suitable for immutable base + ephemeral writes.
- **Device mapper snapshots**: Host-level CoW using `dmsetup`. Multiple VMs share a base image.
- **Pre-bake images**: Copy project files into a block device image before VM boot. Not suitable for interactive edit-run cycles.
- **Network-based sharing**: NFS or custom vsock-based file server. Adds latency and complexity.

**Verdict**: No way to bind-mount host directories into a Firecracker VM. For an interactive CLI tool that needs real-time read/write of project files, this is a significant limitation.

### Real-World Experience (AWS Lambda, Fly.io)

**AWS Lambda**: Uses Firecracker with pre-baked filesystem images and snapshots. No interactive filesystem sharing — the Lambda function code is baked into the execution environment. Filesystem I/O goes to a local ext4 block device in /tmp. This model works for serverless but not for interactive development.

**Fly.io**: Uses Firecracker for app hosting. VMs boot in milliseconds but operate on pre-deployed container images, not shared host filesystems. When scaling to zero, cold start TTFB depends on application init time, not Firecracker boot time.

**E2B**: Uses Firecracker for AI code sandbox execution. Developed OverlayFS-based disk sharing for density. Their use case is ephemeral execution, not interactive editing.

### Summary Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| macOS support | N/A | Linux-only, requires nested VM on macOS |
| Startup time | Excellent | <125ms cold, ~4ms snapshot |
| Filesystem sharing | Poor | Block devices only, no virtiofs, no bind mounts |
| Interactive dev use | Poor | Not designed for interactive file sharing |
| Security | Excellent | Minimal attack surface, ~50k lines Rust |

---

## 2. QEMU / Lima / Colima

### Lima

Lima is a macOS-focused tool that provisions Linux VMs using either QEMU or Apple's Virtualization.framework (`vz` vmtype). It handles SSH, port forwarding, and filesystem mounts automatically.

**Startup time**:
- With `vz` (Virtualization.framework): ~10-15 seconds for first boot, ~3-5 seconds for subsequent starts
- With QEMU: ~15-30 seconds
- Colima (which uses Lima): ~3-5 seconds on M1 with `vz`

**Docker API compatibility**: Yes. Colima configures the Docker socket so standard `docker` and `docker-compose` CLI commands work without modification. Lima itself can also expose a Docker-compatible socket when running containerd or dockerd inside the VM.

### Filesystem Sharing Options

Lima supports four mount types:

| Mount Type | Default For | Performance | File Watchers | Notes |
|------------|-------------|-------------|---------------|-------|
| **reverse-sshfs** | QEMU (<v1.0) | Moderate | No native inotify; polling required | Stable, battle-tested, configurable cache |
| **9p** | QEMU (>=v1.0) | Poor | Limited inotify (no nested events) | `git status` on medium project: ~30 seconds |
| **virtiofs** | VZ (>=v0.17) | Good | Inotify support experimental (Lima v0.21+) | Requires macOS 13+, Apple Silicon recommended |
| **wsl2** | Windows only | Moderate | Underlying 9p performance | Windows 10 Build 19041+ |

**9p is notably slow**. Benchmarks show:
- Sequential read: 98.6 MB/s bandwidth, 24.6k IOPS
- virtiofs with DAX: 703.1 MB/s bandwidth, 175.7k IOPS (7x faster)
- Real-world: 9p operations taking 600+ seconds for tasks that take 25-40 seconds with Mutagen or 60-80 seconds with virtiofs
- Root cause: O(n) fid lookup in QEMU's 9p implementation (fixed upstream, but fundamental protocol overhead remains)

**virtiofs on Lima with vz** is the best option for macOS. Performance approaches 70-90% of native for reads, with 30-50% overhead on writes.

### Colima Specifics

- Uses Lima under the hood
- Provides `docker`, `containerd`, and `kubernetes` runtimes
- On Apple Silicon with `vz`: achieves 92% of bare-metal container performance (KubeCon 2026 metrics)
- Memory: ~400MB idle (vs Docker Desktop's 2GB+ baseline)
- Full Docker API compatibility: `docker build`, `docker run`, `docker-compose` all work

### Summary Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| macOS support | Excellent | Native, first-class |
| Linux support | Good | Lima runs on Linux too, Colima experimental |
| Startup time | Good | 3-5s with vz, 15-30s with QEMU |
| Filesystem sharing | Good (virtiofs) / Poor (9p) | virtiofs on vz is the path |
| Docker compatibility | Excellent | Drop-in replacement |
| Interactive dev use | Good | virtiofs + inotify (experimental) enables watch-based workflows |

---

## 3. Cloud Hypervisor / crosvm

### Cloud Hypervisor

A Rust-based VMM built on the same rust-vmm crates as Firecracker, but with more features.

| Aspect | Cloud Hypervisor | Firecracker |
|--------|-----------------|-------------|
| Boot time | ~200 ms | ~125 ms |
| Codebase | ~50k lines Rust | ~50k lines Rust |
| virtiofs | Yes (Rust virtiofsd) | No |
| CPU/memory hotplug | Yes | No |
| vhost-user devices | Yes | No |
| macOS support | No (KVM/MSHV only) | No (KVM only) |
| GPU passthrough | Limited | No |

**macOS support**: There is a separate `hypervisor-framework` repo with Rust bindings for Apple's Hypervisor.framework, but Cloud Hypervisor itself does not run on macOS. The bindings are experimental/research-grade.

**Desktop developer use**: Not practical. Cloud Hypervisor targets cloud-native server workloads (Kata Containers, multi-tenant SaaS). No CLI tooling, no filesystem mount helpers, no macOS integration.

### crosvm

Google's VMM for ChromeOS (runs Linux and Android guests). Written in Rust, supports KVM, WHPX (Windows), and HAXM.

| Aspect | crosvm |
|--------|--------|
| Primary platform | ChromeOS / Linux |
| macOS support | No (no Hypervisor.framework backend) |
| virtiofs | Yes |
| Desktop use | ChromeOS Crostini only |
| Developer ergonomics | None for general use |

**Verdict for both**: Neither Cloud Hypervisor nor crosvm are practical for desktop developer isolation. They lack macOS support, developer-facing tooling, and filesystem sharing ergonomics. They are interesting as implementation details inside other tools (e.g., Kata Containers uses Cloud Hypervisor) but not direct options.

---

## 4. Filesystem Sharing Deep Dive

### Comparison Matrix

| Technology | Read Perf (vs native) | Write Perf (vs native) | inotify | Availability | Notes |
|-----------|----------------------|----------------------|---------|-------------|-------|
| **virtiofs (macOS/vz)** | 70-90% | 50-70% | Experimental (Lima v0.21+) | macOS 13+, Apple Silicon | Best option for macOS VMs |
| **virtiofs (Linux/KVM)** | 80-95% | 70-90% | Partial (virtiofsd-dependent) | Linux with QEMU or Cloud Hypervisor | Near-native with DAX |
| **9p** | ~14% of virtiofs | Similar | Limited (no nested events) | QEMU on all platforms | Unusable for large projects |
| **reverse-sshfs** | Moderate | Moderate | No | Lima/Colima | Stable but no file events |
| **Docker virtiofs bind mount** | ~33% of native | ~33% of native | Yes (via host) | Docker Desktop macOS | 3x slower than native (was 5-6x) |
| **Docker synced shares** | ~90% of native | ~90% of native | Delayed sync | Docker Desktop (paid) | Mutagen-based, stores files twice |
| **OrbStack custom FS** | 75-95% of native | 75-95% of native | Likely (custom impl) | OrbStack macOS | Proprietary, best-in-class on macOS |
| **NFS** | Moderate | Moderate | No | Universal | Network overhead, stale caches |
| **Block device (ext4)** | ~100% of native | ~100% of native | Yes (local) | Firecracker, QEMU | No host sharing — files baked in |

### File Watcher / inotify Details

File watchers are critical for development tools (hot reload, test runners, IDE integration). The situation across VM filesystem sharing:

- **virtiofs**: Does NOT natively support inotify across the VM boundary. The virtiofsd daemon would need to translate host FSEvents/inotify into guest inotify events. Lima added experimental `mountInotify` support in v0.21, which works across mount types but has limitations (9p misses nested file events).
- **9p**: Limited inotify support. Nested directory events are not propagated.
- **sshfs**: No inotify. Tools must fall back to polling (e.g., `--poll` flag in webpack, `usePolling: true` in chokidar).
- **OrbStack**: Maintains a fork of Go's `fsnotify` library (`orbstack/fsnotify-macvirt`) suggesting they've built custom cross-VM notification support. Likely the best option for file watchers, but proprietary.
- **Docker Desktop**: File watchers work on bind mounts because the Docker VM forwards inotify events. Performance depends on the number of watched files.

**Key insight**: FUSE-based and network-based filesystems (NFS, SMB, FUSE, /proc, /sys) fundamentally do not support kernel-level inotify. The `fsnotify` Go library documentation explicitly states this. Any solution must either implement a custom notification channel or rely on polling.

### Performance Numbers in Context

For a typical Node.js project (`npm install` in a directory with thousands of files):

| Setup | Approximate Time |
|-------|-----------------|
| Native macOS (APFS) | ~10 seconds |
| OrbStack bind mount | ~12 seconds (88% native) |
| Docker Desktop virtiofs | ~30 seconds (3x native) |
| Docker synced shares | ~11 seconds (~native) |
| Lima/Colima virtiofs (vz) | ~15-20 seconds (estimated) |
| Lima 9p | Minutes (unusable) |

---

## 5. macOS Virtualization

### Apple Virtualization.framework

Available since macOS 12 (Monterey), with significant improvements in macOS 13+. Provides:

- **Lightweight Linux VM hosting** with ARM64 guest support
- **virtiofs** for host-guest filesystem sharing (`VZVirtioFileSystemDeviceConfiguration`)
- **Rosetta integration** for running x86_64 binaries in ARM64 Linux guests
- **virtio-net** for networking with NAT or bridged modes
- **Memory ballooning** for dynamic memory management

This is the underlying technology used by Lima (`vz` vmtype), OrbStack, Docker Desktop (partially), and now Apple Containers.

### Apple Containers (WWDC 2025, macOS 26 Tahoe)

Apple announced a first-party containerization framework with a fundamentally different architecture:

| Aspect | Apple Containers | Docker Desktop | OrbStack |
|--------|-----------------|----------------|----------|
| Architecture | 1 VM per container | 1 shared VM | 1 shared VM |
| Isolation | VM-level per container | Namespace/cgroup | Namespace/cgroup |
| Startup | ~200-300 ms per container | Seconds (first container) | Milliseconds (after VM up) |
| Filesystem | EXT4 block devices | virtiofs bind mounts | Custom FS |
| File sharing | virtiofs for specific mounts | virtiofs bind mounts | Proprietary |
| License | Open source (Swift) | Freemium/commercial | Commercial |
| Docker compat | No (OCI images, no Docker API) | Yes (is Docker) | Yes |
| Status | Preview (macOS 26 beta) | Stable | Stable |

**Key difference**: Apple Containers gives each container its own lightweight VM (like a microVM). This provides VM-level isolation without a shared kernel. The filesystem uses EXT4 block devices (not shared mounts), with optional virtiofs for specific host directory sharing.

**Relevance to SPIKE-009**: Apple Containers is architecturally the closest thing to "Firecracker on macOS" — lightweight VMs with strong isolation and fast startup. However:
- macOS 26 only (not yet released, beta expected mid-2026)
- No Docker API compatibility (different CLI, different ecosystem)
- Filesystem sharing model unclear for interactive development workflows
- Very early — not production-ready for at least 6-12 months

### How Tools Use Virtualization.framework

| Tool | Uses Virt.framework? | How |
|------|---------------------|-----|
| **Lima** | Yes (`vz` vmtype) | Full Linux VM with virtiofs mounts |
| **OrbStack** | Yes | Single optimized Linux VM, custom FS layer |
| **Docker Desktop** | Partially | Uses it alongside custom QEMU for some features |
| **Apple Containers** | Yes | One lightweight VM per container |
| **UTM** | Yes (optional) | General-purpose VM manager |

---

## 6. Resource Overhead

### Memory

| Technology | Per-Instance Overhead | Typical Idle Memory |
|-----------|----------------------|-------------------|
| Docker container (Linux) | ~few KB (cgroup metadata) | Depends entirely on process |
| Docker Desktop (macOS) | N/A (shared VM) | 2+ GB for the VM |
| Colima VM | N/A (shared VM) | ~400 MB for the VM |
| OrbStack VM | N/A (shared VM) | ~200-300 MB for the VM |
| Firecracker microVM | <5 MiB per VM | 5 MiB + guest workload |
| Cloud Hypervisor | Similar to Firecracker | ~200ms boot, low overhead |
| Apple Container (VM-per-container) | TBD (early) | Claimed "minimal" per Apple |

**Key insight**: The comparison is nuanced. A Docker container on Linux has near-zero virtualization overhead but shares the host kernel. A Docker container on macOS has the overhead of the entire Docker Desktop VM (2+ GB) shared across all containers. A microVM has ~5MB overhead per instance but provides full kernel isolation.

For a single Claude Code isolation session, the relevant comparison is:
- **Docker on macOS**: ~2GB for Docker Desktop VM + minimal per-container
- **Lima/Colima**: ~400MB for the VM + minimal per-container
- **OrbStack**: ~200-300MB for the VM + minimal per-container
- **Firecracker (if on Linux)**: ~5MB per microVM + guest memory allocation

### CPU Overhead

- **Containers**: Near-zero CPU overhead. Processes run natively on the host kernel.
- **VMs (KVM/Virt.framework)**: <2% CPU overhead for compute workloads thanks to hardware virtualization (VT-x, ARM VHE). The overhead is in VM exits for I/O operations.
- **MicroVMs specifically**: Same as VMs — the "micro" refers to minimal device emulation, not less CPU overhead.
- **Filesystem I/O**: This is where overhead concentrates. Cross-VM filesystem operations (virtiofs, 9p) add 10-70% overhead depending on the mechanism.

### Is the Overhead Justified?

| Threat Model | Container Sufficient? | VM Needed? |
|-------------|----------------------|-----------|
| Prevent accidental `rm -rf /` | Yes | No |
| Isolate untrusted npm packages | Marginal (shared kernel) | Recommended |
| Run arbitrary agent-generated shell commands | No (container escapes exist) | Yes |
| Protect host credentials/SSH keys | Yes (if volumes controlled) | Better with VM |
| Defense against kernel exploits | No | Yes |

For Claude Code running arbitrary shell commands from an AI agent, **VM-level isolation is recommended** but container-level isolation is likely sufficient for the threat model (protecting against accidental damage, not adversarial attack). The practical question is whether the filesystem performance tradeoff is acceptable.

---

## 7. Docker Sandboxes (Docker Desktop 4.58+)

### Overview

Docker launched an evolved version of Docker Sandboxes in early 2026 with microVM-based isolation specifically designed for AI coding agents. This is the most directly relevant product for Claude Code isolation.

### Architecture

Each sandbox runs inside a dedicated microVM with its own private Docker daemon. The architecture uses platform-native hypervisors:

- **macOS**: Apple Virtualization.framework
- **Windows**: Hyper-V (experimental)
- **Linux**: Legacy container-based sandboxes only (no microVM), requires Docker Desktop 4.57+. Experimental single-user support (UID 1000) added recently.

The agent runs inside the VM and cannot access the host Docker daemon, containers, or files outside the workspace. Each sandbox has its own private network namespace and isolated Docker image caches.

### Filesystem Sharing

Docker Sandboxes uses **file synchronization, not volume mounting**. Files are copied between host and VM. The workspace syncs to the sandbox at the same absolute path, so file paths in error messages match between environments. This is a deliberate design choice that trades some consistency for stronger isolation.

### Network Isolation

- Sandboxes cannot communicate with each other
- Outbound internet access flows through an HTTP/HTTPS filtering proxy at `host.docker.internal:3128`
- Allow and deny lists for controlling agent network access
- Credentials injected transparently by the proxy, never stored in the VM
- Port exposure to host device is on the roadmap but not yet available

### Supported Agents

Production-ready: Claude Code. In development: Codex, Copilot, Gemini, OpenCode, Docker Agent, Kiro.

### Performance Characteristics

- **Startup**: No official benchmarks published. Blog states "spin up fresh one in seconds" and "fast reset capability."
- **Resource overhead**: Documentation acknowledges "Sandboxes trade higher resource overhead (VM + daemon) for complete isolation." Each sandbox runs its own Docker daemon and maintains separate image caches.
- **Filesystem**: Sync-based approach means files are copied, not mounted. Performance depends on workspace size and sync frequency. No specific benchmark numbers published.

### Docker-in-Docker

Docker Sandboxes is described as "the only sandboxing solution that allows coding agents to build and run Docker containers while remaining isolated from the host system." The private Docker daemon inside the sandbox enables full `docker build`, `docker run`, and `docker-compose` workflows.

### Licensing

Requires Docker Desktop. Free for organizations under 250 employees AND under $10M revenue; otherwise ~$21/user/month (Docker Business).

### Real-World Assessment (Infralovers, Feb 2026)

An independent evaluation scored Docker Sandboxes 8.1/10 across weighted criteria (security, performance, developer experience). Key findings:

- Approaches "just works" experience for Claude Code
- Reduces permission prompts by ~84% with built-in `/sandbox` path
- npm install benchmark on M4 Pro with bind mounts: Docker Desktop (VZ + sync, paid) at 3.88s vs Lima at 8.99s vs standard Docker Desktop at 9.53s
- Main concern: licensing cost for larger organizations

### Summary Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| macOS support | Excellent | Native via Virtualization.framework |
| Linux support | Poor | Legacy container-only, no microVM isolation |
| Startup time | Good | "Seconds" (unquantified) |
| Filesystem sharing | Good | Sync-based, path-preserving |
| Docker compatibility | Excellent | Full Docker-in-Docker support |
| Interactive dev use | Good | Built for AI agent workflows |
| Security | Excellent | microVM isolation + network filtering |
| Cost | Moderate | Requires Docker Desktop license |

---

## 8. libkrun (Bonus: macOS-Native MicroVMs)

### Overview

libkrun is a dynamic library (from the Containers project, backed by Red Hat) that allows programs to run processes in a partially isolated environment using hardware virtualization — KVM on Linux, Hypervisor.framework (HVF) on macOS/ARM64. It embeds a minimal VMM with the absolute minimum emulated devices required.

### macOS Support

Unlike Firecracker and Cloud Hypervisor, libkrun **does** run natively on macOS ARM64 via Apple's Hypervisor.framework. The companion tool `krunkit` provides a command-line interface for launching lightweight VMs.

### Key Features

- **GPU passthrough on macOS**: Via Mesa's Venus Vulkan driver, enabling GPU workloads inside the guest VM
- **Lima integration**: Lima supports `krunkit` as a VM type, meaning Lima's filesystem sharing and Docker compatibility can run on top of libkrun VMs
- **Minimal footprint**: Designed for process-level isolation with low overhead

### Relevance to SPIKE-009

libkrun is interesting as an alternative to Apple's Virtualization.framework for the underlying VM layer. However, for Claude Code isolation, it's most relevant as an implementation detail inside Lima or Podman rather than a direct tool. RamaLama (Red Hat's AI model runner) uses libkrun for AI workload isolation, which validates the approach for agent-adjacent use cases.

---

## 9. Recommendations for SPIKE-009

### Tier 1: Practical Now

1. **Docker Sandboxes (macOS/Windows)**: Purpose-built for AI agent isolation. MicroVM-based isolation via Virtualization.framework, file sync (not mount), network filtering proxy, Docker-in-Docker support. Scored 8.1/10 in independent evaluation. Requires Docker Desktop license. **Best option if already using Docker Desktop and targeting macOS.** Linux support is container-only (no microVM), which weakens the isolation story on Linux.

2. **Docker via Colima/OrbStack (macOS) + Docker native (Linux)**: Best developer experience for general Docker workflows. Startup in seconds, Docker API compatibility, reasonable filesystem performance with virtiofs. Container-level isolation (not VM-level), but sufficient for most threat models.

3. **OrbStack (macOS only)**: Best filesystem performance (75-95% native), lowest resource usage (~200MB), fastest startup (~2s). Commercial, macOS-only. Container-level isolation only.

### Tier 2: Better Isolation, More Friction

4. **Lima with vz + virtiofs (macOS)**: VM-level isolation with decent filesystem sharing. Slower startup (10-15s) and more complex setup than Docker, but stronger isolation boundary. Good for "defense in depth" approach. Open source, no licensing cost.

### Tier 3: Future Options

5. **Apple Containers (macOS 26+)**: VM-per-container architecture with sub-second startup. Closest to "microVM for developers on macOS." Not available until late 2026 at earliest. No Docker API compatibility.

6. **Firecracker (Linux only)**: Excellent for Linux CI/server environments. Not viable on macOS without nesting.

### Not Recommended

- **9p-based filesystem sharing**: Too slow for interactive use
- **Cloud Hypervisor / crosvm**: No macOS support, no developer tooling
- **Firecracker on macOS (via nested VM)**: Too much complexity and fragility for the isolation benefit

---

## Sources

### Firecracker
- [Firecracker GitHub](https://github.com/firecracker-microvm/firecracker)
- [Host Filesystem Sharing Issue #1180](https://github.com/firecracker-microvm/firecracker/issues/1180)
- [VirtioFS PR #1351](https://github.com/firecracker-microvm/firecracker/pull/1351)
- [Firecracker vs QEMU (E2B)](https://e2b.dev/blog/firecracker-vs-qemu)
- [Firecracker vs Docker Technical Boundary (HuggingFace)](https://huggingface.co/blog/agentbox-master/firecracker-vs-docker-tech-boundary)
- [Scaling Firecracker with OverlayFS (E2B)](https://e2b.dev/blog/scaling-firecracker-using-overlayfs-to-save-disk-space)
- [Firecracker Internals (Tal Hoffman)](https://www.talhoffman.com/2021/07/18/firecracker-internals/)
- [Seven Years of Firecracker (Marc Brooker)](https://brooker.co.za/blog/2025/09/18/firecracker.html)
- [Start a VM in less than a second (Julia Evans)](https://jvns.ca/blog/2021/01/23/firecracker--start-a-vm-in-less-than-a-second/)
- [Firecracker for Students (Tutorials Dojo)](https://tutorialsdojo.com/firecracker-for-students-launch-your-first-microvm-on-any-os/)

### Lima / Colima
- [Lima Filesystem Mounts Documentation](https://lima-vm.io/docs/config/mount/)
- [Lima GitHub](https://github.com/lima-vm/lima)
- [Colima GitHub](https://github.com/abiosoft/colima)
- [Colima FAQ](https://github.com/abiosoft/colima/blob/main/docs/FAQ.md)
- [Colima 9p Performance Issue #544](https://github.com/abiosoft/colima/issues/544)
- [Lima v1.0 Mount Default Change Issue #971](https://github.com/lima-vm/lima/issues/971)
- [How to Choose Between Colima and Docker Desktop (OneUpTime)](https://oneuptime.com/blog/post/2026-02-08-how-to-choose-between-colima-and-docker-desktop-on-macos/view)
- [Migrating from Docker Desktop to Colima 2025](https://code.saghul.net/2025/02/migrating-from-docker-desktop-to-colima-2025-update/)

### Apple Virtualization / Containers
- [Apple Virtualization Framework Documentation](https://developer.apple.com/documentation/virtualization)
- [VZVirtioFileSystemDeviceConfiguration](https://developer.apple.com/documentation/virtualization/vzvirtiofilesystemdeviceconfiguration)
- [Meet Containerization - WWDC25](https://developer.apple.com/videos/play/wwdc2025/346/)
- [Apple Containerization Deep Dive (kevnu.com)](https://www.kevnu.com/en/posts/apple-native-containerization-deep-dive-architecture-comparisons-and-practical-guide)
- [Apple Containerization (InfoQ)](https://www.infoq.com/news/2025/06/apple-container-linux/)
- [Apple Containerization (The Register)](https://www.theregister.com/2025/06/10/apple_tries_to_contain_itself/)
- [Apple Containers vs Docker Desktop (4sysops)](https://4sysops.com/archives/apple-container-vs-docker-desktop/)
- [Container Revolution on macOS: 2025 Landscape](https://thamizhelango.medium.com/container-revolution-on-macos-the-2025-landscape-96e666833552)

### OrbStack
- [OrbStack Fast Filesystem Blog](https://orbstack.dev/blog/fast-filesystem)
- [OrbStack vs Docker Desktop Docs](https://orbstack.dev/docs/compare/docker-desktop)
- [OrbStack fsnotify-macvirt Fork](https://github.com/orbstack/fsnotify-macvirt)
- [OrbStack vs Docker Desktop (sliplane)](https://sliplane.io/blog/orbstack-vs-docker)

### Cloud Hypervisor / crosvm
- [Cloud Hypervisor GitHub](https://github.com/cloud-hypervisor/cloud-hypervisor)
- [Cloud Hypervisor Guide 2026 (Northflank)](https://northflank.com/blog/guide-to-cloud-hypervisor)
- [crosvm Documentation](https://crosvm.dev/book/hypervisors.html)
- [Cloud Hypervisor macOS Hypervisor Framework](https://github.com/cloud-hypervisor/hypervisor-framework)

### Performance / Benchmarks
- [Docker on macOS Performance 2025 (Paolo Mainardi)](https://www.paolomainardi.com/posts/docker-performance-macos-2025/)
- [virtiofs vs 9p Performance (Red Hat mailing list)](https://listman.redhat.com/archives/virtio-fs/2020-September/msg00130.html)
- [QEMU 9p Performance Fix (Linus Heckemann)](https://linus.schreibt.jetzt/posts/qemu-9p-performance.html)
- [Docker Desktop Synchronized File Shares](https://www.docker.com/blog/announcing-synchronized-file-shares/)
- [VirtioFS in Docker Desktop 4.6](https://www.docker.com/blog/speed-boost-achievement-unlocked-on-docker-desktop-4-6-for-mac/)
- [Inotify Support in FUSE and virtiofs (LWN)](https://lwn.net/Articles/874000/)
- [MicroVMs: Scaling Out (OpenMetal)](https://openmetal.io/resources/blog/microvms-scaling-out-over-scaling-up/)

### Docker Sandboxes
- [Docker Sandboxes: Run Claude Code and More Safely (Blog)](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/)
- [Docker Sandboxes Documentation](https://docs.docker.com/ai/sandboxes/)
- [Docker Sandboxes Architecture](https://docs.docker.com/ai/sandboxes/architecture/)
- [Docker Sandboxes Get Started](https://docs.docker.com/ai/sandboxes/get-started/)
- [Docker Sandboxes Product Page](https://www.docker.com/products/docker-sandboxes/)
- [A New Approach for Coding Agent Safety (Docker Blog)](https://www.docker.com/blog/docker-sandboxes-a-new-approach-for-coding-agent-safety/)
- [Sandboxing Claude Code on macOS (Infralovers)](https://www.infralovers.com/blog/2026-02-15-sandboxing-claude-code-macos/)

### libkrun
- [libkrun GitHub](https://github.com/containers/libkrun)
- [Supercharging AI isolation: microVMs with RamaLama & libkrun (Red Hat)](https://developers.redhat.com/articles/2025/07/02/supercharging-ai-isolation-microvms-ramalama-libkrun)
- [Krunkit Lima Integration](https://lima-vm.io/docs/config/vmtype/krunkit/)
- [GPU-Accelerated Containers for Apple Silicon](https://medium.com/@andreask_75652/gpu-accelerated-containers-for-m1-m2-m3-macs-237556e5fe0b)

### Sandbox Isolation Comparison
- [Let's Discuss Sandbox Isolation (shayon.dev)](https://www.shayon.dev/post/2026/52/lets-discuss-sandbox-isolation/)
- [How to Sandbox AI Agents (Northflank)](https://northflank.com/blog/how-to-sandbox-ai-agents)
- [Benchmarking Apple Containers vs Docker Desktop (Repoflow)](https://www.repoflow.io/blog/benchmarking-apple-containers-vs-docker-desktop)
- [Apple Containers vs Docker Desktop vs OrbStack (Repoflow)](https://www.repoflow.io/blog/apple-containers-vs-docker-desktop-vs-orbstack)

### AWS Lambda / Serverless
- [AWS Lambda Cold Starts 2025 (EdgeDelta)](https://edgedelta.com/company/knowledge-center/aws-lambda-cold-start-cost)
- [Lambda SnapStart with Firecracker (ElasticScale)](https://elasticscale.com/blog/aws-lambda-snapstart-reducing-cold-start-times-with-firecracker/)
- [Fly Machines Blog](https://fly.io/blog/fly-machines/)
