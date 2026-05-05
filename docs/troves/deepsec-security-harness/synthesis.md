# Synthesis: deepsec Security Harness

## Key findings

- **deepsec** is an open-source security harness from Vercel that uses coding agents (Claude Opus 4.7, GPT 5.5) to find vulnerabilities in large codebases.
- It runs entirely on your own infrastructure — no cloud service needed for privileged source code access.
- The pipeline has five stages: **scan** (regex), **investigate** (agent analysis), **revalidate** (false-positive removal), **enrich** (git blame for fix ownership), and **export** (ticket-ready findings).
- Optional fanout to Vercel Sandboxes enables parallel execution scaling to 1,000+ concurrent workers.

## Points of agreement

- The false positive rate is roughly 10-20%, which Vercel considers acceptable given the value of true positives.
- The system works best for applications and services, not libraries or frameworks (those need custom prompts and scanners).
- A plugin system with custom regex matchers is the primary extension point for adapting to a specific codebase.
- Works with off-the-shelf models (Opus 4.7, GPT 5.5) — "cyber" fine-tuned variants are optional, not required.
- Refusals are reported as a non-issue with the prompts deepsec uses.

## Points of disagreement

- None identified from this single source.

## Gaps

- No details on the specific regex patterns used in the scan phase.
- No performance benchmarks (time per file, false-positive per language, etc.).
- No comparison to other agentic security tools (e.g., Claude Code security skills, CodeQL, Semgrep).
- No information on supported languages beyond those implicit in the dub.co and Vercel monorepo case studies.
- No details on how the `revalidate` agent differs from the `investigate` agent (different prompt? different model?).
