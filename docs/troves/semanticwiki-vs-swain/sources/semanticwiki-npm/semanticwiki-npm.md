---
source-id: "semanticwiki-npm"
title: "SemanticWiki - npm package README"
type: web
url: "https://www.npmjs.com/package/semanticwiki"
fetched: 2026-04-16T18:15:00Z
hash: ""
notes: "npmjs.com blocked by Cloudflare; content sourced from npm registry API (registry.npmjs.org/semanticwiki)"
---

# SemanticWiki

SemanticWiki is the intellectual property of [reasoning.software](https://reasoning.software) (MadWatch LLC). Created by Dakota Kim.

> Generate architectural documentation wikis with source code traceability

An AI-powered CLI that does two things:

1. **Generates architectural wikis** with source code traceability (`file:line` references)
2. **Works as an agentic coding assistant** like Claude Code

Built with [buildanagentworkshop.com](https://buildanagentworkshop.com)

## Two Ways to Use SemanticWiki

### 1. Generate Documentation (`semanticwiki generate`)

Point SemanticWiki at any codebase and get a complete architectural wiki:

```bash
semanticwiki generate -r ./my-project --site
```

This creates:

- **Architecture Overview** with Mermaid diagrams
- **Module Documentation** with source traceability
- **Data Flow Documentation**
- **Getting Started Guides**
- **Interactive static site** with search, keyboard nav, dark mode

Every concept links directly to source code (`src/auth/jwt.ts:23-67`), so you can navigate from docs to implementation.

### 2. Agentic Codebase Assistant

Under the hood, SemanticWiki is a full agentic coding assistant powered by Claude. It doesn't just template docs — it:

- **Explores your codebase** using filesystem tools
- **Searches semantically** via RAG embeddings (FAISS + all-MiniLM-L6-v2)
- **Reasons about architecture** to identify patterns and relationships
- **Writes and verifies** documentation with automatic link checking

```bash
semanticwiki generate -r ./my-project --verbose
semanticwiki continue -r ./my-project --skip-index
```

The same RAG system that powers documentation generation gives the agent deep, semantic understanding of your codebase — like Claude Code, but with your entire project pre-indexed for instant retrieval.

## Installation

```bash
npm install -g semanticwiki
```

## Prerequisites

- **Node.js** >= 18.0.0
- **Anthropic API key** — Get one at console.anthropic.com

## Quick Start

### 1. Set your API key

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

### 2. Generate wiki + interactive site

```bash
semanticwiki generate -r ./my-project --site
```

### 3. View the results

- **Markdown wiki**: Open `wiki/README.md`
- **Interactive site**: Open `wiki/site/index.html` in your browser

The static site includes search, navigation, keyboard shortcuts, and works offline.

## Usage

### Generate Command

```bash
semanticwiki generate -r .
semanticwiki generate -r ./my-project --site
semanticwiki generate -r ./my-project --site --site-title "My Project Docs" --theme dark
semanticwiki generate -r ./my-project -o ./docs/architecture
semanticwiki generate -r ./my-project -p src/core
semanticwiki generate -r ./my-project -v
semanticwiki generate -r ./my-project -e
```

### Continue Command

Resume generation to fix broken links or add missing pages:

```bash
semanticwiki continue -r ./my-project -o ./wiki
semanticwiki continue -r ./my-project -o ./wiki --verify-only
semanticwiki continue -r ./my-project -o ./wiki --skip-index
```

### Search Command

Search your wiki from the command line:

```bash
semanticwiki search "authentication flow" -w ./wiki
semanticwiki search "how does login work" -w ./wiki --hybrid
```

### MCP Server

Start an MCP server for AI assistant integration (Claude Desktop, Claude Code):

```bash
semanticwiki mcp-server -w ./wiki
semanticwiki mcp-server -w ./wiki -r ./my-project
```

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "my-wiki": {
      "command": "semanticwiki",
      "args": ["mcp-server", "-w", "/path/to/wiki"]
    }
  }
}
```

### Pack & Unpack

Create portable wiki packages for sharing:

```bash
semanticwiki pack -w ./wiki -o ./my-wiki.archiwiki
semanticwiki unpack -p ./my-wiki.archiwiki -o ./extracted
semanticwiki unpack -p ./my-wiki.archiwiki -o ./extracted --wiki-only
```

### Large Codebase Options

For repositories with 10,000+ files:

```bash
semanticwiki generate -r ./large-project --max-chunks 5000
semanticwiki generate -r ./large-project --max-results 5
semanticwiki generate -r ./large-project --batch-size 3000
```

### Direct API Mode

Bypass Claude Code billing and use your API credits directly:

```bash
semanticwiki generate -r ./my-project --direct-api
semanticwiki generate -r ./my-project --direct-api --skip-index
```

### Debug & Development

```bash
semanticwiki generate -r ./my-project --skip-index
semanticwiki generate -r ./my-project --max-turns 50
```

## Command Reference

### `generate` - Create wiki documentation

| Option | Description | Default |
|--------|-------------|---------|
| `-r, --repo <path/url>` | Repository path or GitHub URL (required) | - |
| `-o, --output <dir>` | Output directory for wiki | `./wiki` |
| `-c, --config <file>` | Path to wiki.json config file | - |
| `-t, --token <token>` | GitHub token for private repos | - |
| `-m, --model <model>` | Claude model to use | `claude-sonnet-4-20250514` |
| `-p, --path <path>` | Focus on specific directory | - |
| `-f, --force` | Force regeneration (ignore cache) | - |
| `-v, --verbose` | Show detailed progress | - |
| `-e, --estimate` | Estimate time/cost (dry run) | - |
| `-s, --site` | Generate interactive static site | - |
| `--ai-chat` | Add AI chat assistant to site | - |
| `--site-only` | Generate site only (skip wiki) | - |
| `--site-title <title>` | Custom site title | Project name |
| `--theme <theme>` | Site theme: `light`, `dark`, `auto` | `auto` |
| `--max-chunks <n>` | Limit indexed chunks | unlimited |
| `--max-results <n>` | Max search results per query | `10` |
| `--batch-size <n>` | Enable batched processing | - |
| `--skip-index` | Use cached embeddings index | - |
| `--max-turns <n>` | Limit agent iterations | `200` |
| `--direct-api` | Use Anthropic API directly | - |

### `continue` - Resume/fix wiki generation

| Option | Description | Default |
|--------|-------------|---------|
| `-r, --repo <path>` | Repository path (required) | - |
| `-o, --output <dir>` | Wiki output directory | `./wiki` |
| `-m, --model <model>` | Claude model to use | `claude-sonnet-4-20250514` |
| `-v, --verbose` | Show detailed progress | - |
| `--verify-only` | Only check, don't generate | - |
| `--skip-index` | Use cached embeddings index | - |
| `--direct-api` | Use Anthropic API directly | - |
| `--max-turns <n>` | Limit agent iterations | `200` |

### `search` - Search wiki content

| Option | Description | Default |
|--------|-------------|---------|
| `<query>` | Search query (required) | - |
| `-w, --wiki <dir>` | Wiki directory | `./wiki` |
| `-n, --limit <n>` | Max results | `10` |
| `--hybrid` | Use hybrid search (keyword + semantic) | - |

### `mcp-server` - Start MCP server

| Option | Description | Default |
|--------|-------------|---------|
| `-w, --wiki <dir>` | Wiki directory (required) | - |
| `-r, --repo <path>` | Repository path (enables code search) | - |

### `pack` - Create wiki package

| Option | Description | Default |
|--------|-------------|---------|
| `-w, --wiki <dir>` | Wiki directory (required) | - |
| `-o, --output <file>` | Output package path | `<name>.archiwiki` |
| `-n, --name <name>` | Package name | wiki folder name |
| `--no-rag` | Exclude RAG index | - |

### `unpack` - Extract wiki package

| Option | Description | Default |
|--------|-------------|---------|
| `-p, --package <file>` | Package file (required) | - |
| `-o, --output <dir>` | Output directory | `.` |
| `--wiki-only` | Extract wiki only (no RAG index) | - |

## Static Site Features

When you use `--site`, SemanticWiki generates a fully interactive documentation site:

- **Full-text search** — Instant search across all pages (Cmd/Ctrl+K)
- **AI Chat Assistant** — Ask questions about your codebase (`--ai-chat`)
- **Keyboard navigation** — Arrow keys, vim-style (j/k/h/l)
- **Dark/light mode** — Respects system preference or manual toggle
- **Table of contents** — Auto-generated from headings
- **Mobile responsive** — Works on all devices
- **Offline capable** — No server required, AI runs client-side
- **Mermaid diagrams** — Rendered automatically

### AI Chat (`--ai-chat`)

Add an interactive AI assistant to your documentation site:

```bash
semanticwiki generate -r ./my-project --site --ai-chat
```

The chat assistant:

- Runs entirely in the browser (SmolLM2 via transformers.js)
- Searches your docs semantically to answer questions
- Works offline after initial model download
- Includes "codemap" mode for architecture visualization

## What to Expect

When you run SemanticWiki:

1. **Repository Analysis** — The agent scans your codebase structure
2. **Semantic Indexing** — Creates embeddings for intelligent code search
3. **Architecture Discovery** — Identifies patterns, components, and relationships
4. **Documentation Generation** — Writes markdown pages with diagrams
5. **Verification Loop** — Checks all links and generates missing pages
6. **Source Linking** — Every concept links to specific file:line references

### Typical Runtime

| Codebase Size | Approximate Time |
|---------------|------------------|
| Small (<50 files) | 1-2 minutes |
| Medium (50-200 files) | 2-5 minutes |
| Large (200+ files) | 5-10 minutes |

## Example Output

The generated wiki structure:

```
wiki/
├── README.md                    # Navigation entry point
├── architecture/
│   ├── overview.md              # System architecture + diagrams
│   └── data-flow.md             # Data flow documentation
├── components/
│   └── {module}/
│       └── index.md             # Per-module documentation
├── guides/
│   └── getting-started.md       # Quick start guide
├── glossary.md                  # Concept index
└── site/                        # (with --site flag)
    ├── index.html               # Interactive site entry
    ├── styles.css
    └── scripts.js
```

### Source Traceability Example

Every architectural concept includes clickable source references:

```markdown
## Authentication Flow

The authentication system uses JWT tokens for stateless auth.

**Source:** [`src/auth/jwt-provider.ts:23-67`](../../../src/auth/jwt-provider.ts#L23-L67)
```

## Configuration (Optional)

Create a `wiki.json` file in your project root to customize generation:

```json
{
  "repo_notes": [
    { "content": "Focus on the src/core directory for main logic" }
  ],
  "pages": [
    { "title": "Architecture Overview", "purpose": "High-level design", "parent": null },
    { "title": "Authentication", "parent": "Architecture Overview" }
  ],
  "exclude_patterns": ["**/*.test.ts", "**/__mocks__/**"],
  "output": {
    "format": "markdown",
    "diagrams": true
  }
}
```

## Technical Details

### RAG & Hybrid Search System

SemanticWiki uses a sophisticated retrieval system combining multiple strategies:

- **Chunk size**: 1,500 characters with 200 character overlap
- **Language-aware boundaries**: Chunks end at logical points (`}`, `};`, `end`)
- **Embedding model**: `BGE-small-en-v1.5` (384 dimensions, runs locally)
- **Hybrid search**: BM25 keyword + vector similarity with RRF fusion
- **Vector search**: FAISS with `IndexFlatIP` for cosine similarity
- **Incremental updates**: Only re-embeds changed files on subsequent runs

### Chunk Prioritization

For large codebases, chunks are prioritized by importance:

- Core directories (`src/`, `lib/`, `app/`): +100 points
- Entry points (`index.*`, `main.*`): +50 points
- Config files: +30 points
- Test files: -50 points
- Vendor/generated code: -100 points

## How It Works

SemanticWiki is built with:

- **[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk)** — Orchestrates the AI agent workflow
- **RAG (Retrieval Augmented Generation)** — Semantic code search using embeddings
- **[Model Context Protocol (MCP)](https://modelcontextprotocol.io)** — Tool integration for file operations
- **Mermaid** — Architecture diagram generation
- **FAISS** — High-performance vector similarity search

## Troubleshooting

### "Credit balance is too low" error

Use `--direct-api` to bypass Claude Code's billing check:

```bash
semanticwiki generate -r ./my-project --direct-api
```

### Out of memory on large repos

Limit the indexed chunks:

```bash
semanticwiki generate -r ./large-project --max-chunks 5000 --batch-size 3000
```

### Slow re-runs during development

Skip re-indexing with cached embeddings:

```bash
semanticwiki generate -r ./my-project --skip-index
```

### Missing pages / broken links

Use the continue command to fix:

```bash
semanticwiki continue -r ./my-project -o ./wiki
```

## License

MIT License — Copyright (c) 2025 Dakota Kim / reasoning.software (MadWatch LLC)

## Package Metadata

- **Version**: 1.2.1
- **License**: MIT
- **Keywords**: ai-agent, cli, claude, documentation, architecture, wiki, code-analysis, mcp
- **Dependencies**: @anthropic-ai/claude-agent-sdk, @anthropic-ai/sdk, @huggingface/transformers, @lepion/mcp-server-mermaid, @modelcontextprotocol/server-filesystem, axios, better-sqlite3, chalk, cheerio, commander, dotenv, faiss-node, glob, gray-matter, inquirer, inquirer-autocomplete-prompt, marked, node-llama-cpp, ollama, ora, simple-git
- **GitHub**: <https://github.com/GhostScientist/semanticwiki>