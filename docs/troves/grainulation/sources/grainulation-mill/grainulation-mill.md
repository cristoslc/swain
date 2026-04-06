---
source-id: "grainulation-mill"
title: "Mill — Export Sprint Evidence to 24 Formats"
type: repository
url: "https://github.com/grainulation/mill"
fetched: 2026-04-06T15:00:00Z
hash: "9452e8d4e2ac09846ab8a4bb49b6403cfdf46b33f003adc1be441f3d5a72c799"
highlights:
  - "grainulation-mill.md"
selective: true
notes: "Export engine — 24 formats including PDF, CSV, Obsidian, Jira, JSON-LD; MCP server included"
---

# Mill — Export Sprint Evidence to 24 Formats

**Tagline:** Turn sprint evidence into shareable artifacts.

Mill is the export engine for grainulation sprints. Give it claims.json or HTML output and it produces whatever format your team needs — 24 options including PDF, CSV, slides, Jira, GitHub Issues, Obsidian, and more.

## Install

```bash
npm install -g @grainulation/mill
```

## Quick start

```bash
mill export --format csv claims.json
mill export --format pdf output/brief.html
mill convert --from html --to markdown output/brief.html
mill export --format json-ld claims.json -o claims.jsonld
mill publish --target static output/
mill publish --target clipboard output/brief.html
```

## Export formats (24 built-in)

| Format | Input | Output |
|--------|-------|--------|
| `pdf` | HTML, Markdown | PDF |
| `csv` | claims.json | CSV |
| `markdown` | HTML | Markdown |
| `json-ld` | claims.json | JSON-LD (schema.org) |
| `html-report` | claims.json | Interactive HTML report |
| `slide-deck` | claims.json | Scroll-snap HTML presentation |
| `github-issues` | claims.json | GitHub Issues JSON payloads |
| `jira-csv` | claims.json | Jira-compatible CSV import |
| `yaml` | claims.json | YAML |
| `ndjson` | claims.json | Newline-delimited JSON |
| `dot` | claims.json | Graphviz DOT |
| `graphml` | claims.json | GraphML |
| `bibtex` | claims.json | BibTeX citations |
| `ris` | claims.json | RIS citations |
| `rss` | claims.json | RSS feed |
| `opml` | claims.json | OPML outline |
| `obsidian` | claims.json | Obsidian vault |
| `sql` | claims.json | SQL INSERT statements |
| `typescript-defs` | claims.json | TypeScript type definitions |
| `executive-summary` | claims.json | Executive summary HTML |
| `evidence-matrix` | claims.json | Evidence tier matrix |
| `changelog` | claims.json | Sprint changelog |
| `sankey` | claims.json | Sankey diagram data |
| `treemap` | claims.json | Treemap data |

## Publish targets

| Target | Output |
|--------|--------|
| `static` | Dark-themed static site in `_site/` |
| `clipboard` | System clipboard (pbcopy/xclip/clip) |

## CLI

```
mill export    --format <fmt> <file>              Export to target format
mill convert   --from <fmt> --to <fmt> <file>     Convert between formats
mill publish   --target <dest> <dir>              Publish sprint outputs
mill formats                                      List available formats
mill serve     [--port 9094] [--source <dir>]     Start the export workbench UI
mill serve-mcp                                    Start the MCP server on stdio
```

All commands accept `-o <path>` to set the output location.

## Standalone use

Mill reads sprint output files directly. It does not require wheat — give it HTML, Markdown, or claims JSON and it produces shareable formats.

## Zero dependencies

Node built-in modules only. Heavy operations (PDF) run via `npx` on demand.

## License

MIT
