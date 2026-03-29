---
source-id: "otel-community-repo"
extract: "governance"
files:
  - "governance-charter.md"
  - "tech-committee-charter.md"
  - "mission-vision-values.md"
  - "gc-check-ins.md"
---

# OpenTelemetry Governance Structure

## Two-Body Governance Model

OpenTelemetry uses a dual-committee governance model under the CNCF:

- **Governance Committee (GC)** -- 9 elected members, 2-year staggered terms. Owns non-technical governance: code of conduct, membership policies, project scope, CNCF relations, roadmap prioritization, community health.
- **Technical Committee (TC)** -- No term limits, no max size (min 4, odd preferred). Owns all technical decisions: release dates, quality standards, specification changes, cross-project mediation, donation technical review.

The GC explicitly delegates all technical authority to the TC and SIGs. The TC recognizes that SIG maintainers have significant autonomy over their implementations.

## Governance Committee (GC)

### Mission

The GC provides decision-making and oversight for governance policies, project management, community health, and strategic direction. It stewards the project's mission, vision, and values.

### Scope

- Charter the Technical Committee
- Define and defend the Code of Conduct
- Define contributor advancement paths (member -> triager -> approver -> maintainer)
- Control GitHub org, repos, hosting, marketing, logo
- Maintain CNCF relationship
- Define project vision, values, mission, scope
- Prioritize roadmap and project proposals
- Ensure SIG health via regular check-ins with SIG leads
- Final escalation path for contested decisions
- Request CNCF funds and support

### Structure

- 9 individual members elected for 2-year terms
- Staggered elections: 4 seats in even years, 5 in odd years
- Maximum 2 members from any single company
- Quorum: 2/3 attendance
- Members removed after missing >50% of meetings in a 6-month period

### Elections

- **Voters**: Members of Standing (20+ contributions in prior rolling year, OR approvers/maintainers)
- **Candidates**: Anyone, unless 2 employees of same company already seated and not up for re-election
- **Endorsements**: 3 total from members of standing at 3 different companies
- **Method**: Time-limited approval voting on Helios
- Exception process for contributors who don't meet quantitative thresholds

### Community Manager Role

GC may appoint Community Managers (CMs) as liaisons for end-user and contributor experience programs. One-year terms, re-confirmed annually after GC elections. CMs act as extension of GC for events, social media, CNCF coordination.

## Technical Committee (TC)

### Responsibilities

- Setting release dates and quality standards
- Technical direction and coding standards
- Approving specification changes
- Mediating cross-project technical discussions
- Evaluating and deciding on code donations (must respond within 2 weeks)
- Organizing project structure including SIG creation and alignment

### Sponsorship Model

Every SIG requires TC sponsorship at one of three levels:

| Level | Description | Requirement |
|-------|-------------|-------------|
| **Escalation** | Primary escalation path for cross-project concerns; participates in GC check-ins | Minimum: every TC member sponsors at least 3 SIGs |
| **Guiding** | Active SIG participant; helps align with OTel technical goals | Minimum: every TC member provides at least 2 |
| **Leading** | Active SIG leadership; drives charter goal completion | Maximum: 2 per TC member |

### No Over-Representation

No more than 25% of TC members may share the same employer.

### Participation

TC members automatically removed if they attend <25% of meetings, don't participate in discussions, and don't vote within any 6-month period.

### Decision Making

- Default: Lazy Consensus with defined notification/review periods
- If consensus fails: Consensus Seeking model with moderator
- Formal votes: Simple majority of quorum (>1/2 of TC), can be sync or async
- Any community member can request TC decision by tagging @open-telemetry/technical-committee on a public issue

## Mission, Vision, and Values

### Mission

> To enable effective observability by making high-quality, portable telemetry ubiquitous.

### Vision -- Five Key Opportunities

1. **Telemetry should be easy** -- fast time-to-value, reasonable defaults, excellent developer experience
2. **Telemetry should be universal** -- unified protocols and conventions across languages and signal types
3. **Telemetry should be vendor-neutral** -- level playing field, no lock-in, interoperable with OSS ecosystem
4. **Telemetry should be loosely coupled** -- pick-and-choose components, no "picking winners"
5. **Telemetry should be built-in** -- high-quality telemetry integrated into the software stack like comments

### Engineering Values

- **Compatibility** -- standards-compliant, vendor-neutral, consistent across languages
- **Stability** -- API stability and backwards compatibility are vital; no new concepts unless broadly needed
- **Resilience** -- graceful degradation, never crash the host application
- **Performance** -- minimal overhead; telemetry must not degrade the systems it observes

## GC Check-In Process

Each SIG has an appointed GC liaison responsible for:

- Monthly check-ins with SIG maintainers (meeting or text-based)
- Attending SIG meetings at least quarterly
- Surfacing SIG concerns to the GC
- Quarterly health assessment along three dimensions:
  1. **Progress** -- on schedule relative to own roadmap?
  2. **Contributor experience** -- new contributors, PR turnaround, newbie-friendly issues
  3. **Maintainer experience** -- workload, burnout, collaboration
