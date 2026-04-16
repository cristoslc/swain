# Synthesis: SemanticWiki & Build-An-Agent Workshop vs. Swain

## Overview

SemanticWiki and Build-An-Agent Workshop are both projects by Dakota Kim (reasoning.software / MadWatch LLC). SemanticWiki is a CLI that makes architecture docs from codebases via RAG and agent reasoning. Build-An-Agent Workshop is a platform for building AI agent CLIs. Both use the Claude Agent SDK. This synthesis looks at where they overlap with, complement, and differ from Swain.

## Key Findings

### 1. Documentation as a generated artifact

SemanticWiki treats architecture docs as generated artifacts with `file:line` traceability to source code. Its core thesis: architectural understanding should be queryable, testable, and linked to exact source locations. This echoes Swain's Intent -> Execution -> Evidence -> Reconciliation loop. Both systems reject stale prose. The scope differs. SemanticWiki targets code-level docs (modules, data flows, call graphs). Swain targets project-level decision docs (specs, epics, ADRs). A SemanticWiki wiki and a Swain artifact graph serve different readers. One is for developers entering a codebase. The other is for the operator steering a project.

### 2. The five levers of control

Build-An-Agent Workshop names five control levers for Claude Code agents. They are Memory (CLAUDE.md), Slash Commands, Skills, Subagents, and Hooks. Swain uses the same substrate (AGENTS.md, skills/, .claude/commands/, hooks). The difference is governance. Swain wraps these levers in a governance layer. Artifacts on disk encode decisions. Skill routing enforces workflows. Phase transitions check alignment. Build-An-Agent Workshop gives you the levers as configurable blocks. It does not add a governance layer on top. Swain adds worktree isolation for implementation, phase gates for artifacts, readability thresholds, and the Intent -> Evidence loop as the organizing principle.

### 3. Agent scaffolding vs. agent governance

Build-An-Agent Workshop is an agent generator. It makes standalone agent CLIs from templates. Swain is a governance framework. It constrains an existing agent through conventions, artifacts, and skill routing. The workshop outputs new agents. Swain shapes how one agent works on one project. These are complementary. A workshop agent could run inside a swain-governed project. Swain conventions could be packaged as a workshop template.

### 4. RAG and semantic retrieval

SemanticWiki embeds codebases with FAISS + BGE-small. It provides hybrid search (BM25 + vector, RRF fusion). Swain does not ship this. Swain troves are markdown on disk. They are found by grep and glob, not by similarity. SemanticWiki's retrieval could power richer trove search. It could help find artifacts without exact keywords. But keeping a FAISS index alongside markdown is non-trivial. Swain trades recall for simplicity and determinism.

### 5. Source traceability: file:line vs. artifact@commit

Both systems link claims to evidence. The granularity differs. SemanticWiki traces docs to code lines (`src/auth/jwt.ts:23-67`). Swain traces decisions to artifact commits (`trove: websocket-vs-sse@abc1234`). A combined approach could link a spec's rationale through a trove to research sources, then to implementing code. That gives a full chain from decision to code.

### 6. Verification loops

SemanticWiki has a verification loop. It checks source-link integrity, regenerates missing pages, and measures traceability precision. It treats doc quality as a reliability problem with metrics: traceability precision, architectural coverage, regeneration stability, and link drift resilience. Swain's verification is phase-based. A spec must be reviewed before it becomes active. The verification-before-completion skill runs tests before claiming done. SemanticWiki's metrics are runtime quality signals. Swain's are lifecycle gates. Both matter. Both fail silently without enforcement.

### 7. Multi-SDK posture

Build-An-Agent Workshop supports Anthropic, OpenAI, and HuggingFace SDKs. Swain depends on Claude Code's affordances (CLAUDE.md, .claude/skills, hooks via settings.json). This is a gap. Swain's governance model is portable in principle—it uses markdown artifacts and git conventions. But skill routing and hooks are Claude Code-specific. If the agent substrate changes, conventions survive. The integration layer needs porting.

## Points of Agreement

- Documentation and decisions should be verifiable and linked to their sources.
- Agent behavior should be shaped by explicit control levers, not just prompts.
- Verification should be automated and repeatable.
- The operator must stay in the loop for high-risk or ambiguous decisions.
- Local-first and offline-capable tooling is a worthwhile design goal.

## Points of Disagreement

- **Governance vs. tools**: Build-An-Agent Workshop offers control levers but leaves governance to the user. Swain imposes governance on top of the same levers.
- **Generated vs. authored docs**: SemanticWiki generates docs from code. Swain expects docs to be authored as part of the decision process. These serve different phases of a project's lifecycle. They are not contradictory.
- **Determinism vs. retrieval**: Swain prefers deterministic search (grep, tags, manifests). SemanticWiki invests in semantic retrieval (embeddings, hybrid search). The tradeoff is reproducibility vs. recall.
- **Scope of traceability**: SemanticWiki traces to code lines. Swain traces to artifact commits. Each is narrow in the other's dimension.

## Gaps

- Neither system provides a full chain from project decision through research sources to implementing code. A combined model (`artifact@commit -> trove@hash -> source:file:line`) would close this gap.
- Build-An-Agent Workshop's multi-SDK support highlights Swain's single-substrate dependency. A portability assessment would clarify which Swain conventions transfer and which are Claude Code-specific.
- SemanticWiki has evaluation metrics (traceability precision, regeneration stability) with no Swain equivalent. Swain measures process compliance (are artifacts in the right phase?), not output quality (are artifacts accurate?).

## Complementary Integration Points

1. **SemanticWiki as a swain skill**: A `swain-wiki` skill could call SemanticWiki's `generate` command to refresh architecture docs from code. It could then stamp the wiki into a trove for cross-referencing with specs and ADRs.
2. **Build-An-Agent as a swain template**: A swain governance template for Build-An-Agent could output agents that respect worktree isolation, readability thresholds, and the Intent -> Evidence loop.
3. **Trove search augmentation**: SemanticWiki's RAG pipeline could be offered as an optional search backend for troves. It would fall back to grep when not available.
4. **Traceability chain stitching**: Swain's `trove: id@commit` references could include SemanticWiki-style `file:line` links. This would create a unified traceability chain.