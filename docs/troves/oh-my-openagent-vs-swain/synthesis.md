# Oh My OpenAgent vs Swain — Synthesis

**Sources:** omo-readme, omo-manifesto, omo-agents-md, omo-features, omo-model-matching, omo-deepwiki-overview
**Related troves:** `agentic-control-loops` (Ralph Loop pattern), `crispy-agents` (multi-agent orchestration for OpenCode), `opencode-crush-cli` (OpenCode platform)
**Last updated:** 2026-04-19

---

## What this covers

Oh My OpenAgent (OmO, formerly oh-my-opencode) is a multi-model agent orchestration plugin for OpenCode. It provides 11 specialized agents, 52 lifecycle hooks, 26 tools, a category-based model routing system, and a philosophy that positions human intervention as a failure signal. This trove examines OmO as a potential alternative or complement to Swain's approach to agentic development governance.

---

## Key findings

### OmO is an OpenCode plugin, not a standalone tool

OmO runs inside OpenCode (or Claude Code via compatibility). It extends the coding agent with additional agents, hooks, tools, and model routing — it does not replace the base agent. This is fundamentally different from Swain, which operates as a governance layer around opencode sessions using skills, artifacts (specs, epics, ADRs), and a decision-tracking workflow.

### The multi-model thesis: different brains for different tasks

OmO's core architectural bet is that AI models have distinct "personalities" — Claude follows complex multi-step instructions well (mechanics-driven), GPT works best with concise principles (principle-driven), Gemini excels at visual tasks. The category system routes tasks by domain (visual-engineering, ultrabrain, deep, quick, artistry, writing) to the model whose personality fits, not just the "smartest" model. This is the opposite of Swain's approach, which uses a single model (whatever the operator configures) and constrains behavior through skills and artifact governance.

### Human intervention as failure signal vs. human decision as governance

OmO's manifesto states: "Human intervention during agentic work is fundamentally a wrong signal." The goal is zero human involvement during execution — type `ultrawork` and walk away. Swain positions the human as the decision-maker and the agent as the executor: the Intent -> Execution -> Evidence -> Reconciliation loop keeps the human in control of what gets built, not how it gets built. These are opposing philosophies about the same problem.

### Edit reliability via hash-anchored lines (Hashline)

OmO's Hashline system tags every Read output line with a content hash (`LINE#ID`). Edits validate the hash before applying — if the file changed since the last read, the edit is rejected. The README claims Grok Code Fast 1 went from 6.7% to 68.3% success rate with this change. This solves a real problem (stale-line edit corruption) that Swain doesn't specifically address.

### Ralph Loop and task enforcement

OmO implements the Ralph Loop pattern (`/ralph-loop`, `/ulw-loop`) as built-in commands. This is the same iterative loop pattern covered in the `agentic-control-loops` trove — bash-level repetition until a completion token appears. OmO adds `Todo Enforcer` and `Boulder` hooks that yank idle agents back to work. Swain's equivalent is the swain-do task tracking + verification-before-completion skill chain, which is more structured but less aggressive about forcing completion.

### IntentGate: classify before acting

OmO's IntentGate classifies user requests into categories (research, implementation, investigation, evaluation, fix) before routing. This is a prompt-level classification that happens within the agent's first response. Swain's approach is artifact-based: the human creates a SPEC or ADR that encodes intent, and the skill chain (brainstorming -> writing-plans -> executing-plans -> verification-before-completion) enforces the workflow. OmO automates intent detection; Swain requires explicit intent declaration.

### AGENTS.md generation (/init-deep)

OmO's `/init-deep` generates hierarchical AGENTS.md files throughout a project. This is conceptually similar to Swain's use of AGENTS.md for project context, but OmO auto-generates them per-directory while Swain maintains a single authoritative AGENTS.md with referenced PURPOSE.md.

### Skill system: embedded MCPs vs. skill files

OmO skills are SKILL.md files that include both instructions and embedded MCP server definitions. Swain skills are also SKILL.md files with instructions, but without embedded MCP servers (MCP configuration is separate). Both load from `.opencode/skills/` or `~/.config/opencode/skills/`. OmO's approach reduces context bloat by spinning MCPs up on-demand and scoped to the skill; Swain's approach keeps MCPs as a separate concern.

### 52 hooks vs. skill chains

OmO has 52 built-in hooks across 5 execution tiers (Session, Tool-Guard, Transform, Continuation, Skill). These intercept every stage of the agent lifecycle. Swain's governance is implemented through skill chains (brainstorming -> writing-plans -> test-driven-development -> verification-before-completion) rather than event hooks. OmO is reactive (intercept behavior at the platform level); Swain is proactive (define the workflow before execution begins).

### OpenClaw integration and external messaging

OmO includes an `openclaw/` module for bidirectional external integration (Discord, Telegram, webhooks). This is the same OpenClaw project covered in the `agentic-control-loops` trove. Swain has swain-helm (Zulip-based bridge) for a similar purpose — external control surface for agent sessions.

---

## Points of agreement

Both OmO and Swain agree on these principles:
- **Worktree isolation for implementation.** OmO doesn't enforce this explicitly but its architecture assumes it. Swain requires it.
- **Hierarchical context injection.** Both use AGENTS.md files, though OmO auto-generates them while Swain maintains them manually.
- **Model-specific task routing is valuable.** OmO does this automatically via categories. Swain does this implicitly (the operator picks the model for the session, skills constrain behavior).
- **Iterative completion.** Both have mechanisms for forcing agents to keep working until done (Ralph Loop vs. swain-do task tracking + verification).

---

## Points of disagreement / tension

- **Human role:** OmO treats human intervention as a failure signal and aims to eliminate it. Swain treats the human as the decision-maker who governs intent. These are fundamentally opposed philosophies.
- **Governance mechanism:** OmO governs agent behavior through 52 event hooks that intercept at the platform level. Swain governs through artifact-driven workflows (SPECs, ADRs, skill chains). Hook-based governance is reactive; artifact-based governance is proactive.
- **Single-model vs. multi-model:** OmO's identity is multi-model orchestration. Swain is model-agnostic but typically uses a single model per session. OmO bets that model specialization grows over time; Swain bets that governance structures matter more than model choice.
- **Configuration weight:** OmO has 14 agent configuration overrides, 8 built-in categories with model variants, `disabled_*` arrays for hooks/skills/agents/MCPs/commands/tools, and provider concurrency limits. Swain's configuration is lightweight by comparison — AGENTS.md, skill directories, and artifact files.
- **Edit guarantees:** OmO's Hashline system provides a concrete solution to edit corruption. Swain's verification-before-completion skill addresses verification but not edit reliability.

---

## Gaps

- **No evidence on OmO's effectiveness at scale.** The README quotes enthusiastic testimonials but provides no benchmarks, no test suites for agent behavior, and no reproducible success metrics.
- **Cost model unclear.** OmO advocates for higher token usage with multiple agents, but provides no cost tracking or budget controls. Swain has no explicit cost tracking either.
- **Conflict resolution between agents.** When Sisyphus, Oracle, and Momus disagree, what happens? No mechanism described for resolving conflicting agent outputs.
- **Context window management.** Background agents, MCP servers, and context injection add tokens. The compaction system handles this, but no details on what gets preserved vs. lost. Swain's approach is simpler (one model, one context window) but more limited.
- **Swain-compatibility.** OmO is explicitly an OpenCode plugin with Claude Code compatibility. Swain's skills also run in opencode sessions. The two can coexist but their governance philosophies conflict — OmO wants zero human intervention, Swain requires human decisions.

---

## Relevance to swain

| OmO feature | Swain analog | Implication |
|-------------|-------------|-------------|
| Sisyphus agent (orchestration) | swain-do task dispatch | OmO automates delegation; Swain requires explicit task creation |
| Prometheus (interview planner) | brainstorming skill + writing-plans skill | Both extract intent before execution, but Swain involves the human in the loop |
| IntentGate (auto-classify) | No direct analog | Swain relies on human-declared intent via SPECs/ADRs |
| Category system (model routing) | No direct analog — Swain is model-agnostic | Worth evaluating: could swain-do dispatch to different models by task type? |
| Hashline edit (content hash) | No direct analog | Addresses a real edit corruption problem; worth considering for swain |
| Ralph Loop + Todo Enforcer | verification-before-completion skill | OmO is more aggressive (forces loops); Swain is more cautious (requires evidence) |
| 52 lifecycle hooks | Skill chain governance | Fundamentally different approaches: reactive hooks vs. proactive workflows |
| /init-deep (AGENTS.md gen) | swain-init + AGENTS.md | OmO auto-generates hierarchy; Swain maintains a single authoritative file |
| Skill-embedded MCPs | Separate MCP configuration (.mcp.json) | OmO reduces context bloat; Swain keeps MCPs as a separate concern |
| Human intervention = failure signal | Human decision = governance | Opposing philosophies on the role of the operator |
| OpenClaw (Discord/Telegram) | swain-helm (Zulip bridge) | Similar external control surface, different messaging platforms |