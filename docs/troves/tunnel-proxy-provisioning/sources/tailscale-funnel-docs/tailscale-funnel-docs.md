---
source-id: tailscale-funnel-docs
type: web
url: "https://tailscale.com/kb/1223/funnel"
title: "Tailscale Funnel -- Tailscale Docs"
fetched: 2026-04-06T17:02:56Z
---

# Tailscale Funnel

Tailscale Funnel routes traffic from the public internet to a local service on a device in your tailnet. Anyone can access it, even without Tailscale.

## How It Works

1. Funnel creates a unique URL under your tailnet domain (`*.ts.net`).
2. Public DNS resolves the URL to a Funnel relay server IP, not your device IP.
3. The relay server creates a TCP proxy over Tailscale to your device (encrypted, end-to-end).
4. Your device's Tailscale instance terminates TLS and passes the request to the local service.
5. Responses return via the same encrypted proxy. The relay server cannot decrypt traffic.

## Requirements and Limitations

- Tailscale v1.38.3 or later.
- MagicDNS enabled.
- HTTPS enabled with valid certificates for your tailnet.
- A `funnel` node attribute in the tailnet policy file.
- Can only use DNS names in your tailnet domain (`*.ts.net`) -- no custom domains.
- Ports limited to 443, 8443, and 10000.
- TLS-only connections.
- Non-configurable bandwidth limits.
- Beta status as of January 2026.

## Usage

```bash
tailscale funnel 3000
# Available on the internet:
# https://amelie-workstation.pango-lin.ts.net
# |-- / proxy http://127.0.0.1:3000
```

## Key Properties

- **Single binary**: Tailscale client is the only dependency.
- **No inbound ports**: outbound-only via WireGuard mesh.
- **DNS**: automatic under `*.ts.net`; no custom domain support.
- **TLS**: automatic Let's Encrypt certificates.
- **NAT traversal**: STUN/TURN with hole punching and relay fallback.
- **Dynamic backends**: `tailscale funnel` command registers backends on the fly.
- **Cost**: free on Personal plan; available on Personal Plus, Premium, Enterprise.
- **Limitations**: no custom domains, limited ports, bandwidth caps, beta status.
- **Best for**: development, personal projects, sharing from behind NAT/CGNAT.
