# README as Ambient Intent

## Problem

Projects that use swain have a rich artifact tree — Visions, Designs, Journeys, Specs — but the README is invisible to the alignment loop. The README is the most public statement of what a project claims to do, yet swain never checks whether reality matches those claims. In early project phases, the README may be the *only* intent document, and swain ignores it entirely.

This creates two failure modes:

1. **Early phase blindness.** A new project has a README and code but no artifacts. Swain has nothing to work with. The README — which already describes what the project does — goes unused as an intent source.
2. **Drift without detection.** A mature project's README promises features that were dropped, describes behavior that changed, or omits capabilities that were added. No checkpoint catches this. The README rots silently.

## Design

README.md is a first-class input to swain's alignment loop. It is not a lifecycle artifact — no frontmatter, no phases, no specgraph entry. It is ambient: always present, always checked, never managed.

### Creation

`swain-init` checks for README.md. If absent, swain seeds one based on available context:

- **No code, no artifacts** — Interview the operator ("what does this project do?"), write the README from the answer.
- **Code exists, no artifacts** — Infer from code. Present a draft to the operator for editing.
- **Artifacts exist, no README** — Compile from Visions, Designs, Journeys, and Personas.

The README is never empty after init. `swain-doctor` flags a missing README on every session.

### Artifact seeding

When a README exists but the artifact tree is empty or thin, swain extracts intent from the README and proposes seed artifacts:

- **Vision** — from the README's description of what the project does and why.
- **Personas** — from who the README addresses and what problems it describes.
- **Journeys** — from usage flows, examples, or "getting started" paths in the README.
- **Designs** — from architectural or structural claims.

These are proposals, not automatic creations. The operator approves, edits, or rejects each one.

### Reconciliation checkpoints

Three checkpoints, all "firm elbow" — swain pushes hard but the operator can override.

**1. Session start (focus lane selection)**

When swain-session picks a focus lane, it reads the README and compares against current Vision, Design, and Journey state. If drift is detected, swain surfaces specific mismatches:

> "README says 'real-time sync' but VISION-003 dropped that in favor of batch processing. Which is right?"

The operator resolves before proceeding, or explicitly defers. Deferral is allowed but swain remembers and raises it again next session.

**2. Retro**

swain-retro includes README reconciliation as part of the retrospective flow. After reflecting on what happened in the epic, swain checks whether the README still describes the project accurately. This catches gradual drift — the kind where no single change was wrong but the cumulative effect moved the project away from what the README promises.

**3. Release**

Hard gate with two checks:

- **Alignment** — README claims vs. artifact tree. Unresolved drift blocks the release.
- **Verification** — README claims that imply testable behavior must be covered by the test suite. Untested promises block the release.

For each untested promise, the operator gets a choice: add a test, remove the promise from the README, or explicitly override (accept the gap). The operator can override the full release gate, but swain requires an explicit statement — no silent bypass.

### Reconciliation direction

Reconciliation is bidirectional. Drift does not assume the artifacts are right:

- A new Vision may mean the README is stale and needs updating.
- The README may be right and the Vision needs reshaping.
- A promise may have been intentionally dropped and needs removing from both.

Swain surfaces the divergence. The operator decides which side to update.

### Semantic extraction

Swain reads the entire README as prose and extracts claims regardless of structure. No convention-based sections, no operator-placed markers. Any claim in the README is a promise. Install instructions, feature descriptions, behavioral claims, architectural statements — all fair game.

### Test seeding from README

Swain identifies README claims that imply testable behavior:

- **Install/setup claims** — "run `npm install && npm start`" implies a smoke test that the install path works.
- **CLI behavior** — "`foo init` creates a project" implies an integration test that runs the command and checks output.
- **API surface** — "exports a `createWidget` function" implies a test that the export exists and returns the expected type.
- **Behavioral promises** — "automatically retries on failure" implies a test that retry behavior works.
- **Integration claims** — "works with PostgreSQL 15+" implies an integration test against that version.

Swain does not auto-generate tests. At release time, it extracts implied promises and checks whether the test suite covers them. Outside of release, swain surfaces untested promises during session start or retro as a softer nudge.

## Integration points

No new skills. No new artifact types. No new file formats. Behavior woven into existing skills:

| Skill | Change |
|-------|--------|
| **swain-init** | Seed README if missing. Offer artifact generation from README when artifact tree is empty. |
| **swain-doctor** | Check README exists. Flag if missing. No content reconciliation (that's the checkpoints). |
| **swain-session** | At focus lane selection, run README reconciliation. Firm elbow with deferral tracking. |
| **swain-retro** | Add README drift check to retrospective flow. |
| **swain-release** | Two-part gate: alignment check + verification check. Both must pass or be explicitly overridden. |
| **swain-design** | When transitioning Visions, Designs, Journeys, or Personas, flag that README may need updating. Soft signal, not a blocker. |
| **brainstorming** | When brainstorming for a project with a README but no artifacts, README is the starting context. |

## What this is not

- **Not a new artifact type.** README has no frontmatter, no lifecycle phases, no specgraph entry.
- **Not auto-updating.** Swain never silently rewrites the README. All changes go through the operator.
- **Not a test generator.** Swain identifies untested promises. The operator writes the tests or removes the promises.
- **Not a template.** Swain does not impose README structure. The operator writes in whatever format they want.
