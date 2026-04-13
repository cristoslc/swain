---
source-id: "matterbridge-chat-bridge"
title: "Matterbridge — Single-Binary Chat Bridge Across 30+ Platforms"
type: web
url: "https://github.com/42wim/matterbridge"
fetched: 2026-04-07T06:00:00Z
---

# Matterbridge — Single-Binary Chat Bridge Across 30+ Platforms

## What It Is

Matterbridge is a Go application that bridges messages between chat platforms. It does not provide its own chat interface. It relays messages from one platform to another, preserving author attribution and (when possible) threading.

## Supported Platforms

Matterbridge bridges between: Discord, Slack, IRC, Matrix, Mattermost, Microsoft Teams, Telegram, WhatsApp, Rocket.Chat, Zulip, XMPP, Keybase, Twitch, Mumble, SSH-chat, VK, Nextcloud, Gitter, and more. Third-party plugins add support for Minecraft, Delta Chat, and others via a REST API.

## Deployment

- **Single binary.** Download a pre-compiled Go binary or build from source. Docker images also available.
- **Configuration.** A single TOML file defines which platforms to bridge and how.
- **No database.** Stateless message relay. No persistent storage needed beyond the config file.
- **Resource usage.** Runtime memory is modest (not formally documented). Build requires ~3 GB RAM with all bridges; runtime is far less.

## Thread Handling

Matterbridge "preserves threading when possible." This means:

- If both source and destination platforms support threads, the thread context is maintained.
- If one side lacks threads, the thread context is flattened into the flat message stream.
- Thread handling is best-effort, not guaranteed.

## API

Matterbridge exposes a basic REST API for third-party integrations. External systems can post messages into the bridge and receive messages from it. The API is documented in the project wiki.

## Relevance to Swain

Matterbridge is not a chat server. It is a bridge. It becomes relevant in two scenarios:

### Scenario 1: Multi-platform access

If the operator wants to use Telegram on their phone but the bot posts to a self-hosted platform (e.g., Matrix via conduwuit), matterbridge can bridge between them. The operator reads and replies on Telegram; the bot operates on Matrix. This gives the operator mobile convenience without changing the bot's target platform.

### Scenario 2: Gradual migration

If swain starts with a hosted platform (Telegram) and later migrates to self-hosted (Zulip, Matrix), matterbridge can bridge the two during the transition. Both old and new surfaces see the same messages.

### Limitations

- **Not a standalone solution.** You still need at least one actual chat platform.
- **Thread fidelity is lossy.** Bridging between platforms with different threading models (Zulip topics vs. Telegram forum topics vs. IRC flat) degrades the threading UX.
- **Maintenance.** The upstream project has low activity. A community fork (matterbridge-org) is more actively maintained. Fork governance is a risk factor.
- **Complexity.** Adding a bridge layer adds one more thing to configure and maintain. For a solo operator seeking simplicity, it may add more burden than it saves.

## Verdict

Matterbridge is a useful tool in the swain ecosystem, but it is not a chat platform choice — it is a glue layer. It is most valuable if swain supports multiple chat backends and needs to bridge between them, or if the operator wants to decouple their mobile client from the bot's backend.
