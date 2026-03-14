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
3. Update the artifact's status field in frontmatter to match the new phase.
4. **ADR compliance check** — for transitions to active phases (Active, Ready, In Progress, Complete), run `skills/swain-design/scripts/adr-check.sh <artifact-path>`. Review any findings with the user before committing.
4c. **Alignment check** — for transitions to active phases (Active, Ready), run `skills/swain-design/scripts/specgraph.sh scope <artifact-id>` and assess per [alignment-checking.md](alignment-checking.md). Skip for implementation-phase transitions (In Progress, Needs Manual Test, Complete) unless content changed since last check. Skip for terminal-phase transitions (Abandoned, Retired, Superseded).
4d. **Spike final pass (SPIKE only)** — for `Active → Complete` transitions, populate the `## Summary` section at the top of the spike document. Lead with the verdict (Go / No-Go / Hybrid / Conditional), then 1–3 sentences distilling the key finding and recommended next step. This reorders emphasis without changing content — Findings stay in place, but the reader reaches the decision immediately. See [spike-definition.md](spike-definition.md) for rationale.
4a. **Verification gate (SPEC only)** — for `Needs Manual Test → Complete` transitions, run `skills/swain-design/scripts/spec-verify.sh <artifact-path>`. Address gaps before proceeding.
4b. **Code review gate (SPEC only)** — for `Needs Manual Test → Complete`, if superpowers code review skills are installed, request spec compliance + code quality reviews (see [superpowers-integration.md](superpowers-integration.md)). Not a hard gate.
5. Commit the transition change (move + status update).
6. Stamp the lifecycle table with the transition commit hash. Choose the pattern based on artifact complexity tier (see SPEC-045):
   - **Fast-path tier with no downstream dependents:** Use the inline stamp — run `git rev-parse HEAD` *before* the transition commit, pre-fill the lifecycle row hash, and include it in the single transition commit (step 5). No second commit needed.
   - **Full-ceremony tier, EPICs, or artifacts with downstream dependents:** Append a row with `--` as a placeholder hash in step 5, then commit the hash stamp as a **separate commit** (step 7). Never amend — two distinct commits keeps the stamped hash reachable in git history.
7. *(Full-ceremony only)* Commit the hash stamp as a separate commit — append the commit hash from step 5 into the lifecycle table row and commit. Skip this step for inline-stamped artifacts.
8. **Post-operation scan** — run `skills/swain-design/scripts/specwatch.sh scan`. Fix any stale references.
9. **Index refresh step** — move the artifact's row to the new phase table (see [index-maintenance.md](index-maintenance.md)).

## Completion rules

- An Epic is "Complete" only when all child Agent Specs are "Complete" and success criteria are met.
- An Agent Spec is "Complete" only when its implementation plan is closed (or all tasks are done in fallback mode) **and** its Verification table confirms all acceptance criteria pass (enforced by `spec-verify.sh`).
- An ADR is "Superseded" only when the superseding ADR is "Active" and links back.

## EPIC completion hook

When an EPIC transitions to Complete, invoke the **swain-retro** skill with the EPIC ID to capture retrospective learnings. This is best-effort — if swain-retro is not available or the user declines, the transition still succeeds.
