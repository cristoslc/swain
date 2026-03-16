---
source-id: "002"
title: "cognee-skills README — Full Documentation"
type: local
path: "cognee/cognee_skills/README.md"
url: "https://github.com/topoteretes/cognee/blob/demo/graphskill_COG-4178/cognee/cognee_skills/README.md"
fetched: 2026-03-15T21:05:00Z
hash: "sha256:placeholder"
---

# cognee-skills

Skills are static. They repeat the same mistakes, produce the same bad output, and the only way to fix them is manually (if someone notices at all).

**cognee-skills** gives every skill a self-improvement loop. Every run is scored. Failures are diagnosed. Fixes are proposed, applied, and verified automatically.

## Quickstart

### 1. Install

```bash
pip install cognee
```

Set `LLM_API_KEY` in your `.env` (defaults to OpenAI).

### 2. Load the meta-skill and run it

```python
from cognee import skills

await skills.ingest_meta_skill()
result = await skills.run("A skill keeps producing wrong output. How do I fix it?")
```

`skills.run()` does everything: finds the best skill, executes it, scores the output, records the outcome, and self-repairs on failure.

### 3. Add your own skills

```python
await skills.ingest("./my_skills")
await skills.ingest_meta_skill()
result = await skills.run("Compress this conversation")
```

## The meta-skill

cognee-skills ships with a built-in skill that teaches agents how to use the self-improvement loop.

**Programmatic:**
```python
await skills.ingest_meta_skill()
```

**As a file in your skills folder:**
```bash
cp /path/to/site-packages/cognee/cognee_skills/meta-skill/SKILL.md ./my_skills/cognee-skills/SKILL.md
```

## Integrations

| | Who it's for |
|---|---|
| Claude Code / MCP IDEs | Vibe-coders, anyone using Claude Code or a MCP-enabled IDE |
| Python SDK | Developers building custom workflows or agents |
| CLI | Terminal users, shell scripts, CI pipelines |
| MCP programmatically | Custom agents or services that speak MCP |

### Claude Code / MCP IDEs

```json
{
  "mcpServers": {
    "cognee": {
      "command": "cognee-mcp"
    }
  }
}
```

### Python SDK

```python
from cognee import skills
await skills.ingest("./my_skills")
result = await skills.run("Compress this conversation")
```

### CLI

```bash
cognee-cli skills ingest ./my_skills
cognee-cli skills run "Compress this conversation"
cognee-cli skills inspect summarize
```

### MCP programmatically

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command="cognee-mcp")
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        await session.call_tool("ingest_skills", {"skills_folder": "./my_skills"})
        result = await session.call_tool("run_skill", {"task_text": "Compress this conversation"})
```

## The self-improvement loop

Every run is scored 0.0–1.0 by a second LLM call. Failures accumulate. Once the threshold is hit:

```
skill fails
  → inspect: LLM diagnoses why (root cause, severity, hypothesis)
  → preview: LLM generates improved instructions
  → amendify: fix applied to the graph, original preserved
  → evaluate: before/after scores compared
  → rollback: one call to revert if the fix didn't help
```

## How the graph stores it

```
Skill              — instructions, metadata, content hash
  └─ solves ──→  TaskPattern   — routing patterns with prefers weights
  └─ has ────→  SkillRun       — every execution (success or failure)
  └─ has ────→  SkillInspection — LLM diagnosis of failure patterns
  └─ has ────→  SkillAmendment  — proposed + applied fixes, with history
  └─ has ────→  SkillChangeEvent — temporal log of every change
```

## SkillChangeEvent — audit trail

| Trigger | `change_type` |
|---------|--------------|
| New skill ingested | `"added"` |
| Skill content changed on upsert | `"updated"` |
| Skill deleted | `"removed"` |
| Amendment applied | `"amended"` |
| Amendment reverted | `"rolled_back"` |

Each event stores `skill_id`, `skill_name`, `change_type`, `old_content_hash`, `new_content_hash`, and a UTC `Timestamp` node.

## Repository structure

```
my_skills/
  skill-a/
    SKILL.md        ← required
    references/     ← optional
    scripts/        ← optional
  skill-b/
    SKILL.md
```
