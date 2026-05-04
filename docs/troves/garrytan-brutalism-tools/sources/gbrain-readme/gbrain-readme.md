---
source-id: "gbrain-readme"
title: "GBrain — Your AI Agent's Personal Knowledge Base"
type: web
url: "https://github.com/garrytan/gbrain"
fetched: 2026-04-12T03:50:00Z
hash: "c035464d47c146c14450d96e6f59ef4576eb8082295445074132982ec68f5875"
---

# GBrain

Your AI agent is smart but it doesn't know anything about your life. GBrain fixes that. Meetings, emails, tweets, calendar events, voice calls, original ideas... all of it flows into a searchable knowledge base that your agent reads before every response and writes to after every conversation. The agent gets smarter every day.

> **~30 minutes to a fully working brain.** Your agent does the work. Database ready in 2 seconds (PGLite, no server). Schema, import, embeddings, and integrations take 15-30 minutes depending on brain size. You just answer questions about API keys.
>
> **Requires a frontier model.** Tested with **Claude Opus 4.6** and **GPT-5.4 Thinking**. Likely to break with smaller models.

## Architecture

```
┌──────────────────┐    ┌───────────────┐    ┌──────────────────┐
│   Brain Repo     │    │    GBrain     │    │    AI Agent      │
│   (git)          │    │  (retrieval)  │    │  (read/write)    │
│                  │    │               │    │                  │
│  markdown files  │───>│  Postgres +   │<──>│  skills define   │
│  = source of     │    │  pgvector     │    │  HOW to use the  │
│    truth         │    │               │    │  brain           │
│                  │<───│  hybrid       │    │                  │
│  human can       │    │  search       │    │  entity detect   │
│  always read     │    │  (vector +    │    │  enrich          │
│  & edit          │    │   keyword +   │    │  ingest          │
│                  │    │   RRF)        │    │  brief           │
└──────────────────┘    └───────────────┘    └──────────────────┘
```

The repo is the system of record. GBrain is the retrieval layer. The agent reads and writes through both. Human always wins — you can edit any markdown file directly and `gbrain sync` picks up the changes.

## The Compounding Thesis

Most tools help you find things. GBrain makes you smarter over time.

```
Signal arrives (meeting, email, tweet, link)
  → Agent detects entities (people, companies, ideas)
  → READ: check the brain first (gbrain search, gbrain get)
  → Respond with full context
  → WRITE: update brain pages with new information
  → Sync: gbrain indexes changes for next query
```

Every cycle through this loop adds knowledge. The agent enriches a person page after a meeting. Next time that person comes up, the agent already has context. You never start from zero.

## Voice: "Her" Out of the Box

The voice integration is the strongest demonstration of why a personal brain matters.
Call a phone number. Your AI answers. It knows who's calling, pulls their full context
from thousands of people pages, references your last meeting, and responds like someone
who actually knows your world. When the call ends, a structured brain page appears with
the transcript, entity detection, and cross-references.

## How this happened

I was setting up my OpenClaw agent and started a markdown brain repo. One page per person, one page per company, compiled truth on top, append-only timeline on the bottom. The agent got smarter the more it knew, so I kept feeding it. Within a week I had 10,000+ markdown files, 3,000+ people with compiled dossiers, 13 years of calendar data, 280+ meeting transcripts, and 300+ captured original ideas.

The agent runs while I sleep. The dream cycle scans every conversation, enriches missing entities, fixes broken citations, and consolidates memory. I wake up and the brain is smarter than when I went to sleep.

## The knowledge model

Every page in the brain follows the compiled truth + timeline pattern:

Above the `---` separator: **compiled truth**. Your current best understanding. Gets rewritten when new evidence changes the picture. Below: **timeline**. Append-only evidence trail. Never edited, only added to.

The compiled truth is the answer. The timeline is the proof.

## How search works

- Multi-query expansion (Claude Haiku) generates alternative phrasings
- Parallel vector (HNSW cosine) and keyword (tsvector + ts_rank) search
- RRF Fusion: score = sum(1/(60 + rank))
- 4-Layer Dedup (best chunk per page, cosine similarity > 0.85, type diversity 60% cap, per-page chunk cap)
- Stale alerts (compiled truth older than latest timeline)

## Database schema

10 tables in Postgres + pgvector: pages, content_chunks, links, tags, timeline_entries, page_versions, raw_data, files, ingest_log, config.

## Skills

| Skill | What it does |
|---|---|
| **ingest** | Ingest meetings, docs, articles. Updates compiled truth (rewrite, not append), appends timeline, creates cross-reference links across all mentioned entities. |
| **query** | 3-layer search (keyword + vector + structured) with synthesis and citations. |
| **maintain** | Periodic health: find contradictions, stale compiled truth, orphan pages, dead links, tag inconsistency, missing embeddings, overdue threads. |
| **enrich** | Enrich pages from external APIs. Raw data stored separately, distilled highlights go to compiled truth. |
| **briefing** | Daily briefing: today's meetings with participant context, active deals with deadlines, time-sensitive threads, recent changes. |
| **migrate** | Universal migration from Obsidian, Notion, Logseq, plain markdown, CSV, JSON, Roam. |
| **setup** | Set up GBrain from scratch: auto-provision Supabase via CLI, AGENTS.md injection, import, sync. Target TTHW < 2 min. |

## Integrations

| Recipe | What It Does |
|---|---|
| Public Tunnel | Fixed URL for MCP + voice (ngrok Hobby $8/mo) |
| Credential Gateway | Gmail + Calendar access (ClawVisor or Google OAuth) |
| Voice-to-Brain | Phone calls → brain pages (Twilio + OpenAI Realtime) |
| Email-to-Brain | Gmail → entity pages (deterministic collector) |
| X-to-Brain | Twitter → brain pages (timeline + mentions + deletions) |
| Calendar-to-Brain | Google Calendar → searchable daily pages |
| Meeting Sync | Circleback transcripts → brain pages with attendees |

## Engine Architecture

- PGLite (default): embedded PG 17.5 via WASM, ~/.gbrain/brain.pglite
- PostgresEngine: Supabase Pro ($25/mo), connection pooling via Supavisor
- Bidirectional migration: `gbrain migrate --to supabase/pglite`

## How gbrain fits with OpenClaw/Hermes

| Layer | What it stores | How to query |
|---|---|---|
| **gbrain** | People, companies, meetings, ideas, media | `gbrain search`, `gbrain query`, `gbrain get` |
| **Agent memory** | Preferences, decisions, operational config | `memory_search` |
| **Session context** | Current conversation | (automatic) |

## File storage and migration

Three-stage binary file lifecycle: Local files → `gbrain files mirror` → Cloud copy exists → `gbrain files redirect` → `.redirect` breadcrumbs → `gbrain files clean` → Cloud only. Every stage is reversible until `clean`.

6.5k stars. 715 forks. MIT license. TypeScript 98.1%, PLpgSQL 1.8%.