# Paywall Proxy Fallback for swain-search

## Summary

Update swain-search to automatically detect paywalled web content and try proxy services (starting with Freedium for Medium) before falling back to truncated content. Uses a try-then-fallback strategy with deterministic domain matching via a shell script.

## Context

swain-search collects web sources into troves. When a source URL points to a paywalled article (e.g., Medium member-only), the current behavior falls back to search snippets, producing incomplete source content. We manually confirmed that Freedium (`freedium.cfd`) can retrieve full Medium articles. This enhancement automates that fallback.

## Design Decisions

1. **Try-then-fallback** (not pre-routing) — always try the direct URL first, then detect truncation, then try proxies. Respects the original source and handles free articles correctly.
2. **YAML registry** — `paywall-proxies.yaml` with a many-to-many structure: multiple proxies per domain, multiple domains per proxy. Extensible without touching skill logic.
3. **Deterministic matching** — a shell script (`resolve-proxy.sh`) handles domain matching and proxy URL construction. No LLM tokens spent on mechanical routing.
4. **Manifest provenance** — `proxy-used` field records which proxy delivered the content; `url` always stays the original canonical URL.

## Deliverables

### 1. `skills/swain-search/references/paywall-proxies.yaml`

```yaml
# Paywall proxy registry — many-to-many mapping of domains to proxy strategies.
# Proxies are tried in list order per domain until one returns full content.

domains:
  - pattern: "medium.com"
    match: host-or-subdomain  # matches medium.com and *.medium.com
    proxies: [freedium]
    truncation-signals:
      - "Member-only story"
      - "You have 2 free member-only stories left"
      - "Sign up to discover human stories"

proxies:
  freedium:
    url-template: "https://freedium.cfd/{url}"
    notes: "Mirrors Medium member-only articles. May be intermittent."
```

### 2. `skills/swain-search/scripts/resolve-proxy.sh`

Takes a URL as input. Parses `paywall-proxies.yaml` to find matching domain entries. Outputs proxy URLs and truncation signals in line-oriented format:

```
PROXY:freedium:https://freedium.cfd/https://medium.com/some-article
SIGNAL:Member-only story
SIGNAL:You have 2 free member-only stories left
SIGNAL:Sign up to discover human stories
```

Exit 0 with output = proxies available. Exit 1 = no domain match.

### 3. SKILL.md edits

- New "Paywall proxy fallback" section after "Web page URLs" in Step 2
- Updated "Graceful degradation" table with paywall proxy row
- Flow: fetch page → run `resolve-proxy.sh <url>` → if exit 0, grep for signals → if found, try proxy URLs in order → normalize whichever succeeds

### 4. Manifest schema update

Optional `proxy-used` field on source entries:

```yaml
- source-id: example
  type: web
  url: "https://medium.com/..."
  proxy-used: freedium
  notes: "Full article retrieved via freedium proxy"
```
