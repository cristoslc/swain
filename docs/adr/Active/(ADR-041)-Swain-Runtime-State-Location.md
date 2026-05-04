---
title: "Swain runtime state in .swain/; leave .agents/ to the emerging spec"
artifact: ADR-041
track: standing
status: Active
author: cristos
created: 2026-04-13
last-updated: 2026-04-13
linked-artifacts:
  - SPEC-305
  - ADR-040
  - ADR-042
depends-on-artifacts: []
evidence-pool: ""
---

# Swain runtime state in .swain/; leave .agents/ to the emerging spec

## Context

Swain currently uses `.agents/` as its runtime state and tooling directory. It holds `bin/` symlinks to skill scripts, `session.json`, `hook-state/`, `search-snapshots/`, `chart-cache/`, `specwatch-ignore`, and the installed `skills/` tree. Some entries are tracked. Most are runtime.

An emerging cross-tool spec stewarded by the Agentic AI Foundation — [`agentsfolder/spec`](https://github.com/agentsfolder/spec) — treats `.agents/` as **tracked canonical agent config**. Its schema defines `manifest.yaml`, `prompts/`, `modes/`, `skills/`, and `policies/` — all meant to be checked in. This is the opposite purpose from swain's current use. Any consumer that adopts the spec collides directly with swain's runtime.

Peer-agent dot-folders — `.claude/`, `.cursor/`, `.aider/`, `.goose/`, `.continue/`, and the long list swain tracks in `bin/swain`'s `agent_dirs` array — have no cross-tool standard for track-vs-ignore. Practice varies by project. Some teams track `.cursor/` for shared rules. Some ignore it. No convention makes swain the arbiter.

Two decisions need to be made together. Where does swain keep its runtime state? And what does swain tell consumer projects to gitignore for peer agents?

## Decision

**Runtime state moves to `.swain/`.** Every runtime path currently under `.agents/` migrates to `.swain/`. That includes `.swain/bin/`, `.swain/session.json`, `.swain/hook-state/`, `.swain/search-snapshots/`, `.swain/chart-cache/`, `.swain/specwatch-ignore`, and the installed `.swain/skills/` tree. `.agents/` is left free for the emerging agentsfolder spec. Future swain work may adopt that spec for its own canonical config.

**`.swain/` is gitignored in consumer projects** (with operator confirmation, per [SPEC-305](../../spec/Active/(SPEC-305)-Gitignore-Agentic-Runtime-Folders)). A narrow allowlist re-includes any subpath swain intends to track. Today the allowlist is empty.

**Peer-agent dot-folders are not gitignored by swain-init.** No cross-tool standard exists. Swain does not impose a policy the consumer may reasonably want to override. The consumer chooses whether to track `.cursor/`, `.claude/`, `.aider/`, and the rest. Swain's worktree bootstrap (per [ADR-040](ADR-040-Worktree-Bootstrap-Via-Post-Checkout-Hook)) still symlinks them in, whether they are tracked or not — the hook reacts to presence in the common root, not to ignore status.

## Alternatives Considered

- **Keep `.agents/` as swain runtime.** Lowest churn. Leaves swain in permanent collision with the emerging spec. Blocks consumers who want to adopt it.
- **Split `.agents/` in place — track canonical, ignore `.agents/runtime/`.** Keeps one folder for two purposes. Fragile. Harder to reason about. Every script needs to know which subtree it's in.
- **Gitignore all peer-agent dot-folders in consumer projects.** Imposes a policy with no shared basis. Would fight consumers who deliberately track `.cursor/` or `.claude/` for team sharing.
- **Migrate peer-agent dirs into `.swain/`.** Not ours to move. Each is owned by its respective tool.

## Consequences

- **Breaking change for swain itself.** Every script that references `$REPO_ROOT/.agents/...` must move to `.swain/...`. Every skill, every doc, every symlink target. A migration script, swain-doctor detection, docs update, and major version bump are all required. This matches the standing rule that migration paths are mandatory for swain-internal schema changes.
- **SPEC-305 scope shrinks.** The consumer gitignore writer adds `.swain/` and `.swain-init`. Peer-agent dirs come off the list. The "runtime dir list" data file drives worktree symlinking only, not gitignore content.
- **The worktree bootstrap hook reads from two sources.** One is the swain-owned `.swain/` subset — always symlinked. The other is the peer-agent dir list — symlinked if present in the common root, regardless of ignore status.
- **Path for future alignment.** Swain can later adopt the agentsfolder spec for its own canonical config by populating `.agents/manifest.yaml` and friends. That work is out of scope here but this ADR does not foreclose it.
- **Consumer projects end up with smaller managed gitignore blocks.** Less surface area. Lower risk of stepping on operator intent.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-04-13 | — | Initial creation |
