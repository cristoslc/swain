---
source-id: "stitch-mcp-cli"
title: "davideast/stitch-mcp — CLI for Stitch Design-to-Dev Workflow"
type: web
url: "https://github.com/davideast/stitch-mcp"
fetched: 2026-03-21T00:00:00Z
hash: "c7f9f5c2dc8346954a007218b74ec2b55b6d68b333586c8be6989c0ef283c344"
---

# stitch-mcp

A CLI for moving AI-generated UI designs into your development workflow — preview them locally, build sites from them, and feed them to coding agents.

**Repository:** davideast/stitch-mcp (495 stars, 56 forks)
**Package:** `@_davideast/stitch-mcp` on npm
**License:** Apache 2.0
**Note:** Independent/experimental — NOT affiliated with or endorsed by Google.

## Why

AI-generated designs in Google's Stitch platform live as HTML/CSS behind an API. Getting them into a local development environment — for previewing, building, or handing off to coding agents — requires fetching, serving, and structuring them. stitch-mcp handles this through a set of CLI commands that connect to Stitch.

## Quick Start

```bash
# Set up authentication and MCP client config
npx @_davideast/stitch-mcp init

# Serve all project screens on a local dev server
npx @_davideast/stitch-mcp serve -p <project-id>

# Build an Astro site by mapping screens to routes
npx @_davideast/stitch-mcp site -p <project-id>
```

## Features

- **Preview designs locally** — serve all screens from a project on a Vite dev server
- **Build an Astro site from your designs** — map screens to routes and generate a deployable project
- **Give your agent design context** — proxy Stitch tools to your IDE's coding agent with automatic token refresh
- **Explore your design data** — browse projects, screens, and metadata in the terminal or via CLI
- **Browse projects in your terminal** — navigate screens interactively with copy, preview, and open actions
- **Set up in one command** — guided wizard handles gcloud, auth, and MCP client configuration

## MCP Integration

Add this to your MCP client config to give coding agents access to Stitch tools:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["@_davideast/stitch-mcp", "proxy"]
    }
  }
}
```

**Supported clients:** VS Code, Cursor, Claude Code, Gemini CLI, Codex, OpenCode.

## Virtual Tools

The proxy exposes these tools alongside the upstream Stitch MCP tools. They combine multiple API calls into higher-level operations for coding agents:

- **build_site** — Builds a site from a project by mapping screens to routes. Returns the design HTML for each page.
- **get_screen_code** — Retrieves a screen and downloads its HTML code content.
- **get_screen_image** — Retrieves a screen and downloads its screenshot image as base64.

### build_site input schema

```json
{
  "projectId": "string (required)",
  "routes": [
    { "screenId": "string (required)", "route": "string (required, e.g. \"/\" or \"/about\")" }
  ]
}
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Set up auth, gcloud, and MCP client config |
| `doctor` | Verify configuration health |
| `logout` | Revoke credentials |
| `serve -p <id>` | Preview project screens locally |
| `screens -p <id>` | Browse screens in terminal |
| `view` | Interactive resource browser |
| `site -p <id>` | Generate Astro project from screens |
| `snapshot` | Save screen state to file |
| `tool [name]` | Invoke MCP tools from CLI |
| `proxy` | Run MCP proxy for agents |

## Authentication

- **Automatic (recommended):** Run `init` and follow the wizard. Handles gcloud installation, OAuth, credentials, and project setup.
- **API key:** Set `STITCH_API_KEY` environment variable to skip OAuth entirely.
- **Manual (existing gcloud):** Use `gcloud auth application-default login` then `proxy` with `STITCH_USE_SYSTEM_GCLOUD=1`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `STITCH_API_KEY` | API key for direct authentication (skips OAuth) |
| `STITCH_ACCESS_TOKEN` | Pre-existing access token |
| `STITCH_USE_SYSTEM_GCLOUD` | Use system gcloud config instead of isolated config |
| `STITCH_PROJECT_ID` | Override project ID |
| `GOOGLE_CLOUD_PROJECT` | Alternative project ID variable |
| `STITCH_HOST` | Custom Stitch API endpoint |
