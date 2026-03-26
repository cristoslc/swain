---
source-id: "likec4-repo"
title: "LikeC4 — Architecture as Code (GitHub Repository)"
type: repository
url: "https://github.com/likec4/likec4"
fetched: 2026-03-23T00:00:00Z
hash: "--"
selective: true
highlights:
  - "likec4-repo.md"
---

# LikeC4 — Architecture as Code

**Repository:** https://github.com/likec4/likec4
**Stars:** ~2,936 | **License:** MIT | **Language:** TypeScript
**Homepage:** https://likec4.dev
**Topics:** architecture, architecture-as-code, c4, diagrams

## Description

Visualize, collaborate, and evolve the software architecture with always actual and live diagrams from your code.

LikeC4 is a modeling language for documenting software architecture and generating visual diagrams from those specifications. It draws inspiration from both the C4 Model and Structurizr DSL while offering greater adaptability. Teams can establish personalized notation systems, define custom element types, and create multiple nested architectural levels.

## Project Structure (Monorepo)

Managed by `pnpm` workspaces and `turbo`.

### Apps
- `apps/docs` — Documentation site (likec4.dev)
- `apps/playground` — Online playground (playground.likec4.dev)

### Packages
- `packages/likec4/` — CLI, Vite plugin, static site generator (main entry point)
- `packages/core/` — Core and model types, model builder, compute-view, layout drift detection
- `packages/language-server/` — Langium-based DSL parser and LSP implementation
- `packages/language-services/` — Language services initialization (browser and Node.js compatible)
- `packages/diagram/` — React/ReactFlow diagram renderer
- `packages/layouts/` — Graphviz-based layout algorithms
- `packages/generators/` — Export to Mermaid, PlantUML, D2, etc.
- `packages/vscode/` — VSCode extension
- `packages/vscode-preview/` — Preview panel component for VSCode
- `packages/config/` — Configuration schema and validation
- `packages/icons/` — Icon bundle (script-generated, do not edit)
- `packages/log/` — Shared logging utilities
- `packages/mcp/` — MCP Server as separate package
- `packages/tsconfig/` — Shared TypeScript configuration
- `packages/create-likec4/` — Not used for now
- `packages/react/` — React component library
- `packages/leanix-bridge/` — LeanIX integration

### Other
- `e2e/` — Playwright end-to-end tests (isolated workspace)
- `styled-system/preset` — PandaCSS preset
- `styled-system/styles` — `pandacss codegen` results, shared across packages
- `examples/` — Sample LikeC4 projects
- `devops/` — CI/CD utilities

## Technology Stack
- TypeScript-first repo
- Langium for DSL parsing and language server
- React + ReactFlow for diagram rendering
- Graphviz (WASM or binary) for layout
- Vite for build tooling
- PandaCSS for styling
- Vitest for testing
- dprint for formatting (120-column lines, single quotes, no semicolons)
- oxlint for linting

## Key Features
- Custom DSL (`.c4` / `.likec4` files) for architecture modeling
- Hierarchical element modeling with custom kinds
- Multiple view types: static, dynamic (sequence), deployment
- Predicate-based view generation (include/exclude/where)
- VSCode extension with live preview
- CLI for dev server, static site build, PNG/JSON/DrawIO export
- MCP server for LLM integration
- React components for embedding diagrams
- Export to Mermaid, PlantUML, D2, Graphviz DOT
- Model Builder API for programmatic model construction
- Model API for querying and traversal
