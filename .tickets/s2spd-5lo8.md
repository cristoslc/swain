---
id: s2spd-5lo8
status: closed
deps: []
links: []
created: 2026-04-13T13:30:33Z
type: epic
priority: 2
assignee: Cristos L-C
external-ref: SPEC-297
tags: [spec:SPEC-297]
---
# SPEC-297: Fix session purpose text drop

Move session-purpose handling from agent-dependent skill instructions into deterministic code in the greeting pipeline. Currently skills/swain-init/SKILL.md and swain-session/SKILL.md tell agents to parse 'Session purpose: <text>' and call swain-bookmark.sh, which is unreliable. Fix: launcher always exports SWAIN_PURPOSE; greeting script reads it, writes bookmark deterministically, surfaces it in JSON. Agent just displays from JSON. ACs: session bookmark reflects purpose text after launch; greeting output shows purpose line. See docs/spec/Active/(SPEC-297)-.../...md


## Notes

**2026-04-13T14:27:23Z**

All 5 child tasks closed. Implementation: f33ad99a. SPEC transition: ad2b33c0. SPEC-297 moved to Needs Manual Test pending operator runtime smoke.
