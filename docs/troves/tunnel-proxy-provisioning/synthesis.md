# Tunnel-Proxy-Provisioning Synthesis

Research question: Can DNS + TLS + reverse proxy + tunnel be provisioned as a single automated operation, and which tools compose well for VISION-006 ingress?

## Key Findings

### Single-operation provisioning is achievable today with two tool combinations

**Cloudflare Tunnel + Cloudflare DNS** comes closest to a single-operation stack. One script can create a tunnel, add an ingress rule, and create a CNAME record -- all through the Cloudflare API. TLS terminates at Cloudflare's edge with no setup. No inbound ports are needed. One provider owns the entire DNS + TLS + tunnel + routing chain. (`cloudflare-tunnel-setup-docs`)

**Caddy + DNS provider API** covers the reverse proxy + TLS layer in one step. Caddy issues certificates the moment a domain appears in config. Its REST API (`localhost:2019`) lets you add backends without restarts. Adding a new service takes two calls: (1) create a DNS record, (2) POST a route to Caddy. TLS just works. (`caddy-automatic-https-docs`)

### Composability tiers

**Tier 1 -- Full-stack tunnel services** (tunnel + DNS + TLS in one product):
- Cloudflare Tunnel: best overall for production. Free tier is generous. DDoS protection included. API for full automation. (`cloudflare-tunnel-setup-docs`, `onidel-funnel-cf-nginx-comparison`)
- Tailscale Funnel: easiest setup but limited -- no custom domains, restricted ports (443/8443/10000), bandwidth caps, beta status. Best for dev/personal. (`tailscale-funnel-docs`)
- ngrok: severely restricted free tier since Feb 2026 (1 GB/month, 1 endpoint, interstitial page). No UDP. Best for webhook debugging, not production. (`ngrok-pricing-limits`)

**Tier 2 -- Reverse proxy with automatic TLS** (need separate tunnel/DNS):
- Caddy: simplest config, automatic TLS, REST API for dynamic backends, single binary. Best for small-to-medium deployments. (`caddy-automatic-https-docs`, `zeonedge-nginx-caddy-traefik-comparison`)
- Traefik: automatic service discovery from Docker/K8s labels. Best for container-heavy environments with frequent deploys. Higher resource usage. (`zeonedge-nginx-caddy-traefik-comparison`)
- Nginx + Certbot: most performant, most complex to configure. No dynamic backend API without Nginx Plus (commercial). (`onidel-funnel-cf-nginx-comparison`)

**Tier 3 -- Not a match**:
- Mutagen: file sync and port forwarding for development. Not a tunnel/proxy/DNS tool. (`mutagen-overview`)

### Dynamic backend registration

Three tools support runtime backend registration without restarts:
1. **Caddy**: REST API at `localhost:2019` -- POST routes, on-demand TLS for unknown domains. (`caddy-automatic-https-docs`)
2. **Traefik**: Docker/K8s labels trigger automatic route creation. No config files to edit. (`zeonedge-nginx-caddy-traefik-comparison`)
3. **Cloudflare Tunnel**: API-driven ingress rule updates. (`cloudflare-tunnel-setup-docs`)

Nginx requires a config file edit + reload (or commercial Nginx Plus for API).

### Cost model

| Tool | Free tier | Paid starts | Notes |
|------|-----------|-------------|-------|
| Cloudflare Tunnel | Unlimited tunnels, 50 users. | $7/user/month (Zero Trust). | Generous free tier covers most solo-operator needs. |
| Tailscale Funnel | Personal plan (1 user, 3 devices). | $6/user/month (Personal Plus). | Bandwidth-limited on free. |
| ngrok | 1 GB/month, 1 endpoint. | $8/month (Personal). | Severely restricted since Feb 2026. |
| Caddy | Unlimited (open source). | N/A. | Apache 2.0 license. Self-hosted. |
| Traefik | Unlimited (open source). | Traefik Hub pricing for management UI. | MIT license. Self-hosted. |
| Nginx | Unlimited (open source). | Nginx Plus ~$2,500/year. | BSD license. Self-hosted. |
| Commodore | N/A (personal project). | N/A. | Experimental. |

### Single-binary / low-maintenance tools

- **Cloudflare Tunnel**: `cloudflared` is a single binary. Set as system service and forget.
- **Caddy**: single Go binary, zero-config TLS, auto-renewal.
- **Tailscale**: single binary, auto-updates.
- **ngrok**: single binary, but limited free tier makes it impractical long-term.
- **Traefik**: single binary, but needs Docker/K8s environment for service discovery value.

## Commodore Assessment

Commodore (`cristoslc/commodore-infra`) already covers three of the four layers needed for VISION-006 ingress:

| Layer | Commodore coverage | Adapter |
|-------|-------------------|---------|
| DNS | Covered. | `CloudflareDNS` -- full CRUD via API. |
| Reverse proxy | Covered. | `CaddyAdapter` -- SSH + Caddyfile generation + reload. |
| TLS | Covered (via Caddy). | Caddy handles TLS automatically. |
| Tunnel | **Gap**. | No tunnel port or adapter exists. |
| Container | Covered. | `DockerCompose` -- SSH-based stack management. |

**The single missing piece is a TunnelPort and adapter.** Adding a `CloudflareTunnelAdapter` that wraps the Cloudflare Tunnel API (create tunnel, set ingress rules, manage connectors) would let Commodore provision the full chain -- DNS + tunnel + proxy + container -- in one `cdre apply` call.

Other gaps (HAProxy LB, secrets, infrastructure adapters) are `.gitkeep` placeholders but are not blockers for the ingress use case.

## Points of Agreement

- All sources agree Cloudflare Tunnel is the strongest production option for services behind NAT. (`cloudflare-tunnel-setup-docs`, `onidel-funnel-cf-nginx-comparison`, `ngrok-pricing-limits`)
- All sources agree Caddy has the simplest TLS and reverse proxy configuration. (`caddy-automatic-https-docs`, `zeonedge-nginx-caddy-traefik-comparison`)
- All sources agree Nginx wins on raw performance but loses on operational simplicity. (`onidel-funnel-cf-nginx-comparison`, `zeonedge-nginx-caddy-traefik-comparison`)

## Points of Disagreement

- Traefik vs Caddy for dynamic setups depends on your style. Docker/K8s labels favor Traefik; API-driven config favors Caddy. Neither source credits the other's strength.
- Latency numbers vary. Onidel reports 15-45ms for Cloudflare Tunnel; other sources show lower latency near edge PoPs. Real numbers depend on geography.

## Gaps

- No source measures the **automation effort** of composing these tools -- how many API calls or config files does it take to go from "expose service X" to "service X is live at domain.example.com."
- No source looks at **Commodore-like composition** tools that unify DNS + proxy + tunnel in one model. The closest match is Kubernetes + Traefik + cert-manager + external-dns, but that stack is too heavy for a solo operator.
- Cloudflare Tunnel's **SSE limit on quick tunnels** is in the docs but rarely noted in comparison articles. This matters for VISION-006's chat service use case.

## Recommendation for VISION-006

**Cloudflare Tunnel + Caddy** is the recommended stack, with Commodore as the orchestration layer.

1. **Cloudflare Tunnel** provides the tunnel and public DNS (CNAME to `<tunnel-id>.cfargotunnel.com`).
2. **Caddy** handles reverse proxy, automatic TLS for internal traffic, and dynamic backend registration via API.
3. **Commodore** orchestrates the full chain: DNS record + tunnel ingress rule + Caddy route + container deployment in one `cdre apply`.
4. The missing `TunnelPort` + `CloudflareTunnelAdapter` is the only new code needed in Commodore.

This stack is all single-binary, low-maintenance, and free-tier-compatible for a solo operator.
