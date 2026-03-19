# Claude Web & Desktop Extension Model — Research Trove

**Date researched:** 2026-03-18

---

## Sources

- [What are projects? — Claude Help Center](https://support.claude.com/en/articles/9517075-what-are-projects)
- [How can I create and manage projects? — Claude Help Center](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)
- [Claude Projects Feature Guide (aionx.co)](https://aionx.co/claude-ai-reviews/claude-projects-feature-guide/)
- [Claude Projects vs ChatGPT Projects — Unmarkdown Blog](https://unmarkdown.com/blog/claude-projects-vs-chatgpt-projects)
- [Getting Started with Local MCP Servers on Claude Desktop — Claude Help Center](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
- [One-click MCP server installation for Claude Desktop — Anthropic Engineering](https://www.anthropic.com/engineering/desktop-extensions)
- [Use connectors to extend Claude's capabilities — Claude Help Center](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- [Get started with custom connectors using remote MCP — Claude Help Center](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [MCP connector — Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector)
- [Use Claude Code Desktop — Claude Code Docs](https://code.claude.com/docs/en/desktop)
- [Claude expands tool connections using MCP — Help Net Security (Jan 27, 2026)](https://www.helpnetsecurity.com/2026/01/27/anthropic-claude-mcp-integration/)
- [Anthropic upgrades Cowork and plugins on Claude for Enterprise — Testing Catalog (Feb 2026)](https://www.testingcatalog.com/anthropic-upgrades-cowork-and-plugins-on-claude-for-enterprise/)
- [Anthropic Adds 13 Enterprise Plugins to Claude Cowork (Feb 25, 2026)](https://winbuzzer.com/2026/02/25/anthropic-claude-cowork-13-enterprise-plugins-google-workspace-docusign-xcxwbn/)
- [Anthropic Release Notes — March 2026 (Releasebot)](https://releasebot.io/updates/anthropic)
- [Claude Desktop Roadmap 2026 Features Predictions — Skywork](https://skywork.ai/blog/ai-agent/claude-desktop-roadmap-2026-features-predictions/)
- [The Complete Map of Anthropic's Developer Ecosystem — ClaudeWorld](https://claude-world.com/articles/anthropic-developer-ecosystem-complete-guide/)
- [Claude Agent Skills: A First Principles Deep Dive — Lee Han Chung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Prompting best practices — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Best MCP Server Directories for Developers — Descope Blog](https://www.descope.com/blog/post/mcp-directories)
- [The Best MCP Servers for Developers in 2026 — builder.io](https://www.builder.io/blog/best-mcp-servers-2026)
- [Claude AI Review 2026 — max-productive.ai](https://max-productive.ai/ai-tools/claude/)
- [What makes Claude Code different from regular Claude? — Milvus AI Quick Reference](https://milvus.io/ai-quick-reference/what-makes-claude-code-different-from-regular-claude)
- [Claude, Claude API, and Claude Code: What's the Difference? — 16x Engineer](https://eval.16x.engineer/blog/claude-vs-claude-api-vs-claude-code)

---

## Findings

### Claude Web (claude.ai)

#### Projects

Projects are self-contained workspaces with independent chat histories and knowledge bases. Available to all users including free tier (capped at 5 projects). Paid plans (Pro, Max, Team, Enterprise) unlock RAG scaling and sharing.

**What you can put in a Project:**
- A **project instructions** field (system prompt equivalent). No documented character limit; works like a persistent system prompt applied to every conversation in the project. Token budget consideration: it counts toward the context window on every message.
- A **knowledge base** of uploaded files: PDF, DOCX, CSV, TXT, HTML, ODT, RTF, EPUB. Individual file limit is 30 MB. No cap on number of files provided total content stays within context.
- A **project-scoped memory summary** (auto-synthesized, ~24-hour cycle). Users can view and edit it. Organized into categories like "Role and Work" and "Current Projects."

**Context capacity:**
200,000-token context window per project. On paid plans, RAG mode automatically engages when the knowledge base approaches the limit, providing ~10x effective capacity expansion. On free plans, no RAG fallback.

**Context isolation:** Projects are siloed — documents in one project are not accessible in another. No cross-project references.

**Sharing and collaboration:**
- Free: no sharing.
- Pro/Max: personal use only.
- Team/Enterprise: share at individual, list, or org-wide level. Two permission tiers: "Can use" (view + chat, read-only) and "Can edit" (full modification including instructions and knowledge base).

**MCP / tool integration in Projects:**
Projects themselves have no MCP configuration surface. MCP integration in claude.ai is handled via **Connectors** (separate from Projects), described below.

#### Connectors (MCP in claude.ai)

Launched January 26, 2026. Connectors bring MCP-powered tools into claude.ai chat — including inside Project conversations.

**What they are:** Connectors expose external tools (read data, write data, take actions, render interactive UIs) using MCP. The "MCP Apps" extension to MCP allows connectors to render live interfaces (task boards, dashboards, design canvases) directly inside Claude's chat window.

**Pre-built connector catalog:** As of early March 2026, 50+ curated integrations with new ones added weekly. Categories: communication (Slack, Gmail, Microsoft 365), project management (Asana, Linear, Jira, Monday.com), content (Notion, Google Drive, WordPress.com), design (Canva, Figma), engineering/data (GitHub, Hex, Amplitude), finance (Stripe), healthcare (Apple Health, PubMed). Pre-built connectors work on all plans.

**Custom connectors via remote MCP (beta):** Users can add their own remote MCP server URLs.
- Free: 1 custom connector.
- Pro/Max: unlimited custom connectors, self-managed.
- Team/Enterprise: org-level management with auto-install, allowlist/blocklist, and private GitHub repos as plugin sources (private beta).
- Authentication is OAuth-based; no passwords sent to Claude.
- Connectors added in claude.ai are automatically synced to Claude Code if you log in with the same account.

**Critical limitation:** The API-side MCP connector (`mcp-client-2025-11-20` beta header) supports only **tool calls** from the MCP spec. Prompts and Resources are not supported via the API connector path.

**Note:** Connectors in the web chat are described as "only available in private projects" for Team/Enterprise plans, suggesting they function within the Project context rather than as a separate global layer.

#### Plan-gated features summary

| Feature | Free | Pro | Max | Team | Enterprise |
|---|---|---|---|---|---|
| Projects | Yes (5 max) | Yes | Yes | Yes | Yes |
| RAG in Projects | No | Yes | Yes | Yes | Yes |
| Project sharing | No | No | No | Yes | Yes |
| Pre-built connectors | Yes | Yes | Yes | Yes | Yes |
| Custom connectors | 1 | Unlimited | Unlimited | Org-managed | Org-managed |
| Interactive connector UIs | No | Yes | Yes | Yes | Yes |
| Enterprise plugin marketplace | No | No | No | No | Yes |

---

### Claude Desktop

The Claude Desktop app has **two distinct modes**: the **Chat tab** (consumer chatbot, like claude.ai) and the **Code tab** (Claude Code with a GUI). These share the same desktop binary but are architecturally separate.

#### Claude Desktop Chat tab

The chat experience in the desktop app mirrors claude.ai. It supports Projects, Connectors (same catalog and custom connector setup), and the same plan-gated features. The chat tab does not have native shell/filesystem access.

**Desktop Extensions (.mcpb format):**
Desktop Extensions are locally installed MCP servers packaged as `.mcpb` bundles (ZIP archives with a `manifest.json`). They allow Claude Desktop to expose local MCP servers without terminal setup.

Key technical details:
- File format: `.mcpb` (MCP Bundle); previously `.dxt`, which still works.
- Supported server runtimes: Node.js (built-in runtime shipped with the app), Python, and binary/executable.
- Installation: drag a `.mcpb` file into Claude Desktop settings, or click from the extensions directory in Settings > Extensions.
- Manifest declares: server entry points, user-required inputs (e.g., API keys), available tools and prompts, platform-specific overrides.
- Template variables: `${__dirname}`, `${user_config.key}`, `${HOME}`, `${TEMP}`.
- Security: sensitive config fields stored in OS keychain (macOS) or Credential Manager (Windows). Developers mark fields `"sensitive": true`.
- Enterprise controls: MDM/Group Policy deployment, pre-installation of approved extensions, allowlist/blocklist per publisher, option to disable public directory entirely.
- Developer tooling: `npx @anthropic-ai/mcpb init` and `npx @anthropic-ai/mcpb pack`.

**Important separation:** MCP servers configured for the Claude Desktop chat tab (`claude_desktop_config.json`) are **completely separate** from MCP servers configured for Claude Code (`.claude.json` or `.mcp.json`). They do not share configuration.

#### Claude Desktop Code tab

This is Claude Code with a GUI — same agentic engine, same skills/plugins/MCP config. Adds:
- Visual diff review with inline commenting
- Live app preview with embedded browser and auto-verify
- GitHub PR monitoring with auto-fix and auto-merge
- Parallel sessions with automatic Git worktree isolation
- Scheduled recurring tasks (SKILL.md-backed, local execution)
- Connectors UI (for GitHub, Slack, Linear, Notion, etc.) — same as the claude.ai connector system but with GUI setup flow
- SSH session support (run Claude on a remote machine)
- Remote cloud sessions (Anthropic-hosted, continue when app is closed)

**Code tab does not support:** third-party model providers (Bedrock, Vertex, Foundry), Linux (macOS and Windows only), agent teams/multi-agent orchestration (CLI/Agent SDK only), scripting/automation flags (`--print`, `--output-format`).

---

### Capability Gap Analysis

What Claude Code has that claude.ai web and Claude Desktop chat do not:

| Capability | Claude Code | Claude Web / Desktop Chat |
|---|---|---|
| Filesystem read/write | Native, direct | Not available (file upload only) |
| Shell/bash execution | Native | Not available |
| Git operations | Native (commit, push, branch, worktrees) | Not available |
| Skills (SKILL.md) | Full support — auto-invoked, context-modifying | Not available |
| Plugins (.mcpb bundles) | Full support with plugin marketplace | Desktop chat supports .mcpb for MCP only, no skill/hook/LSP packaging |
| Hooks (pre/post tool events) | Full support (StopFailure, PostCompact, Elicitation, etc.) | Not available |
| CLAUDE.md project memory | Read at session start | Not available (Projects instructions are the analog) |
| Agentic loops / headless mode | Full support (`--print`, Agent SDK) | Not available |
| Multi-agent orchestration | Available (CLI/Agent SDK) | Not available |
| Scheduled tasks | Desktop Code tab (GUI) / cron (CLI) | Not available |
| Third-party LLM providers | Bedrock, Vertex, Foundry | Not available |
| Model override per skill | Yes (YAML frontmatter `model:`) | Not available |
| Tool permission scoping | Fine-grained (`Bash(git:*)`, per-skill) | Not available |
| Plugin persistent data | `${CLAUDE_PLUGIN_DATA}` (as of v2.1.73+) | Not available |
| MCP elicitation (mid-task input) | Supported | Not available |
| Context compaction control | `/compact`, programmatic | Automatic, not user-controlled |

**What claude.ai has that Claude Code does not:**
- Project knowledge bases (persistent uploaded files that don't need re-upload per session)
- RAG-backed knowledge scaling
- Project-scoped memory summaries (auto-synthesized, user-editable)
- Organization-level project sharing (Team/Enterprise)
- Interactive connector UIs (live rendered interfaces from MCP Apps extension)
- Mobile access (iOS/Android — remote Claude Code sessions viewable but not full feature parity)

**The fundamental architectural gap:** Claude Code is a stateful agentic runtime with direct environment access. Claude web/desktop chat is a stateless conversational UI. The closest bridge is the **Connectors** system (MCP in claude.ai), which can expose actions and data reads, but cannot run code locally, access the filesystem, or execute long-horizon agentic loops.

---

### Extensibility Roadmap

Signals from public announcements through March 2026:

**MCP as the universal extension layer:** Anthropic has committed to MCP as the cross-product integration standard. It was donated to the Linux Foundation's Agentic AI Foundation in December 2025. OpenAI adopted it in March 2025, Google DeepMind confirmed support in April 2025. It is now effectively the industry standard.

**January 26, 2026 — Interactive connectors in claude.ai:** Connectors launched with 50+ integrations and "MCP Apps" rendering — live UIs from Figma, Asana, Canva, Slack, etc. inside chat conversations. Available on Pro, Team, Enterprise.

**February 24, 2026 — Enterprise Cowork + 13 new plugins:** Anthropic's "Briefing: Enterprise Agents" event shipped 13 MCP connectors spanning Google Workspace (Drive, Calendar, Gmail), DocuSign, Apollo, Clay, Outreach, SimilarWeb, MSCI, LegalZoom, FactSet, WordPress, Harvey. Enterprise organizations can now build **private plugin marketplaces** for internal tool distribution. Claude can maintain cross-app context (e.g., Excel → PowerPoint multi-step project) as a research preview.

**March 2026 — Persistent agent thread in Cowork:** Pro and Max users get a persistent agent thread for task management via Claude Desktop and mobile (Cowork tab). Rolled out Max first, then Pro.

**Claude Code plugin ecosystem:** Official plugin directory launched early 2026 with 72+ plugins across 24 categories. Plugins now support persistent data storage (`${CLAUDE_PLUGIN_DATA}`), MCP elicitation, new hook events, and 64k output tokens (upper bound 128k).

**1M context GA:** 1M token context is now generally available for Opus 4.6 and Sonnet 4.6 on Max/Team/Enterprise at standard pricing.

**Trajectory:** Anthropic is converging toward a unified extensibility model where MCP servers, skills/plugins, and org-managed marketplaces span web, desktop, and API. The remaining gap between Code and web/desktop chat is the agentic execution environment (filesystem, shell, long-horizon loops). No public announcement of that closing for the web chat surface.

---

### System Prompt Packaging Patterns

#### Project Instructions (claude.ai)

Project Instructions are the web analog of a system prompt. Best practices:

- **No documented character limit** — practical constraint is the context window budget. Long instructions consume tokens on every message.
- Use for: stable behavioral guidelines, role definition, tone, response format preferences, domain context, escalation rules.
- Reserve task-specific instructions for the chat itself.
- Use XML tags to structure instructions: `<instructions>`, `<context>`, `<constraints>`, `<examples>`. This helps Claude parse complex prompts unambiguously.
- For decision-support frameworks: encode the decision tree or criteria hierarchy in the instructions; use knowledge-base files for reference material (rubrics, playbooks, templates).
- Put long documents in the knowledge base (not in instructions) to avoid burning context on every turn.

#### CLAUDE.md / AGENTS.md (Claude Code)

CLAUDE.md is read at session start and injected into Claude Code's context. It functions as the project-level system prompt equivalent for the agentic runtime.

Key patterns used in practice:
- Role definition and behavioral constraints at the top
- `@AGENTS.md` include pattern (swain's approach) for separating project instructions from agent-specific routing rules
- Skill routing tables (trigger → skill mapping)
- Constraint lists (non-interactive flags, tooling preferences, naming conventions)
- Habit instructions that shape how the agent structures its work

#### Agent Skills (SKILL.md)

Skills are the primary mechanism for packaging complex workflows in Claude Code. Each skill is a markdown file with YAML frontmatter + instruction body. They are loaded on demand (not at startup), injected as hidden messages, and can modify tool permissions and model selection for their duration.

Patterns for decision-support workflows:
- **Wizard workflows:** multi-step processes with explicit user confirmation gates between phases
- **Reference loading:** `references/` directory files are loaded into context on demand, not at startup — use for rubrics, playbooks, decision frameworks
- **Script automation:** `scripts/` directory houses Python/Bash that Claude invokes via Bash tool; results fed back into reasoning
- **Read-Process-Write:** load artifacts, transform per rules, emit structured output
- **Prompt for context, then decide:** skill instructions can direct Claude to ask clarifying questions before proceeding — encodes a decision tree as a structured conversation

For packaging a decision-support framework (like swain's artifact lifecycle) as a skill:
1. Define the decision criteria and state machine in the SKILL.md body using structured markdown
2. Store reference tables, rubrics, and examples in `references/` files
3. Include scripts for any deterministic lookups (file existence checks, status reads)
4. Use `allowed-tools` in frontmatter to pre-approve only the tools needed
5. Use `disable-model-invocation: true` if the skill should only be invoked explicitly, not auto-triggered

#### Key Constraints on System Prompt Packaging

- Skills exist only in Claude Code — there is no equivalent in claude.ai Projects.
- The SKILL.md `description` field has a 15,000-character aggregate budget across all installed skills (the Skill tool prompt).
- Skills are Claude Code-specific: YAML frontmatter, `{baseDir}` path resolution, and tool permission syntax are not portable to claude.ai.
- For a workflow to be portable to claude.ai, it must be expressible entirely as Project Instructions + knowledge base files, without shell execution, file writes, or script invocation.

---

### MCP Ecosystem State

#### Scale

As of early 2026:
- PulseMCP: 7,600+ community servers
- MCP Market: 19,000+ servers (largest catalog, minimal curation)
- Glama: 14,000+ servers (most curated — automated security scans, license checks, vulnerability checks)
- GitHub MCP Registry: ~65 servers (official reference implementations only)

MCP was donated to the Linux Foundation's Agentic AI Foundation in December 2025. It is now the universal interface between AI and developer tools.

#### Distribution and Discovery

No single directory dominates. Recommended multi-stage approach:
1. **PulseMCP** for initial discovery (popularity signals, autocomplete search)
2. **Glama** for security verification (DeepSearch with category filters, maintainer authentication)
3. **GitHub Registry** for standards compliance (official reference implementations)

Installation experience is still rough: testing a single server (DBHub) required ~75 minutes across directories, ultimately requiring manual navigation to external documentation. Directories display README files but provide no agent-specific installation flows.

#### Categories of notable MCP servers (2026)

- **Development:** GitHub (50+ tools), filesystem, Postgres, browser automation (Playwright), Docker
- **Productivity:** Google Workspace, Notion, Asana, Linear, Jira, Slack, Microsoft 365
- **Data/Engineering:** Hex, Amplitude, Stripe, databases (SQLite, MySQL, various)
- **Finance:** FactSet, MSCI, S&P Global (via enterprise connectors)
- **Infrastructure/Platform:** OpenTelemetry, observability tools, CI/CD

#### Developer Experience for Building MCP Servers

For **remote MCP servers** (connectors in claude.ai and API):
- Server must be publicly exposed via HTTPS (Streamable HTTP or SSE transports)
- Local STDIO servers cannot connect directly to the API MCP connector
- SDK available in Python and TypeScript
- `npx @anthropic-ai/mcpb init` scaffolds a Desktop Extension bundle
- OAuth for auth; developer handles the OAuth flow before passing `authorization_token` to the API

For **local MCP servers** (Claude Code / Claude Desktop Code tab):
- Configured in `~/.claude.json` or `.mcp.json` (project-scoped)
- Supports STDIO transport (local process) and HTTP/SSE (remote)
- Node.js, Python, binary runtimes supported

**The Connectors shortcut:** For claude.ai integration, building a remote MCP server and registering it as a custom connector is the practical path. The Connectors Directory submission process exists but review criteria are opaque.

---

## Key Takeaways

- **Skills are Claude Code-only.** There is no equivalent of SKILL.md, CLAUDE.md, or hook-based automation in claude.ai Projects. The web analog is Project Instructions (system prompt) + knowledge base files. Portability requires stripping everything that depends on shell access, file writes, or script invocation.

- **Connectors are the bridge, but they are read/write tools, not workflow engines.** MCP connectors in claude.ai can read and write data in external services, and render interactive UIs, but they cannot run agentic loops, execute code locally, or replace the SKILL.md execution model. A swain connector could surface artifact status or trigger actions, but not replicate the full agent workflow.

- **The extensibility model is converging on MCP, but the web surface lags Claude Code.** Claude Code has plugins, skills, hooks, headless mode, and fine-grained tool permissions. Claude web/desktop chat has connectors (MCP) and Project Instructions. The gap is narrowing (interactive UIs, enterprise plugin marketplaces, persistent agent threads in Cowork) but the agentic execution environment is still Code-only.

- **Enterprise is the current distribution vector for complex workflow packaging.** The February 2026 Cowork launch shows Anthropic's path for packaging domain-specific agent workflows: private plugin marketplaces, org-managed connector catalogs, and role-specific agent templates. This is where swain-like decision-support frameworks could land for a non-Code audience.

- **Project Instructions + knowledge base is the practical portability target.** A read-only, conversation-oriented version of swain's artifact lifecycle management could be delivered as a Project with: instructions encoding the lifecycle rules and routing logic, knowledge base files containing artifact templates and ADR playbooks, and a connected MCP server for reading artifact state from the repo. Full write operations (creating files, running transitions) would require Claude Code or the API.
