---
source-id: "crispy-agents-build-workflow"
title: "CRISPY Build Workflow — Orchestrating all CRISPY phases"
type: repository
url: "https://github.com/tfolkman/crispy-agents/blob/master/commands/build-workflow.md"
fetched: 2026-04-13T17:00:00Z
---

# Build Workflow (CRISPY Framework)

Based on Dex's CRISPY framework (RPI v2): **C**ontext → **R**esearch → **I**nvestigate → **S**tructure → **P**lan → **Y**ield → **P**R

## Model Diversity Strategy

**Coder ≠ Reviewer** — Different models catch different issues (like pair programming with different perspectives).

| Phase | Model | Why |
|-------|-------|-----|
| Architect/Structure/Plan | GLM 5.1 | Design docs, SWE-bench Pro #1 |
| Research/Investigate | Qwen 3.6 Plus | MCP-Atlas #1, pure facts |
| Coder | GLM 5.1 | SWE-bench Pro #1, sustained execution |
| **Reviewer** | **Qwen 3.6 Plus** | **Different from coder** — catches GLM blind spots |
| Verifier | GLM 4.7 | Execution, not reasoning |

**Monthly cost**: ~$35-45 depending on usage

## Instruction Budget
- **Frontier LLMs max**: ~150-200 instructions per context window
- **Per phase limit**: <40 instructions each
- **Fix**: Split into focused phases with actual control flow (not prompts)
- **Result**: Better outcomes than 1000-line monolithic plans

## CRISPY Phases

```
START
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. CONTEXT (40 instructions max)                           │
│    Load relevant codebase context                          │
│    Agent: @architect                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. RESEARCH (40 instructions max)                            │
│    Pure facts, NO implementation intent                      │
│    Fresh context window, no opinions                         │
│    Agent: @scout (pure research mode)                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. INVESTIGATE (40 instructions max)                        │
│    Dig deeper on specific areas                              │
│    Decomposed questions only                                  │
│    Agent: @scout + @architect                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. STRUCTURE (40 instructions max)                          │
│    High-level outline with testing CHECKPOINTS               │
│    Like C headers—signatures, not implementation           │
│    Output: structure.md                                     │
│    Agent: @architect                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PLAN (40 instructions max)                               │
│    Tactical execution plan                                   │
│    Human-aligned design first                                │
│    Output: plan.md                                          │
│    Agent: @architect                                        │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
          ┌───────────────┐
          │  HUMAN REVIEW  │◄── STOP: Architect presents structure.md + plan.md
          │  GATE          │    Human approves, revises, or rejects
          └───────┬───────┘
                  │ Approved
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. YIELD (VERTICAL SLICES)                                   │
│    Execute in testable vertical chunks                       │
│    Each slice: mock → wire → integrate                     │
│    TDD mandatory: tests FIRST, watch fail, implement       │
│    Agent: @coder (TDD mode)                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   @reviewer     │◄──────┐ issues
        │ Validates vs    │       │ found
        │ design doc      │       │
        └────────┬────────┘       │
                 │                │
     ┌───────────┼───────────┐    │
     │           │           │    │
   PASS      WARNINGS      FAIL    │
     │           │           │    │
     ▼           ▼           ▼    │
@verifier  @coder fixes  @coder    │
  check       │           fixes    │
  slice       └────────────────────┘
     │
     ▼
  Next slice? ──► Yes ──► Continue YIELD
     │
     No
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. PR (Ship it)                                              │
│    Code review = "yep, that's what we designed"             │
│    Final verification                                        │
└─────────────────────────────────────────────────────────────┘
```

## Vertical vs Horizontal

**Horizontal (FAIL)**
```
Phase 1: All database models
Phase 2: All API endpoints  
Phase 3: All frontend components
→ 1200 lines of untestable code
```

**Vertical (CRISPY)**
```
Slice 1: Mock API → Wire frontend → Mock services → DB migration → Integrate
Slice 2: Mock API → Wire frontend → Mock services → DB migration → Integrate
→ Each slice independently testable, natural checkpoints
```

## Checkpoint Artifacts

Each phase produces a git-tracked artifact in `plans/`:

1. **context.md** — Loaded relevant codebase areas
2. **research.md** — Pure facts, no opinions (<200 lines)
3. **investigate.md** — Deep dive findings (<200 lines)
4. **structure.md** — High-level outline with testing checkpoints (<200 lines)
5. **plan.md** — Tactical execution plan (<200 lines)
6. **slice-N.md** — Per-slice implementation + tests
7. **review-N.md** — Per-slice review results
8. **verification-N.md** — Verifier script + results

**Total design investment**: ~1000 lines across all docs = 1000 lines of code worth of alignment at 1/5 the cost

## Human Review Gate

**After structure.md + plan.md are produced, workflow PAUSES for human review.**

Human reviews:
- structure.md: Do the slices make sense? Testing checkpoints correct?
- plan.md: Agent assignments logical? Scope matches intent?

Human can:
- **Approve** → Continue to YIELD phase
- **Revise** → Architect updates docs, re-present
- **Reject** → Restart structure phase with new guidance

**No code is written until human approves design docs.** This prevents 1000 lines of wrong code going to waste.

## Iteration Loops

### Review → Coder Cycle
- Reviewer validates against **design.md** and **structure.md**
- If issues found: @coder fixes → @reviewer re-reviews
- **Max 3 cycles**, then escalate to @architect

### Verifier → Coder Cycle
- Verifier runs tests for completed slice
- If fail: @coder fixes → @reviewer (if code changed) → @verifier
- **Max 2 cycles**, then escalate

### Vertical Slice Completion
Each slice must:
- [ ] Tests written first (TDD)
- [ ] Implementation complete
- [ ] Tests pass
- [ ] Reviewer approves
- [ ] Verifier confirms

Only then proceed to next slice.

## Escalation Triggers

Escalate to @architect when:
- Review cycles > 3 (design/architecture issue)
- Verifier cycles > 2 (fundamental problem)
- Coder needs to change approach entirely
- New dependencies discovered
- Scope significantly different from structure.md
- **Instruction budget exceeded** (need to split phase)

## Design Doc as Contract

The **structure.md + plan.md** is the contract:
- Reviewer validates code against design, not just "looks good"
- Coder implements plan, doesn't improvise
- Verifier checks acceptance criteria from structure.md
- If code diverges from design, escalate (don't just patch)

## Anti-Patterns (CRISPY Says No)

| Anti-Pattern | CRISPY Fix |
|--------------|------------|
| 1000-line monolithic plan | Split into <40 instruction phases |
| Research knows what you're building | Hide implementation intent, pure facts only |
| Horizontal layers (all DB → all API) | Vertical slices (end-to-end testable chunks) |
| Write code then tests | TDD: tests FIRST, watch fail, implement, watch pass |
| Review the plan then code | Review design doc once, then review code once |
| Prompt-based control flow | Use actual control flow (if/else, cycles) |
| "Slop" at 10x speed | 2-3x speed with near-human quality |

## Usage

```
/build-workflow "add user authentication with JWT"
```

The workflow:
1. Runs CRISPY phases automatically
2. Creates checkpoint artifacts in `plans/{task-id}/`
3. Human reviews structure.md + plan.md before code
4. Enforces vertical slices with TDD
5. Cycles back when issues found (max iterations enforced)
6. Ships only when all slices complete and verified

## Status Tracking

Track in `plans/{task-id}/status.md`:
- Current CRISPY phase
- Current vertical slice (N of M)
- Iteration counts per phase
- Blockers or escalations needed
- Instruction budget usage per phase

---

**Core Principle**: "Going 10x faster doesn't matter if you're going to throw it all away in 6 months." — Quality through phases, not speed through slop.