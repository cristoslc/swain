# Synthesis: Garry Tan's Brutalist Personal AI Tools

## Key findings

Garry Tan (YC President & CEO) advocates a specific architectural philosophy for AI-augmented work: **thin harness, fat skills**. This philosophy manifests concretely in two open source projects — GBrain (personal knowledge engine) and GStack (software factory) — and is articulated in his "Thin Harness, Fat Skills" article.

### Thin harness, fat skills architecture

The central thesis across all three sources is that the multiplier in AI productivity isn't smarter models but better **architecture**. The "2x people and the 100x people are using the same models" (garrytan-thin-harness-article). The architecture has three layers:

1. **Fat skills** (top): Markdown procedures encoding judgment, process, and domain knowledge. This is where 90% of the value lives.
2. **Thin harness** (middle): ~200 lines of code running the LLM in a loop, managing files and context, enforcing safety.
3. **Deterministic application** (bottom): SQL queries, compiled tools, arithmetic — reliable execution with same-input-same-output guarantees.

The principle is directional: push intelligence up into skills, push execution down into deterministic tooling, keep the harness thin. Every model improvement automatically improves every skill; every deterministic step stays perfectly reliable.

### Five architectural definitions

The article defines five interlocking concepts:

- **Skill files**: Reusable markdown documents that work like method calls — same procedure, different parameters, radically different capabilities. Not prompt engineering but software design using markdown as the programming language.
- **The harness**: The thin wrapper running the model. Anti-pattern is fat harness (40+ tool definitions, slow MCP round-trips). Goal is purpose-built fast narrow tools.
- **Resolvers**: Routing tables for context — load the right document at the right moment. The skill description IS the resolver in Claude Code. Tan's own CLAUDE.md was 20,000 lines before he cut it to 200 lines of pointers.
- **Latent vs. deterministic**: The most common mistake is putting the wrong work on the wrong side. LLMs handle judgment (seating 8 people); deterministic code handles combinatorial optimization (seating 800). Never confuse them.
- **Diarization**: The step that makes AI useful for knowledge work — reading everything about a subject and writing a structured profile. No SQL query or RAG pipeline produces this. The model must read, hold contradictions, and synthesize structured intelligence.

### GBrain: personal knowledge compounding

GBrain implements the "brain-agent loop" — read the brain before responding, write after learning, sync for next query. The "compounding thesis" is that every cycle adds knowledge. The agent runs while you sleep (dream cycle), and you wake up with a smarter brain.

Key architectural features: compiled truth + timeline knowledge model, hybrid search (RRF fusion of vector + keyword + multi-query expansion), PGLite default (no server), Supabase for production scale, 30 MCP tools, integrations pipeline (voice, email, calendar, Twitter, meetings).

### GStack: structured sprint process

GStack provides 23 specialist skills and 8 power tools that compose into a sprint: Think → Plan → Build → Review → Test → Ship → Reflect. Each skill feeds into the next. The sprint structure is what makes 10-15 parallel agents work — without process, parallel agents produce chaos.

The claimed output: 600,000+ lines of production code in 60 days, 10-20K lines per day, part-time while running YC. 70.8k GitHub stars.

### Skills as permanent upgrades

The "no one-off work" discipline (garrytan-thin-harness-article): if you do something twice, you failed. Codify it into a skill file. Every skill is a permanent upgrade that never degrades, runs at 3 AM, and instantly benefits from every model improvement. The learning loop: retrieve → read → diarize → count → synthesize, then survey → investigate → diarize → rewrite the skill.

## Points of agreement

- All three sources agree on the primacy of architecture over model intelligence.
- GBrain and GStack both embody the thin harness principle: GBrain is a retrieval layer with fat skill files on top; GStack is a thin harness (Claude Code) with 23 specialist skill docs.
- The "compounding thesis" of GBrain and the "permanent upgrades" thesis of the article are the same idea expressed at different scales: knowledge/skills compound over time and are never lost.

## Points of disagreement or tension

- GBrain uses 40+ MCP tools (30 listed plus auth/management), which appears to contradict the article's warning against "40+ tool definitions eating half the context window." However, GBrain's MCP tools are narrow and deterministic (get_page, search, embed), not god-tools — this is the thin harness principle applied correctly.
- The article says the harness should be ~200 lines of code, but GStack's Claude Code integration is the harness, not GStack itself. GStack is entirely fat skills (markdown files) — consistent with the architecture.

## Gaps

- No independent verification of the 100x productivity claims or 600K LOC output figures.
- The article describes a YC Startup School matching system (6,000 founders) as a future application — not yet deployed for validation.
- GBrain's "dream cycle" (nightly enrichment/consolidation) is described but not documented with benchmark results.
- No discussion of failure modes: when do skill files go wrong? What happens when the resolver loads the wrong context?
- No cost analysis for running these stacks at scale (API costs for 10-15 parallel agents).
- Adjacent troves (agent-memory-systems, cog-cognitive-architecture) cover general agent memory architectures but not this specific brutalist/compounding philosophy.