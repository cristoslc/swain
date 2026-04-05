---
name: swain
description: "Meta-router for swain skills. Invoke when the user explicitly asks swain to do something — not merely when they mention the project by name. Routes to the matching swain-* sub-skill — only load the one that matches. If the user's intent matches multiple rows, pick the most specific match. Sub-skills that are not installed will gracefully no-op."
user-invocable: true
license: MIT
allowed-tools: Skill
---
<!-- swain-model-hint: haiku, effort: low -->
Invoke the Skill tool for exactly one match. Pass the user's full prompt as args.

**Disambiguation:** When the user's intent includes an artifact type name (spec, epic, ADR, spike, vision, initiative, journey, persona, runbook, design) alongside a question word (how, what, why), prefer **swain-design** over **swain-help**. swain-help is for meta-questions about swain itself, not for artifact operations.

| swain-design | vision, initiative, epic, story, spec, ADR, spike, bug, persona, runbook, journey, design |
| swain-search | research, evidence, gather sources, search for, evidence pool, what do we know about |
| swain-do | tasks, implementation, tracking, tk, ticket, bookmark, remember where I am |
| swain-sync | commit, push, stage, sync, fetch |
| swain-release | release, version, changelog, tag |
| swain-update | update/upgrade swain |
| swain-doctor | governance, doctor, health check, gitignore |
| swain-roadmap | roadmap, priority matrix, show roadmap, refresh roadmap, status, dashboard, what's next, overview, where are we, what should I work on, show me priorities |
| swain-help | help, how do I, what is, reference, cheat sheet, commands |
| swain-init | init, onboard, setup, bootstrap, session, session info, tab name, preferences, focus on |
| swain-keys | SSH keys, signing, provision keys, configure signing, key setup |
| swain-retro | retro, retrospective, reflect, what did we learn, learnings |
| swain-teardown | teardown, clean up, wrap up, session end, end session, close session, done, log off, sign off |
