# Tool Availability

Check for required and optional external tools. Report results as a table. **Never install tools automatically** — only inform the user what's missing and how to install it.

## Required tools

These tools are needed by multiple skills. If missing, warn the user.

| Tool | Check | Used by | Install hint (macOS) |
|------|-------|---------|---------------------|
| `git` | `command -v git` | All skills | Xcode Command Line Tools |
| `jq` | `command -v jq` | swain-status, swain-stage, swain-session, swain-do | `brew install jq` |

## Optional tools

These tools enable specific features. If missing, note which features are degraded.

| Tool | Check | Used by | Degradation | Install hint (macOS) |
|------|-------|---------|-------------|---------------------|
| `tk` | `[ -x skills/swain-do/bin/tk ]` | swain-do, swain-status (tasks) | Task tracking unavailable; status skips task section | Vendored at `skills/swain-do/bin/tk` -- reinstall swain if missing |
| `uv` | `command -v uv` | swain-stage (MOTD TUI), swain-do (plan ingestion) | MOTD falls back to bash script; plan ingestion unavailable | `brew install uv` |
| `gh` | `command -v gh` | swain-status (GitHub issues), swain-release | Status skips issues section; release can't create GitHub releases | `brew install gh` |
| `tmux` | `which tmux` | swain-stage, swain-session | swain-stage and session features unavailable — offer to install | `brew install tmux` |
| `fswatch` | `command -v fswatch` | swain-design (specwatch live mode) | Live artifact watching unavailable; on-demand `specwatch.sh scan` still works | `brew install fswatch` |
| `ssh` | `command -v ssh` | swain-keys, git SSH alias remotes | Project-specific GitHub SSH aliases cannot be used from this runtime | `brew install openssh` |

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
  tmux ............. WARN — tmux not found — swain-stage and session features unavailable. [offer to install]
  fswatch .......... MISSING — live specwatch unavailable. Install: brew install fswatch
```

Only flag items that need attention. If all required tools are present, the check is silent except for missing optional tools that meaningfully degrade the experience.

## Install offers

For tools marked `[offer to install]`, after reporting the warning, ask the user:

> `<tool>` is not installed. Install it now? I can run `<install-hint>` for you.

Run the command if the user accepts. For tools without `[offer to install]`, only report the hint — do not prompt.
