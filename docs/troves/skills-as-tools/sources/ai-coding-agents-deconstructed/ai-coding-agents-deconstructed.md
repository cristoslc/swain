---
title: "AI Coding Agents, Deconstructed"
source-url: "https://blog.apiad.net/p/the-anatomy-of-ai-coding-agents"
fetch-date: "2026-05-01"
type: web-page
author: "Alejandro Piad Morffis"
---

# AI Coding Agents, Deconstructed

## Core Thesis

Everything an AI agent does happens inside a context window. System prompt, user input, tool results, skill injections — they all live there. The agent's only mechanism for action is the ReAct (Reasoning + Acting) loop.

## The Enforcement Gap

"Plan mode" in most tools is just a prompt. There is no enforcement. The agent can write code in plan mode if it wants to. It can ignore the plan in build mode. It can skip straight to implementation if the prompt implies urgency.

Proposed architecture — modes with hard enforcement:
- **Analyze mode**: reads and writes summaries to a knowledge base. Cannot touch production files. Not "should not" but *cannot*. Permissions are built into the mode itself.
- **Plan mode**: produces design documents, creates task breakdowns. Cannot modify source files.
- **Build mode**: implements tasks from the plan. Cannot modify the plan itself.

## The Context Window Problem

The agent only has access to what's in its context window. This limits:
- Number of rules and conventions it can follow.
- Amount of codebase it can see at once.
- Depth of reasoning it can maintain.
- Memory across long-running sessions.

## Tool-Based vs Skill-Based

Tools provide deterministic enforcement because they run as code. Skills provide advisory guidance because they run as text in the context window. The key insight: tools can enforce what skills can only suggest.
