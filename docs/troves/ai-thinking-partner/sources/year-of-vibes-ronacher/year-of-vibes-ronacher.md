---
source-id: "year-of-vibes-ronacher"
title: "A Year of Vibes"
type: web
url: "https://lucumr.pocoo.org/2025/12/22/a-year-of-vibes/"
fetched: 2026-03-29T00:00:00Z
hash: "7ccef2b2d77ebb6f7fba778a357abb641a7806721ba8c19f3fc71bc2bc6951b8"
---

# A Year of Vibes

**Author:** Armin Ronacher
**Publication:** lucumr.pocoo.org (personal blog)
**Date:** December 22, 2025
**Reading time:** ~15 minutes

## Overview

A full-year retrospective on agentic coding in production from one of the most experienced Python developers in the world. Ronacher reflects on how 2025 fundamentally changed the way he programs, the tools he uses, and the infrastructure gaps he sees ahead.

## 2025 Was Different

2025 was transformative for Ronacher on multiple fronts:
- Left Sentry and started a new company
- Stopped programming the way he did before
- Moved from Cursor to Claude Code, working "almost entirely hands-off"
- Published 36 blog posts (almost 18% of all posts since 2007)
- Had roughly a hundred conversations about AI with programmers and founders

By June 2025, he felt confident enough to share publicly:

> Where I used to spend most of my time in Cursor, I now mostly use Claude Code, almost entirely hands-off. [...] If you would have told me even just six months ago that I'd prefer being an engineering lead to a virtual programmer intern over hitting the keys myself, I would not have believed it.

## The Year of Agents

### Current Status Quo
- Doubling down on: code generation, file systems, programmatic tool invocation via interpreter glue, skill-based learning
- Claude Code's approach is still state of the art for him
- Foundation model providers doubling down on skills reinforces this belief

### Tool Landscape
- **Amp**: The "Apple or Porsche" of agentic coding tools
- **Claude Code**: The "affordable Volkswagen"
- **Pi** (shittycodingagent.ai): The "Hacker's Open Source choice"
- All TUI-based -- terminal UI made a strong comeback
- All feel built by people who use them to an unhealthy degree

### Beyond Coding
LLMs now help with day-to-day life organization, not just code. Expects this to grow further in 2026.

## The Machine and Me

Ronacher addresses the emotional and philosophical dimensions:

- Increasingly hard not to create parasocial bonds with AI tools, especially those with memory
- Has trained himself for two years to think of models as "mere token tumblers" -- that reductive view no longer works
- These systems have human tendencies, but elevating them to human level would be a mistake
- Takes issue with "agent" as a term because agency and responsibility should remain with humans
- Chatbot psychosis is a real risk if we're not careful
- Inability to properly name these creations in relation to us is a challenge we need to solve

## Opinions Everywhere

On the state of discourse:
- This way of working is less than a year old, yet challenges half a century of software engineering experience
- Much conventional wisdom he doesn't agree with, but nothing to back up opinions beyond vibes
- MCP didn't work for him throughout the year despite others swearing by it
- Model selection is vibes-based -- prefers Claude but can't articulate why beyond preference
- Financial interests shape discourse: investors and paid influencers have biases

## Outsourcing vs Building Yourself

- Companies now sell services you would have built yourself (Stainless, Fern, Mintlify, Clerk)
- With agentic coding, you can build much of this yourself again
- Had Claude build him an SDK generator for Python and TypeScript
- Proponent of simple code and building it yourself
- Unclear whether the trend moves toward fewer dependencies or more outsourcing

## Learnings and Wishes

### New Kind of Version Control
- **Biggest unexpected finding:** Hitting limits of traditional tools for sharing code
- PRs on GitHub don't carry enough information to review AI-generated code -- wants to see prompts
- Value in failures: if you steer back to an earlier state, the tool needs to remember what went wrong
- Discarding failed conversation paths means the model retries the same mistakes
- Some tools now use worktrees, checkpoints, in-conversation branching
- Discussions about stacked diffs and alternatives like Jujutsu
- Wants to tell apart genuine human input from machine output

### New Kind of Review
- GitHub's code review UI assigns strict role definitions that don't work with AI
- Wants to leave review comments for his own agents, but no guided way to do that
- Review interface refuses to let him review his own code
- Increased code review happens locally between developer and agents, invisible to others
- "Code review needs to become part of the VCS"

### New Observability
- LLMs can write eBPF programs, SQL queries, control LLDB
- Anything structured and text-based is fertile ground
- Ideas for better observability that were previously user-unfriendly may now be the right solutions
- Python 3.14's external debugger interface is an amazing capability for agentic tools

### Working with Slop
- Still reviews a lot, treats AI output like regular engineering
- Some people have fully "given in to the machine" with some success
- AI-generated contributions to open source without review are "quite frankly an insult"
- Contribution guidelines and PR templates help but feel like fighting windmills
- Solution: vocal pro-AI people defining what good agentic behavior looks like

## Relevance to AI as Thinking Partner

This retrospective is valuable because it comes from someone who:
1. Has deep expertise (Flask, Jinja2, Ruff ecosystem) providing a high-signal reference point
2. Uses AI heavily but refuses to abandon engineering discipline
3. Identifies specific infrastructure gaps rather than vague complaints
4. Acknowledges the emotional dimension of human-AI interaction honestly
5. Distinguishes between what works in practice vs what sounds good in theory
