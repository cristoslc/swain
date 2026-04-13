---
title: "Retro: Recent Research and Infrastructure Work"
artifact: RETRO-2026-04-07-research-infra
track: standing
status: Active
created: 2026-04-07
last-updated: 2026-04-07
scope: "Recent trove creation and infrastructure updates including Harvey Spectre research"
period: "2026-03-30 — 2026-04-07"
linked-artifacts:
  - SPEC-293
---

# Retro: Recent Research and Infrastructure Work

## Summary
This period focused on expanding the project's research foundation through the `swain-search` skill and finalizing the `Untethered Operator` infrastructure. The primary highlight was the creation of the `harvey-spectre` trove, detailing a cloud-native agent runtime.

## Research Process Analysis

### Tooling & Capability Chain
The research for the `harvey-spectre` trove demonstrated a high-fidelity extraction pipeline:
1. **Discovery:** Used `MCP_DOCKER_browser_navigate` to access the source (X.com).
2. **Extraction:** Employed `MCP_DOCKER_browser_snapshot`. The accessibility tree provided by the snapshot was critical for bypassing the fragmented nature of social media DOMs, allowing for a clean, linear extraction of the full article text.
3. **Normalization:** Applied the `swain-search` skill's normalization patterns to convert raw social media content into a structured markdown format, emphasizing architectural primitives over chronological feed noise.
4. **Verification:** Computed SHA-256 hashes for the normalized content to ensure provenance and prevent drift during future refreshes.
5. **Persistence:** Used the dual-commit stamping pattern to pin the trove version in `manifest.yaml`.

### Learning for Future Agents
- **Fidelity over Summarization:** When capturing architectural insights, using browser snapshots (accessibility trees) is vastly superior to using "summarize page" tools. The latter often strips the nuanced technical primitives (like the "Harness" vs "Wrapper" distinction) that are essential for a research trove.
- **Trove Routing:** The "Prior Art Check" (Phase 1/2) prevented duplication by scanning existing troves before initializing `harvey-spectre`.
- **Provenance:** The dual-commit pattern (`Commit A` for content $\rightarrow$ `Commit B` for hash stamp) creates a reliable audit trail that allows artifacts to reference a specific version of the research.

## Reflection

### What went well
- The `swain-search` workflow effectively transitioned from a raw URL to a thematic synthesis.
- The use of `MCP_DOCKER` tools allowed for reliable interaction with modern, dynamic web pages.

### What was surprising
- The level of detail available in a single "Article" post on X, which provided a comprehensive blueprint of a production agent system.

### Patterns Observed
- A clear convergence toward **Cloud-Native Agent Runtimes**. Research across `harvey-spectre` and `agentic-coding-dual-modes` shows a systemic shift away from "desktop-first" agents to "durable run" architectures to solve for security and organizational boundaries.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| High-fidelity extraction | Pattern | Prefer browser snapshots/accessibility trees over LLM page summaries for technical research |
| Durable Run Architecture | Observation | Cloud-native runtimes are required for enterprise-scale agent deployment (Security/Isolation) |
| dual-commit stamp | Process | Ensures referential integrity between artifacts and evolving troves |
