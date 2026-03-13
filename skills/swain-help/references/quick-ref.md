# Swain Quick Reference

## Skills at a Glance

| Skill | Invoke with | What it does |
|-------|-------------|-------------|
| **swain** | `/swain <request>` | Routes to the right sub-skill |
| **swain-init** | `/swain init` | One-time project setup |
| **swain-doctor** | `/swain-doctor` | Session-start health checks (automatic) |
| **swain-design** | `/swain-design` or `/swain` + artifact request | Create and manage documentation artifacts |
| **swain-search** | `/swain-search` or `/swain` + research request | Collect and cache evidence pools |
| **swain-do** | `/swain-do` or `/swain` + task request | Track tasks and implementation work |
| **swain-sync** | `/swain-sync` or `/swain sync` | Fetch, rebase, commit, and push changes |
| **swain-release** | `/swain-release` or `/swain release` | Version bump, changelog, git tag |
| **swain-update** | `/swain-update` or `/swain update` | Update swain to latest version |
| **swain-dispatch** | `/swain dispatch SPEC-NNN` | Dispatch artifacts to background agents via GitHub |
| **swain-retro** | `/swain-retro` or `/swain retro` | Capture learnings at EPIC completion or on demand |
| **swain-help** | `/swain help` or `/swain-help` | This help system |

## Artifacts

Swain manages 9 artifact types, organized into three lifecycle tracks.

### Implementable track (tracked via tk)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Agent Spec** | SPEC-NNN | Proposed → Ready → In Progress → Needs Manual Test → Complete | Technical specification for an agent or component. Supports `type: feature \| enhancement \| bug`. |

These require a tracked plan (via swain-do) before implementation begins.

### Container track (children are tracked)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Epic** | EPIC-NNN | Proposed → Active → Complete | Large initiative decomposed into specs |
| **Spike** | SPIKE-NNN | Proposed → Active → Complete | Time-boxed investigation to reduce uncertainty |

### Standing track (no tracking)

| Type | ID Pattern | When to use |
|------|-----------|-------------|
| **Vision** | VISION-NNN | Product direction and goals |
| **Journey** | JOURNEY-NNN | User journey with pain points |
| **ADR** | ADR-NNN | Architectural decision record |
| **Persona** | PERSONA-NNN | User persona definition |
| **Runbook** | RUNBOOK-NNN | Operational procedure |
| **Design** | DESIGN-NNN | UI/UX design artifact |

### Artifact relationships

- **Vision** → decomposes into Epics and Journeys
- **Epic** → decomposes into Specs, Spikes
- **Spec** → may reference ADRs, Personas, Designs
- **Spike** → attaches to any artifact, may produce ADRs
- Any artifact can declare `depends-on:` blocking dependencies

## Commands

### Creating artifacts

```
/swain create a vision for X
/swain write a spec for Y
/swain file a bug about Z
/swain plan an epic for W
/swain create an ADR for this decision
/swain create a runbook for deployment
```

### Managing lifecycle

```
/swain move SPEC-001 to Ready
/swain transition SPEC-003 to Complete
/swain abandon SPIKE-002
```

### Task tracking

```
/swain what should I work on next?
/swain show my tasks
/swain create a plan for SPEC-001
```

### Validation and auditing

```
/swain check for stale references
/swain show the dependency graph
/swain validate ADRs
```

### Releasing and committing

```
/swain sync
/swain release
/swain bump version
```

## Key Concepts

### The "plan before code" rule

When a SPEC comes up for implementation, swain requires a tracked plan (via tk) before code is written. This ensures work is visible and manageable across sessions. Swain-design enforces this automatically — when you transition an artifact to its implementation phase, it triggers swain-do to create the plan.

### tk (ticket)

The vendored, git-backed task tracker swain uses. Verified by swain-init, operated by swain-do. Key commands:

| Command | What it does |
|---------|-------------|
| `tk ready` | Show next task to work on (blocker-aware) |
| `tk create "title" -t task` | Create a task |
| `tk claim <id>` | Claim work |
| `tk close <id>` | Mark complete |
| `tk ready` | Overview of ready work |
| `tk blocked` | Show blocked tasks |

### Governance block

The `<!-- swain governance -->` block in AGENTS.md contains routing rules that make swain skills discoverable. Managed automatically by swain-doctor. Don't edit it manually — customize anything outside the markers.

### The @AGENTS.md pattern

CLAUDE.md contains just `@AGENTS.md`, which includes the full AGENTS.md file. This lets one file serve Claude Code, GitHub, Cursor, and other tools that read AGENTS.md natively.

## Project Structure

```
<project>/
├── CLAUDE.md              # Contains: @AGENTS.md
├── AGENTS.md              # Project instructions + governance block
├── .tickets/              # tk database (git-tracked)
├── .agents/               # Swain config and logs
└── docs/
    ├── vision/            # VISION artifacts
    ├── epic/              # EPIC artifacts
    ├── spec/              # SPEC artifacts
    ├── spike/             # SPIKE artifacts
    ├── adr/               # ADR artifacts
    ├── persona/           # PERSONA artifacts
    ├── runbook/           # RUNBOOK artifacts
    ├── design/            # DESIGN artifacts
    ├── journey/           # JOURNEY artifacts
    └── list-*.md          # Lifecycle indexes per type
```
