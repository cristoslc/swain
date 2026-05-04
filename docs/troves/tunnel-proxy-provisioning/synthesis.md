# Tunnel-Proxy-Provisioning Synthesis

Research question: Can DNS + TLS + reverse proxy + tunnel be provisioned as a single automated operation, and which tools compose well for VISION-006 ingress?

## Key Findings

### Single-operation provisioning is achievable today with two tool combinations

**Cloudflare Tunnel + Cloudflare DNS** comes closest to a single-operation stack. One script can create a tunnel, add an ingress rule, and create a CNAME record -- all through the Cloudflare API. TLS terminates at Cloudflare's edge with no setup. No inbound ports are needed. One provider owns the entire DNS + TLS + tunnel + routing chain. (`cloudflare-tunnel-setup-docs`)

**Caddy + DNS provider API** covers the reverse proxy + TLS layer in one step. Caddy issues certificates the moment a domain appears in config. Its REST API (`localhost:2019`) lets you add backends without restarts. Adding a new service takes two calls: (1) create a DNS record, (2) POST a route to Caddy. TLS just works. (`caddy-automatic-https-docs`)

### No self-hosted PaaS covers the full ingress chain

All five self-hosted PaaS platforms surveyed (Coolify, Dokploy, CapRover, Dokku, Kamal) require manual DNS setup. None create DNS records programmatically. All provide automatic TLS via Let's Encrypt. All include a reverse proxy. Only Coolify and Dokploy have documented Cloudflare Tunnel integrations -- neither has native tunnel support. (`coolify-paas-overview`, `dokploy-paas-comparison`, `kamal-deploy-overview`, `dokku-architecture-overview`)

This confirms the original gap: **no lightweight tool unifies DNS + proxy + tunnel in one config file.** The Kubernetes stack (Traefik + cert-manager + external-dns) does, but it is too heavy for a solo operator.

### Composability tiers

**Tier 1 -- Full-stack tunnel services** (tunnel + DNS + TLS in one product):
- Cloudflare Tunnel: best overall for production. Free tier is generous. DDoS protection included. API for full automation. (`cloudflare-tunnel-setup-docs`, `onidel-funnel-cf-nginx-comparison`)
- Tailscale Funnel: easiest setup but limited -- no custom domains, restricted ports (443/8443/10000), bandwidth caps, beta status. Best for dev/personal. (`tailscale-funnel-docs`)
- ngrok: severely restricted free tier since Feb 2026 (1 GB/month, 1 endpoint, interstitial page). No UDP. Best for webhook debugging, not production. (`ngrok-pricing-limits`)

**Tier 2 -- Self-hosted PaaS platforms** (proxy + TLS + container, no DNS or tunnel):
- Coolify: most features, heaviest resource footprint (~500-700 MB RAM idle). Traefik or Caddy proxy. Cloudflare Tunnel integration documented. Monolithic -- not usable as a library. (`coolify-paas-overview`, `dokploy-paas-comparison`)
- Dokploy: lightest PaaS with a UI (~350 MB RAM idle). Traefik-based. Docker Compose-native. Cloudflare Tunnel integration documented. (`dokploy-paas-comparison`)
- CapRover: Nginx-based, Docker Swarm. Mature but slower development. No tunnel integration. (`dokploy-paas-comparison`)
- Dokku: most composable PaaS. Plugin-based architecture with swappable proxy (Nginx, Caddy, Traefik, HAProxy, OpenResty), scheduler (docker-local, K3s, Nomad), and builder. Lightest at ~200 MB RAM. CLI-only. (`dokku-architecture-overview`)

**Tier 3 -- Deployment tools** (proxy + container, no DNS or tunnel or TLS management):
- Kamal 2: single-config-file deployment from 37signals. Custom kamal-proxy replaces Traefik. Automatic Let's Encrypt on single server. Imperative model. Battle-tested at HEY/Basecamp scale. (`kamal-deploy-overview`)

**Tier 4 -- Self-hosted tunnel+proxy platforms** (tunnel + proxy + TLS, no DNS or container):
- Pangolin: self-hosted Cloudflare Tunnel alternative. WireGuard tunnels via Newt (user-space, no root). Traefik for routing. Identity-based access control. Does not deploy containers -- only proxies to running services. (`pangolin-tunneled-proxy`)

**Tier 5 -- Reverse proxy with automatic TLS** (need separate tunnel/DNS):
- Caddy: simplest config, automatic TLS, REST API for dynamic backends, single binary. (`caddy-automatic-https-docs`, `zeonedge-nginx-caddy-traefik-comparison`)
- Traefik: automatic service discovery from Docker/K8s labels. Higher resource usage. (`zeonedge-nginx-caddy-traefik-comparison`)
- Nginx + Certbot: most performant, most complex. No dynamic backend API without Nginx Plus. (`onidel-funnel-cf-nginx-comparison`)

**Tier 6 -- Not a match**:
- Mutagen: file sync and port forwarding for development. Not a tunnel/proxy/DNS tool. (`mutagen-overview`)

### Dynamic backend registration

Four tools support runtime backend registration without restarts:
1. **Caddy**: REST API at `localhost:2019` -- POST routes, on-demand TLS. (`caddy-automatic-https-docs`)
2. **Traefik**: Docker/K8s labels trigger automatic route creation. (`zeonedge-nginx-caddy-traefik-comparison`)
3. **Cloudflare Tunnel**: API-driven ingress rule updates. (`cloudflare-tunnel-setup-docs`)
4. **Pangolin**: Dynamic resource configuration through dashboard and API, propagated to Traefik. (`pangolin-tunneled-proxy`)

### Architecture comparison: composability spectrum

From most composable to most monolithic:

1. **Dokku**: Plugin-based. Proxy, scheduler, and builder all swappable via trigger system. Most "Unix philosophy" approach. (`dokku-architecture-overview`)
2. **Commodore**: Hexagonal port/adapter pattern. DNS, proxy, container adapters swappable by design. (`commodore-infra-repo`)
3. **Pangolin**: Multi-component (Pangolin + Newt + Gerbil + Traefik). Components are separate Docker services but coupled to the Pangolin API. (`pangolin-tunneled-proxy`)
4. **Kamal**: CLI tool with single config file. kamal-proxy is separate but designed as a Kamal component. (`kamal-deploy-overview`)
5. **Coolify**: Monolithic platform. Dashboard-driven. Cannot be used as a library. (`coolify-paas-overview`)

### Cost model

| Tool | Free tier | Paid starts | Notes |
|------|-----------|-------------|-------|
| Cloudflare Tunnel | Unlimited tunnels, 50 users. | $7/user/month (Zero Trust). | Generous free tier covers most solo-operator needs. |
| Tailscale Funnel | Personal plan (1 user, 3 devices). | $6/user/month (Personal Plus). | Bandwidth-limited on free. |
| ngrok | 1 GB/month, 1 endpoint. | $8/month (Personal). | Severely restricted since Feb 2026. |
| Caddy | Unlimited (open source). | N/A. | Apache 2.0 license. Self-hosted. |
| Traefik | Unlimited (open source). | Traefik Hub pricing for management UI. | MIT license. Self-hosted. |
| Nginx | Unlimited (open source). | Nginx Plus ~$2,500/year. | BSD license. Self-hosted. |
| Coolify | Unlimited (open source). | Cloud hosting available. | AGPL-3 license. Self-hosted. |
| Dokku | Unlimited (open source). | Dokku Pro for UI. | MIT license. Self-hosted. |
| Kamal | Unlimited (open source). | N/A. | MIT license. Self-hosted. |
| Pangolin | Community Edition (AGPL-3). | Enterprise + Cloud plans. | Self-hosted or managed. |
| Commodore | N/A (personal project). | N/A. | Experimental. |

### Resource overhead for solo operators

| Tool | Idle RAM | Idle CPU | Notes |
|------|----------|----------|-------|
| Dokku | ~200 MB | <1% | Lightest. CLI only. |
| Dokploy | ~350 MB | ~0.8% | Lightest with UI. |
| CapRover | ~400 MB | ~2-3% | Moderate. |
| Coolify | ~500-700 MB | ~5-6% | Heaviest PaaS. Most features. |
| Kamal (kamal-proxy) | ~50 MB | <1% | Proxy only. Deployment is local CLI. |
| Pangolin (full stack) | ~400-600 MB | ~2-4% | 4+ containers. |
| Cloudflared | ~30 MB | <1% | Single binary tunnel agent. |
| Caddy | ~30 MB | <1% | Single binary proxy. |

## Commodore Assessment

Commodore (`cristoslc/commodore-infra`) covers three of the four layers needed for VISION-006 ingress:

| Layer | Commodore coverage | Adapter |
|-------|-------------------|---------|
| DNS | Covered. | `CloudflareDNS` -- full CRUD via API. |
| Reverse proxy | Covered. | `CaddyAdapter` -- SSH + Caddyfile generation + reload. |
| TLS | Covered (via Caddy). | Caddy handles TLS automatically. |
| Tunnel | **Gap**. | No tunnel port or adapter exists. |
| Container | Covered. | `DockerCompose` -- SSH-based stack management. |

**The single missing piece is a TunnelPort and adapter.** Adding a `CloudflareTunnelAdapter` that wraps the Cloudflare Tunnel API (create tunnel, set ingress rules, manage connectors) would let Commodore provision the full chain -- DNS + tunnel + proxy + container -- in one `cdre apply` call.

### Design patterns from composition tools

The new sources reveal several patterns relevant to Commodore's TunnelPort design:

- **Pangolin's Newt model**: A small user-space WireGuard client that connects outbound to a hub. No root needed. Control messages flow over WebSocket; data flows over WireGuard. This is the best pattern for a self-hosted tunnel adapter. (`pangolin-tunneled-proxy`)
- **Dokku's trigger system**: Fire a trigger, all listeners run. Similar to Commodore's port/adapter pattern but built as loose-coupled scripts, not interface injection. Proves swappable infra components work in practice. (`dokku-architecture-overview`)
- **Kamal's imperative approach**: Rejects Kubernetes' reconciliation loop. Uses explicit commands instead (like Capistrano for containers). Commodore's `cdre apply` sits between -- declarative intent, imperative execution. (`kamal-deploy-overview`)
- **Coolify's Cloudflare Tunnel integration**: Shows how a PaaS can pair with Cloudflare Tunnels for the full chain. The integration is manual -- configure the tunnel separately, point it at Traefik. Not automated. (`coolify-paas-overview`)

### Commodore's unique position

No surveyed tool covers the full DNS + TLS + proxy + tunnel + container chain in one declarative config. The landscape divides into:

- PaaS tools (Coolify, Dokku, Kamal) that handle proxy + TLS + container but not DNS or tunnel.
- Tunnel platforms (Pangolin, Cloudflare Tunnel) that handle tunnel + proxy + TLS but not DNS or container.
- Full Kubernetes stacks that cover everything but are too heavy for a solo operator.

Commodore is the only tool trying to unify DNS + proxy + TLS + container in a composable model. Adding a TunnelPort would make it the only lightweight tool covering all five layers. This is still a real gap in the ecosystem.

## Points of Agreement

- All sources agree Cloudflare Tunnel is the strongest production option for services behind NAT. (`cloudflare-tunnel-setup-docs`, `onidel-funnel-cf-nginx-comparison`, `ngrok-pricing-limits`)
- All sources agree Caddy has the simplest TLS and reverse proxy configuration. (`caddy-automatic-https-docs`, `zeonedge-nginx-caddy-traefik-comparison`)
- All sources agree Nginx wins on raw performance but loses on operational simplicity. (`onidel-funnel-cf-nginx-comparison`, `zeonedge-nginx-caddy-traefik-comparison`)
- All PaaS sources agree that DNS record creation is out of scope -- every platform requires manual DNS setup. (`coolify-paas-overview`, `dokku-architecture-overview`, `kamal-deploy-overview`, `dokploy-paas-comparison`)
- More features means less composability: Dokku (most composable, fewest built-in features) vs. Coolify (least composable, most features). (`dokku-architecture-overview`, `dokploy-paas-comparison`)

## Points of Disagreement

- Traefik vs Caddy for dynamic setups depends on your style. Docker/K8s labels favor Traefik; API-driven config favors Caddy. Neither source credits the other's strength.
- Latency numbers vary. Onidel reports 15-45ms for Cloudflare Tunnel; other sources show lower latency near edge PoPs. Real numbers depend on geography.
- Pangolin vs Cloudflare Tunnel: community favors Pangolin for self-sovereignty. Production sources favor Cloudflare for reliability and DDoS protection. (`pangolin-tunneled-proxy`, `cloudflare-tunnel-setup-docs`)

## Gaps

- No source measures the **automation effort** of composing these tools. How many API calls or config files does it take to go from "expose service X" to "service X is live"?
- Cloudflare Tunnel's **SSE limit on quick tunnels** is in the docs but rarely noted in comparison articles. This matters for VISION-006's chat service use case.
- **Pangolin's performance overhead** from user-space WireGuard vs kernel WireGuard is mentioned but not benchmarked. Matters if Commodore adds a WireGuard-based tunnel adapter.
- No source compares the **API surface area** of these tools. Commodore needs API-driven control, not dashboard-driven config.

## Recommendation for VISION-006

**Cloudflare Tunnel + Caddy** remains the recommended stack, with Commodore as the orchestration layer.

1. **Cloudflare Tunnel** provides the tunnel and public DNS (CNAME to `<tunnel-id>.cfargotunnel.com`).
2. **Caddy** handles reverse proxy, automatic TLS for internal traffic, and dynamic backend registration via API.
3. **Commodore** orchestrates the full chain: DNS record + tunnel ingress rule + Caddy route + container deployment in one `cdre apply`.
4. The missing `TunnelPort` + `CloudflareTunnelAdapter` is the only new code needed in Commodore.

The new sources reinforce this recommendation. No self-hosted PaaS covers the full chain. Commodore does not need to compete with them -- it fills the gap they all leave open. Pangolin's Newt/WireGuard model is worth studying for a future self-hosted tunnel adapter as a Cloudflare alternative.

This stack is all single-binary, low-maintenance, and free-tier-compatible for a solo operator.
