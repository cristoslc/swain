---
name: swain-retro
description: "Automated retrospectives — captures learnings at EPIC completion and on manual invocation. EPIC-scoped retros embed a Retrospective section in the EPIC artifact. Cross-epic and time-based retros produce standalone retro docs. Triggers on: 'retro', 'retrospective', 'what did we learn', 'reflect', or automatically after EPIC terminal transitions."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  short-description: Structured retrospectives at natural completion points
  version: 2.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Retrospectives

Captures learnings at natural completion points and persists them for future use. This skill is both auto-triggered (EPIC terminal transition hook in swain-design) and manually invocable via `/swain-retro`.

## Output modes

| Scope | Output | Rationale |
|-------|--------|-----------|
| **EPIC-scoped** (auto or explicit) | `## Retrospective` section appended to the EPIC artifact | The EPIC already contains lifecycle, success criteria, and child specs — it's the single source of truth for "what we shipped and what we learned" |
| **Cross-epic / time-based** (manual) | Standalone retro doc in `docs/swain-retro/` | No single artifact owns the scope — a dedicated doc is required |

## Invocation modes

| Mode | Trigger | Context source | Output | Interactive? |
|------|---------|---------------|--------|-------------|
| **Auto** | EPIC transitions to terminal state (called by swain-design) | The EPIC and its child artifacts | Embedded in EPIC | No — fully automated |
| **Interactive** | EPIC transitions to terminal state during a live session | The EPIC and its child artifacts | Embedded in EPIC | Yes — reflection questions offered |
| **Manual** | User runs `/swain-retro` or `/swain retro` | Recent work — git log, closed tasks, transitioned artifacts | Standalone retro doc (required) | Yes |
| **Scoped** | `/swain-retro EPIC-NNN` or `/swain-retro SPEC-NNN` | Specific artifact and its related work | Embedded in EPIC (if EPIC-scoped) or standalone | Yes |

**Terminal states** that trigger auto-retro: `Complete`, `Abandoned`, `Superseded`. The retro content adapts to the terminal state — an Abandoned EPIC's retro focuses on why work stopped and what was learned, not on success criteria.

## Step 1 — Gather context

Collect evidence of what happened during the work period.

### For EPIC-scoped retros (auto or scoped)

```bash
# Get the EPIC and its children
bash skills/swain-design/scripts/chart.sh deps <EPIC-ID>

# Get closed tasks linked to child specs
TK_BIN="$(cd skills/swain-do/bin && pwd)"
export PATH="$TK_BIN:$PATH"
ticket-query '.status == "closed"' 2>/dev/null | grep -l "<EPIC-ID>\|<SPEC-IDs>"
```

Also read:
- The EPIC's lifecycle table (dates, duration)
- Child SPECs' verification tables (what was proven)
- Any ADRs created during the work
- Git log for commits between EPIC activation and completion dates

### For manual (unscoped) retros

```bash
# Recent git activity
git log --oneline --since="1 week ago" --no-merges

# Recently closed tasks
TK_BIN="$(cd skills/swain-do/bin && pwd)"
export PATH="$TK_BIN:$PATH"
ticket-query '.status == "closed"' 2>/dev/null | head -20

# Recently transitioned artifacts
bash skills/swain-design/scripts/chart.sh status 2>/dev/null
```

Also check:
- Existing memory files for context on prior patterns
- Previous retro docs in `docs/swain-retro/` for recurring themes

## Step 2 — Generate or prompt reflection

### Auto mode (non-interactive)

When invoked by swain-design during a non-interactive EPIC terminal transition (e.g., dispatched agent, batch processing), **generate the retro content automatically** from the gathered context:

1. Synthesize what was accomplished, what changed from the original scope, and what patterns are visible in the commit/task history
2. For `Abandoned` or `Superseded` EPICs, focus on why the work stopped and what was learned
3. Proceed directly to Step 3 (memory extraction) and Step 4 (write output)

### Interactive mode

When the user is present (live session, manual invocation), present a summary and offer reflection:

#### Summary format

> **Retro scope:** {EPIC-NNN title / "recent work"}
> **Period:** {start date} — {end date}
> **Artifacts completed:** {list}
> **Tasks closed:** {count}
> **Key commits:** {notable commits}

#### Reflection questions

Ask these one at a time, waiting for user response between each:

1. **What went well?** What patterns or approaches worked effectively that we should repeat?
2. **What was surprising?** Anything unexpected — blockers, shortcuts, scope changes?
3. **What would you change?** If you could redo this work, what would you do differently?
4. **What patterns emerged?** Any recurring themes across tasks — tooling friction, design gaps, communication patterns?

Adapt follow-up questions based on user responses. If the user gives brief answers, probe deeper. If they're expansive, move on.

## Step 3 — Distill into memory files

After the reflection conversation, create or update memory files:

### Feedback memories

For behavioral patterns and process learnings that should guide future agent behavior:

```markdown
---
name: retro-{topic}
description: {one-line description of the learning}
type: feedback
---

{The pattern or rule}

**Why:** {User's explanation from the retro}
**How to apply:** {When this guidance kicks in}
```

Write to the project memory directory:
```
~/.claude/projects/<project-slug>/memory/feedback_retro_{topic}.md
```

Update `MEMORY.md` index.

### Project memories

For context about ongoing work patterns, team dynamics, or project-specific learnings:

```markdown
---
name: retro-{topic}
description: {one-line description}
type: project
---

{The fact or observation}

**Why:** {Context from the retro}
**How to apply:** {How this shapes future suggestions}
```

### Rules for memory creation

- Only create memories the user has explicitly validated during the reflection
- Merge with existing memories when the learning extends a prior pattern
- Use absolute dates (from the retro context), not relative
- Maximum 3-5 memory files per retro — distill, don't dump

## Step 4 — Write output

Output destination depends on scope — see **Output modes** at the top.

### EPIC-scoped: embed in the EPIC artifact

Append a `## Retrospective` section to the EPIC markdown file, **before** the `## Lifecycle` table. This keeps the EPIC as the single source of truth.

```markdown
## Retrospective

**Terminal state:** {Complete | Abandoned | Superseded}
**Period:** {activation date} — {terminal date}

### Summary

{What was accomplished — or for Abandoned/Superseded, what was learned and why work stopped}

### Reflection

{Synthesized findings — from auto-generation or interactive Q&A}

### Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_x.md | feedback | ... |
| project_retro_y.md | project | ... |
```

### Cross-epic / time-based: standalone retro doc (required)

For manual retros not scoped to a single EPIC, a standalone doc is **required** — no single artifact owns the scope.

```bash
mkdir -p docs/swain-retro
```

File: `docs/swain-retro/YYYY-MM-DD-{topic-slug}.md`

```markdown
# Retro: {title}

**Date:** {YYYY-MM-DD}
**Scope:** {description of what's covered}
**Period:** {start} — {end}

## Summary

{Brief description of what was completed across the scope}

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| ... | ... | Complete/Abandoned/... |

## Reflection

### What went well
{User's responses, synthesized}

### What was surprising
{User's responses, synthesized}

### What would change
{User's responses, synthesized}

### Patterns observed
{User's responses, synthesized}

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| feedback_retro_x.md | feedback | ... |
| project_retro_y.md | project | ... |
```

## Step 5 — Update session bookmark

```bash
BOOKMARK="$(find . .claude .agents -path '*/swain-session/scripts/swain-bookmark.sh' -print -quit 2>/dev/null)"
bash "$BOOKMARK" "Completed retro for {scope} — {N} learnings captured"
```

## Integration with swain-design

swain-design orchestrates this skill when an EPIC transitions to any terminal state (`Complete`, `Abandoned`, `Superseded`):

1. swain-design completes the phase transition (move, status update, commit, hash stamp)
2. swain-design invokes swain-retro with the EPIC ID and terminal state
3. swain-retro gathers context, generates/prompts reflection, extracts memories, and embeds the `## Retrospective` section in the EPIC
4. swain-design commits the retro content as part of (or immediately after) the transition

**Interactive detection:** If the session is interactive (user is present and responding), swain-retro offers the reflection questions. If non-interactive (dispatched agent, batch), it runs fully automated.

This is best-effort — if swain-retro is not available, the EPIC transition still succeeds without a retro section.

## Referencing prior retros

When running a new retro, scan both EPIC artifacts (grep for `## Retrospective` sections) and `docs/swain-retro/` for prior retros. If patterns recur across multiple retros, call them out explicitly — recurring themes are the most valuable learnings.

```bash
# Check standalone retro docs
ls docs/swain-retro/*.md 2>/dev/null | head -10

# Check embedded retros in EPICs
grep -rl "## Retrospective" docs/epic/ 2>/dev/null | head -10
```
