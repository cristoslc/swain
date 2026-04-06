---
source-id: dokku-architecture-overview
type: web
url: "https://dokku.com/docs/development/architecture/"
title: "Dokku Architecture -- Plugin-Based PaaS with Swappable Proxy"
fetched: 2026-04-06T22:00:00Z
---

# Dokku Architecture Overview

Dokku is a Docker-powered PaaS that calls itself "the smallest PaaS implementation you've ever seen." It provides a Heroku-like `git push` deployment experience on a single server. Its architecture is fully plugin-based, making it the most composable of the self-hosted PaaS options.

## Architecture

- **Core**: Bash + Go hybrid. The `dokku` binary is a bash script that routes commands to plugins via the `plugn` trigger system.
- **Plugin system**: All functionality is implemented through plugins. Plugins communicate via triggers (events), not direct calls. This provides loose coupling and composability.
- **Proxy**: Swappable via plugins. Supports Nginx (default), Caddy, Traefik, HAProxy, and OpenResty. Proxy management was decoupled from nginx-vhosts in v0.5.0.
- **TLS**: SSL certificate management via `certs` plugin. Let's Encrypt integration via `dokku-letsencrypt` community plugin. Automatic renewal supported.
- **DNS**: Manual setup. Dokku provides domain configuration per app (`dokku domains:add myapp example.com`) but does not create DNS records.
- **Tunnel**: Not included. No built-in tunnel support.
- **Container**: Docker-based. Supports multiple schedulers: docker-local (default), K3s, and Nomad.
- **Builder**: Swappable. Herokuish buildpacks, Cloud Native Buildpacks, Nixpacks, Dockerfile, and more.

## Ingress Chain Coverage

| Layer | Covered? | How |
|-------|----------|-----|
| DNS | No | Manual DNS setup. Per-app domain management via CLI. |
| TLS | Yes | Via certs plugin + letsencrypt community plugin. |
| Reverse proxy | Yes | Swappable: Nginx, Caddy, Traefik, HAProxy, OpenResty. |
| Tunnel | No | Not included. |
| Container | Yes | Docker with swappable schedulers. |

## Plugin Trigger System

Dokku's key architectural feature is its trigger system. When a trigger fires, `plugn` runs matching scripts from all enabled plugins:

```
Plugin A (fires "post-deploy") --> plugn --> Plugin B (listens)
                                         --> Plugin C (listens)
```

Trigger categories include: app lifecycle, build, deploy, proxy, and git. This is conceptually similar to Commodore's port/adapter pattern but implemented as an event bus rather than interface injection.

## Key Design Decisions

- **Plugin-based**: All features are plugins, including core ones. Community plugins extend databases, caching, tunneling.
- **Bash + Go hybrid**: Bash for orchestration, Go for performance.
- **File-based state**: No database. All state lives in `/var/lib/dokku/` as flat files. Inspectable with standard Unix tools.
- **Docker foundation**: Container runtime, networking, and image management delegated to Docker.

## Composability

Dokku is the **most composable** self-hosted PaaS. Its plugin architecture means:

- Proxy is swappable (Nginx, Caddy, Traefik, HAProxy, OpenResty).
- Scheduler is swappable (docker-local, K3s, Nomad).
- Builder is swappable (herokuish, pack, dockerfile, nixpacks).
- Any component can be replaced without changing others.

However, Dokku is still a CLI tool, not a library. You cannot import its proxy management or domain configuration into another tool. The plugin system is executable-based, not API-based.

## Solo Operator Burden

- Installation: single script on Ubuntu/Debian.
- Resource overhead: ~200 MB RAM. Lightest of all PaaS options.
- CLI-first. No web UI (Dokku Pro adds a commercial UI).
- Mature: available since 2013. Stable, well-documented, large plugin ecosystem.
- Single-server only (no multi-server in open-source version).

## Comparison to Commodore

- **Architecture**: Both are plugin/adapter-based. Dokku uses trigger-based plugins. Commodore uses hexagonal port/adapter interfaces.
- **Composability**: Both emphasize swappable components. Dokku's proxy and scheduler are swappable via plugins. Commodore's DNS, proxy, and container adapters are swappable via ports.
- **DNS**: Neither automates DNS record creation in the open-source version. Commodore's CloudflareDNS adapter is ahead here.
- **Tunnel**: Neither has tunnel support. Both would need it added.
- **Scope**: Dokku is a full PaaS (git push to deploy). Commodore is an infrastructure orchestration layer (compose DNS + proxy + container).

## Key Takeaway

Dokku's plugin architecture is the most relevant prior art for Commodore's adapter pattern. Both share the principle that infrastructure components should be swappable. Dokku proves this works for proxy, builder, and scheduler -- but stops short of DNS automation and tunnel provisioning. Its trigger system is an event-bus alternative to Commodore's port/adapter injection pattern.
