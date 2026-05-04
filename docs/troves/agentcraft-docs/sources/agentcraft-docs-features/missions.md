---
title: Missions
url: https://www.getagentcraft.com/docs/features/missions
fetched: 2026-05-04
type: documentation
---

# Missions

Track completed tasks with persistent mission history.

Missions represent tasks assigned to your heroes. AgentCraft auto-generates thematic quest names for each task and tracks mission progress with AI-generated summaries.

## Quest Board

Press F9 to open the quest log and see active, completed, and failed missions.

## Mission Lifecycle

1. Start — When you send a prompt to a hero, a mission is created with a thematic name
2. Active — The hero works on the task, tracked in real time
3. Complete — When the hero finishes, the mission is marked as completed
4. Summary — An AI-generated short summary (3 words) and long summary (1 sentence) are created for each completed mission

## Mission Metrics

Each completed mission tracks:

- Duration — How long the mission took
- Total tokens — Token usage during the mission
- Lines added/removed — Code changes made during the mission
- Subagents — Any subagents spawned during the task

## Persistence

Completed missions persist across server restarts. Mission history is stored at ~/.agentcraft/mission-history.json.

When you reconnect to AgentCraft, heroes display their last completed mission info instead of just showing "Idle".

### Limits

- Global history: Up to 200 completed missions
- Per session: Up to 50 missions per hero session
- On connect: The 50 most recent missions are sent to the frontend

## Mission Control

Press M to toggle mission control, which provides an overview of all active and recent missions across your heroes.

## Activity Timeline

Press T to toggle the activity timeline, showing a chronological view of hero activities and mission events.