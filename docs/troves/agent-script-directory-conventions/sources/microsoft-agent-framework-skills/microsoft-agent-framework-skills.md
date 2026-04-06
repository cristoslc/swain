---
source-type: web-page
title: "Agent Skills — Microsoft Agent Framework"
url: https://learn.microsoft.com/en-us/agent-framework/agents/skills
fetched: 2026-04-06
---

# Microsoft Agent Framework Skills

Microsoft's implementation of the Agent Skills standard in their Agent Framework (Python and C#).

## Directory structure

```
expense-report/
├── SKILL.md                          # Required — frontmatter + instructions
├── scripts/
│   └── validate.py                   # Executable code agents can run
├── references/
│   └── POLICY_FAQ.md                 # Reference documents loaded on demand
└── assets/
    └── expense-report-template.md    # Templates and static resources
```

## Script execution model

- **Code-defined scripts** (via `@skill.script` decorator): Run in-process as direct function calls. No runner needed.
- **File-based scripts** (`.py` files in skill directories): Require a `SkillScriptRunner` callable.
- Scripts live in `scripts/` within each skill directory.
- Optional `require_script_approval=True` for human-in-the-loop gating.
- The `SkillsProvider` discovers skills from filesystem directories recursively (up to two levels deep).

## Key conventions

- Uses **`scripts/`** within each skill — not a top-level `bin/`.
- Progressive disclosure: advertise → load → read resources.
- File-based skills from `SKILL.md` files; code-defined skills via Python API.
- Both can coexist in a single `SkillsProvider`.
