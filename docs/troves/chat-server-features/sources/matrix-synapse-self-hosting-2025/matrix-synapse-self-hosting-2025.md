---
source-id: "matrix-synapse-self-hosting-2025"
title: "Self-hosting Matrix in 2025 — Matthias Klein"
type: web
url: "https://blog.klein.ruhr/self-hosting-matrix-in-2025"
fetched: 2026-04-06T20:00:00Z
---

# Self-hosting Matrix in 2025

## Overview

A practical experience report on self-hosting Matrix with Synapse in 2025. The author reports that the setup experience has improved dramatically compared to earlier years.

## Architecture

The setup uses:

- **Synapse** as the Matrix homeserver (Python).
- **PostgreSQL** as the database.
- **Traefik** as the reverse proxy with Let's Encrypt.
- **Docker Compose** for orchestration.

## Threading Model

Matrix supports threading via MSC3440, which landed in Matrix spec v1.4. Threads use `m.thread` relations. Element X and other modern clients render threads. However, threading in Matrix is a relation on messages rather than a first-class structural primitive — it was added later and is less mature than Zulip's topic model.

## Rooms and Spaces

Matrix rooms are the primary organizational unit. Spaces (introduced in later spec versions) group rooms hierarchically, similar to Discord servers or Slack workspaces. A bot can create rooms programmatically via the client-server API.

## Bot API

Matrix uses a standard client-server API (REST/JSON). Any Matrix client library can be used to build bots. Key capabilities:

- Create rooms.
- Join/leave rooms.
- Send messages (text, formatted, files).
- Read messages via sync API.
- Listen for events in real time.
- Manage room state (topic, name, permissions).
- Application Service API for bridges and more advanced bots.

Popular bot SDKs: matrix-nio (Python), matrix-bot-sdk (TypeScript), mautrix (Go/Python).

## Mobile Clients

- **Element X** (iOS, Android): The new flagship client. Uses Sliding Sync for much faster room loads and synchronization. Open source.
- **Element Classic**: Older but more feature-complete.
- **FluffyChat**: Lightweight alternative.
- **SchildiChat**: Element fork with UI improvements.
- Third-party clients available for all platforms.

## Resource Footprint

Single-user Synapse server (2025 data):

- Synapse: 222.5 MB RAM, 0.52% CPU.
- PostgreSQL: 117.9 MB RAM, 0.10% CPU.
- Total: under 350 MB RAM, under 1% CPU.

For small groups (under 20 users):

- Conduit/conduwuit can run on a Raspberry Pi 4 with 4 GB RAM.
- Synapse is too resource-heavy for a Pi.

For larger deployments:

- Production Synapse recommended: 4+ GB RAM, 4+ CPU cores.
- Database grows with federation and large rooms (80+ GB for heavily federated servers).

## Self-Hosting Complexity

Synapse requires Docker Compose with PostgreSQL, a reverse proxy, DNS configuration, and well-known delegation files. It is a multi-service deployment. The 2025 experience is much smoother than earlier years, but it is still more complex than a single-binary solution.

## E2E Encryption

Matrix supports end-to-end encryption via Olm/Megolm. E2E encryption is optional per room. For bots, E2E encryption adds complexity — bots need to handle key management and device verification. Some bot frameworks handle this; others struggle with it (see hermes-agent issues with undecryptable Megolm events). For a self-hosted single-operator setup, disabling E2E in bot rooms is pragmatic.

## Federation

Matrix is federated by design. When a user on server A joins a room on server B, room data is replicated. Federation can be disabled for private deployments. The federation tester tool validates configuration.

## Authentication Options

- Username/password (built-in).
- Matrix Authentication Service (MAS) for SSO.
- OIDC/OpenID Connect.
- LDAP via synapse-ldap3 module.
- SAML2.
- CAS.
