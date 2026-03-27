---
source-id: "otel-community-repo"
extract: "contributing"
files:
  - "CONTRIBUTING.md"
  - "guides/contributor/README.md"
  - "guides/contributor/membership.md"
  - "guides/maintainer/conflict-resolution.md"
---

# OpenTelemetry Contributor Guide

## Getting Started

Prerequisites for contributing:

1. GitHub account with two-factor authentication enabled
2. Sign the Contributor License Agreement (CLA) -- one-time process
3. Read and agree to the Code of Conduct
4. Join the [CNCF Slack](https://slack.cncf.io/) -- main channel: `#opentelemetry`

Contributions are not limited to code. Bug reports, documentation, website work, community management, event organization, and survey participation all count.

## Membership Ladder

OpenTelemetry defines a clear progression path for contributors:

### Member

- **Defined by**: OpenTelemetry GitHub org membership
- **Requirements**: 2 approver/maintainer sponsors (from different companies), multiple contributions, active in 1+ subprojects
- **Privileges**: Can vote in GC elections, be assigned issues/PRs, review PRs (but not sufficient to merge)
- **Process**: Open a membership issue on `open-telemetry/community`, get sponsor confirmations, TC reviews

### Triager

- **Defined by**: GitHub Triage permissions, listed in CONTRIBUTING/CODEOWNERS/README
- **Requirements**: Nominated by a maintainer, 1+ month of consistent issue triage
- **Privileges**: Apply labels, milestones, assignees; organize backlog
- **Note**: Code contributions not required

### Approver

- **Defined by**: Entry in CODEOWNERS file (can be scoped to part of codebase)
- **Requirements**: 1+ month reviewing, 10+ substantial PRs reviewed or authored, nominated by maintainer
- **Privileges**: Approve code contributions, mentor contributors

### Maintainer

- **Defined by**: GitHub org ownership, permissions, CODEOWNERS entry
- **Requirements**: Deep technical understanding, sustained design contributions, authoring/reviewing proposals
- **Privileges**: Make/approve design decisions, set technical direction, define milestones/releases, mentor approvers
- **Election**: Vote of existing SIG maintainers; PR-based process (all approve OR majority approve + no objections, min 5 days open)
- **Self-nomination encouraged**: approach an existing maintainer about sponsoring your candidacy

### Specification Sponsor

- **Defined by**: TC nomination, listed in community-members.md
- **Requirements**: 1+ year contributing, 10+ substantial spec PRs, TC member nomination
- **Privileges**: Approvals count toward spec PR merge requirements; can sponsor spec issues/PRs
- **Bar**: Intentionally high due to cross-project impact of specification changes

### Emeritus

- **Position of honor** for former maintainers/approvers/triagers who step down
- Listed in emeritus section of CONTRIBUTING/CODEOWNERS/README
- Company affiliations removed (may change over time)
- Can be promoted back to previous position at current maintainers' discretion

## Conflict Resolution

SIG-internal technical conflicts follow this process:

1. SIG maintainers document options as a GitHub issue (just the options, not full pros/cons)
2. Each maintainer votes by commenting on the issue
3. Most votes wins
4. If tied, the TC gets a single tiebreaking vote

The process prioritizes velocity while recognizing good intentions and shared goals.

## Key Policies

- **Lazy Consensus**: Default decision model -- silence within defined review period implies consent
- **Consensus Seeking**: Used for TC decisions -- moderator asks "Does anyone object?" as final call
- **Maximal Representation**: Max 2 GC members from same company; max 25% TC members from same employer
- **Donation Process**: Organizations can donate code via issue on `open-telemetry/community`; TC must respond within 2 weeks
- **GenAI Policy**: Documented in `policies/genai.md`

## Communication Channels

- **Slack**: CNCF Slack workspace, per-SIG channels (e.g., `#otel-specification`, `#otel-sampling`, `#otel-collector`)
- **Meetings**: Regular SIG meetings on the OpenTelemetry Public Calendar; most recorded
- **Meeting Notes**: Google Docs (linked from sigs.yml)
- **Mailing Lists**: CNCF-hosted lists for governance, announcements, maintainers
- **GitHub**: Issues and PRs are the primary async work surface
