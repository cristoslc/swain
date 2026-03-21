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

## Agent Integration Points

All sources agree that Stitch is designed for agent integration:

- **Vercel AI SDK**: `stitchTools()` from `@google/stitch-sdk/ai` returns Tool objects compatible with `generateText()`. Models autonomously call `create_project`, `generate_screen`, `get_screen`.
- **MCP Server**: `StitchProxy` exposes tools via stdio transport for any MCP-compatible client (Claude Code, Gemini CLI, Cursor).
- **Direct tool client**: `stitch.callTool("tool_name", args)` for orchestration scripts.
- **Antigravity IDE**: Deep integration — install Stitch Skills from GitHub, agent generates design variations.
- **DESIGN.md export**: Natural language design file for maintaining consistency across tools.

## Authentication

Two paths:
1. **API Key**: Set `STITCH_API_KEY` env var (simplest)
2. **OAuth**: Set `STITCH_ACCESS_TOKEN` + `GOOGLE_CLOUD_PROJECT`

## Platform Evolution

| Date | Milestone |
|------|-----------|
| May 2025 | Launch at Google I/O — text-to-UI, image-to-UI, Figma export |
| Dec 2025 | Gemini 3, interactive prototypes ("Play" button) |
| Mar 2026 | AI-native infinite canvas, Voice Canvas, Vibe Design, Direct Edits, up to 5 screens at once, MCP server + SDK |

## Points of Agreement

- Free tool, Google account only — no usage-based pricing
- Generates functional HTML/CSS, not just mockups
- MCP is the integration substrate for connecting to external agents
- Best positioned as ideation/exploration tool, not production design system replacement
- Figma export preserves Auto Layout and editable layers

## Points of Disagreement

- **Generation limits**: NxCode reports 350 Standard / 50 Experimental per month; other sources say "no limits". The caps may be soft or recently changed.
- **Tailwind support**: SiliconANGLE mentions Tailwind support; SDK README and NxCode guide don't mention it. May be a platform feature not exposed in the SDK.

## Gaps

- **No official tutorial content fetchable**: The stitch.withgoogle.com/docs/sdk/tutorial/ page is a JS SPA that returns no content server-side. The GitHub README is the authoritative SDK documentation.
- **MCP tool list**: No source enumerates the complete list of MCP tools available. `listTools()` would need to be called at runtime.
- **Rate limits for SDK**: API rate limits for programmatic usage are undocumented.
- **OAuth flow details**: How to obtain an OAuth access token for Stitch specifically is not documented.
- **Streaming**: Whether `streamText()` integration supports streaming screen generation progress is unclear.
