# opencode-notify Snapshot

**Repository**: https://github.com/kdcokenny/opencode-notify
**License**: MIT (Copyright 2025 kdcokenny)
**Author**: kdcokenny
**Part of**: KDCO/OCX ecosystem (https://github.com/kdcokenny/ocx)

## Project Structure

```
opencode-notify/
  registry.json           # OCX registry metadata
  README.md
  LICENSE
  src/
    notify.ts              # Main plugin (~994 lines)
    notify/
      backend.ts           # Notification backend abstraction (cmux → node-notifier fallback)
      cmux.ts              # cmux CLI integration for notifications + status
    kdco-primitives/       # Shared utilities (duplicated in plugin/ subdir)
      types.ts             # OpencodeClient type
      with-timeout.ts      # Promise timeout helper
      terminal-detect.ts   # Terminal detection
      get-project-id.ts
      mutex.ts
      shell.ts
      log-warn.ts
      temp.ts
      index.ts
    plugin/
      kdco-primitives/     # Same primitives, for plugin distribution
```

## How Notifications Work

1. **Plugin registers event handlers** via `NotifyPlugin` export (OpenCode `Plugin` interface)
2. **Events listened for**: `session.idle`, `session.error`, `permission.updated`, `permission.asked`, `question.asked`, `tool.execute.before` (for question tool)
3. **Smart suppression**:
   - Only parent sessions notify by default (`notifyChildSessions: false`)
   - Terminal focus detection on macOS suppresses notifications when terminal is active
   - Quiet hours support (configurable time window)
   - Deduplication windows to prevent notification spam (1.5s for questions/permissions/ready)
4. **Two notification backends**:
   - **cmux** (preferred): `cmux notify` + `cmux set-status`/`cmux clear-status` for animated busy states, when `CMUX_WORKSPACE_ID` is set
   - **node-notifier** (fallback): Native OS notifications via terminal-notifier (macOS), SnoreToast (Windows), notify-send (Linux)
5. **OSC title integration**: Sets terminal title with busy spinner animation when supported
6. **Configuration**: `~/.config/opencode/kdco-notify.json` with sounds, quiet hours, terminal override
7. **Installation**: Via OCX (`ocx add kdco/notify`) or manual copy to `.opencode/plugins/`

## Key Files

| File | Purpose |
|------|---------|
| `src/notify.ts` | Main plugin — event handlers, dedup, terminal detection, notification sending |
| `src/notify/backend.ts` | Backend abstraction: try cmux first, fall back to node-notifier |
| `src/notify/cmux.ts` | cmux CLI integration — `cmux notify`, `cmux set-status`, `cmux clear-status` |
| `src/kdco-primitives/types.ts` | OpencodeClient type definition |
| `registry.json` | OCX registry package metadata |