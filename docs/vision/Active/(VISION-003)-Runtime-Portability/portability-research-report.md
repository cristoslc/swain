# Swain Everywhere — Portability Research Report

**Date:** 2026-03-18
**Author:** Agent (Opus 4.6)
**For:** cristos — morning review
**Parent:** VISION-003 (Swain Everywhere), INITIATIVE-014 (Cross-Surface Portability)

---

## Executive Summary

Swain is better positioned for cross-surface portability than expected. The three conventions swain already uses — AGENTS.md, SKILL.md, and markdown artifacts — have become industry standards governed by the Linux Foundation. The ecosystem has converged on exactly the patterns swain bet on. The main work is not reinvention but **packaging and layering**.

**Verdict: Three-phase rollout, starting with what already works.**

---

## The Big Picture

Four research troves (23–28 sources each, 100+ total) investigated Claude web/desktop extensions, agent runtime compatibility, MCP as a distribution layer, and portable framework patterns. Three spikes synthesized the findings:

| Spike | Question | Verdict |
|-------|----------|---------|
| SPIKE-028 | Can Claude web/desktop deliver swain's value? | **Conditional Go** — read/advisory via web, full via Desktop Code tab, partial via MCP |
| SPIKE-029 | Is there a common substrate across runtimes? | **Go** — AGENTS.md + MCP + SKILL.md cover 6+ runtimes today |
| SPIKE-030 | Can MCP serve as swain's distribution layer? | **Conditional Go** — hybrid (skills + MCP) is strongest, not MCP-only |

---

## What We Learned

### 1. Swain's existing conventions ARE the emerging standards

- **AGENTS.md** is now a Linux Foundation standard with 60K+ repo adoption. Every major runtime reads it natively (Codex, OpenCode, Cursor, Windsurf, Copilot, Gemini CLI). Claude Code is the outlier — it uses CLAUDE.md, but swain's `@AGENTS.md` include pattern bridges this.

- **SKILL.md** is the Agent Skills open standard, supported by 14+ platforms. Swain's `.agents/skills/` directory is the emerging cross-runtime discovery path — OpenCode and Gemini CLI both prioritize it.

- **MCP** is universal. Every major runtime except Aider supports it in production. One MCP server works across Claude Code, Claude Desktop, VS Code, Cursor, Windsurf, JetBrains, and more.

**Implication:** Swain doesn't need to reinvent its packaging. It needs to produce the right *bundles* from its existing source.

### 2. The hybrid model is the right architecture

Going MCP-only would lose skill chaining, inline context injection, and zero-friction installation. Going skills-only keeps the current Claude Code lock-in. The answer is both:

- **Skills** = orchestration layer (how Claude should reason, what methodology to follow)
- **MCP server** = persistence layer (artifact state in SQLite, deterministic transition enforcement, structured queries)

This is exactly the architecture Claude Code's plugin system was designed for. A `plugin.json` bundles both in a single installable artifact.

### 3. Claude web is advisory-only; Claude Desktop bridges the gap

- **Claude web** can deliver swain's decision-support *patterns* via Project Instructions + knowledge base. A custom MCP Connector can add artifact state queries. But it cannot create files, run scripts, or execute agentic loops. Advisory mode only.

- **Claude Desktop Chat tab** can use a Desktop Extension (.mcpb) packaging swain's MCP server with local filesystem access. Richer than web — can read and write artifacts locally.

- **Claude Desktop Code tab** is full Claude Code. Swain already works there.

### 4. No prior art for swain's scope

GitHub Spec Kit covers spec scaffolding. ADR tools cover decision capture. LangChain Hub covers prompt lifecycle. Task trackers cover execution. **No existing tool integrates all four into a session-aware, artifact-state-tracking, alignment-enforcing system.** The closest analog (cc-sdd) is a shallow implementation of just the spec concern. Swain is genuinely novel in scope.

---

## Recommended Phased Approach

### Phase 1: "Already Works" (0–2 weeks)

**Goal:** Make swain discoverable and usable across runtimes that read AGENTS.md and SKILL.md — with zero code changes.

Actions:
- Ensure AGENTS.md contains swain's core governance rules (already done)
- Verify `.agents/skills/` contains all swain skills (already done)
- Test swain discovery in OpenCode and Gemini CLI (likely works today)
- Register swain in the skills.sh marketplace for broader discovery
- Document the degraded experience: what works, what doesn't, per runtime

**What users get:** Swain's instructions as context. No skill chaining, no session management, no automated transitions — but the artifact model, lifecycle rules, and decision-support patterns are available as plain markdown guidance.

### Phase 2: "Swain MCP Server" (2–6 weeks)

**Goal:** Build a swain MCP server that provides the artifact lifecycle engine, orchestration, and methodology loading as portable MCP primitives.

Actions:
- Build `swain-mcp` server with 10–15 Tools + Prompts + Resources:
  - **Tools:** `artifact_list`, `artifact_read`, `artifact_create`, `lifecycle_transition`, `lifecycle_status`, `chart_query`, `status_dashboard`, `tk_query`, `tk_update`, `load_methodology` (the portable skill-chaining mechanism)
  - **Prompts:** `design`, `do`, `status`, `session` (surfaced as `/mcp__swain__*` slash commands — direct analog of current skill invocation)
  - **Resources:** `swain://definitions/{type}`, `swain://templates/{type}`, `swain://artifacts/{id}`, `swain://chart` (reference materials available via @ mention)
- Back with SQLite for persistent state (proven pattern from lifecycle-mcp)
- Bundle as Claude Code plugin (`plugin.json` with skills + MCP config)
- Package as Desktop Extension (.mcpb) for Claude Desktop Chat tab
- Publish as npm package for any MCP client
- Language: either TypeScript or Python — both work in plugins (the manifest just specifies the command to run; plugin system is language-agnostic for the MCP server component)

**What users get:** Artifact lifecycle enforcement across any MCP-compatible client. Methodology loading via `load_methodology` tool replicates skill chaining portably. MCP Prompts provide the `/swain-design` experience in any client that supports them. Claude Code users get skills + MCP (best of both); everyone else gets MCP-only (still powerful).

### Phase 3: "Claude Web Project" (4–8 weeks, can overlap with Phase 2)

**Goal:** Package swain's decision-support patterns for Claude web users.

Actions:
- Create a "Swain Project" template:
  - Project Instructions encoding artifact conventions, lifecycle rules, decision-support methodology
  - Knowledge base files: artifact templates, ADR playbooks, lifecycle reference
- If Phase 2's MCP server is deployed as a remote endpoint, register as a custom Connector for artifact state queries
- Document the advisory-mode limitations clearly

**What users get:** Swain's thinking patterns in Claude web conversations. Friends and colleagues can use a shared Project (Team/Enterprise) or copy the instructions into their own. No enforcement, no automation — but the structured thinking is available.

### Phase 4: "Per-Runtime Bundles" (8+ weeks, only if demand warrants)

**Goal:** Produce optimized bundles for specific runtimes.

Actions:
- Gemini CLI extension (MCP + GEMINI.md context + commands)
- Copilot plugin (MCP + agents + skills + hooks)
- Standalone framework documentation (for runtimes with no extension model)

**What users get:** First-class swain experience in their preferred runtime. But only build this if Phase 1–2 adoption signals demand it.

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| MCP spec instability (registry in preview) | Medium | Build against stable 2025-11-25 spec; avoid registry-dependent distribution until GA |
| Token overhead in non-Claude-Code clients | Medium | Keep MCP tool count under 15; design tool descriptions for token efficiency |
| Claude web Connectors too limited for write ops | Low | Accept advisory-only mode for web; don't fight the platform |
| Maintenance burden of N runtime bundles | High | Phase 4 is optional; only build bundles with proven demand |
| AGENTS.md standard drift | Low | Linux Foundation governance; swain's patterns already aligned |
| Skill chaining authority gap (tool results vs system prompt) | Low | Frontier models follow tool-returned instructions reliably; Sampling resolves when available |

---

## Decision Points for the Operator

1. **Phase 1 is free.** Swain's existing packaging is already compatible with multiple runtimes. The only work is testing and documentation. Recommend proceeding immediately.

2. **Phase 2 is the strategic investment.** The MCP server is the core portability asset. It determines whether swain can offer more than advisory-mode instructions on non-Claude-Code surfaces. The key decision: **TypeScript or Python for the MCP server?** TypeScript aligns with Claude Code plugins and .mcpb Desktop Extensions. Python aligns with FastMCP's ergonomic DX and swain's existing specgraph Python package.

3. **Phase 3 depends on your own Claude web usage.** If you'd use swain's patterns in Claude web today, the Project template is low-effort and immediately valuable. If you primarily use Claude Code, defer this.

4. **Phase 4 should wait for signal.** Don't build Gemini CLI extensions or Copilot plugins until someone (including you) actually wants them.

---

## Artifacts Created in This Session

| Artifact | Type | Status | Path |
|----------|------|--------|------|
| VISION-003 | Vision | Active | `docs/vision/Active/(VISION-003)-Runtime-Portability/` |
| INITIATIVE-014 | Initiative | Active | `docs/initiative/Active/(INITIATIVE-014)-Cross-Surface-Portability/` |
| SPIKE-028 | Research Spike | Active | `docs/research/Active/(SPIKE-028)-Claude-Web-Desktop-Extension-Model/` |
| SPIKE-029 | Research Spike | Active | `docs/research/Active/(SPIKE-029)-Cross-Runtime-Portability-Substrate/` |
| SPIKE-030 | Research Spike | Active | `docs/research/Active/(SPIKE-030)-MCP-as-Distribution-Layer/` |

**Research troves:**
- `docs/troves/claude-web-desktop-extensions.md` (297 lines, 23 sources)
- `docs/troves/agent-runtime-extensions.md` (317 lines, 28 sources)
- `docs/troves/mcp-distribution-layer.md` (340 lines, 23 sources)
- `docs/troves/portable-framework-patterns.md` (267 lines, 26 sources)

---

## Operator Feedback & Resolutions

**Phase 1 — "are we not already there?"**
Yes. You've already used swain in Copilot and OpenCode. Phase 1 is documentation + re-testing on current versions (Gemini CLI untested, OpenCode needs retest). Epic created to track.

**Phase 2 — "why can't MCP provide skill chaining?"**
Corrected. SPIKE-030 v2 analysis confirms MCP CAN replicate skill chaining via: (1) `load_methodology` tool returning instructional text, (2) MCP Prompts as methodology templates surfaced as slash commands, (3) Sampling with Tools for server-controlled orchestration (when client support arrives). The original report understated MCP's capability. Architecture updated to hybrid-now, MCP-primary-later.

**Language — "Do plugins work with python?"**
Yes. Plugins are language-agnostic — the `plugin.json` manifest just specifies the command to run. TypeScript and Python both work. Python has FastMCP ergonomics + alignment with swain's existing specgraph package. TypeScript has stronger .mcpb tooling.

## Next Steps

- [x] Review report and spike verdicts
- [x] Proceed with Phase 1
- [x] Create Epics for Phase 1 and Phase 2
- [x] Decide Phase 2 MCP server language → **Python** (FastMCP ergonomics + specgraph reuse)
- [ ] Scope Phase 2 tool/prompt/resource set (draft in Epic)
