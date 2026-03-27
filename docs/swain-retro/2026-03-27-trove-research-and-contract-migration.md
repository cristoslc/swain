---
title: "Retro: Trove research and evidence-pool contract migration"
artifact: RETRO-2026-03-27-trove-research-and-contract-migration
track: standing
status: Active
created: 2026-03-27
last-updated: 2026-03-27
scope: "Session work: two new troves, PERSONA-001 trove link, frontmatter contract rename, 160-file migration"
period: "2026-03-27"
linked-artifacts:
  - PERSONA-001
  - DESIGN-006
---

# Retro: Trove research and evidence-pool contract migration

## Summary

Session started with collecting two external sources into separate troves (Karpathy's vibe-coding blog post and Collison's Stripe Projects announcement). Linking one trove to [PERSONA-001](../persona/Active/(PERSONA-001)-Swain-Project-Developer/(PERSONA-001)-Swain-Project-Developer.md) exposed that the `evidence-pool` → `trove` rename from the trove redesign spec was incomplete in the frontmatter contract. This cascaded into fixing the contract, adding `trove` as an optional field for PERSONA artifacts, migrating 160 artifact files, and repinning [DESIGN-006](../design/Active/(DESIGN-006)-Artifact-Frontmatter-Schema/(DESIGN-006)-Artifact-Frontmatter-Schema.md)'s stale sourcecode-ref.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| `vibe-coding-practitioner-experience` (trove) | Karpathy MenuGen vibe coding experience | Created |
| `agent-service-provisioning` (trove) | Collison Stripe Projects announcement | Created |
| PERSONA-001 | Swain Project Developer | Updated with trove reference |
| DESIGN-006 | Artifact Frontmatter Schema | Prose + sourcecode-ref repinned |
| `frontmatter-contract.yaml` | Data contract | Field renamed, PERSONA column added |
| 160 artifact files | Frontmatter migration | `evidence-pool:` → `trove:` |

## Reflection

### What went well

- **Trove routing decision was correct on the first pass.** User suggested separate troves, agent agreed based on content analysis (practitioner vs. platform layer). No misrouting — contrast with the 2026-03-25 trove misrouting retro where the agent dismissed a matching trove. The Phase 2 semantic topic matching added after that retro is working.
- **X.com fallback was smooth.** When direct tweet fetching failed (JS-required), user provided an alternative URL (twitter-thread.com) that worked immediately. No time wasted retrying.
- **Parallel agent dispatch.** Both troves were created simultaneously via parallel agents, cutting wall-clock time roughly in half.

### What was surprising

- **The `evidence-pool` → `trove` rename was never completed.** The trove redesign spec and migration plan existed since 2026-03-15, and the directory/file renames happened, but the frontmatter contract and 160 artifact files were never updated. The gap was only discovered because the operator asked "doesn't that violate an ADR?" when the agent tried to use the old field name.
- **The contract had no `trove` field for PERSONA at all.** Standing-track artifacts (PERSONA, JOURNEY, RUNBOOK) were excluded from the evidence-pool field originally. Personas benefit from external research backing — the field should have been optional for them from the start.

### What would change

- **Migration completeness checks.** When a rename spec exists with a migration plan, there should be a verification step that confirms all instances were actually migrated. The trove redesign plan listed "92 artifact files" to migrate — we found 160. The plan was stale before it was ever fully executed.

### Patterns observed

- **Small research tasks surface contract debt.** This is a recurring pattern: what starts as "add two sources" reveals a schema inconsistency that cascades into a broader fix. The incremental cost was low (sed across 160 files), but the debt could have compounded if left unfixed.
- **Operator catches contract violations that agents miss.** The agent was about to use `evidence-pool` without questioning it. The operator's "doesn't that violate an ADR?" was the forcing function. This echoes the trove misrouting retro — agents follow the path of least resistance unless the operator intervenes on schema/contract questions.

## Learnings captured

| Memory file | Type | Summary |
|------------|------|---------|
| `feedback_retro_live_verify.md` | feedback | (Existing) Reinforced: file existence alone produces false positives — run ACs live |
| *(no new memories created — learnings are contract/artifact fixes, not behavioral)* | | |
