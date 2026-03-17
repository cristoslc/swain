# Context Fork in Claude Code -- Synthesis

## Key Findings

Context fork is a Claude Code skill frontmatter directive (`context: fork`) that runs a skill in an isolated sub-agent context with separate conversation history. This is a first-party mechanism for agent call optimization: the forked context gets independent history and tool access, preventing skill execution details from polluting the main conversation thread.

### Mechanism

- Declared in skill frontmatter alongside `name` and `description`
- Optional `agent` field selects the sub-agent type (e.g., `Explore`)
- Forked context has independent conversation history and tool access
- Results return to the main thread without the intermediate execution steps

### Relevance to Model Routing and Context Optimization

Context fork directly intersects with two completed swain initiatives:

1. **Context footprint reduction (EPIC-006):** Context fork is an alternative lever for managing context pressure. Rather than compressing skill content (the strategy swain pursued), forking isolates execution entirely so the main thread never sees the intermediate tokens. The two approaches are complementary -- compressed skills that also fork would have minimal footprint impact.

2. **Model routing (EPIC-007):** The `agent` field in context fork frontmatter hints at per-skill agent type selection. This is a runtime-native mechanism for what SPIKE-013 found no runtime supports via instruction text: directing a skill to run on a different agent (and potentially different model). If Claude Code exposes model selection per forked context, this becomes the implementation path for SPIKE-014's per-operation tier routing.

### Points of Agreement with Existing Research

- Aligns with SPIKE-013's finding that model/agent routing is out-of-band (config/frontmatter), not in instruction text
- Validates SPIKE-011's Strategy C (conditional loading via splitting) -- context fork achieves similar isolation without skill proliferation

### Gaps

- No documentation on whether the forked context can specify a different model (e.g., Haiku for lightweight skills)
- No clarity on whether `context: fork` is composable with other frontmatter fields beyond `agent`
- No performance data on fork overhead vs. inline execution
- Single source -- would benefit from extension with Claude Code source code analysis or official documentation
