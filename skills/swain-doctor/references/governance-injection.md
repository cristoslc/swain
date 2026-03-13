# Governance Injection

When governance rules are not found (or were deleted during legacy cleanup), inject them into the appropriate context file.

## Claude Code

Determine the target file:

1. If `CLAUDE.md` exists and its content is just `@AGENTS.md` (the include pattern set up by swain-init), inject into `AGENTS.md` instead.
2. Otherwise, inject into `CLAUDE.md` (create it if it doesn't exist).

Read the canonical governance content from `skills/swain-doctor/references/AGENTS.content.md` and append it to the target file.

## Cursor

Write the governance rules to `.cursor/rules/swain-governance.mdc`. Create the directory if needed.

Prepend Cursor MDC frontmatter to the canonical content from `skills/swain-doctor/references/AGENTS.content.md`:

```markdown
---
description: "swain governance — skill routing, pre-implementation protocol, issue tracking"
globs:
alwaysApply: true
---
```

Then append the full contents of `skills/swain-doctor/references/AGENTS.content.md` after the frontmatter.

## After injection

Tell the user:

> Governance rules installed in `<file>`. These ensure swain-design, swain-do, and swain-release skills are routable. You can customize the rules — just keep the `<!-- swain governance -->` markers so this skill can detect them on future sessions.
