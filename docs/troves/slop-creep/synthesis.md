# Slop Creep — Synthesis

## Key findings

- **Slop creep** is the gradual, invisible degradation of a codebase through individually reasonable but collectively destructive agent-generated decisions. No single commit is the problem — the damage is emergent and cumulative. (boristane-slop-creep-enshittification)

- **Sloppypasta** is the communication-layer analog: verbatim LLM output copy-pasted at someone, unread, unrefined, and unrequested. It shifts the full burden of reading, verifying, and distilling onto the recipient. (stopsloppypasta-ai)

- **Both phenomena share the same root cause: effort asymmetry.** LLMs make producing output near-free while the cost to consume, verify, and act on that output remains unchanged — or increases due to the verification tax.

- **Agents remove the natural circuit breaker** that used to constrain bad decisions. In code: a slow developer would hit friction before burying the codebase. In communication: writing effort forced authors to think before sharing. LLMs eliminate both friction points. (boristane-slop-creep-enshittification, stopsloppypasta-ai)

- **The core failure mode in code**: agents optimize for the prompt, not the system. They produce solutions that are correct in isolation but wrong for the codebase as a whole — wrong abstractions, wrong cardinality, boolean fields where enums belong, no thought to query patterns or future evolution. (boristane-slop-creep-enshittification)

- **The core failure mode in communication**: the sender delegates comprehension to the recipient. "ChatGPT says" is the enshittified LMGTFY. Trust erodes because the recipient can't distinguish what the sender checked vs. what they just forwarded. (stopsloppypasta-ai)

- **One-way doors are the critical boundary** in code: data models, service boundaries, and key abstractions. The agent should never walk through a one-way door alone. (boristane-slop-creep-enshittification)

- **Writing is thinking.** Multiple studies show delegating tasks to LLMs creates cognitive debt — reduced comprehension of and recall about the delegated subject. Shortcutting the writing process hurts the sender's own understanding. (stopsloppypasta-ai, citing Anthropic research + MIT Media Lab)

- **Trust is the casualty.** Pre-LLM, "trust but verify" worked because writing carried implicit proof-of-thought. LLM output obfuscates the chain of trust — the recipient doesn't know what was verified and what wasn't. Repeated sloppypasta is the modern "Boy Who Cried Wolf." (stopsloppypasta-ai)

## Points of agreement

- AI tools are net positive and should not be abandoned — both sources explicitly say this
- The human's role shifts from producing to thinking — system-level judgment (code) and editorial judgment (communication)
- The mitigation is the same in both domains: **read, verify, distill, then share**
- More context and better models will likely improve code quality over time (boristane-slop-creep-enshittification)

## Points of tension

- Boristane focuses on the **producer's responsibility** to plan tightly before letting agents execute — the problem is between the engineer and the codebase
- Stopsloppypasta focuses on the **sender-recipient relationship** — the problem is between people, and the guidelines are social norms (disclose, share as link, share only when requested)
- These are complementary rather than contradictory: one addresses slop at the point of creation, the other at the point of distribution

## Guidelines (from stopsloppypasta-ai)

1. **Read** — Read the output before sharing
2. **Verify** — Check facts; your reputation depends on what you share
3. **Distill** — Cut to what matters; verbosity is the LLM's default, not yours
4. **Disclose** — Say how AI helped; restore trust signals
5. **Share only when requested** — Don't impose effort asymmetry unsolicited
6. **Share as a link** — Don't filibuster the conversation viewport

## Gaps

- No quantitative data on slop creep rates or codebase health metrics
- No comparison of agent workflows (how much does iterative planning actually reduce slop vs. one-shot prompting?)
- No discussion of automated guardrails (linters, architectural tests, fitness functions) as complementary defenses for code slop
- No mention of multi-agent patterns or agent-to-agent review as a mitigation
- No organizational policy frameworks — both sources address individual behavior, not team/org norms
- No discussion of when raw AI output *is* appropriate (brainstorming, drafting, explicit "here's what the model said" contexts)

## Relevance to swain

Both sources validate swain's design philosophy from different angles:

- **Code quality (boristane):** Structured planning (swain-design), iterative refinement (brainstorming + writing-plans chain), and agent alignment through artifacts on disk. The "one-way door" framing maps to swain's coordination-tier (Vision/Epic) vs. implementation-tier (Spec) distinction — the operator makes the calls, the agent fills the gaps.

- **Communication quality (stopsloppypasta):** The "read, verify, distill" guidelines parallel how swain-design asks the operator to review and refine agent-drafted artifacts before they become authoritative. Swain artifacts are never raw agent output — they go through iterative refinement with operator judgment at each step.
