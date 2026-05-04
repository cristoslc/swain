---
source-id: "zulip-cloud-hosted"
title: "Zulip Cloud — Hosted Platform with Full API Parity to Self-Hosted"
type: web
url: "https://zulip.com/plans/"
fetched: 2026-04-06T22:00:00Z
---

# Zulip Cloud — Hosted Platform with Full API Parity to Self-Hosted

## Overview

Zulip Cloud is the hosted version of Zulip, run by Zulip Inc. It uses the same 100% open-source codebase as self-hosted Zulip. The API is identical. Bot code written for Zulip Cloud works on a self-hosted Zulip server with zero changes — you point the SDK at a different URL.

## Pricing (as of 2026)

| Plan | Cost | Message History | Storage | Key Features |
|---|---|---|---|---|
| **Free** | $0 | 10,000 messages searchable | 5 GB total | Full threading, bot API, integrations, roles, permissions, guest accounts. |
| **Standard** | $6.67/user/month (annual) or $8/month (monthly) | Unlimited | 5 GB per user | Custom user groups, retention policies, logo branding, priority support. |
| **Plus** | $10/user/month (annual) or $12/month (monthly) | Unlimited | 25 GB per user | SAML, SCIM, custom domains, restricted guest access. Minimum 10 users. |

## Bot Billing

Zulip documentation does not explicitly state whether bots count as billable users. Bots are described as a "special kind of user" with limited permissions. Guest users have a generous ratio (5 guests per paid user at no extra charge). For a solo operator with a few bots, the free tier's 10,000-message limit is more likely to be the constraint than user count.

## API Parity with Self-Hosted

Zulip Cloud and self-hosted Zulip run the same software. There is no "open core" catch — every feature available on Cloud is available on self-hosted, and vice versa. The API endpoints, authentication methods, bot framework, and webhook integrations are identical. The only difference is who runs the infrastructure.

This means:
- Bot code targets `zulip.Client(site="https://yourorg.zulipchat.com")` for Cloud or `zulip.Client(site="https://zulip.yourdomain.com")` for self-hosted.
- The `zulip` Python SDK works with both. No adapter changes.
- Webhooks, incoming bots, outgoing bots, and interactive bots all behave identically.

## Migration Path

Zulip provides bidirectional migration tools:
- **Cloud to self-hosted.** Export your organization data from Zulip Cloud and import it into a self-hosted Zulip server. Message history, users, streams, topics, and uploaded files transfer.
- **Self-hosted to Cloud.** Export from self-hosted and import to Zulip Cloud.

The migration preserves message history and organization structure. An operator can start on Zulip Cloud for zero ops and move to self-hosted later if they need data sovereignty or customization — without rewriting any bot code.

## Free Tier Viability for Swain

A solo operator with N bots generating continuous output will hit the 10,000-message search limit quickly. At 20 messages per session and 5 sessions per day, the limit is reached in about 100 days. After the limit, older messages are no longer searchable (but still exist). For a development tool where recent sessions matter most, this may be acceptable. For unlimited history, the Standard plan at $8/month (1 human + bots) is cheap.

## Threading

Zulip's mandatory stream + topic model is unchanged on Cloud. Every message must have a stream and a topic. The bot sets `topic: "session-2026-04-06-001"` and gets an organized thread for free. This is the same gold-standard threading from the self-hosted analysis.

## Provisioning Automability

Creating a Zulip Cloud organization requires manual signup (web form). But once the organization exists:
- Streams can be created via API (`POST /api/v1/users/me/subscriptions`).
- Bots can be created via API (`POST /api/v1/bots`).
- Bot API keys are returned on creation.
- Topics are created implicitly when the first message is sent.

A `/swain-stage` command could: verify the organization exists, create the project stream, register the bot, and store the API key. The initial organization signup is the one manual step.

## Security

Messages on Zulip Cloud are stored on Zulip Inc's infrastructure. Zulip Cloud supports TLS, and Zulip the company has a solid open-source reputation. For a development tool (not handling customer PII), this is acceptable. For operators who need full data sovereignty, self-hosted Zulip is a seamless alternative.
