---
title: "Swain Project Developer"
artifact: PERSONA-001
status: Validated
author: cristos
created: 2026-03-11
last-updated: 2026-03-11
linked-artifacts:
  - JOURNEY-001
depends-on-artifacts: []
---

# Swain Project Developer

## Archetype Label

Solo Developer with AI Pair

## Demographic Summary

- **Role:** Independent software developer or small-team lead
- **Technical proficiency:** High — comfortable with CLI tools, git workflows, and AI-assisted development
- **Project type:** Side projects, personal tools, or early-stage products managed solo or with 1-2 collaborators
- **AI usage:** Heavy — uses Claude Code, OpenCode, Codex, or Gemini CLI as a pair programmer. Delegates routine tasks to agents, expects tools to be agent-accessible. May switch between coding agents across sessions.
- **Environment:** macOS, terminal-based AI coding agent (owns stdin/stdout), browser for dashboards, GitHub for hosting

## Goals and Motivations

1. **Keep momentum on multi-stream projects.** Often juggles 3-5 active workstreams (features, spikes, bug fixes) across a single repo. Needs to context-switch quickly without losing track of where things stand.
2. **Trust the system of record.** Wants one authoritative source for project state — not a mental model, not a separate app, not a Notion board that drifts from reality.
3. **Minimize ceremony.** Will tolerate process (specs, ADRs, lifecycle phases) if it genuinely prevents rework, but abandons tools that create more overhead than they save.
4. **Let the agent help.** Expects the AI pair to read project state, suggest what to work on, and execute plans — not just respond to explicit commands.

## Frustrations and Pain Points

1. **Tool maintenance eats into build time.** bd requires Dolt server management, .beads hygiene, and periodic CLI errors. swain-doctor patches over this, but the underlying fragility remains.
2. **No visual dashboard for project state.** CLI output is text-only — no board view for tasks, no at-a-glance artifact status. "What's the state of my project?" requires running multiple commands and synthesizing mentally.
3. **Context loss across sessions.** After a break (hours, days), getting back up to speed requires re-reading status output, checking git log, and remembering what was in progress. The agent starts fresh each session.
4. **Invisible implementation plans.** After specs are approved and tasks are created, there's no way to see the plan visually — just flat `bd list` output with no structure or progress indication.

## Behavioral Patterns

- Starts each session with `/status` or expects the MOTD panel to orient them
- Works in focused bursts (1-3 hours), then steps away; expects to resume without ramp-up cost
- Delegates git operations, task tracking, and boilerplate to the agent
- Reads specs and spikes as reference material but rarely opens them manually — expects the agent to surface relevant context
- Will override or skip process when it feels like friction rather than value ("just do it, we'll spec it later")

## Context of Use

- **When:** Start of work session (orientation), mid-session (checking progress), end of session (bookmarking state)
- **Where:** Terminal — tmux with multiple panes, one dedicated to MOTD/status
- **How:** Conversational with agent, slash commands, occasional direct CLI for git or debugging
- **Frequency:** Daily or near-daily for active projects, weekly check-ins for maintenance projects

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Draft | 2026-03-11 | — | Initial creation from spike investigation pain points |
| Validated | 2026-03-11 | a950529 | Approved by developer — persona confirmed |
