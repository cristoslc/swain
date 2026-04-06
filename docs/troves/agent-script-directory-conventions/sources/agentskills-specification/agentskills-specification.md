---
source-type: documentation-site
title: "Agent Skills Specification — agentskills.io"
url: https://agentskills.io/specification
fetched: 2026-04-06
---

# Agent Skills Specification

The open format standard for giving agents new capabilities and expertise. Maintained by Anthropic under Apache 2.0, with 15.2k GitHub stars. Donated to the community alongside MCP and AGENTS.md under the Linux Foundation's Agentic AI Foundation (AAIF).

## Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file:

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

## Key conventions

- **`name` field**: Max 64 chars, lowercase alphanumeric + hyphens, must match parent directory name.
- **`description` field**: Max 1024 chars, describes what + when.
- **Progressive disclosure**: Metadata (~100 tokens) always loaded; instructions (<5000 tokens) on trigger; resources as needed.
- **`scripts/`**: Executable code. Self-contained or clearly documented dependencies. Common languages: Python, Bash, JavaScript.
- **`references/`**: Additional documentation loaded on demand.
- **`assets/`**: Static resources (templates, schemas, data files).
- Keep SKILL.md under 500 lines; move detail to references.

## Discovery paths

Not specified by the core spec — left to implementers. See Codex, Claude Code, OpenCode for implementation-specific paths.

## Notable absence

The spec defines **`scripts/`** within each skill directory, **not** `bin/`. There is no concept of a top-level `bin/` directory for aggregated executables in the specification. Each skill is self-contained with its own `scripts/` subdirectory.
