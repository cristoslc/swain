---
source-id: "005"
title: "cognee-skills Example Skills and Test Harness"
type: local
path: "cognee/cognee_skills/example/ and cognee/cognee_skills/example_skills/"
url: "https://github.com/topoteretes/cognee/tree/demo/graphskill_COG-4178/cognee/cognee_skills/example"
fetched: 2026-03-15T21:05:00Z
hash: "sha256:placeholder"
---

# cognee-skills Example Skills and Test Harness

## Example Skills

### data-extraction (example_skills/)

```yaml
---
name: data-extraction
description: >
  Extract structured data from unstructured text, PDFs, or web pages.
  Use when the user asks to "extract data from", "pull out the fields",
  "parse this into a table", "get the entities from".
---
```

Process: Identify source format → determine target schema → extract entities → validate → return JSON with confidence score and warnings.

### team-comms (example/skills/) — Intentionally broken for demo

```yaml
---
name: team-comms
description: Write internal team communications — status updates, incident reports, and announcements.
---
```

This skill has **deliberately wrong instructions** — it tells the agent to write haiku about the ocean instead of team communications. This is the skill used to demonstrate the self-improvement loop in test_sdk.py.

## Example CLAUDE.md

```
Use run_skill via MCP for tasks — skills learn from their mistakes and get better over time.
Skills are in the ./skills folder. Run ingest_skills(skills_folder="./skills") if they haven't been loaded yet.
```

## Test SDK (test_sdk.py) — Full self-improvement loop demo

Demonstrates the complete cycle:

1. **Ingest:** Load skills from `./skills` folder
2. **Run 3 times:** Execute team-comms skill (bad instructions → low quality scores)
3. **Inspect:** Analyze failed runs → identifies `failure_category`, `root_cause`, `severity`
4. **Preview fix:** Generate amended instructions (not applied yet)
5. **Apply fix:** `skills.amendify(amendment_id)` — updates skill in graph
6. **Run again:** Execute same task with fixed skill → higher quality score

This test demonstrates how the deliberately broken team-comms skill (haiku instead of comms) gets automatically diagnosed and repaired.

## Graph Visualization

```python
from cognee.api.v1.visualize import start_visualization_server
await start_visualization_server(port=8080)
```

Or via CLI: `cognee-cli -ui` launches UI at http://localhost:3000.

Live example at graphskills.vercel.app.
