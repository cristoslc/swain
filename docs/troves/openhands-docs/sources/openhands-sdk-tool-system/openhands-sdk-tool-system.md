---
title: "OpenHands Tool System & MCP"
url: https://docs.openhands.dev/sdk/arch/tool-system
hostname: docs.openhands.dev
description: "High-level architecture of the action-observation tool framework"
date: 2025-01-13
sitename: OpenHands Documentation
type: web-page
---

# Tool System & MCP

> High-level architecture of the action-observation tool framework

The **Tool System** provides a type-safe, extensible framework for defining agent capabilities.

## Core Responsibilities

The Tool System has four primary responsibilities:

1. **Type Safety** - Enforce action/observation schemas via Pydantic models
2. **Schema Generation** - Auto-generate LLM-compatible tool descriptions
3. **Execution Lifecycle** - Validate inputs, execute logic, wrap outputs
4. **Tool Registry** - Discover and resolve tools by name or pattern

## Key Components

| Component | Purpose | Design |
|-----------|---------|--------|
| `ToolBase` | Abstract base class | Generic over Action/Observation types |
| `ToolDefinition` | Concrete tool class | Can be instantiated directly or subclassed |
| `Action` | Input model | Pydantic model with `visualize` property |
| `Observation` | Output model | Pydantic model with `to_llm_content` property |
| `ToolExecutor` | Execution interface | ABC with `__call__()` method |
| `ToolRegistry` | Tool discovery | Resolves Tool specs to ToolDefinition |

## Action-Observation Pattern

The tool system follows a **strict input-output contract**: `Action → Observation`

**Tool System Boundary:**
- **Input**: `dict[str, Any]` (JSON arguments) → validated `Action` instance
- **Output**: `Observation` instance with structured result
- **No knowledge of**: Events, LLM messages, conversation state

## Tool Definition Patterns

### Pattern 1: Direct Instantiation (Simple Tools)

For stateless tools that don't need runtime configuration (e.g., `finish`, `think`):

1. **Action** - Pydantic model with `visualize` property for display
2. **Observation** - Pydantic model with `to_llm_content` property for LLM
3. **ToolExecutor** - Stateless executor with `__call__(action) → observation`
4. **ToolDefinition** - Direct instantiation with executor instance

### Pattern 2: Subclass with Factory (Stateful Tools)

For tools requiring runtime configuration (e.g., `execute_bash`, `file_editor`):

1. **Action/Observation** - Same as Pattern 1
2. **ToolExecutor** - Stateful executor with `__init__()` and optional `close()`
3. **MyTool(ToolDefinition)** - Subclass with `@classmethod create()` factory
4. **Factory Method** - Returns configured tool instances

## Tool Annotations

Tools include optional `ToolAnnotations` based on the MCP spec:

| Field | Meaning | Examples |
|-------|---------|----------|
| `readOnlyHint` | Tool doesn't modify state | `glob` (True), `execute_bash` (False) |
| `destructiveHint` | May delete/overwrite data | `file_editor` (True) |
| `idempotentHint` | Repeated calls are safe | `glob` (True) |
| `openWorldHint` | Interacts beyond closed domain | `execute_bash` (True) |

## MCP Integration

The tool system supports external tools via the **Model Context Protocol (MCP)**.

**Key MCP Components:**

| Component | Purpose |
|-----------|---------|
| `MCPClient` | MCP server connection |
| `MCPToolDefinition` | Wraps MCP tools as SDK `ToolDefinition` |
| `MCPToolExecutor` | Bridges agent actions to MCP tool calls |

**Discovery Flow:**
1. Spawn MCP server via stdio protocol
2. Call MCP `tools/list` endpoint
3. Parse schemas from MCP response
4. Create `MCPToolDefinition` instances
5. Add to agent's `tools_map` during initialization

**Sync/Async Bridge:**
- MCP protocol is asynchronous, SDK tools execute synchronously
- Bridge pattern solves this via background event loop

## File Organization

Tools follow consistent structure:

```
my_tool/
├── __init__.py           # Export MyTool
├── definition.py         # Action, Observation, MyTool(ToolDefinition)
├── impl.py              # MyExecutor(ToolExecutor)
└── [other modules]      # Tool-specific utilities
```

**Benefits:**
- Separation of Concerns: Public API separate from implementation
- Avoid Circular Imports: Import `impl` only inside `create()`
- Consistency: All tools follow same structure
