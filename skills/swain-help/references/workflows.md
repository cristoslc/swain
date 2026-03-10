# Common Workflows

## New feature (end-to-end)

1. **Define scope**: `/swain create an epic for user authentication`
   - Swain-design creates EPIC-NNN with scope, success criteria, and acceptance tests

2. **Decompose**: `/swain create a spec for JWT token handling` (reference the epic)
   - Creates SPEC-NNN linked to the epic

3. **Plan implementation**: When the spec reaches Approved, swain-design triggers swain-do to create a tracked plan with tasks

4. **Work the plan**: `/swain what should I work on?`
   - Swain-do shows the next ready task (blocker-aware)
   - Claim it, do the work, mark complete

5. **Commit**: `/swain push`

6. **Release**: `/swain release` when the epic is complete

## Bug fix

1. **File the bug**: `/swain file a bug: login fails when password contains special characters`
   - Creates BUG-NNN with reproduction steps and affected artifacts

2. **Plan the fix**: Swain creates tracked tasks before code changes begin

3. **Fix and verify**: Work the tasks, mark resolved, verify

4. **Commit**: `/swain push`

## Research spike

1. **Create the spike**: `/swain create a spike to evaluate WebSocket vs SSE for real-time updates`
   - Time-boxed investigation with clear questions to answer

2. **Do the research**: Spike moves to Active

3. **Record findings**: Complete the spike with conclusions
   - May produce an ADR if an architectural decision was made

## Starting a new session

1. **Health check**: `/swain-doctor` runs automatically (or invoke manually)

2. **See what's in progress**: `/swain show my tasks` or `bd status`

3. **Pick up work**: `/swain what should I work on?`

## Adopting swain in an existing project

1. **Run init**: `/swain init`
   - Migrates CLAUDE.md, installs bd, adds governance rules

2. **Orientation**: Swain-help walks you through what's available

3. **Start creating artifacts**: `/swain create a vision for this project`

## Artifact lifecycle walkthrough

A typical implementation-tier artifact goes through:

1. **Create** — artifact lands in its first-phase directory (e.g., `docs/spec/draft/`)
2. **Review** — transition to the review phase when ready for feedback
3. **Approve** — transition to approved after review passes
4. **Plan** — swain-do creates tracked tasks for implementation
5. **Implement** — work the tasks, committing along the way
6. **Complete** — artifact moves to its final phase directory
7. **Validate** — specwatch checks for stale refs; adr-check validates compliance
