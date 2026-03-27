---
title: "Credential Scoping Analysis Across Sandbox Types"
artifact: SPIKE-031
track: container
status: Complete
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-011
parent-vision: VISION-002
question: "Can Tier 1 native sandbox (Seatbelt/Landlock) provide credential isolation equivalent to Docker Sandboxes, or is it inherently leakier because it shares the host environment?"
gate: Pre-MVP
risks-addressed:
  - Unattended agent inherits operator's full credential set
  - No documented comparison of credential isolation properties across sandbox types
trove: "sandbox-runtime source (anthropic-experimental/sandbox-runtime), Claude Code sandboxing docs, Docker Sandboxes architecture docs, Seatbelt SBPL reference, Landlock kernel docs, bubblewrap man pages, CVE-2025-55284, CVE-2025-59536, CVE-2026-21852"
linked-artifacts:
  - EPIC-005
  - SPEC-067
  - SPEC-071
depends-on-artifacts: []
---

# Credential Scoping Analysis Across Sandbox Types

## Summary

**Verdict: Conditional Go** -- Native sandbox (Seatbelt/Landlock) cannot restrict environment variable access at the OS-sandbox layer, but the `env -i` wrapper technique provides application-level credential scoping that meets the threshold. The combination of `env -i VAR=val ... claude --sandbox` restricts the sandboxed process to an explicit allowlist of environment variables (fewer than 3 credential keys), satisfying the gate criteria. However, this is defense-in-depth at the process-launch layer, not at the kernel-sandbox layer, making it weaker than Docker Sandboxes' proxy-managed credential injection where credentials never enter the execution environment at all.

**Recommendation:** Native sandbox with `env -i` wrapper is sufficient for **attended** and **lightly-unattended** use (operator can review session output). For fully unattended execution where the agent could be prompt-injected into exfiltrating env vars via allowed network egress, Docker Sandboxes remains the stronger posture because credentials are injected per-request by the MITM proxy and never exist in the agent's environment.

## Question

Can Tier 1 native sandbox (Seatbelt/Landlock) provide credential isolation equivalent to Docker Sandboxes, or is it inherently leakier because it shares the host environment?

## Go / No-Go Criteria

- **Go (native is sufficient):** Seatbelt/Landlock can restrict environment variable access and keychain reads to a defined allowlist, preventing agents from accessing credentials beyond what's explicitly granted.
- **No-Go (native is insufficient):** Native sandbox shares the host environment unconditionally — any env var or keychain entry accessible to the user is accessible to the sandboxed agent.
- **Threshold:** If native sandbox cannot restrict credential access to fewer than 3 specific keys (API token, git token, optional secondary), it fails the gate.

## Pivot Recommendation

If native sandbox cannot scope credentials: recommend Docker Sandboxes as the only supported unattended execution mode, with Tier 1 relegated to attended-only use. Document the security gap clearly in the architecture overview.

## Findings

### 1. macOS Seatbelt (sandbox-exec) and Environment Variables

**Finding: Seatbelt cannot restrict environment variable access.**

The Seatbelt sandbox operates via SBPL (Sandbox Profile Language) profiles -- a Scheme-like DSL that controls filesystem, network, process, and IPC operations. The SBPL language has **no operations for environment variable filtering**. Seatbelt profiles can deny file reads, network connections, and mach port lookups, but environment variables exist in-process memory and are outside Seatbelt's enforcement scope.

When `sandbox-exec -p <profile> <command>` launches a process, the child inherits the full parent environment unconditionally. The SBPL profile has no mechanism analogous to `(deny env-read)` or `(allow env-read (variable "ANTHROPIC_API_KEY"))`.

**Confirmed by source analysis:** The `anthropic-experimental/sandbox-runtime` macOS implementation ([macos-sandbox-utils.ts](https://github.com/anthropic-experimental/sandbox-runtime)) invokes `env ... sandbox-exec -p <profile> <shell> -c <command>` and does NOT clear inherited environment variables. It only _adds_ proxy-related vars (HTTP_PROXY, HTTPS_PROXY, etc.) on top of whatever the parent process already has.

Third-party tools (e.g., ai-jail) implement "lockdown mode" by calling `cmd.env_clear()` at the application level _before_ spawning the sandboxed process, then selectively restoring PATH, HOME, and TERM. This is process-level mitigation, not Seatbelt enforcement.

**Sources:**
- [DeepWiki: macOS Seatbelt Sandboxing (ai-jail)](https://deepwiki.com/akitaonrails/ai-jail/4.5-macos:-seatbelt-sandboxing)
- [sandbox-exec overview (Igor's Techno Club)](https://igorstechnoclub.com/sandbox-exec/)
- [anthropic-experimental/sandbox-runtime source](https://github.com/anthropic-experimental/sandbox-runtime)
- [Pierce Freeman: Deep Dive on Agent Sandboxes](https://pierce.dev/notes/a-deep-dive-on-agent-sandboxes)

### 2. Linux Landlock and Environment Variables

**Finding: Landlock cannot restrict environment variable access.**

Landlock is a Linux Security Module (LSM) that provides unprivileged filesystem and network access control. As of ABI v5, Landlock can restrict:
- Filesystem operations (read, write, execute, truncate, ioctl)
- TCP bind and connect (by port number)
- Abstract UNIX socket and signal scoping (IPC)

Landlock explicitly **does not** cover environment variables. The [kernel documentation](https://docs.kernel.org/userspace-api/landlock.html) scopes Landlock to "access control on kernel objects" and defers syscall-level filtering to seccomp-bpf. Environment variables are process memory, not kernel objects, so they fall outside Landlock's domain entirely.

**Sources:**
- [Landlock kernel documentation](https://docs.kernel.org/userspace-api/landlock.html)
- [Landlock userspace API](https://docs.kernel.org/userspace-api/landlock.html)
- [landlock.io](https://landlock.io/)

### 3. Linux Bubblewrap and Environment Variables

**Finding: Bubblewrap CAN restrict environment variables via `--clearenv` + `--setenv`.**

Bubblewrap provides explicit environment control:
- `--clearenv` -- Unsets all environment variables except PWD
- `--setenv VAR VALUE` -- Sets a specific variable in the sandbox
- `--unsetenv VAR` -- Removes a specific variable

The combination `bwrap --clearenv --setenv ANTHROPIC_API_KEY <val> --setenv PATH <val> --setenv HOME <val> ...` produces a sandbox where only the explicitly named variables exist. This is a true allowlist.

**However, Claude Code's sandbox-runtime does NOT use `--clearenv`.** The [linux-sandbox-utils.ts](https://github.com/anthropic-experimental/sandbox-runtime) source constructs bwrap arguments with `--setenv` for proxy variables but never invokes `--clearenv`. The parent shell environment is fully inherited by the sandboxed process.

This means the _capability_ exists in bubblewrap but is unused by the current `claude --sandbox` implementation.

**Sources:**
- [bwrap(1) man page](https://manpages.debian.org/testing/bubblewrap/bwrap.1.en.html)
- [Bubblewrap ArchWiki](https://wiki.archlinux.org/title/Bubblewrap)
- [anthropic-experimental/sandbox-runtime source](https://github.com/anthropic-experimental/sandbox-runtime)
- [containers/bubblewrap Issue #281 (clearenv)](https://github.com/containers/bubblewrap/issues/281)

### 4. Docker Sandboxes Credential Injection Model

**Finding: Docker Sandboxes provide strong credential isolation via MITM proxy -- credentials never enter the VM.**

Docker Sandboxes use a fundamentally different credential model:

1. **MITM proxy** runs on the host at `host.docker.internal:3128`
2. Agent VM makes API requests **without credentials** -- outbound traffic is routed through the proxy
3. Proxy intercepts requests, matches the destination (api.anthropic.com, api.github.com, api.openai.com, etc.), and **injects the appropriate auth header** from host-side credential storage
4. Credentials are read from the operator's shell profile (~/.zshrc, ~/.bashrc) by the Docker Desktop daemon at startup, **not from the current shell session**
5. Host env vars are **not passed into the sandbox VM** -- the proxy tells agents to set placeholder values (e.g., `apiKeyHelper: "echo proxy-managed"`)
6. When the sandbox is deleted, no credentials remain

This architecture provides the strongest credential scoping: the agent process literally cannot access the credential values, only the proxy can. Even if the agent is compromised via prompt injection, it cannot exfiltrate credentials from its own environment because they are not there.

**Limitation:** The MITM proxy breaks OAuth/OIDC flows (docker/desktop-feedback#198) because it terminates TLS. This means Claude Max/Pro subscription auth does not work -- only API key auth is supported.

**Sources:**
- [Docker Sandboxes Architecture](https://docs.docker.com/ai/sandboxes/architecture/)
- [Docker Agent Sandbox docs](https://docs.docker.com/ai/sandboxes/agents/docker-agent/)
- [Docker Sandboxes Network Policies](https://docs.docker.com/ai/sandboxes/network-policies/)

### 5. `claude --sandbox` Environment Variable Passthrough

**Finding: `claude --sandbox` passes through all host environment variables.**

Confirmed via source code analysis of `anthropic-experimental/sandbox-runtime`:

- **macOS (Seatbelt):** The sandbox is invoked as `env <proxy_vars> sandbox-exec -p <profile> <shell> -c <command>`. No `env -i` or `env_clear()` is used. The child process inherits the full parent environment plus injected proxy variables.

- **Linux (Bubblewrap):** The sandbox is invoked with `bwrap --setenv <proxy_vars> ... <command>`. No `--clearenv` is used. The child process inherits the full parent environment plus injected proxy variables.

This is a confirmed security gap: any environment variable set in the operator's shell (ANTHROPIC_API_KEY, GITHUB_TOKEN, AWS_SECRET_ACCESS_KEY, database credentials, etc.) is visible to the sandboxed agent and could be exfiltrated via allowed network egress or even via DNS requests (CVE-2025-55284).

Known CVEs related to Claude Code credential exposure:
- **CVE-2025-59536** (CVSS 8.7): RCE via malicious project hooks that can access env vars
- **CVE-2026-21852**: Settings file can redirect API requests to attacker-controlled endpoint, leaking API keys
- **CVE-2025-55284**: Data exfiltration via DNS requests (bypasses network sandbox)

**Sources:**
- [anthropic-experimental/sandbox-runtime source](https://github.com/anthropic-experimental/sandbox-runtime)
- [Claude Code Sandboxing docs](https://code.claude.com/docs/en/sandboxing)
- [Anthropic engineering: Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- [CVE-2025-55284: DNS exfiltration](https://embracethered.com/blog/posts/2025/claude-code-exfiltration-via-dns-requests/)
- [CVE-2025-59536 / CVE-2026-21852 (Check Point Research)](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)
- [Claude Code env var exposure issue #11271](https://github.com/anthropics/claude-code/issues/11271)

### 6. Application-Level Mitigation: `env -i` Wrapper

**Finding: `env -i` provides effective application-level credential scoping for native sandbox.**

The POSIX `env -i` command launches a process with an empty environment. Combined with explicit variable assignments, it creates an allowlisted environment:

```sh
env -i \
  HOME="$HOME" \
  PATH="/usr/local/bin:/usr/bin:/bin" \
  ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  claude --sandbox
```

This technique:
- Strips ALL inherited env vars (AWS keys, database passwords, other tokens)
- Passes only the explicitly named variables
- Works on both macOS and Linux
- Is composable with both Seatbelt and Bubblewrap sandboxing
- Can restrict to fewer than 3 credential keys (meeting the threshold)

**Caveats:**
- Defense is at the process-launch layer, not kernel-enforced. If the agent can escape the sandbox and spawn a new process outside it, the operator's full env is accessible from parent processes.
- The `env -i` wrapper must be applied by the launcher (e.g., swain-box), not by claude itself.
- Some tools may break without expected env vars (TERM, LANG, USER, SHELL, TMPDIR, etc.). Testing required per runtime.
- Does NOT protect against credentials stored in files (~/.netrc, ~/.aws/credentials, keychain) -- only env var scoping.

**Sources:**
- [env -i on Linux](https://www.linuxbash.sh/post/run-a-command-in-a-restricted-environment-with-env--i)
- [env(1) man page](https://www.geeksforgeeks.org/linux-unix/env-command-in-linux-with-examples/)

### Comparison Matrix

| Property | Native Sandbox (`claude --sandbox`) | Native + `env -i` Wrapper | Docker Sandboxes |
|---|---|---|---|
| **Env var inheritance** | Full passthrough | Allowlist only | None (proxy-managed) |
| **Credential in agent memory** | Yes (all host env vars) | Yes (only allowlisted vars) | No (proxy injects per-request) |
| **Enforcement layer** | None for env vars | Process launch (application) | VM boundary + MITM proxy (hypervisor) |
| **Exfiltration via network** | Possible (allowed domains) | Possible (allowed domains) | Blocked (proxy filters egress) |
| **Exfiltration via DNS** | Possible (CVE-2025-55284) | Possible for allowlisted vars | Blocked (VM network isolation) |
| **File-based credentials** | Accessible (~/.aws, ~/.netrc) | Accessible (~/.aws, ~/.netrc) | Not accessible (separate VM filesystem) |
| **Keychain access** | Accessible (user keychain) | Accessible (user keychain) | Not accessible (no host keychain) |
| **Credential count restriction** | No limit (all env vars) | Operator-defined allowlist | Proxy-defined provider list |
| **OAuth support** | Yes | Yes | No (MITM breaks TLS pinning) |
| **Meets threshold (<3 keys)** | No | Yes | Yes |
| **Startup overhead** | Near-zero | Near-zero | ~2-5s (VM boot) |
| **Platform support** | macOS + Linux | macOS + Linux | macOS + Linux (Docker Desktop) |

### Residual Risks by Tier

**Native + `env -i` (Tier 1 hardened):**
- File-based credential access (~/.aws/credentials, ~/.ssh/*, ~/.netrc, keychain)
- DNS exfiltration of allowlisted credentials
- Sandbox escape to parent process environment
- Seatbelt profile bypass (sandbox-exec is deprecated by Apple)

**Docker Sandboxes (Tier 2):**
- OAuth authentication broken (docker/desktop-feedback#198)
- Proxy misconfiguration could leak credentials to wrong provider
- VM escape (theoretical, very high bar)
- Docker Desktop dependency (not available on headless CI without desktop)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Created for INITIATIVE-011 decomposition |
| Complete | 2026-03-19 | — | Conditional Go — env -i wrapper meets threshold; Docker Sandboxes remains stronger |
