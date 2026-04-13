---
source-id: "conduit-matrix-homeserver"
title: "Conduit and conduwuit — Lightweight Matrix Homeservers"
type: web
url: "https://conduit.rs/"
fetched: 2026-04-06T20:00:00Z
---

# Conduit and conduwuit — Lightweight Matrix Homeservers

## Overview

Conduit is a lightweight, open-source Matrix homeserver written in Rust. It focuses on easy setup and low system requirements. It ships as a **single binary** with an embedded database (RocksDB by default).

**conduwuit** is a well-maintained hard-fork of Conduit with additional features, bug fixes, performance improvements, moderation tools, and more. As of 2026, conduwuit is the recommended production fork. **Continuwuity** is a community-driven second-degree fork focusing on user experience.

## Threading Model

Conduit/conduwuit implement the Matrix specification, so threading support depends on which spec version is implemented. MSC3440 threading (from Matrix v1.4) support varies by fork. The threading experience depends primarily on the client used (Element X, etc.) rather than the homeserver.

## Rooms and Spaces

Full Matrix room support. Rooms, spaces, and the complete Matrix room hierarchy are supported. Bots interact with rooms using the standard Matrix client-server API.

## Bot API

Same as any Matrix homeserver — the client-server API is the standard REST API. All Matrix bot SDKs work with Conduit/conduwuit.

## Mobile Clients

Same as any Matrix server — Element X, FluffyChat, SchildiChat, and all other Matrix clients work.

## Resource Footprint

- Conduit/conduwuit runs on a Raspberry Pi 4 with 4 GB RAM.
- Single binary, no separate database server needed (embedded RocksDB).
- Database size: approximately 2 GB after a few months with zstd compression.
- Far lower memory and CPU usage than Synapse, especially when joining large rooms.
- Reddit users report conduwuit uses significantly less resources than Synapse with better performance in large rooms.

## Self-Hosting Complexity

**Simplest option in the Matrix ecosystem:**

- Single binary deployment.
- Embedded database (no separate PostgreSQL needed).
- Docker available: `docker run girlbossceo/conduwuit:latest`.
- Configuration via a single TOML file.
- No separate Sliding Sync proxy needed (handled by the server).

## E2E Encryption

Supports Matrix E2E encryption (Olm/Megolm) as part of the Matrix spec implementation.

## Authentication

Supports Matrix standard authentication. SSO/OIDC support depends on the fork version and may be more limited than Synapse.

## Caveats

- Conduit itself is in beta and development has slowed.
- conduwuit is actively maintained but underwent community drama in late 2025/early 2026.
- Continuwuity emerged as the community fork after conduwuit issues.
- Some Matrix features may be missing or incomplete compared to Synapse.
- Federation works but may have edge cases.
