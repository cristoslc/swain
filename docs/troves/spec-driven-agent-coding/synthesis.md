# Synthesis: Spec-Driven Agent Coding

**Trove:** `spec-driven-agent-coding`
**Sources:** 1
**Last updated:** 2026-05-18

## Key Findings

### The Slop Problem

Joshua Levy's article frames "slop" as a natural law for LLM-generated code — not just low quality, but an entropic tendency toward mediocre patterns that accelerate over time. Agents gravitate toward the center of their training distribution unless structures actively push them toward clarity and simplicity. Poor code begets more poor code, as subsequent agents imitate the questionable patterns they encounter.

Common slop patterns include: duplicating types, choosing outdated libraries, skipping tests, writing useless test clutter, hallucinating API features, compounding design mistakes, and blindly confirming incorrect human assumptions.

### The Spec-Driven Solution

The core countermeasure is specification-driven development with strict process discipline. The workflow breaks development into phases — planning, implementation, and validation — and enforces coding rules at commit time. Agents can tolerate far more process overhead than human engineers, making the investment in structure worthwhile.

### Doc Taxonomy and Lifecycle

Two document categories serve different purposes:

- **Long-lived docs** — research briefs, architecture docs, shortcut docs — provide persistent context that agents reference repeatedly.
- **Shorter-lived specs** — plan specs, implementation specs, validation specs, bugfix specs — are transient, focusing a specific effort and referencing long-lived docs for background.

The directory layout separates shared general docs (synced across repos via `speculate update`) from project-specific docs. Completed specs are archived to avoid clutter while preserving history.

### The 95/90/10 Rule

- 95% of code was agent-written (with iterative human feedback).
- 90% of specs and architecture docs were agent-written (with heavier human editing).
- Only 10% of agent rules and process docs were agent-written. Rules must be carefully authored by humans — e.g., banning optional parameters in TypeScript because they cause subtle refactoring bugs.

### Why Specs Work for Agents

Specs force thinking in steps for both human and agent, manage context efficiently, allow multi-model review (have Opus write, then GPT and Gemini critique), and consolidate internal and external references to prevent wheel-reinvention.

### The Testing Trinity

The single greatest accelerator is exhaustive, maintainable, token-friendly testing. Three strategies make this possible: CLI-first architectures where everything runs without a browser, mockable APIs and databases for integration tests, and golden tests that serialize stable execution traces into version-controlled session files that are diff-able.

### Limitations

Spec-driven development works best for product/full-stack engineering. Algorithmic, infrastructure, and ML engineering still benefit more from iterative hand-coding. It requires senior engineering judgment to correct agents during spec writing and code review.

## Points of Agreement with Related Troves

- Aligns with `slop-creep` trove on the entropic nature of LLM code quality decay.
- Aligns with `agentic-coding-dual-modes` on agent tolerance for process overhead.
- Complements `vibe-coding-practitioner-experience` by offering a structured alternative to casual vibe coding.

## Gaps

- Single-source trove. Would benefit from sources on beads integration, alternative spec formats, and comparisons with other structured agent workflows.
- No quantitative metrics on defect rates, velocity, or cost comparisons with human-only or hybrid development.
- Limited coverage of multi-agent coordination beyond multi-model spec review.
