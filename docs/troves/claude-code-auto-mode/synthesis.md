# Synthesis: Claude Code Auto Mode

## Key findings

- **Auto mode is a new permission tier** in Claude Code, sitting between the conservative default (every tool call prompts) and the risky `--dangerously-skip-permissions` flag. Announced March 24, 2026 as a research preview.

- **Mechanism: classifier-gated execution.** Before each tool call runs, a classifier evaluates it for destructive actions (mass file deletion, data exfiltration, malicious code execution). Safe actions proceed automatically; risky ones are blocked and Claude is redirected. Repeated blocks eventually escalate to a user permission prompt.

- **Availability is tiered.** Research preview for Team plan first, with Enterprise and API users following. Works with both Sonnet 4.6 and Opus 4.6. Disabled by default on the Claude desktop app.

- **Not a replacement for isolation.** Anthropic still recommends isolated environments even with auto mode. The classifier can miss risky actions when intent is ambiguous or environmental context is insufficient, and can occasionally block benign actions.

- **Activation:** `claude --enable-auto-mode` to enable, `Shift+Tab` to cycle to it. Admins can disable with `"disableAutoMode": "disable"` in managed settings.

## Points of agreement

Single source — no cross-source convergence analysis possible yet.

## Points of disagreement

Single source — no cross-source conflict analysis possible yet.

## Gaps

- **Classifier internals are opaque.** No documentation on what the classifier checks, its false-positive/negative rates, or how it's trained. The linked docs page ("what the classifier blocks by default") may contain more detail.
- **Token/cost impact unquantified.** "Small impact on token consumption, cost, and latency" — no numbers provided.
- **No comparison with existing permission presets.** How does auto mode interact with existing allowlists (e.g., `permissions.allow` in settings)?
- **Community reception unknown.** No user feedback yet (announced same day as this trove).
- **Interaction with hooks unclear.** How does auto mode interact with Claude Code hooks (pre/post tool execution hooks)?
