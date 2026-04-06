# Changelog

## [0.29.2-alpha] - 2026-04-06

### Features

#### False Positive Gitignore Warning Fixed

Preflight's skill folder gitignore check reported ".claude/skills/
not gitignored" even when the .gitignore entries were correct. The
check used git check-ignore, which returns a fatal error (exit 128)
for paths beyond a symlink — and the script treated that error as
"not ignored." Now only exit code 1 (explicitly not ignored) triggers
the warning; symlink-traversal errors are silently skipped.

## [0.29.1-alpha] - 2026-04-06

### Features

#### Consumer Script Resolution Fix

migrate-to-trunk-release.sh was missing in consumer projects because
it lived only in the swain source repo. The preflight told consumers
to run it, but the script never reached them via skill installation.
Moved to skills/swain-doctor/scripts/ so it gets symlinked into
.agents/bin/ during init, like all other agent-facing scripts.

#### Dual Version Display Restored

Version display changes from SPEC-287 were lost during a merge.
Re-applied so init messages, the swain marker, and update reports
show both the release version and installed skill version.

### Planned

- Plugin-namespaced script aggregation (ADR-036, EPIC-069) — agent-facing
  scripts move to .agents/scripts/swain/, operator-facing to
  .agents/bin/swain/. Eliminates flat-namespace collision risk and
  aligns with the Agent Skills standard.
- Runtime adapter architecture (SPIKE-061) — evaluating whether swain
  should present a Claude Code plugin shape while conforming to the
  Agent Skills standard for other runtimes.

### Research

- Ollama launch wrapper spike (SPIKE-060) complete — validated
  local model invocation.
- Agent runtime I/O compatibility research (SPIKE-059) complete.
- Agent script directory conventions trove — 12 sources surveyed
  across the Agent Skills standard, Claude plugins, and 9 runtime
  implementations.

### Supporting Changes

- Readability checker bug filed (SPEC-289) — markdown link regex
  breaks on parentheses in artifact paths, inflating FK scores.
- ADR-019 superseded by ADR-036.

## [0.29.0-alpha] - 2026-04-06

### Features

#### Worktree Isolation Redesign

EPIC-056 rebuilt worktree management from the ground up. Sessions now claim
lockfiles to prevent collisions, worktrees get artifact-aware names derived from
the spec being worked on, and completed sessions archive to a timestamped record.
All worktrees live under .worktrees/ instead of scattered locations (ADR-034).

#### Launcher Improvements

bin/swain now wraps sessions in tmux for persistence across terminal disconnects.
Skills are symlinked into worktrees at creation time, and runtime selection is
interactive when multiple runtimes are available.

#### Readability Threshold Raised

Flesch-Kincaid grade threshold raised from 9 to 10 in swain-design, and the
bullet-period governance rule added to prevent inflated scores from unterminated
list items.

### Planned

- Title-based artifact identifiers (ADR-035) with timestamp suffixes to replace
  numeric IDs. EPIC-064 tracks the migration.
- BDD traceability (EPIC-060/062) — linking behavioral specs to artifact
  acceptance criteria.
- Born-in-worktree session isolation (ADR-033) — sessions that originate inside
  a worktree stay scoped to it.
- swain-session deprecation (ADR-023) — responsibilities redistributed to
  swain-init, swain-do, and swain-teardown.

### Research

- RTK CLI token compression trove — 1 source collected.
- AI development patterns trove — 1 source collected.
- Retrospective resynthesize from all 29 retros.

### Supporting Changes

- BDD test suite with 84 behavioral specs and swain-test.sh gate.
- Automated completion pipeline — swain-do auto-transitions parent epics.
- Session preflight script consolidates startup reads into structured JSON.
- git-compact wrapper for compressed git output via RTK.
- Doctor detects and migrates flat-file artifacts to foldered format (ADR-027).
- Doctor excludes Docker MCP gateway from crash debris detection.
- grep -c anti-pattern audited and fixed across all scripts.
- Chart extended with relationship symlinks and standalone placement.
- 25 artifact number collisions from concurrent worktree work resolved.
- Worktree location standardized to .worktrees/ (ADR-034).
- swain-do commits dirty tracked files before worktree creation.
- Sync stash handling hardened against data loss.

## [0.28.0-alpha] - 2026-04-01

### Features

**#### Orphan Worktree Removal**  
swain-teardown now offers operator-confirmed removal of orphan worktrees. Full safety checks: dirty state, unmerged branches, current directory, and trunk protection all block removal with explicit reasons. SESSION-ROADMAP.md logs any removals.

**#### Unified Bookmark Storage**  
swain-bookmark.sh now manages worktree records alongside context notes through a single `worktrees` array in session.json. The broken session-bookmark.sh symlink removed.

**#### Retro Without Active Session**  
swain-retro now falls back to git log evidence when no session is active, so retrospectives work independently of the session lifecycle.

### Supporting Changes

- swain-do path corrected for swain-bookmark.sh
- Legacy skill cleanup in swain-doctor and swain-preflight, improving reliability
- Broken link resolution and readability improvements across documentation
- Skill-creator audit requirement added for skill modifications
- swain-status references retired in favor of swain-session

## [0.27.1-alpha] - 2026-04-01

### Features

#### Session Bookmark Handoff Safety

New sessions launched from the main checkout now open a worktree before handing off `Session purpose`, so the bookmark for the new session is written in the checkout that owns the work instead of clobbering trunk state. When a session starts inside a linked worktree that already has a bookmark, swain now treats that worktree as active context and steers the operator toward resuming it or opening a different worktree rather than silently overwriting the bookmark.

Runtime launcher templates now prefer `bin/swain`, which routes startup through the canonical pre-runtime guard instead of injecting `Session purpose` directly. This closes the second entry point that could bypass the worktree-aware handoff.

### Supporting Changes
- Added a standalone retrospective for the session bookmark handoff bug and fix

## [0.27.0-alpha] - 2026-04-01

### Features

#### Doctor Self-Repair Expansion

swain-doctor now repairs stale artifact indexes and promotes five more warn-only checks to auto-repair. Missing or stale index entries are rebuilt automatically, and previously advisory checks for memory directories, script permissions, signing setup, stale governance blocks, and crash-debris git locks now repair themselves instead of only warning.

#### Session Freshness Tracking

swain-session now tracks freshness from last activity instead of aging purely from session start time. Long-running sessions stay active when decisions or updates are still happening, which avoids false stale-state interruptions during real work.

#### Roadmap And Release Rendering Hardening

chart.sh and chart_cli.py now resolve imports through their real script paths, so repo-local symlink installs no longer shadow the specgraph package. Reciprocal xref validation accepts enriched backlink metadata, and the changelog renderer now resolves its bundled template correctly through .agents/bin symlinks, removing the need for manual template overrides during release preparation.

### Supporting Changes
- .gitignore now ignores session state and SESSION-ROADMAP.md so local session artifacts do not leak into commits
- crash-debris-lib.sh is now marked executable so doctor auto-repair paths can invoke it reliably

## [0.26.0-alpha] - 2026-03-31


### Features



#### Worktree Path Link Safety

Files edited inside a worktree sometimes contain absolute paths that break when the worktree is removed. Two new scripts close this gap: detect-worktree-links.sh scans any file for worktree-relative paths (handling parentheses in filenames and skipping inline code), and resolve-worktree-links.sh rewrites them in place to repo-root-relative paths. swain-sync now runs the rewriter automatically at worktree completion, so links are fixed before changes land on trunk.




#### Manifest-Driven Operator Bin Auto-Repair

swain-doctor's symlink check (check 15) has been replaced with a manifest-driven approach. Skills declare operator-facing scripts by placing them in a usr/bin/ directory. swain-doctor scans these manifests, compares them against bin/, and auto-repairs missing or stale symlinks. Hardcoded paths are gone — the check works correctly regardless of where swain is installed.



### Planned

- Automated test gates (EPIC-052) — a suite of specs is being designed to let swain verify its own promises end-to-end, including a swain-test harness, swain-sync and swain-release test gate integration, and swain-doctor checks that work in consumer repos

### Supporting Changes

- Pre-commit artifact flush — swain-do now commits any uncommitted artifacts before creating a worktree, preventing tracked files from being orphaned mid-session
- Portable skills path resolution — hardcoded skills/ references across multiple skills replaced with installation-aware lookups
- swain-do audit repairs — step numbering, pre-commit scope description, and cheatsheet text corrected
- Worktree isolation rule documented in AGENTS.md

## [0.25.0-alpha] - 2026-03-31

### Features

#### README as Ambient Intent

README.md is now a first-class input to swain's alignment loop. Six existing skills gained README awareness: swain-init seeds a README when missing and proposes artifacts from it, swain-doctor flags missing READMEs, swain-session checks for drift at focus-lane selection, swain-retro surfaces README drift during retrospectives, swain-release gates on README alignment and untested promises, and swain-design nudges the operator to update the README after artifact transitions. Reconciliation is always bidirectional — the operator decides which side to update.

#### Context-Rich Progress Tracking

Artifact references throughout swain now carry human-readable context instead of bare IDs. A new artifact-context.sh utility resolves any artifact ID to a one-liner with title, status, and progress. Session digests auto-generate at close and feed into per-epic progress logs. The session dashboard, retro output, roadmap, and design skill all use context lines so the operator never has to look up what an ID means.
- Progress section added to epic and initiative templates for session-digest auto-population

### Research
- Claude Code source leak 2026 — trove created with initial source

### Supporting Changes
- Collision keeper overwrite fix — fix-collisions.sh no longer over-rewrites keeper references during artifact renumbering
- Session greeting symlink wiring for new .agents/bin/ scripts
- Worktree-safe path resolution in session scripts
- Removed stale swain-dispatch from README skill table

## [0.24.0-alpha] - 2026-03-30

### Features

#### Deferred Worktree Creation

Worktree creation is now deferred to swain-do task dispatch rather than happening at plan time. This removes unnecessary branch scaffolding for tasks that never run and keeps the worktree list clean.

#### Fast-Path Session Greeting

A new greeting script delivers the session startup summary without waiting for the full init chain. Returning projects skip the onboarding flow entirely when the .swain-init marker is present, reducing first-prompt latency.

### Supporting Changes
- fix(SPEC-197): rename specgraph.py to specgraph_entry.py to resolve import shadowing bug

## [0.23.0-alpha] - 2026-03-30

### Features

#### Flesch-Kincaid Readability Enforcement

New readability-check.sh script scores markdown artifacts for
Flesch-Kincaid grade level, stripping frontmatter, code blocks,
tables, and other non-prose content before scoring. A governance
rule in AGENTS.md requires all artifacts to meet grade 9 or below.
A shared readability protocol doc gives skills the integration
contract: when to check, how to rewrite on failure, and a
3-attempt cap before proceeding.

#### Shell Launcher Init Marker

The swain shell launcher functions (bash and zsh) now check for
a .swain-init marker file before running full onboarding. If the
marker exists, the launcher skips init and goes straight to
session startup — cutting first-prompt latency for returning
projects.
- Retroactive verification completed for SPEC-192 (doctor parallel check cascade) and SPEC-193 (cross-branch artifact ID allocation)

### Planned

#### Session Startup Fast Path

EPIC-048 planned with supporting specs to reduce session startup
latency. SPIKE-001 measured baseline timing and discovered a bug
in the bootstrap script that added unnecessary overhead.

### Research
- Task management systems — extended with reddit and Linear issue-tracking sources
- Architecture intent-evidence loop — 15 sources on architectural thinking patterns
- AI thinking partner — 6 sources on collaborative AI reasoning
- Intent hierarchy — 3 sources from TL Capability Map chapter 10 on writing to influence
- TL Capability Map — initial trove with 1 source

## [0.22.3-alpha] - 2026-03-29

### Features
- Preflight no longer silently exits in worktrees — a set -e interaction with glob non-match on .claude/skills/*/scripts/ killed the script before reaching the .agents/bin/ auto-repair section. Now handles missing directories gracefully.
- New bin/swain and .agents/bin/render_changelog.py symlinks added to the two-tier convention

### Supporting Changes
- EPIC-047 (ADR-019 Script Convention Implementation) formally completed — all 5 child specs verified with live acceptance tests and transitioned to Complete, retrospective embedded
- Documentation references updated from ./swain-box to bin/swain-box across RUNBOOK-002, DESIGN-005, and SPEC-092

## [0.22.2-alpha] - 2026-03-29

### Features

#### Consolidated doctor health checks

swain-doctor now runs all 17 health checks through a single swain-doctor.sh script instead of firing them as parallel tool calls. This eliminates the cascade failure where one check erroring caused the runtime to cancel all sibling checks — producing zero diagnostic output. The script outputs structured JSON and always exits 0.

#### Cross-branch artifact ID allocation

New next-artifact-id.sh scans all local branches (not just the working tree) to determine the next available artifact number. Prevents ID collisions when parallel worktree sessions create artifacts concurrently — the bug that caused SPEC-191 to collide with an existing spec on trunk.

### Supporting Changes
- Two bug specs created: SPEC-192 (doctor cascade), SPEC-193 (ID allocation)

## [0.22.1-alpha] - 2026-03-29

### Features
- Preflight now self-heals three additional checks per ADR-020: creates missing `.agents/` directory, removes stale tk lock files (>1h), and fixes missing executable permissions on skill scripts

### Supporting Changes
- ADR-020 codifies the preflight self-healing convention — checks must auto-repair when safe and deterministic
- SPEC-191 audited all 17 preflight checks; 3 converted from report-only to self-healing

## [0.22.0-alpha] - 2026-03-29

### Features

#### Two-tier script convention (ADR-019)

Swain scripts now follow a two-tier convention: operator-facing scripts (like swain-box) live in bin/ with symlinks, while agent-facing scripts (like swain-trunk.sh) live in .agents/bin/. The preflight auto-repairs both tiers on every session start — missing or stale symlinks are recreated from the skill tree without operator intervention. This fixes the bug where consumer projects reported swain-trunk.sh as missing because it only existed in the swain source repo.
- All 10 swain skills migrated from find-based script lookups (~55 invocations) to direct .agents/bin/ resolution — O(1) instead of filesystem traversal
- swain-box migrated from project root symlink to bin/swain-box
- swain-init now bootstraps .agents/bin/ during project onboarding

### Planned
- Pre-runtime crash recovery script designed with two new specs (SPEC-180, SPEC-181) — the operator will type bin/swain to get crash detection, debris cleanup, and session resume before the LLM starts

### Supporting Changes
- ADR-019 codifies the project-root script convention with operator-facing (bin/) and agent-facing (.agents/bin/) tiers
- SPEC-135/136/137/147/170 aligned to use .agents/bin/ paths
- EPIC-047 created and completed — five child specs covering doctor auto-repair, init bootstrap, bin/ migration, and skill-wide resolution migration

## [0.21.1-alpha] - 2026-03-28

### Features
- Skills now fetch and merge upstream before pushing, preventing avoidable push rejections when trunk moves during a worktree session (swain-sync worktree path, swain-release trunk + release branch push)

### Research
- Cline Kanban added to kanban-tools trove — browser-based agent orchestration board with worktree isolation, validating swain's worktree-per-task pattern

## [0.21.0-alpha] - 2026-03-28

### Features

#### Session lifecycle management

Sessions now have a bounded lifecycle — start, work, close, resume — with
decision budgets that nudge the operator to wrap up before cognitive overload.
The status dashboard was absorbed into swain-session so project health,
recommendations, and session state live in one place. Every state-changing
skill now checks for an active session before proceeding, and an alignment
audit verified all skills and scripts follow the new lifecycle contract.
Part of the ongoing Session Facilitation Rebuild (EPIC-039).

#### tmux-based swain-stage removed

The tmux stage system is gone. Session management no longer depends on tmux —
it works in any terminal, any agentic runtime. Orphaned stage-status hooks
were cleaned up across all skill files.
- Launcher free text (e.g. `swain new bug about timestamps`) is now forwarded as the session purpose and auto-bookmarked
- Deterministic worktree naming with timestamp and random suffix prevents same-second collisions
- Pre-commit hooks now resolve paths via `$CLAUDE_PROJECT_DIR`, fixing failures when running inside worktrees
- Post-GREEN TDD self-critique gate added to swain-do's test-driven development enforcement
- Session bootstrap jq fallback hardened with 24 tests covering edge cases

### Planned
- Pre-launch crash recovery — swain will check for prior sessions that crashed due to terminal or host shutdown and offer to resume or clean up
- Session sleep and end operations are being designed for graceful session suspension and termination
- Doctor consolidation and PR queue review spikes added to the research backlog

### Research
- Pre-runtime structural layer (SPIKE-051) — Go verdict with 5 proposed specs for the swain shell launcher to subsume runtime launch
- Agent session persistence trove — 5 sources on session state across agent restarts
- OpenTelemetry trove — 11 sources on observability for agent systems
- Kanban tools trove extended with Cline/kanban source

### Supporting Changes
- ADR-017 defines supported agentic CLI runtimes (Claude Code, Crush, Gemini CLI, Copilot CLI, OpenCode)
- ADR-018 requires runtime invocations to be structural (hooks, config) rather than prosaic ("please run X")
- Artifact renumber collision fix for concurrent EPIC-045 worktree work

## [0.20.0-alpha] - 2026-03-27

### Features

#### swain-init delegates to swain-session after first run

After initial onboarding completes, swain-init now hands off directly to swain-session instead of stopping. Returning users get session restoration automatically without a separate invocation step.

#### Frontmatter contract: evidence-pool renamed to trove

The frontmatter schema contract (DESIGN-006) renamed the `evidence-pool` field to `trove` across all artifact types, and added a `trove` field to PERSONA. A bulk migration updated 160 artifacts to match the new naming, completing the vocabulary unification started in v0.6.0.

### Planned
- Shell launcher onboarding is being planned to streamline first-run experience for new swain users installing via shell scripts
- Session bootstrap consolidation and tool-call noise audit are being designed to reduce startup overhead and suppress low-value tool calls during session init

### Research
- Vibe coding practitioner experience and agent service provisioning troves created with initial sources
- Self-hosted LLM inference costs (SPIKE-045) — trial findings recorded with costed alternatives for local model hosting

### Supporting Changes
- Frontmatter-contract.yaml sourcecode-ref repinned after trove rename
- Retro session captured for trove research and evidence-pool contract migration

## [0.19.0-alpha] - 2026-03-25

### Features

#### Semantic topic matching in trove prior art check

swain-search's prior art check now runs in two phases. Phase 1 searches by literal keyword (existing behavior). Phase 2 extracts topic keywords from the source's content and searches existing trove tags and synthesis summaries for semantic overlap. A forced decision gate makes every Create/Extend routing decision visible and auditable — no more silent misrouting when a source uses different vocabulary for a known topic.

### Research
- Agent memory systems trove extended with Cog (marciopuga/cog) — a convention-only cognitive architecture for Claude Code with 3-tier memory, L0/L1/L2 progressive retrieval, and a 4-stage maintenance pipeline. Synthesis rewritten as a 6-tier landscape; SPIKE-044 rewritten with full context across all 12 sources.
- Ollama cloud subscription pricing trove — 6 sources on GPU-as-a-service costs across RunPod, Vast.ai, Lambda, and others

### Supporting Changes
- Trove misrouting retro — root cause analysis and process fix for standalone trove creation when extending was correct

## [0.18.0-alpha] - 2026-03-25

### Features

#### Skill folder gitignore hygiene

swain-doctor now verifies that vendored swain skill directories (swain/ and swain-*/ under .claude/skills/ and .agents/skills/) are gitignored in consumer projects. Consumer projects' own skills are not affected. Auto-remediates missing entries on confirmation. Skipped when running inside the swain source repo.

#### Cross-reference integrity repair

Resolved all cross-reference gaps and missing reciprocal edges across 45 artifacts. xref validation now catches orphaned links before they accumulate.

#### Worktree isolation by default

swain-do now isolates all mutating tasks into worktrees, not just implementation tasks. Prevents accidental trunk contamination during any tracked work.
- Source renumber fix — corrected --source-dir targeting, keeper restoration, and dry-run allocation tracking
- Superpowers detection fix — the zsh word-splitting difference from bash caused the detection loop to always report 0/6 skills found. Fixed by inlining the skill list and using file-test checks.

### Planned

#### PURPOSE.md and vision restructuring

Swain's identity migrated from VISION-001 into a standalone PURPOSE.md, establishing a seven-vision structure split into foundational and aspirational tiers. Governance references now point to PURPOSE.md as the canonical identity source.

#### Swain Memory Architecture

Planning began for structured agent memory — moving beyond flat file memory toward graph-based, scoped memory that persists learnings across sessions.
- Skill chaining table refactor proposed — extracting the superpowers chaining table from AGENTS.md into a dedicated reference file for cleaner governance

### Research
- Ollama Cloud Dispatch Worker feasibility spike — 10 sources collected across tool-calling architecture, API testing, and vLLM integration
- Agent memory systems — trove extended with OSS frameworks, graph memory, and MCP servers (10+ sources across two collection rounds)
- Product vision frameworks — 10 sources on tenets, Amazon principles, and intent hierarchies
- LikeC4 architecture-as-code — 15 sources collected
- Claude Code auto-mode and thinking redaction troves created

### Supporting Changes
- ADR-015 amended — tickets as committed coordination state, renamed to Merge Tickets To Trunk
- Governance block reconciled to canonical AGENTS.content.md with updated heading levels and expanded description
- Security scan findings triaged — eval removed from migration script, false-positive semgrep annotations added to hook scripts

## [0.17.0-alpha] - 2026-03-23

### Features

#### Centralized artifact number allocation

EPIC-043 delivered. next-artifact-number.sh scans all worktrees to allocate globally unique artifact IDs without collisions. detect-duplicate-numbers.sh catches conflicts with 13 test cases, and swain-sync now gates on collision-free state before pushing. migrate-bugs.sh and all SKILL.md step-1 instructions migrated to use the centralized allocator.

#### Ephemeral ticket lifecycle (ADR-015)

Tickets are now treated as disposable execution scaffolding rather than permanent records. swain-do and swain-retro updated to match — tickets track in-flight work and are cleaned up after completion.

### Research
- Platform hooks validation completed (SPIKE-038) — 4 of 5 platforms validated (Claude Code, Gemini CLI, Copilot CLI, OpenCode) with working prototypes for each; findings written to INITIATIVE-020
- Phase complexity model (SPIKE-043) — Stacey Matrix adaptation for swain, 4 sources collected

### Supporting Changes
- Retro learnings routing corrected — findings go into skill files, not memory
- EPIC-043 and SPIKE-038 lifecycle completions

## [0.16.1-alpha] - 2026-03-23

### Features

#### Paywall proxy fallback for swain-search

swain-search now automatically detects paywalled Medium articles and tries proxy services before falling back to truncated content. A YAML registry maps domains to ordered proxy lists with truncation signals, and a deterministic shell script handles URL matching without spending LLM tokens. Ships with freedium-mirror (primary) and freedium (fallback) for medium.com. Extensible to other paywalled domains by editing the registry — no skill file changes needed.
- Superpowers chain routing fixed — brainstorming now correctly chains through swain-design for artifact creation instead of skipping it

### Research
- PreToolUse hook adapter feasibility validated — Claude Code's hook system can gate tool calls, enabling runtime governance enforcement

### Supporting Changes
- AGENTS.md reconciled from canonical AGENTS.content.md source
- swain-dispatch deprecated (requires API billing, incompatible with Max/Pro)

## [0.16.0-alpha] - 2026-03-23

### Features

#### Retro session intelligence

New epic (EPIC-042) with four child specs defining how swain-retro will evolve: structured retro data extraction, cross-session pattern detection, retro-driven backlog generation, and retro quality scoring. The design spec covers the full architecture.

#### Paywall proxy fallback for swain-search

When swain-search encounters a paywalled or inaccessible page, it now falls back to a proxy chain (archive.org, Google cache, etc.) to retrieve content before giving up. Includes an implementation plan for the full proxy stack.
- State machine definitions added to the artifact frontmatter schema design (DESIGN-006) — formalizes lifecycle transitions for all artifact types
- adr-check.sh exit codes fixed to properly distinguish missing vs. malformed ADR files
- Superpowers chain bug fixed — artifact creation was being skipped when superpowers skills were chained during swain-design workflows

### Planned

#### Trustworthy agent governance

A new vision and initiative exploring how swain can help operators verify agent behavior — including alignment monitoring, platform hooks validation, task management system evaluation, and decision framework integration.
- Centralized artifact number allocation being planned — ensuring artifact IDs are globally unique and conflict-free across concurrent agent sessions
- swain-dispatch deprecated — requires API billing, incompatible with Max/Pro subscription plans

### Research
- Agent alignment monitoring — 6 sources collected covering runtime verification, constitutional AI enforcement, and behavioral drift detection techniques
- Platform hooks validation — 5 sources on Claude Code, Cursor, and Windsurf hook/rule systems for constraining agent behavior
- Task management systems — 5 sources surveying structured task tracking approaches for AI-assisted development, plus swain ecosystem analysis
- Critical path analysis — 5 sources on dependency-aware scheduling and bottleneck identification for multi-agent project planning

### Supporting Changes
- Lifecycle hash stamps and index refreshes for new artifacts
- Swain ecosystem analysis rewritten in terse format with honest traceability scoring

## [0.15.1-alpha] - 2026-03-22

### Features
- swain-search now checks existing troves for relevant content before running web searches or creating new troves — avoids duplicate research and surfaces connections to prior work

### Research
- field-notes trove created — catch-all for interesting references without immediate purpose; first entry: /sclear session capture skill (devlog extraction patterns)

## [0.15.0-alpha] - 2026-03-22

### Features

#### Skill change discipline

Non-trivial skill file changes now trigger an advisory warning at session start via swain-preflight. A new governance principle ("Skill changes are code changes") in AGENTS.md instructs agents to use worktree isolation for structural skill edits — the same discipline applied to .sh and .py files. Trivial fixes (typos, single-line corrections, ≤5-line diffs) remain trunk-eligible. Detection script: check-skill-changes.sh scans the last 10 trunk commits for non-trivial skill diffs.
- swain-do pre-plan step now checks for unmerged worktree branches before creating implementation plans, catching already-done work early

### Planned
- Worktree discipline epic (EPIC-041) — generalizing trunk change detection beyond skill files to cover all code-like files (scripts, tests, tooling)

### Supporting Changes
- Retroactive close of 9 implemented-but-untracked specs: SPEC-052 (vision-rooted chart), SPEC-057 (tk close lock), SPEC-091 (TRAIN type), SPEC-103 (cross-ref hyperlinking), SPEC-115 (roadmap initiative filtering), SPEC-129 (specwatch-ignore), SPEC-138 (tab name bleed), SPEC-139 (Desired Outcomes), SPEC-142 (completion/retro chain)
- swain-do skill audit and quality rectification (v3.2.0)

## [0.14.0-alpha] - 2026-03-22

### Features

#### Per-artifact roadmap slices

chart.sh roadmap --scope generates focused roadmap slices for individual Visions and Initiatives, written directly to each artifact's folder. Each slice shows an intent summary, a children tree grouped by lifecycle phase, a progress bar counting all descendants, a recent activity table with absolute timestamps, and an Eisenhower priority subset. The project-wide chart.sh roadmap now regenerates all slices automatically alongside ROADMAP.md. The swain-roadmap skill accepts an optional artifact ID to generate and open a single slice. Replaces the old --focus flag.

#### Roadmap decision and recommendation sections

ROADMAP.md now opens with a Decisions section (bucketed into operator-facing vs agent-handleable) and a Recommended Next callout showing the single highest-leverage item. When no decisions are pending, the section explicitly states so rather than being absent.

#### SPEC-level priority-weight override

SPECs can now carry their own priority-weight in frontmatter, overriding the inherited weight from their parent Epic or Initiative. The priority cascade is Vision > Initiative > Epic > Spec, with each level able to override its ancestor.
- Desired Outcomes section added to SPEC, EPIC, and INITIATIVE templates — connects shipping to user impact
- Artifact frontmatter schema contract (ADR-014, DESIGN-006) — formalizes which fields each artifact type must carry
- Retro docs now hyperlink bare artifact IDs automatically
- brief-description field parsed into specgraph node schema (forward-compat for SPEC-144)

### Planned
- Per-artifact roadmap slices will gain agent-authored intent summaries once the brief-description frontmatter field (SPEC-144) is implemented — currently shows a placeholder that swain-roadmap post-processes
- Design creation prompts and design coverage audit lens being specified to improve how DESIGN artifacts are authored and validated
- Worktree ticket isolation bug (SPEC-142) identified — tk tickets created in worktrees get orphaned when the worktree is removed

### Research
- PM-in-the-age-of-AI trove — 8 sources collected covering how product management practices are evolving with AI tooling

### Supporting Changes
- Plan completion handoff in swain-do now triggers the retro chain consistently
- Full project retro expanded with narrative history and evolution timeline
- SPEC-120, SPEC-134, SPEC-141, SPEC-143 transitioned to Complete with verification evidence

## [0.13.1-alpha] - 2026-03-21

### Features

#### Cross-session title isolation

Fixed a bug where tmux tab names bled across iTerm tabs when multiple sessions ran on the same tmux server. The root cause: when a pane-focus-in hook fires via run-shell, tmux's display-message and untargeted rename commands resolve to the calling client's session — not the hook's session. All sessions were writing OSC title escapes to the wrong TTY. The fix passes session name, pane path, and pane ID as environment variables that tmux expands at hook fire time, then uses explicit -t targeting for every tmux command.

### Supporting Changes
- Full-project retrospective covering v0.1.0 through v0.13.0 (14 days, 730 commits, 13 releases)

## [0.13.0-alpha] - 2026-03-21

### Features

#### Universal find-based script discovery

All swain skills now resolve script paths using find-based discovery instead of hardcoded relative paths. Previously, $REPO_ROOT/skills/... paths silently failed when agents ran from linked worktrees because git rev-parse --show-toplevel returns the worktree root, not the main repo root where skills live. Eight SKILL.md files updated: swain-doctor, swain-status, swain-security-check, swain-session, swain-do, swain-stage, swain-sync, swain-retro.
- swain-doctor reduced from 406 to 266 lines by extracting lifecycle migration, worktree detection, and initiative migration into reference files with one-line pointers

### Planned
- Roadmap legend epic name visibility — when an initiative has a single child epic, the legend will show both names instead of hiding the epic behind the initiative grouping

### Research
- Skill routing disambiguation (SPIKE-033) — investigated overlap between swain-help and swain-design trigger phrases. Found the problem narrower than the audit suggested: Claude Code's description-based routing plus enriched descriptions handle most cases. Recommended No-Go on a disambiguation framework; added one routing hint to the meta-router instead.

### Supporting Changes
- EPIC-031 Skill Audit Remediation completed — 7 of 9 specs verified as already done, 2 implemented, retro captured

## [0.12.1-alpha] - 2026-03-21

### Supporting Changes
- Retrospective changelog rewrite for 0.7.0–0.10.0 — applied ADR-014 data contract quality rules to remove artifact ID soup, replace commit-type buckets with thematic narratives, and rename "Roadmap"/"Coming Next" to "Planned"

## [0.12.0-alpha] - 2026-03-21

### Features

#### Contract-driven changelog pipeline

The changelog generation pipeline is now governed by a data contract (changelog-contract.yaml) that defines per-field interpretation rules instead of scattering them across SKILL.md prose. Each field has a semantic (what it means), source (where data comes from), and quality block (rules, anti-patterns with explanations, good/bad examples). The agent reads the contract before classifying commits, producing better-structured data for the Jinja2 template to render.
- "Coming Next" section replaces "Roadmap" in changelogs — forward-looking previews of planned work instead of artifact state transitions

### Research
- Data contract standards — surveyed ODCS v3.1.0, datacontract.com spec v0.9.0, and OpenMetadata Data Contract entity to inform ADR-014

## [0.11.0-alpha] - 2026-03-21

### Features

#### Auto-detecting trunk branch

swain-trunk.sh detects the development branch from git worktree state instead of hardcoding it. Repos on develop, main, trunk, or any branch are supported automatically with zero configuration. All runtime skills (swain-sync, swain-doctor, swain-release) now use dynamic detection via a $TRUNK variable sourced at workflow start. An optional git.trunk override in swain.settings.json handles edge cases like detached HEAD, but is never required for normal operation.
- Doctor and preflight now detect whether the trunk+release model is configured and advise on migration

### Planned
- Data contracts for agent-produced data — a lightweight schema+semantics+quality contract format that gives agents scoped per-field interpretation rules instead of unstructured prose. The changelog pipeline is the first consumer; future skills will follow the same pattern.

### Supporting Changes
- Jinja2 changelog template with H4 feature headings for swain-release
- Changelog pipeline rewritten to be contract-driven — interpretation rules now live in changelog-contract.yaml instead of SKILL.md prose
- v0.10.0-alpha release retrospective

## [0.10.0-alpha] - 2026-03-21

### Features

#### CLI roadmap renderer

`chart.sh roadmap --cli` produces deterministic, terminal-friendly output grouped by Eisenhower quadrant with all first-degree children nested under their parent initiative. New `swain-roadmap` skill wraps it as the user-facing entry point: regenerate ROADMAP.md, open it, and display a scannable CLI summary.
- Worktree landing via merge-with-retry verified end-to-end — concurrent agents can now land work on trunk without rebasing, with automatic fetch-merge-retry on push rejection
- iTerm tab name bleed fix — OSC title escapes now target the specific client terminal instead of using global `tmux set-titles`

### Planned
- Session facilitation rebuild — rethinking how swain helps the operator maintain focus, make decisions, and recover context across sessions
- Two new behavioral rules distilled from retrospective: agents must read artifacts before reasoning about them, and must produce evidence before asserting outcomes

### Research
- Google Stitch SDK trove — 7 sources collected and normalized across 2 research sessions

### Supporting Changes
- Artifact cross-reference enrichment — ~100 doc files now have sorted, bidirectional `linked-artifacts` frontmatter
- Changelog format standardized to four fixed sections

## [0.9.0-alpha] - 2026-03-20

### Features

#### Trunk+release branch model

swain now supports a two-branch workflow where `trunk` is the development branch and `release` is the distribution branch, squash-merged at release time. Consumers installing via `npx skills add` get clean single-commit releases instead of merge noise from concurrent agent landing. A migration script handles the rename from `main` to `trunk` and configures the GitHub default branch.
- Merge-with-retry replaces rebase-then-push for worktree landing — agents no longer need to rebase, reducing conflicts and data loss risk
- Roadmap now shows SPECs and Spikes attached directly to Initiatives — previously only Epics were rendered, silently dropping direct-child specs from Eisenhower tables, Gantt charts, and progress counters

### Supporting Changes
- DESIGN artifact template expanded with domain field guidance (`interaction`, `data`, `system`)
- Quadrant boundary alignment and X-axis jitter fix for roadmap scatter plot
- Dependency graph switched to `flowchart TD` layout for clearer rendering

## [0.8.0-alpha] - 2026-03-20

### Features

#### Security scanning

Swain now has a built-in security posture — not just "run a scanner" but a layered system that integrates into the existing workflow at multiple points. **swain-security-check** orchestrates gitleaks, osv-scanner, trivy, semgrep, and two built-in scanners (context file injection, threat surface heuristic) into a unified, severity-bucketed report. Missing scanners are skipped with install hints — the scan always completes. Doctor checks scanner availability on session start. A post-implementation security gate runs automatically before claiming work is complete, and external security skills can hook in via a documented interface.

#### Docker sandbox (swain-box)

swain-box grew from a proof-of-concept Docker wrapper into a real launcher with multi-step UX. The launcher walks through authentication first (OAuth token from Keychain, API key detection, login confirmation), then isolation (worktree-enforced sandbox with bind-mounted project files). Auth and isolation are separate menus, not a single flag soup. A long tail of OAuth and API key bugs resolved — the launcher now warns clearly when credentials are missing rather than failing silently.

#### TRAIN artifact type

A new artifact type for training materials, documentation guides, and onboarding content. TRAIN gets the full lifecycle treatment: type definition, template, staleness detector (`train-check.sh`), inference routing, specwatch integration, and phase transition hooks. As part of this work, "enriched linked-artifacts" were renamed to the clearer **artifact-refs**, and a new **sourcecode-refs** field was added for linking artifacts to implementation files.

#### Design integrity

Artifacts can now detect when their own content has drifted from what was reviewed and approved. `design-check.sh` compares blob SHAs of design-critical sections against stamped baselines, surfacing drift in specwatch, swain-sync, and swain-design workflows. DESIGN artifacts gain a Design Intent section for capturing original rationale, and swain-design now scans active same-type artifacts for scope overlap when creating new standing-track artifacts.

### Planned
- Safe autonomy direction established — unattended agent safety guardrails, credential scoping, and multi-runtime support being designed
- Portable framework patterns being researched — how swain's skill model could work outside Claude Code
- Unified project state graph planned — event-driven orchestration to replace prose chaining tables

### Research
- Design staleness and drift detection — 7 sources surveyed for prior art on content drift detection
- Docker sandbox patterns and docker-agent isolation approaches
- Claude Code plugin intercom mechanisms
- Framework portability — surveyed Cursor, Windsurf, and generic agent patterns

### Supporting Changes
- Gracefully handle unauthenticated gh CLI in swain-keys
- Slim AGENTS.md from 220 to ~60 lines
- Skill audit remediation across all skills
- swain-do: pre-plan implementation detection, retroactive-close for already-shipped specs, and several ticket CLI fixes
- tk: release claim lock on close to prevent stale lock accumulation

## [0.7.0-alpha] - 2026-03-17

### Features

#### Pane-aware tmux tab naming

Tmux tabs now show the project name and branch for the active pane, with `--path` flag support and worktree awareness. Tab names update automatically when switching between panes that are in different repos or worktrees. Includes `resolve_path()` extraction, per-window hooks, and `SWAIN_TMUX_SOCKET` override for testability.
- Project identity enforcement — swain-design validates that artifacts reference the correct project context

### Research
- Public intake channel authentication — threat-modeled authentication for public-facing intake channels, evaluated TOTP, OAuth, and API key mechanisms, concluded TOTP-in-the-clear is acceptable when scoped to low-value intake actions with replay mitigation

### Supporting Changes
- THIRD_PARTY_NOTICES and attribution header for vendored tk (MIT, wedow/ticket)
- Cross-reference gap closure across 79 artifact files
- Tab naming acceptance test suite

## [0.6.0-alpha] - 2026-03-16

### Trove Redesign (BREAKING)

"Evidence pool" is now "trove" — a better name for what swain-search produces,
which ranges from research evidence to reference libraries to repo mirrors.
`evidencewatch` becomes `trovewatch`.

**Hierarchical sources** — sources are no longer flattened to `001-slug.md`. Each
source gets its own directory (`sources/<source-id>/`), and repository or
documentation-site sources mirror their original tree structure. Large sources can
be selectively ingested (`selective: true`).

**Migration** — `migrate-to-troves.sh` converts existing evidence pools
non-destructively. `swain-doctor` detects unmigrated pools and offers migration.

**Wordlist disambiguator** — when source-id slugs collide within a trove, a
`__word1-word2` suffix is appended from a curated wordlist.

### Swain Chart & Specgraph

- Add `swain chart` CLI with lens framework and VisionTree renderer
- Extend priority-weight cascade to epics
- Wire swain chart into all skill invocations

## [0.5.0-alpha] - 2026-03-15

### Prioritization Layer

Swain now answers "what matters most?" — not just "what's actionable?"

**Initiative artifact type** — a new layer between Vision and Epic for grouping
related work under a strategic focus. Epics and standalone specs attach to
Initiatives; Initiatives attach to Visions. This gives the operator a way to
say "security matters more than polish right now" and have swain's
recommendations follow.

**Vision-weighted recommendations** — Visions carry a `priority-weight`
(high/medium/low) that cascades through the hierarchy. The recommendation
formula (`score = unblock_count × vision_weight`) surfaces decisions with the
most downstream leverage in the highest-priority strategic direction.

**Attention tracking** — swain scans git history to show where the operator has
actually been spending time vs. where they said they'd focus. Drift alerts fire
when a high-priority vision goes untouched past a configurable threshold.

**Focus lane** — the operator can say "focus on security" to scope
recommendations to a single vision or initiative. Other lanes appear as
peripheral awareness ("Meanwhile: Design has 4 pending decisions") — visible
but not nagging.

**Guided migration** — `swain-doctor` detects existing epics without an
Initiative parent and walks the operator through grouping them, creating
Initiatives, and setting vision weights. Migration is incremental — one vision
at a time.

### Supporting Changes

- Three new specgraph commands: `recommend`, `decision-debt`, `attention`
- Mode inference in swain-status (vision mode vs detail mode, with ask on ambiguity)
- Artifact type selection guide in swain-design (Initiative vs Epic vs Spec)
- Metadata update workflow for `priority-weight` and `parent-initiative`
- Prioritization settings in `swain.settings.json` (drift thresholds, attention window)
- Updated all reference docs: relationship model, lifecycle tracks, specgraph guide, phase transitions, quick-ref

## [0.4.0-alpha] - 2026-03-14

### Changes
- Rewrite README to focus on decision traceability and human-AI alignment
- Add alpha status callout
- Remove experimental sandbox section
- Remove deprecated swain-push from skills table
- Adopt 0.x semver to reflect alpha status (previous v1/v2/v3 tags preserved as history)

## [3.0.0] - 2026-03-14

### Breaking Changes
- **swain-do now requires worktree isolation for implementation work.** When invoked from the main worktree for plan creation, task claim, or code execution, swain-do invokes the `using-git-worktrees` superpowers skill to create a linked worktree first. If superpowers is not installed, swain-do stops and reports rather than running in the main worktree. Read-only operations (`tk ready`, status checks) are unaffected.

### New Features
- **Isolated execution (`claude-sandbox`)** — new `scripts/claude-sandbox` launcher runs Claude Code inside a sandboxed environment. Tier 1 uses native OS sandboxing (macOS `sandbox-exec`, Linux Landlock/bubblewrap). Tier 2 (`--docker`) runs in a Docker container with bind-mounted project files. Config via `swain.settings.json` (`sandbox.dockerImage`, `sandbox.allowedDomains`). (EPIC-005, SPEC-048, SPEC-049)
- **Specgraph Python rewrite** — `specgraph.sh` replaced by a Python implementation with a full CLI: `build`, `ready`, `next`, `status`, `overview`, `mermaid`, `blocks`, `blocked-by`, `tree`, `neighbors`, `scope`, `impact`, `edges`. Finished artifacts hidden by default; `--all` shows them. (EPIC-013, SPEC-030/031)
- **Cross-reference (xref) validation** — specgraph now validates bidirectional frontmatter consistency across all artifacts. Body references not declared in frontmatter and missing reciprocal links are surfaced in `swain-status` as a Cross-Reference Gaps section. (SPEC-032, SPEC-033)
- **Automatic worktree lifecycle** — swain-sync is worktree-aware: detects linked worktree context, rebases onto `origin/main` when no upstream exists, pushes via `HEAD:main`, opens a PR on branch-protection rejection, and prunes the worktree after landing. swain-doctor detects stale linked worktrees (orphaned, merged, unmerged) and reports cleanup commands. (EPIC-015, SPEC-039, SPEC-043, SPEC-044, ADR-005)
- **swain-status decision support** — status output now leads with a single ranked Recommendation (highest-unblock-count ready item), followed by a Decisions Needed table for human-gated artifacts. (SPEC-036)
- **Artifact workflow efficiency** — fast-path authoring skips full lifecycle ceremony for low-ceremony artifacts. Lazy index rebuild defers specgraph cache updates until needed. Inline lifecycle hash stamping collapses stamp commits into their transition commit. (EPIC-014, SPEC-045/046/047)
- **MOTD improvements** — staged/unstaged/untracked file counts in the header. Interactive Commit & Push button. Reactive agent status updates via Claude Code hooks (no manual `motd update` required). Border animation direction fixed. (EPIC-011, SPEC-040/041/042)
- **Dynamic track resolution** — specgraph now reads the `track` field from artifact frontmatter to classify resolution logic, replacing the hardcoded `RESOLVED_RE` regex. Existing artifacts backfilled with `track` values. (SPEC-038)
- **Model routing annotations** — all skills annotated with `<!-- swain-model-hint: {model}, effort: {level} -->` for runtime model selection. (EPIC-007, SPEC-026)
- **Agent dispatch** — `swain-dispatch` ships artifacts to background agents via GitHub Issues + Claude Code Action workflow. (EPIC-010)
- **Automated retrospectives** — `swain-retro` captures learnings at EPIC completion or on demand, prompts reflection questions, and distills findings into memory files. (SPEC-011)

### Fixes
- Fix `ticket-query` crash with `TICKETS_DIR: unbound variable` when called by external scripts (SPEC-035)
- Fix specgraph `ready` command leaking standing-track artifacts (ADR, PERSONA, JOURNEY, VISION, RUNBOOK, DESIGN) into implementation-ready list (SPEC-037)
- Fix swain-doctor to auto-create `swain.settings.json` when missing
- Fix specwatch to suppress superseded-ADR warnings for closed artifacts
- Fix swain-session to store `session.json` per-project in `.agents/` instead of global memory (SPEC-027)
- Fix `.worktrees/` not gitignored — added pattern to `.gitignore`

### Documentation
- README: add Isolated execution section (`claude-sandbox` usage)
- README: document automatic worktree isolation in swain-do and swain-sync workflow
- ADR-005: document worktree lifecycle decision — swain-do creates, swain-sync lands

## [2.0.0] - 2026-03-12

### New Features
- Add swain-session and swain-stage skills (tmux workspace, bookmarks, preferences)
- Add swain-status skill for cross-cutting project dashboard
- Add swain-help skill for contextual help and onboarding
- Add swain-init skill for one-time project onboarding
- Add swain-keys skill for per-project SSH key provisioning
- Add swain-search evidence pool collection and normalization (EPIC-001)
- Add specgraph dependency visualization with hide-finished default
- Add specwatch bd-sync checker and two-phase audit workflow
- Add swain meta-router for sub-skill dispatch
- Add OSC 8 clickable hyperlinks for artifact IDs
- Add decision-support rendering with impact sorting to swain-status
- Add verification gate for Spec Testing phase
- Add Textual TUI MOTD for swain-stage
- Backup local modifications before skill update

### Fixes
- Fix doctor/update: add command-based detection alongside HOME dotfolder checks
- Fix update: autodetect agent platforms to prevent dotfolder clutter
- Fix doctor: clean up platform dotfolders created by npx skills add
- Fix doctor: clean up retired pre-swain skills during legacy cleanup
- Fix swain-session: use #W format token for tmux set-titles-string
- Fix specwatch: grep -c zero-match fallback
- Fix swain-stage: redesign focus layout as 3-pane with browser and TUI MOTD

### Documentation
- Frame swain around operator decision-support and agent alignment
- Rewrite README for new user onboarding (EPIC-003)
- Create VISION-001, PERSONA-001/002, JOURNEY-001/002, EPIC-002/003/004
- Complete SPIKE-003/004, close SPIKE-001/002
- Add EPIC-004 + SPIKE-004: Superpowers integration assessment
- Unify BUG into SPEC type system

### Refactoring
- Centralize session bookmark updates via swain-bookmark.sh
- Extract reference docs and restructure swain-design SKILL.md
- Extract governance content into single-source-of-truth reference file
- Slim AGENTS.md and relocate detail into skill files
- Migrate python3 invocations to uv run
- Remove automated conflict resolution from swain-push

## [1.1.0] - 2026-03-10

### Breaking Changes
- Rename swain-config → swain-doctor (legacy cleanup handles the transition)

### New Features
- Add beads gitignore hygiene to swain-doctor — validates `.beads/.gitignore` against canonical reference every session, patches missing entries
- Add `git rm --cached` cleanup to swain-doctor — untracks runtime files that leaked into git
- Add `source: swain` fingerprint to all skill frontmatters for safe legacy cleanup
- Add `references/legacy-skills.json` — machine-readable old→new skill name mapping
- Add `references/.beads-gitignore` — canonical gitignore reference for `.beads/` directories
- Add fingerprint safety check to legacy skill cleanup — third-party skills with overlapping names are never deleted

### Fixes
- Fix swain-update to use `--all` flag for non-interactive `npx skills add`
- Fix swain-init to invoke swain-doctor in Phase 4 (catches broken `.beads/.gitignore` on both fresh and existing installs)

## [1.0.0] - 2026-03-08

### New Features
- Rename all skills with `swain-` namespace prefix (swain-config, swain-design, swain-do, swain-release, swain-push, swain-update)
- Add legacy skill cleanup on session start via swain-config
- Add skill table and conflict resolution policy to AGENTS.md
- Enforce TDD methodology in implementation plans
- Add product-type branching for vision artifacts
- Implement governance skill with first-use setup
- Add release automation skill
- Add execution tracking skill (bd/beads integration)
- Add spec management skill (artifact lifecycle)
- Add swain-push skill (commit, push, conflict resolution)
- Add swain-update skill (self-updater via npx)

### Documentation
- README with full skill description table
- AGENTS.md as canonical consumer governance template
