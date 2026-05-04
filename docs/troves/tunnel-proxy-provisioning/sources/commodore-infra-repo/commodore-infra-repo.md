---
source-id: commodore-infra-repo
type: repository
url: "https://github.com/cristoslc/commodore-infra"
title: "Commodore Infrastructure Platform (cristoslc/commodore-infra)"
fetched: 2026-04-06T17:03:00Z
selective: true
highlights:
  - "README.md"
  - "architecture-overview.md"
  - "VISION-001 vision doc"
---

# Commodore Infrastructure Platform

CLI: `cdre`. Hexagonal architecture infrastructure platform separating service definitions from runtime concerns. Services declare what they need and their security classification; the platform resolves placement across heterogeneous hosts.

**Status**: Experimental -- not tested, not production-ready.

## Architecture

Hexagonal (ports and adapters). Core owns domain models and business logic. All external interactions through port interfaces with swappable adapters.

## Driven Ports (Implemented)

| Port | Responsibility | v1 Adapter(s) |
|------|---------------|----------------|
| DNSPort | CRUD DNS records in a zone. | Cloudflare API. |
| ReverseProxyPort | Deploy/fetch/validate proxy config. | SSH + Caddy (docker exec). |
| LoadBalancerPort | Deploy/fetch/validate LB routes. | SSH + HAProxy (systemctl). |
| ContainerPort | Deploy/manage workloads. | Docker Compose (SSH). |
| SecretPort | Fetch secrets by key. | 1Password (op read). |
| InfrastructurePort | Provision hosts, networks, storage. | Placeholder (future). |

## Adapter File Inventory

- `src/commodore/adapters/dns/cloudflare.py` -- Cloudflare DNS adapter (CRUD via API).
- `src/commodore/adapters/reverse_proxy/caddy.py` -- SSH+Caddy reverse proxy adapter.
- `src/commodore/adapters/container/docker_compose.py` -- Docker Compose container adapter.
- `src/commodore/adapters/loadbalancer/` -- `.gitkeep` only (HAProxy adapter not yet implemented).
- `src/commodore/adapters/infrastructure/` -- `.gitkeep` only (placeholder).
- `src/commodore/adapters/secrets/` -- `.gitkeep` only (placeholder).
- `src/commodore/adapters/frontends/` -- `.gitkeep` only (no driving adapters beyond CLI).

## Service Composition Model

A service declares: workload + classification + DNS record + ingress (reverse proxy site) + load balancer route. All defined in one YAML file and deployed with `cdre apply`.

## What Commodore Covers for Ingress

1. **DNS**: Cloudflare adapter creates/updates/deletes DNS records via API.
2. **Reverse proxy**: Caddy adapter generates Caddyfile blocks, deploys via SSH, reloads Caddy. Caddy handles TLS automatically.
3. **Container deployment**: Docker Compose adapter creates/updates stacks via SSH.
4. **Service composition**: one `cdre apply` triggers DNS + proxy + container in a single operation.

## Gaps Relative to Tunnel-Proxy-Provisioning

1. **No tunnel adapter** -- there is no CloudflaredPort, TailscalePort, or NgrokPort. Traffic exposure assumes direct port access or pre-existing tunnel setup outside Commodore's scope.
2. **LoadBalancer adapter not implemented** -- HAProxy port exists but no adapter code.
3. **Infrastructure adapter not implemented** -- no Terraform/OpenTofu integration yet.
4. **Secrets adapter not implemented** -- 1Password port exists but adapter is `.gitkeep`.
5. **No Traefik adapter** -- only Caddy for reverse proxy.
6. **Experimental status** -- no tests, not production-ready.

## Relevance to VISION-006 Ingress Layer

Commodore already models the DNS + reverse proxy + container composition that VISION-006 needs. The main gap is a tunnel adapter (e.g., CloudflareTunnelAdapter) that would allow Commodore to provision the full ingress chain -- DNS record + tunnel route + reverse proxy backend -- as a single operation. Adding a tunnel port and adapter would close this gap without touching the core.
