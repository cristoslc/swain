---
source-type: web-page
title: "Spring AI Agentic Patterns — Agent Skills"
url: https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills/
fetched: 2026-04-06
---

# Spring AI Agent Skills

VMware/Broadcom's Spring AI framework implements the Agent Skills standard.

## Directory structure

```
my-skill/
├── SKILL.md       # Required: instructions + metadata
├── scripts/       # Optional: executable code
├── references/    # Optional: documentation
└── assets/        # Optional: templates, resources
```

## Key conventions

- Follows the open Agent Skills specification exactly.
- Scripts in `scripts/` within each skill.
- Activation: when a task matches a skill's description, the agent reads full SKILL.md.
- Execution: agent follows instructions, optionally loading references or running scripts.
- Works with Spring AI's Dynamic Tool Discovery and Tool Argument Augmentation.
