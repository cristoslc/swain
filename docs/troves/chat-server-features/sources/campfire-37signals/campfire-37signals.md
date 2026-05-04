---
source-id: "campfire-37signals"
title: "Campfire by 37signals — Simple Self-Hosted Group Chat"
type: web
url: "https://once.com/campfire"
fetched: 2026-04-06T20:00:00Z
---

# Campfire by 37signals — Simple Self-Hosted Group Chat

## Overview

Campfire is a self-hosted group chat system from 37signals (makers of Basecamp). It is free, open source (MIT license), and designed for simplicity. The source code is a Ruby on Rails application that serves as educational material for how 37signals builds software.

## Threading Model

**Campfire does not support threads.** Messages are flat within rooms. There is no thread, topic, or reply-to-message structure. This is a fundamental limitation for session-per-thread mapping.

## Rooms

Campfire supports rooms (public and private) and direct messages. Rooms can be open to everyone or restricted. No concept of spaces or room hierarchy.

## Bot API

Campfire has a simple HTTP webhook-based bot API:

- Bots receive POST requests when @-mentioned.
- Bots can respond with text or attachments.
- Bot authentication uses tokens embedded in URLs.
- A `campfire-bot-kit` repository provides examples.
- Webhook payloads include room and message paths.

**Limitations:**

- No API for creating or managing rooms programmatically.
- No API for reading message history.
- No thread management (threads do not exist).
- Bots are reactive (respond to mentions) rather than proactive (cannot independently poll or post without being triggered).
- The API is minimal compared to Matrix, Zulip, or Mattermost.

## Mobile Clients

Campfire uses a Progressive Web App (PWA) approach rather than native apps. It works in mobile browsers and can be installed as a PWA from the home screen. Supports push notifications and badge counts. No native iOS or Android apps.

## Resource Footprint

| Concurrent Users | RAM  | CPU   |
|------------------|------|-------|
| 250              | 2 GB | 1 CPU |
| 1,000            | 8 GB | 4 CPU |
| 5,000            | 32 GB | 16 CPU |
| 10,000           | 64 GB | 32 CPU |

For a single-operator use case, resource requirements are minimal (2 GB RAM, 1 CPU).

## Self-Hosting Complexity

**Very simple installation:**

```
curl https://get.once.com/campfire | sh
```

Single command installation via the ONCE CLI. Runs on any server that can host WordPress. Works on local machines, closet servers, or cloud instances. Automatic updates (can be disabled). Can run air-gapped without internet access.

## E2E Encryption

No end-to-end encryption. Messages are stored in plaintext on the server. TLS for transport only.

## Authentication

Basic username/password authentication. No SSO, LDAP, SAML, or OIDC support mentioned. Simple invite-based user management.

## Key Strengths

- Extreme simplicity.
- Beautiful, clean UI (Rails-quality code).
- Zero recurring cost.
- Open source (MIT).
- Air-gap capable.

## Key Weaknesses for Bot-Driven Workflow

- No threads — a dealbreaker for session-per-thread mapping.
- Minimal bot API — no room creation, no message history reading.
- No SSO or advanced auth.
- No federation.
- PWA-only mobile experience (no native apps).
