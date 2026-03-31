# Phase Transitions

## Phase skipping

Phases listed in the artifact definition files are available waypoints, not mandatory gates. An artifact may skip intermediate phases and land directly on a later phase in the sequence. This is normal in single-user workflows where drafting and review happen conversationally in the same session.

- The lifecycle table records only the phases the artifact actually occupied — one row per state it landed on, not rows for states it skipped past.
- Skipping is forward-only: an artifact cannot skip backward in its phase sequence.
- **Abandoned** is a universal end-of-life phase available from any state, including Proposed. It signals the artifact was intentionally not pursued. Use it instead of deleting artifacts — the record of what was considered and why it was dropped is valuable.
- Other end-of-life transitions (Retired, Superseded) require the artifact to have been in an active state first — you cannot skip directly from Proposed to Retired.

## Workflow

1. Validate the target phase is reachable from the current phase (same or later in the sequence; intermediate phases may be skipped).
2. **Move the artifact** to the new phase subdirectory using `git mv` (e.g., `git mv docs/epic/Proposed/(EPIC-001)-Foo/ docs/epic/Active/(EPIC-001)-Foo/`). Every artifact type uses phase subdirectories — see the artifact's definition file for the exact directory names. Phase subdirectories use PascalCase: `Proposed/`, `Ready/`, `InProgress/`, `NeedsManualTest/`, `Complete/`, `Active/`, `Retired/`, `Superseded/`, `Abandoned/`.
2a. **Relink inbound hyperlinks** — after moving the artifact directory, inbound markdown links from other artifacts pointing to the old path are now broken. Run:
    ```bash
    bash "$(find "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" -path '*/swain-design/scripts/relink.sh' -print -quit 2>/dev/null)" 2>/dev/null
    ```
    This updates all broken `[ID](old-path)` links across docs/ to point at the artifact's new location. Stage the relinked files alongside the `git mv` in the same commit. If `relink.sh` is not found, skip silently.
3. Update the artifact's status field in frontmatter to match the new phase.
4. **ADR compliance check** — for transitions to active phases (Active, Ready, In Progress, Complete), run `scripts/adr-check.sh <artifact-path>`. Review any findings with the user before committing.
4c. **Alignment check** — for transitions to active phases (Active, Ready), run `bash scripts/chart.sh scope <artifact-id>` and assess per [alignment-checking.md](alignment-checking.md). Skip for implementation-phase transitions (In Progress, Needs Manual Test, Complete) unless content changed since last check. Skip for terminal-phase transitions (Abandoned, Retired, Superseded).
4d. **Spike final pass (SPIKE only)** — for `Active → Complete` transitions, populate the `## Summary` section at the top of the spike document. Lead with the verdict (Go / No-Go / Hybrid / Conditional), then 1–3 sentences distilling the key finding and recommended next step. This reorders emphasis without changing content — Findings stay in place, but the reader reaches the decision immediately. See [spike-definition.md](spike-definition.md) for rationale.
4e. **Spike back-propagation (SPIKE only)** — for `Active → Complete` transitions, scan for artifacts whose assumptions may be invalidated by the spike's findings. This is a semantic check, not just a structural xref:
   1. Read the spike's verdict and key findings from `## Summary`.
   2. Query `chart.sh scope <SPIKE-ID>` to identify sibling artifacts in the same parent-vision/parent-initiative scope.
   2b. Additionally scan `docs/train/` for TRAINs whose `linked-artifacts` contain any artifact in the same parent-vision or parent-initiative scope with `rel: [documents]`.
   3. For each sibling (SPEC, EPIC, or TRAIN) that is Complete or Active, check whether any acceptance criteria, documented behavior, or training content contradict the spike's findings.
   4. Surface contradictions as `IMPLICIT_CONFLICT` findings (see [alignment-checking.md](alignment-checking.md)). Present them to the operator before proceeding.
   5. If contradictions exist, recommend updating the affected artifacts' acceptance criteria and any downstream code/runbooks that implemented the invalidated assumptions.
   This step is **advisory** — it does not block the spike completion — but findings must be presented, not silently skipped.
4a. **Verification gate (SPEC only)** — for `Needs Manual Test → Complete` transitions, run `scripts/spec-verify.sh <artifact-path>`. Address gaps before proceeding.
4b. **Code review gate (SPEC only)** — for `Needs Manual Test → Complete`, if superpowers code review skills are installed, request spec compliance + code quality reviews (see [superpowers-integration.md](superpowers-integration.md)). Not a hard gate.
5. Commit the transition change (move + status update).
5a. **specwatch-ignore maintenance (→ Superseded only)** — when the target phase is `Superseded`, append glob patterns to `.agents/specwatch-ignore` so that intentional backward references don't pollute specwatch output. Create the file if it doesn't exist. Deduplicate before appending.
   ```
   # <OLD-ID> superseded by <NEW-ID> (<YYYY-MM-DD>)
   docs/<type>/Superseded/(<OLD-ID>)*
   docs/<type>/<new-phase>/(<NEW-ID>)*
   ```
   Include patterns for: (a) the superseded artifact itself (its frozen outbound refs), (b) the superseding artifact (its intentional backward ref). If an ADR was created as part of the same operation, include its path too.
5b. **Back-reference update (→ Superseded only)** — after suppressing the superseded artifact's own refs (5a), find all *other* non-terminal artifacts that still reference the superseded artifact in frontmatter fields (`linked-artifacts`, `depends-on-artifacts`, `addresses`). Run:
   ```bash
   grep -rl '<OLD-ID>' docs/ | grep -v Superseded/ | grep -v Abandoned/
   ```
   For each non-terminal result:
   1. **Alignment check**: Read the referencing artifact's context (problem statement, scope, goals) and compare it against the successor `<NEW-ID>`. Supersession often changes scope — the successor may have different goals, constraints, or boundaries than the original. If the referencing artifact's relationship was specific to the *old* artifact's scope and doesn't hold for the successor, flag it for the operator rather than silently updating.
   2. **If aligned**: replace `<OLD-ID>` with `<NEW-ID>` in frontmatter fields. If `<NEW-ID>` is already present (dedup), remove the old entry instead. Record what changed in the commit message (e.g., "update EPIC-031 linked-artifacts: INITIATIVE-001 → INITIATIVE-013").
   3. **If misaligned or uncertain**: present the finding to the operator — "SPEC-NNN references `<OLD-ID>` which was superseded by `<NEW-ID>`, but the successor's scope diverges. Should this reference update, be removed, or remain (with specwatch-ignore suppression)?"
   4. **Provenance links**: if the referencing artifact is the superseding artifact itself (intentional provenance), add it to specwatch-ignore (step 5a) instead of rewriting.
   5. **Frozen sources**: references from Complete or Superseded source artifacts are handled by specwatch-ignore in step 5a — this step only updates Active, Proposed, or InProgress artifacts.
6. Stamp the lifecycle table with the transition commit hash. Choose the pattern based on artifact complexity tier (see SPEC-045):
   - **Fast-path tier with no downstream dependents:** Use the inline stamp — run `git rev-parse HEAD` *before* the transition commit, pre-fill the lifecycle row hash, and include it in the single transition commit (step 5). No second commit needed.
   - **Full-ceremony tier, EPICs, or artifacts with downstream dependents:** Append a row with `--` as a placeholder hash in step 5, then commit the hash stamp as a **separate commit** (step 7). Never amend — two distinct commits keeps the stamped hash reachable in git history.
7. *(Full-ceremony only)* Commit the hash stamp as a separate commit — append the commit hash from step 5 into the lifecycle table row and commit. Skip this step for inline-stamped artifacts.
8. **Post-operation scan** — run `scripts/specwatch.sh scan`. Fix any stale references.
9. **Index refresh step** — move the artifact's row to the new phase table (see [index-maintenance.md](index-maintenance.md)).

## Completion rules

- An Initiative is "Complete" only when all child Epics are "Complete" and its stated objectives are met.
- An Epic is "Complete" only when all child Agent Specs are "Complete" and success criteria are met.
- An Agent Spec is "Complete" only when its implementation plan is closed (or all tasks are done in fallback mode) **and** its Verification table confirms all acceptance criteria pass (enforced by `spec-verify.sh`).
- An ADR is "Superseded" only when the superseding ADR is "Active" and links back.

## Child artifact propagation

When a parent artifact (e.g., INITIATIVE, EPIC, VISION) transitions to a new phase, child artifacts that were already attached at the time of the transition should be promoted to the equivalent phase automatically:

1. After completing the parent's own phase transition (steps 1–9 above), identify all child artifacts currently linked to the parent (via `parent-initiative`, `parent-epic`, `parent-vision`, `linked-specs`, `linked-research`, etc.).
2. For each child that is in the same phase as the parent *was* (or in `Proposed` if the parent was being activated), transition it to match the parent's new phase using the same workflow.
3. Children created **after** a parent transition are not affected retroactively — they follow the normal creation rules (user-requested → Active; agent-suggested → Proposed).
4. If a child has already advanced past the equivalent phase, leave it in its current phase — only pull lagging children forward, never push advanced ones backward.

**Example:** User promotes EPIC-005 from `Proposed` → `Active`. SPEC-012 and SPIKE-014, both currently in `Proposed`, are automatically promoted to `Active`. SPEC-013, already in `InProgress`, is left alone.

## INITIATIVE phase transitions

INITIATIVE follows the **container track** (same as EPIC): `Proposed → Active → Complete`, with `Abandoned` and `Superseded` available from any phase.

| From | To | Gate |
|------|----|------|
| Proposed | Active | Objectives and scope defined; at least one child Epic linked |
| Active | Complete | All child Epics are Complete and stated objectives are met |
| Any | Abandoned | Intentionally dropped — record rationale in the lifecycle table Notes column |
| Active | Superseded | A replacement Initiative exists and links back via `superseded-by` |

Use two-commit stamp for all INITIATIVE transitions (same rule as EPIC).

## EPIC terminal transition hook

When an EPIC transitions to any terminal state (`Complete`, `Abandoned`, `Superseded`), invoke **swain-retro** with the EPIC ID and terminal state. swain-retro embeds a `## Retrospective` section directly in the EPIC artifact.

**Orchestration:**

1. Complete the phase transition (steps 1–9 above)
2. Invoke swain-retro: pass EPIC ID, terminal state, and whether the session is interactive
3. swain-retro gathers context, generates or prompts reflection, extracts memories, and returns the retro content
4. The `## Retrospective` section is appended to the EPIC (before `## Lifecycle`)
5. Commit the retro content (may be part of the transition commit or a follow-up)

**Interactive detection:** If the user is present and responding in the current session, swain-retro offers interactive reflection questions. If non-interactive (dispatched agent, batch processing), it generates the retro automatically from gathered context.

This is best-effort — if swain-retro is not available, the EPIC transition still succeeds without a retro section.

### TRAIN documentation hooks

**On SPEC completion** (`In Progress → Needs Manual Test` or `Needs Manual Test → Complete`):
1. Scan `docs/train/` for TRAINs whose enriched `linked-artifacts` contain this SPEC with `rel: [documents]`.
2. If found: surface advisory — "SPEC-NNN completed. TRAIN-NNN documents this spec — review for updates." Strong preference for updating existing TRAINs over creating new ones.
3. If not found: no action (documentation is optional per-SPEC).

**On EPIC completion** (`Active → Complete`):
1. Collect all SPECs under this EPIC.
2. Scan `docs/train/` for TRAINs documenting any of those SPECs.
3. If TRAINs found: surface advisory — "EPIC-NNN completed. TRAIN-NNN documents features from this epic — review for updates."
4. If no TRAINs found: surface suggestion — "EPIC-NNN completed with no linked TRAIN artifacts. Consider documenting: [epic title]."
5. The agent/subagent/MCP tool drafts the TRAIN; the operator reviews.
