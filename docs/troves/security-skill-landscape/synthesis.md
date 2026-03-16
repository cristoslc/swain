# Synthesis: Security Skill Landscape for Claude Code

**Pool:** security-skill-landscape
**Created:** 2026-03-14
**Question:** Is there a security skill worth pulling into swain — analogous to obra/superpowers (dev workflow) or impeccable.style (frontend design)?

---

## Key Findings

### 1. The baseline is already built-in

Claude Code ships `/security-review` out of the box (`anthropics/claude-code-security-review` — source 004). It covers injection, auth/authz, crypto, data exposure, XSS, deserialization, supply chain, and more. It has thoughtful false-positive filtering and is customizable via `.claude/commands/security-review.md`. For swain's primary use case — reviewing changes before commit — this is already present and sufficient at the surface level.

**Implication:** The question isn't "is there a built-in?", it's "is there a skill that *meaningfully extends* the built-in, the way superpowers extended Claude's base capabilities?"

### 2. Trail of Bits is the closest true analogue to impeccable.style

`trailofbits/skills` (source 001) is:
- From a professional security firm with real audit/research credentials
- A plugin marketplace with 20+ specialized security plugins
- Covers static analysis (CodeQL, Semgrep, SARIF), variant analysis, supply chain, malware, mobile, smart contracts, cryptographic side-channels
- Has a Trophy Case of real bugs found using the skills
- Licensed CC-BY-SA-4.0
- Installable via: `/plugin marketplace add trailofbits/skills`

**The analogy holds well:** impeccable.style brought professional design-system taste to frontend work. Trail of Bits brings professional security-firm methodology to code auditing. The skills are modular — you pick the relevant plugins (`static-analysis`, `differential-review`, `sharp-edges`, etc.) rather than loading everything.

**However:** Trail of Bits skills are heavily oriented toward security *researchers* and *auditors*, not everyday developers. Skills like `variant-analysis`, `yara-authoring`, `spec-to-code-compliance`, and `constant-time-analysis` are specialized for security professionals, not general development workflow. The fit for swain (which is a developer-workflow/documentation tool) is narrower than the full marketplace suggests.

**Most relevant Trail of Bits plugins for swain's use case:**
- `differential-review` — security-focused code diff review (complements built-in `/security-review`)
- `sharp-edges` — identifies error-prone APIs and dangerous configurations during dev
- `insecure-defaults` — detects hardcoded credentials, fail-open patterns
- `supply-chain-risk-auditor` — dependency audit
- `fp-check` — systematic false positive verification (useful when `/security-review` flags something)

### 3. OWASP Security Skill fills a guidance gap

`agamm/claude-code-owasp` (source 002) is complementary to, not a replacement for, the built-in review. Its value:
- Activates *proactively during coding*, not just at review time
- Provides language-specific security quirks for 20+ languages
- Covers ASVS 5.0 verification requirements (structured checklists)
- Uniquely covers **Agentic AI security (ASI01-ASI10)** — relevant for swain since swain itself is agent infrastructure

The built-in `/security-review` looks at code after it's written. `owasp-security` is meant to inform Claude while writing. These are different layers.

**Fit for swain:** Good alignment with swain's philosophy of embedding context early (like how superpowers embeds brainstorming before coding). The agentic AI security section is directly relevant to swain's domain.

### 4. VibeSec is lower signal

`BehiSecc/VibeSec-Skill` (source 003) self-describes 60-70% coverage. It's written from a bug-bounty perspective and is useful, but:
- Lighter-weight than Trail of Bits or OWASP skill
- Has an upsell to a commercial `vibesec.sh` tier
- Overlaps heavily with both the built-in `/security-review` and the OWASP skill
- Community-maintained without the institutional backing of Trail of Bits or Anthropic

**Fit for swain:** Low. Covered by better options.

### 5. obra/defense-in-depth is minimal

Already present via superpowers inheritance. From search snippets: "Implement multi-layered testing and security best practices." It's a lightweight integration of security thinking into the TDD/testing workflow, not a dedicated security capability. Not a standalone addition worth pulling.

---

## Points of Agreement

- The `/security-review` built-in is the floor, not the ceiling
- Trail of Bits is universally cited as the most authoritative community security skill library
- Modular plugin installation is preferred over monolithic "security SKILL.md" files
- Security skills split into two distinct modes: *proactive* (guide writing) vs *reactive* (review after)

## Points of Disagreement

- Whether the audience matters: Trail of Bits skills are auditor-grade, which is overkill for routine development but appropriate for security-conscious projects
- Scope: some sources suggest "just use VibeSec" for developer workflows; others argue OWASP skill is more standards-grounded

## Gaps

- No evidence of a skill with swain-aware integration (security review of documentation artifacts, threat modeling for agent infrastructure design)
- No evidence of a skill covering agentic pipeline security beyond agamm's OWASP agentic section
- Trail of Bits `agentic-actions-auditor` audits GitHub Actions CI/CD workflows — not agent skill infrastructure

---

## Recommendation Summary

| Option | Fit for Swain | Rationale |
|--------|--------------|-----------|
| **Trail of Bits** (select plugins) | High — for projects using swain that also do security work | Authoritative, modular, real credentials. Pick `differential-review`, `sharp-edges`, `insecure-defaults`. Skip the auditor-specialized ones. |
| **agamm/owasp-security** | Medium-High — adds proactive guidance layer + agentic security coverage | Complements built-in review; unique agentic AI section relevant to swain's domain |
| **anthropic/security-review** (built-in) | Already present | No action needed |
| **VibeSec** | Low — superseded by above | Skip |
| **obra/defense-in-depth** | Already present via superpowers | No action needed |

**Short answer:** Yes — `trailofbits/skills` (specifically the auditing and detection plugins) is the closest analogue to what impeccable.style was for frontend. It's from a professional firm, modular, and meaningfully extends the built-in baseline. The `agamm/owasp-security` skill adds a proactive layer (write secure code, not just review for vulnerabilities) and is the only skill covering agentic AI security risks — directly relevant to swain.
