---
name: swain-retro
description: "Automated retrospectives — captures learnings at EPIC completion and on manual invocation. EPIC-scoped retros embed a Retrospective section in the EPIC artifact. Cross-epic and time-based retros produce standalone retro docs. Triggers on: 'retro', 'retrospective', 'post-mortem', 'lessons learned', 'debrief', 'what worked', 'what didn't work', 'what did we learn', 'reflect', or automatically after EPIC terminal transitions."
user-invocable: true
license: MIT
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion
metadata:
  short-description: Structured retrospectives at natural completion points
  version: 2.0.0
  author: cristos
  source: swain
---
<!-- swain-model-hint: sonnet, effort: medium -->

# Retrospectives

<!-- session-check: SPEC-121 -->
Before proceeding with any state-changing operation, check for an active session:
```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-session-check.sh" 2>/dev/null
```
If the JSON output has `"status"` other than `"active"`, inform the operator: "No active session — start one with `/swain-session`?" Proceed if they dismiss.

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
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
# Get the EPIC and its children
bash "$REPO_ROOT/.agents/bin/chart.sh" deps <EPIC-ID>

# Session log — the primary evidence source for retros (ADR-015)
# Contains decisions, pivots, rationale, and operator feedback
cat .agents/session.json 2>/dev/null | grep -i "<EPIC-ID>\|<SPEC-IDs>"
```

Also read:
- The EPIC's lifecycle table (dates, duration)
- Child SPECs' verification tables (what was proven)
- Any ADRs created during the work
- Git log for commits between EPIC activation and completion dates

**Note (ADR-015):** Do not use tickets (`tk` / `.tickets/`) as retro evidence. Tickets are ephemeral execution scaffolding — they record task status, not decisions or rationale. The session log (`.agents/session.json` JSONL) captures the actual conversation: what was tried, what pivoted, why, and what the operator said. Build the retro narrative from session logs and git history.

### For manual (unscoped) retros

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
# Recent git activity
git log --oneline --since="1 week ago" --no-merges

# Session log — primary evidence source (ADR-015)
cat .agents/session.json 2>/dev/null | tail -100

# Recently transitioned artifacts
bash "$REPO_ROOT/.agents/bin/chart.sh" status 2>/dev/null
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

## Step 3 — Distill learnings

After the reflection conversation, persist the learnings — but **where** they go depends on whether this is the swain project itself or a consumer project that uses swain.

### Detect context

```bash
# Check if the current repo IS swain (the tool itself)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
if [ -f "$REPO_ROOT/skills/swain/SKILL.md" ] && git remote get-url origin 2>/dev/null | grep -q "swain"; then
  echo "SWAIN_REPO"
else
  echo "CONSUMER_PROJECT"
fi
```

### In consumer projects: write to memory

Learnings from consumer projects go into Claude memory files because they represent operator preferences and project-specific patterns that should persist across sessions.

#### Feedback memories

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

The project slug is the project path with slashes replaced by dashes (e.g., `/Users/cristos/Documents/code/myapp` → `-Users-cristos-Documents-code-myapp`). These files live in Claude's memory system (not swain's `.agents/` state), which is intentional — retro learnings persist across all Claude Code sessions for this project.

Update `MEMORY.md` index.

#### Project memories

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

#### Rules for memory creation

- Only create memories the user has explicitly validated during the reflection
- Merge with existing memories when the learning extends a prior pattern
- Use absolute dates (from the retro context), not relative
- Maximum 3-5 memory files per retro — distill, don't dump

### In the swain repo: propose artifacts, not memory

When the retro is running inside swain itself, learnings that imply behavioral changes, new capabilities, or process fixes are **not memory** — they are work items. Swain's behavior is encoded in skills, specs, and ADRs, not in operator memory files.

Classify each learning and route it to the right output:

| Learning type | Route | Example |
|--------------|-------|---------|
| A skill needs new behavior or guardrails | **SPEC candidate** — add to the retro doc's "SPEC candidates" section | "swain-release should refuse to run in worktrees" |
| A cross-cutting process change | **ADR candidate** — note in retro doc | "Dispatched agents should never use reset --hard" |
| A new capability or initiative | **EPIC candidate** — note in retro doc | "Session logs need command-level forensics" |
| A bug in an existing skill | **GitHub issue** via `gh issue create` | "swain-sync doesn't preserve symlinks" |
| Operator preference or project context | **Memory** (same as consumer) | "Operator prefers bundled PRs for refactors" |

For artifact candidates, add a `## SPEC candidates` section (or `## ADR candidates`, `## EPIC candidates`) to the retro doc output. Each entry should include enough context to draft the artifact later:

```markdown
## SPEC candidates

1. **{Title}** — {one-line description of what needs to change and why}
2. ...
```

Do **not** create the specs/epics/ADRs during the retro — that is swain-design's job. The retro captures what was learned; the operator decides what to build next. Only write to memory for learnings that are genuinely about operator preferences or project context (the last row in the table above).

## Step 4 — Write output

Output destination depends on scope — see **Output modes** at the top.

### EPIC-scoped: embed in the EPIC artifact

Append a `## Retrospective` section to the EPIC markdown file, **before** the `## Lifecycle` table. This keeps the EPIC as the single source of truth.

```markdown
## Retrospective

**Terminal state:** {Complete | Abandoned | Superseded}
**Period:** {activation date} — {terminal date}
**Related artifacts:** {SPEC-NNN}, {SPEC-NNN}, ...

### Summary

{What was accomplished — or for Abandoned/Superseded, what was learned and why work stopped}

### Reflection

{Synthesized findings — from auto-generation or interactive Q&A}

### Learnings captured

<!-- In consumer projects, this table lists memory files. In the swain repo, it lists
     artifact candidates (SPECs, ADRs, issues) plus any memory files for operator preferences. -->

| Item | Type | Summary |
|------|------|---------|
| ... | memory / SPEC candidate / issue | ... |
```

Hyperlink the artifact IDs in `Related artifacts` using Step 4.5.

### Cross-epic / time-based: standalone retro doc (required)

For manual retros not scoped to a single EPIC, a standalone doc is **required** — no single artifact owns the scope.

```bash
mkdir -p docs/swain-retro
```

File: `docs/swain-retro/YYYY-MM-DD-{topic-slug}.md`

```markdown
---
title: "Retro: {title}"
artifact: RETRO-{YYYY-MM-DD}-{topic-slug}
track: standing
status: Active
created: {YYYY-MM-DD}
last-updated: {YYYY-MM-DD}
scope: "{description of what's covered}"
period: "{start} — {end}"
linked-artifacts:
  - {ARTIFACT-ID-1}
  - {ARTIFACT-ID-2}
---

# Retro: {title}

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

<!-- In consumer projects, this table lists memory files. In the swain repo, it lists
     artifact candidates (SPECs, ADRs, issues) plus any memory files for operator preferences. -->

| Item | Type | Summary |
|------|------|---------|
| ... | memory / SPEC candidate / issue | ... |
```

## Step 4.5 — Hyperlink artifact references

After writing the retro output (standalone doc or embedded EPIC section), scan all body text for bare artifact ID references matching `(SPEC|EPIC|INITIATIVE|VISION|SPIKE|ADR|PERSONA|RUNBOOK|DESIGN|JOURNEY|TRAIN)-[0-9]+`. For each bare ID not already inside a markdown link or code fence, resolve and replace:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/resolve-artifact-link.sh" <ARTIFACT-ID> <RETRO-FILE>
```

Replace bare IDs with `[ARTIFACT-ID](relative-path)`. If the script returns non-zero or empty output (artifact not found), leave the bare ID as-is. Frontmatter `related-artifacts` values stay as plain IDs (YAML compatibility).

### Context-rich artifact references

When referencing artifacts in retro output (child specs, related artifacts, linked work), use context lines:

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/artifact-context.sh" <ID> 2>/dev/null
```

Fall back to `<ID> — <title>` if the utility is unavailable.

## Step 4.7 — README drift check (SPEC-210)

After reflection and before closing the retro, check if the README still matches the project.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
[ -f "$REPO_ROOT/README.md" ] && echo "has_readme" || echo "no_readme"
```

If README.md exists:

1. Read README.md and extract claims about what the project does and how it works.
2. Compare claims against artifacts that changed during the retro scope (from Step 1 context).
3. Surface drift findings:
   - **New features the README omits** — the epic shipped something the README does not mention.
   - **Stale promises** — the epic dropped or replaced something the README still claims.
   - **Changed behavior** — the epic changed how something works but the README still shows the old way.

Show findings to the operator. They can fix the README, fix the artifact, or defer.

In auto mode, add drift findings to the `## Reflection` section. In interactive mode, show them after the reflection questions and before writing output.

If no drift exists, skip — do not add a "no drift" note.

Deferred findings go in a `### README drift` subsection of the retro output so they stay visible.

## Step 5 — Update session bookmark

```bash
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
bash "$REPO_ROOT/.agents/bin/swain-bookmark.sh" "Completed retro for {scope} — {N} learnings captured"
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
