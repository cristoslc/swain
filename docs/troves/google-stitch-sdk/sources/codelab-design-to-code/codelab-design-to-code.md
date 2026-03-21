---
source-id: "codelab-design-to-code"
title: "Design-to-Code with Antigravity and Stitch MCP — Google Codelab"
type: web
url: "https://codelabs.developers.google.com/design-to-code-with-antigravity-stitch?hl=en"
fetched: 2026-03-21T00:00:00Z
hash: "d129cd70dd83a3ecb6ff559a921b1f28b57ad952b1975fb30146e0800a127535"
---

# Design-to-Code with Antigravity and Stitch MCP

**Google Codelabs** — Official tutorial

## Overview

Build a production-ready website by bridging AI-driven design with an agent-first development environment. Use Google Stitch to generate a high-fidelity UI, then connect it to the Antigravity IDE via the Model Context Protocol (MCP). Finally, use an autonomous agent to fetch the "Design DNA" and implement a pixel-perfect React application.

## What You'll Do

- **Generate UI in Stitch:** Use natural language to create a full-scale web design in Google Stitch.
- **Bridge with MCP:** Connect Antigravity to your Stitch project using the Model Context Protocol.
- **Autonomous Implementation:** Use Antigravity's "Agent Tab" to fetch design tokens and scaffold a React/Tailwind project.
- **Verify and Refine:** Use the integrated browser to "Vibe Check" the code against the original design.

## What You'll Learn

- How to use Google Stitch to rapidly prototype high-fidelity UI designs.
- How to configure MCP Servers within the Antigravity IDE.
- How to use autonomous agents to translate visual design metadata into modular code.

## Prerequisites

- Chrome web browser
- Antigravity IDE installed
- Google Stitch account
- Stitch API Key
- Node.js (v18+) installed locally
- Google Cloud project with billing enabled

## Step 1: Create the Design in Google Stitch

1. Navigate to stitch.withgoogle.com
2. Select **Web** for browser-optimized layouts
3. Choose model: ensure **Gemini 3** is selected (via model dropdown showing "3.0 Flash")
4. Enter prompt: "Design a modern SaaS landing page for a space-tech startup called LaunchPad. Use a midnight blue and neon purple palette. Include a hero section with a 'Get Started' button, a 3-column features grid, and a glassmorphism pricing table."
5. Click the arrow icon to generate
6. Name the project `LaunchPad`

## Step 2: Configure Antigravity MCP

### Generate the Stitch API Key

1. In Stitch, click Profile Picture > Stitch settings
2. Navigate to API key section
3. Click Create key
4. Copy and store the key securely

### Configure the Stitch MCP in Antigravity

1. Open Antigravity IDE
2. Open Agent Manager (CMD+E Mac / CTRL+E Windows)
3. Click + Open Workspace, name it `LaunchPad-Project`, select a local directory
4. Go to Agent Manager > MCP Servers (via "..." dropdown)
5. Search for "Stitch" and click Install
6. Paste your Stitch API Key
7. Verify: type `List my Stitch projects.` — should return `LaunchPad`

## Step 3: Fetch the Design Context

In the Antigravity chat, type: "Use the Stitch MCP to fetch the 'LaunchPad' project. Extract the color palette and typography, then generate a `DESIGN.md` file in my root directory."

Review the newly created `DESIGN.md` to see hex codes and layout rules the agent extracted.

## Step 4: Implementation (The Build)

Give the "Build" prompt: "I want to build this full website now. Use React and Tailwind CSS. Ensure the components are modular. Once finished, run the dev server and show it to me in the integrated browser."

The agent scaffolds the project in the terminal, writes components in the editor, and opens the preview in the integrated browser.

## Step 5: Review and Refine

1. Compare the Integrated Browser output to the original Stitch design
2. If any element doesn't match, prompt: "The 'Get Started' button padding is slightly off. Refer back to the Stitch design and update the Tailwind classes."
3. The agent re-fetches design context and applies the fix instantly

## Key Concepts

- **DESIGN.md** — A natural language file capturing design tokens (colors, typography, spacing) extracted from Stitch, used as the agent's reference for implementation accuracy
- **MCP** — Acts as a bridge between Antigravity and Google Stitch; instead of manually exporting design tokens, MCP allows Antigravity to fetch the Design DNA directly when needed
- **Agent Manager** — Toggle between Agent Manager and editor with CMD+E / CTRL+E
- **Vibe Check** — Using the integrated browser to visually compare agent output against the original design
