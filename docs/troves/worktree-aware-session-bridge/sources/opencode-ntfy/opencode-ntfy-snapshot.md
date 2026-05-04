# opencode-ntfy.sh Snapshot

**Repository**: https://github.com/lannuttia/opencode-ntfy.sh
**License**: MIT (Copyright 2026 Anthony Lannutti)
**Author**: lannuttia

## Project Structure

```
opencode-ntfy.sh/
  src/
    index.ts               # Plugin entry point — wires SDK to ntfy backend
    backend.ts             # NotificationBackend implementation (HTTP POST to ntfy.sh)
    config.ts              # Config parsing: topic, server, token, priority, icon, templates
  tests/
    backend.test.ts        # Backend tests (MSW HTTP mocking)
    config.test.ts         # Config validation tests
    typecheck.test.ts      # Compile-time type conformance
    msw-helpers.ts         # MSW test helpers
  assets/
    opencode-icon-dark.png # Dark mode icon
    opencode-icon-light.png# Light mode icon
  notification-ntfy.schema.json  # JSON Schema for config validation
  PROMPT.md                # Development prompt/spec document
  PLAN.md                  # Implementation task tracker
  ralph.sh                 # Loop script
  eslint.config.js
  vitest.config.ts
  bunfig.toml
  package.json
```

## How Notifications Work

1. **Built on `opencode-notification-sdk`** — the SDK handles event routing, subagent suppression, and config loading. This plugin is a **notification backend** implementing `NotificationBackend.send()`.
2. **Config**: `~/.config/opencode/notification-ntfy.json` — includes SDK-level toggles (`enabled`, `events`) and ntfy-specific `backend` config (topic, server, token, priority, icon, fetchTimeout, title/message templates).
3. **Event types**: `session.idle`, `session.error`, `permission.asked` — classified by the SDK, then passed to the backend's `send()` method.
4. **Notification delivery**: HTTP POST to `https://ntfy.sh/<topic>` with headers: `Title`, `Priority`, `Tags` (emoji shortcodes), `X-Icon`, optional `Authorization: Bearer <token>`.
5. **Content templates**: Configurable per-event via `backend.title` and `backend.message` — supports `value` (template strings with `{var_name}` substitution) and `command` (render template then execute as shell command). Variables: `{event}`, `{time}`, `{project}`, `{session_id}`, `{error}`, `{permission_type}`, `{permission_patterns}`.
6. **Variable substitution**: SDK expands `{env:VAR_NAME}` and `{file:path}` in config strings before validation.
7. **Icon resolution**: Defaults to GitHub raw URLs for dark/light OpenCode icons; configurable `icon.mode` and custom `icon.variant.light`/`icon.variant.dark` URLs.
8. **Testing**: Uses MSW (Mock Service Worker) for HTTP interception — no implementation-coupled mocks.

## Key Files

| File | Purpose |
|------|---------|
| `src/index.ts` | Plugin entry — creates NotificationBackend, wires SDK |
| `src/backend.ts` | `NotificationBackend.send()` — formats title/message/tags, HTTP POST to ntfy.sh |
| `src/config.ts` | Config parsing: topic (required), server, token, priority, icon, fetchTimeout, templates |
| `notification-ntfy.schema.json` | JSON Schema (draft 2020-12) for config validation |
| `PROMPT.md` | Full development spec and instructions |