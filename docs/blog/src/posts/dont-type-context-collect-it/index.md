---
layout: post.njk
title: "Don't Type Context. Collect It."
description: "The bottleneck in agent workflows isn't the agent — it's you, typing context. Research troves turn background briefings into reusable, inspectable, versioned artifacts."
date: 2026-04-16T12:00:00
published: 2026-04-16T12:00:00
tags:
  - post
  - research
  - agent-workflows
  - swain
---

There's a lot I've not gotten right in [swain](https://github.com/cristoslc/swain). But one piece has been super useful: [swain-search](https://github.com/cristoslc/swain/blob/release/skills/swain-search/SKILL.md), a skill for collecting research on a topic in a standardized format and piping it into design workflows.

The shift it enables is small but compounds: instead of typing background context into every session, I say "research X" and get back a *trove* — collected sources, normalized to markdown, synthesized into key findings — that any artifact can reference. I can inspect what went in. I don't have to re-enter it.


## The context problem

Agent sessions start from scratch. Every session, you either supply context or the agent works without it. The default move is to paste it in — the relevant docs, the prior decisions, the background on a technical choice. This works once. Then the next session starts and you paste it again.

The loss is bigger than repetition. Pasted context is:

- **Ephemeral.** It lives in one conversation. The next agent — or the same agent, next session — doesn't see it.
- **Unverified.** You typed it from memory. Maybe you got it right. Maybe not.
- **Uninspectable.** The agent saw your summary, not the sources. If the conclusion was wrong, you can't trace why.
- **Untethered.** There's no pointer back to what you read or decided. Just your paraphrase.

This is the bottleneck. Not the agent's capability — your ability to get context into it accurately and repeatedly.


## What troves do

A trove is three things:

1. **`sources/`** — the raw material, normalized to markdown. Web pages stripped of boilerplate. Video transcripts with timestamps. X threads unrolled and cited. Repo trees mirrored selectively. Each source gets a slug, frontmatter with provenance, and a content hash.
2. **`manifest.yaml`** — one entry per source. URL, fetch date, content hash, freshness TTL. Provenance and discoverability.
3. **`synthesis.md`** — a thematic distillation. Not source-by-source summaries; findings grouped by theme, with explicit points of agreement, disagreement, and gaps.

The [swain-search skill](https://github.com/cristoslc/swain/blob/release/skills/swain-search/SKILL.md) handles collection: web search, page fetch, video transcription, X thread unrolling, local files, repo mirroring. Normalization strips the format-specific noise (navigation, ads, cookie banners) and leaves the content in a consistent markdown structure. The skill also checks whether an existing trove already covers the topic — extending is preferred over creating parallel troves.


## Why it works

Three properties that pasted context doesn't have:

**Inspectable inputs.** The synthesis tells you what the sources collectively say. The sources tell you what each one said. You can disagree with the synthesis, check the source, and correct it. With pasted context, you're trusting your own summary with no audit trail.

**Reusable across sessions.** Artifacts reference troves with `trove: <id>@<commit-hash>`. The hash pins the trove to a specific version. If the trove gets extended or refreshed later, the artifact still points at the version it was written against. Next session, a different agent reads the same trove. No re-entry.

**Git-versioned provenance.** Troves live in `docs/troves/` and are committed like any other artifact. The manifest records when each source was fetched, what its hash was, whether a paywall proxy was needed. If a source goes stale, the refresh mode re-fetches and updates. The history is in git.


## An example output

The [multi-agent-collision-vectors](https://github.com/cristoslc/swain/blob/release/docs/troves/multi-agent-collision-vectors/synthesis.md) trove collected 16 sources on how parallel AI agents collide — git worktree safety, merge queue patterns, TOCTOU mitigation, framework coordination models. The synthesis surfaces what the sources agree on, where they conflict, and what they don't cover at all.

That trove fed a spike that informed swain's three-layer merge strategy. The spike is done. The trove persists. If I revisit the coordination model in six months, I don't re-research from scratch — I refresh the trove and read what changed.

That's the compounding effect. Research becomes a durable asset, not session overhead.


## Excisable by design

Swain-search works inside swain. But both the skill and its outputs are designed to be liftable without the rest of the framework.

The skill is a single markdown file and a handful of scripts. No swain-specific runtime. No artifact graph dependency. It reads sources, normalizes them, writes markdown to disk, commits to git. Any agent that can run shell commands and read markdown can use it.

The outputs are standard markdown files in a directory tree. No database. No proprietary format. Another agent — or a human — can read `synthesis.md` and the `sources/` directory without knowing swain exists. This is the [excisability](../../posts/excisable-software/series-outline/) property: a concept, tests, and evidence with no framework entanglement.

The excision works in both directions. You can use the skill without swain. You can use the trove outputs without the skill. Neither direction requires the other.


## Takeaway

Research is usually treated as session overhead: something you do before the work starts, then discard. Troves make it a first-class artifact — collected, normalized, synthesized, versioned, and referenceable.

The practical shift: instead of "let me explain the background" at the start of every session, you say "research X" once. The trove becomes context that any agent can read, any artifact can reference, and you can inspect when the conclusions don't match reality.

This doesn't require swain. It requires treating research as an asset worth versioning, not conversation overhead worth discarding.

I'm at [@cristoslc](https://github.com/cristoslc). The [swain-search skill](https://github.com/cristoslc/swain/blob/release/skills/swain-search/SKILL.md) and the [multi-agent-collision-vectors trove](https://github.com/cristoslc/swain/blob/release/docs/troves/multi-agent-collision-vectors/synthesis.md) are both public.