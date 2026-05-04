# Skills as Tools — Synthesis

This trove surveys the architectural shift from injecting methodology as text-in-context (skills) to delivering it as executable tools (MCP servers, CLIs, ACP harnesses). It is the research foundation for exploring what swain v2 would look like as a standalone tool rather than a skill overlay.

## Key Findings

### The Enforcement Gap Is Structural

Skills are advisory by nature — markdown files injected into an agent's context window. They say "should" but cannot say "must." The agent can ignore them, skip steps, or drift from the methodology when context pressure is high. [ai-coding-agents-deconstructed] identifies this as the fundamental weakness of prompt-based governance: plan mode is just a prompt, and the agent can write code in plan mode if it wants to.

Tools, by contrast, enforce deterministically. An MCP tool handler is arbitrary code. It can refuse invalid state transitions, validate inputs against schema, enforce ordering constraints, and persist state across sessions. The agent cannot bypass code — only reason about whether to call it.

### The Industry Is Converging on Hybrid Architecture

Every major 2026 analysis agrees: the answer is not "skills or MCP" but "all three layers." [skill-vs-mcp-comparisons] synthesizes five independent sources into a consistent framework:

- **Memory** (CLAUDE.md, project context): ambient knowledge.
- **Skills** (SKILL.md files): methodology, procedure, domain expertise.
- **MCP servers**: external connectivity and deterministic enforcement.

The skill layer provides zero-friction ergonomics (markdown files, progressive disclosure, cross-platform portability). The MCP layer provides hard guarantees (database persistence, state machines, multi-client support). They compose: a skill teaches the approach, the MCP server enforces the rules.

### Production MCP Servers Demonstrate Viability

SPIKE-030 identified two production MCP servers implementing methodology enforcement:

- **lifecycle-mcp**: 22 tools, 6 handler modules, SQLite persistence, requirement state machines, GitHub issue sync.
- **spec-workflow-mcp**: sequential phase enforcement (Requirements → Design → Tasks), approval gates, cross-tool support.

These prove that methodology-as-MCP works at production scale. The protocol places no ceiling on handler complexity.

### ACP and CLI Tools Form a Third Path

Beyond MCP, the ACP (Agent Client Protocol) ecosystem provides another tool-over-skill pattern. [acpx-harness-adapter] demonstrates acpx — a standalone CLI that orchestrates coding agent sessions over a structured protocol instead of PTY scraping or skill injection. Key properties:

- Headless execution with permission profiles.
- Sessions survive gateway restarts.
- Cross-harness compatibility (Pi, Claude Code, Codex, Gemini CLI, OpenCode).
- Each agent gets its own workspace with isolated conversations.

This pattern — a CLI tool that orchestrates agents rather than injecting text into them — is directly relevant to swain v2's design space.

### Token Economics Favor Skills Today, Tools Tomorrow

The MorphLLM analysis [morphlm-skills-mcp-plugins] quantifies the token trade-off:

| Extension | Base Cost | Loaded Cost |
|-----------|-----------|-------------|
| Skill | 30-50 tokens | <5k tokens |
| MCP Server | 1-50k tokens | Same |

But Anthropic's Tool Search feature reduces MCP overhead by ~85%. And the [mcp-protocol-roadmap] confirms that reference-based results and streaming improvements are active 2026 priorities. As these land, MCP's token disadvantage narrows to negligible.

## Points of Agreement

1. **Advisory != enforcement.** All sources agree that skills cannot deterministically enforce methodology.
2. **Hybrid is the near-term answer.** Skills for ergonomics, MCP for persistence and enforcement.
3. **Cross-platform portability favors protocols.** Skills have broad adoption (Claude, Codex, Gemini CLI). MCP has broader reach (any MCP client). Tools win on reach.
4. **Deterministic enforcement needs code.** Lifecycle state machines belong in MCP tools, not in skill instructions.
5. **The trajectory is MCP-primary.** As Sampling with Tools matures, orchestration migrates from skill text to server code.

## Points of Disagreement

1. **Is context bloat a deal-breaker?** The "MCP is dead" argument centers on token overhead. The rebuttal: Tool Search already solves 85% of it, and the 2026 roadmap addresses the rest. For methodology servers with 10-15 lean tools, overhead is already acceptable.
2. **Can MCP Prompts replace slash commands?** In theory, MCP Prompts surface as `/mcp__swain__design`. In practice, the UX gap (skill ergonomics vs tool workflow) is real but narrowing as clients improve.
3. **Does auth complexity kill adoption?** Skills are zero-setup (markdown files). MCP needs process configuration. For solo developers, the added friction may outweigh the enforcement benefit. For teams, the enforcement benefit justifies the setup cost.

## Gaps

1. **No direct ACP methodology integration explored.** The acpx pattern (headless CLI orchestrating sessions) hasn't been applied to methodology enforcement. This is uncharted territory.
2. **No comparison of MCP vs CLI as delivery mechanism.** This trove covers MCP servers as tools. CLI tools as methodology enforcers (e.g., a `swain-do` binary that agents invoke for task tracking) are a separate design space not yet researched.
3. **No measurement of enforcement effectiveness.** Does deterministic enforcement through MCP actually produce better outcomes than advisory skill guidance? No empirical studies found.
4. **No exploration of MCP Apps (interactive UI).** The Jan 2026 MCP Apps specification (interactive tool responses like dashboards, forms, visualizations) could fundamentally change the tool UX but is not yet widely adopted.

## Relevance to Swain v2

The research establishes that a tool-based swain is not merely viable — it's an active industry direction. The specific forms (CLI-only, MCP-only, hybrid, ACP-integrated) remain design decisions. The trove provides the evidence base for a SPIKE exploring these options.
