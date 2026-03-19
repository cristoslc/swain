# Swain Skill Audit — 2026-03-18

Full skill-creator audit of all 18 swain skills. Covers description quality, structural quality, operational issues, and content quality.

## Executive Summary

| Skill | Lines | Desc Words | High | Med | Low | Scripts | Refs |
|-------|-------|------------|------|-----|-----|---------|------|
| swain | 23 | 32 | 0 | 2 | 3 | yes | no |
| swain-design | 173 | 67 | 0 | 3 | 4 | yes | yes (37) |
| swain-dispatch | 197 | 47 | 2 | 3 | 2 | no | no |
| swain-do | 188 | 103 | 0 | 3 | 3 | yes | yes (7) |
| swain-doctor | 405 | 57 | 0 | 3 | 3 | yes | yes (10) |
| swain-help | 85 | 74 | 0 | 1 | 4 | no | yes (2) |
| swain-init | 417 | 53 | 0 | 3 | 3 | no | no |
| swain-keys | 93 | 30 | 0 | 2 | 2 | yes | no |
| swain-push | 17 | 8 | 1 | 2 | 1 | no | no |
| swain-release | 164 | 71 | 0 | 2 | 3 | no | no |
| swain-retro | 272 | 45 | 1 | 2 | 2 | no | no |
| swain-search | 255 | 91 | 0 | 3 | 3 | yes | yes (4) |
| swain-security-check | 179 | 45 | 0 | 3 | 2 | yes (8) | no |
| swain-session | 232 | 34 | 0 | 3 | 3 | yes (3) | no |
| swain-stage | 169 | 33 | 0 | 2 | 3 | yes (4) | yes |
| swain-status | 140 | 31 | 1 | 3 | 1 | yes | yes (2) |
| swain-sync | 298 | 28 | 2 | 3 | 2 | no | no |
| swain-update | 175 | 42 | 2 | 2 | 2 | no | yes (1) |
| **Totals** | | | **9** | **45** | **45** |  |  |

### Cross-Cutting Themes

1. **Relative path fragility** — Most skills hardcode `skills/swain-*/scripts/...` paths assuming CWD is project root. Breaks in worktrees. Only swain-status and the bookmark/focus scripts use `find`-based discovery. This should be the universal pattern.

2. **Description word counts uniformly low** — 12 of 18 skills are under 50 words (recommended: 50-150). Richer descriptions with concrete trigger phrases would improve routing recall without increasing false positives.

3. **`AskUserQuestion` missing from allowed-tools** — swain-retro, swain-search, swain-keys, and swain-release all require interactive confirmation but don't list `AskUserQuestion`. Agents must embed questions in response text, which is less reliable.

4. **Cache/state location divergence** — swain-status writes to `~/.claude/projects/<slug>/memory/`, while swain-session and swain-stage have migrated to `.agents/`. Two sources of truth.

5. **SKILL.md as API documentation** — swain-security-check (external hook API, ~50% of file) and swain-session (post-operation bookmark protocol) inline developer-facing docs that belong in `references/` files.

6. **No `ExitWorktree` companion** — swain-do and swain-session list `EnterWorktree` in allowed-tools but provide no guidance on when/how to exit, risking agents stranded in worktrees.

---

## Individual Skill Audits

---

## swain (meta-router)
- **Lines**: 23
- **Description word count**: 32
- **Has scripts**: yes (`scripts/swain-box`)
- **Has references**: no

### Strengths
- Extremely compact — does exactly one thing (route to sub-skills)
- Routing table is exhaustive and easy to scan
- Model hint (`haiku`) is appropriate for a pure dispatch task

### Issues
- [SEVERITY: medium] Routing table includes sub-skills that may not exist in `.claude/skills/` — no note that some rows are aspirational/uninstalled. Agent attempting to invoke missing skills will fail confusingly.
- [SEVERITY: medium] The `swain-box` script in `scripts/` is not referenced in SKILL.md. Agent doesn't know it exists.
- [SEVERITY: low] "mentions swain by name" trigger clause is overly broad — could trigger on any conversational mention of the project.
- [SEVERITY: low] No `user-invocable`, `license`, or `allowed-tools` fields in frontmatter. Inconsistent with other skills.
- [SEVERITY: low] No disambiguation guidance when user intent matches multiple routing rows.

### Description improvement suggestions
- Narrow "mentions swain by name" to "explicitly asks swain to do something — not merely when they mention the project."
- Add graceful-skip note for uninstalled sub-skills.

---

## swain-design
- **Lines**: 173
- **Description word count**: 67
- **Has scripts**: yes (`chart.sh`, `specgraph.sh`, `specwatch.sh`, `adr-check.sh`, `rebuild-index.sh`, `spec-verify.sh`, `specgraph/`, `migrate-*.py`, `migrate-bugs.sh`, `issue-integration.sh`, `chart_cli.py`)
- **Has references**: yes (37 files covering definitions, templates, guides, and integration docs)

### Strengths
- Description is specific and comprehensive
- Progressive disclosure well-executed: 173-line SKILL.md delegates detail to `references/`
- Complexity tier detection (fast-path vs. full ceremony) reduces overhead for trivial artifacts
- Artifact type table with paired definition + template links is excellent
- Intent-to-artifact inference table gives agents heuristics for ambiguous requests

### Issues
- [SEVERITY: medium] Script invocations use relative paths (`skills/swain-design/scripts/chart.sh`) — break in worktrees.
- [SEVERITY: medium] Steps 8 and 8a both numbered "8" — could confuse step tracking.
- [SEVERITY: medium] `swain-search` referenced indirectly but may not be installed.
- [SEVERITY: low] `allowed-tools` doesn't include `EnterWorktree` despite worktree isolation references in execution tracking handoff.
- [SEVERITY: low] Bookmark script uses fragile `find` with `print -quit` — no fallback.
- [SEVERITY: low] `chart.sh build` not cross-referenced to specgraph guide for failure handling.
- [SEVERITY: low] Minor `type` value inconsistency between description and complexity tier section.

### Description improvement suggestions
- Split single run-on sentence into two for easier routing-layer parsing.
- Add "update frontmatter field", "re-parent", "set priority" as signal phrases.

---

## swain-dispatch
- **Lines**: 197
- **Description word count**: 47
- **Has scripts**: no
- **Has references**: no

### Strengths
- Description clear and specific — GitHub Issues + Claude Code Action mechanism named explicitly
- Preflight check well-structured with explicit failure conditions
- Workflow template embedded directly, reducing setup friction
- Trigger timing table explains `issues.opened` gotcha

### Issues
- [SEVERITY: high] Step 5 uses `gh api repos/${OWNER_REPO}/dispatches` with `event_type="agent-dispatch"`, but the embedded workflow YAML doesn't include a `repository_dispatch` trigger. The auto-trigger cannot work with the provided template.
- [SEVERITY: high] Bash heredoc in Step 4 uses single-quoted `EOF` which suppresses variable expansion — `${ARTIFACT_ID}` and `${ARTIFACT_CONTENT}` will be written literally.
- [SEVERITY: medium] No `references/` directory. All content inline at 197 lines.
- [SEVERITY: medium] Uses `find` in Bash while other skills prefer `Glob` — minor style inconsistency.
- [SEVERITY: medium] `swain.settings.json` referenced with no schema docs or absent-file handling.
- [SEVERITY: low] "offload work to a background agent" is too broad — could match non-dispatch situations.
- [SEVERITY: low] No version tracking for embedded workflow YAML.

### Description improvement suggestions
- Add "GitHub Actions", "autonomous agent", "claude-code-action" as trigger phrases.
- Replace vague "offload work" with: "dispatch a swain artifact to a GitHub Actions runner for autonomous implementation via Claude Code Action."

---

## swain-do
- **Lines**: 188
- **Description word count**: 103
- **Has scripts**: yes (`ingest-plan.py`)
- **Has references**: yes (`tk-cheatsheet.md`, `tdd-enforcement.md`, `escalation.md`, `plan-ingestion.md`, `execution-strategy.md`, `configuration.md`, `reconciliation.md`)

### Strengths
- Description among the best — covers primary use cases and names common user phrasings
- Four-tier tracking model prevents agents from accidentally creating plans for coordination artifacts
- Term mapping table is precise (abstract → concrete)
- Pre-plan implementation detection with anti-rationalization safeguard is rigorous
- Worktree isolation preamble distinguishes read-only vs. write operations
- Fallback for missing `tk` is graceful

### Issues
- [SEVERITY: medium] Description at 103 words is too long for routing. Several clauses ("even if they don't mention 'execution tracking' explicitly") should be in the body.
- [SEVERITY: medium] `ticket-query` referenced in Operating Rule 7 but no location or definition provided — fresh agent won't know it's a vendored binary distinct from `tk`.
- [SEVERITY: medium] `EnterWorktree` in allowed-tools but no `ExitWorktree` — no guidance on when/how to exit. Agents could be stranded in worktrees.
- [SEVERITY: low] `ticket-query` says "available in the vendored `bin/` directory" — doesn't specify which `bin/`.
- [SEVERITY: low] Cross-skill dependency on `chart.sh` not declared.
- [SEVERITY: low] Fragile bookmark `find` pattern.

### Description improvement suggestions
- Trim to ~70 words. Suggested: "Operate the external task-management CLI (tk) as source of truth for agent execution tracking. Invoke when any SPEC comes up for implementation, when the user asks to track tasks, check what to work on, see task status, manage work dependencies, or close/abandon tasks."

---

## swain-doctor
- **Lines**: 405
- **Description word count**: 57
- **Has scripts**: yes (`swain-preflight.sh`, `swain-initiative-scan.sh`)
- **Has references**: yes (10 files)

### Strengths
- Progressive disclosure consistent — almost every check defers to `references/`
- Superpowers detection loop is clean and non-blocking
- Summary report format is well-designed for quick scanning
- Lifecycle directory migration uses `uv run python3` per project conventions

### Issues
- [SEVERITY: medium] At 405 lines — longest SKILL.md. Lifecycle migration, worktree detection, and epic-parent migration could move to references (~120 lines savings).
- [SEVERITY: medium] Description says "ALWAYS invoke at the START of every session" but preflight skips it on exit 0. Misleading.
- [SEVERITY: medium] "Evidence Pool → Trove Migration" references `swain-search` script that may not exist.
- [SEVERITY: low] `shasum -a 256` is macOS-specific. Linux uses `sha256sum`.
- [SEVERITY: low] Hardcoded `docs/epic/` path in parent-initiative check.
- [SEVERITY: low] `swain-initiative-scan.sh` referenced without documentation on output format.

### Description improvement suggestions
- Replace "ALWAYS invoke at the START" with accurate conditional: "Auto-invoked at session start when swain-preflight.sh exits 1. Also user-invocable for on-demand health checks."
- Drop one-time migration details from description.

---

## swain-help
- **Lines**: 85
- **Description word count**: 74
- **Has scripts**: no
- **Has references**: yes (`quick-ref.md`, `workflows.md`)

### Strengths
- Most trigger-phrase-rich description in the set
- Three-mode design (onboarding / question / reference) prevents wall-of-text responses
- Model hints well-applied (sonnet for concepts, haiku for lookups)
- "Admit gaps" instruction prevents hallucination
- "Hand off when appropriate" prevents help from becoming a dead end

### Issues
- [SEVERITY: medium] Generic trigger phrases ("how do I", "what is") overlap with swain-design and swain-do intents. No disambiguation guidance.
- [SEVERITY: low] Cross-skill paths assume project root as CWD.
- [SEVERITY: low] Onboarding template hardcodes `/swain` as entry point.
- [SEVERITY: low] No tie-breaker when both question and reference modes apply.
- [SEVERITY: low] `Skill` tool referenced in body matches allowed-tools — fine, but worth noting.

### Description improvement suggestions
- Trim redundant catch-all ("any question about...") since explicit phrase list already covers it.

---

## swain-init
- **Lines**: 417
- **Description word count**: 53
- **Has scripts**: no
- **Has references**: no (references `swain-doctor/references/AGENTS.content.md` at runtime)

### Strengths
- Comprehensive six-phase structure with clear skip conditions
- Decision matrix for CLAUDE.md state is exhaustive
- Warns rather than fails on missing optional tools
- Distinguishes itself from swain-doctor (init = one-time, doctor = ongoing)

### Issues
- [SEVERITY: medium] `brew install tmux` is macOS-only with no Linux fallback.
- [SEVERITY: medium] Phase 5.3 reads `AGENTS.content.md` from relative paths — fails in projects without vendored swain.
- [SEVERITY: medium] `ticket-migrate-beads` called as bare binary with no error guidance.
- [SEVERITY: low] 417 lines with no references/ — Phase 3 YAML blocks could be externalized.
- [SEVERITY: low] "offers to" in description is a weak trigger signal.
- [SEVERITY: low] `Skill` tool not in allowed-tools but Phase 6 chains to swain-doctor and swain-help.

### Description improvement suggestions
- Add trigger phrases: "set up swain", "onboard this project", "initialize swain", "migrate CLAUDE.md"
- Drop "Run once" tautology.

---

## swain-keys
- **Lines**: 93
- **Description word count**: 30
- **Has scripts**: yes (`scripts/swain-keys.sh`)
- **Has references**: no

### Strengths
- Clean delegation pattern — thin SKILL.md defers to shell script
- Workflows clearly separated (default/status, provision, verify)
- Handles GitHub OAuth scope-refresh edge case
- Model hint `haiku` appropriate for script delegation

### Issues
- [SEVERITY: medium] `AskUserQuestion` absent from allowed-tools despite interactive confirmation requirement.
- [SEVERITY: medium] Description at 30 words is below floor. No trigger phrases for "configure signing", "fix SSH", "why does 1Password keep prompting?"
- [SEVERITY: low] OAuth flow reads as if agent will complete it — should clarify agent must wait.
- [SEVERITY: low] Missing bookmark graceful degradation note.

### Description improvement suggestions
- Expand: "configure git signing", "set up SSH keys", "bypass 1Password for git", "add key to GitHub", "troubleshoot 1Password git prompts"

---

## swain-push (deprecated)
- **Lines**: 17
- **Description word count**: 8
- **Has scripts**: no
- **Has references**: no

### Strengths
- Correctly self-describes as deprecated with replacement
- Minimal body appropriate for a redirect

### Issues
- [SEVERITY: high] `name` field is `swain-~push` (with tilde). Either intentional suppression (undocumented) or typo that breaks routing.
- [SEVERITY: medium] `user-invocable: true` on deprecated alias may be counterproductive.
- [SEVERITY: medium] Description (8 words) is purely deprecation notice. No routing signal.
- [SEVERITY: low] `allowed-tools` includes `Edit` but only needs `Skill` (which isn't listed).

### Description improvement suggestions
- Expand: "Deprecated alias for swain-sync. If you're trying to stage, commit, and push changes, use /swain-sync instead."
- Consider `user-invocable: false`.

---

## swain-release
- **Lines**: 164
- **Description word count**: 71
- **Has scripts**: no
- **Has references**: no

### Strengths
- Description explicitly lists multiple trigger phrases — excellent routing coverage
- Override file pattern (`.agents/release.override.skill.md`) is clean extensibility
- "Propose before executing" gate prevents accidental releases
- Edge cases section is thorough
- Generic by design — detects rather than assumes

### Issues
- [SEVERITY: medium] Version-file detection `grep -rl 'version'` will match hundreds of files. No filtering guidance.
- [SEVERITY: medium] `license: UNLICENSED` while other skills use MIT. Inconsistent.
- [SEVERITY: low] `git push --tags` pushes all tags, not just the new one.
- [SEVERITY: low] Bookmark pattern lacks "if found" fallback.
- [SEVERITY: low] No `AskUserQuestion` despite interactive confirmation requirements.

### Description improvement suggestions
- Add: "ship a version", "publish", "prepare a release", "what version are we on"

---

## swain-retro
- **Lines**: 272
- **Description word count**: 45
- **Has scripts**: no
- **Has references**: no

### Strengths
- Output mode table (EPIC-scoped vs cross-epic) is clearly explained
- Invocation mode matrix covers full surface area
- Terminal state adaptation for Abandoned/Superseded shows contextual awareness
- Memory creation rules are constrained (max 3-5, user-validated only)
- Prior retro cross-referencing looks for recurring themes

### Issues
- [SEVERITY: high] `AskUserQuestion` absent from allowed-tools. Interactive mode asks four questions "one at a time, waiting for user response" — cannot reliably pause without this tool.
- [SEVERITY: medium] `chart.sh` and `TK_BIN` use hardcoded relative paths. Break outside project root.
- [SEVERITY: medium] `docs/epic/` hardcoded in grep for embedded retros.
- [SEVERITY: low] Description at 45 words below floor. Missing "post-mortem", "lessons learned", "debrief", "what worked".
- [SEVERITY: low] Memory files written to `~/.claude/projects/<slug>/memory/` — slug derivation unspecified.

### Description improvement suggestions
- Add: "post-mortem", "lessons learned", "debrief", "what worked", "what didn't work"

---

## swain-search
- **Lines**: 255
- **Description word count**: 91
- **Has scripts**: yes (`migrate-to-troves.sh`, `trovewatch.sh`)
- **Has references**: yes (`normalization-formats.md`, `manifest-schema.md`, `wordlist.txt`, `trovewatch-guide.md`)

### Strengths
- Mode detection table covers full lifecycle (Create / Extend / Refresh / Discover)
- Graceful degradation table prevents total failure
- Source type handling is comprehensive with distinct normalization paths
- Dual-commit stamp pattern ensures reproducible artifact-trove linking
- References properly externalized

### Issues
- [SEVERITY: medium] `trovewatch-guide.md` exists but never mentioned in SKILL.md — dead documentation.
- [SEVERITY: medium] `migrate-to-troves.sh` and `trovewatch.sh` scripts exist but never referenced in SKILL.md.
- [SEVERITY: medium] "what do we know about X" trigger may set wrong expectations (Discover mode vs. new research).
- [SEVERITY: low] `AskUserQuestion` not in allowed-tools despite interactive Create mode.
- [SEVERITY: low] "build a trove" is domain-specific jargon — broader phrasing would help new users.
- [SEVERITY: low] Generic verbs ("clone or read", "crawl or fetch") without specifying which tools.

### Description improvement suggestions
- Replace "build a trove" with "compile research on" or "gather background material for"
- Clarify "what do we know about X" → "find existing research on X"
- Reference the orphaned scripts and trovewatch guide, or remove them.

---

## swain-security-check
- **Lines**: 179
- **Description word count**: 45
- **Has scripts**: yes (8: `security_check.py`, `context_file_scanner.py`, `scanner_availability.py`, `external_hooks.py`, `security_briefing.py`, `security_gate.py`, `threat_surface.py`, `doctor_security_check.py`)
- **Has references**: no

### Strengths
- Explicit trigger-phrase list in description
- Graceful degradation: built-in scanners always run, external are advisory
- Report format table is clear
- Exit codes documented
- External-hook API provides complete integration contract

### Issues
- [SEVERITY: medium] SPEC references (058, 059, 061, 063, 065) are all Proposed — readers can't distinguish normative vs. aspirational.
- [SEVERITY: medium] Script path `python3 skills/swain-security-check/scripts/security_check.py .` is relative — breaks in worktrees.
- [SEVERITY: medium] `swain-init` integration referenced but not noted as a separate skill.
- [SEVERITY: low] External hook API (~50% of file) is developer docs that belongs in `references/`.
- [SEVERITY: low] Description at 45 words missing "audit dependencies", "check secrets", "check for injections".

### Description improvement suggestions
- Add triggers: "audit dependencies", "check secrets", "find vulnerabilities", "scan codebase"
- Move external hook API to `references/external-hook-api.md`.

---

## swain-session
- **Lines**: 232
- **Description word count**: 34
- **Has scripts**: yes (`swain-tab-name.sh`, `swain-bookmark.sh`, `swain-focus.sh`)
- **Has references**: no (but has `tests/test-tab-name.sh`)

### Strengths
- Steps clearly numbered and sequenced
- session.json schema provided inline with concrete example
- `swain-bookmark.sh` API documented with exact invocation patterns
- Error handling explicit and non-fatal by design
- Migration path for old global session.json specified
- Focus Lane section is self-contained
- Test file exists (rare among these skills)

### Issues
- [SEVERITY: medium] Tab-naming script uses relative `skills/swain-session/scripts/...` path in Steps 1 and 1.5 — breaks in worktrees. Inconsistent with bookmark/focus scripts that use `find`.
- [SEVERITY: medium] Step 1.5 auto-creates a worktree on every session start with no user confirmation gate — may conflict with operators intending to work on `main`.
- [SEVERITY: medium] `swain-design/scripts/chart.sh` called in session info and Focus Lane with no `find` fallback.
- [SEVERITY: low] Description doesn't explain when auto-invocation happens — mechanism is in AGENTS.md only.
- [SEVERITY: low] Post-operation bookmark section is documentation for other skill authors, not runtime instructions.
- [SEVERITY: low] "Set preference" documented as if functional but is "currently informational" with no effect.

### Description improvement suggestions
- Add manual triggers: "set focus", "bookmark this", "remember where I am", "session info", "rename tab"
- Clarify: "Auto-invoked on session start. Manually invokable to bookmark context, set focus, manage tab name, or check session state."

---

## swain-stage
- **Lines**: 169
- **Description word count**: 33
- **Has scripts**: yes (`swain-stage.sh`, `swain-motd.py`, `swain-motd.sh`, `stage-status-hook.sh`)
- **Has references**: yes (`references/layouts/`, `references/yazi/`)

### Strengths
- Command reference is clean and complete
- Settings table well-structured with types, defaults, descriptions
- Agent-triggered pane operations section provides concrete patterns
- Graceful degradation covered for every dependency
- Prerequisite stated upfront

### Issues
- [SEVERITY: medium] `stage-status.json` location never stated in SKILL.md — agent can't find or debug it.
- [SEVERITY: medium] Hook configuration verification not described — if hook missing, MOTD never updates with no diagnostic.
- [SEVERITY: low] "lets the agent directly manage panes" is confusing capability framing.
- [SEVERITY: low] Relative script paths without `find` fallback.
- [SEVERITY: low] Legacy `swain-motd.sh` fallback limitations undocumented.

### Description improvement suggestions
- Replace confusing framing with: "invoke to set up workspace layout, manage panes, or update MOTD status"
- Add: "set up workspace", "open layout", "start MOTD", "open file browser", "split pane"

---

## swain-status
- **Lines**: 140
- **Description word count**: 31
- **Has scripts**: yes (`swain-status.sh`)
- **Has references**: yes (`agent-summary-template.md`, `status-format.md`)

### Strengths
- Compact and focused
- Mode inference logic explicit with prioritized conditions
- Peripheral Awareness and Focus Lane well-specified
- Scoring formula for recommendations documented
- `--compact` flag for MOTD integration documented

### Issues
- [SEVERITY: high] Cache location uses old `~/.claude/projects/<slug>/memory/` path while project has migrated to `.agents/`. Will cause state divergence.
- [SEVERITY: medium] `references/agent-summary-template.md` referenced but never linked or quoted. Missing template = unstructured output.
- [SEVERITY: medium] Ambiguous whether mode inference happens in script or agent — could cause duplicate/conflicting selection.
- [SEVERITY: medium] Script discovery uses `find` (good) but template discovery does not.
- [SEVERITY: low] "status" and "progress" triggers are very broad — could match "git status" or "PR progress".

### Description improvement suggestions
- Tighten: "project status" or "swain status" instead of bare "status"
- Add: "am I blocked", "what needs review", "show me priorities"

---

## swain-sync
- **Lines**: 298
- **Description word count**: 28
- **Has scripts**: no
- **Has references**: no

### Strengths
- Step sequencing explicit and complete
- Secrets detection before staging is proactive
- Gitignore hygiene check with skip logic and suppress mechanism
- Conventional commit guidance with examples
- Worktree detection used consistently throughout
- Pre-commit hook requirement is non-negotiable

### Issues
- [SEVERITY: high] `allowed-tools: Bash, Read, Edit` missing `Write` and `Glob`. Step 3 scans for secret files across tree.
- [SEVERITY: high] Worktree pruning command is fragile — could target wrong worktree in multi-worktree setup.
- [SEVERITY: medium] Index rebuild uses cross-skill path that silently no-ops if swain-design installed under `.claude/skills/`.
- [SEVERITY: medium] Description omits gitignore hygiene, ADR compliance, and index rebuilding — surprising undocumented behaviors.
- [SEVERITY: medium] Co-Authored-By model name detection unreliable; "AI Assistant" fallback too generic.
- [SEVERITY: low] `swain-init` reference for setup not explained.
- [SEVERITY: low] 298 lines with no references/ — gitignore check and index rebuild could be externalized.

### Description improvement suggestions
- Expand to cover full behavior: "Stage all changes (with secrets detection and gitignore hygiene), generate a conventional-commit message, commit (with pre-commit enforcement), and push. Runs ADR compliance warnings and rebuilds artifact indexes."

---

## swain-update
- **Lines**: 175
- **Description word count**: 42
- **Has scripts**: no
- **Has references**: yes (`references/agent-platforms.json`)

### Strengths
- Explicit trigger phrases in description
- Backup-before-overwrite is a meaningful safety feature
- Platform detection avoids unnecessary stubs
- `npx` → git-clone fallback chain is robust
- Restore guidance distinguishes config files vs. patched scripts

### Issues
- [SEVERITY: high] `SKILL_DIR` used as literal placeholder in bash code blocks — not runnable. Agent told to "replace" it but no discovery mechanism provided.
- [SEVERITY: high] Git-clone fallback copies to `.claude/skills/` only — wrong if project uses `.agents/skills/`.
- [SEVERITY: medium] Modified-file detection requires network access (git clone for comparison). No offline fallback.
- [SEVERITY: medium] `allowed-tools` includes `Write, Edit, Grep, Glob` but skill text uses exclusively Bash.
- [SEVERITY: low] "Invoke swain-doctor" without specifying how.
- [SEVERITY: low] "npx" described as "skills package manager" — misleading.

### Description improvement suggestions
- Replace "Runs the skills package manager (npx)" with "Uses npx to pull the latest swain release from GitHub."
- Add: "reinstall swain", "refresh skills"

---

## Priority Action Items

### High severity (fix first — 9 issues)
1. **swain-dispatch**: `repository_dispatch` trigger missing from workflow YAML (autoTrigger broken)
2. **swain-dispatch**: Single-quoted heredoc suppresses variable expansion
3. **swain-push**: `name: swain-~push` — tilde in name breaks routing
4. **swain-retro**: `AskUserQuestion` absent — interactive mode unreliable
5. **swain-status**: Cache location uses old `~/.claude/` path instead of `.agents/`
6. **swain-sync**: `allowed-tools` missing `Write` and `Glob`
7. **swain-sync**: Worktree pruning command fragile in multi-worktree setup
8. **swain-update**: `SKILL_DIR` literal placeholder not runnable
9. **swain-update**: Git-clone fallback targets wrong install location

### Systemic improvements
1. **Universal `find`-based script discovery** — replace all hardcoded relative paths
2. **Description enrichment** — add concrete trigger phrases to all skills under 50 words
3. **`AskUserQuestion` audit** — add to allowed-tools for all interactive skills
4. **`ExitWorktree` guidance** — add exit instructions wherever `EnterWorktree` is used
5. **Progressive disclosure** — move developer-facing API docs to `references/` in swain-security-check, swain-session
6. **State location migration** — move swain-status cache from `~/.claude/` to `.agents/`
