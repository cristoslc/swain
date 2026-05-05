---
title: Scheduled Tasks
url: https://www.getagentcraft.com/docs/features/scheduled-tasks
fetched: 2026-05-04
type: documentation
---

# Scheduled Tasks

Create recurring agent tasks with cron-like intervals.

Scheduled tasks (loops) let you set up recurring agent work on a timer. Pick a hero, choose an interval, type a prompt, and let the agent execute it repeatedly.

## Active Loops Panel

The Active Loops widget appears in the left sidebar. It shows all running loops with:

- Hero name and avatar
- Loop prompt (truncated)
- Iteration count
- One-click stop button

## Creating a Loop

1. Open the Active Loops panel in the left sidebar
2. Select a hero to assign the loop to
3. Choose an interval preset:

| Interval | Use Case |
| --- | --- |
| 1 min | Rapid polling or checks |
| 5 min | Frequent monitoring |
| 15 min | Periodic tasks |
| 30 min | Regular maintenance |
| 1 hour | Hourly jobs |

4. Type the prompt the agent should execute each iteration
5. Click Start Loop

## How It Works

When a loop starts, AgentCraft sends the prompt to the selected hero at the configured interval. The agent executes the prompt as a normal message each time. Loop state is tracked server-side and persists across page refreshes.

### UI Badges

Loop status is visible across the UI:

- Agent Roster — Loop badge next to the hero name
- Vitals Header — Active loop indicator in the top bar
- Composer — Loop icon when chatting with a looping hero

## Stopping Loops

Click the stop button next to any loop in the Active Loops panel. The loop stops immediately — the current iteration (if running) completes but no further iterations are scheduled.

## Use Cases

- Continuous testing — Run test suites every few minutes during development
- Log monitoring — Have an agent check logs periodically and summarize issues
- Code review — Schedule regular code quality checks on a branch
- Status reports — Get periodic summaries of project progress