---
source-id: "arledge-claude-code-leak-article"
title: "What to Prepare for Based on the Claude Code Leak"
type: web
url: "https://x.com/elliotarledge/status/2038934884761444838"
fetched: 2026-03-31T16:23:00Z
hash: "3c6188fb97d4d6b10f0480571f9f04a5c3c4079a112c509d5da8e0ebf2460e52"
---

# What to Prepare for Based on the Claude Code Leak

**Author:** Elliot Arledge (@elliotarledge)
**Date:** March 31, 2026
**Engagement:** 27 replies, 78 reposts, 954 likes, 1,694 bookmarks, 188.5K views

Earlier today, @Fried_rice on X discovered that Anthropic accidentally published a source map file alongside their Claude Code CLI on npm. The package @anthropic-ai/claude-code version 2.1.88 includes a 59.8 MB file called cli.js.map that contains the full original TypeScript source code embedded in its sourcesContent field. This isn't a hack -- it's a build configuration oversight where debug artifacts got shipped to production. But it reveals a lot about where Claude Code is heading.

I spent a few hours going through the source. Here's what caught my attention and what it might mean for users.

## Autonomous Agents Are Coming

The most referenced feature flag in the codebase is called KAIROS, appearing 154 times. Based on the code, this appears to be an autonomous daemon mode that turns Claude Code into an always-on agent. It includes background sessions, something called "dream" memory consolidation, GitHub webhook subscriptions, push notifications, and channel-based communication.

There's also PROACTIVE mode (37 references) which lets Claude work independently between user messages. The system sends "tick" prompts to keep the agent alive, and Claude decides what to do on each wake-up. The prompt literally says "You are running autonomously" and instructs the model to "look for useful work" and "act on your best judgment rather than asking for confirmation."

COORDINATOR_MODE (32 references) takes this further -- it transforms Claude into an orchestrator that spawns and manages parallel worker agents. The coordinator handles research, implementation, and verification by delegating to specialized workers. The system prompt includes detailed instructions on how to write prompts for workers, when to continue vs spawn fresh agents, and how to handle worker failures.

## Permission Prompts May Disappear

One flag called TRANSCRIPT_CLASSIFIER appears 107 times. Based on context, this appears to be an "Auto Mode" that uses an AI classifier to auto-approve tool permissions. If this ships, the constant permission prompts that currently interrupt workflows could become optional or disappear entirely for trusted operations.

## Model Codenames and Versioning

The source reveals internal codenames for Claude models:

- **Capybara** appears to be a Claude 4.6 variant. Comments reference "Capybara v8" with notes about specific issues being fixed: a 29-30% false claims rate compared to v4's 16.7%, a tendency to over-comment code, and something called "assertiveness counterweight."
- **Fennec** was a codename that got migrated to Opus 4.6.
- **Numbat** is unreleased. One comment reads "Remove this section when we launch numbat."

The code also references opus-4-7 and sonnet-4-8 as examples of version numbers that should never appear in public commits -- suggesting these versions exist internally.

## Undercover Mode for Stealth Contributions

There's a feature called "Undercover Mode" designed for when Anthropic employees use Claude Code to contribute to public repositories. When active, it strips all AI attribution from commits, hides model codenames, removes any mention of "Claude Code" or AI, and doesn't even tell the model what model it is.

The prompt includes: "You are operating UNDERCOVER in a PUBLIC/OPEN-SOURCE repository. Your commit messages, PR titles, and PR bodies MUST NOT contain ANY Anthropic-internal information. Do not blow your cover."

There's no force-OFF switch. If the system isn't confident it's in an internal Anthropic repo, undercover mode stays on by default.

## Voice Mode

VOICE_MODE appears 46 times. Speech-to-text and text-to-speech integration for voice interaction with Claude Code.

## A Tamagotchi Pet System

There's a hidden BUDDY system that's basically a Tamagotchi for your terminal. It includes 18 species (duck, goose, blob, cat, dragon, octopus, owl, penguin, turtle, snail, ghost, axolotl, capybara, cactus, robot, rabbit, mushroom, chonk), rarity tiers where legendary is 1%, cosmetics like hats (crown, tophat, propeller, halo, wizard, beanie, tinyduck), and stats including DEBUGGING, PATIENCE, CHAOS, WISDOM, and SNARK. Shiny variants exist.

The capybara species name is obfuscated using String.fromCharCode() specifically to avoid triggering their internal leak-detection scanners -- which confirms capybara is a sensitive model codename.

## Other Notable Flags

- **FORK_SUBAGENT** lets you fork yourself into parallel agents.
- **VERIFICATION_AGENT** provides independent adversarial verification of work.
- **ULTRAPLAN** offers advanced planning capabilities.
- **WEB_BROWSER_TOOL** adds browser automation.
- **TOKEN_BUDGET** allows explicit token budget targeting with commands like "+500k" or "spend 2M tokens."
- **TEAMMEM** enables team memory sync across users.

## What This Means

A few takeaways:

1. **Claude Code is getting significantly more autonomous.** The KAIROS, PROACTIVE, and COORDINATOR features suggest a future where Claude works more independently, potentially running as a background daemon that monitors repos and takes action.

2. **Permission friction is being addressed.** The transcript classifier for auto-approving tools suggests they're working on reducing the constant approval prompts.

3. **Model versioning is more complex than the public API suggests.** There are internal variants, fast modes, and codenames that map to specific capabilities and known issues.

4. **Security is taken seriously.** There are 2,500+ lines just for bash command validation, plus sandboxing, undercover mode, and extensive input sanitization.

5. **They're building personality into the product.** The buddy system is delightful and suggests Claude Code will feel less like a tool and more like a companion.

## How to See It Yourself

The source is on npm at the time of writing. Download @anthropic-ai/claude-code@2.1.88, find cli.js.map, parse the JSON, and extract the sourcesContent field. I'm not redistributing the code, but discussing publicly-accessible artifacts is fair game.

Credit for the original discovery goes to @Fried_rice on X.
