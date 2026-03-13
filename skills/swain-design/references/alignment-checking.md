# Alignment Checking

Agent instructions for semantic alignment assessment of artifacts in the swain hierarchy.

## What alignment means

Alignment means **oriented toward the same goal** — usually the Vision at the top of the hierarchy. It does not mean content must match or detail levels must agree.

- **Goal coherence**: Each artifact's purpose should serve its parent's purpose, which in turn serves the Vision's value proposition.
- **Non-contradiction**: Artifacts should not actively work against each other's goals or constraints.
- **Scope consistency**: An artifact should not address problems or audiences outside its parent's defined boundaries.

Things that merely do not contradict each other but are otherwise semantically distant can still align with the same goal. Alignment is about shared direction, not proximity.

## Procedure

1. Run `specgraph.sh scope <ID>` to identify the alignment scope — the parent chain, siblings, and lateral links.
2. Read the Vision at the top of the chain. This is the "North Star" — the goal everything should orient toward.
3. Read the changed/created artifact.
4. Assess each relationship level per the checks below.

## What to check per relationship level

### Vision - Epic

- Does the Epic's goal serve the Vision's value proposition?
- Is the Epic's scope within the Vision's stated boundaries (non-goals)?
- Does the Epic target an audience consistent with the Vision's audience?

### Epic - SPEC

- Does the SPEC's problem statement address something within the Epic's scope?
- Do the acceptance criteria contribute to the Epic's success criteria?
- Is the SPEC's `type` (feature/enhancement/bug) consistent with the Epic's current phase?

### Vision - Journey

- Does the Journey's user goal connect to the Vision's audience and value proposition?
- Are the Journey's pain points problems the Vision aims to solve?

### Journey pain point - addressing artifacts

- Does the addressing artifact (SPEC/EPIC) actually resolve the described friction?
- Is the pain point's severity consistent with the addressing artifact's priority?

### ADR - SPEC/Epic

- Is the approach consistent with the ADR's decision? Does the artifact avoid rejected alternatives?
- If the ADR constrains technology choices, does the artifact respect those constraints?

### Persona - Journey/Story

- Does the Journey/Story's user match the Persona's profile?
- Are the needs and behaviors described in the Persona reflected in the Journey/Story?

### Architecture overview - ADRs

- Do Active ADRs match what the architecture overview describes?
- Has the overview been updated to reflect recent ADR decisions?

### Sibling SPECs under same Epic

- Do they contradict each other or create redundancy?
- Do overlapping acceptance criteria agree on expected behavior?
- Are there gaps between siblings that the Epic expects to be covered?

## Finding types and severity

### MISALIGNED (blocking)

Active contradiction between artifacts. The artifact's stated goal or approach directly conflicts with its parent's goal, an Active ADR's decision, or a sibling's acceptance criteria.

**Examples:**
- A SPEC implementing an approach that an Active ADR explicitly rejected
- An Epic whose goal undermines its parent Vision's value proposition
- Sibling SPECs with contradictory acceptance criteria

### SCOPE_LEAK (advisory)

The artifact works outside its parent's boundaries. The content addresses problems or audiences not within scope.

**Examples:**
- A SPEC under an Epic about "authentication" that adds unrelated logging features
- A Story targeting a persona not defined in the parent Vision

### GOAL_DRIFT (advisory)

The artifact's purpose has diverged from the Vision's intent. Typically happens when an artifact was aligned at creation but has been updated independently.

**Examples:**
- A SPEC whose problem statement evolved to address a different concern than what the Epic describes
- An Epic whose success criteria no longer connect to the Vision's value proposition

### STALE_ALIGNMENT (advisory)

The artifact was aligned when created, but its parent changed since. The alignment has not been re-verified.

**Examples:**
- A SPEC created under an Epic that subsequently changed scope
- An artifact linked to an ADR that was superseded

### IMPLICIT_CONFLICT (advisory)

No explicit link exists between the artifacts, but their content contradicts. Found during broader scope analysis.

**Examples:**
- Two SPECs under different Epics that make incompatible assumptions about the same system component
- A Runbook that describes a procedure inconsistent with an ADR's decision

## Noise reduction

Do **not** flag:

- **Detail-level differences** — A Vision is naturally more abstract than its child SPECs. Different granularity is expected, not a finding.
- **Terminological variation** — An Epic calling something a "module" while a SPEC calls it a "service" is not a conflict unless the concepts genuinely differ.
- **Terminal-phase artifacts** — Completed, Abandoned, or Superseded artifacts are historical record. Only flag if an active artifact references them as current guidance.
- **Informational cross-refs that are merely distant** — An ADR referencing a SPEC in a different Epic for background context is not misalignment.
- **Missing optional links** — Not every artifact needs every possible cross-reference. Only flag missing links when the content demonstrates an undeclared dependency.

**Rule of thumb:** If the finding wouldn't change what the developer decides, don't report it.
