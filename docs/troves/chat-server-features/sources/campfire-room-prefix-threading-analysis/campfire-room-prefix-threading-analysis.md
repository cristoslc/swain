---
source-id: "campfire-room-prefix-threading-analysis"
title: "Campfire Prefix-as-Thread Workaround — Viability Analysis"
type: web
url: "https://github.com/basecamp/once-campfire/discussions"
fetched: 2026-04-06T22:00:00Z
---

# Campfire Prefix-as-Thread Workaround — Viability Analysis

## The Idea

Use prefixed room names as pseudo-threads in Campfire. For example, `swain/` as the project room and `swain/SPEC-142-session-abc` as a "thread" room. Each bot session creates a new room, archives it when done.

## Evaluation Against Requirements

### Can rooms be created and archived programmatically?

**No.** The Campfire bot API has no room CRUD endpoints. Rooms can only be created through the web UI by admins (restricted to admins as of v1.4.0). There is no archive or delete API. A bot cannot spin up a thread room on demand.

**Workaround:** Fork Campfire and add room-management API endpoints. The source is MIT-licensed Rails code, so this is possible but adds maintenance burden. Every upstream Campfire update would require merge conflict resolution.

### Does Campfire support room grouping or hierarchy?

**No.** Rooms are a flat list in the sidebar. There is no folder, category, space, or nesting concept. Prefixed names like `swain/SPEC-142` would appear alphabetically sorted alongside all other rooms, but they would not visually group under a `swain/` parent.

On mobile (Campfire is PWA-only), the flat room list is even harder to navigate. With 10+ "thread rooms" active, the sidebar becomes cluttered. There is no collapse, filter, or search within the room list documented in the changelog or discussions.

### How does it compare to native threading?

| Feature | Zulip (stream+topic) | Matrix (MSC3440) | Campfire prefix rooms |
|---|---|---|---|
| Thread creation | Automatic on first message with a topic. | Bot sets `m.thread` relation on message. | Manual room creation (no API). |
| Thread discovery | Topics listed in stream sidebar. Unread counts per topic. | Thread panel in Element. | Flat room list, no grouping. |
| Thread archival | Topics auto-collapse when inactive. | Threads stay in timeline. | No archive API. |
| Mobile UX | Native app with topic list. | Element X with thread panel. | PWA with flat room list. |
| Bot effort | Zero — just set the topic field. | Moderate — track root event IDs. | High — requires source fork for room API. |
| Context switching | Click topic in same stream. | Click thread in same room. | Switch rooms entirely. |

### Community evidence

No one in the Campfire community has proposed or documented this pattern. GitHub Discussions show no threading workarounds. The absence suggests either the pattern has been tried and abandoned (unlikely given Campfire's age as ONCE), or the user base does not need threads.

## Verdict

The prefix-as-thread workaround is **not viable** for automated bot use. Three blocking issues:

1. **No room creation API.** The bot cannot create thread rooms without a source fork.
2. **No room hierarchy.** Prefixed rooms are visually indistinct from other rooms in the flat sidebar.
3. **PWA-only mobile.** Room switching on mobile is heavyweight compared to clicking a topic or thread.

Even with a source fork adding room CRUD, the UX remains poor. The flat sidebar with no grouping turns many thread rooms into visual noise. Zulip's stream+topic model and Matrix's in-room threading are both qualitatively superior for this use case.
