---
source-id: "brian-scanlan-intercom-claude-code"
title: "Intercom's Internal Claude Code Plugin System (24-tweet thread)"
type: forum
url: "https://twitter-thread.com/t/2033980599073907163"
fetched: 2026-03-17T00:00:00Z
hash: "76ca32d9e643c50fdc3615fe5b019583b7f87c5a17d126f20a45888c6e9dcb88"
participants:
  - "brian_scanlan"
post-count: 24
---

# Intercom's Internal Claude Code Plugin System (24-tweet thread)

**Author:** Brian Scanlan (@brian_scanlan), Intercom
**Thread:** https://twitter.com/brian_scanlan/status/2033980599073907163

---

## brian_scanlan — 2026-03-17 (tweet 1)

We've been building an internal Claude Code plugin system at Intercom with 13 plugins, 100+ skills, and hooks that turn Claude into a full-stack engineering platform. Lots done, more to do. Here's a thread of some highlights.

## brian_scanlan — 2026-03-17 (tweet 2)

The wildest one: we gave Claude a read-only Rails production console via MCP. Claude can now execute arbitrary Ruby against production data - feature flag checks, business logic validation, cache state inspection etc.

## brian_scanlan — 2026-03-17 (tweet 3)

Safety gates: read-replica only, blocked critical tables, mandatory model verification before every query, Okta auth, DynamoDB audit trail. I launched it by saying "It is either the worst thing in the world that will ruin Intercom, or complete genius."

It is used a lot. No issues so far. Last time I looked the top-5 users weren't engineers - design managers, customer support engineers, product management leaders were all actively using it!

## brian_scanlan — 2026-03-17 (tweet 4)

The console is part of a broader Admin Tools MCP that gives Claude the same production visibility engineers have: Customer/feature flag/admin lookups etc. A skill-level gate blocks all these tools until Claude loads the safety reference docs first. No cowboy queries.

## brian_scanlan — 2026-03-17 (tweet 5)

We instrumented every Claude Code lifecycle event with OpenTelemetry. SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, SubagentStart... 14 event types flowing to Honeycomb. Privacy-first: we explicitly never capture user prompts, messages, or tool input.

## brian_scanlan — 2026-03-17 (tweet 6)

Session transcripts sync to S3 (with username SHA256-hashed for privacy). We can analyze how people actually use Claude at scale. On SessionEnd, a hook analyzes the entire session transcript with Claude Haiku looking for improvement opportunities.

## brian_scanlan — 2026-03-17 (tweet 7)

It auto-classifies gaps (missing_skill, missing_tool, repeated_failure, wrong_info) and posts to Slack with a pre-filled GitHub issue URL. This creates a feedback loop: real sessions -> detected gaps -> GitHub issues -> new skills -> better sessions.

## brian_scanlan — 2026-03-17 (tweet 8)

Our flaky test fixer is a 9-step forensic investigation workflow with a 20-category taxonomy of flakiness patterns. Hard rules:
- NEVER skip a spec as a "fix"
- NEVER guess root cause without CI error data
- Downloads failure data from S3, classifies against the taxonomy

Sweeps for "sibling" instances of the same antipattern. Fixes common patterns widely. This matters a lot when you've got hundreds of thousands of tests.

## brian_scanlan — 2026-03-17 (tweet 9)

Claude Code hooks enforce our PR workflow at the shell level and blocks it unless the create-pr skill was activated first:
1. A PreToolUse hook intercepts raw `gh pr create`
2. The skill extracts business INTENT before creating — asks "why?" not just "what changed?"
3. Another hook blocks ALL modifications to merged PR branches (push, commit, rebase, edit)
4. After PR creation, a background agent auto-monitors CI checks using ETag-based polling (zero rate-limit cost)

## brian_scanlan — 2026-03-17 (tweet 10)

After 5 permission prompts in a session, a hook suggests running the permissions analyzer. It scans your last 14 days of session transcripts, extracts every Bash command approved, and classifies them:
- GREEN: ls, grep, test runners
- YELLOW: git, mkdir
- RED: rm, sudo, curl etc.

Then writes the safe ones to your settings.json. Evidence-based, not prescriptive. We also maintain good defaults!

## brian_scanlan — 2026-03-17 (tweet 11)

Tool misses — A PostToolUse hook detects "command not found" errors and BSD/GNU incompatibilities in real-time. Spots things like `grep -P` failing on MacOS. Once per session, suggests the fix. Installs via Homebrew and updates CLAUDE.md so Claude knows the tool exists in future.

## brian_scanlan — 2026-03-17 (tweet 12)

Video transcript skill: feed it a Google Meet recording, get a markdown transcript with intelligently-placed inline screenshots at moments where the speaker says "as you can see" or "look at this."

## brian_scanlan — 2026-03-17 (tweet 13)

QA follow-up skill: takes QA session documents through a 7-stage pipeline that identifies issues, investigates the codebase, filters for quality, and creates GitHub issues to track. Far easier QA!

## brian_scanlan — 2026-03-17 (tweet 14)

Our data team built a Claude4Data platform with 30+ analytics skills — Snowflake queries, Gong call analysis, finance metrics, customer health reports. Sales reps, PMs, and data scientists all use it. "Friends at other tech companies are nowhere near this level of sophistication."

## brian_scanlan — 2026-03-17 (tweet 15)

We automatically ship our marketplace and keep it up to date on our Macs using JAMF. We run reports on skill creation and usage, and keep an eye on quality. The most used skills have high quality evals and are reviewed regularly.

## brian_scanlan — 2026-03-17 (tweet 16)

The wild thing is we're just getting started. All technical work and our entire SDLC is getting skill-ified. Remote agents will accelerate things even more.

## brian_scanlan — 2026-03-17 (tweet 17)

Ok, more stuff. A weekly Github Action job that fact checks and updates all CLAUDE.md and files referenced. Needs to go further and continually learn. Code Review agents with manners that only post important feedback. LSP servers for all main runtimes, speeding up code search.

## brian_scanlan — 2026-03-17 (tweet 18)

We started ingesting more of our logs into Snowflake and have a very well tuned skill (excellent evals etc.) that is very precise at finding the right logs for incidents and general troubleshooting. Works well with trace data in Honeycomb and infrastructure metrics in Datadog.

## brian_scanlan — 2026-03-17 (tweet 19)

Local development environment setup and troubleshooting. Very necessary as more non-engineers are using developer environments these days!

## brian_scanlan — 2026-03-17 (tweet 20)

LOADS of incident/troubleshooting investigation skills. They're starting to converge, using progressive disclosure in a solid core skill that can figure out what to do for specific issues. We have a goal to make all runbooks follow-able by Claude in the next 6 weeks.
