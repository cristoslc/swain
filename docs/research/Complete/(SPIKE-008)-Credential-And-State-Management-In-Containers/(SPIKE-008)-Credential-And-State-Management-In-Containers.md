---
title: "Credential and State Management in Isolated Environments"
artifact: SPIKE-008
track: container
status: Complete
author: cristos
created: 2026-03-12
last-updated: 2026-03-14
question: "How should credentials, git configuration, and agent state be forwarded into ephemeral isolated environments while keeping storage filesystem-bound?"
gate: Pre-MVP
risks-addressed:
  - API keys baked into images would be a security risk
  - Git commit signing (SSH keys) may not transfer cleanly into isolated environments
  - Agent state directories (.claude/, .agents/, .tickets/) need to survive environment restarts
  - gh CLI auth tokens live in host-specific paths that differ inside the environment
trove:
linked-artifacts:
  - EPIC-005
  - SPEC-023
  - SPEC-024
  - SPIKE-009
---

# Credential and State Management in Isolated Environments

## Summary

**Go** (No-Go condition did not trigger). swain-keys file-based per-project signing keys eliminate the need for SSH agent socket forwarding; `ANTHROPIC_API_KEY` and `GH_TOKEN` (via `gh auth token`) are plain env vars; all remaining credentials are file bind-mounts. Use the filesystem binding map from §2 as the canonical reference for EPIC-005 container implementation.

## Question

How should credentials, git configuration, and agent state be forwarded into ephemeral isolated environments while keeping storage filesystem-bound?

Sub-questions:
1. What is the minimal set of credentials Claude Code needs? (API key, git identity, gh auth token)
2. What filesystem binding strategy keeps agent state persistent? Map of host paths to environment paths for: project dir, `.claude/`, `.agents/`, `.tickets/`, global Claude config (`~/.claude/`).
3. How should the Anthropic API key be passed — environment variable, mounted secrets file, or runtime-specific secrets mechanism?
4. Can `gh auth` credentials be forwarded via binding `~/.config/gh/`? Any permission or path issues?
5. How do git signing keys (SSH-based, per swain-keys) work inside the environment? Does the agent need access to `~/.ssh/` or can signing be host-delegated?
6. What exclusions prevent leaking sensitive host files into the environment?

## Go / No-Go Criteria

- **Go**: A documented binding and env-var configuration that lets Claude Code inside the isolated environment: (a) authenticate to the Anthropic API, (b) make signed git commits, (c) push to GitHub via gh, and (d) persist .tickets/ and .claude/ state across restarts — all without baking secrets into the image.
- **No-Go**: Credential forwarding requires host-specific daemons (e.g., 1Password SSH agent socket) that can't be reliably forwarded across isolation boundaries.

## Pivot Recommendation

If credential forwarding proves too fragile:
1. Use a `.env` file (gitignored) read at environment start, accepting the tradeoff of secrets on disk
2. Use a compose/orchestration layer with structured secrets management
3. Fall back to running Claude Code on host but with restricted PATH/env to simulate isolation

## Findings

### 1. Minimal Credential Set

| Credential | Mechanism | Required for |
|---|---|---|
| `ANTHROPIC_API_KEY` | Env var | All Claude Code API calls |
| `GH_TOKEN` | Env var (preferred) | `gh` CLI — push, PR, key registration |
| `~/.gitconfig` + `~/.config/git/local.gitconfig` | File mount (ro) | Git identity, signing config |
| `~/.ssh/<project>_signing` + `.pub` | File mount (ro) | SSH commit signing (swain-keys per-project key) |
| `~/.ssh/allowed_signers_<project>` | File mount (ro) | Commit signature verification |
| `~/.ssh/config.d/<project>.conf` | File mount (ro) | SSH host alias for `github.com-<project>` |
| `~/.ssh/known_hosts` | File mount (ro) | Prevent TOFU prompts on GitHub |

**Critical gitconfig override** (already handled by swain-keys, lives in `.git/config`):
```
[gpg "ssh"]
  program = ssh-keygen   # overrides host's op-ssh-sign path — unreachable in containers
```
This is set locally per-project by `swain-keys.sh:step_configure_git_signing()` and is carried in automatically via the project bind mount.

**What is NOT needed** (reducing these reduces attack surface):
- `~/Library/` — contains 1Password data, Keychain, browser credentials
- `~/.ssh/id_ed25519` or other personal identity keys
- The 1Password agent socket (`~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock`) — not forwardable into Docker on macOS, and not needed since swain-keys uses file-based signing

### 2. Filesystem Binding Map

#### State directories covered by the project root bind mount

`.claude/`, `.agents/`, `.tickets/` are subdirectories of the project root — they are automatically covered and do not need separate mounts.

#### Tier 2 (Docker) — `docker run` volume flags

| Host Path | Container Path | Mode | Purpose |
|---|---|---|---|
| `$(pwd)` | `/workspace` | `rw` | Project files + `.git/`, `.tickets/`, `.agents/`, `.claude/` |
| `~/.claude/` | `/root/.claude/` | `rw` | Global Claude config, memory, skills, session history |
| `~/.gitconfig` | `/root/.gitconfig` | `ro` | Git identity; excludes `gpg.ssh.program` override if needed |
| `~/.config/git/local.gitconfig` | `/root/.config/git/local.gitconfig` | `ro` | Machine-specific identity |
| `~/.config/gh/` | `/root/.config/gh/` | `ro` | `gh` host config (token via `GH_TOKEN` env var instead) |
| `~/.ssh/<project>_signing` | `/root/.ssh/<project>_signing` | `ro` | Per-project signing private key |
| `~/.ssh/<project>_signing.pub` | `/root/.ssh/<project>_signing.pub` | `ro` | Per-project signing public key |
| `~/.ssh/allowed_signers_<project>` | `/root/.ssh/allowed_signers_<project>` | `ro` | Allowed signers for verification |
| `~/.ssh/config.d/<project>.conf` | `/root/.ssh/config.d/<project>.conf` | `ro` | SSH host alias |
| `~/.ssh/known_hosts` | `/root/.ssh/known_hosts` | `ro` | Prevent TOFU prompts |

**Example `docker run` invocation:**
```bash
docker run --rm -it \
  -e ANTHROPIC_API_KEY \
  -e GH_TOKEN \
  -v "$(pwd):/workspace" \
  -v "$HOME/.claude:/root/.claude:rw" \
  -v "$HOME/.gitconfig:/root/.gitconfig:ro" \
  -v "$HOME/.config/git/local.gitconfig:/root/.config/git/local.gitconfig:ro" \
  -v "$HOME/.config/gh:/root/.config/gh:ro" \
  -v "$HOME/.ssh/${PROJECT}_signing:/root/.ssh/${PROJECT}_signing:ro" \
  -v "$HOME/.ssh/${PROJECT}_signing.pub:/root/.ssh/${PROJECT}_signing.pub:ro" \
  -v "$HOME/.ssh/allowed_signers_${PROJECT}:/root/.ssh/allowed_signers_${PROJECT}:ro" \
  -v "$HOME/.ssh/config.d/${PROJECT}.conf:/root/.ssh/config.d/${PROJECT}.conf:ro" \
  -v "$HOME/.ssh/known_hosts:/root/.ssh/known_hosts:ro" \
  -w /workspace \
  <image> claude
```

### 3. API Key Strategy

**Environment variable. Never mounted file. Never baked into image.**

- Pass with `-e ANTHROPIC_API_KEY` (no value — inherits from host shell, never appears in `docker run` history)
- For Tier 1 (sandbox-exec/bwrap): env vars inherit from parent process automatically — no special handling needed
- `ANTHROPIC_BASE_URL` is optional if routing through a network proxy for filtering
- Pre-commit hooks (SPEC-023/SPEC-024) already guard against `.env` files with secrets leaking into the repo

### 4. gh Auth Forwarding

**Yes, with a caveat: use `GH_TOKEN` env var, not file-based forwarding.**

`~/.config/gh/hosts.yml` contains metadata (user, protocol) but the actual token may be in the macOS Keychain rather than the file — depends on how `gh auth login` was run. If the token is in Keychain only, binding `~/.config/gh/` gives `gh` the config but not the token; `gh` commands will fail with auth errors.

**Recommended approach:** retrieve the token once with `gh auth token` on the host, then pass as `GH_TOKEN` env var. `gh` reads `GH_TOKEN` and bypasses all file-based auth.

```bash
export GH_TOKEN=$(gh auth token)
docker run ... -e GH_TOKEN ...
```

Binding `~/.config/gh/` is still useful as a fallback for configs (default protocol, user) but `GH_TOKEN` is the reliable path for token auth.

**Permissions:** No issues if the container runs as root. For non-root users, ensure dir is 700 and files are 600. `gh` also reads `$GH_CONFIG_DIR` if set.

### 5. Git Signing in Containers

**SSH_AUTH_SOCK forwarding into Docker on macOS is unreliable. Use file-based keys.**

The macOS SSH agent socket (`SSH_AUTH_SOCK`) is at a dynamic path under `/private/tmp/com.apple.launchd.*`. Docker Desktop on macOS runs containers inside a Linux VM — Unix domain sockets on the macOS host are not visible to the VM. Docker Desktop provides a proxy at `/run/host-services/ssh-auth.sock` but:
- Only works with Docker Desktop (not OrbStack, Colima, or Linux native)
- Unreliable for 1Password's agent socket, which is a macOS Keychain-backed daemon

**This is not a blocker.** swain-keys already provides the escape hatch:
- Per-project file-based keys at `~/.ssh/<project>_signing`
- `step_configure_git_signing()` writes `git config --local gpg.ssh.program ssh-keygen` to override `op-ssh-sign`
- The container mounts the key file and uses standard `ssh-keygen` for signing — no daemon, no socket

Additionally: this repo uses HTTPS push (not SSH push). Pushes go through `GH_TOKEN`, not the SSH agent. The signing key is only needed for `git commit -S`, which is file-based.

**Do NOT attempt `SSH_AUTH_SOCK` forwarding for Docker on macOS.** Use file-based keys.

### 6. Tier 1 Sandbox Path Allowlist

#### macOS sandbox-exec (Seatbelt)

Invoked as:
```bash
sandbox-exec -f profile.sb -D HOME="$HOME" -D PROJECT="<project-name>" -- claude
```

Relevant credential-related rules (deny-first profile):
```scheme
; Global Claude config (rw)
(allow file-read* file-write*
  (subpath (string-append (param "HOME") "/.claude")))

; Git credentials (ro)
(allow file-read*
  (literal (string-append (param "HOME") "/.gitconfig"))
  (subpath (string-append (param "HOME") "/.config/git")))

; gh CLI credentials (ro)
(allow file-read*
  (subpath (string-append (param "HOME") "/.config/gh")))

; SSH signing keys (ro) — per-project files only, not entire ~/.ssh/
(allow file-read*
  (literal (string-append (param "HOME") "/.ssh/" (param "PROJECT") "_signing"))
  (literal (string-append (param "HOME") "/.ssh/" (param "PROJECT") "_signing.pub"))
  (literal (string-append (param "HOME") "/.ssh/allowed_signers_" (param "PROJECT")))
  (literal (string-append (param "HOME") "/.ssh/config.d/" (param "PROJECT") ".conf"))
  (literal (string-append (param "HOME") "/.ssh/known_hosts")))
```

The 1Password agent socket is not needed and should not be allowed.

#### Linux bubblewrap

```bash
bwrap \
  --bind "$HOME/.claude" "$HOME/.claude" \
  --ro-bind "$HOME/.gitconfig" "$HOME/.gitconfig" \
  --ro-bind "$HOME/.config/git" "$HOME/.config/git" \
  --ro-bind "$HOME/.config/gh" "$HOME/.config/gh" \
  --ro-bind "$HOME/.ssh/${PROJECT}_signing" "$HOME/.ssh/${PROJECT}_signing" \
  --ro-bind "$HOME/.ssh/${PROJECT}_signing.pub" "$HOME/.ssh/${PROJECT}_signing.pub" \
  --ro-bind "$HOME/.ssh/allowed_signers_${PROJECT}" "$HOME/.ssh/allowed_signers_${PROJECT}" \
  --ro-bind "$HOME/.ssh/config.d/${PROJECT}.conf" "$HOME/.ssh/config.d/${PROJECT}.conf" \
  --ro-bind "$HOME/.ssh/known_hosts" "$HOME/.ssh/known_hosts" \
  --setenv ANTHROPIC_API_KEY "$ANTHROPIC_API_KEY" \
  --setenv GH_TOKEN "$GH_TOKEN" \
  # ... other system paths ...
  -- claude
```

### 7. What Never to Bind-Mount

| Path | Reason |
|---|---|
| `~/Library/` | 1Password data, Keychain, browser credentials |
| `~/.ssh/id_ed25519` / `id_rsa` / `id_ecdsa` | Personal identity keys — per-project keys only |
| `~/.ssh/` (entire dir) | Too broad — mount only the specific per-project files |
| `~/.aws/` | AWS credentials — not needed for Claude Code |
| `~/.netrc` | May contain HTTP auth credentials |
| `~/.zshrc` / `~/.bashrc` / `~/.profile` | Shell init may leak env vars, PATH manipulation |
| `~/.gnupg/` | GPG keys — not needed if using SSH signing |
| `~/.kube/` | Kubernetes credentials |
| `~/.claude/history.jsonl` | Conversation transcripts — sensitive; acceptable for operator-trusted agents but should be flagged as a sensitivity boundary |
| Full `~/.config/gh/config.yml` if it contains the token | Use `GH_TOKEN` env var instead |

### 8. Verdict

**Go — the No-Go condition does not trigger.**

The No-Go condition was: "Credential forwarding requires host-specific daemons (e.g., 1Password SSH agent socket) that can't be reliably forwarded across isolation boundaries."

This condition does not apply because:

1. **swain-keys already provides the file-based key escape hatch.** Per-project keys at `~/.ssh/<project>_signing` exist precisely for this scenario. `step_configure_git_signing()` already overrides `op-ssh-sign` with `ssh-keygen` locally.

2. **This repo uses HTTPS push.** SSH push is not used; `GH_TOKEN` handles all GitHub auth.

3. **`GH_TOKEN` env var bypasses macOS Keychain entirely.** One-time retrieval with `gh auth token`.

4. **`ANTHROPIC_API_KEY` is a plain env var.** No daemon, no socket.

5. **All remaining credentials are files.** File bind-mounts work reliably in both Tier 1 and Tier 2.

The complete forwarding path:
- Anthropic API: `-e ANTHROPIC_API_KEY`
- GitHub push: `-e GH_TOKEN`
- Git signing: `~/.ssh/<project>_signing` bind-mount + `ssh-keygen` (from `.git/config`)
- Git identity: `~/.gitconfig` + `~/.config/git/local.gitconfig` bind-mounts
- Agent state: project root bind-mount (covers `.claude/`, `.agents/`, `.tickets/`)
- Global Claude config + memory: `~/.claude/` bind-mount

### 9. Sources

- `docs/research/Complete/(SPIKE-009)-Isolation-Mechanism-Selection/` — Tier 1/2/3 architecture, sandbox-exec profile syntax, bubblewrap invocation
- `skills/swain-keys/scripts/swain-keys.sh` — per-project key paths, `op-ssh-sign` override logic
- `~/.gitconfig`, `~/.config/git/macos.gitconfig`, `~/.config/git/local.gitconfig` — actual signing config, op-ssh-sign path
- `~/.ssh/config.d/` — 1Password agent socket path, per-project SSH config structure
- `~/.claude/settings.json` — Claude Code config structure, env var patterns
- `~/.config/gh/hosts.yml` — `gh` config file structure, token location

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-12 | — | Initial creation |
| Active | 2026-03-14 | 257ea9c | Transition to Active |
| Complete | 2026-03-14 | e510403 | All findings documented; Verdict: Go |
