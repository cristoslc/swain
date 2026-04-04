# Tool Availability

Check for required and optional external tools. Report results as a table. Classify each finding per ADR-020's three-tier remediation model:

- **Self-heal**: local, idempotent fixes — execute silently with advisory log line
- **Bundle-offer**: external installs (e.g., `brew install`) — collect into a fix plan presented at scan end, require operator consent before executing
- **Report-only**: judgment calls — show as warnings, no fix offered

## Required tools

These tools are needed by multiple skills. If missing, warn the user.

| Tool | Check | Used by | Install hint (macOS) |
|------|-------|---------|---------------------|
| `git` | `command -v git` | All skills | Xcode Command Line Tools |
| `jq` | `command -v jq` | swain-init, swain-teardown, swain-do | `brew install jq` |

## Optional tools

These tools enable specific features. If missing, note which features are degraded.

| Tool | Check | Used by | Degradation | Install hint (macOS) | Action |
|------|-------|---------|-------------|---------------------|--------|
| `tk` | `[ -x "$SKILLS_ROOT/swain-do/bin/tk" ]` | swain-do | Task tracking unavailable; status skips task section | Vendored at `swain-do/bin/tk` -- reinstall swain if missing | report-only |
| `uv` | `command -v uv` | swain-do (plan ingestion) | Plan ingestion unavailable | `brew install uv` | bundle-offer |
| `gh` | `command -v gh` | swain-roadmap (GitHub issues), swain-release, swain-teardown | Status skips issues section; release can't create GitHub releases | `brew install gh` | bundle-offer |
| `tmux` | `which tmux` | swain-init | Session tab-naming unavailable outside tmux | `brew install tmux` | bundle-offer |
| `fswatch` | `command -v fswatch` | swain-design (specwatch live mode) | Live artifact watching unavailable; on-demand `specwatch.sh scan` still works | `brew install fswatch` | bundle-offer |
| `ssh` | `command -v ssh` | swain-keys, git SSH alias remotes | Project-specific GitHub SSH aliases cannot be used from this runtime | `brew install openssh` | bundle-offer |
| `rtk` | `command -v rtk` | git-compact (context-window compression) | `git-compact` passes through to raw git — no compression savings | `brew install rtk` | bundle-offer |

## Reporting format

After checking all tools, output a summary:

```
Tool availability:
  git .............. ok
  jq ............... ok
  tk ............... ok (vendored)
  uv ............... ok
  gh ............... ok
  tmux ............. ok
  tmux ............. WARN — tmux not found — session tab-naming unavailable. [offer to install]
  fswatch .......... MISSING — live specwatch unavailable. Install: brew install fswatch
```

Only flag items that need attention. If all required tools are present, the check is silent except for missing optional tools that meaningfully degrade the experience.

## Remediation (ADR-020)

After all checks complete, collect findings by action tier:

1. **Self-heal** findings execute silently during the scan (advisory log line only)
2. **Bundle-offer** findings are collected into a fix plan presented once at the end:

```
Doctor found 2 fixable issues:

  1. tmux not installed — session tab-naming unavailable
     Fix: brew install tmux

  2. rtk not installed — git-compact passes through without compression
     Fix: brew install rtk

Run all fixes? [y/N]
```

3. **Report-only** findings are shown as warnings with no fix offered

On operator approval, execute each fix command sequentially and report per-item success/failure. On decline, log findings as advisories and continue.

With `--auto-fix`, self-heal fixes run but bundle-offer fixes are skipped (no operator to consent).
