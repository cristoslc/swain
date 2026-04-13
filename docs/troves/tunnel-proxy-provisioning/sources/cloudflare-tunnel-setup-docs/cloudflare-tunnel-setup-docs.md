---
source-id: cloudflare-tunnel-setup-docs
type: web
url: "https://developers.cloudflare.com/tunnel/setup/"
title: "Set up Cloudflare Tunnel -- Cloudflare Docs"
fetched: 2026-04-06T17:02:55Z
---

# Set up Cloudflare Tunnel

Cloudflare Tunnel creates an encrypted tunnel between your origin web server and Cloudflare's nearest data center, without opening any public inbound ports.

## Prerequisites

- A Cloudflare account.
- A domain on Cloudflare (required to publish applications).
- A server or VM with internet access to install `cloudflared`.
- If behind a restrictive firewall, the server must reach Cloudflare on port 7844.

## Creating a Tunnel

### Dashboard Method

1. Go to Networking > Tunnels in the Cloudflare dashboard.
2. Select Create Tunnel and name it (e.g., `production-web`).
3. Select your OS and architecture, copy the install commands, run them on your server.
4. Once connected, the tunnel appears as `Healthy`.

### API Method

1. Create an API token with `Cloudflare Tunnel: Edit` and `DNS: Edit` permissions.
2. POST to `https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/cfd_tunnel` with `name` and `config_src`.
3. The response returns a tunnel `id` and `token`.

## Publishing an Application

Publishing maps a public hostname to a local service.

### Dashboard

1. Select your tunnel, then Add route > Published application.
2. Enter a subdomain, select a domain, set the local service URL (e.g., `http://localhost:80`).

### API

1. PUT ingress rules to the tunnel configurations endpoint with hostname-to-service mappings.
2. Create a CNAME DNS record: `app.example.com` pointing to `<TUNNEL_ID>.cfargotunnel.com` with `proxied: true`.
3. Install `cloudflared` and run with the tunnel token.

All DNS, TLS, and routing happen automatically -- Cloudflare handles CDN caching, WAF, and DDoS protection.

## Quick Tunnels (Development)

For local dev, run `cloudflared tunnel --url http://localhost:8080` to get a random `trycloudflare.com` subdomain. Limited to 200 concurrent requests and no SSE support.

## Key Properties

- **Single binary**: `cloudflared` is the only dependency.
- **No inbound ports**: outbound-only connections.
- **DNS automation**: dashboard or API creates CNAME records automatically.
- **TLS termination**: handled by Cloudflare's edge.
- **Dynamic backends**: ingress rules can be updated via API without restarting the tunnel.
- **Cost**: free tier includes unlimited tunnels; advanced features (Access, WAF) are paid.
- **Protocol support**: HTTP natively; TCP/SSH/RDP require `cloudflared` on client side.
