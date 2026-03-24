---
source-id: "likec4-mcp-server"
title: "LikeC4 MCP Server Documentation"
type: documentation-site
url: "https://likec4.dev/tooling/mcp/"
fetched: 2026-03-23T00:00:00Z
hash: "--"
---

# LikeC4 MCP Server

## Overview

Integrates your architecture model with large language models, enabling natural language queries of your system design.

## Setup Options

### VSCode Extension (Built-in)

Enable via `likec4.mcp.enabled` setting. Configure `.vscode/mcp.json`:

```json
{
  "servers": {
    "likec4": {
      "type": "sse",
      "url": "http://localhost:33335/mcp"
    }
  }
}
```

### NPM Package

```json
{
  "mcpServers": {
    "likec4": {
      "command": "npx",
      "args": ["-y", "@likec4/mcp"],
      "env": {
        "LIKEC4_WORKSPACE": "${workspaceFolder}"
      }
    }
  }
}
```

### CLI

```bash
likec4 mcp --stdio          # stdio transport
likec4 mcp --http           # HTTP (port 33335)
likec4 mcp -p 1234          # custom port
likec4-mcp-server --no-watch  # reduce resource use
```

## Available Tools

| Tool | Purpose |
|------|---------|
| `list-projects` | Enumerate all LikeC4 projects |
| `read-project-summary` | Specs, configs, elements, deployments, views |
| `search-element` | Query by ID, title, kind, shape, tags, metadata |
| `read-element` | Full element details with relationships |
| `read-deployment` | Deployment node or instance information |
| `read-view` | Complete view structure and source location |
| `find-relationships` | Direct/indirect connection discovery |
| `query-graph` | Element hierarchy and single-hop relationships |
| `query-incomers-graph` | Upstream dependency mapping (recursive BFS) |
| `query-outgoers-graph` | Downstream consumer identification (recursive BFS) |
| `query-by-metadata` | Search with exact/contains/exists matching |
| `query-by-tags` | Boolean tag filtering (allOf, anyOf, noneOf) |
| `query-by-tag-pattern` | Pattern-based tag searching |
| `find-relationship-paths` | Multi-hop relationship chain discovery |
| `batch-read-elements` | Bulk element retrieval |
| `subgraph-summary` | Descendant analysis with depth metrics |
| `element-diff` | Property and relationship comparison |
| `open-view` | Launch view panel (editor only) |
