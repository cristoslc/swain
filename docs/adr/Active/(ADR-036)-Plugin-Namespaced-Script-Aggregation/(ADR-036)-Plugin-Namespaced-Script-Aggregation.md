---
title: "Plugin-Namespaced Script Aggregation"
artifact: ADR-036
track: standing
status: Active
author: cristos
created: 2026-04-06
last-updated: 2026-04-06
linked-artifacts:
  - EPIC-069
depends-on-artifacts: []
supersedes: ADR-019
trove: agent-script-directory-conventions
---

# Plugin-Namespaced Script Aggregation

## Context

[ADR-019](../../Superseded/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md) put operator scripts in `bin/` and agent scripts in `.agents/bin/`. Both use flat symlink directories that point into the skill tree. Three problems surfaced:

1. **Flat namespace collisions.** Two skills that ship a script with the same name clobber each other in `.agents/bin/`. This risk grows with every new skill.

2. **Industry misalignment.** The Agent Skills standard (Anthropic/AAIF) uses `scripts/` for skill-scoped code. Every major adopter agrees: Codex, Copilot, Kiro, Spring AI, OpenCode, Microsoft. None use `bin/` at this level. Claude Code plugins use `bin/` at the plugin root — but only for PATH-added executables. Swain's `.agents/bin/` matches neither convention.

3. **No plugin boundary.** If a consumer installs swain next to another skill framework, both write to the same `.agents/bin/` with no isolation. Claude Code solves this with `plugin-name:skill-name` namespacing. Swain has no equivalent.

Research across 14 sources (trove: `agent-script-directory-conventions`) confirms the gap. The Agent Skills ecosystem treats skills as self-contained packages. No standard defines cross-skill script aggregation. Swain fills a real need — agent scripts that cross skill boundaries need a stable path — but the flat layout doesn't scale.

## Decision

### Agent-facing script aggregation

Agent-facing scripts live under `.agents/scripts/<plugin>/`. The `<plugin>` name matches the framework that installed the skills. For swain:

```
.agents/scripts/swain/
├── swain-trunk.sh      -> ../../../skills/swain-sync/scripts/swain-trunk.sh
├── swain-preflight.sh  -> ../../../skills/swain-doctor/scripts/swain-preflight.sh
├── chart.sh            -> ../../../skills/swain-design/scripts/chart.sh
└── ...
```

**Namespace rules:**

- The plugin directory (`swain`) is the collision boundary. Swain owns dedup within its namespace. If two swain skills ship the same script name, swain-doctor reports the conflict.
- Other frameworks get their own directories (e.g., `.agents/scripts/acme/`). Cross-plugin collision is impossible by structure.
- Skills resolve agent-facing scripts via `$REPO_ROOT/.agents/scripts/swain/<script-name>`. This is the only supported path. `find`, direct skill-tree paths, and the legacy `.agents/bin/` path are all banned.

**Symlink mechanics:**

- Symlinks use relative paths.
- swain-init creates the directory at onboarding. swain-doctor repairs it on later sessions.
- In worktrees with a skill tree present, symlinks point to the local tree. In worktrees without a skill tree, the bootstrap copies scripts instead. Doctor detects and repairs the mode each session.

### Operator-facing script aggregation

Operator-facing scripts use a parallel aggregation model. This ADR defines the layout and collision rules. The exact DX path (how the operator invokes the command) is deferred to a DESIGN artifact.

**Aggregation path:** `.agents/bin/<plugin>/`

```
.agents/bin/swain/
├── swain     -> ../../../skills/swain/scripts/swain
└── swain-box -> ../../../skills/swain/scripts/swain-box
```

**Why `.agents/bin/`:** Claude Code plugins use `bin/` at plugin root for PATH-added executables. `.agents/bin/<plugin>/` follows that pattern. The two tiers stay clear: `scripts/` for agents, `bin/` for operators.

**DX note:** `.agents/bin/swain/swain` is not ergonomic to type. A shell alias, PATH entry, or wrapper solves this. The DESIGN artifact for operator DX will address invocation. This ADR only sets the aggregation layout.

### Script audience declaration

Each skill MAY mark individual scripts as `operator` or `agent` facing. Default is `agent`. The marker is a comment header:

```bash
#!/usr/bin/env bash
# swain-audience: operator
```

The bootstrap reads this header when creating symlinks. It routes scripts to `.agents/scripts/swain/` (agent) or `.agents/bin/swain/` (operator). No header means agent-facing.

### README files

The bootstrap writes `README.md` files in `.agents/scripts/` and `.agents/bin/`. These explain the swain extension of the Agent Skills standard. They are rebuilt on each init/doctor run. Do not edit them by hand.

### Migration from ADR-019

1. Doctor detects `.agents/bin/` with flat (non-namespaced) symlinks. It moves them to `.agents/scripts/swain/` or `.agents/bin/swain/` based on the audience header.
2. The project-root `bin/` directory is removed. Its symlinks move to `.agents/bin/swain/`.
3. All skill references to `.agents/bin/<script>` change to `.agents/scripts/swain/<script>`.
4. Doctor warns consumers on first run after update and migrates the layout.

## Alternatives Considered

**Flat namespace with collision detection (ADR-019).** Works at small scale. Breaks as skill count grows. No isolation between frameworks. The collision risk is structural.

**Per-skill paths (`.agents/skills/<skill>/scripts/<script>`).** Most standard-aligned. Rejected: (a) agent confusion in worktrees from fragmented paths, (b) every callsite must know which skill owns a script, and (c) paths are long and error-prone.

**Flat `.agents/scripts/<skill>-<script>` naming.** Bakes skill identity into filenames. Renaming a skill breaks all callsites. Still flat. Less likely to collide, but still possible.

**No aggregation — skills reference their own scripts.** Pure standard compliance. Rejected because swain has real cross-skill script needs (preflight calls trunk detection, session calls focus management).

## Consequences

**Positive:**

- Cross-plugin collision is impossible by structure. The namespace is the boundary.
- Names align with the Agent Skills ecosystem: `scripts/` for agents, `bin/` for operators.
- Intra-plugin collision is detectable. Doctor can report "skill X and Y both ship `validate.sh`."
- Migration is automatic. Doctor detects the old layout and converts it.
- README files make the convention self-documenting.

**Accepted downsides:**

- Paths are slightly longer: `.agents/scripts/swain/foo.sh` vs `.agents/bin/foo.sh`. One-time search-and-replace.
- Two aggregation directories instead of one. Clear audience split keeps them from being confusing.
- Operator DX is deferred. Consumers won't get a better `./bin/swain` experience from this ADR alone. That's intentional — aggregation and invocation are separate concerns.

## Upstream feedback

The Agent Skills standard has no convention for cross-skill script aggregation. Issues #95 and #100 on the agentskills repo are adjacent (skill-to-skill invocation) but don't cover shared executables. Filing an issue on `agentskills/agentskills` to describe the pattern is recommended but optional. Swain does not block on upstream.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-06 | -- | Supersedes [ADR-019](../../Proposed/(ADR-019)-Project-Root-Script-Convention/(ADR-019)-Project-Root-Script-Convention.md). Motivated by flat namespace collision risk, industry misalignment, and consumer bug report. Research: trove `agent-script-directory-conventions` (14 sources). |
