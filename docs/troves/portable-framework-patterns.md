# Portable Agent Framework Patterns — Research Trove

**Research date:** 2026-03-18
**Purpose:** Inform swain's packaging, distribution, and portability strategy.

---

## Sources

- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) (accessed 2026-03-18)
- [Agent Skills Specification — agentskills.io](https://agentskills.io/specification) (accessed 2026-03-18)
- [Agent Skills Open Standard Overview — inference.sh](https://inference.sh/blog/skills/agent-skills-overview) (accessed 2026-03-18)
- [Inside Claude Code Skills: Structure, prompts, invocation — Mikhail Shilkov](https://mikhail.io/2025/10/claude-code-skills/) (accessed 2026-03-18)
- [AGENTS.md — agents.md](https://agents.md/) (accessed 2026-03-18)
- [CLAUDE.md, AGENTS.md, and Every AI Config File Explained — DeployHQ](https://www.deployhq.com/blog/ai-coding-config-files-guide) (accessed 2026-03-18)
- [Claude Code Skills vs MCP vs Plugins: Complete Guide 2026 — Morph](https://www.morphllm.com/claude-code-skills-mcp-plugins) (accessed 2026-03-18)
- [Claude Code Plugins: Anthropic's Official Plugin Ecosystem — Groundy](https://groundy.com/articles/claude-code-plugins-anthropic-s-official-plugin-ecosystem/) (accessed 2026-03-18)
- [Agent Skills Are Spreading Hallucinated npx Commands — Aikido Security](https://www.aikido.dev/blog/agent-skills-spreading-hallucinated-npx-commands) (accessed 2026-03-18)
- [The Complete Guide to Agent Skills Installation Tools — AgentSkillsRepo](https://agentskillsrepo.com/news/the-complete-guide-to-agent-skills-installation-tools) (accessed 2026-03-18)
- [Skills-CLI Guide: Using npx skills to Supercharge Your AI Agents — Bo Liu, Medium](https://medium.com/@jacklandrin/skills-cli-guide-using-npx-skills-to-supercharge-your-ai-agents-38ddf3f0a826) (accessed 2026-03-18)
- [Vercel Launches Skills — "npm for AI Agents" — Dev Genius](https://blog.devgenius.io/vercel-launches-skills-npm-for-ai-agents-with-react-best-practices-built-in-452243ea5147) (accessed 2026-03-18)
- [Fabric — danielmiessler/Fabric on GitHub](https://github.com/danielmiessler/Fabric/blob/main/README.md) (accessed 2026-03-18)
- [Mastering Prompt Versioning — DEV Community](https://dev.to/kuldeep_paul/mastering-prompt-versioning-best-practices-for-scalable-llm-development-2mgm) (accessed 2026-03-18)
- [The 5 best prompt versioning tools in 2025 — Braintrust](https://www.braintrust.dev/articles/best-prompt-versioning-tools-2025) (accessed 2026-03-18)
- [Prompts as Software Engineering Artifacts — arXiv](https://arxiv.org/abs/2509.17548) (accessed 2026-03-18)
- [LangChain Hub — LangChain Blog](https://blog.langchain.com/langchain-prompt-hub/) (accessed 2026-03-18)
- [Versioning Published MCP Servers — modelcontextprotocol.io](https://modelcontextprotocol.io/registry/versioning) (accessed 2026-03-18)
- [Spec-Driven Development with GitHub Spec Kit — Microsoft Developer Blog](https://developer.microsoft.com/blog/spec-driven-development-spec-kit) (accessed 2026-03-18)
- [GitHub Spec Kit repository — github/spec-kit](https://github.com/github/spec-kit) (accessed 2026-03-18)
- [cc-sdd: Spec-driven development for AI agents — gotalab/cc-sdd](https://github.com/gotalab/cc-sdd) (accessed 2026-03-18)
- [Top 10 Claude Code Skills — Composio](https://composio.dev/content/top-claude-skills) (accessed 2026-03-18)
- [Top Multi-Agent Tools Compared: LangGraph, AutoGen, CrewAI — Amplework](https://www.amplework.com/blog/langgraph-vs-autogen-vs-crewai-multi-agent-framework/) (accessed 2026-03-18)
- [Semantic Kernel + AutoGen = Microsoft Agent Framework — Visual Studio Magazine](https://visualstudiomagazine.com/articles/2025/10/01/semantic-kernel-autogen--open-source-microsoft-agent-framework.aspx) (accessed 2026-03-18)
- [ADR GitHub Organization — adr.github.io](https://adr.github.io/) (accessed 2026-03-18)
- [CrewAI vs LangGraph vs AutoGen — OpenAgents Blog](https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared) (accessed 2026-03-18)

---

## Findings

### Prompt & Skill Packaging Systems

**The Agent Skills open standard (SKILL.md)**

Released by Anthropic in late 2025 and quickly adopted as a community-governed open standard (hosted at `github.com/agentskills/agentskills`), the Agent Skills format is the most directly relevant precedent for how swain packages its skill files.

A skill is a self-contained directory with a required `SKILL.md` file and optional subdirectories:

```
skill-name/
├── SKILL.md          # required: YAML frontmatter + markdown instructions
├── scripts/          # executable code agents can run
├── references/       # detailed docs loaded on demand
└── assets/           # templates, data files, static resources
```

The `SKILL.md` frontmatter defines `name` (required, used as the slash-command), `description` (required, the auto-invocation trigger), `license`, `compatibility`, `metadata` (arbitrary KV), and `allowed-tools`. The body is freeform markdown. Claude Code extends the base spec with additional fields: `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `hooks`, `model`, and `argument-hint`.

The key design principle is **progressive disclosure**:
1. Metadata only (~100 tokens): loaded at session start for all skills
2. Full SKILL.md body (<5000 tokens recommended): loaded when a skill is activated
3. Referenced files (scripts/, references/, assets/): loaded only when the agent needs them

This three-tier architecture minimizes context overhead while preserving full capability when invoked.

Cross-platform compatibility is broad: Claude Code, OpenAI ChatGPT and Codex CLI, Cursor, GitHub Copilot in VS Code, Windsurf, Gemini CLI, Goose, Roo Code, Trae, Amp, Factory, and others all support the same `SKILL.md` format. Platform-specific extensions (like Claude Code's `context: fork`) are additive and gracefully ignored by other platforms.

**Fabric (danielmiessler/fabric)**

Fabric's distribution model is different and older than the Agent Skills ecosystem. Patterns are stored as `system.md` files in `~/.config/fabric/patterns/<pattern-name>/`. The community contributes ~200+ patterns via Git. Installation is via `fabric --setup` which pulls the patterns directory. Users can create custom patterns in the same directory. The system supports aliasing so `summarize` invokes `fabric --pattern summarize`. There is no formal frontmatter schema; patterns are pure system prompts. Distribution is entirely git-based with no package registry.

**LangChain Hub**

LangChain Hub (now part of LangSmith) provides a community prompt registry where prompts are stored, versioned, and pulled into code via SDK (`langsmith.hub.pull("owner/name")`). Prompts are first-class versioned artifacts with commit history, branching, and staged deployment (dev/staging/prod environments pinned to specific prompt versions). The bidirectional sync pattern (pull to git, review in PR, push back) makes prompts reviewable as code without requiring them to live in the application repository. This is the most mature prompt-as-deployable-artifact model.

**Prompt libraries as frameworks (2025–2026 consensus)**

The field has converged on treating prompts not as text but as software artifacts: versioned, reviewed in PRs, tested in CI, and deployed through gates. Research published in late 2025 (arXiv:2509.17548) found that current practice remains largely ad-hoc (trial-and-error, rarely reused), but tooling is rapidly catching up. The dominant platforms are Langfuse, PromptLayer, Braintrust, and Agenta — all converging on immutable versions, branching, environment promotion, and evaluation integration.

---

### Agent Framework Distribution Models

**LangGraph / LangChain**

Python-first, installed via pip. The framework itself is runtime-dependent (Python). Agents are defined as code (graph nodes, edges, state schemas). Distribution is via Python packages. LangGraph Platform provides hosted deployment with persistence, streaming, and memory. The framework is not portable in the "runs anywhere as a file" sense — it requires Python runtime and LangChain dependencies.

**CrewAI**

Role-based, Python-first, lightweight. Deployable with minimal infrastructure. Adding A2A (Agent-to-Agent) protocol support in 2026. Distribution is via pip. Same portability constraints as LangGraph — requires runtime.

**AutoGen (Microsoft)**

Python and .NET. Conversational multi-agent patterns. Being merged with Semantic Kernel into a unified "Microsoft Agent Framework" (announced October 2025). Portable across Python and .NET runtimes. Deployed as packages. No "zero-install" story.

**Semantic Kernel**

Microsoft's most mature framework (27K+ GitHub stars). Supports C#, Python, Java. Plugin architecture promotes modular, composable agents. Plugins can be loaded at runtime, enabling "portable, reusable skill packages that provide domain expertise on demand." Distributed via NuGet, pip, Maven. Still runtime-dependent.

**Key observation:** None of the major agent frameworks have a "zero-install, drop a file" distribution model. They all require language runtimes and package managers. The Agent Skills spec (SKILL.md) is the only format that achieves true zero-runtime portability — it requires only a compatible AI tool that reads markdown files.

**The MCP (Model Context Protocol) distribution model**

MCP servers are distributed via npm under the `@modelcontextprotocol` namespace. The official registry at `modelcontextprotocol.io/registry` uses semantic versioning, `server.json` manifests, and requires npm public registry for JavaScript servers. The MCP SDK has spawned 6,700+ dependent projects. This is a strong precedent for using npm as the distribution channel for agent extensions. The Claude Code Plugin ecosystem bundles MCP server configurations into `plugin.json`-manifest packages alongside skills, hooks, and agents — a richer "all-in-one" distribution unit.

---

### Developer Decision-Support Tools

**GitHub Spec Kit**

The most directly comparable tool to swain. GitHub Spec Kit implements "Spec-Driven Development" (SDD) — the idea that polished specifications become the single source of truth, guiding AI agents to generate software reliably.

Structure: a `.specify/` folder with four plain markdown files:
- **Specification document** — what and why (functional requirements)
- **Technical plan** — how (frameworks, databases, architecture decisions)
- **Tasks breakdown** — phased implementation units
- **Constitution document** — non-negotiable organizational principles

Invoked via slash commands (`/specify`, `/plan`, `/tasks`) that drive agents through sequential phases. Distribution is via `uvx --from git+https://github.com/github/spec-kit.git specify init`.

Key difference from swain: Spec Kit is a one-time scaffold generator — it creates markdown files and exits. Swain is an ongoing lifecycle manager with artifact state tracking, phase transitions, and session-persistent alignment. Spec Kit is the scaffold; swain is the operating model.

**cc-sdd (gotalab)**

A community implementation of "Kiro-style" spec-driven development that supports Claude Code, Codex, Opencode, Cursor, GitHub Copilot, Gemini CLI, and Windsurf from a single skill package. Demonstrates that structured-requirements → design → tasks workflows can be packaged as a cross-platform skill.

**ADR tooling**

Architecture Decision Records (ADR) are the most established pattern for capturing decisions as markdown files committed to a repo. Tools like `adr-tools` (CLI for creating/linking ADRs) provide scaffolding but no lifecycle management. AWS and Azure both recommend ADRs in their Well-Architected Frameworks. The gap swain fills — tracking decision artifacts through lifecycle states, linking them hierarchically (Vision → Initiative → Epic → Spec), and integrating with session context — has no comparable prior art in the ADR space.

**No direct equivalent to swain found.** The closest cluster is: Spec Kit (spec scaffolding) + ADR tooling (decision capture) + LangChain Hub (prompt lifecycle) + task trackers (execution). Swain integrates all four concerns into a single, markdown-native, session-aware system.

---

### System Prompt as Application

**Examples in production**

OpenAI's ChatGPT ships built-in skills (discovered in December 2025 at `/home/oai/skills/`) for PDF processing, document handling, and spreadsheets — these are structured SKILL.md files embedded in the product, delivered as system prompt injections. The entire Claude Code bundled skill set (batch, debug, simplify, loop, claude-api, etc.) is implemented as prompt-based playbooks, not code — they "give Claude a detailed playbook and let it orchestrate the work using its tools."

Swain's skills (swain-design, swain-do, swain-doctor, swain-status, swain-session) follow exactly this pattern: complex applications delivered as structured system prompt injections via SKILL.md files.

**Limits of the pattern**

- **Context budget:** Skill descriptions are always loaded; full bodies only load on invocation. Claude Code enforces a dynamic budget (2% of context window, fallback 16,000 characters) for skill metadata. At high skill counts, descriptions are excluded.
- **No persistent state:** System prompts cannot maintain state across sessions without an external store. This is why swain-do relies on tk (ticket) as an external task tracker rather than encoding state in prompts.
- **Instruction following limits:** Research suggests frontier LLMs reliably follow ~150–200 instructions. Combined with system prompts consuming ~50 "slots," files should stay under 300 lines.
- **No versioning primitive:** The SKILL.md format has no built-in version field (the base spec puts it in `metadata.version`). Versioning must be handled externally (git tags, npm semver).
- **Security:** LLM-generated skills spreading hallucinated package references (the "slopsquatting" problem documented by Aikido Security in October 2025) demonstrate that skills with executable side-effects need human review. Pure-instruction skills (like swain's) carry no such risk.

**Prompt versioning maturity**

The field has converged on: extract prompts from code → store in versioned registry → deploy through environment gates → tie versions to production traces. For a markdown-native tool like swain, this translates to: git tags as the version primitive, CHANGELOG.md as the audit trail (swain-release already manages this), and the `metadata.version` field in SKILL.md frontmatter for runtime discovery.

---

### Package Manager Distribution

**The `skills` npm package and registry**

`npx skills <command>` provides access to 40,000+ marketplace skills across 10+ platforms (Claude, Cursor, GitHub Copilot, Codex, Windsurf, Antigravity, etc.). Installation: `npx skills add <owner/repo>`. The registry at skills.sh maintains a leaderboard of popular skills and supports installation from GitHub repos, not just npm packages. Skills are stored in platform-specific directories (`~/.claude/skills/`, `~/.codex/skills/`, etc.) with the same `SKILL.md` content.

**Alternative CLI tools for skill installation**

Four tools now compete in this space:

| Tool | Install | Focus |
|------|---------|-------|
| `npx skills` | no install needed | 40K+ marketplace skills, 10+ platforms |
| `npx add-skill` | no install needed | GitHub URLs, local paths, auto-detects agent |
| `openskills` | `npx openskills` | Claude Code-compatible format, generates AGENTS.md |
| `skillport` | `uv tool install skillport` | Enterprise, per-client filtering, MCP server |

**Claude Code Plugin marketplace architecture**

Plugins are the richer distribution unit: a `plugin.json` manifest in `.claude-plugin/` bundles skills, MCP configurations, hooks, subagents, and LSP servers into one installable package. Marketplaces are defined by a `marketplace.json` catalog and added via `/plugin marketplace add <source>`. Decentralized — anyone can host a marketplace. Supports GitHub repos, git URLs, local paths, and npm packages. 9,000+ plugins available as of February 2026.

**npm as universal distribution channel for agent tooling**

The convergence is unmistakable: Anthropic (Claude Code skills, MCP servers), OpenAI (Codex skills), Microsoft (Semantic Kernel plugins via NuGet/pip), and the open-source community are all using standard package managers for agent extension distribution. npm dominates the JavaScript/Node.js surface; pip for Python frameworks. The `npx`-without-install pattern (ephemeral execution) is particularly clean for scaffolding and install tools.

**swain's current model**

swain currently uses `npx skills` for self-distribution. This aligns with the dominant pattern. The `npx skills add anthropics/swain` flow (or equivalent) would give swain access to the 40K+ platform user base of the skills registry.

---

### Markdown-as-Interface Pattern

**The AGENTS.md / CLAUDE.md ecosystem (2025–2026)**

The convergence on markdown files as the primary agent configuration interface is now an industry standard, not a swain-specific pattern.

Key facts:
- `AGENTS.md` is stewarded by the Agentic AI Foundation under the Linux Foundation.
- 60,000+ open-source projects use `AGENTS.md`.
- Supported by: OpenAI Codex, Google Jules, GitHub Copilot, VS Code, Cursor, Zed, JetBrains Junie, Aider, Goose (Block), Devin, Windsurf, Factory, Warp, Semgrep, Augment Code.
- `CLAUDE.md` adds Claude-specific features (skills integration, sub-agent definition, MCP config) on top of the portable AGENTS.md base.
- Best practice: maintain AGENTS.md as single source of truth; CLAUDE.md references it (`@AGENTS.md`).

**Hierarchy and scoping**

All major tools implement multi-level discovery:
- Global: `~/.claude/CLAUDE.md` or `~/.config/tool/`
- Project root: `./AGENTS.md`, `./CLAUDE.md`
- Subdirectory: nested files, closest takes precedence (monorepo support)
- Enterprise: managed settings deployed org-wide

Claude Code adds a fourth layer: plugin-scoped skills that namespace as `plugin-name:skill-name`, preventing conflicts.

**Tool-specific formats and their limits**

| File | Scope | Portability |
|------|-------|-------------|
| `AGENTS.md` | Universal | Best — 60K+ projects, Linux Foundation stewardship |
| `CLAUDE.md` | Claude-specific | Good within Claude ecosystem; `@AGENTS.md` pattern enables both |
| `.cursor/rules/*.mdc` | Cursor | Not portable; activation modes (Always/Auto/Manual) not universal |
| `.github/copilot-instructions.md` | Copilot | GitHub-scoped; not portable |
| `GEMINI.md` | Gemini CLI | Not portable |

**Practical limits**

Windsurf enforces hard limits: 6,000 characters per file, 12,000 characters combined. Research suggests LLMs reliably follow 150–200 instructions total. Files exceeding ~300 lines begin degrading agent compliance. The right architecture is: put core invariants in AGENTS.md (portable, concise), put tool-specific extensions in `CLAUDE.md`, and offload detailed reference material to skill directories loaded on demand.

**Swain's current pattern (`@AGENTS.md` from `CLAUDE.md`) is best practice.** The Linux Foundation stewardship of `AGENTS.md` validates the bet on this file as the stable, portable anchor.

---

### Progressive Enhancement Examples

No examples were found of AI tools explicitly using the web-development "progressive enhancement" framing, but the underlying pattern is well-established in practice.

**The Agent Skills progressive disclosure model**

The Agent Skills spec explicitly encodes a three-tier disclosure model (metadata → instructions → resources). This is structurally identical to progressive enhancement: the agent always has the skill's name and description (minimal viable information), loads full instructions when needed (enhanced mode), and loads referenced files only on demand (maximum capability mode). A skill designed this way works in any context that supports `SKILL.md` format, with full capability only on the home platform.

**Claude Code bundled vs. project vs. personal skills**

Claude Code itself demonstrates surface-aware capability degradation: bundled skills (batch, simplify, loop) are always available; project skills are available only in that project; personal skills are available everywhere for that user; plugin skills are available only where the plugin is enabled. A skill that works across all surfaces needs to avoid dependencies on project-local MCP servers or scripts.

**CLI-based tools across IDEs**

Continue.dev (open-source) runs in VS Code and JetBrains with a companion CLI for terminal workflows — the same assistant adapts its interface to the surface it's on. This is the closest explicit example of progressive enhancement for AI tools: full capability in the IDE, reduced-but-useful capability in the terminal.

**Cross-platform agent skills (cc-sdd, add-skill)**

The `add-skill` tool explicitly auto-detects the current agent platform and installs the same SKILL.md to the right location. The `cc-sdd` skill set works across 7 platforms from a single source. Both demonstrate the "write once, run anywhere" ideal for markdown-as-interface tools.

**Where swain fits**

Swain's skills invoke slash commands that are specific to Claude Code's Skill tool. On other platforms that support SKILL.md but not the full Claude Code skill-chaining model, swain skills would fall back to providing the markdown instructions as plain context — a useful degraded mode. The session startup pattern (swain-doctor → swain-session) is the most Claude-Code-specific behavior; all other skills (swain-design, swain-do, swain-status) could work in degraded form on any platform that reads SKILL.md.

---

## Key Takeaways

1. **The Agent Skills spec (SKILL.md) is the right distribution primitive.** It is now a Linux Foundation-adjacent open standard with 60K+ project adoption across 14+ platforms. Swain's current SKILL.md packaging is not ahead of the curve — it is aligned with the curve. The progressive disclosure architecture (metadata → instructions → referenced files) is the canonical model for token-efficient skill packaging.

2. **npm/npx is the dominant distribution channel for agent extensions.** The `npx skills add` pattern (no install required, installs from GitHub or registry) is the right model for swain distribution. Swain should ensure it can be installed via `npx skills add cristoslc/swain` (or equivalent) and list itself in the skills.sh registry with a strong description that enables auto-invocation.

3. **No prior art exists for swain's lifecycle management scope.** GitHub Spec Kit (SDD scaffolding), ADR tooling (decision capture), LangChain Hub (prompt lifecycle), and task trackers each cover one quadrant. Swain integrates all four into a session-aware, artifact-state-tracking, alignment-enforcing system. The closest analog — `cc-sdd` — is a shallow implementation of just the spec-scaffolding concern.

4. **The AGENTS.md + CLAUDE.md layering pattern is now best practice.** Swain's existing `CLAUDE.md @AGENTS.md` pattern is exactly what the industry has converged on. The Linux Foundation stewardship of AGENTS.md validates it as the stable, portable anchor for the next several years. Swain's core invariants should live in AGENTS.md; Claude-specific extensions (skill routing, session startup, superpowers chaining) belong in CLAUDE.md.

5. **Prompt versioning should be treated as a first-class concern.** The industry consensus (Braintrust, Langfuse, PromptLayer) is immutable versions + environment promotion + git as source of truth. Swain's `metadata.version` field in SKILL.md frontmatter, combined with swain-release git tagging, already provides the version primitive. The gap is: no mechanism for pinning a project to a specific swain skill version (all projects pick up the global `~/.claude/skills/swain-*/` install). A plugin-based distribution model (plugin.json bundling all swain skills) would enable per-project version pinning and solve the version stability problem.
