---
source-id: pangolin-tunneled-proxy
type: web
url: "https://docs.pangolin.net/about/how-pangolin-works"
title: "Pangolin -- Self-Hosted Tunneled Reverse Proxy with Identity and Access Control"
fetched: 2026-04-06T22:00:00Z
---

# Pangolin -- Self-Hosted Tunneled Reverse Proxy

Pangolin is an open-source, identity-based remote access platform that combines reverse proxy and VPN capabilities into one system. It uses WireGuard tunnels to expose private services without opening inbound ports, and Traefik for HTTP routing. Rapidly growing in the self-hosted community as a Cloudflare Tunnel alternative.

## Architecture

Pangolin is a multi-component system:

- **Pangolin server**: Central management dashboard with identity/access control, resource configuration, and coordination.
- **Newt**: Lightweight WireGuard tunnel client that runs in user space (no root required). Connects remote sites to the Pangolin server via encrypted tunnels.
- **Gerbil**: WireGuard management server that handles peer creation and tunnel lifecycle via HTTP API.
- **Traefik**: Reverse proxy and load balancer. Handles HTTP routing, automatic SSL certificates, and integrates with Traefik plugins (Fail2Ban, CrowdSec).
- **Badger**: Traefik plugin that authenticates every request through Pangolin's identity system.

## Ingress Chain Coverage

| Layer | Covered? | How |
|-------|----------|-----|
| DNS | Partial | Requires manual A record for base domain. Supports wildcard domains so individual resources do not need separate DNS entries. |
| TLS | Yes | Automatic Let's Encrypt via Traefik. |
| Reverse proxy | Yes | Traefik with dynamic configuration from Pangolin. |
| Tunnel | Yes | WireGuard tunnels via Newt (user space, no root). |
| Container | No | Not a deployment tool. Proxies to existing services. |
| Identity/access | Yes | Zero-trust, identity-based access control per resource. |

## Deployment Model

Pangolin requires a VPS with a public IP as the central hub. Remote sites connect outbound to this hub. This is a deliberate architectural choice for reverse proxy use cases. Available as:

- **Pangolin Cloud**: Fully managed hosted service. Free tier available.
- **Self-hosted**: Docker Compose deployment on your own VPS. Community Edition (AGPL-3) and Enterprise Edition available.

## Composability

Pangolin is a **platform**, not a library. Its components (Newt, Gerbil, Traefik) are separate services but designed to work together. Newt could theoretically be used standalone as a WireGuard client, but it is tightly coupled to Pangolin's API.

The system is more composable than Coolify but less than Commodore. Individual components have defined boundaries, but the system expects to own the full tunnel + proxy + identity chain.

## Solo Operator Burden

- Installation: one-command installer for self-hosted.
- Resource overhead: Docker Compose stack with 4+ containers (Pangolin, Gerbil, Traefik, Newt per site).
- Maintenance: regular updates via Docker image pulls.
- Dashboard UI for all configuration.
- Growing community: popular on r/selfhosted, active development.

## Comparison to Commodore

- **Scope overlap**: Pangolin covers tunnel + proxy + TLS + identity. Commodore covers DNS + proxy + TLS + container. Pangolin fills Commodore's tunnel gap. Commodore fills Pangolin's DNS and container gaps.
- **Architecture**: Both use component-based design. Pangolin bundles Traefik + WireGuard + identity. Commodore uses hexagonal port/adapter pattern.
- **Composability**: Pangolin's components are separate Docker services but coupled. Commodore's adapters are swappable by design.
- **Tunnel**: Pangolin's strongest feature. WireGuard tunnels with user-space client, no root needed. Commodore has no tunnel adapter yet.
- **Container deployment**: Pangolin does not deploy containers. It only proxies to running services. Commodore deploys via DockerCompose adapter.

## Key Takeaway

Pangolin is the closest thing to a "self-hosted Cloudflare Tunnel" with added identity management. It covers tunnel + proxy + TLS in one system, which is exactly the gap Commodore needs to fill. However, it does not handle DNS provisioning or container deployment. Its WireGuard-based tunnel approach (via Newt) is the most relevant design pattern for a potential Commodore TunnelPort adapter.
