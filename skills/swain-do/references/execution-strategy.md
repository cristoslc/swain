# Execution Strategy

When dispatching implementation work, swain-do selects the execution strategy based on environment and task characteristics.

## Strategy selection

```
superpowers installed?
├── YES → prefer subagent-driven development
│         ├── Complex task (multi-file, >5 min) → dispatch subagent with worktree
│         ├── Simple task (<5 min, single file) → serial execution (subagent overhead not worth it)
│         └── Research task → dispatch parallel investigation agents
└── NO  → tk-tracked serial execution (current default)
```

**Detection:** Check whether superpowers' execution skills exist:

```bash
ls .claude/skills/subagent-driven-development/SKILL.md .agents/skills/subagent-driven-development/SKILL.md \
   .claude/skills/using-git-worktrees/SKILL.md .agents/skills/using-git-worktrees/SKILL.md 2>/dev/null
```

If at least one path exists for each skill, subagent-driven development is available.

## Worktree-artifact mapping

When a spec is implemented via a git worktree (superpowers' `using-git-worktrees` skill), swain-do records the mapping in the tk epic's notes:

```bash
tk add-note <epic-id> "Worktree: branch <branch-name> implements <SPEC-ID>"
```

This enables:
- Status queries to show which worktrees are active for which specs
- Cleanup checks after spec completion (orphaned worktrees)
- Traceability between the spec artifact and its implementation branch

When the spec transitions to Implemented, verify the worktree has been cleaned up or merged.
