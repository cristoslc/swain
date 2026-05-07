---
source-id: omo-slim-package
title: oh-my-opencode-slim — package.json
url: https://github.com/alvinunreal/oh-my-opencode-slim/blob/master/package.json
fetched: 2026-05-05
type: repository
version: 1.0.6
---

# Project Manifest

- **Name:** oh-my-opencode-slim
- **Version:** 1.0.6
- **Type:** ES module
- **License:** MIT
- **Entry:** `dist/index.js` (types: `dist/index.d.ts`)
- **CLI bin:** `oh-my-opencode-slim` → `dist/cli/index.js`
- **TUI export:** `dist/tui.js`

## Keywords

opencode, opencode-plugin, ai, agents, orchestration, llm, claude, gpt, gemini

## Published Files

`dist/`, `src/skills/`, `oh-my-opencode-slim.schema.json`, `README.md`, `LICENSE`

## Core Dependencies

- `@ast-grep/cli` ^0.42.1
- `@modelcontextprotocol/sdk` ^1.29.0
- `@mozilla/readability` ^0.6.0
- `@opencode-ai/plugin` ^1.3.17
- `@opencode-ai/sdk` ^1.3.17
- `jsdom` ^26.1.0
- `lru-cache` ^11.3.3
- `turndown` ^7.2.4

## Dev Dependencies

- `@biomejs/biome` 2.4.11
- `bun-types` 1.3.12
- `typescript` ^5.9.3
- `zod` ^4.3.6 (peer)

## Scripts

| Script | Purpose |
|--------|---------|
| `build:plugin` | Bundle `src/index.ts` + `src/tui.ts` → `dist/` |
| `build:cli` | Bundle `src/cli/index.ts` → `dist/cli/` |
| `build` | Full build pipeline |
| `typecheck` | `tsc --noEmit` |
| `test` | `bun test` |
| `check:ci` | Biome CI check |
| `dev` | Build + run OpenCode |
| `generate-schema` | Generate JSON schema from Zod |
| `release:patch/minor/major` | Version bump + git push + npm publish |
