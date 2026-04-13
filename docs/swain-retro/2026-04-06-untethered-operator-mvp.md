---
title: "Retro: Untethered Operator MVP"
artifact: RETRO-2026-04-06-untethered-operator-mvp
track: standing
status: Active
created: 2026-04-06
last-updated: 2026-04-06
scope: "VISION-006 brainstorming through MVP smoke test — single session"
period: "2026-04-06"
linked-artifacts:
  - VISION-006
  - VISION-003
  - INITIATIVE-018
  - ADR-037
  - ADR-038
  - ADR-039
  - EPIC-070
  - EPIC-071
  - EPIC-072
  - EPIC-073
  - EPIC-074
  - DESIGN-022
  - DESIGN-023
  - DESIGN-024
  - SPIKE-062
---

# Retro: Untethered Operator MVP

## Summary

Single session from brainstorming to working smoke test. Created VISION-006 (Untethered Operator), designed the architecture through iterative refinement with the operator, ran 4 trove research campaigns (7 extensions), created 17 child artifacts, implemented the MVP (~1350 LOC Python, 56 unit tests), and smoke-tested bidirectional Zulip messaging.

The session demonstrated that swain's artifact model can carry a project from "here's an idea" to "here's a working prototype" in one sitting when the ceremony is right-sized. The MVP process — skip heavy specs, write code with TDD, smoke test fast — produced a working prototype faster than a full artifact build-out would have.

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| VISION-006 | Untethered Operator | Created, Active. |
| VISION-003 | Renamed to Runtime Portability | Scope clarification. |
| INITIATIVE-018 | Remote Operator Interaction | Re-parented, scope updated, 5 child epics. |
| ADR-037 | Chat Platform and Deployment Model | Decided: Zulip Cloud default. |
| ADR-038 | Microkernel Plugin Architecture | Decided: subprocess + NDJSON over stdio. |
| ADR-039 | Hub-and-Spoke Topology | Decided: host bridge as hub. |
| EPIC-070–074 | Host Bridge, Project Bridge, Chat Plugin, Runtime Plugin, Provisioning | All Active, not yet complete. |
| DESIGN-022–024 | Chat Interaction, Deployment Topology, Event Schema | All Active. |
| JOURNEY-003–007 | Phone Check-In through New Project from Phone | All Active. |
| SPIKE-062 | Session Recovery After Host Restart | Active, not yet researched. |
| 4 troves | chat-server-features, agentic-runtime-chat-adapters, tunnel-proxy-provisioning, process-supervision-patterns | All created + extended. |

## Reflection

### What went well

- **Background trove agents.** Running 4 research agents in parallel while brainstorming in the foreground was highly productive. Trove results arrived just as decisions needed evidence. This pattern should be the default for any vision/initiative brainstorming session.
- **Iterative architecture refinement.** The operator caught 5+ architectural gaps that the agent missed — each one refined the design before code was written. The brainstorming-as-conversation model (not brainstorming-as-ceremony) works well when the operator has strong opinions.
- **MVP focus.** Skipping full spec → plan → implementation chains for the MVP and going straight to TDD produced a working prototype in ~6 commits. The prototype taught more than the architecture doc alone.
- **TDD red-green cycle.** Every module started with failing tests, then implementation. Zero test debugging — all 56 tests passed on first GREEN attempt per module.
- **Hosted-first insight.** Questioning "why self-host?" eliminated the VPS, tunnel, and DNS layers from v1 entirely. The operator's instinct ("it feels hinky installing a chat server on a bare machine") was the trigger.

### What was surprising

- **Architecture pivoted 5+ times during brainstorming.** Each pivot was operator-initiated: hexagonal → DDD bounded contexts → two microkernel boundaries → hub-and-spoke → hosted-first. The agent proposed; the operator refined.
- **Commodore-infra reuse.** The operator's own infrastructure project turned out to cover 3 of 4 ingress layers. This wouldn't have surfaced without the operator mentioning it.
- **Campfire eliminated.** The trove research revealed no room creation API and no viable threading workaround — saving wasted implementation effort.
- **ACP has Python SDK.** Eliminated a potential Node.js dependency. The trove extension answered this in one run.
- **Background agent commit collision.** The WhatsApp trove agent committed while 17 artifacts were staged in the foreground, sweeping them into the wrong commit message. Not harmful, but messy.
- **Triple Zulip message.** The relay's dedup logic failed — the outbox had duplicate entries and the `posted_ids` tracking didn't prevent re-sending. First real bug found during smoke test.

### What would change

- **Question "why self-host?" on day zero.** The first 3 hours assumed a VPS. The hosted-first insight late in the session retroactively simplified every architectural decision. For personal products, the build-vs-buy priority stack should extend to infrastructure: hosted > VPS > bare metal.
- **Smoke test earlier.** Building all 5 layers before testing was unnecessary. A 2-layer smoke test (protocol + Zulip adapter posting a message) would have validated the approach in 20 minutes. The operator's "wire it up to this session" request proved this.
- **Coordinate foreground/background git staging.** Background agents should not `git add -A` when the foreground may have staged files. Needs a staging lock or scoped `git add` with explicit file lists.
- **The brainstorming skill ceremony didn't fit.** The brainstorming → design doc → spec review → swain-design chain assumes the output is a spec. This session's output was the vision itself. The chain was bypassed, which was correct but means the skill doesn't cover the "brainstorm a vision" shape.

### Patterns observed

- **Operator as architecture reviewer.** The operator consistently caught structural issues the agent missed: chat bot as three concerns, security domain scoping, host bridge needs multiple chat services, session adoption doesn't need a query protocol. This confirms the alignment loop — the agent proposes, the operator refines.
- **Trove-driven decisions.** Every ADR was informed by trove research. The trove → ADR pipeline works. Background agents make it non-blocking.
- **Smaller bets, faster correction.** The operator explicitly called this out: swain needs to focus on creating smaller bets with more course-correction opportunities, without individual checks becoming overwhelming or rabbit-holing. The MVP approach validated this — prototype first, then fill in specs.

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| Session/worktree ordering bug | GitHub issue (cristoslc/swain#112) | swain-do checks session before worktree; should be reversed. Sessions are worktree-scoped. |
| Smaller bets for course-correction | SPEC candidate | swain should support a "prototype-first" workflow where MVP code precedes full spec decomposition. The current spec → plan → implement chain is too heavy for exploratory work. |
| Background agent staging coordination | SPEC candidate | Background agents need scoped `git add` (explicit file lists, not `-A`) to avoid sweeping foreground-staged files into their commits. |
| Brainstorming skill: vision-shaped output | SPEC candidate | The brainstorming skill assumes output is a design doc that feeds into swain-design for spec creation. When the output is a vision (the artifact IS the brainstorming result), the chain doesn't fit. Add a "vision" output mode. |
| Hosted-first for personal products | ADR candidate | The build-vs-buy priority stack for personal products should extend to infrastructure: hosted platform > VPS > bare metal. Self-hosting is an option, not the default. |
| Relay dedup bug | Bug (in MVP code) | The relay outbox can produce duplicate posts. Fix: deduplicate by content hash before posting, or use a write-once outbox pattern. |
