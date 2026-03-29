---
title: "Project-Root Script Convention"
artifact: ADR-019
track: standing
status: Proposed
author: cristos
created: 2026-03-28
last-updated: 2026-03-28
linked-artifacts:
  - SPEC-067
  - SPEC-180
  - SPEC-181
  - EPIC-029
depends-on-artifacts: []
evidence-pool: ""
---

# Project-Root Script Convention

## Context

Swain ships scripts that fall into two categories:

1. **Operator-facing** — the human types them directly (e.g., `./swain`, `./swain-box`). These need to be discoverable at the project root.
2. **Agent-facing** — called by skills at runtime, never typed by the operator (e.g., `swain-trunk.sh`, `swain-status.sh`). These need a stable, resolvable path that works in both the swain repo and consumer projects.

The first instance of the operator-facing pattern — `swain-box` (SPEC-067) — established an ad-hoc convention: script lives at `skills/swain/scripts/swain-box`, swain-doctor creates a root symlink, and the doctor checks symlink health on every session. With the `swain` pre-runtime script (SPEC-180) following the same pattern, we need to codify both conventions.

The agent-facing gap surfaced when swain-doctor's preflight (EPIC-029) expected `$REPO_ROOT/scripts/swain-trunk.sh` in consumer projects — a script that only existed in the swain source repo, with no distribution or resolution mechanism.

## Decision

Swain scripts follow one of two conventions based on their audience.

### Operator-facing scripts (`bin/`)

Scripts the operator invokes directly.

**Examples:** `bin/swain-box`

#### 1. Canonical location

The script lives inside the skill tree at:

```
skills/<owning-skill>/scripts/<script-name>
```

For scripts that serve the swain meta-skill (not a specific sub-skill), the location is `skills/swain/scripts/<script-name>`.

The script is executable (`chmod +x`) and committed to the swain repo. Consumer projects receive it via `npx skills add`.

#### 2. `bin/` symlink

A symlink in `$REPO_ROOT/bin/` points to the canonical location:

```
bin/<script-name> -> ../skills/<owning-skill>/scripts/<script-name>
```

The symlink uses a **relative path** so it works regardless of where the repo is cloned. The `bin/` directory and its symlinks are created by either:
- **swain-init** (during onboarding — first-run setup), or
- **swain-doctor** (on subsequent sessions — repair if missing)

This keeps the project root clean — operator-facing executables live in a standard, well-understood directory rather than cluttering the root alongside `README.md` and config files.

#### 3. Doctor health check

swain-doctor includes a check for each `bin/` symlink, using this status model:

| Status | Condition | Action |
|--------|-----------|--------|
| **ok** | Symlink exists and points to the correct target | Silent |
| **missing** | No file at `bin/script-name` | Auto-create symlink, report "repaired" |
| **stale** | Symlink exists but points to wrong target (e.g., after skill tree restructure) | Auto-repair symlink, report "repaired" |
| **conflict** | A real file (not a symlink) exists at `bin/script-name` | Warn with manual remediation instructions |

#### Naming

Operator-facing scripts are prefixed with `swain` (e.g., `swain-box`) to avoid namespace collisions with other tools in `bin/`.

#### Gitignore

The `bin/` directory should be tracked in git for the swain repo itself. In consumer projects, `bin/` is gitignored (vendored skill directories are already gitignored per swain-doctor's skill folder hygiene check).

### Agent-facing scripts (.agents/bin/)

Scripts called by skills at runtime — the operator never invokes them directly.

**Examples:** `swain-trunk.sh`, `swain-status.sh`, `chart.sh`

#### 1. Canonical location

Same as operator-facing: the script lives in the skill tree at `skills/<owning-skill>/scripts/<script-name>`. This is the source of truth.

#### 2. Resolution path

Skills resolve agent-facing scripts via `.agents/bin/`:

```
$REPO_ROOT/.agents/bin/<script-name>
```

This directory contains symlinks to the canonical skill-tree locations:

```
.agents/bin/swain-trunk.sh -> ../../skills/swain-sync/scripts/swain-trunk.sh
```

Symlinks use **relative paths**. The directory is created and populated by:
- **swain-init** (during onboarding), or
- **swain-doctor** (repair on subsequent sessions)

Skills that call agent-facing scripts **must** use the `.agents/bin/` path, not `find` or hardcoded paths. This gives a stable, O(1) resolution with no filesystem traversal.

#### 3. Doctor health check

swain-doctor checks `.agents/bin/` symlinks using the same ok/missing/stale/conflict model as root symlinks. The preflight should check for the `.agents/bin/` path, not `$REPO_ROOT/scripts/`.

#### Why not project root?

Agent-facing scripts are implementation details. Placing them at the project root pollutes the operator's workspace with files they never interact with. `.agents/` is the runtime directory — session state, execution tracking, and now agent-facing binaries.

#### Why not `find` resolution?

The existing skill pattern (`find "$REPO_ROOT" -path '*/skill/scripts/name' -print -quit`) works but is slow (filesystem traversal on every invocation) and fragile (breaks if the skill tree restructures). `.agents/bin/` symlinks are resolved once at init/doctor time and thereafter O(1).

## Alternatives Considered

**Script directly in project root (no symlink).** Simpler, but the script diverges from the vendored version on updates. The symlink ensures the operator always runs the version that shipped with their installed skills.

**Operator-facing symlinks at project root.** The original convention (SPEC-067). Works, but clutters the project root with executable symlinks alongside `README.md`, `package.json`, etc. `bin/` is a standard Unix convention that keeps executables contained.

**Agent-facing scripts at project root.** Places internal utilities next to operator entry points, polluting the root with files the operator never touches.

**`find`-based resolution for agent-facing scripts.** The existing pattern in many skills. Works but incurs filesystem traversal on every call and breaks if the skill tree restructures. `.agents/bin/` trades one-time setup for O(1) resolution.

**No convention — each script decides independently.** The status quo. Works for one script, creates inconsistency at two, becomes confusing at three. The cost of the convention is near zero.

## Consequences

**Positive:**
- Clear mental model: `bin/` = for the operator, `.agents/bin/` = for skills. Clean project root.
- Future scripts of either type follow a known pattern with zero design effort.
- swain-doctor's symlink checks are formulaic — each new script adds ~20 lines using the same detection/remediation template, for both tiers.
- `npx skills update` automatically updates script content; symlinks don't change.
- Agent-facing resolution is O(1) — no `find` traversal at runtime.

**Accepted downsides:**
- Symlinks can confuse some tools (e.g., some editors resolve symlinks and open the canonical path). This is minor and consistent with standard Unix practice.
- Consumer projects need `.gitignore` entries for `bin/` and `.agents/bin/`. swain-doctor can automate this.
- Two resolution conventions instead of one — mitigated by clear audience distinction (operator vs. agent).

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-28 | — | Initial creation; codifies pattern established by SPEC-067 (swain-box) |
| Proposed | 2026-03-28 | — | Added two-tier model: operator-facing (`bin/`) vs agent-facing (`.agents/bin/`); motivated by swain-trunk.sh distribution gap (EPIC-029) |
