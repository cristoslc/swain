---
source-id: "whatsapp-business-api-platform"
title: "WhatsApp Business API — Pricing, Rate Limits, Threading, and Provisioning for Bot-Driven Workflows"
type: web
url: "https://business.whatsapp.com/products/platform-pricing"
fetched: 2026-04-06T22:00:00Z
---

# WhatsApp Business API — Pricing, Rate Limits, Threading, and Provisioning for Bot-Driven Workflows

## Overview

WhatsApp Business API (Cloud API, hosted by Meta) lets businesses send and receive messages programmatically. This source evaluates it as a hosted chat transport for a bot-driven development workflow where one operator steers agentic coding sessions from a phone.

## Pricing Model

As of July 2025, Meta shifted from conversation-based pricing to per-message pricing. The model has four categories:

| Category | Cost (approx., US market) | Notes |
|---|---|---|
| Marketing | $0.05-0.25/msg | Most expensive. Volume discounts excluded. |
| Utility | ~$0.02-0.05/msg | Volume tiers available. Free within 24h service window. |
| Authentication | ~$0.03/msg domestic | International auth can reach $0.60+/msg. |
| Service | Free | Within 24-hour customer service window after user initiates. |

**The 24-hour customer service window is the key mechanism.** When a user (the operator) sends a message to the bot, the bot can reply with service messages for free for 24 hours. For a swain session where the operator initiates by sending a command and the bot replies with session output, most messages would fall within the service window and cost nothing.

**However:** If the bot needs to send messages without the operator messaging first (proactive notifications, session start alerts, error alerts), those require pre-approved template messages and incur per-message fees. Template messages must be submitted to Meta for approval, which takes up to 24 hours.

**No true free tier.** There is no "free plan" like Telegram or Discord. Meta offers a test phone number for development, but production use requires a verified business account and incurs per-message costs for template messages outside the service window.

## Rate Limits and Throughput

### Messaging Volume Tiers

WhatsApp limits outbound business-initiated messages (templates) by tier:

| Tier | Unique Users per 24h | How to Reach |
|---|---|---|
| Unverified | 250 | Default for new accounts. |
| Tier 1 | 1,000 | Interact with 1,000 unique contacts in 30 days. |
| Tier 2 | 10,000 | Sustained quality + volume. |
| Tier 3 | 100,000 | Sustained quality + volume. |
| Unlimited | No cap | Exceptional quality rating. |

These limits apply to unique recipients, not total messages. For swain's use case (one operator), the volume tier is irrelevant — the bot talks to one person.

### API Throughput

The Cloud API supports approximately 80 messages per second (MPS) by default per phone number. This is far more than any chat platform's per-channel limit. The binding constraint is not throughput but cost and the 24-hour service window.

### Quality Rating

Meta assigns a quality rating (high, medium, low) based on user feedback, opt-outs, and response rates. Low quality ratings reduce messaging limits. For a solo-operator bot where the operator never reports the bot, quality should remain high.

## Threading Support

WhatsApp has no threading model analogous to Zulip topics, Slack threads, or Discord forums.

- **Reply-to-message** exists. Any message can quote a previous message. This creates a visual link but not a navigable thread.
- **No thread containers.** There is no way to group messages into a named session or topic.
- **No forum mode.** Unlike Telegram supergroups with forum topics, WhatsApp groups are flat message streams.
- **Workaround: one group per session.** The bot could create a new WhatsApp group for each session. This is clunky — groups require adding participants, the operator's phone would fill with groups, and group creation is manual via the client app (the Bot API cannot create groups).
- **Workaround: message prefixes.** Prefix each message with `[session-id]`. This is a filtering mechanism, not real threading. The operator cannot collapse or navigate sessions.

For swain's session-per-thread requirement, WhatsApp is the weakest platform evaluated. There is no viable way to isolate sessions without creating separate groups, which is operationally impractical.

## Security

- **End-to-end encryption** is enabled by default for personal WhatsApp messages. However, WhatsApp Business API messages are **not E2E encrypted** — Meta processes them on Cloud API servers.
- **Meta sees message content.** Cloud API messages pass through Meta's infrastructure. Meta's privacy policy permits using business messaging data for ads targeting and platform improvement.
- **Metadata exposure.** Phone numbers, message timestamps, delivery receipts, and contact lists are visible to Meta regardless of encryption status.
- **No formal compliance certifications** comparable to Slack (SOC 2) or Teams (FedRAMP). WhatsApp relies on Meta's broader privacy framework.

For dev session data (code output, architecture decisions, build logs), the lack of E2E encryption and Meta's data practices make WhatsApp the weakest security story among evaluated platforms.

## Bot Account Requirements

Setting up a WhatsApp Business API bot requires:

1. **Meta Business Account.** Create or use an existing Meta Business account at business.facebook.com.
2. **Meta Business Verification.** Submit business documents (registration papers, tax ID, proof of address). Takes up to 24 hours. Requires a real registered business entity.
3. **Phone Number.** A dedicated phone number not linked to any existing WhatsApp account. Must receive SMS or voice calls for verification. Cannot be a personal number already on WhatsApp.
4. **WhatsApp Business Account (WABA).** Created within Meta Business Suite after business verification.
5. **App Registration.** Create an app in Meta Developer Portal, enable WhatsApp product, generate access tokens.
6. **Display Name Approval.** Business display name must be approved by Meta before the bot can send messages.
7. **Two-Step Verification.** 6-digit PIN required for registration.

### Provisioning Automability

The setup is the most bureaucratic of any evaluated platform:

- **Manual steps:** Business verification, phone number procurement, display name approval, and initial WABA creation all require manual interaction with Meta's portal.
- **API-automatable after setup:** Once the WABA exists and is verified, message sending, template submission, and webhook configuration are API-driven.
- **No programmatic account creation.** Unlike Zulip (API-create bots) or Discord (Developer Portal + API), the WhatsApp onboarding cannot be scripted end-to-end.
- **Embedded Signup flow** can reduce initial setup to 10-15 minutes but still requires human interaction.

`/swain-stage` could not automate WhatsApp provisioning. The operator would need to manually complete Meta Business Verification, procure a phone number, and configure the WABA before swain could connect.

## Self-Hosted Path

There is no self-hosted WhatsApp. The platform is entirely Meta-controlled. The On-Premises API (deprecated in favor of Cloud API) still ran through Meta's infrastructure for message routing. Migration away from WhatsApp means switching platforms entirely — no data export, no message history portability.

## Key Limitations for Swain Use Case

1. **No threading.** The session-per-thread pattern has no clean implementation.
2. **Cost for proactive messages.** Bot-initiated notifications outside the 24h window cost money.
3. **Meta Business Verification.** Requires a registered business entity — individual developers or hobbyists may not qualify.
4. **No self-hosted fallback.** One-way vendor lock-in with no migration path.
5. **Template approval latency.** New message templates need Meta approval (up to 24h), blocking new notification types.
6. **Phone number requirement.** A dedicated phone number must be procured and cannot be shared with personal WhatsApp.
7. **BSUID migration.** Business-Scoped User IDs required by March 31, 2026, adding API migration complexity.
