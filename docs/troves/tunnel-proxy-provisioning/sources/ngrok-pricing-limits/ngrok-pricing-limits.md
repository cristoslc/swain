---
source-id: ngrok-pricing-limits
type: web
url: "https://ngrok.com/docs/pricing-limits"
title: "ngrok Pricing and Limits"
fetched: 2026-04-06T17:03:01Z
---

# ngrok Pricing and Limits

## Free Tier (2026)

- 1 GB/month bandwidth.
- 1 active endpoint.
- Random domains only (no persistent subdomain).
- Interstitial warning page injected for all free-tier HTML browser traffic (anti-phishing).
- No session timeout -- endpoint stays alive while the process runs.

## Paid Tiers

- **Personal**: $8/month -- 5 GB bandwidth, 1 persistent domain.
- **Pro**: $20/month -- 15 GB bandwidth.
- **Enterprise**: $39/month -- higher limits.

## Recent Changes (February 2026)

ngrok dramatically restricted its free tier. The DDEV open-source project opened an issue to consider dropping ngrok as its default sharing provider due to the tightened limits.

## Protocol Support

- HTTP, TLS, and TCP.
- No UDP support as of 2026 -- rules out game servers, VoIP, CoAP, DTLS.

## Key Properties

- **Single binary**: easy install.
- **DNS**: ngrok provides random or persistent subdomains under `ngrok-free.app` / `ngrok.app`.
- **Custom domains**: paid plans only.
- **TLS**: handled by ngrok's edge.
- **Dynamic backends**: `ngrok http <port>` registers backends instantly.
- **API**: ngrok provides an API for managing tunnels programmatically.
- **Inspection**: built-in request inspection dashboard (useful for webhook development).
- **Cost model**: free tier severely limited; paid plans start at $8/month.
- **Best for**: development/testing, webhook debugging. Less suitable for production self-hosted services due to cost and bandwidth limits.
