---
title: "Paywall Proxy Fallback for swain-search"
artifact: SPEC-155
track: implementable
status: Active
author: cristos
created: 2026-03-22
last-updated: 2026-03-22
priority-weight: ""
type: enhancement
parent-epic: ""
parent-initiative: ""
linked-artifacts: []
depends-on-artifacts: []
addresses: []
evidence-pool: ""
source-issue: ""
swain-do: required
---

# Paywall Proxy Fallback for swain-search

## Problem Statement

swain-search produces incomplete source content when fetching paywalled articles (e.g., Medium member-only). The agent falls back to search snippets, losing article structure, full argumentation, and references. This was confirmed when the Yi Zhou "Agentic Engineering" article in the `agent-alignment-monitoring` trove had to be manually re-fetched via Freedium to get the full text.

## Desired Outcomes

Operators get complete source content in troves without manual intervention. The agent automatically detects paywalled content and tries proxy services before degrading gracefully. Adding support for new proxy services or new paywalled domains requires editing a YAML file, not the skill logic.

## External Behavior

**Inputs:**
- A web URL provided to swain-search for collection

**Preconditions:**
- `skills/swain-search/references/paywall-proxies.yaml` exists with at least one domain/proxy mapping
- `skills/swain-search/scripts/resolve-proxy.sh` is executable

**Flow:**
1. Agent fetches the web page directly (existing behavior, unchanged)
2. Agent runs `resolve-proxy.sh <url>`
   - Exit 1: no proxy configured for this domain — use direct fetch as-is
   - Exit 0: outputs `PROXY:<name>:<proxy-url>` and `SIGNAL:<text>` lines
3. Agent greps the fetched content for each `SIGNAL` string
4. If any signal matches (or article body is under ~200 words):
   - Try each `PROXY` URL in order, fetching and normalizing the result
   - First proxy that returns substantive content wins
5. If all proxies fail: keep the original content, note in manifest

**Outputs:**
- Normalized source markdown (full content when proxy succeeds, truncated when not)
- Manifest entry with optional `proxy-used: <name>` field
- Notes field indicating provenance ("Full article retrieved via <name> proxy" or "Paywalled; proxies exhausted")

**Constraints:**
- `url` in manifest always stores the original canonical URL, never the proxy URL
- Domain matching and proxy URL construction are deterministic (shell script), not LLM-driven
- Proxy failures are non-fatal — graceful degradation to truncated content

## Acceptance Criteria

**AC1: Proxy registry structure**
- Given `paywall-proxies.yaml` exists with a `domains` list and a `proxies` map
- When a domain entry maps to multiple proxies
- Then each proxy has a `url-template` with `{url}` placeholder, and the domain entry's `proxies` list defines try-order

**AC2: Domain matching script**
- Given a Medium URL (e.g., `https://medium.com/pub/article-slug`)
- When `resolve-proxy.sh` is called with that URL
- Then it exits 0 and outputs one `PROXY:<name>:<proxy-url>` line per configured proxy (in priority order) and one `SIGNAL:<text>` line per truncation signal for that domain

**AC3: No-match passthrough**
- Given a URL for a domain not in `paywall-proxies.yaml` (e.g., `https://example.com/page`)
- When `resolve-proxy.sh` is called with that URL
- Then it exits 1 with no output

**AC4: Subdomain matching**
- Given a URL like `https://engineering.medium.com/some-article`
- When `resolve-proxy.sh` is called
- Then it matches the `medium.com` domain entry (host-or-subdomain matching)

**AC5: Skill file instructs proxy fallback**
- Given SKILL.md's "Web page URLs" section
- When an agent follows the updated instructions
- Then after fetching a page, it runs `resolve-proxy.sh`, checks for truncation signals, and tries proxy URLs before degrading gracefully

**AC6: Graceful degradation on proxy failure**
- Given all configured proxies fail for a paywalled URL
- When the agent follows the skill instructions
- Then it keeps the original truncated content and sets `notes: "Paywalled; proxies exhausted — content from direct fetch only"` in the manifest entry

**AC7: Manifest provenance**
- Given a proxy successfully retrieves full content
- When the manifest entry is written
- Then `url` contains the original URL, `proxy-used` contains the proxy name, and `notes` describes the proxy used

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|

## Scope & Constraints

**In scope:**
- `paywall-proxies.yaml` registry file
- `resolve-proxy.sh` script
- SKILL.md updates (new section + graceful degradation table)
- Manifest schema update (optional `proxy-used` field)

**Out of scope:**
- Browser-based proxy navigation (Playwright/puppeteer automation)
- Caching proxy responses
- Proxy health monitoring or automatic failover across sessions
- Adding proxies beyond Freedium (future work — the registry supports it)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-22 | -- | Initial creation; design validated via brainstorming |
