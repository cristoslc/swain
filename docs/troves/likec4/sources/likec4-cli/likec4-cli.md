---
source-id: "likec4-cli"
title: "LikeC4 CLI Documentation"
type: documentation-site
url: "https://likec4.dev/tooling/cli/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 CLI Documentation

## Installation

```bash
npm i -D likec4     # local
npm install --global likec4  # global
npx likec4 start    # via npx
```

## Commands

### Preview/Development Server

```bash
likec4 serve   # or: likec4 start, likec4 dev
```

Recursively searches for `*.c4` and `*.likec4` files. By default listens on localhost; use `--listen 0.0.0.0` to expose.

### Build Static Website

```bash
likec4 build -o ./dist
```

Options: `--output`, `--base-url`, `--use-hash-history`, `--use-dot`, `--webcomponent-prefix`, `--title`, `--output-single-file`.

### Export to PNG

```bash
likec4 export png -o ./assets
```

Uses Playwright for screenshots. Options: `--theme` (light/dark), `--filter`, `--timeout`, `--max-attempts`.

### Export to JSON

```bash
likec4 export json -o dump.json
```

### Export to DrawIO

```bash
likec4 export drawio -o ./diagrams
```

Options: `--all-in-one`, `--roundtrip`, `--uncompressed`, `--profile` (default/leanix).

### Generate Diagram Formats

```bash
likec4 gen mmd       # Mermaid
likec4 gen dot       # Graphviz DOT
likec4 gen d2        # D2
likec4 gen plantuml  # PlantUML
```

### Validate

```bash
likec4 validate
```

Identifies syntax errors and layout drift. Non-zero exit code on errors.

### Format

```bash
likec4 format              # format workspace
likec4 format --check      # CI mode (no changes)
```

### Language Server (LSP)

```bash
likec4 lsp --stdio
likec4 lsp --socket 3000
```

Transports: `--stdio`, `--node-ipc`, `--socket`, `--pipe`.

### MCP Server

```bash
likec4 mcp           # stdio (default)
likec4 mcp --http    # HTTP transport (port 33335)
```
