# Common Workflows

## New feature (end-to-end)

1. **Define scope**: `/swain create an epic for user authentication`
   - Swain-design creates EPIC-NNN with scope, success criteria, and acceptance tests

2. **Decompose**: `/swain create a spec for JWT token handling` (reference the epic)
   - Creates SPEC-NNN linked to the epic

3. **Plan implementation**: When the spec reaches Ready, swain-design triggers swain-do to create a tracked plan with tasks

4. **Work the plan**: `/swain what should I work on?`
   - Swain-do shows the next ready task (blocker-aware)
   - Claim it, do the work, mark complete

5. **Commit**: `/swain sync`

6. **Release**: `/swain release` when the epic is complete

## Bug fix

1. **File the bug**: `/swain file a bug: login fails when password contains special characters`
   - Creates a SPEC with `type: bug`, including reproduction steps, severity, and expected vs. actual behavior

2. **Plan the fix**: Swain creates tracked tasks before code changes begin

3. **Fix and verify**: Work the tasks, mark resolved, verify

4. **Commit**: `/swain sync`

## Research spike

1. **Create the spike**: `/swain create a spike to evaluate WebSocket vs SSE for real-time updates`
   - Time-boxed investigation with clear questions to answer

2. **Do the research**: Spike moves to Active

3. **Record findings**: Complete the spike with conclusions
   - May produce an ADR if an architectural decision was made

## Checking project status

1. **Get the dashboard**: `/swain-session` or just ask "what's next?" / "where are we?"
   - Shows active epics with progress ratios (e.g., 3/5 specs complete)
   - Surfaces blocked items, in-progress tasks, and GitHub issues
   - Provides a ranked recommendation for what to work on next

2. **Drill into specifics**: Follow up on anything in the dashboard
   - "Tell me more about EPIC-003"
   - "What's blocking SPEC-012?"

3. **Act on the recommendation**: The dashboard points you to the highest-leverage next step

## Starting a new session

1. **Health check**: `/swain-doctor` runs automatically (or invoke manually)

2. **Context restore**: `/swain-session` runs automatically — restores your last context bookmark

3. **See what's in progress**: `/swain-session` or `tk ready`

4. **Pick up work**: Follow the dashboard's recommendation or ask `/swain what should I work on?`

## Adopting swain in an existing project

1. **Run init**: `/swain init`
   - Migrates CLAUDE.md, verifies tk, adds governance rules

2. **Orientation**: Swain-help walks you through what's available

3. **Start creating artifacts**: `/swain create a vision for this project`

## Artifact lifecycle walkthrough

A typical implementation-tier artifact (Spec) goes through:

1. **Proposed** — artifact lands in `docs/spec/Proposed/`
2. **Ready** — transition when scope, acceptance criteria, and dependencies are confirmed
3. **In Progress** — swain-do creates tracked tasks; implementation begins
4. **Needs Manual Test** — all tasks complete; populate the Verification table with evidence
5. **Complete** — artifact moves to `docs/spec/Complete/` after all criteria pass
6. **Validate** — specwatch checks for stale refs; adr-check validates compliance
