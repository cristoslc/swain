# Synthesis: SemanticWiki vs. Swain

## The shared problem

Both systems reject stale documentation. Both want claims anchored to something verifiable. SemanticWiki anchors to source code. Swain anchors to decision records. This is the fundamental difference, and everything else follows from it.

## Ground truth: code vs. decisions

SemanticWiki's core thesis is that architectural understanding should be queryable, testable, and linked to exact source locations. Its ground truth is the current codebase. Every claim in a SemanticWiki wiki links to `file:line`. When the code changes, the claim either updates or breaks. Drift is detectable because the anchor moves.

Swain's ground truth is the decision record. Every claim in a swain artifact links to a commit in git. When the decision changes, the change is explicit — an ADR superseded, a spec phase-transitioned. The anchor moves deliberately, not accidentally.

This is not a symmetrical choice. Code changes constantly. A `file:line` reference is valid until the next refactor. Decision records change infrequently. A `spec@commit` reference is valid for the entire lifetime of that spec phase. SemanticWiki's traceability is precise but fragile. Swain's is coarser but more durable.

Both systems detect the same problem: documentation diverged from reality. They repair it differently. SemanticWiki regenerates. It re-runs the agent, re-indexes the codebase, and produces fresh output. Swain re-decides. It surfaces the divergence and asks the operator what to do about it. SemanticWiki treats drift as a freshness problem. Swain treats drift as an alignment problem.

## Verification: metrics vs. gates

SemanticWiki has four quantitative metrics for documentation quality. Traceability precision measures what percentage of claims resolve to valid source spans. Architectural coverage measures what percentage of core modules are represented. Regeneration stability measures similarity across repeated runs. Link drift resilience measures integrity after code edits.

Swain has no equivalent metrics. Its verification is procedural. The verification-before-completion skill runs tests before claiming done. Phase transitions require evidence. Reconciliation compares intent against observed reality. But Swain checks whether a spec passed review, not whether the spec is accurate. It checks whether tests pass, not whether they cover the right things. It checks process compliance, not output quality.

This is a gap. SemanticWiki's metrics could be adapted for swain artifacts. A spec with `file:line` references to implementation could be checked for traceability precision. Architectural coverage could be measured against a spec's stated scope. Regeneration stability could detect whether a spec drifts between sessions. Swain currently has no quantitative quality signal on its own artifacts.

## Deterministic vs. semantic retrieval

Swain finds artifacts by grep, glob, and manifest tags. The same tag always finds the same artifact. This is intentional. Artifacts are ground truth. They must be findable by exact reference. Troves have manifests with explicit tags. Specs reference troves by `trove:id@commit`. The chain is deterministic.

SemanticWiki finds information by embedding similarity and hybrid search. A query about "authentication" surfaces the JWT provider even if the file is named `token-service.ts`. This is recall-oriented. In a large codebase, the developer may not know the right name.

Both choices are correct for their context. Swain needs determinism because artifacts are cited by exact reference in other artifacts. A trove reference must resolve to the same content every time. SemanticWiki needs recall because codebases are large and developers often don't know where to look.

But the gap is real. Swain's grep-based trove search cannot find semantically related sources without an exact tag match. A trove about "real-time communication" won't surface in a search for "WebSocket alternatives" unless both tags are present. SemanticWiki's RAG pipeline could augment trove search to get recall without sacrificing determinism at the artifact level.

## Generated vs. authored documentation

SemanticWiki generates docs from code. The human reviews after the fact. Swain expects the operator to author artifacts as part of deciding. These serve different phases. You author a spec before code exists. You generate a wiki after code exists.

The tension is real. Generated docs go stale when code changes. SemanticWiki handles this by regenerating. Authored docs go stale when decisions change. Swain handles this by re-deciding. But there's a deeper tension: generated documentation reflects what the code does. Authored documentation reflects what the code should do. When these diverge, neither system alone can tell you why.

## Where they could integrate

### Swain as the decision layer for SemanticWiki

SemanticWiki generates architecture docs from code. But architecture is the consequence of decisions. A swain-aware SemanticWiki could link wiki pages to the ADRs and specs that motivated the architecture, not just to the code. This would close the gap between what the code does and why it does it.

### SemanticWiki as a swain skill

A `swain-wiki` skill could invoke SemanticWiki's `generate` command to refresh architecture docs from code. The output could be stamped into a trove for cross-referencing with specs and ADRs. This would give swain artifacts a code-level counterpart. The spec says what should exist. The wiki describes what does exist. Both are anchored to the same repository.

### Traceability metrics on swain artifacts

SemanticWiki's four metrics could be adapted for swain. Traceability precision could verify that a spec's implementation references resolve. Architectural coverage could verify that a spec's stated scope matches the actual module structure. Link drift resilience could detect when committed references no longer resolve. This would give Swain what it currently lacks: quantitative evidence that artifacts accurately describe reality.

### The missing middle

Swain traces decisions to commits. SemanticWiki traces documentation to code lines. Nobody links a spec's acceptance criteria through an architecture description to the implementing function. The full chain is: decision -> spec -> ADR -> architecture description -> module -> function -> line. You currently get decision -> commit (Swain) or doc -> line (SemanticWiki). The middle is missing. An integration that connected swain artifacts to SemanticWiki wiki pages, with both pointing to `file:line` references, would close this gap.

## Where they diverge

### Drift repair: regenerate vs. re-decide

This is the deepest architectural choice. SemanticWiki treats documentation as a cache that can be regenerated from source. Swain treats documentation as a decision record that must be explicitly updated. The cache model is fast but silent. It doesn't tell you what changed or why. The decision model is slow but explicit. It surfaces the divergence and asks the operator to choose.

Neither model is strictly better. A cache that regenerates without telling you what changed is a cache you can't trust. A decision record that never gets updated is a record that rots. The right answer depends on context. Use generated documentation for what the code does today. Use authored documentation for what the code should do tomorrow.

### Scope: codebase vs. project

SemanticWiki's scope is the codebase. It indexes files, extracts structure, and generates documentation about what exists. Swain's scope is the project. It captures decisions, tracks progress, and generates artifacts about what was decided and what remains.

A codebase is one form of evidence about a project, but not the only one. A project includes research, decisions, plans, and retrospectives — none of which exist in the code. SemanticWiki can tell you what the code does. Swain can tell you why it does it. Neither subsumes the other.

### Agent posture: autonomous vs. governed

SemanticWiki's agent runs autonomously. It explores the codebase, makes decisions about what to document, and produces output without asking. The operator reviews after the fact. This works because the output is documentation. If it's wrong, the cost is confusion, not malfunction.

Swain's agent is governed. It operates within constraints expressed in artifacts. It asks before acting on ambiguous signals. It verifies before claiming done. This works because the output is implementation. If it's wrong, the cost is a broken system. The difference in agent posture follows from the difference in output stakes.