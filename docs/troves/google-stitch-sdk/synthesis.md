# Google Stitch SDK — Synthesis

## What Stitch Is

Google Stitch is an AI-powered UI design tool from Google Labs that generates high-fidelity interfaces from text prompts, images, sketches, or voice descriptions. It produces clean HTML/CSS code and interactive prototypes. Completely free — requires only a Google account. Powered by Gemini models (2.5 Flash, 2.5 Pro, Gemini 3).

## SDK Architecture

The `@google/stitch-sdk` npm package provides programmatic access to Stitch's capabilities. It communicates with Stitch via an MCP (Model Context Protocol) server at `stitch.googleapis.com/mcp`. Key classes:

- **`Stitch`** — root class managing projects. Singleton `stitch` import for zero-config usage.
- **`Project`** — contains screens. `generate()` creates screens from text prompts with device type targeting (MOBILE/DESKTOP/TABLET/AGNOSTIC).
- **`Screen`** — generated UI. Supports `edit()`, `variants()`, `getHtml()`, `getImage()`. Model selection: GEMINI_3_PRO or GEMINI_3_FLASH.
- **`StitchToolClient`** — low-level MCP pipe for direct tool access (`callTool`, `listTools`). Auto-connects lazily.
- **`StitchProxy`** — MCP proxy server to expose Stitch tools through your own MCP server.
- **`stitchTools()`** — drops Stitch MCP tools into Vercel AI SDK's `generateText()`/`streamText()` for autonomous agent usage.

## Skills Ecosystem

Yes — there is a rich ecosystem of skills wrapping Stitch, at multiple levels:

### Official: google-labs-code/stitch-skills (2.9k stars)

Google Labs maintains an official skill library following the **Agent Skills open standard**. Seven skills available, installable via `npx skills add`:

| Skill | Purpose |
|-------|---------|
| **stitch-design** | Unified entry point — prompt enhancement, DESIGN.md synthesis, screen generation/editing |
| **stitch-loop** | Full multi-page website from a single prompt, with file organization and validation |
| **design-md** | Analyzes Stitch projects → generates DESIGN.md documenting the design system in semantic language |
| **enhance-prompt** | Transforms vague UI ideas into Stitch-optimized prompts with UI/UX keywords |
| **react-components** | Converts Stitch screens → React component systems with design token consistency |
| **remotion** | Generates walkthrough videos from Stitch projects using Remotion |
| **shadcn-ui** | Expert guidance for integrating shadcn/ui components into React apps |

Compatible with: **Antigravity, Gemini CLI, Claude Code, Cursor**.

Skill structure follows a standard layout: `SKILL.md` (mission control), `scripts/` (validators), `resources/` (knowledge base), `examples/` (gold standards).

### Community: davideast/stitch-mcp (495 stars)

David East's independent CLI and MCP proxy adds higher-level "virtual tools" on top of the upstream Stitch MCP:

- **build_site** — maps screens to routes, generates an Astro site
- **get_screen_code** — retrieves screen HTML content
- **get_screen_image** — retrieves screenshot as base64

Also provides: local Vite dev server preview, interactive terminal browser, `init` wizard for auth setup, `doctor` for config health.

Supported clients: VS Code, Cursor, Claude Code, Gemini CLI, Codex, OpenCode.

### Third-party marketplace skills

Multiple community skills on mcpmarket.com and lobehub: `stitch-ui-design`, `stitch-build-loop`, `stitch-prompt-architect`, `google-stitch-expert`, `stitch-setup`. These wrap specific Stitch workflows for Claude Code's `.claude/skills/` directory.

## Agent Integration Points

All sources agree that Stitch is designed for agent integration:

- **Vercel AI SDK**: `stitchTools()` from `@google/stitch-sdk/ai` returns Tool objects compatible with `generateText()`. Models autonomously call `create_project`, `generate_screen`, `get_screen`.
- **MCP Server (official)**: `StitchProxy` exposes tools via stdio transport for any MCP-compatible client.
- **MCP Proxy (community)**: `@_davideast/stitch-mcp proxy` adds virtual tools and auto token refresh.
- **Direct tool client**: `stitch.callTool("tool_name", args)` for orchestration scripts.
- **Antigravity IDE**: Deep integration — MCP store has one-click Stitch install, Agent Tab for autonomous builds.
- **Gemini CLI Extension**: Terminal-based Stitch interaction with AI-driven prompts aligned to brand guidelines.
- **DESIGN.md**: The key bridge artifact — extracted design tokens (colors, typography, spacing) in natural language, consumed by coding agents for implementation accuracy.

## The Design-to-Code Workflow

The Google Codelab documents the canonical end-to-end flow:

1. **Design in Stitch** — natural language prompt → Gemini 3 generates high-fidelity UI
2. **Generate API key** — Profile > Settings > API key
3. **Configure MCP** — install Stitch in Antigravity's MCP store (or add to Claude Code/Cursor config)
4. **Extract DESIGN.md** — agent fetches design tokens via MCP into a `DESIGN.md` file
5. **Autonomous build** — agent scaffolds React + Tailwind project from design context
6. **Vibe Check** — compare integrated browser output to original Stitch design
7. **Refine** — agent re-fetches design context and fixes discrepancies

## Authentication

Three paths (from most to least common):
1. **API Key**: Set `STITCH_API_KEY` env var (simplest)
2. **OAuth via gcloud**: `gcloud auth application-default login` + enable Stitch API
3. **OAuth token**: Set `STITCH_ACCESS_TOKEN` + `GOOGLE_CLOUD_PROJECT`

The `stitch-mcp init` wizard automates gcloud setup and MCP client configuration.

## Platform Evolution

| Date | Milestone |
|------|-----------|
| May 2025 | Launch at Google I/O — text-to-UI, image-to-UI, Figma export |
| Jan 2026 | MCP Server, Gemini CLI Extension, Agent Skills announced |
| Mar 2026 | AI-native infinite canvas, Voice Canvas, Vibe Design, Direct Edits, up to 5 screens at once, SDK + official skills repo (v0.1) |

## Points of Agreement

- Free tool, Google account only — no usage-based pricing
- Generates functional HTML/CSS, not just mockups
- MCP is the integration substrate for connecting to external agents
- Skills follow the Agent Skills open standard — cross-compatible across Antigravity, Gemini CLI, Claude Code, Cursor
- DESIGN.md is the canonical bridge artifact between design and code
- Best positioned as ideation/exploration tool, not production design system replacement
- Figma export preserves Auto Layout and editable layers

## Points of Disagreement

- **Generation limits**: NxCode reports 350 Standard / 50 Experimental per month; other sources say "no limits". The caps may be soft or recently changed.
- **Tailwind support**: SiliconANGLE mentions Tailwind support; SDK README doesn't mention it. The Codelab uses React + Tailwind as the build target, confirming Tailwind is supported in output, even if not as a direct SDK feature.
- **Official vs community MCP**: The official `StitchProxy` from `@google/stitch-sdk` and `@_davideast/stitch-mcp` serve similar purposes but the community version adds virtual tools (build_site) and Astro site generation. Not clear if official SDK will absorb these.

## Gaps

- **No official tutorial content fetchable**: The stitch.withgoogle.com/docs/sdk/tutorial/ page is a JS SPA that returns no content server-side. The GitHub README is the authoritative SDK documentation.
- **MCP tool list**: No source enumerates the complete list of MCP tools available. `listTools()` would need to be called at runtime.
- **Rate limits for SDK**: API rate limits for programmatic usage are undocumented.
- **Skill internals**: The official stitch-skills repo README documents what each skill does, but the actual SKILL.md content, scripts, and examples are not ingested in this trove.
- **Streaming**: Whether `streamText()` integration supports streaming screen generation progress is unclear.
