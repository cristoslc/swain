---
source-id: "zulip-self-hosting"
title: "Self-host Zulip — Requirements, Features, and Pricing"
type: web
url: "https://zulip.com/self-hosting/"
fetched: 2026-04-06T20:00:00Z
---

# Self-host Zulip — Requirements, Features, and Pricing

## Overview

Zulip is an open-source team chat application with a unique topic-based threading model. The self-hosted version is 100% open source and includes all features available on Zulip Cloud. There is no "open core" catch.

## Threading Model

Zulip uses a two-level hierarchy: **streams** (channels) and **topics** (threads within channels). Every message belongs to both a stream and a topic. This is not optional threading bolted on after the fact; it is the core organizational primitive. Topics max out at 60 characters.

This model means conversations are automatically organized. A bot posting to a specific stream and topic effectively creates a thread that stays separate from other conversations in the same stream.

## Streams and Rooms

Streams function as channels. They can be public or private. Users can subscribe and unsubscribe per-stream. Streams support muting and notification controls at the topic level.

## Bot API

Zulip provides a comprehensive REST API with official Python and JavaScript SDKs. Bots can:

- Create and manage streams.
- Send messages to streams with specific topics.
- Read messages from streams, topics, or by stream-id.
- Filter by private messages and mentions.
- React to messages with emoji.
- Upload files.
- Use outgoing webhooks and incoming webhooks.
- Over 100 native integrations.

Bot types include interactive bots (respond to @-mentions), outgoing webhook bots, and generic API bots. The Python SDK provides a bot framework with `handle_message` callbacks.

## Mobile Clients

Zulip has native apps for iOS and Android built with React Native. Desktop apps use Electron. All apps are open-source. The mobile experience is rated well by users, with push notifications working on self-hosted instances (free for up to 10 users or qualifying communities; paid plans for unlimited).

## Resource Footprint

- Fewer than 100 users: 1 CPU, 2 GB RAM (with 2 GB swap), 10 GB disk.
- 100+ users: 2 CPUs, 4 GB RAM minimum.
- 300+ daily active users: 4 GB RAM recommended.
- 2000+ daily active users: 32 GB RAM plus 32 GB for database.
- Database: PostgreSQL (required).
- OS: Ubuntu or Debian Linux (native install); Docker available.

## Self-Hosting Complexity

Zulip provides an installer script that sets up Nginx, PostgreSQL, Redis, RabbitMQ, and memcached. It is a multi-service deployment but the installer handles all of it. Upgrades are scripted. Docker deployment is also supported. Not a single binary.

## E2E Encryption

Zulip does not support end-to-end encryption. Messages are encrypted in transit (TLS) and at rest on the server, but the server can read all messages. For a self-hosted single-operator setup, this is not a significant concern since you control the server.

## Authentication Options

All authentication methods are available on the free self-hosted version:

- Email/password.
- LDAP (including Active Directory) with user sync.
- SAML (Okta, OneLogin, Entra ID/AzureAD, Keycloak, Auth0).
- OpenID Connect.
- Google OAuth.
- GitHub OAuth.
- GitLab OAuth.
- Apple OAuth.

## AI Integrations

Zulip has built-in support for AI integrations, including topic summarization using configurable LLM models. The interactive bots API allows AI models to participate in conversations.

## Pricing

Self-hosted Zulip is completely free with all features. Paid plans ($3.50-$8/user/month) add support services and unlimited mobile push notifications.
