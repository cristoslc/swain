# Synthesis: Claude Code Thinking Redaction

## Key findings

- **Thinking content was silently redacted starting in v2.1.69** (March 5, 2026). The `thinking` field in thinking blocks is returned as an empty string, while the `signature` field (cryptographic proof thinking occurred) remains populated. This is a data-level change, not a rendering bug.

- **Mechanism: `redact-thinking-2026-02-12` beta header.** Claude Code injects this header into API requests, instructing the API to strip plaintext thinking text before returning it. The thinking still happens (and is billed), but the content is never sent to the client.

- **The behavior is gated by an undocumented setting and a server-controlled feature flag.** The setting `showThinkingSummaries` (defaults to `undefined`, treated as `false`) controls whether the redaction header is sent. The `tengu_quiet_hollow` feature flag is server-side and currently enabled. Setting `"showThinkingSummaries": true` in `~/.claude/settings.json` is a confirmed workaround.

- **Timeline shows intentional rollout, not accidental regression:**
  - v2.1.64 (Mar 3): redact-thinking introduced
  - v2.1.66 (Mar 3): reverted same day
  - v2.1.68 (Mar 4): still reverted (last working version)
  - v2.1.69 (Mar 5): re-introduced permanently
  - v2.1.70–72 (Mar 6–10): present in all subsequent versions

- **Community reverse-engineering (anthrotype)** decompiled the minified JS and documented the full code path: beta header injection → API response stripping → renderer returning null for empty strings. This is the most detailed technical analysis in the thread.

## Points of agreement

- All participants agree thinking content is empty at the data level (not a rendering issue).
- Multiple independent confirmations: macOS, Warp terminal, Max subscription, two separate machines.
- The `showThinkingSummaries: true` workaround is confirmed working by multiple users (anthrotype, tsobczynski).

## Points of disagreement

- **Intentional vs accidental:** qishaoyumu filed it as a bug/regression. CairoAC and anthrotype suspect it's intentional policy ("they are really trying hard to hide those thinking messages"). jcbzqy frames it as either anti-distillation defense or negligence.
- **Duplicate status:** The bot flagged it as a duplicate of #30958. The community pushed back (3 thumbs-down on the bot comment), arguing it adds distinct data points.

## Gaps

- **No official Anthropic response.** No maintainer has commented on the issue or the related #30958. No public statement on whether thinking redaction is intentional policy.
- **Impact on agent workflows.** The issue focuses on human-visible thinking in the TUI, but doesn't explore implications for programmatic access (e.g., agents that read session transcripts for reasoning traces).
- **Billing implications.** If thinking tokens are generated and billed but the content is discarded before reaching the client, users are paying for invisible computation.
- **Interaction with other thinking-related issues.** The thread references #16965 (thinking not persisting), #25980 and #22977 (verbose mode display), but no unified analysis of Anthropic's thinking visibility strategy exists.
- **Community patches.** anthrotype references `aleks-apostle/claude-code-patches` for inline thinking restoration — this could be a useful extension source.
