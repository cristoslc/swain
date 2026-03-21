---
source-id: "stitch-skills-repo"
title: "google-labs-code/stitch-skills — Official Stitch Agent Skills"
type: web
url: "https://github.com/google-labs-code/stitch-skills"
fetched: 2026-03-21T00:00:00Z
hash: "3de301eb745e4d82bf9d128818528a6aecc0aad4ebd1d76ac31bdc12a453ce18"
---

# Stitch Agent Skills

A library of Agent Skills designed to work with the Stitch MCP server. Each skill follows the Agent Skills open standard, for compatibility with coding agents such as Antigravity, Gemini CLI, Claude Code, Cursor.

**Repository:** google-labs-code/stitch-skills (2.9k stars, 319 forks)
**Release:** v0.1 — March 4, 2026
**Languages:** TypeScript 81.3%, Shell 18.7%
**License:** Apache 2.0

## Installation & Discovery

Install any skill from this repository using the skills CLI. This command will automatically detect your active coding agents and place the skill in the appropriate directory.

```bash
# List all available skills in this repository
npx skills add google-labs-code/stitch-skills --list

# Install a specific skill
npx skills add google-labs-code/stitch-skills --skill react:components --global
```

## Available Skills

### stitch-design

Unified entry point for Stitch design work. Handles prompt enhancement (UI/UX keywords, atmosphere), design system synthesis (.stitch/DESIGN.md), and high-fidelity screen generation/editing via Stitch MCP.

```bash
npx skills add google-labs-code/stitch-skills --skill stitch-design --global
```

### stitch-loop

Generates a complete multi-page website from a single prompt using Stitch, with automated file organization and validation.

```bash
npx skills add google-labs-code/stitch-skills --skill stitch-loop --global
```

### design-md

Analyzes Stitch projects and generates comprehensive DESIGN.md files documenting design systems in natural, semantic language optimized for Stitch screen generation.

```bash
npx skills add google-labs-code/stitch-skills --skill design-md --global
```

### enhance-prompt

Transforms vague UI ideas into polished, Stitch-optimized prompts. Enhances specificity, adds UI/UX keywords, injects design system context, and structures output for better generation results.

```bash
npx skills add google-labs-code/stitch-skills --skill enhance-prompt --global
```

### react-components

Converts Stitch screens to React component systems with automated validation and design token consistency.

```bash
npx skills add google-labs-code/stitch-skills --skill react:components --global
```

### remotion

Generates walkthrough videos from Stitch projects using Remotion with smooth transitions, zooming, and text overlays to showcase app screens professionally.

```bash
npx skills add google-labs-code/stitch-skills --skill remotion --global
```

### shadcn-ui

Expert guidance for integrating and building applications with shadcn/ui components. Helps discover, install, customize, and optimize shadcn/ui components with best practices for React applications.

```bash
npx skills add google-labs-code/stitch-skills --skill shadcn-ui --global
```

## Repository Structure

Every directory within `skills/` or at the root level follows a standardized structure to ensure the AI agent has everything it needs to perform "few-shot" learning and automated quality checks.

```
skills/[category]/
├── SKILL.md       — The "Mission Control" for the agent
├── scripts/       — Executable enforcers (Validation & Networking)
├── resources/     — The knowledge base (Checklists & Style Guides)
└── examples/      — The "Gold Standard" syntactically valid references
```

## Suggested New Skills

- **Validation:** Skills that convert Stitch HTML to other UI frameworks and validate the syntax
- **Decoupling Data:** Skills that convert static design content into external mock data files
- **Generate Designs:** Skills that generate new design screens in Stitch from a given set of data

## Disclaimer

This is not an officially supported Google product.
