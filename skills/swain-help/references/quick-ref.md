# Swain Quick Reference

## Skills at a Glance

| Skill | Invoke with | What it does |
|-------|-------------|-------------|
| **swain** | `/swain <request>` | Routes to the right sub-skill |
| **swain-init** | `/swain init` | One-time project setup |
| **swain-config** | `/swain-config` | Session-start governance (automatic) |
| **swain-design** | `/swain-design` or `/swain` + artifact request | Create and manage documentation artifacts |
| **swain-search** | `/swain-search` or `/swain` + research request | Collect and cache evidence pools |
| **swain-do** | `/swain-do` or `/swain` + task request | Track tasks and implementation work |
| **swain-push** | `/swain-push` or `/swain push` | Commit and push changes |
| **swain-release** | `/swain-release` or `/swain release` | Version bump, changelog, git tag |
| **swain-update** | `/swain-update` or `/swain update` | Update swain to latest version |
| **swain-help** | `/swain help` or `/swain-help` | This help system |

## Artifacts

Swain manages 11 artifact types, organized by tier.

### Implementation tier (tracked via bd)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Story** | STORY-NNN | Todo → In Progress → Done | User-facing feature with acceptance criteria |
| **Agent Spec** | SPEC-NNN | Draft → Review → Approved → Testing → Implemented | Technical specification for an agent or component |
| **Bug** | BUG-NNN | Reported → Active → Fixed → Verified | Defect to track and fix |

These require a tracked plan (via swain-do) before implementation begins.

### Coordination tier (children are tracked)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Epic** | EPIC-NNN | Proposed → Active → Testing → Complete | Large initiative decomposed into stories and specs |

### Research tier (tracking optional)

| Type | ID Pattern | Phases | When to use |
|------|-----------|--------|-------------|
| **Spike** | SPIKE-NNN | Planned → Active → Complete | Time-boxed investigation to reduce uncertainty |

### Reference tier (no tracking)

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
- **Epic** → decomposes into Stories, Specs, Spikes
- **Story/Spec** → may reference ADRs, Personas, Designs
- **Spike** → attaches to any artifact, may produce ADRs
- **Bug** → affects Specs, Epics; may link to Designs
- Any artifact can declare `depends-on:` blocking dependencies

## Commands

### Creating artifacts

```
/swain create a vision for X
/swain write a spec for Y
/swain file a bug about Z
/swain plan an epic for W
/swain add a user story for ...
/swain create an ADR for this decision
/swain create a runbook for deployment
```

### Managing lifecycle

```
/swain move SPEC-001 to Review
/swain transition STORY-003 to Done
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
/swain push
/swain release
/swain bump version
```

## Key Concepts

### The "plan before code" rule

When a SPEC, STORY, or BUG comes up for implementation, swain requires a tracked plan (via bd) before code is written. This ensures work is visible and manageable across sessions. Swain-design enforces this automatically — when you transition an artifact to its implementation phase, it triggers swain-do to create the plan.

### bd (beads)

The external, git-backed task tracker swain uses. Installed by swain-init, operated by swain-do. Key commands:

| Command | What it does |
|---------|-------------|
| `bd ready --json` | Show next task to work on (blocker-aware) |
| `bd create "title" -t task --json` | Create a task |
| `bd update <id> --claim --json` | Claim work |
| `bd close <id>` | Mark complete |
| `bd status` | Overview of all work |
| `bd list --pretty` | Detailed task list |
| `bd blocked` | Show blocked tasks |

### Governance block

The `<!-- swain governance -->` block in AGENTS.md contains routing rules that make swain skills discoverable. Managed automatically by swain-config. Don't edit it manually — customize anything outside the markers.

### The @AGENTS.md pattern

CLAUDE.md contains just `@AGENTS.md`, which includes the full AGENTS.md file. This lets one file serve Claude Code, GitHub, Cursor, and other tools that read AGENTS.md natively.

## Project Structure

```
<project>/
├── CLAUDE.md              # Contains: @AGENTS.md
├── AGENTS.md              # Project instructions + governance block
├── .beads/                # bd database (git-tracked)
├── .agents/               # Swain config and logs
└── docs/
    ├── vision/            # VISION artifacts
    ├── epic/              # EPIC artifacts
    ├── story/             # STORY artifacts
    ├── spec/              # SPEC artifacts
    ├── spike/             # SPIKE artifacts
    ├── adr/               # ADR artifacts
    ├── persona/           # PERSONA artifacts
    ├── runbook/           # RUNBOOK artifacts
    ├── bug/               # BUG artifacts
    ├── design/            # DESIGN artifacts
    ├── journey/           # JOURNEY artifacts
    └── list-*.md          # Lifecycle indexes per type
```
