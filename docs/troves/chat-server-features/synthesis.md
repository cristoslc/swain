# Synthesis: Self-Hostable Chat Servers for Bot-Driven Development

## Context

This trove looks at self-hostable chat servers for a bot-driven dev workflow run by one person. The use case: one room per project, one thread per session. A bot posts updates nonstop. The operator reads and steers from a phone. This feeds an ADR for chat protocol selection under VISION-006 (Untethered Operator).

## Key Findings

### Threading decides the winner.

The platforms fall into three tiers:

1. **Zulip** — every message must have a stream (channel) and a topic (thread). A bot that sends a message with `topic: "session-2026-04-06-001"` creates an organized thread with no extra work. Threading is built in, not bolted on. [zulip-self-hosting, zulip-bot-api]
2. **Matrix and Mattermost** — both support threads, but threads are opt-in. In Matrix, the bot must track root event IDs and set `m.thread` relations (MSC3440, spec v1.4). In Mattermost, the bot must track parent post IDs. More code for the same result. [matrix-threading-msc3440, mattermost-vs-rocketchat-comparison]
3. **Campfire** — no threads at all. Messages are flat in rooms. This rules it out for session-per-thread mapping. [campfire-37signals]

### Bot APIs range from rich to bare.

Zulip and Mattermost have the best bot APIs. Both offer full CRUD on channels and messages, official SDKs, and webhook support. Matrix has a strong client-server API, but it serves all clients, not just bots. Campfire only has webhooks. It cannot create rooms or read message history. [zulip-bot-api, mattermost-vs-rocketchat-comparison, campfire-37signals]

### Lighter servers need fewer resources.

For a single-operator setup:

- **Conduit/conduwuit** (Matrix): Lightest option. One binary, embedded database. Runs on a Raspberry Pi 4. [conduit-matrix-homeserver]
- **Campfire**: Light (2 GB RAM, 1 CPU) but missing key features. [campfire-37signals]
- **Zulip**: Needs 1 CPU and 2 GB RAM at minimum. Runs PostgreSQL, Redis, RabbitMQ, and Nginx behind the scenes. The installer sets it all up. [zulip-self-hosting]
- **Synapse** (Matrix): Uses 350 MB for one user. Grows fast with federation and large rooms. [matrix-synapse-self-hosting-2025]
- **Mattermost**: Needs 2-4 GB RAM. One binary plus PostgreSQL. [mattermost-vs-rocketchat-comparison]
- **Rocket.Chat**: Heaviest due to MongoDB and Meteor. Skip it for small setups. [mattermost-vs-rocketchat-comparison]

### Setup ranges from trivial to involved.

From easiest to hardest:

1. **Campfire**: One curl command installs it. [campfire-37signals]
2. **Conduit/conduwuit**: One binary or `docker run`. One TOML config file. [conduit-matrix-homeserver]
3. **Mattermost**: One binary plus PostgreSQL. Docker is the common path. [mattermost-vs-rocketchat-comparison]
4. **Zulip**: An install script sets up five services. Upgrades are scripted too. Docker is also an option. [zulip-self-hosting]
5. **Synapse**: Docker Compose with PostgreSQL, a reverse proxy, and DNS delegation. Much better in 2025 than before, but still the most moving parts. [matrix-synapse-self-hosting-2025]

### E2E encryption does not matter here.

Only Matrix has mature E2E encryption (Olm/Megolm). But E2E makes bot work harder. Bots must handle key swaps and device checks. Some bot tools fail at this. When you own the server, E2E adds cost with no benefit. [matrix-synapse-self-hosting-2025, mattermost-vs-rocketchat-comparison]

### Mobile apps vary in quality.

- **Matrix**: Element X is fast and polished. Many other clients exist too. [matrix-synapse-self-hosting-2025]
- **Zulip**: Native iOS and Android apps (React Native). Push alerts are free for up to 10 users on self-hosted. [zulip-self-hosting]
- **Mattermost**: Native mobile apps. Solid. [mattermost-vs-rocketchat-comparison]
- **Campfire**: PWA only. No native apps. [campfire-37signals]

## Points of Agreement

All sources agree on these points:

- Self-hosted chat is easier in 2026 than ever.
- Threading quality is the top factor when choosing a platform.
- Zulip has the best threading for organized, searchable talks.
- Matrix has the richest protocol but the most complexity.
- Campfire trades features for simplicity.

## Points of Disagreement

- **Matrix vs. Zulip for bots**: Matrix fans say the federated protocol and large client pool outweigh the threading gap. Zulip fans say first-class threading removes a whole class of bot problems.
- **Mattermost licensing**: Some see the open-core model as fine. Others call the 10,000-message search cap on the free tier a dealbreaker.
- **conduwuit stability**: Drama around the conduwuit fork (and the later Continuwuity fork) raises questions about long-term upkeep.

## Gaps

- **Zulip push on self-hosted**: Free tier caps push alerts at 10 users. Fine for one operator but good to note.
- **Matrix bot thread code**: No source shows a side-by-side code comparison of thread handling in Matrix vs. Zulip. The design gap is clear but the code effort is not measured.
- **Campfire bot API growth**: Campfire went open source recently. The bot API may grow, but there is no public roadmap.
- **Stoat/Revolt**: Named as a Discord alternative but too young to evaluate now. Worth a check later.
- **XMPP**: Not covered. It has MUC and threading add-ons, but the ecosystem is fragmented and mobile clients are weak in 2026.

## Recommendation Signal

For this use case (one operator, room per project, thread per session, bot posts nonstop, operator steers from mobile):

**Zulip is the best fit.** Its mandatory topic threading maps straight to the session-per-thread need with zero extra bot code. The bot API covers all needed actions. Resource use is fair. Mobile apps work well. All features are free when self-hosted.

**Matrix (with conduwuit) is the top backup.** Lower resource use, richer protocol, real E2E encryption, and more client choices. But threading takes more bot code and the ecosystem has more parts to manage.

**Mattermost is a solid third pick** if Slack-like UX matters. The open-core license and missing E2E encryption are downsides.

**Campfire is ruled out** because it has no threads and a bare-bones bot API.
