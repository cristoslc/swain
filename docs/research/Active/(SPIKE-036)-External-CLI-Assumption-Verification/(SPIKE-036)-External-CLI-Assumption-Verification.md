---
title: "External CLI Assumption Verification"
artifact: SPIKE-036
track: container
status: Active
author: cristos
created: 2026-03-19
last-updated: 2026-03-19
parent-initiative: INITIATIVE-016
parent-vision: VISION-001
question: "What verification mechanisms can an agent use to validate assumptions about external CLI behavior before embedding commands in scripts?"
gate: Pre-MVP
risks-addressed:
  - Agent writes Docker/git/runtime commands based on documentation assumptions that don't match actual CLI behavior
  - Syntax-valid scripts fail on first real use because external commands behave differently than expected
evidence-pool: ""
linked-artifacts:
  - SPEC-092
  - SPEC-126
  - VISION-002
depends-on-artifacts: []
---

# External CLI Assumption Verification

## Summary

## Question

What verification mechanisms can an agent use to validate assumptions about external CLI behavior before embedding commands in scripts?

## Go / No-Go Criteria

- **Go:** A practical verification step exists that agents can invoke during implementation — either a probe pattern, a dry-run mechanism, or a structured discovery phase — that catches incorrect CLI assumptions before they reach the script.
- **No-Go:** No general mechanism exists; each external tool requires bespoke verification logic, making the approach unmaintainable.
- **Threshold:** The mechanism must have caught at least 2 of the 3 bugs from the 2026-03-19 VISION-002 session (hanging probe, missing -it, wrong CMD).

## Pivot Recommendation

If no general mechanism works: fall back to a per-tool verification checklist embedded in swain-do's implementation plan template. Less elegant, but at least it forces the agent to think about each external command.

## Findings

### Evidence from the 2026-03-19 session

Three bugs, three patterns:

| Bug | Root cause | What would have caught it |
|-----|-----------|--------------------------|
| `docker sandbox run <name> --version` hangs | Assumed `run` with `--version` acts as a probe; it actually boots a full VM | Running the command once before writing it into a loop |
| `docker sandbox exec <name> /bin/bash` exits immediately | Assumed exec allocates TTY by default; it doesn't without `-it` | Checking `docker sandbox exec --help` for required flags |
| `docker run ... --dangerously-skip-permissions` as CMD | Assumed args append to image CMD; without explicit command, they replace it | Reading `docker image inspect` for entrypoint/cmd before constructing the run command |

### Candidate verification approaches

TBD — research needed:
1. **Command probing** — run the command in a throwaway context before writing it into the script
2. **Help parsing** — read `--help` output for required flags and argument positions
3. **Image/sandbox inspection** — `docker image inspect`, `docker sandbox ls` before constructing commands
4. **Dry-run flags** — check if the external tool supports `--dry-run` or equivalent
5. **Pre-implementation discovery phase** — structured step in swain-do that says "before writing any external command, verify its behavior"

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Active | 2026-03-19 | — | Created from retro on CLI assumption bugs |
