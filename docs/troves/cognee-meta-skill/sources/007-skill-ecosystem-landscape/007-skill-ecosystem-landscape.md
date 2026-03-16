---
source-id: "007"
title: "SKILL.md Ecosystem — Claude Code Skills Landscape and Meta-Skill Patterns"
type: web
url: "https://code.claude.com/docs/en/skills"
fetched: 2026-03-15T21:06:00Z
hash: "sha256:placeholder"
---

# SKILL.md Ecosystem Landscape

Survey of the Claude Code skills ecosystem, meta-skill patterns, and how cognee-skills fits.

## Official Anthropic Skill Spec

Skills are specialized folders containing instructions, scripts, and resources that Claude dynamically discovers and loads when relevant. Progressive disclosure architecture:
- Metadata loading (~100 tokens): scan available skills for relevance
- Full load: only when selected

Structure: `my-skill/SKILL.md` (required) + optional `scripts/`, `references/`, `assets/`.

SKILL.md: YAML frontmatter (between `---` markers) configuring when/how, markdown body with instructions.

## Anthropic skill-creator (Official Meta-Skill)

The official skill-creator from `anthropics/skills` is a meta-skill for creating other skills. It generates properly formatted SKILL.md files. It includes an eval system:
- Splits eval set into 60% train / 40% held-out test
- Evaluates description trigger rate (runs each query 3 times)
- Proposes description improvements based on what failed

## Other Meta-Skills in the Ecosystem

### YYH211/Claude-meta-skill
Curated collection of reusable skills with create-skill-file guidance. Template and example approach.

### metaskills/skill-builder
Claude Code Agent Skills Builder — generates skills with correct structure.

### daymade/claude-code-skills
Skills marketplace with skill-creator, continue-claude-work, financial-data-collector.

### skillsmp.com (Agent Skills Marketplace)
Cross-platform skills marketplace — works with Claude Code, OpenAI Codex CLI, and other SKILL.md-compatible tools.

### travisvn/awesome-claude-skills
Curated list with documentation converters, Manus-style workflow patterns, and community resources.

## How cognee-skills Differs from Other Meta-Skills

| Aspect | Static meta-skills (Anthropic, YYH211, etc.) | cognee-skills |
|--------|----------------------------------------------|---------------|
| **What they create** | SKILL.md files (one-time generation) | Living skills in a knowledge graph |
| **Routing** | Claude's built-in LLM reasoning | Two-stage: vector search + learned `prefers` weights |
| **Quality signal** | None (user judges) | Every run scored 0.0-1.0 by evaluator LLM |
| **Self-repair** | None (user edits SKILL.md manually) | Full loop: inspect → preview → amendify → evaluate → rollback |
| **Memory** | Stateless per conversation | Graph-persistent: SkillRun, SkillInspection, SkillAmendment |
| **Audit trail** | Git history only | SkillChangeEvent nodes with temporal tracking |
| **Integration** | File-based only | SDK, CLI, MCP server, or file-based |
