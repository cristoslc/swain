# Synthesis: Docker Agent

**Trove:** docker-agent
**Sources:** 3 (Docker docs — overview, best practices, tutorial)
**Date:** 2026-03-17

---

## Key Findings

Docker Agent (experimental, bundled with Docker Desktop 4.63+) is an open-source YAML-defined multi-agent framework that runs locally against any LLM provider. It is positioned as "the coordination layer" — you define agents with roles; Docker Agent handles delegation, tool access, and execution. The OCI packaging model lets teams share agent configurations like container images.

---

## Theme 1: YAML-first, provider-agnostic configuration

Every agent is a YAML stanza: `model`, `description`, `instruction`, `toolsets`, `sub_agents`. Model strings use `provider/model-id` notation (`anthropic/claude-sonnet-4-5`, `openai/gpt-5-mini`) — you switch providers by changing one line.

```yaml
agents:
  root:
    model: anthropic/claude-sonnet-4-5
    instruction: |
      ...
    sub_agents: [helper]
  helper:
    model: openai/gpt-5-mini
    instruction: |
      ...
```

Agents do **not** share context — each has its own context window. This is an explicit design choice, not a limitation. [docker-agent-overview]

---

## Theme 2: Toolsets as capability grants

Agents are capability-minimal by default. You grant tools explicitly via `toolsets`:

| Toolset | What it gives |
|---------|--------------|
| `filesystem` | Read/write files in working directory |
| `shell` | Execute commands |
| `todo` | Track multi-step progress |
| `think` | Internal reasoning scratch space |
| `fetch` | Fetch URLs |
| `mcp ref: docker:duckduckgo` | Web search via Docker MCP Gateway |

Built-in tools also include memory and task delegation. External tools are added via MCP server references. [docker-agent-overview, docker-agent-tutorial-coding-agent]

---

## Theme 3: Coordinator pattern as the recommended team structure

The canonical multi-agent pattern is a **coordinator root + specialist sub-agents**:

- Root understands the full task and delegates
- Specialists are focused and do not coordinate with each other
- Root retains final control and can loop (e.g., send back to editor if reviewer fails)

Documented example: `root (coordinator) → writer → editor → reviewer`. Each agent has a single responsibility; the coordinator sequences them and handles retries. [docker-agent-best-practices]

The docs distinguish two delegation mechanisms:
- **`sub_agents`** — root delegates discrete tasks and waits for results (root stays in control)
- **handoffs** — agents transfer full control to each other (referenced but not detailed in captured pages)

---

## Theme 4: Instructions as the primary quality lever

The docs are explicit: "Generic instructions produce generic results." Well-structured instructions include:

1. A named **workflow** (Analyze → Examine → Modify → Validate)
2. **Constraints** (NEVER skip tests; NEVER modify generated/ directory)
3. **Project-specific commands** (the exact CLI commands for this stack)
4. **Scope preservation** for documentation agents (don't transform a 90-line how-to into a 200-line tutorial)

The `add_date` and `add_environment_info` flags inject current date and OS context automatically. [docker-agent-tutorial-coding-agent, docker-agent-best-practices]

---

## Theme 5: Context management is a first-class operational concern

Two recurring patterns for keeping agents from hitting context limits:

1. **Redirect large outputs to files** — `command > output.log 2>&1` then read the file. The Read tool auto-truncates to 2000 lines. Never pipe large outputs directly into the agent's context. [docker-agent-best-practices]

2. **RAG scope narrowing** — index only the directories an agent actually needs, not the full repo. Combine with batching (`batch_size: 50`, `max_embedding_concurrency: 10`) and BM25 for exact-match lookup (function names, identifiers) without API calls. [docker-agent-best-practices]

---

## Theme 6: Model tiering by task complexity

Consistent pattern across all three sources: use large models for reasoning-heavy work, small models for tool execution:

| Role | Recommended model | Why |
|------|------------------|-----|
| Coordinator / planner | Sonnet, GPT-5 | Complex reasoning, judgment |
| Writer / editor | Sonnet, GPT-5 | Judgment about content quality |
| Validator / reviewer | Haiku, GPT-5 Mini | Runs commands, checks errors — no reasoning needed |
| Documentation researcher | Haiku, GPT-5 Mini | Search + fetch, cost-sensitive |

[docker-agent-best-practices, docker-agent-tutorial-coding-agent]

---

## Theme 7: OCI packaging for team distribution

Agent configs are packaged as OCI artifacts:

```bash
docker agent share push ./team.yaml myusername/team
docker agent share pull myusername/team
```

Works with Docker Hub or any OCI-compatible registry. Creates the repository on first push. This means agent teams are versioned and distributable the same way container images are. [docker-agent-overview]

---

## Points of Agreement

- Agents don't share context — isolation is a feature, not a bug
- Structured YAML instructions outperform open-ended prompts
- Smaller models for mechanical tasks save cost and latency
- File-based output buffering prevents context overflow on large command outputs

---

## Points of Disagreement / Open Questions

- The docs recommend `sub_agents` (coordinator pattern) for most cases, but mention "handoffs" for transfer-of-control patterns without fully documenting them in the captured pages — the distinction matters for designing workflows where specialists need to communicate bidirectionally
- RAG configuration is mentioned but the full RAG reference page was not available (404)

---

## Gaps

- **Configuration reference** — the full `config-reference` page was 404; field-level documentation for all YAML keys is missing from this trove
- **MCP Gateway integration** — `docker:duckduckgo` MCP reference is shown but the MCP Gateway docs were not captured
- **Handoffs mechanism** — referenced but not detailed
- **`docker agent new`** — AI-powered team generation mentioned but not documented in captured pages
- **Editor / IDE integration** — mentioned as a capability but not documented here
- **Security model** — no detail on what permissions agents have, sandboxing, or audit trails (contrast with Intercom's production console approach in `intercom-claude-code-plugins`)
