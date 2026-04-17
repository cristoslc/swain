# Synthesis: SemanticWiki & Build-An-Agent Workshop vs. Swain

## What these projects are

SemanticWiki and Build-An-Agent Workshop both come from Dakota Kim (reasoning.software). SemanticWiki generates architecture docs from codebases using RAG and agent reasoning. Build-An-Agent Workshop scaffolds standalone agent CLIs from templates. Both occupy the same landscape as Swain: how humans and AI agents cooperate on software work.

## Overlaps

### Traceability

All three systems link claims to evidence. SemanticWiki links docs to `file:line` in source code. Swain links decisions to `artifact@commit` in git. Build-An-Agent Workshop links agent behavior to the five levers (memory, commands, skills, subagents, hooks) that shaped it.

The deepest overlap is SemanticWiki vs. Swain. Both treat docs as verifiable. SemanticWiki says architectural understanding should be queryable and linked to exact source locations. Swain says decisions must live in artifacts, not in prose or memory. Both want a chain from claim to ground truth.

The difference is what counts as ground truth. SemanticWiki anchors to source code. Swain anchors to decision records. Code changes constantly. `file:line` references rot. Decision records change less often, and when they do, the change is explicit.

Both detect the same problem: documentation diverged from reality. They repair it differently. SemanticWiki regenerates. Swain re-decides.

### The five levers

Build-An-Agent Workshop names the same levers Swain uses: memory, commands, skills, subagents, hooks. Both build on Claude Code's affordances. The divergence is what each does with them.

The workshop treats them as configurable blocks. You pick levers, configure them, and generate an agent. The operator has full control but no enforced discipline. Nothing stops you from generating an agent with unrestricted permissions.

Swain wraps the same levers in governance. AGENTS.md is a constitution that skills must read. Skills route through a dispatch table matching intent to handler. Hooks enforce readability thresholds and security checks. Phase transitions are gates requiring evidence before advancing.

The workshop asks: how do I build an agent? Swain asks: how do I keep an agent aligned? The workshop gives tools. Swain gives discipline.

### Verification

SemanticWiki has the most concrete verification. It defines four metrics: traceability precision, architectural coverage, regeneration stability, and link drift resilience. It treats doc generation as a measurable reliability problem. Its loop checks every source link, regenerates missing pages, and scores output.

Swain's verification is procedural. It checks whether a spec passed review, not whether it is accurate. It checks whether tests pass, not whether they cover the right things. It lacks quantitative quality signals on artifacts.

Build-An-Agent Workshop has the weakest verification. It delegates to the agent's permission system and trusts the operator. Its "not a silver bullet" disclaimer is honest but leaves a gap.

## Complementary possibilities

### SemanticWiki could give Swain measurable quality

Swain detects drift but doesn't measure artifact quality. SemanticWiki's metrics could apply to swain artifacts. A spec with `file:line` references could be checked the same way SemanticWiki checks its wiki. This would give Swain a quantitative quality signal, not just a procedural gate.

### The workshop could carry Swain's governance into generated agents

A swain governance template would produce agents that respect worktree isolation, readability thresholds, and the Intent -> Evidence loop by default. The workshop's multi-SDK posture could also help Swain identify which conventions are substrate-independent and which are Claude Code-specific.

### Swain could give SemanticWiki a decision layer

SemanticWiki generates docs from code. But architecture is the consequence of decisions. Swain's decision artifacts (specs, ADRs, epics) could serve as the intent layer for SemanticWiki's wiki. A swain-aware SemanticWiki could link wiki pages to the ADRs and specs motivating the architecture, not just the code.

### Together they form a traceability chain

The three systems cover different chain segments:

- Swain: decision -> artifact -> commit
- SemanticWiki: code -> wiki -> file:line
- Build-An-Agent Workshop: template -> agent -> levers

A unified model could link a spec's acceptance criteria (swain) through an architecture description (SemanticWiki) to the implementing code (SemanticWiki file:line). Neither system does this alone.

## Fundamental differences

### Generated vs. authored

SemanticWiki generates docs. The human points it at a codebase and reviews output. Swain expects the operator to author artifacts as part of deciding. These serve different phases. You author a spec before code exists. You generate a wiki after code exists. The tension is real but not contradictory. Generated docs go stale differently than authored docs. SemanticWiki handles this by regenerating. Swain handles it by re-deciding.

### Agent as tool vs. governed entity

The workshop treats agents as products you build and ship. Swain treats the agent as an entity that must be governed. The workshop asks what an agent can do. Swain asks whether the agent is doing what was decided. These are complementary questions producing different priorities. The workshop optimizes for capability. Swain optimizes for alignment.

### Deterministic vs. semantic retrieval

Swain finds artifacts by grep, glob, and manifest tags. SemanticWiki finds information by embedding similarity and hybrid search. Swain is deterministic. The same tag always finds the same artifact. SemanticWiki is recall-oriented. A query about "authentication" surfaces the JWT provider even if the file is named `token-service.ts`.

Swain chooses determinism because artifacts are ground truth. They must be findable by exact reference. SemanticWiki chooses recall because codebases are large and developers may not know the right name. Both choices are correct for their context. But trove search augmented by RAG could get recall without sacrificing determinism at the artifact level.

### Multi-agent substrate

The workshop generates agents for three SDKs (Anthropic, OpenAI, HuggingFace). Swain depends on Claude Code's specific affordances. This is a portability gap. Swain's governance model is substrate-independent in principle. It's markdown files in git. But skill routing, AGENTS.md parsing, and hook configuration are Claude Code-specific. To work across substrates, Swain needs to separate the essential from the incidental and port the essential parts.

## Gaps neither system fills

- **End-to-end traceability.** Swain traces decisions to commits. SemanticWiki traces docs to code lines. Nobody links a spec's acceptance criteria through architecture to the implementing function. You get decision -> commit or doc -> line. The middle is missing.
- **Quantitative artifact quality.** Swain measures process compliance. SemanticWiki measures doc accuracy. Nobody measures whether a spec accurately describes what was built.
- **Agent substrate portability.** Swain is Claude Code-specific. The workshop generates for three SDKs. Neither addresses how governance transfers across substrates.