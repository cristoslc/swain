---
title: "Mermaid Rendering for Chat"
artifact: SPEC-294
track: implementable
status: Active
author: cristos
created: 2026-04-07
last-updated: 2026-04-07
priority-weight: medium
type: feature
parent-epic: [EPIC-071](../../../epic/Active/(EPIC-071)-Project-Bridge-Kernel/(EPIC-071)-Project-Bridge-Kernel.md)
parent-initiative: [INITIATIVE-018](../../../initiative/Active/(INITIATIVE-018)-Remote-Operator-Interaction/(INITIATIVE-018)-Remote-Operator-Interaction.md)
linked-artifacts:
depends-on-artifacts:
  - [SPEC-293](../(SPEC-293)-Output-Shaping-For-Chat/(SPEC-293)-Output-Shaping-For-Chat.md)
addresses:
evidence-pool:
source-issue:
swain-do: required
---

# Mermaid Rendering for Chat

## Problem Statement

When agents emit Mermaid diagrams (flowcharts, sequence diagrams, class diagrams, etc.), the raw Mermaid code is sent to the chat adapter as a code block. Operators see unreadable syntax instead of rendered visual diagrams, reducing comprehension and requiring manual copy-paste to external renderers.

## Desired Outcomes

Operators see rendered Mermaid diagrams as images in the chat interface. The project bridge automatically detects Mermaid code blocks, renders them to PNG/SVG, and attaches the rendered image to the chat message alongside or instead of the raw code.

## External Behavior

**Inputs:**
- Agent output containing Mermaid code blocks (fenced with \`\`\`mermaid) from the runtime adapter via NDJSON `agent_output` events.

**Outputs:**
- Chat messages with rendered Mermaid images (PNG or SVG) attached as file uploads or inline images, depending on chat platform capabilities.
- Optional: Raw Mermaid code preserved in a collapsible section or separate code block.

**Preconditions:**
- Mermaid rendering CLI tool (`mmdc` from mermaid-cli) is installed and available in PATH, or a configured rendering service endpoint is reachable.
- Project bridge config has `mermaid_rendering: enabled`.

**Postconditions:**
- Mermaid code blocks are transformed to images before being sent to the chat adapter.
- Original Mermaid code is optionally preserved for reference.

**Constraints:**
- Rendering is asynchronous — the project bridge does not block the message pipeline waiting for render completion.
- Failed renders (invalid Mermaid syntax, tool unavailable) fall back to sending raw code with a warning note.
- Image size is constrained to chat platform limits (configurable max dimensions).

## Acceptance Criteria

1. **Given** the project bridge receives agent output with a valid Mermaid code block, **when** mermaid rendering is enabled, **then** the project bridge renders the diagram to an image and attaches it to the chat message.

2. **Given** the project bridge renders a Mermaid diagram, **when** the render succeeds, **then** the chat message includes the rendered image and optionally the raw Mermaid code.

3. **Given** the project bridge receives invalid Mermaid syntax, **when** rendering is attempted, **then** the project bridge sends the raw code with a warning that rendering failed.

4. **Given** the mermaid CLI (`mmdc`) is not installed, **when** the project bridge starts, **then** it logs a warning and disables mermaid rendering (falls back to raw code).

5. **Given** multiple Mermaid code blocks in a single agent output, **when** rendering is enabled, **then** each block is rendered to a separate image and all are attached to the chat message.

6. **Given** a chat platform with file upload limits, **when** a rendered Mermaid image exceeds the size limit, **then** the project bridge scales the image down or falls back to sending raw code.

## Verification

| Criterion | Evidence | Result |
|-----------|----------|--------|
| 1 | Integration test: test_mermaid_render_single_diagram | Pending |
| 2 | Integration test: test_mermaid_render_with_fallback_code | Pending |
| 3 | Integration test: test_mermaid_invalid_syntax_handling | Pending |
| 4 | Integration test: test_mermaid_cli_missing_graceful_degradation | Pending |
| 5 | Integration test: test_mermaid_render_multiple_diagrams | Pending |
| 6 | Integration test: test_mermaid_image_size_constraint | Pending |

## Scope & Constraints

**In scope:**
- Mermaid code block detection in agent output (regex or parser-based).
- Integration with `mmdc` CLI or alternative rendering service.
- Image attachment to chat messages via the chat adapter's file upload capability.
- Error handling and fallback to raw code.
- Configuration options for enabling/disabling, image format (PNG/SVG), size limits.

**Out of scope:**
- Support for other diagram types (PlantUML, Graphviz) — future enhancement.
- Interactive diagram editing or modification after rendering.
- Caching of rendered diagrams (future optimization).

## Implementation Approach

1. **Detection:** Add a Mermaid detector to the output shaping pipeline (from SPEC-293) that identifies \`\`\`mermaid code blocks using regex.

2. **Renderer:** Create a `MermaidRenderer` class that:
   - Spawns `mmdc` as a subprocess with the Mermaid code as input.
   - Captures the rendered PNG/SVG output.
   - Handles errors (invalid syntax, missing CLI) gracefully.

3. **Integration:** Wire the renderer into the project bridge's message relay — after output shaping, before sending to chat adapter. The renderer returns image blobs that are attached to the message.

4. **Config:** Add `mermaid_rendering` section to project bridge config with fields: `enabled`, `format` (png/svg), `max_width`, `max_height`, `preserve_code`.

5. **Tests:** Write integration tests for each acceptance criterion, including a mock `mmdc` for deterministic testing.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-07 | a194674c | Initial creation |
