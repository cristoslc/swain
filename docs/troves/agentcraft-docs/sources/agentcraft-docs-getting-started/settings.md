---
title: Settings
url: https://www.getagentcraft.com/docs/getting-started/settings
fetched: 2026-05-04
type: documentation
---

# Settings

Configure AgentCraft preferences, models, and display options.

## Accessing Settings

Click the Settings icon in the UI or access via the in-game menu.

## Game Tab

| Setting | Description |
| --- | --- |
| Agent Teams | Toggle team display for Claude Code team configurations |
| Default Agent Model | Model for spawned heroes (see below) |
| Usage Analytics | Toggle anonymous analytics |
| Team Banners | Customize team colors and banner icons |

## Default Agent Model

Controls the --model flag when spawning heroes:

| Option | Behavior |
| --- | --- |
| Default | No --model flag (recommended for Bedrock/Vertex) |
| Opus | --model opus |
| Sonnet | --model sonnet |
| Haiku | --model haiku |
| Custom... | Any model string (e.g., ollama:llama3) |

You can also override the model per hero using the model dropdown at the top of the side panel.

## About Tab

Shows version info, detected CLI versions, provider info, and links to:

- Privacy policy
- Website, Twitter, Discord
- Hall of Glory (Achievements) button — opens the achievement gallery

## Configuration Files

All AgentCraft config lives in ~/.agentcraft/:

| File | Purpose |
| --- | --- |
| config.json | Port, autoOpenBrowser, API keys |
| auth.json | Auth tokens (0o600 permissions) |
| server.pid | PID of daemon-mode server |
| mission-history.json | Persisted completed missions |

## Restore Settings

If something goes wrong, restore your original Claude settings:

```
npx @idosal/agentcraft restore
```

This restores ~/.claude/settings.json from the pre-install backup.