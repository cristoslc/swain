---
title: "Chat Platform and Deployment Model"
artifact: ADR-037
track: standing
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
linked-artifacts:
  - VISION-006
  - INITIATIVE-018
depends-on-artifacts: []
evidence-pool: "chat-server-features"
---

# Chat Platform and Deployment Model

## Context

VISION-006 (Untethered Operator) needs a chat platform for the operator to steer agentic sessions from any device. The platform must support rooms (project separation), threads (session separation), a bot API (programmatic posting and room management), and mobile clients. Every swain adopter will face the ops burden of whatever platform we choose, so the default path must be zero-ops.

## Decision

Hosted chat platforms are the default deployment model for v1. Self-hosted is an option, not a requirement.

Zulip Cloud is the recommended starting platform:

- Native stream+topic model maps directly to room-per-project, topic-per-session with zero custom bot threading code.
- Same API as self-hosted Zulip — bot code is identical, migration is seamless and bidirectional.
- $0/month (free tier, 10K message history) or $8/month (Standard, full history) for a single operator. Bots are generic accounts and do not count as paid users.
- Python SDK (`zulip` package) is mature and maintained.

Slack and Telegram are viable Tier 2 alternatives — operators can use them via the plugin system. Self-hosted Zulip or conduwuit (Matrix) are Tier 3 for operators needing full control.

The chat adapter is a plugin (subprocess speaking NDJSON over stdio). Platform choice is an operator config decision, not an architectural one.

## Alternatives Considered

- **Self-hosted only (Zulip or conduwuit on VPS).** Eliminated as default because it adds $6-12/month VPS cost plus ongoing server maintenance for every adopter. Zulip's five-service architecture (app, PostgreSQL, Redis, RabbitMQ, Memcached) is heavyweight for a solo operator. Conduwuit is lighter (single binary) but threading requires explicit bot management of MSC3440 event relations.
- **Telegram as default.** Zero ops, rich bot API, forum topics for threading. But rate-limited to 20 messages/minute per group — too slow for continuous bot posting during active sessions. No E2E encryption for group chats.
- **Slack as default.** Excellent bot SDK (Bolt for Python), native threading. But free plan limits history to 90 days and rate-limits to 1 message/second per channel. Paid plan starts at $7.25/user/month.
- **Discord as default.** Free and generous, but designed for gaming communities. Forum channels with auto-archiving add friction. Security story is weaker for development workflows.
- **Campfire (37signals).** Eliminated — no threading, no room creation API, no programmatic room management. The prefix-as-room workaround is non-viable.

## Consequences

- Adopters get a working chat bridge with zero server provisioning — `/swain-stage` registers a Zulip bot and connects bridges.
- The 10K message limit on the free tier may require pruning or upgrading for active projects.
- Zulip Cloud is a vendor dependency — mitigated by same-API self-hosted migration path.
- The plugin architecture means this decision is not permanent for any individual operator.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Informed by chat-server-features trove (6 extensions, 20+ sources). |
