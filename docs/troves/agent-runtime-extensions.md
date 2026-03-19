# Agent Runtime Extension Models — Research Trove

**Date researched:** 2026-03-18

## Sources

- [OpenCode GitHub Repository](https://github.com/opencode-ai/opencode) — accessed 2026-03-18
- [OpenCode Docs: Agents](https://opencode.ai/docs/agents/) — accessed 2026-03-18
- [OpenCode Docs: MCP Servers](https://opencode.ai/docs/mcp-servers/) — accessed 2026-03-18
- [OpenCode Docs: Rules](https://opencode.ai/docs/rules/) — accessed 2026-03-18
- [OpenCode Docs: Skills](https://opencode.ai/docs/skills/) — accessed 2026-03-18
- [Gemini CLI GitHub Repository](https://github.com/google-gemini/gemini-cli) — accessed 2026-03-18
- [Gemini CLI Docs: Extensions](https://google-gemini.github.io/gemini-cli/docs/extensions/) — accessed 2026-03-18
- [Gemini CLI Docs: GEMINI.md and AGENTS.md](https://geminicli.com/docs/cli/gemini-md/) — accessed 2026-03-18
- [Gemini CLI Docs: Skills](https://geminicli.com/docs/cli/skills/) — accessed 2026-03-18
- [Google InfoQ: Gemini CLI Extensions](https://www.infoq.com/news/2025/10/gemini-cli-extensions/) — accessed 2026-03-18
- [Codex CLI Docs: AGENTS.md](https://developers.openai.com/codex/guides/agents-md) — accessed 2026-03-18
- [Codex CLI Docs: MCP](https://developers.openai.com/codex/mcp) — accessed 2026-03-18
- [Codex CLI Docs: Agent Skills](https://developers.openai.com/codex/skills) — accessed 2026-03-18
- [GitHub Copilot CLI GA Announcement](https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/) — accessed 2026-03-18
- [GitHub Copilot CLI: Adding MCP Servers](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers) — accessed 2026-03-18
- [GitHub Copilot CLI: Creating Custom Agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli) — accessed 2026-03-18
- [GitHub Copilot coding agent AGENTS.md support changelog](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/) — accessed 2026-03-18
- [Aider Docs: Configuration](https://aider.chat/docs/config.html) — accessed 2026-03-18
- [Aider Docs: Coding Conventions](https://aider.chat/docs/usage/conventions.html) — accessed 2026-03-18
- [Cursor Docs: Rules](https://cursor.com/docs/context/rules) — accessed 2026-03-18
- [Cursor Docs: MCP](https://cursor.com/docs/context/mcp) — accessed 2026-03-18
- [Windsurf Docs: AGENTS.md](https://docs.windsurf.com/windsurf/cascade/agents-md) — accessed 2026-03-18
- [Windsurf Docs: Cascade MCP](https://docs.windsurf.com/windsurf/cascade/mcp) — accessed 2026-03-18
- [AGENTS.md Official Site](https://agents.md/) — accessed 2026-03-18
- [AGENTS.md GitHub Repository](https://github.com/agentsmd/agents.md) — accessed 2026-03-18
- [InfoQ: AGENTS.md Emerges as Open Standard](https://www.infoq.com/news/2025/08/agents-md/) — accessed 2026-03-18
- [MCP Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol) — accessed 2026-03-18
- [MCP One Year Anniversary Post](http://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/) — accessed 2026-03-18
- [VS Code: Add and manage MCP servers](https://code.visualstudio.com/docs/copilot/customization/mcp-servers) — accessed 2026-03-18

---

## Runtime Profiles

### OpenCode

**Overview:** Open-source terminal-based AI coding agent written in Go. 95K+ GitHub stars as of early 2026. Supports 75+ models (Claude, OpenAI, Gemini, AWS Bedrock, Groq, Azure, OpenRouter). Available as CLI, desktop app, and IDE extension for VS Code, Cursor, and any ACP-compatible editor.

- **Extension model:** Three-layer extension system:
  1. **Agents** — configurable in `opencode.json` (JSON) or as markdown files with YAML frontmatter in `~/.config/opencode/agents/` (global) or `.opencode/agents/` (project). Agents specify model, system prompt, tools, permissions, temperature, max steps, and which subagents they may invoke. Primary agents and subagents are distinct categories; subagents are invoked via `@` mention.
  2. **Skills** — reusable instruction packages stored as `SKILL.md` files in `.opencode/skills/<name>/`, `~/.config/opencode/skills/<name>/`, or Claude-compatible/agent-compatible paths. Agents discover skills via a native `skill` tool and load them on demand. Frontmatter requires `name` and `description`.
  3. **Instructions** — arbitrary markdown files specified via `opencode.json` `"instructions"` array (local paths with glob patterns, or remote URLs). These are combined with AGENTS.md content.

- **MCP support:** Full, first-class. Both local (stdio, `type: "local"`) and remote (HTTP with OAuth, `type: "remote"`) MCP servers. Configured in `opencode.json` under `"mcp"`. Tools available globally or scoped per-agent. OAuth flow handled automatically via RFC 7591 Dynamic Client Registration. Tokens stored in `~/.local/share/opencode/mcp-auth.json`. Tool enable/disable via glob patterns.

- **AGENTS.md support:** Yes, native. `/init` command auto-generates an `AGENTS.md` by scanning project contents. File precedence order on startup:
  1. Local files via directory traversal (`AGENTS.md`, then fallback to `CLAUDE.md`)
  2. Global `~/.config/opencode/AGENTS.md`
  3. Legacy `~/.claude/CLAUDE.md` (unless disabled via `OPENCODE_DISABLE_CLAUDE_CODE=1`)

  Custom instruction files in `opencode.json` are merged with AGENTS.md content.

- **Custom tool/plugin support:** MCP servers are the primary tool extension point. Per-agent tool permission control (allow/deny/ask), including fine-grained bash command glob patterns. LSP server configuration also supported.

- **Relevance to swain:** OpenCode is architecturally the closest non-Claude runtime to swain's model. It natively reads AGENTS.md and CLAUDE.md, supports SKILL.md in `.agents/skills/` paths (the same convention swain uses), and has a richer agent/subagent model than most peers. Swain's skills will be discoverable by OpenCode out of the box with no modification.

---

### Gemini CLI

**Overview:** Google's open-source terminal AI agent. Node.js-based. Uses Gemini models. Supports a formal extension system, MCP, skills, and context files.

- **Extension model:** Formal **extension** architecture. Extensions live in `~/.gemini/extensions/<name>/` as directories containing:
  - `gemini-extension.json` — config with `name`, `version`, `mcpServers`, `contextFileName`, `excludeTools`
  - `GEMINI.md` (or custom `contextFileName`) — context injected into every session when the extension is active
  - `commands/` directory — TOML files defining custom slash commands
  - Bundled MCP servers that start automatically with the extension

  `settings.json` overrides extension MCP server config when names conflict.

- **MCP support:** Full, first-class. MCP servers configurable in `settings.json` or packaged inside extensions. Transport types: stdio and remote. OAuth supported. Google also announced fully-managed remote MCP servers for all Google/Google Cloud services.

- **AGENTS.md support:** Supported as an alternative to GEMINI.md. The primary file is `GEMINI.md`; AGENTS.md is supported as a configured alternative via `context.fileName` in `settings.json` (e.g., `["AGENTS.md", "GEMINI.md"]`). When both exist in the same directory, GEMINI.md takes precedence. Discovery follows a three-tier hierarchy:
  1. Global: `~/.gemini/GEMINI.md`
  2. Workspace: scans workspace directories and parents
  3. JIT: auto-discovered when tools access files, up to the trusted root

  `/memory show`, `/memory reload`, `/memory add` commands manage context. Modular imports via `@file.md` syntax.

- **Skills support:** Full skills system following the [Agent Skills open standard](https://agentskills.io). Skills are `SKILL.md` directories discovered at:
  1. Workspace: `.gemini/skills/` or `.agents/skills/`
  2. User: `~/.gemini/skills/` or `~/.agents/skills/`
  3. Extension-bundled

  Within a tier, `.agents/skills/` takes precedence over `.gemini/skills/`. Skills are activated via a four-step consent flow: discovery → identification → user consent → injection. Management via `/skills` commands and `gemini skills` CLI.

- **Relevance to swain:** Gemini CLI is the most sophisticated peer. It reads `.agents/skills/` paths (swain's convention) and supports AGENTS.md as a configured alternative to GEMINI.md. Swain skills placed in `.agents/skills/` will be discoverable. The extension bundling model (MCP server + context file + commands) is more structured than swain's current skill model — a potential design reference.

---

### Codex CLI (OpenAI)

**Overview:** OpenAI's terminal AI coding agent. Rust-based. Supports OpenAI models and models via OpenAI-compatible APIs. Introduced AGENTS.md as a standard in August 2025.

- **Extension model:** Two primary mechanisms:
  1. **AGENTS.md / instruction files** — project and global context layering (see below)
  2. **MCP servers** — tool extension via external processes or remote endpoints
  3. **Agent Skills** — a skills layer was documented but details are sparse in public docs

  Codex can itself be exposed as an MCP server (via `codex mcp serve`), enabling other agents to orchestrate it via the OpenAI Agents SDK.

- **MCP support:** Full, first-class. Two server types:
  - STDIO: local processes configured with `command`, `args`, `env`, `cwd`
  - Streamable HTTP: remote servers with bearer token or OAuth auth

  Configured via `codex mcp add <name>` CLI command or directly in `~/.codex/config.toml` (global) or `.codex/config.toml` (project, requires trust). Per-server `enabled_tools` / `disabled_tools` filtering. `/mcp` command in TUI for interactive access.

- **AGENTS.md support:** Native, first-class — Codex originated the AGENTS.md standard. Discovery order:
  1. Global: `~/.codex/AGENTS.override.md` (if present), else `~/.codex/AGENTS.md`
  2. Project: walks from git root to current directory, checking each level for `AGENTS.override.md`, then `AGENTS.md`, then fallback filenames configured via `project_doc_fallback_filenames`
  3. Files concatenate root-downward; closer files override earlier guidance by appearing later

  Combined guidance capped at 32 KiB (configurable via `project_doc_max_bytes`). Empty files skipped.

- **Custom tool/plugin support:** MCP servers only (no native plugin API beyond MCP). Configuration shared between CLI and IDE extension.

- **Relevance to swain:** Codex is the originator and canonical reference implementation of AGENTS.md. Its discovery hierarchy (global override → global → root-down traversal → override takes precedence) is the reference spec. Swain's AGENTS.md will be read correctly by Codex. The `.codex/config.toml` project-scoped MCP config is a security-conscious pattern worth noting.

---

### GitHub Copilot (CLI and IDE)

**Overview:** GitHub's AI coding assistant. GA for CLI as of February 2026. Available as VS Code extension, CLI, and IDE plugins for JetBrains, Vim, etc. Backed by GitHub/Microsoft infrastructure.

- **Extension model:** Multi-layer:
  1. **Custom agents** — `.agent.md` files in `.github/agents/` (project) or `~/.copilot/agents/` (user). Created interactively or manually. Agents specify tools, MCP servers, and instructions. User-level agents override project-level on naming conflict.
  2. **Skill files** — markdown-based skill files loaded automatically when relevant, work across Copilot coding agent, Copilot CLI, and VS Code
  3. **Plugins** — installable from GitHub repos via `/plugin install owner/repo`. Plugins can bundle MCP servers, agents, skills, and hooks.
  4. **Custom instructions** — `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` env var, `.copilot/` directory files, `.github/copilot-instructions.md`, and `.github/instructions/**.instructions.md`

- **MCP support:** Full, production-grade. GitHub's MCP server is built in. Custom MCP servers added via `/mcp add` (interactive) or by editing `~/.copilot/mcp-config.json`. Supported transports: STDIO, Streamable HTTP, SSE (deprecated). Tool selection granular: `*` for all, or comma-separated list. Management commands: `/mcp show`, `/mcp edit`, `/mcp delete`, `/mcp disable`, `/mcp enable`.

- **AGENTS.md support:** Full, multi-format. Copilot reads and respects:
  - `AGENTS.md` (standard, auto-read)
  - `.github/copilot-instructions.md`
  - `.github/instructions/**.instructions.md`
  - `CLAUDE.md` and `GEMINI.md` (cross-tool compatibility)

  Support announced August 28, 2025 for the coding agent. CLI GA includes AGENTS.md as first-class input. Nested AGENTS.md files supported for monorepos.

- **Custom tool/plugin support:** Plugin system for community/custom extensions. Enterprise teams can manage custom instructions via dashboard-based Team Rules.

- **Relevance to swain:** Copilot is the highest-adoption target. Its multi-format instruction reading (AGENTS.md + CLAUDE.md + GEMINI.md) means swain artifacts would be visible. The plugin bundling model (MCP + agents + skills + hooks in one installable unit) is a more polished version of what swain's skill distribution could become.

---

### Aider

**Overview:** Mature, open-source terminal AI coding assistant. Python-based. Pioneered pair-programming workflows with LLMs before the agentic wave. Highly configurable via YAML.

- **Extension model:** Conventions-first, not plugin-based:
  1. **Conventions files** — arbitrary markdown files (e.g., `CONVENTIONS.md`) loaded via `--read` flag or `read:` directive in `.aider.conf.yml`. Marked read-only and eligible for prompt caching. No special schema required.
  2. **`.aider.conf.yml`** — YAML configuration file in home dir or git root. Covers model settings, API keys, editor, and persistent read files.
  3. **No native MCP support** — MCP integration requires community tools like `mcpm-aider`, which generate a tool prompt and inject it into Aider's context. These are experimental as of early 2026, not official.
  4. **No plugin system** — extensibility is purely via file inclusion and model configuration. No hooks, no extension registry.

- **MCP support:** Not native. Community workarounds (mcpm-aider) exist but are unstable. Aider was designed before MCP's emergence and has not yet added first-class support. This is the largest extensibility gap relative to peers.

- **AGENTS.md support:** Listed on agents.md as a supported tool as of 2026. However, the mechanism appears to be via the `--read` convention (users add `read: AGENTS.md` to `.aider.conf.yml`) rather than automatic discovery. Aider does not auto-scan for AGENTS.md on startup the way Codex or OpenCode do.

- **Custom tool/plugin support:** None beyond file inclusion. The coder implementation (edit format, tool calls) is extensible in source code but not via user-facing plugin APIs.

- **Relevance to swain:** Aider is used by developers who prefer minimal configuration and explicit file management. Swain content will reach Aider users only if they manually add `read: AGENTS.md` to their config, or if Aider adds auto-discovery. The lack of MCP support means swain's MCP-oriented skill patterns have no traction here currently.

---

### Cursor

**Overview:** AI-first IDE (fork of VS Code). Dominant in the "agentic IDE" category as of 2025-2026. Strong MCP adoption. Advanced rules system.

- **Extension model:** Rules-based + MCP:
  1. **Project Rules** — `.cursor/rules/` directory, version-controlled. Markdown (`.md`) or Cursor Markdown (`.mdc`) files with optional YAML frontmatter. Four activation modes: Always Apply, Apply Intelligently (agent decides), Apply to Specific Files (glob), Manual (@-mention). Replaces deprecated `.cursorrules` file (now `.cursor/rules/*.mdc`).
  2. **User Rules** — global preferences in Cursor Settings. Applied to Agent/Chat only, not Inline Edit.
  3. **Team Rules** — organization-wide rules via dashboard (Team/Enterprise plans).
  4. **AGENTS.md** — supported as a simpler alternative to `.cursor/rules`. Plain markdown, no frontmatter. Location determines activation: root = always-on, subdirectory = auto-glob for that directory.

- **MCP support:** Full, among the most complete implementations. Configured via `.cursor/mcp.json` (project) or global settings. Supports resources (since v1.6, September 2025). Full protocol support. One-click "Add to Cursor" buttons on MCP server documentation pages. Security note: CVE-2025-54136 ("MCPoison") revealed trust was pinned to key name not command — patched.

- **AGENTS.md support:** Yes, native. Cursor explicitly documents AGENTS.md as a first-class alternative to `.cursor/rules`. Auto-discovered, location-based scoping. No frontmatter needed.

- **Custom tool/plugin support:** MCP servers are the primary tool extension mechanism. VS Code extension marketplace for IDE-level extensions. SKILL.md files supported for agent skills (domain-specific knowledge packages).

- **Relevance to swain:** Cursor's distinction between "AGENTS.md for simple location-based instructions" and "Rules for complex cross-cutting concerns" is a useful design frame. Swain's AGENTS.md will work natively in Cursor. Swain's SKILL.md convention maps to Cursor's skill system.

---

### Windsurf

**Overview:** AI-first IDE by Codeium. Agent is called Cascade. Emphasizes "Flow" — a continuous, intent-aware coding experience. Full MCP support. Native AGENTS.md.

- **Extension model:** Rules + Memories + MCP:
  1. **Rules** — stored in `.windsurf/rules/` with frontmatter. Control activation via glob patterns, always-on, or model-decided. Similar to Cursor's rule types.
  2. **Memories** — persistent notes Cascade accumulates and recalls across sessions. Configurable.
  3. **AGENTS.md** — native, auto-discovered. Fed into the same Rules engine with location-based activation inferred from file placement rather than frontmatter.
  4. **MCP servers** — via MCP Marketplace in Cascade panel or Settings. One-click setup for curated servers.

- **MCP support:** Full. Three transport types: stdio, Streamable HTTP, SSE. MCP Marketplace for curated one-click server installs. MCP servers scoped to Cascade interactions.

- **AGENTS.md support:** Yes, native. File discovery is case-insensitive (`AGENTS.md` or `agents.md`). Scans workspace and parent directories up to git root. Location determines activation mode:
  - Root directory → always-on rule (included in every message's system prompt)
  - Subdirectory → glob rule auto-generated as `<directory>/**`

  Both AGENTS.md and `.windsurf/rules/` are functional; AGENTS.md is recommended for simple location-based instructions.

- **Custom tool/plugin support:** MCP servers are the tool extension mechanism. No standalone plugin registry.

- **Relevance to swain:** Windsurf's AGENTS.md integration is the most semantically correct of the IDEs — it maps file location directly to activation scope, which is how swain's nested AGENTS.md files are intended to work. The root = always-on / subdirectory = scoped behavior is an important pattern.

---

### VS Code (with GitHub Copilot)

**Overview:** Microsoft's dominant code editor. AI capabilities via GitHub Copilot Chat extension. Agent mode became broadly available in April 2025. MCP support added same year.

- **Extension model:**
  1. **Custom instructions** — `.github/copilot-instructions.md` for repo-wide instructions. `.github/instructions/**.instructions.md` for scoped instructions. Configurable via `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`. Supports AGENTS.md.
  2. **Custom agents** — `.agent.md` files define specialized agents with their own tools and instruction sets.
  3. **MCP servers** — full support, configured in VS Code settings or `mcp.json` files.
  4. **VS Code extensions** — the broader marketplace ecosystem also contributes tools and agents to Copilot.

- **MCP support:** Full. Supports stdio and SSE transports. Built-in GitHub MCP server via a setting. Multi-agent orchestration (expanded in v1.107, November 2025). Enterprise controls added.

- **AGENTS.md support:** Yes. Copilot reads AGENTS.md alongside its own instruction formats. `/init` generates custom instructions for the project.

- **Custom tool/plugin support:** VS Code Marketplace extensions can contribute tools to Copilot. MCP servers are the primary open extension mechanism.

- **Relevance to swain:** VS Code is the largest installed base. Swain's AGENTS.md will be read by Copilot in VS Code. The dual-format support (AGENTS.md + `.github/copilot-instructions.md`) means swain doesn't need VS Code-specific packaging.

---

## Cross-Runtime Analysis

### Common Extension Mechanisms

The following mechanisms appear across two or more runtimes:

| Mechanism | Runtimes |
|-----------|----------|
| **AGENTS.md auto-discovery** | Codex CLI, OpenCode, Cursor, Windsurf, Gemini CLI (configured), GitHub Copilot, VS Code Copilot, Aider (manual) |
| **MCP server integration** | Codex CLI, OpenCode, Gemini CLI, GitHub Copilot CLI, Cursor, Windsurf, VS Code Copilot |
| **SKILL.md conventions** | OpenCode, Gemini CLI, Cursor, GitHub Copilot (skill files) |
| **Agent definition files** (.agent.md, agent YAML/MD) | OpenCode (.opencode/agents/), GitHub Copilot (.github/agents/), Gemini CLI (agent config) |
| **Global vs. project config separation** | All runtimes — global config in home dir, project config in repo root or subdirectory |
| **Directory-walk instruction loading** | Codex CLI (git root → cwd), OpenCode (root → cwd → global), Gemini CLI (global → workspace → JIT), Windsurf (git root) |
| **Skills/plugins bundling MCP + instructions** | Gemini CLI (extensions bundle MCP + GEMINI.md + commands), GitHub Copilot (plugins bundle MCP + agents + skills + hooks) |

### AGENTS.md Adoption

**Status:** Emerged as an open standard in August 2025, originated by OpenAI for Codex CLI. Stewardship transferred to the Agentic AI Foundation (AAIF) under the Linux Foundation in December 2025, co-founded by Anthropic, Block, and OpenAI. AGENTS.md is one of three founding projects alongside MCP and Block's goose.

**Adoption scale:** 60,000+ open-source projects as of early 2026.

**Runtimes with native auto-discovery of AGENTS.md:**
- OpenAI Codex CLI (originator — full spec compliance)
- OpenCode (native, with CLAUDE.md fallback)
- Cursor (first-class alternative to .cursor/rules, location-based scoping)
- Windsurf (native, feeds into Rules engine, location-based activation)
- GitHub Copilot coding agent and CLI (since August 2025, multi-format compatible)
- Google Gemini CLI (configurable via `context.fileName`, GEMINI.md takes precedence when both exist)
- Google Jules (native)
- Aider (listed as supported; mechanism is manual `--read` or `read:` config rather than auto-discovery)
- VS Code Copilot (via Copilot Chat)
- Zed, Warp, JetBrains Junie, Devin, Amp, goose, RooCode, Augment Code, and others

**Notable holdout:** Claude Code (Anthropic) uses CLAUDE.md, not AGENTS.md. An open GitHub issue requesting AGENTS.md support has 3,000+ upvotes. Anthropic has not committed to adding it. OpenCode bridges this by reading both AGENTS.md and CLAUDE.md.

**Format spec:** Plain markdown, no required fields or schema. Common sections: project overview, build/test commands, code style, contribution guidelines, security notes. Nested AGENTS.md files supported in monorepos; closest file takes precedence (or at root = always-on in some runtimes).

### MCP Adoption Outside Claude

**Status:** MCP was announced by Anthropic in November 2024, donated to the Linux Foundation's AAIF in December 2025. It is the dominant tool integration standard across the AI coding agent ecosystem.

**Adoption milestones:**
- March 2025: OpenAI adopted MCP across Agents SDK, Responses API, and ChatGPT Desktop
- April 2025: Google DeepMind adoption
- May 2025: Microsoft Build — GitHub and Microsoft joined MCP steering committee
- November 2025: MCP spec v2025-11-25 released; 97 million monthly SDK downloads, 10,000+ active servers
- December 2025: Donated to AAIF/Linux Foundation

**Runtimes with first-class MCP support:**
- OpenCode (local + remote, OAuth, per-agent scoping)
- Codex CLI (STDIO + Streamable HTTP, project-scoped config, also exposes itself as MCP server)
- Gemini CLI (via extensions or settings.json, Google-managed remote MCP)
- GitHub Copilot CLI and VS Code (built-in GitHub MCP server, custom servers)
- Cursor (most complete implementation, resources since v1.6)
- Windsurf (MCP Marketplace, three transports)
- VS Code (native, multi-agent orchestration)
- JetBrains IDEs, Zed, Sourcegraph, Replit

**Runtimes without native MCP:**
- Aider — community workarounds only (mcpm-aider), experimental/unstable

**Maturity gradient:**
- Production-grade: Cursor, VS Code Copilot, GitHub Copilot CLI, Gemini CLI
- Solid but newer: OpenCode, Codex CLI, Windsurf
- Community/experimental: Aider ecosystem

---

## Key Takeaways

- **AGENTS.md is the cross-runtime compatibility layer.** It has achieved near-universal adoption in under a year. Swain's AGENTS.md-based instruction model will work in Codex CLI, Cursor, Windsurf, Copilot, and Gemini CLI without modification. The main gap is Aider (manual config required) and the notable inverse gap is Claude Code (uses CLAUDE.md). OpenCode bridges both by reading AGENTS.md, CLAUDE.md, and legacy paths simultaneously.

- **SKILL.md in `.agents/skills/` is an emerging cross-runtime convention.** Both OpenCode and Gemini CLI treat `.agents/skills/` as a preferred discovery path (Gemini CLI explicitly prioritizes it over `.gemini/skills/`). Swain's skill packaging in `.agents/skills/` and `.claude/skills/` is positioned well for multi-runtime discovery.

- **MCP is the universal tool extension bus.** Every major runtime except Aider supports MCP natively in production. Swain MCP server patterns will transfer directly across Codex, Gemini CLI, Copilot, Cursor, and Windsurf. Designing swain tools as MCP servers rather than runtime-specific plugins maximizes portability.

- **The bundling model is converging.** Gemini CLI extensions (MCP server + context file + commands), GitHub Copilot plugins (MCP + agents + skills + hooks), and OpenCode's combined agent/skill/instruction system all describe a similar pattern: a named, distributable unit that bundles context, tools, and behavior together. Swain's skill model is architecturally compatible with this direction and could be extended to produce installable bundles.

- **Claude Code is the outlier, not the standard.** CLAUDE.md is Claude Code's proprietary instruction file; the ecosystem default is AGENTS.md. Swain should maintain CLAUDE.md as the primary file for Claude Code while ensuring AGENTS.md is present (or symlinked/copied) for cross-runtime use. Projects that only ship CLAUDE.md will be invisible to every non-Anthropic runtime. The AAIF governance structure means AGENTS.md has institutional backing that makes it safe to invest in long-term.
