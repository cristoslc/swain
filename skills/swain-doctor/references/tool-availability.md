# Tool Availability

Check for required and optional external tools. Report results as a table. **Never install tools automatically** — only inform the user what's missing and how to install it.

## Required tools

These tools are needed by multiple skills. If missing, warn the user.

| Tool | Check | Used by | Install hint (macOS) |
|------|-------|---------|---------------------|
| `git` | `command -v git` | All skills | Xcode Command Line Tools |
| `jq` | `command -v jq` | swain-session, swain-session, swain-do | `brew install jq` |

## Optional tools

These tools enable specific features. If missing, note which features are degraded.

| Tool | Check | Used by | Degradation | Install hint (macOS) |
|------|-------|---------|-------------|---------------------|
| `tk` | `[ -x "$SKILLS_ROOT/swain-do/bin/tk" ]` | swain-do, swain-session (tasks) | Task tracking unavailable; status skips task section | Vendored at `swain-do/bin/tk` -- reinstall swain if missing |
| `uv` | `command -v uv` | swain-do (plan ingestion) | Plan ingestion unavailable | `brew install uv` |
| `gh` | `command -v gh` | swain-session (GitHub issues), swain-release | Status skips issues section; release can't create GitHub releases | `brew install gh` |
| `tmux` | `which tmux` | swain-session | Session tab-naming unavailable outside tmux | `brew install tmux` |
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
  tmux ............. WARN — tmux not found — session tab-naming unavailable. [offer to install]
  fswatch .......... MISSING — live specwatch unavailable. Install: brew install fswatch
```

Only flag items that need attention. If all required tools are present, the check is silent except for missing optional tools that meaningfully degrade the experience.

## Install offers

For tools marked `[offer to install]`, after reporting the warning, ask the user:

> `<tool>` is not installed. Install it now? I can run `<install-hint>` for you.

Run the command if the user accepts. For tools without `[offer to install]`, only report the hint — do not prompt.
