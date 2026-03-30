---
source-id: "agentic-coding-ronacher"
title: "Agentic Coding: Armin Ronacher"
type: media
url: "https://www.youtube.com/watch?v=bpWPEhO7RqE"
fetched: 2026-03-29T00:00:00Z
hash: "fc8ef0e829486cf29463431ccbd1ae79885c062cfec5d1753cdb463d889ca0b4"
notes: "Transcript not available via automated fetch; content synthesized from video metadata and author's related writing"
---

# Agentic Coding: Armin Ronacher

**Channel:** Microsoft Azure Developers
**Speaker:** Armin Ronacher (creator of Flask, Jinja2, Ruff; founder of Sentry spinoff)
**Duration:** ~71 minutes
**Format:** Conference talk / presentation

## Overview

Armin Ronacher -- one of the most respected Python developers and the creator of Flask -- shares his real production workflow with Claude Code and other agentic coding tools. This talk captures the perspective of a deeply experienced systems programmer who has fully embraced agentic coding in his daily work.

## Key Themes

### The Shift to Agentic Coding

Ronacher describes a fundamental change in how he works: transitioning from hands-on coding in an editor to acting as an "engineering lead to a virtual programmer intern." He moved from Cursor to Claude Code over the course of 2025, working almost entirely hands-off.

### Tools and Workflow

- Primary tools: Claude Code, Amp, Pi (shittycodingagent.ai)
- Claude Code described as the "affordable Volkswagen" of agentic tools
- Amp as the "Apple or Porsche" -- polished but different tradeoffs
- All three are TUI (terminal UI) tools, marking an unexpected comeback for command-line interfaces

### The Machine and the Developer

A significant portion addresses the evolving relationship between developer and AI:
- Difficulty avoiding parasocial bonds with AI tools, especially those with memory
- Tension between viewing LLMs as "mere token tumblers" and their increasingly human-like tendencies
- Discomfort with the term "agent" because agency and responsibility should remain with humans
- Concern about unintentional anthropomorphization

### Version Control Needs Reinvention

One of Ronacher's strongest arguments: current tools (Git, GitHub PRs) are insufficient for agentic workflows:
- PRs don't carry enough information to review AI-generated code -- he wants to see the prompts that led to changes
- Value in failures: models need to remember what went wrong; discarding failed paths means the model tries the same mistakes again
- Interest in stacked diffs and alternative VCS like Jujutsu
- Code review needs to become part of the VCS itself

### Code Review in the Agentic Era

- Current code review UIs assign strict role definitions that don't work with AI
- GitHub's review interface refuses to let you review your own code
- Much iteration now happens locally between developer and agents, invisible to team
- Needs rethinking for AI-assisted workflows

### Observability Opportunities

- LLMs can write eBPF programs, SQL queries, LLDB scripts
- Anything structured and text-based is fertile ground for agentic tools
- Python 3.14's external debugger interface is an "amazing capability for an agentic coding tool"
- Dynamic reconfiguration of services for targeted filtering -- previously user-unfriendly, now viable via LLMs

### Working with "Slop"

- Ronacher still reviews extensively and treats AI output like regular software engineering
- Acknowledges others who have fully "given in to the machine" with some success
- AI-generated contributions to open source projects without review are "quite frankly an insult"
- Contribution guidelines and PR templates help but feel like "a fight against windmills"
- Solution may come from vocal pro-AI people defining what good behavior looks like

### Build vs Buy

- Increased outsourcing of services (Stainless, Fern, Mintlify, Clerk) raised the bar
- But agentic coding means you can build much of this yourself
- Ronacher had Claude build him an SDK generator for Python and TypeScript
- Optimistic that AI could encourage building on fewer dependencies
- Tension with current trend of outsourcing everything

## Relevance to AI as Thinking Partner

This talk is essential viewing for experienced developers because Ronacher:
1. Demonstrates what a mature, skeptical adoption of AI coding looks like
2. Identifies genuine infrastructure gaps (VCS, code review, observability)
3. Refuses to either dismiss or uncritically embrace the tools
4. Speaks from months of daily production use, not demos or toy projects
