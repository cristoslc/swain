---
title: "Claude Config Dir Mount Strategy In Docker Sandboxes"
artifact: SPIKE-027
track: container
status: Complete
author: cristos
created: 2026-03-17
last-updated: 2026-03-17
question: "Can ~/.claude/ be selectively mounted into a Docker Sandbox so that the existing login session (Max subscription OAuth token) and global skills are available, without exposing per-project memories or allowing the sandbox to write back to the host config dir?"
gate: Pre-implementation
risks-addressed:
  - Re-login friction for Max subscription users in every new sandbox
  - Global swain skills unavailable inside sandbox
  - Per-project memories from unrelated projects leaking into sandboxed agent context
  - Claude Code runtime errors from read-only ~/.claude/ mount
evidence-pool: ""
linked-artifacts:
  - SPEC-067
---

# Claude Config Dir Mount Strategy In Docker Sandboxes

## Summary

**Conditional Go — simpler than expected: don't mount `~/.claude/` at all.**

The Docker Sandbox already creates `/home/agent/.claude/` with proxy-managed auth during VM init, the sandbox home (`/home/agent`) doesn't match the host path (`/Users/cristos/.claude`) so a naïve mount lands at the wrong location anyway, and `~/.claude/projects/` exposes 60+ cross-project memory dirs that would actively contaminate the sandboxed agent's context. Credentials flow through the sandbox proxy automatically for `ANTHROPIC_API_KEY`; Max subscription users use `CLAUDE_CODE_OAUTH_TOKEN` env var (confirmed in binary) to bypass keychain. Global CLAUDE.md and skills belong in a custom sandbox template, not a live host mount. Update SPEC-067 accordingly: no `~/.claude/` mount, credential strategy documented per auth method.

## Question

Can `~/.claude/` be selectively mounted into a Docker Sandbox so that the existing login session (Max subscription OAuth token) and global skills are available, without exposing per-project memories or allowing the sandbox to write back to the host config dir?

## Investigation Threads

### Thread 1: Claude Code credential file location

What file(s) does `claude login` (OAuth flow) write to inside `~/.claude/`? Is it a single named file (e.g., `credentials.json`, `.credentials`, `auth.json`) or embedded in a broader settings file?

- Check `~/.claude/` on the host after a successful `claude login`
- Identify the exact path(s) Claude Code reads to authenticate API calls
- Determine whether the credential is a bearer token, refresh token, or session cookie

### Thread 2: Claude Code behavior with read-only `~/.claude/`

Does Claude Code fail hard or degrade gracefully when `~/.claude/` is read-only?

- Start Claude Code with `~/.claude/` mounted read-only (or chmod 555 the dir temporarily)
- Observe: does it launch? Does it error immediately or only when writing state?
- Identify which write operations it attempts: project memory, settings, bookmarks, telemetry

### Thread 3: `CLAUDE_HOME` or equivalent env var

Does Claude Code support redirecting its config/state directory via an environment variable (e.g., `CLAUDE_HOME`, `CLAUDE_CONFIG_DIR`, `XDG_CONFIG_HOME`)?

- Check Claude Code CLI help and any documented env vars
- Test: set a candidate env var to a writable path inside the sandbox; verify Claude Code writes state there instead of `~/.claude/`
- If no official env var exists, check whether `HOME` override alone is sufficient

### Thread 4: Docker Sandboxes mount granularity

Does `docker sandbox run` support mounting individual files (not just directories) read-only? Does the `:ro` flag prevent writes inside the sandbox VM, or only prevent sync-back to the host?

- Test `docker sandbox run claude "$PWD" ~/.claude/some-file:ro` — does it accept file-level paths?
- Test `docker sandbox run claude "$PWD" ~/.claude:ro` — do writes inside the VM error (EROFS) or succeed silently without syncing back?
- Check Docker Sandboxes docs/changelog for file-level mount support

### Thread 5: Selective subdirectory mounts

If full `~/.claude/` read-only is problematic, can individual subdirs be mounted independently?

- Test: `docker sandbox run claude "$PWD" ~/.claude/skills:ro` — does it mount only that subdir?
- Test combination: skills + CLAUDE.md read-only, no projects/ mount, fresh writable home for runtime state
- Determine whether multiple `~/.claude/` subpath mounts result in a coherent directory structure inside the sandbox

## Go / No-Go Criteria

**Go** (proceed with selective mount in SPEC-067) if ALL of:
- The OAuth credential file is identifiable and mountable in isolation OR `CLAUDE_HOME`-style redirection works
- Claude Code launches successfully with read-only credential access (Thread 2 passes)
- The sandbox cannot write back to the host `~/.claude/` when `:ro` is used

**Conditional Go** if:
- `CLAUDE_HOME` redirection works: mount `~/.claude/` read-only as a source, set `CLAUDE_HOME` to a fresh writable dir inside the sandbox, and copy only the credential file at sandbox startup

**No-Go** (accept re-login cost, document as known limitation in SPEC-067) if:
- Claude Code errors on launch with read-only `~/.claude/` AND no env var redirection exists
- Docker Sandboxes `:ro` flag syncs writes back anyway (no isolation guarantee)

## Pivot Recommendation

If No-Go: accept re-login per sandbox as the documented UX. Add a note to the `swain-box` output on first run: "No existing session found — run `claude login` to authenticate with your Max subscription. This session will persist for this sandbox." Update SPEC-067 AC-8 to reflect this explicitly rather than treating it as a fallback.

## Findings

### Thread 1: Credential file location

On macOS, `claude login` writes OAuth tokens to the **macOS Keychain** (service: `Claude Code-credentials`, account: OS username). The file `~/.claude/.credentials.json` is the Linux/fallback path and does not exist on macOS when Keychain is available.

`~/.claude.json` (at `$HOME`, not inside `~/.claude/`) holds account identity metadata only (`oauthAccount` keys: uuid, email, org, billingType — no tokens).

**Keychain token structure** (keys only):
```
claudeAiOauth: { accessToken, refreshToken, expiresAt, scopes, subscriptionType, rateLimitTier }
```

Mounting the macOS Keychain into a Linux Docker container is not viable (macOS-only, Secure Enclave encrypted). The `CLAUDE_CODE_OAUTH_TOKEN` env var bypasses Keychain entirely.

### Thread 2: Read-only `~/.claude/` behavior

`CLAUDE_CONFIG_DIR` env var confirmed — redirects **all** Claude Code writes (including `.claude.json`) to the specified directory. This is the clean solution for state isolation.

With `~/.claude/` read-only but `CLAUDE_CONFIG_DIR` pointing to a writable dir: Claude Code launches normally. Session state (history, conversation logs, file-edit history, telemetry) silently does not persist — no crash, no user-facing error.

Fully read-only HOME causes an **indefinite silent hang** — Claude Code cannot write its initial `.claude.json` and blocks without surfacing an error.

**Write operations during a session:**
- `.claude.json` — main settings/state (written to `CLAUDE_CONFIG_DIR` or `$HOME`)
- `plugins/blocklist.json`, `policy-limits.json` — fetched from remote on startup
- `projects/<cwd-slug>/<uuid>.jsonl` — conversation log (written immediately)
- `sessions/<pid>.json`, `history.jsonl`, `shell-snapshots/`, `paste-cache/`, `file-history/` — session state

### Thread 3: `CLAUDE_CONFIG_DIR` env var

Confirmed in source:
```js
process.env.CLAUDE_CONFIG_DIR ?? path.join(homedir(), ".claude")
```

**Keychain hash suffix:** When `CLAUDE_CONFIG_DIR` is set, the Keychain service name gets a hash suffix (e.g., `Claude Code-credentials-3dcf291c`). The existing Keychain entry (service: `Claude Code-credentials`) is **not found** when the var is set — OAuth via Keychain breaks.

**`CLAUDE_CODE_OAUTH_TOKEN`** and **`CLAUDE_CODE_OAUTH_REFRESH_TOKEN`** are confirmed env vars in the binary. These bypass Keychain entirely and work regardless of `CLAUDE_CONFIG_DIR`.

HOME override alone does not redirect config (Claude Code resolves the config dir explicitly, not via `$HOME/.claude`).

### Thread 4: Docker Sandboxes `:ro` semantics

- Docker Desktop **4.65.0** installed; `docker sandbox` **v0.12.0** available — meets the 4.58+ requirement.
- `:ro` enforces a **hard VM-level read-only filesystem** (EROFS). Every write inside the VM against a `:ro` path fails at the kernel level — this is not a soft "no sync-back" flag.
- **File-level mounts not supported.** Only directory-level paths accepted. Passing a file path produces `workspace path exists but is not a directory`.
- The primary workspace correctly writes through and syncs back to the host.

### Thread 5: Sandbox home dir + env var injection + `~/.claude/` contents

**Sandbox home dir is `/home/agent`** (not `/Users/cristos`). The Docker Sandbox VM runs an `agent` user. Host workspace paths are preserved at the same absolute path, but the user home is different.

Consequence: mounting `~/.claude/` (host path `/Users/cristos/.claude`) into the sandbox places it at `/Users/cristos/.claude` inside the VM — not at `$HOME/.claude` (`/home/agent/.claude`). Claude Code running inside the VM looks for `$CLAUDE_CONFIG_DIR` or `$HOME/.claude` — the mounted host path is **invisible to it by default**.

The sandbox init script already creates `/home/agent/.claude/settings.json` and `/home/agent/.claude.json` with proxy-managed auth configuration. Mounting the host `~/.claude/` would not override this; it would just be an orphaned directory at a different path.

**No `-e`/`--env` CLI flag** on `docker sandbox run`. Env vars are injected via the Docker Sandboxes proxy mechanism (reads from the host shell environment, picked up by the daemon). `ANTHROPIC_API_KEY` flows through the proxy automatically. `CLAUDE_CODE_OAUTH_TOKEN` must be exported in `~/.zshrc` before Docker Desktop starts.

**`~/.claude/projects/` exposure risk:** Contains **61 subdirectories** — one per project with Claude conversation history. Each contains `MEMORY.md` files with auto-captured notes from unrelated projects (finance tools, IAC repos, design projects, etc.). Mounting `~/.claude/` wholesale would expose all of this to the sandboxed agent.

**`~/.claude/` useful content:**
- `CLAUDE.md` (symlink to dotfiles repo) — global instructions
- `settings.json` (symlink to dotfiles repo) — global settings
- `skills/` — 2 entries (symlinks)

**`~/.claude/` sensitive content:**
- `projects/` — 61 cross-project memory dirs
- `history.jsonl` (1.1 MB) — full conversation history across all projects
- `session-env/`, `sessions/`, `paste-cache/`, `file-history/` — session state from other projects

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-17 | — | Initial creation; gates SPEC-067 Ready transition |
| Complete | 2026-03-17 | — | All 5 threads resolved; verdict: Conditional Go — no ~/.claude/ mount; credential strategy via env vars |
