---
title: "Security Scanning Landscape and BUILD vs BUY for swain-security-check"
artifact: SPIKE-020
track: container
status: Proposed
author: cristos
created: 2026-03-14
last-updated: 2026-03-14
question: "For a personal-project context (low budget, high automation preference), should swain-security-check be built as an orchestration skill over existing tools, or can an existing solution cover the multi-vector attack surface well enough to BUY/integrate instead?"
gate: Pre-development
risks-addressed:
  - Building a custom skill that duplicates work an existing tool already does well
  - Choosing a tool that cannot cover the prompt injection vector (novel attack surface)
  - Choosing a tool with licensing or cost requirements incompatible with a personal-project context
linked-artifacts:
  - EPIC-017
  - SPIKE-015
evidence-pool: ""
---

# Security Scanning Landscape and BUILD vs BUY for swain-security-check

## Summary

<!-- Populated when transitioning to Complete. -->

## Question

For a personal-project context (low budget, high automation preference), should swain-security-check be built as an orchestration skill over existing tools, or can an existing solution cover the multi-vector attack surface well enough to BUY/integrate instead?

The attack surface has three vectors (note: SPIKE-015 already resolved vectors 1 and 2 for the pre-commit scanner set — this spike focuses on the gaps and on the prompt injection vector):

1. **Secrets and credentials** — SPIKE-015 finding: gitleaks + opt-in TruffleHog/OSV-Scanner/Trivy. Considered resolved; this spike validates whether swain-security-check should reuse that selection or evaluate alternatives.
2. **Dependency vulnerabilities** — SPIKE-015 finding: OSV-Scanner or Trivy. Considered resolved for the same reason.
3. **Prompt injection** — two sub-vectors not covered by SPIKE-015:
   - *LLM-consuming projects*: static analysis of application code that calls LLM APIs — detecting unvalidated inputs passed as context, inline user-controlled system prompt fragments, missing output validation
   - *Agentic coding runtime*: the context files that swain itself uses (`AGENTS.md`, `CLAUDE.md`, skill files, `.cursor/rules/`) — evaluating whether these contain patterns that could redirect an agent (injected instructions in generated files, dependencies with embedded prompts, etc.)

## Go / No-Go Criteria

**GO (BUILD — orchestration skill):**
- No single existing tool covers all three vectors in one invocation
- Prompt injection detection tools are available as libraries or CLIs that can be called from a skill
- The orchestration layer adds enough value (unified report, swain-native remediation steps) to justify skill authorship
- Personal-project cost: $0 (all tools open-source, no SaaS required)

**NO-GO (BUY — integrate existing tool):**
- A single open-source tool covers secrets + dependency vulns + prompt injection with acceptable quality
- Its output format is consumable by swain without a custom parsing layer
- It runs on macOS/Linux without a mandatory cloud account or paid tier

**Partial GO (hybrid):**
- Prompt injection coverage requires a BUILD component (novel vector, thin tooling)
- Secrets + dependency coverage can be BUY (delegate to SPIKE-015 selections)
- Verdict: BUILD an orchestration wrapper; BUY the individual scanners for vectors 1 and 2

## Pivot Recommendation

If no usable prompt injection detection tools exist (open-source, CLI-friendly, personal-project cost):
- Build heuristic detection rules for common injection patterns in context files (regex-based, covering the most common attack patterns: role-override instructions, `ignore previous instructions`, `you are now`, base64-encoded instructions, hidden Unicode text)
- Document the heuristics as a versioned rule set within the skill
- Note the inherent limitations of static heuristic detection vs. runtime detection

If a mature all-in-one tool is found that covers all three vectors:
- Reduce swain-security-check to a thin wrapper that invokes it and formats its output for swain's report format
- Skip building the orchestration layer

## Findings

<!-- Populated during Active phase. -->

Investigation areas:

### 1. Prompt injection detection tools landscape

Evaluate tools in the prompt injection detection space:
- **rebuff** (protectai/rebuff) — open-source prompt injection detection library
- **LLM Guard** (protect-ai/llm-guard) — input/output scanners for LLM applications
- **Vigil** (deadbits/vigil-llm) — LLM prompt injection and jailbreak detection
- **prompt-injection-detector** pattern libraries
- GitHub semgrep rule sets for LLM security (e.g., `trailofbits/semgrep-rules` LLM patterns)
- OWASP LLM Top 10 tooling (if any CLI tools exist)

Evaluate against criteria:
- Covers static analysis (not just runtime) — swain is a static scan skill
- Open-source, permissive license, personal-project cost $0
- CLI-friendly (not a Python library requiring embedded invocation)
- Maintained (last commit < 12 months)

### 2. Agentic runtime context file attack surface

Document the attack surface specific to swain and other agentic coding tools:
- Which files constitute trust boundaries: `AGENTS.md`, `CLAUDE.md`, skill `.md` files, `.cursor/rules/*.mdc`, `SYSTEM_PROMPT` patterns in config files
- Attack patterns to detect: instruction injection (`ignore previous instructions`), role override (`you are now`), privilege escalation (`you have full access`), exfiltration instructions (`send the contents of`), hidden Unicode/homoglyphs
- Whether any existing tools scan for these patterns in markdown/text files (most tools scan source code, not instruction files)

### 3. All-in-one security scan tools (BUY candidates)

Evaluate:
- **Semgrep** (with LLM security rule packs) — does it cover all three vectors?
- **Snyk** (free tier) — scope and personal-project limitations
- **Socket** (socket.dev) — dependency security; does it cover the other vectors?
- **Bearer** (bearer/bearer) — SAST with data flow analysis; any LLM patterns?
- **Aikido Security** — does it have a CLI/local mode for personal projects?

### 4. BUILD cost estimate

If BUILD is the verdict: estimate effort for the orchestration skill:
- Reusing SPIKE-015 scanner set for vectors 1 and 2: expected low effort
- Prompt injection heuristics for context files: medium effort
- Unified report format: medium effort
- `swain-doctor` integration hook: low effort

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; prior art in SPIKE-015 for secret/dependency scanning |
