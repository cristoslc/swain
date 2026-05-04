---
source-id: caddy-automatic-https-docs
type: web
url: "https://caddyserver.com/docs/automatic-https"
title: "Automatic HTTPS -- Caddy Documentation"
fetched: 2026-04-06T17:02:58Z
---

# Caddy Automatic HTTPS

Caddy was the first web server to use HTTPS automatically and by default. It provisions TLS certificates for all sites, keeps them renewed, and redirects HTTP to HTTPS.

## Overview

- Public DNS names get certificates from Let's Encrypt or ZeroSSL via ACME.
- Local/internal hostnames get self-signed certificates from Caddy's built-in CA.
- All managed certificates are auto-renewed. HTTP redirects to HTTPS automatically.

## Requirements for Public Domains

- A/AAAA records pointing to the server.
- Ports 80 and 443 externally accessible (or forwarded to Caddy).
- Writeable, persistent data directory.
- Domain name appears in the config.

If these are met, HTTPS works with zero additional configuration.

## ACME Challenges

1. **HTTP challenge** (default): CA requests a resource over port 80.
2. **TLS-ALPN challenge** (default): CA requests a resource over port 443.
3. **DNS challenge** (manual): CA looks up a TXT record. Does not require open ports. Needs DNS provider credentials. Enables wildcard certificates.

## On-Demand TLS

Caddy can obtain certificates dynamically during the first TLS handshake for unknown domains. Useful for SaaS platforms where customers add custom domains. Requires an "ask" endpoint to prevent abuse.

## Dynamic Configuration

- REST API at `localhost:2019` for live config changes without restart.
- `/config/` endpoint for full JSON config.
- `/load` replaces the entire config atomically.
- Routes can be added at runtime.
- Dynamic upstream discovery modules for rapidly changing environments.

## Issuer Failover

Caddy is the first server to support fully-redundant, automatic failover between CAs. Default: Let's Encrypt primary, ZeroSSL fallback. Retries with exponential backoff up to 30 days.

## Tailscale Integration

Domains ending in `.ts.net` are handled by the local Tailscale instance for certificate provisioning, enabling Caddy + Tailscale Serve/Funnel without additional config.

## Key Properties

- **Single binary**: Go, no dependencies.
- **Automatic TLS**: zero-config for public and local domains.
- **API-driven**: live configuration via REST API, no restarts.
- **On-demand TLS**: certificates issued at handshake time for dynamic domains.
- **Reverse proxy**: built-in with load balancing, health checks, retries.
- **HTTP/3 (QUIC)**: supported out of the box.
- **ECH support**: Caddy is the first server to automatically generate, publish, and serve Encrypted ClientHello configs.
- **Cost**: free, open source (Apache 2.0).
