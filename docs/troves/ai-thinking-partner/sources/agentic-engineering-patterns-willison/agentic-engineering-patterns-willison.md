---
source-id: "agentic-engineering-patterns-willison"
title: "Agentic Engineering Patterns"
type: web
url: "https://simonwillison.net/guides/agentic-engineering-patterns/"
fetched: 2026-03-29T00:00:00Z
hash: "f8cd41888547c70a9b0876564e9ecf90aa0c049ed76f43da947ba24dd3041700"
---

# Agentic Engineering Patterns

**Author:** Simon Willison
**Publication:** simonwillison.net (guide / living document)
**Date:** Created February 23, 2026; continuously updated
**Reading time:** ~30 minutes (across all chapters)

## Overview

A curated, evolving guide to patterns for getting the best results out of coding agents like Claude Code and OpenAI Codex. Willison -- creator of Datasette and one of the most prolific writers on practical AI use -- identifies patterns that demonstrably get results and are unlikely to become outdated as tools advance.

## Structure

The guide is organized into six sections with 16 chapters total:

1. **Principles** (5 chapters)
2. **Working with coding agents** (3 chapters)
3. **Testing and QA** (3 chapters)
4. **Understanding code** (2 chapters)
5. **Annotated prompts** (1 chapter)
6. **Appendix** (1 chapter)

---

## Part 1: Principles

### What is Agentic Engineering?

**Agentic engineering** = developing software with the assistance of coding agents.

**Coding agents** = agents that can both write and execute code (Claude Code, OpenAI Codex, Gemini CLI).

**Agents** = software that runs tools in a loop to achieve a goal.

Key insight: Code execution is the defining capability. Without the ability to run code, LLM output is of limited value. With it, agents can iterate toward software that demonstrably works.

What's left for humans? *So much stuff.* Writing code was never the sole activity. The craft has always been figuring out *what* code to write -- navigating dozens of potential solutions with different tradeoffs.

**This is not just "vibe coding."** Vibe coding (coined by Andrej Karpathy, Feb 2025) means prompting LLMs to write code while you "forget that the code even exists." Agentic engineering is the broader practice of bringing code up to production-ready standard.

### Writing Code Is Cheap Now

The biggest challenge: getting comfortable with the consequences of code being cheap.

- **Macro level**: We used to spend great time designing, estimating, planning to ensure expensive coding time was spent efficiently. Features had to earn their development costs many times over.
- **Micro level**: Hundreds of daily decisions predicated on available time. Refactor that function? Write documentation? Add a test for this edge case? Build a debug interface?

Coding agents disrupt all of these intuitions. Parallel agents make it even harder to evaluate -- one human can implement, refactor, test, and document simultaneously.

**But good code still has a cost.** Delivering new code is nearly free; delivering *good* code is not. Good code: works, we know it works, solves the right problem, handles errors gracefully, is simple, protected by tests, documented, affords future changes, meets non-functional requirements.

### Hoard Things You Know How to Do

A key professional asset: a deep collection of answers to "can this be done?" questions, accompanied by proof in the form of running code.

Willison hoards solutions via his blog, TIL blog, 1000+ GitHub repos, and tools.simonwillison.net (HTML tools collection).

**Recombining from your hoard**: One of his favorite patterns is combining two or more existing working examples. Example: building an OCR tool by combining PDF.js (PDF-to-image) + Tesseract.js (image-to-text) with a single prompt.

**Coding agents make this even more powerful**: Tell an agent to clone repos, search for examples, and combine them. "We only ever need to figure out a useful trick *once*."

### AI Should Help Us Produce Better Code

If adopting coding agents demonstrably reduces code quality, address it directly. Shipping worse code is a *choice*.

**Avoiding technical debt**: Common debt involves changes that are simple but time-consuming (poor API design, bad naming, duplication, oversized files). Coding agents handle refactoring tasks like this ideally -- fire up an agent, tell it what to change, leave it in a branch.

**Consider more options**: LLMs help ensure you don't miss obvious solutions. More importantly, agents enable **exploratory prototyping** -- build simulations to test technology choices at near-zero cost.

**Compound engineering loop**: Every project ends with a retrospective. Take what worked, document it for future agent runs. Small improvements compound.

### Anti-Patterns: Things to Avoid

**Don't file PRs with code you haven't reviewed yourself.** If you open a PR with hundreds of AI-generated lines you haven't verified, you are delegating the actual work to reviewers. They could have prompted an agent themselves.

Good agentic PRs:
- Code works, and you're confident it works
- Change is small enough to review efficiently
- Includes additional context (goals, linked issues)
- PR descriptions have been reviewed (agents write convincing but potentially wrong descriptions)
- Include evidence of manual testing (screenshots, notes)

---

## Part 2: Working with Coding Agents

### How Coding Agents Work

A coding agent is a **harness** for an LLM, extending it with capabilities via invisible prompts and callable tools.

Core mechanics:
- **LLMs** work with tokens, not words; charge by token count
- **Chat templated prompts** simulate conversation; LLMs are stateless, so full conversation is replayed each time
- **Token caching** offsets cost of growing conversations; agents avoid modifying earlier content to preserve cache
- **Tools** are functions the harness makes available; model outputs tool calls, harness executes and returns results
- **System prompts** provide instructions (can be hundreds of lines)
- **Reasoning/thinking** lets models spend more tokens working through problems before responding

The whole thing is: LLM + system prompt + tools in a loop.

### Using Git with Coding Agents

Git is a key tool. Coding agents are fluent in Git, including advanced features.

Useful prompts:
- "Review changes made today" -- seeds session with recent context via `git log`
- "Sort out this git mess for me" -- agents navigate Byzantine merge conflicts
- "Use git bisect to find when this bug was introduced" -- agents handle the bisect boilerplate
- "Find and recover my code that does ..." -- agents can search reflog

**Rewriting history**: Don't think of Git history as permanent record -- think of it as a deliberately authored story. Agents can undo commits, remove specific files, combine commits, extract libraries with preserved history.

### Subagents

Subagents provide a way to handle larger tasks without burning through top-level context. A fresh copy dispatched with a new context window and fresh prompt.

Types:
- **Explore subagent**: Investigates the codebase and returns findings
- **Parallel subagents**: Multiple subagents simultaneously for independent tasks
- **Specialist subagents**: Code reviewer, test runner, debugger -- each with custom system prompts

Key value: preserving root context and managing token-heavy operations.

---

## Part 3: Testing and QA

### Red/Green TDD

"Use red/green TDD" is a pleasingly succinct way to get better results. Write tests first, confirm they fail (red), then implement until they pass (green).

Fantastic fit for coding agents because:
- Protects against code that doesn't work
- Protects against unnecessary code
- Ensures a robust test suite for regression protection

Every good model understands "red/green TDD" as shorthand for the full test-first development discipline.

### First Run the Tests

Four-word prompt: "First run the tests." Serves three purposes:
1. Tells the agent there's a test suite and forces it to figure out how to run tests
2. Provides proxy for project complexity
3. Puts agent in a testing mindset

Automated tests are no longer optional with coding agents. The old excuses (time-consuming, expensive to maintain) no longer hold.

### Agentic Manual Testing

Just because code passes tests doesn't mean it works as intended. Manual testing catches what automated tests miss.

Mechanisms:
- `python -c "..."` for quick function testing
- `curl` for JSON APIs ("run a dev server and explore that new API using curl")
- **Playwright** for browser automation
- **Rodney** (Willison's Chrome DevTools Protocol tool)
- **Showboat** for documenting manual test flow

Key pattern: Issues found via manual testing should be added to permanent automated tests.

---

## Part 4: Understanding Code

### Linear Walkthroughs

When you need to understand a codebase (existing code, forgotten details, vibe-coded projects), have an agent construct a structured walkthrough.

Example: Willison vibe-coded a SwiftUI presentation app, then used Claude Code + Showboat to create a detailed walkthrough. Learned about SwiftUI structure and Swift language from reading the agent-generated document.

### Interactive Explanations

When linear walkthroughs aren't enough, build **interactive explanations** -- animated visualizations that make algorithms click.

Example: Understanding word cloud placement algorithm by having Claude build an animated HTML page that shows the Archimedean spiral placement step by step.

Frontier models (Opus 4.6 specifically noted) have good taste in building explanatory animations.

---

## Part 5: Annotated Prompts

### GIF Optimization Tool

A detailed case study of building a GIF optimizer using WebAssembly-compiled Gifsicle, prompted from an iPhone. Demonstrates:
- Compiling C to WASM via a single prompt phrase
- Drag-and-drop UI patterns
- Browser automation testing with Rodney
- Follow-up prompts for build scripts, WASM bundles, credits
- Using `--help` output to teach agents tools

---

## Part 6: Appendix

### Prompts I Use

- **Artifacts**: Instructions for plain HTML/vanilla JS (no React), specific CSS/JS formatting
- **Proofreader**: Spelling, grammar, repeated terms, logical errors, weak arguments, empty links
- **Alt text**: Uses Claude Opus for first-draft alt text; often edits manually afterward

## Relevance to AI as Thinking Partner

This guide is the most practical reference for effective AI-assisted development:

1. **Patterns over tools**: Focus on principles that survive tool evolution
2. **Testing as foundation**: TDD becomes more important, not less, with AI
3. **Evidence over vibes**: Manual testing, automated testing, and linear walkthroughs provide verification
4. **Context management**: Understanding how agents work (tokens, context limits, caching) enables better use
5. **Living document**: Continuously updated as the field evolves
