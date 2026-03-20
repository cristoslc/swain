# Design Staleness & Drift — Synthesis

## Key Findings

### 1. DDRs are NOT an established pattern distinct from ADRs

The "Design Decision Record" (DDR) format that exists (Well-Architected Guide) is structurally identical to ADRs — same fields (Context, Decision, Alternatives, Consequences, Status), same lifecycle (Proposed → Accepted → Superseded). Microsoft's Engineering Playbook explicitly recommends using ADRs for *all* decisions including design decisions, with no separate DDR type. The academic literature uses the term "Design Rationale" (DR) rather than DDR, and has proposed many frameworks (IBIS, DRL, QOC, SEURAT, DRed) — none of which achieved widespread adoption due to capture overhead.

**Implication:** Creating a DDR artifact type would duplicate ADR with a different name. The right move is to use ADRs for design decisions and capture rationale within the DESIGN artifact itself.

### 2. Design drift is a well-documented, distinct problem from decision rationale

Drift is the *slow divergence between intended patterns and what ships*. It's caused by:
- Translation gaps (mockup → code)
- Variant sprawl without lifecycle management
- Local optimization overwhelming global vision
- Entropy (order requires energy; drift is the default)

This is a different problem from "recording why we chose rounded corners." Drift detection asks "does the app still match the design?" — not "why did we pick this design?"

### 3. Industry approaches split into two categories

**A. Code-level drift detection** (automated, precise, narrow scope):
- drift-guard: snapshots design tokens + DOM structure, checks for changes via CLI
- Buoy: PR-level drift detection for hardcoded colors, token violations, rogue components
- Bridgy: Figma→code sync enforcement
- Chromatic: visual regression testing in CI

**B. Process-level drift prevention** (governance, broad scope):
- Component lifecycle: Propose → Review → Build → Document → Release → Measure → Deprecate
- Exception tracking with expiry dates
- Monthly drift review rituals
- "Encode intent as constraints" — design tokens as enforceable rules, not just documentation
- Code-first design: Storybook as source of truth, synced to Figma

### 4. The "intent vs. current state" gap is recognized but unsolved at the document level

Multiple sources note the distinction between *design intent* and *design state*:
- Hardware design: "design readiness stages represent intent rather than design state"
- Productic: "encode intent as constraints" so intent survives independently of documentation
- UXPin: governance playbooks track *intended patterns* vs. *what ships*

No source describes a document-level solution to tracking how a *design document* diverges from *running code*. The industry has converged on making code the source of truth and treating design documents as upstream intent — not authoritative records of current state.

## Points of Agreement

- **ADRs/DDRs are the same thing** — no source argues for a structurally distinct DDR format
- **Drift is inevitable without active maintenance** — entropy is the default
- **The biggest drift driver is the translation gap** — any step where humans reinterpret intent introduces drift
- **Code should be the source of truth** when design documents and code diverge
- **Automated tooling catches code-level drift** but nobody has solved document-level drift detection

## Points of Disagreement

- **Code-first vs. design-first**: Powell and UXPin advocate code-first (Storybook → Figma); some design teams resist this as limiting creative freedom. The pragmatic middle ground: code is the source of truth for *current state*, while design documents capture *intent and vision*.
- **Governance weight**: UXPin recommends heavy governance (RACI, monthly rituals, exception tracking); drift-guard takes a lightweight CLI approach. These aren't contradictory — they operate at different scales.

## Gaps

1. **No existing pattern for document-to-code drift detection** — all tools work code-to-code (snapshot vs. current) or design-tool-to-code (Figma vs. Storybook). Nobody checks "does this markdown design document still accurately describe what the app does?"
2. **No framework for preserving original design vision alongside evolving design** — sources discuss versioning design *systems* (component libraries) but not versioning design *documents* that track intent evolution
3. **TRAIN-style commit-pinned staleness for DESIGNs is unexplored** — swain's TRAIN pattern (pin to a commit, detect when documented artifacts change) has no equivalent in the literature for design artifacts, but the mechanism transfers directly
