---
source-id: kamal-deploy-overview
type: web
url: "https://kamal-deploy.org/"
title: "Kamal 2 -- Deploy Web Apps Anywhere (37signals)"
fetched: 2026-04-06T22:00:00Z
---

# Kamal 2 -- Deploy Web Apps Anywhere

Kamal is a deployment tool from 37signals (makers of Basecamp and HEY) for running web apps on bare metal or cloud VMs using Docker and SSH. Version 2.0 replaced Traefik with a custom-built proxy called kamal-proxy.

## Architecture

- **Declarative config**: Single `config/deploy.yml` file defines service, image, servers, proxy, registry, builder, accessories, and environment.
- **Proxy**: kamal-proxy, a lightweight custom proxy built by 37signals. Handles TLS termination, zero-downtime deploys, rolling restarts, canary deploys, and multi-app routing on a single server. Replaces Traefik from v1.
- **TLS**: Automatic Let's Encrypt certificate issuance when `proxy.ssl: true` and a host is configured. Works for single-server deployments. For multi-server, requires external TLS (e.g., Cloudflare).
- **DNS**: Not managed. Users must configure DNS records manually to point to their server IPs.
- **Tunnel**: Not included. No built-in tunnel support.
- **Container**: Docker-based. Builds images, pushes to a registry, pulls on target servers via SSH.
- **Imperative model**: Unlike Kubernetes' declarative reconciliation, Kamal uses imperative commands (like Capistrano for containers).

## Ingress Chain Coverage

| Layer | Covered? | How |
|-------|----------|-----|
| DNS | No | Manual DNS setup required. |
| TLS | Partial | Automatic Let's Encrypt on single server; external for multi-server. |
| Reverse proxy | Yes | kamal-proxy with host-based and path-based routing. |
| Tunnel | No | Not included. |
| Container | Yes | Docker via SSH. |

## Config Example (simplified)

```yaml
service: my-app
image: user/my-app
servers:
  web:
    - 1.2.3.4
proxy:
  ssl: true
  host: app.example.com
registry:
  username: user
  password:
    - KAMAL_REGISTRY_PASSWORD
```

## Composability

Kamal is a **CLI tool**, not a platform. It does one thing well: deploy containerized apps to servers via SSH. kamal-proxy is a separate binary that can theoretically be used independently, but it is designed as a Kamal component, not a general-purpose proxy.

Kamal is not a library. You cannot import its proxy or deployment logic into another tool. But its simplicity and single-config-file approach make it easy to wrap in scripts.

## Solo Operator Burden

- Installation: `gem install kamal` or Docker alias.
- No server prep needed beyond SSH access and Docker.
- Single config file. One command to deploy: `kamal deploy`.
- Maintenance: minimal. kamal-proxy is a single Go binary.
- Designed for 37signals' own use (HEY, Basecamp) on their own hardware.

## Comparison to Commodore

- **Scope**: Kamal covers proxy + container. Commodore covers DNS + proxy + TLS + container. Both lack native tunnel support.
- **Architecture**: Kamal is imperative CLI. Commodore is hexagonal with adapters. Both reject Kubernetes complexity.
- **DNS**: Kamal does not automate DNS. Commodore does via CloudflareDNS adapter.
- **Composability**: Both are built for composition, but differently. Kamal composes with external tools (you bring your own DNS, tunnel). Commodore composes internally via port/adapter interfaces.

## Key Takeaway

Kamal is the strongest "deploy to your own servers" tool for solo operators. It covers proxy + TLS + container in a single config file and single command. It does not cover DNS or tunnel, expecting you to handle those externally. Clean, minimal, and battle-tested at 37signals scale.
