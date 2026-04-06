# Agent Script Directory Conventions — Synthesis

## Key findings

The Agent Skills standard — maintained by Anthropic, adopted by OpenAI Codex, Microsoft Agent Framework, GitHub Copilot, Kiro, OpenCode, Spring AI, and others — has established a clear, consistent convention for how agent-facing executables are organized.

### 1. `scripts/` is the universal convention, not `bin/`

Every implementation of the Agent Skills standard uses `scripts/` as the subdirectory name for executable code within skills:

| Implementation | Script Directory | Source |
|---------------|-----------------|--------|
| Agent Skills spec | `scripts/` | agentskills.io/specification |
| OpenAI Codex | `scripts/` | developers.openai.com/codex/skills |
| Microsoft Agent Framework | `scripts/` | learn.microsoft.com |
| Claude Platform | `scripts/` | platform.claude.com |
| GitHub Copilot / VS Code | `scripts/` | code.visualstudio.com |
| Kiro (Amazon) | `scripts/` | kiro.dev/docs/skills |
| Spring AI | `scripts/` | spring.io |
| OpenCode (SST) | `scripts/` | opencode.ai |
| everything-claude-code | `scripts/` | github.com/affaan-m |

No implementation uses `bin/`. The Agent Skills specification explicitly defines `scripts/` and makes no mention of `bin/` at any level.

### 2. Scripts live within skills, not aggregated at a top level

The Agent Skills standard treats each skill as a self-contained package. Scripts belong to the skill that uses them:

```
.agents/skills/
├── my-skill/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── validate.py
│   └── references/
└── other-skill/
    ├── SKILL.md
    └── scripts/
        └── process.sh
```

No standard or implementation defines a top-level aggregation directory like `.agents/bin/` or `.agents/scripts/`. The ecosystem assumes scripts are discovered through skill directories, not through a shared executable path.

### 3. The `.agents/` directory is the cross-tool standard

Codex established `.agents/skills/` as the canonical discovery path. OpenCode explicitly recognizes `.agents/skills/` as the "agent-compatible" standard path alongside tool-specific paths (`.claude/skills/`, `.opencode/skills/`, `.kiro/skills/`). The AAIF under the Linux Foundation is formalizing this.

### 4. Discovery model: walk-up, not PATH-like

All implementations use a "walk-up" discovery model — scanning from CWD to repo root for skill directories. This contrasts with the Unix `PATH` model where `bin/` directories are added to an executable search path. The agent skills world doesn't need a `bin/` because agents don't resolve scripts by name from a search path — they resolve them by skill, then read the skill's scripts.

## Points of agreement

All 9 surveyed implementations agree on:
- `scripts/` as the directory name for executable code.
- Scripts scoped within individual skill directories, not aggregated.
- `.agents/skills/` as the interoperability standard path.
- Progressive disclosure as the loading strategy.
- SKILL.md as the required entry point.

## Points of disagreement

- **Tool-specific paths**: `.claude/skills/`, `.kiro/skills/`, `.opencode/skills/` vs `.agents/skills/`. Most tools support multiple paths for compatibility.
- **Script execution model**: Microsoft requires an explicit `SkillScriptRunner` with optional approval gating. Claude runs scripts via bash directly. Codex uses its own sandboxed execution.

## Gaps

- **Cross-skill shared scripts**: No standard addresses the case where multiple skills need the same utility script. The spec assumes skills are self-contained. Swain's `.agents/bin/` symlink layer solves a real problem the standard doesn't address.
- **Non-skill scripts**: The Agent Skills standard covers scripts within skills, but projects also have scripts that aren't part of any skill — migration scripts, health checks, build utilities. Where these live is undefined by any standard.

## Implications for swain

Swain's `.agents/bin/` serves a purpose the Agent Skills standard doesn't cover: a shared, stable resolution path for agent-facing scripts that cross skill boundaries. The industry convention is `scripts/` (not `bin/`), and the standard scopes scripts within skills. Swain's approach of symlinking from `.agents/bin/` to `skills/*/scripts/` creates a flat namespace that no other tool uses or expects.

Options for alignment:
1. **Rename to `.agents/scripts/`** — aligns with industry naming while keeping the aggregation concept.
2. **Keep `.agents/bin/`** — Unix-correct but diverges from the ecosystem convention. No other agentic tool uses `bin/`.
3. **Eliminate the aggregation layer** — reference scripts via skill paths directly (`.agents/skills/<name>/scripts/<script>`). Most aligned with the standard, but longer paths.
