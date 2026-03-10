---
name: swain-doctor
description: "ALWAYS invoke this skill at the START of every session before doing any other work. Validates project health: ensures governance rules are installed, cleans up legacy skill directories, and repairs .beads/.gitignore to prevent runtime files from leaking into git. Idempotent — safe to run every session."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Session-start health checks and repair
  version: 1.0.0
  author: cristos
  source: swain
---

# Doctor

Session-start health checks for swain projects. This skill is idempotent — run it every session; it only writes when repairs are needed.

## Session-start governance check

1. Detect the agent platform and locate the context file:

   | Platform | Context file | Detection |
   |----------|-------------|-----------|
   | Claude Code | `CLAUDE.md` (project root) | Default — use if no other platform detected |
   | Cursor | `.cursor/rules/swain-governance.mdc` | `.cursor/` directory exists |

2. Check whether governance rules are already present:

   ```bash
   grep -l "swain governance" CLAUDE.md AGENTS.md .cursor/rules/swain-governance.mdc 2>/dev/null
   ```

   If any file matches, governance is already installed. Proceed to [Legacy skill cleanup](#legacy-skill-cleanup).

3. If no match, run [Legacy skill cleanup](#legacy-skill-cleanup), then proceed to [Governance injection](#governance-injection).

## Legacy skill cleanup

Clean up skill directories that have been superseded by renames. Read the legacy mapping from `references/legacy-skills.json` in this skill's directory.

For each entry in the `renamed` map:

1. Check whether `.claude/skills/<old-name>/` exists.
2. If it does NOT exist, skip (nothing to clean).
3. If it exists, check whether `.claude/skills/<new-name>/` also exists. If the replacement is missing, **skip and warn** — the update may not have completed:
   > Skipping cleanup of `<old-name>` — its replacement `<new-name>` is not installed.
4. If both exist, **fingerprint check**: read `.claude/skills/<old-name>/SKILL.md` and check whether its content matches ANY of the fingerprints listed in `legacy-skills.json`. Specifically, grep the file for each fingerprint string — if at least one matches, the skill is confirmed to be a swain skill.
5. If no fingerprint matches, **skip and warn** — this may be a third-party skill with the same name:
   > Skipping cleanup of `.claude/skills/<old-name>/` — it does not appear to be a swain skill (no fingerprint match). If this is a stale swain skill, delete it manually.
6. If fingerprint matches and replacement exists, **delete the old directory**:
   ```bash
   rm -rf .claude/skills/<old-name>
   ```
   Tell the user:
   > Removed legacy skill `.claude/skills/<old-name>/` (replaced by `<new-name>`).

After processing all entries, check whether the governance block in the context file references old skill names. If the governance block (between `<!-- swain governance -->` and `<!-- end swain governance -->`) contains any old-name from the `renamed` map, delete the entire block (inclusive of markers) and proceed to [Governance injection](#governance-injection) to re-inject a fresh copy with current names.

## Governance injection

When governance rules are not found (or were deleted during legacy cleanup), inject them into the appropriate context file.

### Claude Code

Determine the target file:

1. If `CLAUDE.md` exists and its content is just `@AGENTS.md` (the include pattern set up by swain-init), inject into `AGENTS.md` instead.
2. Otherwise, inject into `CLAUDE.md` (create it if it doesn't exist).

Append the following block to the target file:

```markdown
<!-- swain governance — do not edit this block manually -->

## Skill routing

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs (architecture overviews, competitive analyses, journey maps), **always invoke the swain-design skill**. This includes requests like "write a spec", "let's plan the next feature", "create an ADR for this decision", "move the spike to Active", "add a user story", "create a runbook", "file a bug", or "update the architecture overview." The skill contains the artifact types, lifecycle phases, folder structure conventions, relationship rules, and validation procedures — do not improvise artifact creation outside the skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system. This applies whether tasks originate from swain-design (implementation plans) or from standalone work. The swain-do skill bootstraps and operates the external task backend — it will install the CLI if missing, manage fallback if installation fails, and translate abstract operations (create plan, add task, set dependency) into concrete commands. Do not use built-in agent todos when this skill is available.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires a swain-do plan **before** writing code. Invoke the swain-design skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **swain-do** skill for all bd operations — it provides the full command reference and workflow.

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

When the user wants to create, plan, write, update, transition, or review any documentation artifact (Vision, Journey, Epic, Story, Agent Spec, Spike, ADR, Persona, Runbook, Bug) or their supporting docs (architecture overviews, competitive analyses, journey maps), **always invoke the swain-design skill**. This includes requests like "write a spec", "let's plan the next feature", "create an ADR for this decision", "move the spike to Active", "add a user story", "create a runbook", "file a bug", or "update the architecture overview." The skill contains the artifact types, lifecycle phases, folder structure conventions, relationship rules, and validation procedures — do not improvise artifact creation outside the skill.

**For all task tracking and execution progress**, use the **swain-do** skill instead of any built-in todo or task system. This applies whether tasks originate from swain-design (implementation plans) or from standalone work. The swain-do skill bootstraps and operates the external task backend — it will install the CLI if missing, manage fallback if installation fails, and translate abstract operations (create plan, add task, set dependency) into concrete commands. Do not use built-in agent todos when this skill is available.

## Pre-implementation protocol (MANDATORY)

Implementation of any SPEC artifact (Epic, Story, Agent Spec, Spike) requires a swain-do plan **before** writing code. Invoke the swain-design skill — it enforces the full workflow.

## Issue Tracking

This project uses **bd (beads)** for all issue tracking. Do NOT use markdown TODOs or task lists. Invoke the **swain-do** skill for all bd operations — it provides the full command reference and workflow.

<!-- end swain governance -->
```

### After injection

Tell the user:

> Governance rules installed in `<file>`. These ensure swain-design, swain-do, and swain-release skills are routable. You can customize the rules — just keep the `<!-- swain governance -->` markers so this skill can detect them on future sessions.

## Beads gitignore hygiene

This section runs every session, after governance checks. It is idempotent. **Skip entirely if `.beads/` does not exist** (the project has not initialized bd yet).

### Step 1 — Validate .beads/.gitignore

The following are the canonical ignore patterns. This list is kept in sync with `references/.beads-gitignore` in this skill's directory.

**Canonical patterns** (non-comment, non-blank lines):

```
dolt/
dolt-access.lock
bd.sock
bd.sock.startlock
sync-state.json
last-touched
.local_version
redirect
.sync.lock
export-state/
ephemeral.sqlite3
ephemeral.sqlite3-journal
ephemeral.sqlite3-wal
ephemeral.sqlite3-shm
dolt-server.pid
dolt-server.log
dolt-server.lock
dolt-server.port
dolt-server.activity
dolt-monitor.pid
backup/
*.db
*.db?*
*.db-journal
*.db-wal
*.db-shm
db.sqlite
bd.db
.beads-credential-key
```

1. If `.beads/.gitignore` does not exist, create it from the reference file (`references/.beads-gitignore`) and skip to Step 2.

2. Read `.beads/.gitignore`. For each canonical pattern above, check whether it appears as a non-comment line in the file.

3. Collect any missing patterns. If none are missing, this step is silent — move to Step 2.

4. If patterns are missing, append them to `.beads/.gitignore`:

   ```

   # --- swain-managed entries (do not remove) ---
   <missing patterns, one per line>
   ```

5. Tell the user:
   > Patched `.beads/.gitignore` with N missing entries. These entries prevent runtime and database files from being tracked by git.

### Step 2 — Clean tracked runtime files

After ensuring the gitignore is correct, check whether git is still tracking files that should now be ignored:

```bash
cd "$(git rev-parse --show-toplevel)" && git ls-files --cached .beads/ | while IFS= read -r f; do
  if git check-ignore -q "$f" 2>/dev/null; then
    echo "$f"
  fi
done
```

This lists files that are both tracked (in the index) and matched by the current gitignore rules.

If no files are found, this step is silent.

If files are found:

1. Remove them from the index (this untracks them without deleting from disk):

   ```bash
   git rm --cached <file1> <file2> ...
   ```

2. Tell the user:
   > Untracked N file(s) from git that are now covered by `.beads/.gitignore`. These files still exist on disk but will no longer be committed. You should commit this change.

## Governance content reference

The canonical governance rules are embedded in the [Governance injection](#governance-injection) section above. If the upstream rules change in a future swain release, update the embedded blocks and bump the skill version. Consumers who want the updated rules can delete the `<!-- swain governance -->` block from their context file and re-run this skill.
