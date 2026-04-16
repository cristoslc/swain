---
source-id: "build-an-agent-workshop"
title: "Build-An-Agent Workshop"
type: web
url: "https://www.buildanagentworkshop.com/"
fetched: 2026-04-16T18:15:00Z
hash: ""
notes: "Intellectual property of reasoning.software (MadWatch LLC), created by Dakota Kim (GhostScientist)"
---

# Build-An-Agent Workshop

build-an-agent / create-agent-app is the intellectual property of [reasoning.software](https://reasoning.software) (MadWatch LLC), created by [Dakota Kim](https://github.com/GhostScientist)

## Idea to AI Agent CLI in Minutes

An educational platform for building AI agent CLIs. Explore what goes into agentic systems and ship when you're ready. Free and open-source.

Supports three agent SDKs:

- **Anthropic Claude Agents SDK**
- **OpenAI Agents SDK**
- **HuggingFace Tiny Agents**

Two ways to build:

- **Web Builder** — browser-based configuration UI
- **CLI** — `npx build-agent-app`

## Why Build-An-Agent?

An exploration tool for understanding agentic workflows. Not a magic solution.

### Not a Silver Bullet

- Agents can make mistakes and hallucinate. Always verify outputs.
- Complex tasks still need human oversight and judgment.
- This tool helps you learn and experiment, not replace expertise.
- Start small, iterate, and understand what works for your use case.

### Security-First Mindset

- Sandbox code execution in VMs or containers.
- Minimize agent permissions by default.
- Define explicit workflow boundaries.
- Validate outputs before acting on them.

Built for developers, researchers, domain specialists, and curious minds exploring what's possible with agentic workflows.

## Enterprise Workflows Meet AI Intelligence

Generated agents include sophisticated slash command workflows for multi-step operations. Built on Claude Agent SDK, OpenAI Agents API, and HuggingFace Tiny Agents with MCP tools, streaming, and configurable security.

### Multi-Step Workflows

Domain-specific slash commands like `/literature-review`, `/code-audit`, `/invoice-batch` orchestrate complex multi-step processes. Template variables, retry logic, and error handling built-in. Demonstrated for Claude and OpenAI SDKs.

### Configurable Security

Claude Code-style permission system with interactive prompts for file operations, command execution, and network requests. Users approve high-risk actions before they execute. Demonstrated for Claude and OpenAI SDKs.

### SDK-Native & Customizable

Download complete TypeScript source code. Full control over prompts, tools, and workflows. Extend with custom business logic from day one. Demonstrated for Claude and OpenAI SDKs.

### Zero-Build Tiny Agents

Create lightweight agents with just JSON + markdown. No build step, no dependencies. Run instantly with npx, share to the HuggingFace community, and use powerful open-source models.

## The 5 Levers of Control

Claude Code agents are shaped by 5 control mechanisms. Each serves a distinct purpose in the agentic workflow.

### Memory

Project context and coding standards. CLAUDE.md.

### Slash Commands

Reusable task templates. `.claude/commands/`

### Skills

Specialized expertise modules. `.claude/skills/`

### Subagents

Specialized worker processes. `.claude/agents/`

### Hooks

Event-driven automation. `.claude/settings.json`

## Expert Agent Templates

### Research Ops Agent

Evidence-backed literature reviews, source tracking, and analyst-ready briefs. Capabilities: Web Fetch/Search, Document Parsing, Citation Tracking, +1 more.

### Legacy Code Modernization

Analyze legacy codebases, identify technical debt, and create modernization strategies. Capabilities: Code Analysis, Migration Planning, Security Audit, +1 more.

### Document Processing

Extract, analyze, and transform business documents at scale with automation. Capabilities: PDF Extraction, Classification, Data Validation, +1 more.

### Social Media Manager

Create, plan, and optimize social media content across all major platforms. Capabilities: Content Creation, Trend Analysis, Scheduling, +1 more.

## Vision

Build An Agent Workshop is an educational resource for understanding what goes into AI agents. Core beliefs: learning before automating, open-source community-driven development, and the future of local-first, offline-capable AI tooling.

- Open Source
- Educational First
- Local-First Future

## Research Agent Demo

```
$ researcher-agent

🔬 Research Operations Agent

Evidence-backed research with systematic literature reviews

researcher> /literature-review --sources ./papers --limit 15

✓ Step 1/6: Found 23 documents in ./papers
✓ Step 2/6: Extracted 15 key claims with citations
⋯ Step 3/6: Identifying research gaps...
```

## Related

- GitHub: <https://github.com/GhostScientist/build-an-agent>
- reasoning.software: <https://reasoning.software>
- MIT License (c) 2025-2026 Dakota Kim / reasoning.software (MadWatch LLC)