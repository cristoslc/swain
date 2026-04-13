---
source-id: "grainulation-barn"
title: "Barn — Shared Tools for the Grainulation Ecosystem"
type: repository
url: "https://github.com/grainulation/barn"
fetched: 2026-04-06T15:00:00Z
hash: "1979f3a5471cc53107ac8a503d6ecd6f951d17ee89cb53f3299c38f6947ddd88"
highlights:
  - "grainulation-barn.md"
selective: true
notes: "Shared utility library — 17 HTML templates, sprint detection, manifest generation, PDF builder"
---

# Barn — Shared Tools for the Grainulation Ecosystem

**Tagline:** Shared tools for the grainulation ecosystem.

Barn extracts the reusable utilities from wheat into a standalone package: sprint detection, manifest generation, PDF builds, and 17 dark-themed HTML templates for research artifacts.

## Install

```bash
npm install @grainulation/barn
```

## Tools

### detect-sprints

Find sprint directories in a repo by scanning for `claims.json` files. Uses git history to determine which sprint is active.

```bash
barn detect-sprints              # Human-readable output
barn detect-sprints --json       # Machine-readable JSON
barn detect-sprints --active     # Print only the active sprint path
barn detect-sprints --root /path # Scan a specific directory
```

### generate-manifest

Build a `wheat-manifest.json` topic map from claims, files, and git history. Gives AI tools a single file that describes the entire sprint state.

```bash
barn generate-manifest
barn generate-manifest --root /path
barn generate-manifest --out custom-name.json
```

### build-pdf

Convert markdown to PDF via `md-to-pdf` (invoked through npx — no local install needed).

```bash
barn build-pdf output/brief.md
```

## Templates (17 total)

Self-contained HTML templates. Dark theme, inline CSS/JS, no external deps, mobile responsive.

| Template | Purpose |
|----------|---------|
| `adr.html` | Architecture Decision Record |
| `brief.html` | Sprint brief / recommendation document |
| `certificate.html` | Compilation certificate |
| `changelog.html` | Sprint changelog |
| `comparison.html` | Side-by-side comparison dashboard |
| `conflict-map.html` | Claim conflict visualization |
| `dashboard.html` | Sprint status dashboard |
| `email-digest.html` | Email digest summary |
| `evidence-matrix.html` | Evidence tier matrix |
| `explainer.html` | Full-screen scroll-snap presentation |
| `handoff.html` | Knowledge transfer document |
| `one-pager.html` | Single-page executive summary |
| `postmortem.html` | Sprint postmortem |
| `rfc.html` | Request for Comments |
| `risk-register.html` | Risk tracking register |
| `slide-deck.html` | Slide deck presentation |
| `wiki-page.html` | Wiki-style documentation page |

```bash
cp node_modules/@grainulation/barn/templates/explainer.html ./output/
```

## Zero dependencies

Node built-in modules only.

## License

MIT
