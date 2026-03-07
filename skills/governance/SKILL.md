---
name: governance
description: "ALWAYS invoke this skill at the START of every session before doing any other work. This skill ensures the host project has agent governance rules (skill routing, pre-implementation protocol, issue tracking conventions) installed in its context file. It is idempotent — if rules are already present, it exits silently. Without this skill running first, other swain skills (spec-management, execution-tracking, release) will not be routable."
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Agent routing and governance rules
  version: 1.0.0
  author: cristos
---

# Governance

Ensure the host project's agent context file contains the swain governance rules. This skill is idempotent — run it every session; it only writes on first use.

## Session-start check

1. Detect the agent platform and locate the context file:

   | Platform | Context file | Detection |
   |----------|-------------|-----------|
   | Claude Code | `CLAUDE.md` (project root) | Default — use if no other platform detected |
   | Cursor | `.cursor/rules/swain-governance.mdc` | `.cursor/` directory exists |

2. Check whether governance rules are already present:

   ```bash
   grep -l "swain governance" CLAUDE.md .cursor/rules/swain-governance.mdc 2>/dev/null
   ```

   If any file matches, governance is already installed. **Stop here — no action needed.**

3. If no match, proceed to [First-use setup](#first-use-setup).

## First-use setup

When governance rules are not found, inject them into the appropriate context file.

### Claude Code

Append the following block to `CLAUDE.md` in the project root. If `CLAUDE.md` does not exist, create it.

```markdown
<!-- swain governance — do not edit this block manually -->

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs (architecture overviews, competitive analyses, journey maps), **always invoke the spec-management skill**. This includes requests like "write a spec", "let's plan the next feature", "create an ADR for this decision", "move the spike to Active", "add a user story", "create a runbook", "file a bug", or "update the architecture overview." The skill contains the artifact types, lifecycle phases, folder structure conventions, relationship rules, and validation procedures — do not improvise artifact creation outside the skill.

**For all task tracking and execution progress**, use the **execution-tracking** skill instead of any built-in todo or task system. This applies whether tasks originate from spec-management (implementation plans) or from standalone work. The execution-tracking skill bootstraps and operates the external task backend — it will install the CLI if missing, manage fallback if installation fails, and translate abstract operations (create plan, add task, set dependency) into concrete commands. Do not use built-in agent todos when this skill is available.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires an execution-tracking plan **before** writing code. Invoke the spec-management skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **execution-tracking** skill for all bd operations — it provides the full command reference and workflow.

<!-- end swain governance -->
```

### Cursor

Write the governance rules to `.cursor/rules/swain-governance.mdc`. Create the directory if needed.

```markdown
---
description: "swain governance — skill routing, pre-implementation protocol, issue tracking"
globs:
alwaysApply: true
---

<!-- swain governance — do not edit this block manually -->

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs (architecture overviews, competitive analyses, journey maps), **always invoke the spec-management skill**. This includes requests like "write a spec", "let's plan the next feature", "create an ADR for this decision", "move the spike to Active", "add a user story", "create a runbook", "file a bug", or "update the architecture overview." The skill contains the artifact types, lifecycle phases, folder structure conventions, relationship rules, and validation procedures — do not improvise artifact creation outside the skill.

**For all task tracking and execution progress**, use the **execution-tracking** skill instead of any built-in todo or task system. This applies whether tasks originate from spec-management (implementation plans) or from standalone work. The execution-tracking skill bootstraps and operates the external task backend — it will install the CLI if missing, manage fallback if installation fails, and translate abstract operations (create plan, add task, set dependency) into concrete commands. Do not use built-in agent todos when this skill is available.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires an execution-tracking plan **before** writing code. Invoke the spec-management skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **execution-tracking** skill for all bd operations — it provides the full command reference and workflow.

<!-- end swain governance -->
```

### After injection

Tell the user:

> Governance rules installed in `<file>`. These rules ensure spec-management, execution-tracking, and release skills are routable. You can customize the rules — just keep the `<!-- swain governance -->` markers so this skill can detect them on future sessions.

## Governance content reference

The canonical governance rules are embedded in the [First-use setup](#first-use-setup) section above. If the upstream rules change in a future swain release, update the embedded blocks and bump the skill version. Consumers who want the updated rules can delete the `<!-- swain governance -->` block from their context file and re-run this skill.
