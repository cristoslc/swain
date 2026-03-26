---
source-id: "gh-issue-31326-thinking-empty"
title: "Thinking block content empty (thinking_len=0) since v2.1.69 — only encrypted signature returned"
type: forum
url: "https://github.com/anthropics/claude-code/issues/31326"
fetched: 2026-03-24T00:00:00Z
hash: "d624f04fe52328a5ae3c7ca030eeba92f5521e3382dbe58b577e7c44c9d3db9d"
participants:
  - "qishaoyumu"
  - "anthrotype"
  - "gordonrust"
  - "CairoAC"
  - "tsobczynski"
  - "jcbzqy"
post-count: 12
---

# [BUG] Thinking block content empty (thinking_len=0) since v2.1.69 — only encrypted signature returned

**State:** Open
**Labels:** bug, has repro, platform:macos, area:model, regression
**Author:** qishaoyumu (Cyrus Cui)
**Created:** 2026-03-06

## qishaoyumu — 2026-03-06 03:09 UTC

Since v2.1.69, the `thinking` field in thinking blocks is returned as an empty string (`""`), while the `signature` field still contains encrypted data. This means thinking content is completely invisible even with verbose mode enabled — not because of a display bug, but because the API response no longer contains plaintext thinking summaries.

**Verified with two Mac machines, same account (Max plan), same model (Opus 4.6 with 1M context):**

| Version | thinking_len | sig_len | Thinking visible? |
|---------|-------------|---------|-------------------|
| v2.1.68 | 1312 | 2876 | Yes (plaintext summary present) |
| v2.1.69 | 0 | 436 | No (empty string) |
| v2.1.70 | 0 | 1064 | No (empty string) |

**Raw data from JSONL session transcripts:**

v2.1.68 (working):
```
thinking_len=1312  sig_len=2876
thinking content: "The user is asking about the strategy for managing their forked repository of 'superpowers'. Let me understand the situation..."
```

v2.1.69 (broken):
```
thinking_len=0  sig_len=436
thinking content: ""
```

v2.1.70 (broken):
```
thinking_len=0  sig_len=1064
thinking content: ""
```

This was verified by extracting thinking blocks from `~/.claude/projects/{project}/{session-id}.jsonl` files.

### What Should Happen

The `thinking` field in thinking blocks should contain a plaintext summary of Claude's reasoning process (as it did in v2.1.68), so that verbose mode can display it. The `signature` field confirms thinking IS happening — the summarized content is just no longer being returned.

### Steps to Reproduce

1. Install Claude Code v2.1.69 or v2.1.70
2. Use Opus 4.6 (1M context) with thinking enabled
3. Start a new session, send any message
4. Check the session JSONL file for `"type":"thinking"` entries
5. Observe: `thinking` field is `""`, `signature` field has content
6. Compare: Downgrade to v2.1.68, repeat — `thinking` field has plaintext content

### Environment

- **Claude Model:** Opus 4.6 (1M context)
- **Last Working Version:** 2.1.68
- **Claude Code Version:** 2.1.70
- **Platform:** Anthropic API (Max plan)
- **OS:** macOS (tested on two separate Mac machines)
- **Terminal:** Warp

This is **not** the same as #25980 or #22977 (verbose mode display bug). Those issues report thinking blocks existing but not rendering in the terminal. This issue is that the thinking block **content itself is empty** at the data level.

## qishaoyumu — 2026-03-06 03:12 UTC

**Correction:** The platform is **Claude Max subscription** (not direct API). Claude Code is authenticated via Max plan, not API keys. This may be relevant if thinking summary behavior differs between Max and API access paths.

## github-actions — 2026-03-06 03:13 UTC

Found 2 possible duplicate issues:

1. https://github.com/anthropics/claude-code/issues/30958
2. https://github.com/anthropics/claude-code/issues/31143

This issue will be automatically closed as a duplicate in 3 days.

## qishaoyumu — 2026-03-06 03:14 UTC

This is a duplicate of #30958 which reports the exact same regression (v2.1.68 → v2.1.69, thinking content empty, only signature returned). That issue has been labeled as `regression` and `bug` by maintainers.

Our report adds additional data points:
- Confirmed on **macOS + Warp** (not just Linux)
- Confirmed on **Max subscription** (not just API)
- Confirmed across **two separate machines** with the same account
- Tested on both v2.1.69 and v2.1.70 — both affected

## CairoAC — 2026-03-09 03:02 UTC

I'm starting to think this is on purpose, THEY ALWAYS MESS UP thinking

## CairoAC — 2026-03-09 03:03 UTC

> Found 2 possible duplicate issues...

not a duplicate

## anthrotype — 2026-03-10 10:04 UTC

I also noticed the same, but since Anthropic hasn't documented this yet, I asked Claude to dig into this, below is the report:

### How `redact-thinking` works in Claude Code v2.1.69+

#### The mechanism

Starting in v2.1.69 (March 5, 2026), Claude Code sends a `redact-thinking-2026-02-12` beta header with every API request. This header tells the Anthropic API to **strip the text content from all thinking blocks** before returning them to the client. The thinking blocks still appear in the response with valid cryptographic signatures (proving thinking occurred), but the `thinking` property is an empty string.

#### The code path (v2.1.71)

**Step 1: Beta header injection**

When building API request parameters, Claude Code constructs the `betas` array. The relevant condition (deminified):

```js
if (
  hasThinking &&                                          // thinking is enabled
  modelSupportsInterleavedThinking(model) &&              // model supports it
  !isVerboseMode() &&                                     // not in verbose/transcript mode
  getSettings().showThinkingSummaries !== true &&          // setting is NOT explicitly true
  getFeatureFlag("tengu_quiet_hollow", false)              // feature flag (defaults to false)
) {
  betas.push("redact-thinking-2026-02-12");
}
```

The `showThinkingSummaries` setting defaults to `undefined` (not documented, not set by default). Since `undefined !== true` evaluates to `true`, the condition passes and the redact header is **always included** unless the user explicitly sets `"showThinkingSummaries": true` in `~/.claude/settings.json`.

**Note:** The `tengu_quiet_hollow` feature flag check uses `p8("tengu_quiet_hollow", false)` where `false` is the default — meaning when the flag is not set, it defaults to `false`, and the condition `false` would block the beta. However, this flag appears to be **server-controlled** and is currently returning `true` for users, enabling the redaction.

**Step 2: API response**

The API receives the `redact-thinking-2026-02-12` beta header and returns thinking blocks like:

```json
{
  "type": "thinking",
  "thinking": "",
  "signature": "EuEECkYICxgCKkBrmuins..."
}
```

The `thinking` text is empty. The `signature` is valid (proving the model did think).

**Step 3: Rendering**

The thinking content renderer extracts the `thinking` property from the content block:

```js
let { thinking } = contentBlock;
if (!thinking) return null;  // empty string is falsy → renders nothing
```

Since `thinking` is `""` (empty string, falsy in JavaScript), the component returns `null`. **Nothing is rendered** — not in the live view, not in the transcript view (ctrl+o), nowhere.

#### The setting

```json
// ~/.claude/settings.json
{
  "showThinkingSummaries": true
}
```

The setting's internal schema description is:
> "Show thinking summaries in the transcript view (ctrl+o). Default: false."

This is misleading. The setting doesn't control a UI display toggle — it controls whether the **API request includes a beta header that causes the server to strip thinking text from the response entirely**.

#### Timeline

| Version | Date | Status |
|---------|------|--------|
| ≤ v2.1.63 | Feb 28 | No redaction. Thinking text sent normally. |
| v2.1.64 | Mar 3 | `redact-thinking` introduced |
| v2.1.66 | Mar 3 | Reverted (same day) |
| v2.1.68 | Mar 4 | Still reverted |
| **v2.1.69** | **Mar 5** | **Re-introduced permanently** |
| v2.1.70–72 | Mar 6–10 | Present in all versions |

#### Impact

- The ctrl+o transcript view (the official way to view thinking) shows nothing because the thinking text was never received
- `alwaysThinkingEnabled: true` still causes the model to think (and bill for thinking tokens), but the output is discarded before reaching the client
- The setting is not documented in the official settings documentation
- Users have no way to discover this setting exists unless they read the minified source code

#### Workaround

Add to `~/.claude/settings.json`:

```json
{
  "showThinkingSummaries": true
}
```

Then restart Claude Code.

## gordonrust — 2026-03-11 06:42 UTC

Two things:
1. is there a way to be in verbose mode by default (i believe verbose mode is just ctrl+o,)? the problem is that if i do ctrl+o, the tui doesnt show what claude is doing, from the point when i pushed ctrl+o.
2. How did you do this exploration? how did you learn this?

## gordonrust — 2026-03-11 16:57 UTC

The thinking doesn't seem to persist and only shows the current thinking. Past thinkings are deleted. Is there a way to persist them?

## anthrotype — 2026-03-11 17:07 UTC

> The thinking doesn't seem to persist and only shows the current thinking. Past thinkings are deleted.

yet another bug (or 'feature'):
https://github.com/anthropics/claude-code/issues/16965

they are really trying hard to hide those thinking messages from us. I have Claude regularly patch the minified JS to restore them inline as they used to appear before they started thinkering with them: https://github.com/aleks-apostle/claude-code-patches/pull/9

there are several other community patches that do the same. Dozens of similar issues related to thinking messages have been closed automatically after inactivity. They haven't bothered explaining if this is intentional design/policy decision, but it is a fact that they are consistently restricting visibility of thinking messages.

## tsobczynski — 2026-03-15 15:00 UTC

The setting above (`"showThinkingSummaries": true`) worked for me. Possibly because it's coupled with verbose mode, I'm now getting the thinking blocks inline again, as desired.

## jcbzqy — 2026-03-16 10:38 UTC

The purpose of a system is what it does. Since early February, thinking mode has anecdotally been broken ~50% of the time for me.

I posit two collectively exhaustive but not mutually exclusive possibilities:
- Unstable/unreliable thinking display is a pragmatic defense against distillation.
- Nobody at Anthropic has thought to write an integration test which sends a query with `"alwaysThinkingEnabled": true`, then checks to see if the TUI shows thinking output after `ctrl-o`.

Between malice and negligence, I hope it is negligence.
