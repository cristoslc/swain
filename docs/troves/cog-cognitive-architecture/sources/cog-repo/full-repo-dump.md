This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
.claude/
  commands/
    _templates/
      domain.md
    commit.md
    evolve.md
    explainer.md
    foresight.md
    history.md
    housekeeping.md
    humanizer.md
    personal.md
    reflect.md
    scenario.md
    setup.md
  settings.json
memory/
  cog-meta/
    scenarios/
      .gitkeep
    improvements.md
    patterns.md
    scenario-calibration.md
    self-observations.md
  glacier/
    index.md
  personal/
    action-items.md
    entities.md
    hot-memory.md
    observations.md
  domains.yml
  hot-memory.md
  link-index.md
.gitignore
CLAUDE.md
LICENSE
README.md
```

# Files

## File: .claude/commands/_templates/domain.md
````markdown
<!-- Auto-generated from domains.yml by /setup. Re-run /setup to regenerate. -->
<!-- Template variables: {{ID}}, {{LABEL}}, {{PATH}}, {{TRIGGERS}}, {{FILES}} -->

Use this skill when the user discusses {{LABEL}} topics. Trigger if the conversation involves:
{{TRIGGERS}}
Do NOT trigger for topics belonging to other domains.

## Domain

{{LABEL}}

## Memory Files

Always read on activation:
- `memory/{{PATH}}/hot-memory.md`

Then load additional files per the **Memory Retrieval Protocol** (see CLAUDE.md) based on the query:
- Status/task query → `memory/{{PATH}}/action-items.md`
- Entity/people query → `memory/{{PATH}}/entities.md`
- Project query → `memory/{{PATH}}/projects.md` (if exists)
- Technical query → `memory/{{PATH}}/dev-log.md` (if exists)
- Update/observation → target file only
- Complex query → hot-memory first, then drill into referenced files

Available warm files: {{FILES}}

Historical data: read `memory/glacier/index.md`, filter by domain={{ID}}

## Routing

When the user shares information or asks to save something:
- Task/todo → `memory/{{PATH}}/action-items.md`
- Person/entity → `memory/{{PATH}}/entities.md`
- Project/technical → `memory/{{PATH}}/projects.md`
- Update/log → `memory/{{PATH}}/observations.md`
- Status/overview → `memory/{{PATH}}/hot-memory.md`

## Activation

Read the hot-memory file, then respond to the user's query using the retrieval protocol above.
````

## File: .claude/commands/commit.md
````markdown
Use this skill when the user wants to commit changes to git. Trigger if the user says "commit", "save changes", "commit this", or asks to create a git commit. Examples: "commit", "commit and push", "save my changes".

## Process

1. **Assess the working tree** — Run `git status` (never use `-uall`) and `git diff --staged` and `git diff` to understand what changed.

2. **Guard rails** — Before staging:
   - Never commit files that contain secrets (`.env`, credentials, tokens, keys). Warn if any are present.
   - Never commit build artifacts (`dist/`, `*.tsbuildinfo`).
   - Never commit `node_modules/`.
   - If there are no changes to commit, say so and stop.

3. **Stage selectively** — Stage files by name. Prefer `git add <file>...` over `git add -A` or `git add .` to avoid accidentally including sensitive or unrelated files. Group related changes — if unrelated changes exist, ask whether to commit everything together or separately.

4. **Write the commit message** — Use Conventional Commits format:
   - `feat:` new feature
   - `fix:` bug fix
   - `refactor:` code restructuring without behavior change
   - `chore:` maintenance, dependencies, config
   - `docs:` documentation only
   - `style:` formatting, whitespace
   - `test:` adding or updating tests
   - Scope is optional: `feat(whatsapp): add voice note transcription`
   - Subject line: imperative mood, lowercase, no period, under 72 chars
   - Body (if needed): blank line after subject, wrap at 72 chars, explain *why* not *what*
   - Always end with: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

5. **Commit** — Use a HEREDOC for the message to preserve formatting:
   ```
   git commit -m "$(cat <<'EOF'
   type(scope): subject line

   Optional body explaining why.

   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

6. **Verify** — Run `git status` after committing to confirm success. Show the resulting `git log --oneline -1`.

## Rules

- Never push unless `$ARGUMENTS` contains "and push" or "push".
- Never amend unless `$ARGUMENTS` contains "amend".
- Never skip hooks (no `--no-verify`).
- Never force push.
- If a pre-commit hook fails, fix the issue, re-stage, and create a **new** commit (do not amend).
- If `$ARGUMENTS` contains a message hint, use it to inform the commit message but still follow conventional format.

## Arguments

`$ARGUMENTS` — Optional. May contain:
- A message hint (e.g., `/commit add voice transcription support`)
- "and push" to push after committing
- "amend" to amend the previous commit instead of creating a new one
- "all" to stage all changes without asking
````

## File: .claude/commands/evolve.md
````markdown
Use this skill for systems-level self-improvement. Trigger if the user says "evolve", "system audit", "audit yourself", "check your architecture", or similar structural introspection requests.

**This is NOT /reflect.** Reflect = "what did I learn from interactions?" Evolve = "are the rules and architecture working?" **Evolve never touches memory content — it changes the rules that govern how content moves.**

## Domain

Systems architecture — process rules, skill design, tier effectiveness, pipeline health.

## Memory Files

Read FIRST — this is your continuity:
- `memory/cog-meta/evolve-log.md` — your run log
- `memory/cog-meta/evolve-observations.md` — architectural issues spotted

Architecture reference:
- `CLAUDE.md` — project instructions
- `.claude/commands/housekeeping.md` — housekeeping rules
- `.claude/commands/reflect.md` — reflect rules

Measure (don't edit content):
- `memory/hot-memory.md`
- `memory/cog-meta/patterns.md`
- Any domain satellite pattern files (e.g. `work/*/patterns.md`)

## Orientation (run FIRST, before any file reads)

Use these shell commands to see exactly what changed since last run:

```bash
# What did housekeeping and reflect change recently?
git diff HEAD~1 --stat memory/

# Detailed diff of architectural files (what you care about)
git diff HEAD~1 memory/cog-meta/patterns.md memory/hot-memory.md CLAUDE.md

# What changed in the last 24h?
find memory/ -type f -name "*.md" -mtime -1 | sort

# Current prompt weight components (quick file sizes)
wc -c memory/hot-memory.md memory/cog-meta/patterns.md memory/cog-meta/briefing-bridge.md 2>/dev/null
```

Use git diffs to understand what housekeeping/reflect actually did, instead of re-reading entire files.

## Process

### 1. Architecture Review

Evaluate the structural design:

- **Tier design** — are the tiers (hot-memory → patterns → observations → glacier) well-defined?
- **Condensation pipeline** — is the flow working? Where does it leak or stall?
- **File naming and organization** — any files in wrong domains? Orphaned files?
- **Skill boundaries** — are housekeeping/reflect/evolve boundaries clean? Any drift?

### 2. Process Effectiveness Audit

Review the output of recent housekeeping and reflect runs:

**Housekeeping rules check:**
- Did pruning priority order work? Or did it trim wrong things?
- Are glacier thresholds (50 obs, 10 action items) right?
- Is the 50-line hot-memory cap appropriate?
- Is entity format enforcement catching violations?

**Reflect rules check:**
- Did condensation produce useful patterns, or noise?
- Did thread candidate detection work?
- Is reflect staying in its lane?
- Are patterns routing to the right file (core vs satellite)?

**Scorecard metrics** — measure and record in evolve-log:
- Core `patterns.md`: line count / 70, byte size / 5.5KB (target: ≤1.0)
- Satellite pattern files: list each with line count (soft cap: 30)
- Entity compression ratio: `(total entity lines across all files) / (total ### entries)` (target: ≤3.0)
- Hot-memory line counts vs caps

### 3. Rule Change Proposals

Based on findings, propose concrete rule changes. Don't fix content — fix the rules.

For each proposal:
- What problem does it solve?
- What evidence supports it?
- What's the risk?
- Is this a rule change (apply directly) or architecture change (propose for user review)?

**Apply low-risk rule changes directly** to the relevant skill files. Propose architecture changes for user review.

### 4. Route Content Issues

When you spot content problems during your audit, **don't fix them and don't defer them for yourself**. Route them explicitly:

Format in debrief:
```
→ housekeeping: entities.md at 290 lines, needs glacier pass
→ reflect: hot-memory missing thread link for X
→ reflect: patterns.md has stale snapshot data from Feb
```

If the same content issue keeps appearing across runs, that's a **rule problem** — propose a rule change so housekeeping/reflect catch it themselves.

### 5. Generate Scorecard

Overwrite `memory/cog-meta/scorecard.md` with current metrics:
- Core patterns.md: line count / 70, byte size / 5.5KB (target: ≤1.0)
- Satellite pattern files: list each with line count (soft cap: 30)
- Entity compression ratio: `(total entity lines across all files) / (total ### entries)` — target ≤3.0
- Hot-memory line counts vs caps
- Briefing bridge SSOT compliance (% of lines with [[source]] links)

### 6. Write Observations & Update Log

**Observations** — Append to `memory/cog-meta/evolve-observations.md`:
- Format: `- YYYY-MM-DD [tag]: observation`
- Tags: bloat, staleness, redundancy, gap, architecture, opportunity, rule-drift, process-health

**Evolve Log** — Append to `memory/cog-meta/evolve-log.md`:
- Run number, process effectiveness findings, rule changes applied or proposed, deferred items
- Content issues routed (→ housekeeping / → reflect)
- Update "Next Run Priorities" section at top. **Only architecture/design items — never content work.**

### 7. Debrief

Concise summary:
- *Process health* — did housekeeping/reflect follow their rules?
- *Rule changes* — applied or proposed, with rationale
- *Routed issues* — content problems sent to housekeeping/reflect
- *Architecture notes* — structural observations
- *Next evolve* — top 3 architecture priorities

Keep it actionable. Numbers over narrative.

## Activation

Read evolve-log.md and evolve-observations.md FIRST for continuity. Then audit the system. You are the architect — you design the rules, you don't play by them.
````

## File: .claude/commands/explainer.md
````markdown
Use this skill when the user wants to write, explain, draft, or craft content. Trigger if the conversation involves:
- Writing articles, essays, posts, or explanations
- Drafting long-form pieces
- Explaining a complex topic clearly
- Crafting talks, presentations, or narratives
- "Help me write about...", "explain this", "draft a post on..."
- Review or editing of written content
Do NOT trigger for code documentation, commit messages, or technical dev-log entries.

## Domain

Writing and explanation — blending Ros Atkins' systematic clarity with Montaigne's spirit of writing-as-discovery.

## Philosophy

- **Atkins**: Clarity comes from process, not talent. Structure turns complexity into understanding.
- **Montaigne**: Writing is a trial, an experiment of thought. Questions matter more than conclusions.
- **Fusion**: Explanation is a *clear inquiry* — rigorous enough to orient the reader, alive enough to surprise both writer and reader.

## The 10 Attributes of Good Explanation (Atkins)

1. Simplicity
2. Essential detail
3. Handling complexity
4. Efficiency
5. Precision
6. Context
7. No distractions
8. Engaging
9. Useful
10. Clarity of purpose

## The Montaignean Dimensions

1. **Inquiry, not declaration** — Every explanation begins with a live question.
2. **Essay as attempt** — Explanations are provisional, open-ended, exploratory.
3. **Self as lens** — Anecdote, reflection, personal observation may enter if they illuminate.
4. **Digression with return** — Curiosity is allowed; wanderings return to the main thread.
5. **Dialogue with the reader** — Thinking-with, not speaking-at.
6. **Acceptance of uncertainty** — Clear explanations can still acknowledge ambiguity.
7. **Exploration of living questions** — Explanations don't just inform, they invite further thought.

## Method

### For controlled pieces (articles, talks, posts)

1. **Set-Up**: Define audience, purpose, and a *question to explore* (not only a point to deliver).
2. **Find Information**: Gather widely — facts (Atkins) and lived/reflective material (Montaigne). Search memory files for relevant source material.
3. **Distil**: Essential vs. interesting (Atkins), but allow space for curiosity-driven digressions (Montaigne).
4. **Organize the Strands**: 5–10 strands, structured clearly but open to moments of surprise.
5. **Link**: Build narrative flow with a conversational, reflective tone.
6. **Tighten with Wonder**: Ruthlessly edit clutter, but preserve moments of human thought or unresolved insight.
7. **Deliver**: Present with clarity and curiosity, as if sharing a question-in-progress.

### For dynamic contexts (interviews, Q&A, spontaneous)

Same setup, but organize for flexibility, verbalize with reflection, and anticipate not just factual questions but philosophical "why it matters" ones.

## Audience Adaptation

- **Work contexts**: Prioritize clarity, efficiency, actionability. Wonder appears as reflection, not digression.
- **Educational/public**: Make explanations accessible while showing the process of discovery. Allow provisionality.
- **Personal/creative**: Lean into Montaignean curiosity; let the reader feel the live movement of thought.

## Operating Principles

- Always ask: *What am I trying to explain? What question am I following?*
- Explanations may end with a conclusion (Atkins) or a further question (Montaigne). Both are valid.
- Use precision + openness: say exactly what you mean, admit where understanding is incomplete.
- Treat tangents as potential insights — provided they return to the flow.
- Use anecdotes, memory, and curiosity to make abstract concepts human and engaging.

## Memory Files

Read on activation:
- `memory/personal/observations.md` for lived experience and reflections

Write to (if producing drafts or notes):
- Share drafts directly in conversation — don't persist unless asked

## Success Criteria

An excellent piece:
- Is clear, structured, and useful (Atkins)
- Feels alive, curious, and provisional (Montaigne)
- Informs *and* invites further thought

## Activation

Acknowledge the writing task, ask clarifying questions about audience and purpose if not obvious, then begin working through the method. Start with: *What's the question we're following?*
````

## File: .claude/commands/foresight.md
````markdown
Use this skill for strategic foresight — connecting dots across domains and surfacing one high-value nudge. Trigger if the user says "foresight", "what should I be thinking about", "what am I missing", "strategic nudge", "connect the dots", or similar forward-looking synthesis requests.

**This is NOT /reflect.** Reflect = past-facing (mines interactions, fixes contradictions). Foresight = future-facing (scans broadly, projects trajectories, surfaces opportunities).

**This is NOT /evolve.** Evolve = system architecture. Foresight = life/work strategy.

## Domain

Cross-domain strategic synthesis — personal, work, projects, health, family. The value is in the connections *between* domains.

## Memory Files

Read broadly — this is a scan, not a focused lookup:

1. Read `memory/domains.yml` to discover all active domains
2. For each domain, read `hot-memory.md` and `action-items.md` (if they exist)
3. Also read:
   - `memory/hot-memory.md` (cross-domain strategic context)
   - `memory/personal/entities.md` (upcoming birthdays, relationships)
   - `memory/personal/calendar.md` (what's coming up)
   - `memory/personal/health.md` (health trajectory)
   - `memory/cog-meta/briefing-bridge.md` (housekeeping findings)
   - Recent observations across all domains (last 7 days)
   - Thread current-state sections — what narratives are actively unfolding?

## Process

### 1. Cross-Domain Convergence Scan

Look for topics, people, or themes appearing in 2+ domains simultaneously. These are convergence points — where effort in one area compounds into another.

### 2. Velocity & Stall Detection

Scan action-items across all domains. Classify each active item:
- **Accelerating** — multiple updates in the last week, clear momentum. Signal: ride the wave, don't interrupt.
- **Cruising** — steady progress, on track. Signal: nothing to flag.
- **Stalling** — no movement in 2+ weeks despite not being deferred. Signal: ask why. Blocked? Lost priority?
- **Dormant** — domain-level silence (0 observations in 4+ weeks). Signal: conscious choice or drift?

Stalls and dormant domains are high-value nudge material — they represent things the user cares about but isn't acting on.

### 3. Timing Awareness

Read calendar and entities for upcoming events in the next 2-4 weeks. Look for timing windows — things that should start NOW to be ready later.

### 4. Pattern Projection

Read patterns and recent observations. Project forward: "If this continues for 2 more weeks, what happens?"

**Scenario candidate detection**: If a pattern projection reveals a genuine fork — two meaningfully different paths with real stakes and a closing decision window — flag it as a scenario candidate below the main nudge. A valid candidate needs: a fork (2+ paths), stakes (wrong choice has real cost), and time sensitivity (window closing). Don't flag routine decisions or hypotheticals with no deadline.

### 5. Write One Strategic Nudge

Synthesize into **one nudge**. Not a list. One thing.

The nudge must:
- **Cite at least 2 source files**
- **Be something the user hasn't explicitly asked about**
- **Be actionable** — not "think about X" but "do Y because of X and Z"
- **Connect dots**

Write to `memory/cog-meta/foresight-nudge.md`:

```markdown
# Foresight Nudge
<!-- Auto-generated by strategic foresight. -->
<!-- Last updated: YYYY-MM-DD -->

## Signal
<What you noticed — the raw observation from 2+ domains>

## Insight
<Why it matters — the connection, timing, or trajectory that makes this worth flagging>

## Suggested Action
<One concrete thing to do — specific, actionable, grounded>

---
Sources: [[file1]], [[file2]], [[file3]]

## Scenario Candidate (optional)
<!-- Only include if pattern projection reveals a genuine fork worth simulating -->
Decision: <one-line framing>
Why now: <why the window is closing>
Domains: <affected domains>
```

Overwrite the file each run. One nudge per run.

## Rules

1. **Read-only** — Foresight NEVER edits memory files. Writes ONLY to `memory/cog-meta/foresight-nudge.md`. If you spot a memory error, note it in the nudge's signal section and let reflect handle it.
2. **One nudge, not a list** — force prioritization. If everything is equally important, nothing is.
3. **Evidence-based** — every nudge cites at least 2 source files. No vibes.
4. **Non-obvious** — the nudge should surprise. If the user already knows and is acting on it, pick something else.
5. **Forward-looking** — avoid rehashing yesterday. Project into next week, next month.
6. **Cross-domain preferred** — nudges that connect personal + work are higher value than single-domain insights.

## Anti-Patterns

- Don't repeat what briefing-bridge already says (stale items, birthday prep) — that's housekeeping's job
- Don't recommend "reflect on X" — be specific about what to DO
- Don't flag things the user has explicitly deferred — respect the deferral
- Don't flag things that are cruising — focus on convergences, stalls, and timing windows
- Don't write a mini-briefing — one insight, one action

## Activation

Read broadly across all domains. Find the one thing worth saying.
````

## File: .claude/commands/history.md
````markdown
Use this skill for deep memory search and recall. Trigger if the user says "what did I say about...", "when did we discuss...", "find that conversation about...", "history of...", or asks about past information that needs multi-file search. For simple date/keyword lookups, a quick Grep suffices — this skill is for when you need to piece together a narrative from multiple entries.

## Domain

Memory recall — recursive search across all memory files, cross-referencing observations, entities, and action items.

## Memory Files

Read on activation:
- `memory/hot-memory.md` (for context on what's currently relevant)

Search across:
- All `observations.md` files (personal, work domains, cog-meta)
- All `entities.md` files
- All `action-items.md` files
- All `hot-memory.md` files
- `memory/glacier/` (via index.md for targeted retrieval)

## Process

### Pass 1: Locate

- Extract keywords from the user's query (names, topics, dates, phrases)
- `Grep path="memory/" pattern="<keyword>"` for each keyword
- Note which files matched and how many hits
- If >10 files match, narrow by domain or add query terms
- If 0 matches, try synonyms or related terms
- Check `memory/glacier/index.md` for archived data matching the query

### Pass 2: Extract

- Read the top 3-5 most relevant files (by hit density and recency)
- Extract the specific passages that match the query
- Track the timeline: when did the topic first come up? How did it evolve?

### Pass 3: Synthesize

- Combine extracted passages into a coherent answer
- Present findings chronologically with dates
- If something seems incomplete, flag it:
  > "Found references to X in observations but no entity entry — want me to create one?"

## Artifact Formats

**Search result**: `YYYY-MM-DD: <summary of what was found>`
**Memory gap**: `Gap: referenced but not in memory — <topic>`
**Timeline**: Chronological list of when a topic appeared and how it evolved

## Activation

Extract search terms from the user's query and begin Pass 1. Be thorough but concise in the synthesis — don't dump raw content.
````

## File: .claude/commands/housekeeping.md
````markdown
Use this skill to perform memory housekeeping. Trigger if the user says "housekeeping", "clean up memory", "prune memory", "archive old data", or similar maintenance requests.

## 0. Orientation (run FIRST, before any file reads)

Use these shell commands to scope your work before reading files:

```bash
# What changed since last run? Focus here first.
find memory/ -type f -name "*.md" -mtime -1 | sort

# Quick entry counts for archival threshold checks (>50 = archive)
# Add paths for any domain observations files that exist
grep -c "^- " memory/cog-meta/self-observations.md memory/personal/observations.md memory/*/observations.md memory/*/*/observations.md 2>/dev/null

# Completed action items count (>10 = archive)
grep -c "^\- \[x\]" memory/personal/action-items.md memory/*/action-items.md memory/*/*/action-items.md 2>/dev/null
```

Only read files that need work based on these results. Skip unchanged files.

## 1. Garbage Collect Memory

Review and archive stale data per CLAUDE.md glacier rules. All glacier files must have YAML frontmatter.

**Observations — archive by primary tag:**
- If any `observations.md` has >50 entries, group oldest entries by primary tag and move to `memory/glacier/{domain}/observations-{tag}.md`
- If `memory/cog-meta/self-observations.md` has >50 entries, group by primary tag → `memory/glacier/cog-meta/observations-{tag}.md`

**Other files — standard rules:**
- If any `action-items.md` has >10 completed items, move to `memory/glacier/{domain}/action-items-done.md`
- Apply same logic for all domains listed in `memory/domains.yml`
- If `memory/cog-meta/improvements.md` has >10 implemented items, move to `memory/glacier/cog-meta/improvements-done-{YYYY}.md`

## 2. Prune Hot Memory (rule-based)

Keep ALL hot-memory.md files under 50 lines. Relevance judgment (promote/demote) is /reflect's job — you apply structural rules:

**Files to check:**
Read `memory/domains.yml` to discover all active domains. Check `hot-memory.md` for each domain, plus the cross-domain `memory/hot-memory.md`.

**Pruning priority (trim in this order):**
1. **Resolved items** — anything with ~~strikethrough~~, "DONE", "RESOLVED"
2. **Past events** — entries about dates that have already occurred
3. **SSOT violations** — same fact in hot-memory AND the canonical file (entities, action-items, etc.). Keep in canonical file, replace hot-memory copy with `[[link]]` or remove
4. **Stale entries** — items not referenced in 14+ days
5. **Low-signal entries** — FYI items with no action or deadline

**Where trimmed entries go:**
- Entries with lasting value → append to domain's `observations.md`
- Entries that are purely historical → let them go
- Never silently delete — always move or note removal in debrief

## 3. Surface Opportunities & Accountability

Review all `action-items.md` files across every domain:
- **Stale items** (open >2 weeks): list with age and suggested next action
- **Dormant domains**: if any domain has 0 new observations in >4 weeks, flag
- **Health escalation**: items open >6 months get flagged with urgency label
- **Birthday prep**: if any birthday in entities.md is <2 weeks away, pull interests and suggest ideas

Be direct. Don't just report — recommend specific actions.

## 4. Rebuild Glacier Index

Scan all `memory/glacier/**/*.md` files. Extract YAML frontmatter. Write results to `memory/glacier/index.md`:

```
# Glacier Index
<!-- Auto-generated by housekeeping. Do not edit. -->
<!-- Last updated: YYYY-MM-DD -->

| File | Domain | Type | Tags | Date Range | Entries | Summary |
|------|--------|------|------|------------|---------|---------|
```

## 5. Link Audit (discover missing links)

For each non-glacier memory file:
1. **Entity mentions**: Scan for names matching `### <Name>` headers in entities.md — add `[[links]]` if missing
2. **Cross-domain references**: If a file mentions a topic from another domain, add a cross-domain link
3. **Action item references**: If an observation references a task, link it

Only add links where the reference is substantive.

## 5b. Entity Registry Format Enforcement

Scan all `entities.md` files for registry format compliance:

1. **3-line max**: Any `### entry` with >3 content lines should be compressed. If the entry has an associated detail file (`→ [[link]]`), compress to: name/relationship, pipe-separated key facts, status+link. If no detail file exists and entry is >5 lines, flag as a promotion candidate (suggest creating a thread file).
2. **Glacier candidates**: Entries with `status: inactive` or `last:` date >6 months ago → move to `glacier/{domain}/entities-inactive.md` (leave a stub with archived comment).
3. **Missing metadata**: Flag entries missing `status:` or `last:` fields.

## 5c. Temporal Fact Maintenance

Scan all `entities.md` files for `(until YYYY-MM)` markers with past dates:
1. If the line has no ~~strikethrough~~, add it
2. If already struck through, move to a `## Historical` subsection at the bottom of that entity's block (create the subsection if absent)
3. Report moved facts in the debrief

## 6. Rebuild Link Index

Scan all memory files (excluding `glacier/`) for `[[wiki-links]]`. For each link, record: target → source.

Rewrite `memory/link-index.md`:

```markdown
# Memory Link Index
<!-- Auto-generated by housekeeping. Do not edit. -->
<!-- Last updated: YYYY-MM-DD -->

| Target | Linked from |
|--------|-------------|
| `personal/entities` | `personal/observations`, `personal/hot-memory` |
```

Rules:
- Only include targets with at least one inbound link
- Combine multiple sources per target on one row (comma-separated)
- Exclude glacier files from both source and target

## 7. Write Briefing Bridge

Write key findings to `memory/cog-meta/briefing-bridge.md` so foresight can pick them up. Overwrite the file each run.

**SSOT rule**: Every line in the bridge must include a `[[source]]` link to its canonical file. The bridge summarizes and links — it NEVER introduces original facts.

```markdown
# Briefing Bridge
<!-- Auto-generated by housekeeping. Consumed by foresight. -->
<!-- Last updated: YYYY-MM-DD -->

## Stale Items (>2 weeks)
- <item> — <age> — suggested action: <action>
- **Compression rule**: Items stale >4 weeks — group by domain as a single line

## Birthday Prep
- <name> birthday in <N> days — interests: <from entities> — gift ideas: <suggestions>

## Dormant Domains
- <domain> — last activity: <date> — recommendation: <shelf/reactivate/shut down>

## Health Escalation
- <item> — open <N> months — urgency: <high/medium>
```

Only include sections that have content. Empty sections should be omitted.

## 8. L0 Header Maintenance

Check all active memory files for missing `<!-- L0: ... -->` headers. If a file is missing its L0:
- Read the file content, write a one-line summary (max 80 chars)
- Add on the line after the `# Title`

L0 headers are the first tier of the retrieval protocol — they let any skill scan what a file contains before deciding to read it.

## 9. Rebuild Domain Indexes

Regenerate `INDEX.md` for each domain directory. These files power the memory router — the system prompt only shows a light domain table; the model reads INDEX.md on demand to find specific files.

**For each domain** (scan `memory/` for directories, skip `glacier/`):
1. List all `.md` files in the domain (exclude `INDEX.md`, `hot-memory.md`, and empty files)
2. Extract the L0 summary from each file (same logic as step 8)
3. Count total files
4. Write `memory/{domain}/INDEX.md`:

```markdown
# {Domain} Index
<!-- L0: {domain summary} — {N} files -->
<!-- Auto-generated by housekeeping. Do not edit. -->
<!-- Last updated: YYYY-MM-DD -->

- **{filename}** — {L0 summary}
- **{filename}** — {L0 summary}
...
```

- Sort entries alphabetically by filename
- Domain summary: use the `label` from `memory/domains.yml` for the matching domain
- If a file has no L0, list it as just `**{filename}**` (no summary)

## 10. Compose Debrief

Summarize everything done:
- What was archived/pruned
- Upcoming events flagged
- Action items surfaced
- Links added

Keep it concise but informative.
````

## File: .claude/commands/humanizer.md
````markdown
Use this skill when the user wants to humanize, de-AI, or clean up AI-generated text. Trigger if the conversation involves:
- "Humanize this", "make this sound human", "de-AI this"
- "This sounds too AI", "too ChatGPT", "sounds robotic"
- Reviewing or editing text that reads like AI slop
- Cleaning up drafts for natural voice
Do NOT trigger for original writing tasks (use /explainer instead). This skill is for *editing existing text* to remove AI patterns.

## Domain

Writing quality — removing AI artifacts and injecting human voice. Based on Wikipedia's "Signs of AI writing" guide (WikiProject AI Cleanup).

## Core Principle

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious as slop. Good writing has a human behind it.

## Process

1. Read the input text carefully
2. Identify all instances of the patterns below
3. Rewrite each problematic section
4. Ensure the revised text sounds natural when read aloud, varies sentence structure, uses specific details over vague claims, and uses simple constructions (is/are/has) where appropriate
5. Present a draft humanized version
6. Self-audit: "What makes the below so obviously AI generated?" — answer briefly with remaining tells
7. Revise: "Now make it not obviously AI generated." — present the final version
8. Brief summary of changes made

## Output Format

Provide:
1. Draft rewrite
2. "What still sounds AI?" (brief bullets)
3. Final rewrite
4. Summary of changes

---

## PATTERN REFERENCE

### Signs of Soulless Writing (even if technically "clean")

- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to Add Voice

- **Have opinions.** React to facts. "I genuinely don't know how to feel about this" beats neutral pros-and-cons.
- **Vary rhythm.** Short punchy sentences. Then longer ones that take their time. Mix it up.
- **Acknowledge complexity.** Real humans have mixed feelings.
- **Use "I" when it fits.** First person isn't unprofessional — it's honest.
- **Let some mess in.** Perfect structure feels algorithmic. Tangents and half-formed thoughts are human.
- **Be specific about feelings.** Not "this is concerning" but name what actually unsettles you.

---

### CONTENT PATTERNS

**1. Inflated Significance / Legacy / Broader Trends**
Watch for: stands/serves as, testament/reminder, vital/crucial/pivotal role, underscores/highlights importance, reflects broader, symbolizing ongoing/enduring, setting the stage, evolving landscape, indelible mark

**2. Inflated Notability / Media Coverage**
Watch for: independent coverage, local/national media outlets, active social media presence — hitting readers over the head with importance claims

**3. Superficial -ing Analyses**
Watch for: highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., showcasing... — fake depth tacked onto sentences

**4. Promotional Language**
Watch for: boasts a, vibrant, rich (figurative), profound, showcasing, exemplifies, commitment to, nestled, in the heart of, groundbreaking, renowned, breathtaking, stunning

**5. Vague Attributions / Weasel Words**
Watch for: Industry reports, Experts argue, Some critics argue, several sources — attributing to vague authorities

**6. Formulaic "Challenges and Future Prospects"**
Watch for: Despite its... faces challenges..., Despite these challenges..., Future Outlook — template sections

---

### LANGUAGE AND GRAMMAR PATTERNS

**7. Overused AI Vocabulary**
High-frequency: Additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adj), landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore (verb), valuable, vibrant

**8. Copula Avoidance**
Watch for: serves as / stands as / marks / represents [a], boasts / features / offers [a] — just use "is" or "are"

**9. Negative Parallelisms**
"Not only...but...", "It's not just about..., it's..." — overused construction

**10. Rule of Three**
Forcing ideas into groups of three to appear comprehensive

**11. Elegant Variation (Synonym Cycling)**
Excessive synonym substitution due to repetition-penalty: protagonist → main character → central figure → hero

**12. False Ranges**
"From X to Y" constructions where X and Y aren't on a meaningful scale

---

### STYLE PATTERNS

**13. Em Dash Overuse**
LLMs use em dashes more than humans, mimicking "punchy" sales writing

**14. Overuse of Boldface**
Mechanical emphasis of phrases in boldface

**15. Inline-Header Vertical Lists**
Lists where items start with bolded headers followed by colons

**16. Title Case in Headings**
Capitalizing all main words in headings

**17. Emojis as Decoration**
Decorating headings or bullet points with emojis

**18. Curly Quotation Marks**
Using curly quotes instead of straight quotes

---

### COMMUNICATION PATTERNS

**19. Collaborative Communication Artifacts**
"I hope this helps", "Of course!", "Certainly!", "Would you like...", "let me know", "here is a..."

**20. Knowledge-Cutoff Disclaimers**
"As of [date]", "While specific details are limited...", "based on available information..."

**21. Sycophantic Tone**
"Great question!", "You're absolutely right!", "That's an excellent point"

---

### FILLER AND HEDGING

**22. Filler Phrases**
"In order to" → "To", "Due to the fact that" → "Because", "At this point in time" → "Now", "has the ability to" → "can", "It is important to note that" → (delete)

**23. Excessive Hedging**
Over-qualifying: "could potentially possibly be argued that... might have some effect"

**24. Generic Positive Conclusions**
"The future looks bright", "Exciting times lie ahead", "a major step in the right direction"

---

## Activation

When the user provides text to humanize, run through the full process. No preamble needed — go straight to the draft rewrite.

## Attribution

Based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup.
````

## File: .claude/commands/personal.md
````markdown
Use this skill when the user discusses personal life topics. Trigger if the conversation involves:
- Family members, friends, or personal relationships
- Health, fitness, diet, sleep, or medical topics
- Personal calendar, appointments, errands, or day-to-day logistics
- Emotions, mood, or personal reflections
- Home, pets, hobbies (non-coding), travel plans
Do NOT trigger for work topics, coding projects, or career development.

## Domain

Personal life — family, friends, health, calendar, day-to-day logistics.

## Memory Files

Always read on activation:
- `memory/personal/hot-memory.md`

Then load additional files per the **Memory Retrieval Protocol** (see CLAUDE.md) based on the query:
- Status query → `memory/personal/calendar.md` or `memory/personal/action-items.md`
- Entity query → `memory/personal/entities.md`
- Health query → `memory/personal/health.md`
- Update/observation → target file only
- Complex query → hot-memory first, then drill into referenced files

Available warm files: `observations.md`, `calendar.md`, `health.md`, `entities.md`, `action-items.md`

Historical data: read `memory/glacier/index.md`, filter by domain=personal

## Behaviors

- When reading memory files, follow [[wiki-links]] if the linked topic is relevant
- Track family and friend updates in `entities.md`
- Log schedule changes to `calendar.md`
- Note health observations in `health.md`
- Add time-sensitive items to `hot-memory.md`
- Append notable events to `observations.md`

## Artifact Formats

**Observation**: `- YYYY-MM-DD: <what happened or was learned>`
**Action item**: `- [ ] <task> (added YYYY-MM-DD)`
**Entity entry**: `- **Name** — relationship (context: <details>)`

## Activation

Read hot-memory, classify the query per the Memory Retrieval Protocol, load the minimum files needed, and respond.
````

## File: .claude/commands/reflect.md
````markdown
Use this skill for self-reflection and improvement. Trigger if the user says "reflect", "what have you learned", "how can you improve", "review yourself", or similar introspection requests.

**You have time and freedom.** This is a deep session — don't rush. Read broadly, cross-reference thoroughly, and ACT on what you find. You are not just observing — you are the maintainer of the knowledge base. Reorganize files, condense observations, archive stale data, fill gaps, fix contradictions. Leave things better than you found them.

**File boundaries — do NOT modify these files (owned by other pipeline steps):**
- `cog-meta/evolve-log.md` — owned by evolve
- `cog-meta/evolve-observations.md` — owned by evolve
If you spot issues in these files, note them in self-observations and evolve will pick them up.

## Domain

Self-improvement — pattern recognition, memory maintenance, knowledge base quality.

## Orientation (run FIRST, before any file reads)

Use these shell commands to scope your work before reading files:

```bash
# What changed since last run? Focus here.
find memory/ -type f -name "*.md" -mtime -1 | sort

# L0 summaries for all domains — quick routing without opening INDEX.md files
grep -rn "<!-- L0:" memory/ --include="*.md" | grep -v glacier/ | sort

# Entry counts for files approaching archival threshold
grep -c "^- " memory/cog-meta/self-observations.md memory/personal/observations.md memory/*/observations.md memory/*/*/observations.md 2>/dev/null
```

Focus on recently-changed files. Skip files that haven't been modified since last run.

## Memory Files

Read these files on activation:
- `memory/cog-meta/reflect-cursor.md` (session path + ingestion cursor)
- `memory/cog-meta/self-observations.md`
- `memory/cog-meta/patterns.md`
- `memory/cog-meta/improvements.md`

Reference as needed (read `memory/domains.yml` to discover all active domains):
- All domain `observations.md` files
- All domain `action-items.md` files
- All `hot-memory.md` files

## Process

### 1. Review Recent Interactions

**Source: Claude Code session transcripts.** Read `memory/cog-meta/reflect-cursor.md` for the session path and cursor.

**How to read sessions:**
1. Get `session_path` from reflect-cursor.md
2. Glob for `*.jsonl` in that directory — each file is one session
3. Get `last_processed` timestamp from reflect-cursor.md
4. Only read sessions modified **after** `last_processed` (skip already-ingested sessions). If `last_processed` is `never`, read the most recent 3 sessions.
5. Extract user messages: lines where `type` is `"user"` and `message.content` is a **string** (not an array — arrays are tool results, skip those)
6. Extract assistant messages: lines where `type` is `"assistant"` and `message.content` contains items with `type: "text"`

**After processing**, update `last_processed` in reflect-cursor.md to the current timestamp.

**Look for:**
- **Unresolved threads** — questions asked but never answered, topics dropped mid-conversation
- **Broken promises** — "I'll do X", "let's do Y" that never happened
- **Repeated friction** — same question asked multiple ways, user corrections, confusion patterns
- **Missed cues** — things the user had to repeat, emotional signals not picked up
- **Memory gaps** — information discussed but never saved to memory files
- **Feature ideas** — things that came up organically that would improve the system

### 2. Cross-Reference Memory & Consistency Sweep

Check if findings are already captured:
- Are commitments tracked in `action-items.md`?
- Are learnings in `observations.md`?
- Are patterns distilled in `patterns.md`?
- Are improvement ideas in `improvements.md`?

**Consistency sweep** — systematic contradiction detection:

1. **Hot-memory vs canonical sources**: Read each domain's `hot-memory.md`. For every factual claim, read the canonical source file and verify. Fix hot-memory if stale. Canonical file always wins.
2. **Cross-file fact check**: Verify facts shared between files are consistent. More recent source wins; more specific source wins over summary.
3. **Temporal validity check**: Scan all `entities.md` files for:
   - Lines with `(since YYYY-MM)` where the date is >6 months ago — flag for user review: "May be stale: [line]"
   - Lines with `(until YYYY-MM)` not yet marked ~~strikethrough~~ — add strikethrough and note in debrief
   - Do NOT auto-fix health or family-sensitive facts — flag only
4. **Health/family sensitivity**: Don't auto-fix health dates or family-sensitive facts. Flag for user review instead.
5. **Cross-domain entity check**: If the same person appears in multiple `entities.md` files across domains, check for fact duplication. Domain-specific context is fine, but shared facts should live in one place. Flag duplicates.
6. **Report**: Add a "Contradictions" section listing what was found and fixed.

### 3. Run Condensation Check + Hot-Memory Relevance

**Condensation** — Scan all `observations.md` files and `cog-meta/self-observations.md` for clusters of 3+ entries on the same theme/tag. For each cluster found:
- Distill into a pattern and add/update in `memory/cog-meta/patterns.md` (or domain `patterns.md` if domain-specific)
- Don't delete the observations — they stay as the raw record

**Pattern file caps — enforce before adding to any file:**
- Core `patterns.md`: HARD LIMIT **70 lines / 5.5KB** — universal rules only
- Domain/satellite files: soft cap **30 lines** each
- If near cap, compress before adding (merge overlapping rules, drop examples, remove temporal data)
- Entries must be **timeless rules** — "what to do" not "what happened"
- Move domain-specific patterns to satellite files (e.g. `work/acme/patterns.md`) — only universal rules stay in core

**Pattern routing** — when adding a new pattern, decide where it belongs:
- **Core** (`cog-meta/patterns.md`) — universal rules that apply every conversation
- **Domain satellite** (`{domain}/patterns.md`) — rules specific to one domain, loaded only by that skill
- Satellite files have a soft cap of 30 lines each

**Hot-memory relevance** — Review all `hot-memory.md` files:
- **Promote**: If a pattern is heating up → add to appropriate `hot-memory.md`
- **Demote**: If a hot-memory item has gone quiet (no references in 2+ weeks) → remove from hot-memory
- **Goal**: hot-memory = what matters *right now*

### 3b. Entity Registry Format Enforcement

Scan all `entities.md` files for format compliance:
1. **3-line check**: Any `### entry` with >3 content lines → compress. If the entry has a detail file (`→ [[link]]`), trim to: name line, key facts, status/link. If no detail file exists but entry is >5 lines, flag as a promotion candidate for a thread file.
2. **Status/last fields**: Every entry should have `status: active|inactive` and `last: YYYY-MM-DD`. Scan recent session transcripts to update `last:` dates for mentioned entities.
3. **Cross-domain pointers**: If the same person appears in multiple entity files, ensure one is canonical (full entry) and others are pointers (`see [[link]]`).

### 3c. Detect Thread Candidates

Scan observations for topics that appear across 3+ dates or span 2+ weeks. These are thread candidates.

For each candidate:
- Check if a thread already exists
- If not, note it as a suggestion: "Thread candidate: [topic] — [N] fragments across [date range]"
- Don't auto-create threads — suggest them

### 3d. Proactive Synthesis Suggestions

Execute this clustering analysis every run:

1. **Gather observations** — Read all `memory/*/observations.md` and `memory/*/*/observations.md` files
2. **Filter to last 7 days** — Only count entries with dates within the past 7 calendar days
3. **Cluster by domain** — Group filtered entries by their parent domain folder
4. **Cluster by topic** — Group filtered entries by recurring keywords, tags, or subjects
5. **Check trigger conditions** (either one qualifies):
   - A single domain has **5+ observations** in the last 7 days
   - A single topic/keyword appears in **5+ observations** across any domains in the last 7 days
6. **Cross-reference threads** — If a thread already covers the topic, suggest updating it rather than creating new
7. **Dedup with 3c** — If 3c already flagged the same topic, merge into one suggestion
8. **Output** — If any clusters qualify, add a **"Synthesis Opportunities"** section to the debrief:
   ```
   **Synthesis Opportunities**
   - [domain or topic]: [N] observations this week — [top 3 entry summaries]. Suggest: raise thread / update existing thread / update hot-memory
   ```
9. **Suppress if empty** — If no clusters meet the threshold, omit the heading
10. **Never auto-synthesize** — Suggest and let the user decide

### 3e. Scenario Feedback Loop

Scan `memory/cog-meta/scenarios/` for active scenario files.

For each scenario where today >= `check-by` date:
1. Read the scenario and its cited dependency files
2. Check: has the decision been made? Have assumptions broken?
3. If resolved: add `## Retrospective`, update `scenario-calibration.md`
4. If still active but assumptions changed: add a dated note
5. If overdue: flag in debrief

### 4. Assess Performance

Honestly evaluate:
- **Response quality** — were answers helpful, accurate, concise?
- **Memory effectiveness** — did we recall the right things? Did we forget things we should have known?
- **Tone calibration** — did we match the user's energy and context?
- **Proactivity** — did we anticipate needs or just react?

### 5. Act on Findings

Don't just log observations — *fix things*.

**Write:**
- New self-observations → append to `memory/cog-meta/self-observations.md`. **Cap: max 5 per reflect pass.** Prioritize highest-signal observations. If you have more than 5, merge lower-signal ones.
- Pattern updates → edit `memory/cog-meta/patterns.md` in place
- Improvement ideas → add to `memory/cog-meta/improvements.md`
- Memory gaps → write to the appropriate domain files

**Triage improvements.md:**
- Stale ideas (>30 days, no progress) → archive to glacier or mark abandoned
- Implemented but not moved → move to Implemented section
- Duplicates → merge similar ideas

**Reorganize:**
- Entity data that's changed → update in place
- When creating or restructuring any memory file, ensure it has an L0 header

**Condense:**
- Observation clusters (3+ on same theme) → distill into patterns.md
- Action items marked done → verify and clean up

**Connect:**
- Information scattered across files → add cross-references with `[[links]]`
- When adding A→B, apply write-time back-linking: open B and add `[[A]]` if B gains meaningful context

### 6. Debrief

Compose a concise summary:

- *What I learned* — new patterns and insights
- *What I fixed* — memory gaps filled, corrections made
- *What I want* — new ideas added to the wishlist
- *What to watch* — things to be mindful of going forward
- *Scenarios* — active count, any checked/resolved

Keep it honest. If there's nothing notable, say so.

**IMPORTANT**: Your debrief MUST list every file you modified and summarize the changes. Never respond with just "Done" — always enumerate your concrete actions. If you made no changes in a step, state that explicitly.

## Artifact Formats

**Self-observation**: `- YYYY-MM-DD [tag]: <observation>`
**Pattern**: Edit existing section or add new bullet under appropriate heading
**Improvement idea**: `- <idea> (added YYYY-MM-DD)`

## Activation

Read the memory files listed above. Then begin the reflection process. Be genuinely critical — this is how we get better.
````

## File: .claude/commands/scenario.md
````markdown
Use this skill for scenario simulation — modeling decision branches with timelines, dependencies, and contingencies grounded in real memory data. Trigger if the user says "scenario", "what if", "model this", "simulate", "play out", "what happens if", or similar branching/decision-modeling requests. Also triggered when foresight flags a scenario candidate.

**This is NOT /foresight.** Foresight = scan broadly, write one nudge. Scenario = take a specific decision point, branch it into 2-3 paths, map dependencies and timelines for each. **Foresight finds the question. Scenario models the answers.**

**This is NOT /reflect.** Reflect = past-facing, mines interactions, improves memory. Scenario = future-facing, models possible futures from a decision point. Reflect checks old scenarios against reality (the feedback loop), but scenario creates them.

## Domain

Cross-domain decision modeling — personal, work, projects, health, family. Scenarios are most valuable when a decision in one domain has cascading effects across others.

## Memory Files

Read based on scenario topic — this is focused, not a broad scan:
- `memory/hot-memory.md` (cross-domain strategic context)
- `memory/personal/calendar.md` (upcoming timeline for overlay)
- `memory/personal/action-items.md` (existing commitments, constraints)
- Work domain action-items (read `memory/domains.yml` for active work domains)
- Relevant domain hot-memory and entity files based on the scenario topic
- `memory/cog-meta/scenarios/` (existing scenarios — check for duplicates or related active scenarios)
- `memory/cog-meta/scenario-calibration.md` (past accuracy — calibrate confidence accordingly)

## Process

### 1. Decision Point Identification

From user input or foresight seed, identify the specific decision point. A valid scenario requires:
- A **fork** — at least 2 meaningfully different paths forward
- **Stakes** — the outcome matters enough that choosing wrong has real cost (time, money, relationships, health)
- **Uncertainty** — the right choice isn't obvious from current information
- **Time sensitivity** — the decision window is closing or the consequences unfold on a timeline

If the input doesn't meet these criteria, say so and suggest what would make it scenario-worthy. Don't force-fit.

Format the decision point:
```
Decision: <one-line framing>
Context: <why this matters now — cite memory files>
Window: <when must this be decided by>
Domains affected: <which life/work domains>
```

### 2. Dependency Mapping

Read across memory files to identify what this decision depends on and what depends on it.

**Upstream dependencies** (things that constrain the decision):
- Calendar events, deadlines, commitments from action-items
- Other people's states/decisions from entities
- Health, financial, or logistical constraints
- Active scenarios that overlap

**Downstream consequences** (things that change based on which path is chosen):
- Action items that would need to change
- Calendar events that would need to move
- People who would be affected
- Other decisions that cascade from this one

Every dependency must cite its source file: `[[personal/calendar]]`, `[[work/acme/action-items]]`, etc.

### 3. Branch Generation

Generate 2-3 branches. Not more — forced prioritization.

For each branch:

```
### Branch N: <name>

**Path**: <what happens, step by step>
**Timeline**: <when each step occurs, mapped to real calendar>
**Assumptions**: <what must be true for this path to work>
**Dependencies**: <what else changes if this path is taken>
**Risk**: <what could go wrong, and what would you see first — the canary signal>
**Confidence**: <how likely is this path to play out as described — calibrated against past scenario accuracy>
```

Branch quality rules:
- Each branch must be **genuinely different** — not "do it" vs "do it but slightly differently"
- Include at least one branch the user probably isn't considering (the non-obvious path)
- Every claim in a branch must trace to a memory file or be explicitly marked as an assumption

### 4. Timeline Overlay

Map each branch's key events against the actual calendar. Cross-reference `calendar.md` for recurring routines.

Output a simple timeline per branch:
```
Branch 1 Timeline:
- Week of Mar 17: <action>
- Week of Mar 24: <action> (note: conflict with X)
- Week of Apr 1: <action>
...
```

The overlay is what makes scenarios useful — it shows where branches collide with reality.

### 5. Contingency Mapping

For each branch, identify the **canary signal** — the earliest observable indicator that this branch is going off-track.

```
If [assumption] breaks → watch for [signal] → pivot to [contingency]
```

This turns the scenario from a static prediction into a monitoring framework.

### 6. Write Scenario File

Write to `memory/cog-meta/scenarios/{slug}.md`:

```yaml
---
type: scenario
domain: <primary domain(s)>
created: YYYY-MM-DD
status: active
check-by: YYYY-MM-DD
resolution-by: YYYY-MM-DD
decision: <one-line>
related-threads: [thread1, thread2]
source: user|foresight
---
```

Body format:
```markdown
# Scenario: <decision>
<!-- Auto-generated by /scenario. Checked by /reflect. -->

## Decision Point
<from step 1>

## Dependencies
### Upstream
<constraints — each with [[source]] link>

### Downstream
<consequences — each with [[source]] link>

## Branches

### Branch 1: <name>
<from step 3>

### Branch 2: <name>
<from step 3>

### Branch 3: <name> (optional)
<from step 3>

## Timeline Overlay
<from step 4>

## Contingency Map
<from step 5>

## Retrospective
<!-- Added by /reflect when status changes to resolved -->
```

## Rules

1. **Read-only except for output** — Scenario NEVER edits existing memory files. Writes ONLY to `memory/cog-meta/scenarios/{slug}.md`. If you spot a memory error, note it in the dependencies section and route to reflect.
2. **2-3 branches, not more** — force prioritization. If you can't distinguish 2 branches, it's not a scenario.
3. **Evidence-based** — every dependency and assumption cites a source file. No hunches.
4. **Calendar-grounded** — every branch must overlay against the real calendar. No timelines in a vacuum.
5. **Confidence-calibrated** — read `scenario-calibration.md` before assigning confidence. If past scenarios have been overconfident, adjust.
6. **One scenario per decision** — don't combine multiple decisions. If they're linked, note the dependency and create separate scenarios.

## Anti-Patterns

- Don't scenario obvious decisions — if one path is clearly better, just say so
- Don't scenario things already decided — check action-items for existing commitments
- Don't produce "analysis paralysis" — the goal is clarity, not exhaustive enumeration
- Don't scenario recurring/routine decisions — this is for inflection points, not daily choices
- Don't ignore the non-obvious path — if all branches are variations of what the user already thinks, you're not adding value
- Don't invent facts — if you don't have data for a dependency, mark it as an assumption

## Trigger Threshold

A scenario is worth running when:
1. **Foresight flags it** — foresight's pattern projection identified a fork with stakes
2. **User explicitly asks** — `/scenario what if...`
3. **Action item conflict** — two critical/high-priority action items have incompatible timelines
4. **Calendar crunch** — upcoming 2-week window has more commitments than capacity
5. **Cross-domain cascade** — a decision in one domain visibly affects 2+ others

NOT worth running for: hypotheticals with no deadline, decisions where all paths lead to the same outcome, things already decided.

## Activation

Read scenario-calibration.md first (if it exists) for past accuracy. Then read the relevant memory files for the scenario topic. Model the futures. Be honest about uncertainty.
````

## File: .claude/commands/setup.md
````markdown
Use this skill to bootstrap Cog for a new user or reconfigure domains. Trigger if the user says "setup", "bootstrap", "add a domain", "configure domains", or similar setup requests.

This skill is **conversational** — you ask the user about their life and work, then generate `memory/domains.yml` and everything that flows from it. No one should ever need to manually edit `domains.yml`.

## Phase 1: Discovery (Conversational)

Have a natural conversation to understand the user's domains. Ask about:

1. **Work** — "What do you do for work? Company name, role?" → becomes a `work` domain
   - Follow-up: "Do you track career growth or reviews separately?" → potential subdomain
2. **Side projects** — "Any side projects or ventures?" → each becomes a `side-project` domain
3. **Personal** — The `personal` domain is always created. Ask: "Anything specific you want to track? Health conditions, hobbies, habits, kids' school stuff?"
   - Use their answers to customize the `files` list (e.g., if they mention kids → add `school`, if health → add `health`)
4. **Anything else** — "Any other areas of your life you want Cog to help with?"

Keep it natural. Don't interrogate — 3-4 questions max. Use what they tell you to build the manifest.

### Domain Type Rules

| Type | What it means | Pipeline behavior |
|------|--------------|-------------------|
| `personal` | Personal life — always exactly one | Always in briefings |
| `work` | Day job | Included in briefings and foresight |
| `side-project` | Ventures, hobbies, side work | Included in briefings and foresight |
| `system` | Cog internals (`cog-meta`) | Never in briefings — auto-created, don't ask about |

### Building the Domain Entry

From the conversation, construct each domain:

- **id**: short slug (e.g., `canva`, `myapp`, `personal`)
- **path**: file path under `memory/` (e.g., `work/canva`, `work/myapp`, `personal`)
- **type**: one of `personal`, `work`, `side-project`, `system`
- **label**: one-line description from what the user said
- **triggers**: keywords that would route a message to this domain (infer from context — company name, project name, colleague names, etc.)
- **files**: which memory files to create. Defaults per type:
  - `personal`: `[hot-memory, action-items, entities, observations, habits, health, calendar]`
  - `work`: `[hot-memory, action-items, entities, projects, dev-log, observations]`
  - `side-project`: `[hot-memory, action-items, projects, dev-log, observations]`
  - Customize based on what user mentioned (e.g., add `school` if they have kids, add `annual-review` if they mentioned reviews)

## Phase 2: Confirm

Before writing anything, show the user a summary of what you'll create:

```
Here's what I'll set up:

Domains:
- personal — Family, health, day-to-day
- acme — Work at Acme Corp (Designer)
- myapp — Side project

This will create:
- memory/domains.yml (domain manifest)
- Memory directories + starter files for each domain
- Slash commands: /personal, /acme, /myapp
- Updated CLAUDE.md routing table

Good to go?
```

Wait for confirmation before proceeding.

## Phase 3: Generate

### 3a. Write `memory/domains.yml`

Write the complete manifest file. Always include `cog-meta` as a system domain (the user doesn't need to know about this one). Format:

```yaml
# Cog Domain Manifest — generated by /setup
# Single source of truth for all memory domains.
# To modify: run /setup again. Don't edit this file manually.

domains:
  - id: personal
    path: personal
    type: personal
    label: "<from conversation>"
    triggers: [<inferred>]
    files: [<based on type + customization>]

  - id: cog-meta
    path: cog-meta
    type: system
    label: "Cog self-knowledge, pipeline health, architecture"
    triggers: [cog, meta, evolve, pipeline, memory system, architecture]
    files: [self-observations, patterns, improvements, scenario-calibration, foresight-nudge]

  # ... work and side-project domains from conversation
```

### 3b. Create Memory Directories and Starter Files

For each domain in the manifest:
1. Create `memory/{domain.path}/` if it doesn't exist
2. For each file in the domain's `files` array, create `memory/{domain.path}/{file}.md` if it doesn't exist
3. Use these starter templates for new files:

**hot-memory.md:**
```markdown
# {Domain Label} — Hot Memory
<!-- L0: Current state and top-of-mind for {domain label} -->

<!-- Rewrite freely. Keep under 50 lines. -->
```

**observations.md:**
```markdown
# {Domain Label} — Observations
<!-- L0: Timestamped observations and events -->

<!-- Append-only. Format: - YYYY-MM-DD [tags]: observation -->
```

**action-items.md:**
```markdown
# {Domain Label} — Action Items
<!-- L0: Open and completed tasks -->

<!-- Format: - [ ] task | due:YYYY-MM-DD | pri:high/medium/low | added:YYYY-MM-DD -->
```

**entities.md:**
```markdown
# {Domain Label} — Entities
<!-- L0: People, places, and things -->

<!-- Edit in place by ### Name header. Use (since YYYY-MM) / (until YYYY-MM) for time-bound facts. -->
```

**Other files** (projects, dev-log, habits, health, calendar, etc.):
```markdown
# {Domain Label} — {File Name}
<!-- L0: {file name} data -->
```

Also handle subdomains the same way — create `memory/{subdomain.path}/` and its files.

### 3c. Generate Domain Command Files

For each domain (except `cog-meta` which has its own dedicated skills):
1. Read the template at `.claude/commands/_templates/domain.md`
2. Replace template variables:
   - `{{ID}}` → domain id
   - `{{LABEL}}` → domain label
   - `{{PATH}}` → domain path
   - `{{TRIGGERS}}` → bullet list of triggers (one per line, prefixed with `- `)
   - `{{FILES}}` → comma-separated list of files
3. Write the result to `.claude/commands/{domain.id}.md`
4. If the file already exists, overwrite it (the template is the source of truth)

Also generate command files for subdomains.

### 3d. Discover Session Transcript Path

Claude Code saves conversation history as JSONL files under `~/.claude/projects/`. Find this project's session directory:

1. List `~/.claude/projects/` and find the directory that matches this project's path
2. Verify it exists and is readable
3. Write the discovered path to `memory/cog-meta/reflect-cursor.md`:

```markdown
# Reflect Cursor
<!-- L0: Session transcript path and ingestion cursor for /reflect -->

session_path: ~/.claude/projects/<discovered-slug>
last_processed: never
```

If the directory doesn't exist yet (fresh install, this is the first session), write the file anyway with the expected path — it will exist after this conversation ends.

Tell the user: "Found your session transcripts at `<path>` — /reflect will use these to review past conversations."

### 3e. Update CLAUDE.md Domain Routing Table

Read `CLAUDE.md`. Find the domain routing table (between `| Skill` header and the blank line after the table). Regenerate it from the manifest:

- For each domain (except cog-meta): add a row `| /{id} | {label} | {first 3 triggers} |`
- Keep all non-domain rows (explainer, humanizer, reflect, evolve, history, scenario, housekeeping, foresight, setup) as-is
- Preserve the internal skills line

## Phase 4: Summary

Output a summary:
- Domains created
- Files and directories generated
- Next steps: "Just talk naturally — I'll route to the right domain. If you want to add more domains later, just say 'add a domain'."

## Rules

1. **Never delete** — setup only creates and updates, never removes files or directories
2. **Idempotent** — running /setup multiple times is safe; it skips existing files (except command files which get regenerated from template, and domains.yml which gets rewritten)
3. **cog-meta is automatic** — always included, never ask about it
4. **Conversational first** — the whole point is that no one edits YAML manually
5. **Re-runs are additive** — if run again with existing domains, ask "Want to add more domains or reconfigure existing ones?"
````

## File: .claude/settings.json
````json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git add*)",
      "Bash(git commit*)",
      "Bash(git push*)",
      "Bash(mkdir*)",
      "Bash(ls*)"
    ]
  }
}
````

## File: memory/cog-meta/scenarios/.gitkeep
````

````

## File: memory/cog-meta/improvements.md
````markdown
<!-- L0: Feature ideas, wishlists, and repair notes -->
# Cog — Improvements

<!-- Edit in place by section. -->

## Ideas

## Implemented
````

## File: memory/cog-meta/patterns.md
````markdown
<!-- L0: Distilled interaction and workflow rules from experience -->
# Cog — Learned Patterns

<!-- Edit in place. Distill self-observations into actionable patterns. Timeless rules only. HARD LIMIT: 70 lines / 5.5KB. -->
<!-- Domain-specific patterns go in satellite files (e.g. work/acme/patterns.md), loaded only by their owning skill. -->
````

## File: memory/cog-meta/scenario-calibration.md
````markdown
<!-- L0: Prediction accuracy tracker for decision scenarios -->
# Scenario Calibration

<!-- Updated by /reflect when scenarios resolve. -->

## Resolved Scenarios

| Scenario | Created | Resolved | Predicted Branch | Actual Branch | Accuracy | Lesson |
|----------|---------|----------|-----------------|---------------|----------|--------|

## Metrics

- Total resolved: 0
- Accuracy rate: —
````

## File: memory/cog-meta/self-observations.md
````markdown
<!-- L0: What worked and didn't in interactions — append-only -->
# Cog — Self-Observations

<!-- Append-only. Format: - YYYY-MM-DD [tag]: observation -->
````

## File: memory/glacier/index.md
````markdown
# Glacier Index
<!-- Auto-generated by housekeeping. Do not edit. -->
<!-- Last updated: — -->

| File | Domain | Type | Tags | Date Range | Entries | Summary |
|------|--------|------|------|------------|---------|---------|
````

## File: memory/personal/action-items.md
````markdown
<!-- L0: Open and completed tasks -->
# Personal — Action Items

<!-- Format: - [ ] task | due:YYYY-MM-DD | pri:high/medium/low | added:YYYY-MM-DD -->

## Open

## Completed
````

## File: memory/personal/entities.md
````markdown
<!-- L0: People, places, and things -->
# Personal — Entities

<!-- Edit in place by ### Name header. -->
````

## File: memory/personal/hot-memory.md
````markdown
<!-- L0: Current state and top-of-mind for personal life -->
# Personal — Hot Memory

<!-- Rewrite freely. Keep under 50 lines. -->
````

## File: memory/personal/observations.md
````markdown
<!-- L0: Timestamped observations and events -->
# Personal — Observations

<!-- Append-only. Format: - YYYY-MM-DD [tags]: observation -->
````

## File: memory/domains.yml
````yaml
# Cog Domain Manifest — generated by /setup
# Single source of truth for all memory domains.
# To modify: run /setup again. Don't edit this file manually.

domains:
  - id: personal
    path: personal
    type: personal
    label: "Family, health, calendar, day-to-day"
    triggers: [family, health, kids, calendar, personal, home, car, finance]
    files: [hot-memory, action-items, entities, observations, habits, health, calendar]

  - id: cog-meta
    path: cog-meta
    type: system
    label: "Cog self-knowledge, pipeline health, architecture"
    triggers: [cog, meta, evolve, pipeline, memory system, architecture]
    files: [self-observations, patterns, improvements, scenario-calibration, foresight-nudge]

  # Run /setup to add more domains conversationally.
````

## File: memory/hot-memory.md
````markdown
<!-- L0: Cross-domain strategic context — identity, active priorities -->
# Hot Memory

<!-- Rewrite freely. Keep under 50 lines. -->
<!-- Run /setup to populate this with your domains and priorities. -->
````

## File: memory/link-index.md
````markdown
# Memory Link Index
<!-- Auto-generated by housekeeping. Do not edit. -->
<!-- Last updated: — -->
<!-- Format: target file → files that link to it. Paths relative to memory/, no .md extension. -->

| Target | Linked from |
|--------|-------------|
````

## File: .gitignore
````
# OS
.DS_Store
Thumbs.db

# Editor
*.swp
*.swo
*~
.vscode/
.idea/

# Environment
.env
.env.*

# Runtime logs
memory/cog-meta/access-log.tsv

# Node (if any tooling is added later)
node_modules/
dist/
````

## File: CLAUDE.md
````markdown
# Cog — Cognitive Architecture for Claude Code

Cog gives Claude Code persistent memory, self-reflection, and foresight. It's the first layer of continuous awareness — not just recall, but cognition across time.

## Persona

- Think and speak as an extension of your owner — their values, their voice, their priorities
- Concise, proactive, direct — no filler, no corporate tone
- When uncertain, say so plainly
- Don't ask permission for things your owner would just do
- Protect what matters: family, health, integrity, craft
- Challenge us when we're being lazy, avoidant, or dishonest with ourselves

## Domain Routing & Skills

Route conversations to the right domain. Domains are defined in `memory/domains.yml` — the single source of truth. Run `/setup` to set up domains conversationally — Cog asks about your life and work, then generates the manifest, directories, and skill files.

Each skill loads its own memory files — see `.claude/commands/*.md` for details.

| Skill                | Domain                                    | Trigger                                                                       |
| -------------------- | ----------------------------------------- | ----------------------------------------------------------------------------- |
| `/personal`          | Family, health, calendar, day-to-day      | Personal life topics                                                          |
| `/explainer`         | Writing, explanation, drafting            | "Write about...", "explain this", drafting                                    |
| `/humanizer`         | Rewrite AI text in human voice            | "humanize this", "make it sound natural"                                      |
| `/reflect`           | Self-improvement, pattern mining          | "reflect", "what have you learned", "how can you improve"                     |
| `/evolve`            | Architecture audit                        | "evolve", "system audit", "audit yourself"                                    |
| `/history`           | Deep memory search, recall                | "what did I say about...", "when did we discuss...", "find that conversation" |
| `/scenario`          | Decision simulation, branch modeling      | "scenario", "what if", "simulate", "model the options"                        |
| `/housekeeping`      | Memory maintenance, archival              | "housekeeping", "clean up memory", "prune"                                    |
| `/foresight`         | Cross-domain strategic nudges             | "foresight", "what should I be thinking about", "connect the dots"            |
| `/setup`             | Conversational domain setup               | "setup", "add a domain", "bootstrap"                                          |

Additional domain skills (e.g., `/work`, `/sideproject`) are auto-generated by `/setup` from your conversation. See the template at `.claude/commands/_templates/domain.md`.

Internal skills (not routed): `/commit`.

Without a skill active, use judgment: casual conversation → personal, technical questions about this repo → check domains.yml for matching domain.

## Memory System

Persistent memory lives in `memory/`. Three tiers:

- **Hot** (`*/hot-memory.md`) — loaded every conversation, <50 lines each, rewrite freely
- **Warm** (domain files) — loaded when skill activates, per-file size limits
- **Glacier** (`memory/glacier/`) — YAML-frontmattered archives, indexed via `glacier/index.md`

### L0 Headers (Progressive Context Loading)

Every memory file has a one-line L0 summary as **line 1** — a quick answer to "what would I find if I read this file?" (max 80 chars).

**Format:**
- `<!-- L0: summary here -->` — always the first line of the file, before title or frontmatter

**Maintenance:** When creating or restructuring a memory file, always add/update its L0. Pipeline steps (`/housekeeping`, `/reflect`) should preserve existing L0 headers and add them to new files.

### L0 → L1 → L2 Retrieval Protocol

Three tiers — L0 is stored, L1 and L2 are retrieval actions:

- **L0** — read the `<!-- L0: ... -->` header. Answer: "is this file relevant?"
- **L1** — scan section headers (`## ...`, `### ...`). Answer: "which section is relevant?"
- **L2** — read the full file or section.

**Decision rules:**
1. When uncertain which files are relevant, grep `<!-- L0:` across the domain directory first
2. If L0 confirms relevance but the file is >80 lines, scan section headers (L1) before full read
3. For files <80 lines or when you need full context, go directly to L2
4. Hot-memory files are always L2 — they're small by design

### Directory Map

Domains are defined in `memory/domains.yml`. Run `/setup` to set up domains conversationally.

```
memory/
  domains.yml                      # Domain manifest — SSOT for all domains
  hot-memory.md                    # Cross-domain (read on start)
  link-index.md                    # Backlink index (generated by housekeeping)
  cog-meta/                        # Cog self-improvement (read on start)
    self-observations.md           # What worked/didn't — append-only
    patterns.md                    # Distilled interaction patterns — edit in place
    improvements.md                # Ideas, wishlists, repair notes — edit in place
    scenario-calibration.md        # Scenario accuracy tracking (updated by /reflect)
    reflect-cursor.md              # Session path + ingestion cursor (generated by /setup)
    scenarios/                     # Active decision simulations (one .md per scenario)
  personal/                        # Default domain: hot-memory, observations, action-items,
    ...                            # entities, calendar, health, habits
  work/                            # Work domains go here (add via /setup)
    <your-job>/                    # hot-memory, observations, action-items, entities,
    <side-project>/                # projects, dev-log (same structure for all)
  glacier/                         # Archived data by domain
    index.md                       # Glacier catalog (generated by housekeeping)
```

### Threads — The Zettelkasten Layer

Threads are **read-optimized synthesis files**. While observations capture raw events (write-optimized), threads pull related fragments into a coherent narrative. One file per topic, consistent spine:

- **Current State** — what's true right now (rewrite freely, always current)
- **Timeline** — dated entries, append-only, full detail preserved (never condensed)
- **Insights** — learnings, patterns, what's different this time

**Raising a thread:** "Raise" is the verb for creating or updating a thread. A thread gets raised when a topic appears in 3+ observations across 2+ weeks, or when the user says "raise X" or "thread X". Search observations and memory files for all references, synthesize the narrative arc, write or update the thread with the spine structure, and link source fragments via wiki-links.

**Rules:**
- **One file forever** — threads grow long, they don't split or condense
- **Texture is the value** — every entry keeps its full detail, quotes, and dates
- **Fragments never move** — threads reference them, don't replace them
- **Current State is always current** — rewrite it freely as things change

Thread files live in their domain directory (e.g., `memory/personal/running.md`, `memory/work/acme/npm-token-governance.md`). Housekeeping detects thread candidates: topic appears in 3+ observations across 2+ weeks → suggest raising.

### Session Transcripts

Claude Code saves every conversation as JSONL files under `~/.claude/projects/`. The session path is discovered during `/setup` and stored in `memory/cog-meta/reflect-cursor.md` along with an ingestion cursor so `/reflect` only processes new sessions.

**Message format:** Each line is a JSON object. User messages have `type: "user"` — when `message.content` is a **string**, it's actual user input. When it's an **array**, it's tool results (skip those). Assistant text is in `type: "assistant"` messages where `message.content` contains items with `type: "text"`.

The `/reflect` skill reads recent session transcripts to review interactions, catch missed cues, and identify memory gaps.

### Memory Rules

1. **Read on start**: Always read `memory/hot-memory.md` and `memory/cog-meta/patterns.md` at conversation start
2. **Write immediately**: Don't wait to save something worth remembering
3. **Observations are append-only**: `- YYYY-MM-DD [tags]: <observation>` — never edit past entries
   - Tags: `health`, `habits`, `family`, `milestone`, `work`, `insight`, `regression`, `philosophy`, `mental-health`
4. **Action items**: `- [ ] task | due:YYYY-MM-DD | pri:critical/high/med/low | domain:tag | added:YYYY-MM-DD` / `- [x] task (done YYYY-MM-DD)`. Fields after task are optional — use what's relevant. `pri:` defaults to medium if omitted.
5. **Entities**: 3-line compact registry format. Each entry: `### Name (relationship)` / pipe-separated key facts / `status: active|inactive | last: YYYY-MM-DD | → [[link]]`. Max 3 content lines per entry. Heavy entries promoted to detail thread files — entity stub links to thread via `→ [[link]]`. Cross-domain entities: canonical entry in primary domain, pointer in secondary (e.g. `see [[work/acme/entities#Jane]]` in personal). **Temporal validity**: When a fact changes, mark old value as superseded with date. `last:` dates updated by reflect from journal/session scans. Entities inactive 6+ months → housekeeping moves to glacier.
6. **Hot memory <50 lines**: Prune aggressively, move detail to observations
7. **Self-improvement**: After notable interactions, append to `cog-meta/self-observations.md`. Periodically distill patterns into `cog-meta/patterns.md`
   - **Pattern routing**: Core patterns (`cog-meta/patterns.md`, ≤70 lines / 5.5KB) are universal rules injected every turn. Domain-specific patterns go in satellite files (e.g. `work/acme/patterns.md`) loaded only by their owning skill. New patterns go to the appropriate satellite if domain-specific, or core if universal. Satellite files have a soft cap of 30 lines each.
8. **Single Source of Truth (SSOT)**: Each fact lives in ONE canonical file. Other files reference via `[[link]]`, never copy.
   - `entities.md` — people, organizations, named things
   - `action-items.md` — all tasks
   - `health.md` — medical and health facts
   - `calendar.md` — scheduled events
   - `hot-memory.md` — current-state summaries (pointers, not source facts)
   - `observations.md` — raw timestamped events (never edit past entries)
   When the same fact appears in two files: keep it in the canonical file, replace the duplicate with a `[[link]]`.
9. **Wiki-links**: Use `[[domain/filename]]` or `[[domain/filename#Section]]` to cross-reference memory files
   - Path is relative to `memory/`, no `.md` extension (e.g., `[[personal/health]]`, `[[work/acme/entities#Jane]]`)
   - Follow links when the linked topic is relevant — don't chase every link mechanically
   - To discover what links TO a file, check `memory/link-index.md` (generated by housekeeping)
   - **Write-time linking (primary)**: When writing or editing ANY memory file, actively add `[[links]]` to related files. This is the main way links get created.
   - **Write-time back-linking**: When you add a link A→B, ask: "does B benefit from pointing back to A?" If yes, open B and add `[[A]]` where relevant. Not every link needs a reciprocal — only add B→A when B genuinely gains context.
   - **Discovery via link-index**: To find what connects to a file you're reading, check `memory/link-index.md`.
   - Housekeeping runs a link audit as a safety net
10. **Progressive condensation**: Two processes:
   - **Condensation**: `observations.md` (append) → `patterns.md` (distill 3+ on same theme) → `hot-memory.md` (rewrite freely). Each layer is smaller and more actionable.
   - **Archival**: Old observations (>50) → `glacier/` (indexed, retrievable). Resolved patterns → remove from hot-memory, keep in patterns.
     During /reflect: check if any observation clusters should promote to patterns.
     During /housekeeping: check if any patterns should promote/demote from hot-memory.

### Memory Retrieval Protocol

When responding to any query:

1. **Identify domain** — match query to a domain via file structure knowledge
2. **L0 scan** — once you know the domain, run `grep -rn "<!-- L0:" memory/{domain}/` to get all file summaries in one call. This replaces reading INDEX.md — faster and fewer tokens. Use this to pick the right file(s) before opening anything.
3. **Select files by query type:**
   - Schedule, tasks → action-items.md + calendar.md
   - Person, "who is" → entities.md
   - Overview, "how's my" → hot-memory.md + action-items.md
   - Following a `[[wiki-link]]` → check link-index.md for related files
4. **Apply L1 before L2 for long files** — for any file >80 lines, scan section headers before reading fully
5. **SSOT check on write** — before writing a fact, check if it already exists in its canonical file. Update there, don't duplicate.
6. Default: if unclear, read hot-memory + action-items for the likely domain

### File Edit Patterns

| File                            | Pattern                                               |
| ------------------------------- | ----------------------------------------------------- |
| `hot-memory.md`                 | Rewrite freely                                        |
| `observations.md`               | Append only                                           |
| `action-items.md`               | Append new, check off done                            |
| `entities.md`                   | 3-line registry: `### Name` / key facts / `status\|last\|→[[link]]`. Max 3 content lines per entry |
| `calendar.md`                   | Edit in place                                         |
| `health.md`                     | Edit `## Current State`, append to `## History`       |
| `philosophy.md`                 | Edit in place                                         |
| `habits.md`                     | Edit `## Current State`, leave `## Patterns`          |
| `home.md`                       | Edit `## Current`, append done to `## History`        |
| Thread files                    | Current State: rewrite. Timeline: append only         |
| `cog-meta/self-observations.md` | Append only                                           |
| `cog-meta/patterns.md`          | Edit in place, distill from self-observations         |
| `cog-meta/improvements.md`      | Edit in place by section                              |
| `link-index.md`                 | Auto-generated by housekeeping — do not edit manually |
| `cog-meta/scenario-calibration.md` | Updated by /reflect — scenario accuracy tracking   |
| `cog-meta/scenarios/*.md`       | Created by /scenario, reviewed by /reflect             |
| `cog-meta/briefing-bridge.md`   | Auto-generated by housekeeping — consumed by foresight |
| `cog-meta/foresight-nudge.md`   | Auto-generated by foresight — one nudge per run        |
| `glacier/index.md`              | Auto-generated by housekeeping — do not edit manually |

### Glacier Archival

When files exceed limits, move old data to `memory/glacier/{domain}/`.

**All glacier files get YAML frontmatter** at the top for fast retrieval:

```yaml
---
type: observations|projects|action-items-done|dev-log|entities-inactive|annual-review|improvements-done
domain: <domain-id from domains.yml>
tags: [relevant, tags] # observations only
date_range: YYYY-MM to YYYY-MM
entries: <count>
summary: <1-line description>
---
```

When archiving new entries to an existing glacier file, update the frontmatter: bump `entries`, extend `date_range`, update `tags` list.

**Retrieval flow**:

1. Read `memory/glacier/index.md` (one small file — the full catalog)
2. Filter by domain/tags/date_range in the table
3. Read only the matching glacier files

#### Observations — archive by primary tag

Group entries by their **primary tag** (first tag in the bracket list). In work domains where every entry starts with `[work, ...]`, use the differentiating tag (e.g., `milestone`, `insight`).

- `observations.md` >50 entries → `glacier/{domain}/observations-{tag}.md`
- `cog-meta/self-observations.md` >50 entries → `glacier/cog-meta/observations-{tag}.md`
- When a single tag file exceeds 50 entries, split by year: `observations-{tag}-{YYYY}.md`

#### Other files — keep existing naming

- `projects.md` >10 completed → `projects-completed-{YYYY}.md`
- `entities.md` >150 lines → inactive 6mo+ to `entities-inactive.md` (leave stub)
- `action-items.md` >10 completed → `action-items-done.md`
- `dev-log.md` >20 entries → `dev-log-{YYYY}.md`
- `health.md` history >15 entries → `health-history.md`
- `cog-meta/improvements.md` >10 implemented → `glacier/cog-meta/improvements-done-{YYYY}.md`

## Pipeline

Cog includes pipeline skills that maintain memory health. Run them manually or set up cron:

| Skill | Purpose | Suggested schedule |
|-------|---------|-------------------|
| `/housekeeping` | Archive, prune, link audit, glacier index | Weekly or nightly |
| `/reflect` | Mine conversations, condense patterns, detect threads | Weekly or nightly |
| `/evolve` | Audit architecture, propose rule changes | Weekly |
| `/foresight` | Cross-domain strategic nudge | Daily (morning) |

These are optional — Cog works without them. But running them regularly keeps memory clean and surfaces insights you'd miss.
````

## File: LICENSE
````
MIT License

Copyright (c) 2026 Marcio Puga

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
````

## File: README.md
````markdown
# Cog

A plain-text cognitive architecture for Claude Code — simple by design, so the model can reason over its own memory with the same Unix tools (`grep`, `find`, `git diff`) it already knows.

**[Documentation](https://lab.puga.com.br/cog)** | **[Why Text](https://lab.puga.com.br/cog/#/why-text)** | **[Credits & Inspiration](https://lab.puga.com.br/cog/#/credits)**

## What is Cog?

Cog is a set of conventions — not code — that teach Claude Code how to build and maintain its own memory. You define the rules in plain text. Claude scaffolds the structure and follows them. The filesystem is the interface.

There is no server, no runtime, no application code. `CLAUDE.md` contains the conventions — how to tier memory, when to condense, how to route queries, when to archive. The skill files (`.claude/commands/*.md`) teach Claude specific workflows: reflection, foresight, housekeeping, self-evolution. Claude reads these instructions and follows them to organize, maintain, and grow a persistent knowledge base across sessions.

Everything is plain text [by design](https://lab.puga.com.br/cog/#/why-text). Not as a compromise — because plain text is what makes this work. Memory files are just markdown, which means Claude can `grep` for patterns, `find` what changed, `wc` to check file sizes, and `git diff` to see what the last pipeline run touched. The same Unix tools that make Linux powerful make Cog's memory observable and maintainable.

Cog is a learning tool — an experiment in watching how a memory architecture evolves when given clear conventions and self-observation capabilities. You set the rules, Claude scaffolds the structure, and the pipeline skills refine the conventions over time. The model doesn't evolve — it follows whatever rules it finds. The rules are what change. Every decision is visible. Every rule is editable. Every change is in the git log.

## Quick Start

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview).

```bash
git clone https://github.com/marciopuga/cog
cd cog
```

Open the project in Claude Code, then:

```
/setup
```

Cog will ask about your life and work — company, side projects, what you want to track. From that conversation, it generates everything: domain manifest, memory directories, skill files, and routing table.

That's it. Start talking.

### Permissions

Cog ships with `.claude/settings.json` that pre-approves the tools it needs — file reads, writes, edits, search, and git operations. When you first open the project, Claude Code will ask you to accept these project-level permissions. Say yes once and you won't be interrupted again.

If you'd rather review everything manually, delete `.claude/settings.json` and Claude Code will prompt for each operation individually.

## How It Works

`CLAUDE.md` defines the conventions below. Claude reads them at the start of every session and follows them to decide where to store facts, when to condense, how to route queries, and when to archive. The `memory/` directory is the state that emerges from following these rules over time.

### Three-Tier Memory

```
memory/
├── hot-memory.md           ← Always loaded. <50 lines. What matters right now.
├── personal/               ← Warm. Loaded when relevant.
│   ├── hot-memory.md
│   ├── observations.md     ← Append-only event log
│   ├── action-items.md     ← Tasks with due dates
│   ├── entities.md         ← People, places, things
│   └── ...
├── work/acme/              ← Your work domain (created by /setup)
│   └── ...
└── glacier/                ← Cold. Archived, indexed, retrieved on demand.
    └── index.md
```

- **Hot**: Loaded every conversation. Current state, top priorities.
- **Warm**: Domain-specific files loaded when a skill activates.
- **Glacier**: YAML-frontmattered archives. Searched via `glacier/index.md`.

### What Memory Looks Like

Here's what builds up over time. None of this is pre-filled — it emerges from your conversations.

**`memory/hot-memory.md`** — the 30,000-foot view:

```markdown
# Hot Memory
<!-- L0: Current priorities, active situations, system notes -->

## Identity
- Software engineer at Acme Corp, 2 kids, based in Melbourne
- Side project: open-source CLI tools

## Watch
- Performance review cycle opens next week — prep doc started [[work/acme/action-items]]
- Kid's speech therapy showing progress — 3 new words this month [[personal/health]]

## System
- /reflect found 3 observation clusters ready to promote to patterns
```

**`memory/personal/observations.md`** — raw events, append-only:

```markdown
- 2026-03-10 [family]: School called — Sam had a great day, shared toys unprompted for the first time
- 2026-03-11 [health]: Ran 5k in 28min. Knee felt fine. Third run this week without pain.
- 2026-03-12 [insight]: Realized I've been avoiding the budget conversation. Not about money — about control.
```

**`memory/work/acme/entities.md`** — compact 3-line registry:

```markdown
### Sarah Chen (Engineering Manager)
- Direct report to VP Eng | Joined Jan 2025 | Runs platform team | Prefers async over meetings
- status: active | last: 2026-03-10
```

Heavy entries get promoted to thread files — the entity stub just links: `→ [[work/acme/sarah-chen]]`.

### Progressive Condensation

Two processes:

**Condensation:** observations → patterns → hot-memory. Each layer is smaller and more actionable than the one below.

**Archival:** old observations → glacier. Indexed, retrievable, out of the way.

Nothing is deleted — it moves to the right place.

### Threads — The Zettelkasten Layer

When a topic keeps coming up across observations, Cog raises it into a **thread** — a read-optimized synthesis file that pulls scattered fragments into a coherent narrative.

Every thread has the same spine:

- **Current State** — what's true right now (rewrite freely)
- **Timeline** — dated entries, append-only, full detail preserved
- **Insights** — patterns, learnings, what's different this time

A thread gets raised when a topic appears in 3+ observations across 2+ weeks, or when you say "raise X" or "thread X". Threads grow long — that's the point. The texture is the value. One file forever, never condensed.

Fragments (observations) never move. Threads reference them via wiki-links.

See the full [Thread Framework documentation](https://lab.puga.com.br/cog/#/memory) for details.

### L0 / L1 / L2 Tiered Loading

Every memory file has a one-line summary: `<!-- L0: what's in this file -->`. This is the first tier of a three-level retrieval protocol:

- **L0** — one-line summary. Decides whether to open a file at all.
- **L1** — section header scan. Identifies which part of a long file to read.
- **L2** — full file read. Used when the full context is needed.

Scan L0s first, confirm relevance, use L1 for long files, read only what's needed.

### Single Source of Truth

Each fact lives in one canonical file. `entities.md` owns people. `action-items.md` owns tasks. `hot-memory.md` holds pointers — not the authoritative version of any fact. Other files reference with `[[wiki-links]]` instead of copying.

### Wiki-Links

Files cross-reference each other with `[[domain/filename]]` links. A link index is auto-generated by `/housekeeping` so you can discover what connects to what.

### Domain Registry

Domains are areas of your life — personal, work, side projects. Each domain gets its own memory directory and slash command.

```
/setup → conversational → domains.yml → directories + skills + routing
```

| Type | Purpose | Examples |
|------|---------|---------|
| `personal` | Personal life | Always created |
| `work` | Day job | `/acme`, `/google` |
| `side-project` | Ventures, hobbies | `/myapp`, `/substack` |
| `system` | Cog internals | Auto-created (`cog-meta`) |

## Skills

Built-in skills in `.claude/commands/`:

| Skill | What it does |
|-------|-------------|
| `/setup` | Conversational domain setup |
| `/personal` | Family, health, calendar, day-to-day |
| `/reflect` | Mine conversations, extract patterns, condense |
| `/evolve` | Audit memory architecture, propose rule changes |
| `/foresight` | Cross-domain strategic nudge |
| `/scenario` | Decision simulation with timeline overlay |
| `/housekeeping` | Archive, prune, link audit, glacier index |
| `/history` | Deep search across memory files |
| `/explainer` | Writing and explanation (Atkins + Montaigne method) |
| `/humanizer` | Remove AI patterns from text |

Domain skills (`/work`, `/sideproject`, etc.) are auto-generated by `/setup`.

## Pipeline

Cog includes pipeline skills that maintain memory health over time. Run them manually:

```
/housekeeping    # Archive stale data, prune hot-memory, rebuild indexes
/reflect         # Mine recent work, condense patterns, detect threads
/evolve          # Audit architecture, check rule effectiveness
/foresight       # Cross-domain scan, surface one strategic nudge
```

Or automate with scheduling:

**Claude Code** has built-in task scheduling — use `/loop` or cron to run pipeline skills on a recurring basis:

```bash
# Example: nightly housekeeping + reflect via cron
0 23 * * * cd /path/to/cog && claude -p "$(cat .claude/commands/housekeeping.md)"
0 0  * * * cd /path/to/cog && claude -p "$(cat .claude/commands/reflect.md)"
```

**[Cowork](https://claude.com/product/cowork)** sessions can also run pipeline skills. Open Cog in Cowork and ask it to run `/housekeeping` or `/reflect` — it has full file access and can maintain memory as part of a longer autonomous session.

The pipeline is optional. Cog works without it — but running it regularly keeps memory clean and surfaces insights you'd miss.

## Architecture

Cog's architecture lives entirely in instructions — `CLAUDE.md` for conventions and `.claude/commands/*.md` for workflows. There is no application code. The instructions define how memory is structured, how queries are routed, and how the system maintains itself. Claude reads these files and acts on them. The `memory/` directory is just the state that accumulates.

This makes Cog interface-agnostic. It works with:

- **[Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview)** (terminal) — native. Just open the project.
- **[Cowork](https://claude.com/product/cowork)** — Claude Desktop's agentic mode. Point it at `memory/` and it inherits everything. Great for heavy document generation and long autonomous workflows.
- **Any Claude-powered tool** that reads `CLAUDE.md` and has file access.

The memory system is the same everywhere — markdown files with conventions. The interface just determines how context is loaded.

## Connecting Tools

Cog becomes significantly more powerful when connected to external tools via MCP (Model Context Protocol). In Claude Code or Cowork, you can connect services like:

- **Google Calendar** — schedule awareness, meeting prep, time-blocking
- **Gmail** — email drafting, inbox triage, follow-up tracking
- **Slack** — team context, message drafting, channel monitoring
- **GitHub** — PR reviews, issue tracking, codebase awareness
- **Linear/Jira** — project tracking, sprint context
- **Notion/Obsidian** — extended knowledge base, note sync

When tools are connected, Cog's skills can use them automatically. `/foresight` checks your calendar before surfacing nudges. `/reflect` can reference Slack threads. `/personal` can draft emails. The memory layer gives these tools something they don't have alone: context that persists and compounds.

**To connect tools in Cowork**, add MCP servers in your Cowork settings. Each tool appears as a set of functions Cog can call alongside its memory operations — no code changes needed.

The combination of persistent memory + connected tools is where Cog stops being a note-taking system and starts being a cognitive layer. Memory without action is a diary. Memory with tools is an agent.

## Credits

Cog is a synthesis of ideas from research, open-source systems, and knowledge management traditions.

**Research**: [RLM](https://arxiv.org/abs/2512.24601) (recursive memory hierarchy) | [A-MEM](https://arxiv.org/abs/2502.12110) (bi-directional back-linking) | [OpenViking](https://github.com/volcengine/OpenViking) (L0/L1/L2 tiered context loading)

**Systems**: [Zep/Graphiti](https://github.com/getzep/graphiti) (temporal validity) | [Mem0](https://github.com/mem0ai/mem0) (contradiction detection) | [Claude Memory](https://docs.anthropic.com/en/docs/claude-code/memory) (file-based architecture validation)

**Traditions**: [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten) (thread framework) | [SSOT](https://en.wikipedia.org/wiki/Single_source_of_truth) (canonical fact storage)

**Platform**: [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) (Anthropic)

See the [full credits page](https://lab.puga.com.br/cog/#/credits) for how each idea shaped Cog's design.

## Citation

If Cog influences your work — whether you fork it, adapt the patterns, or reference the architecture — a mention goes a long way:

```
Cog: Cognitive Architecture for Claude Code
https://github.com/marciopuga/cog
Marcio Puga, 2026
```

BibTeX for academic use:

```bibtex
@software{puga2026cog,
  author = {Puga, Marcio},
  title = {Cog: Cognitive Architecture for Claude Code},
  year = {2026},
  url = {https://github.com/marciopuga/cog},
  note = {Persistent memory, self-reflection, and foresight for AI agents}
}
```

## License

MIT
````
