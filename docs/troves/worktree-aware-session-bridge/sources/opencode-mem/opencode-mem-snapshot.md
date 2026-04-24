# opencode-mem Snapshot

**Repository**: https://github.com/tickernelz/opencode-mem
**License**: MIT
**Author**: tickernelz
**npm**: opencode-mem (v2.13.0)
**Inspired by**: opencode-supermemory

## Project Structure

```
opencode-mem/
  src/
    index.ts                    # Main plugin (~588 lines) — event handlers, memory tool, auto-capture, compaction
    plugin.ts                   # Plugin module entry point (re-exports OpenCodeMemPlugin)
    config.ts                   # Extensive config system (~582 lines) — JSONC, defaults, provider settings
    services/
      client.ts                 # MemoryClient — SQLite-backed memory operations
      context.ts                # Context formatting for prompt injection
      embedding.ts              # Embedding service (local Xenova models or remote APIs)
      auto-capture.ts            # Auto-capture AI analysis on session.idle
      cleanup-service.ts        # Memory cleanup/compaction service
      deduplication-service.ts   # Smart dedup of similar memories
      language-detector.ts      # Language detection for auto-capture
      logger.ts                 # Logging utility
      migration-service.ts       # DB migration service
      privacy.ts                # Strip private content from memories
      secret-resolver.ts        # Resolve env:// file:// and direct API keys
      jsonc.ts                  # JSONC (JSON with comments) parser
      tags.ts                   # Project/user tag generation
      web-server.ts             # HTTP web UI server for memory visualization
      web-server-worker.ts      # Web server worker thread
      ai/
        ai-provider-factory.ts  # AI provider factory
        opencode-provider.ts    # OpenCode provider (uses opencode's own auth)
        provider-config.ts      # Provider configuration
        providers/
          anthropic-messages.ts  # Anthropic API provider
          base-provider.ts      # Base AI provider class
          google-gemini.ts      # Google Gemini provider
          openai-chat-completion.ts # OpenAI Chat Completion provider
          openai-responses.ts   # OpenAI Responses API provider
        session/
          ai-session-manager.ts # AI session management
          session-types.ts      # Session type definitions
        tools/
          tool-schema.ts        # Tool schema definitions for AI
        validators/
          user-profile-validator.ts # User profile data validation
      sqlite/
        connection-manager.ts   # SQLite connection management
        shard-manager.ts        # Database sharding
        sqlite-bootstrap.ts     # Database initialization
        types.ts                # SQLite types
        vector-search.ts        # Vector similarity search
      user-profile/
        profile-context.ts      # Profile context generation
        profile-utils.ts        # Profile utility functions
        types.ts                # Profile types
        user-profile-manager.ts # User profile CRUD and learning
      user-prompt/
        user-prompt-manager.ts  # User prompt tracking and injection
      vector-backends/
        backend-factory.ts      # Vector backend factory
        exact-scan-backend.ts   # Fallback exact vector scan
        types.ts                # Vector backend types
        usearch-backend.ts      # USearch vector indexing
      api-handlers.ts           # Web API route handlers
  web/
    app.js, index.html, styles.css, i18n.js, favicon.ico  # Web UI
  tests/                        # Comprehensive test suite (20+ files)
  package.json
  tsconfig.json
```

## How Memory Works

### Core Architecture

1. **SQLite + vector database**: Memories stored in SQLite with USearch-first vector indexing (exact-scan fallback). Supports 12+ local embedding models via `@huggingface/transformers` (Xenova/nomic-embed-text-v1 default).
2. **Memory scopes**: `project` (default) or `all-projects`. Memories are tagged with project metadata and user info.
3. **Single `memory` tool** with subcommands: `add`, `search`, `profile`, `list`, `forget`, `help`.

### Memory Lifecycle

4. **Auto-capture** (`session.idle` event): After 10s idle, AI analyzes the conversation to extract and store memories. Configurable provider (opencode's own auth, OpenAI, Anthropic).
5. **Chat injection** (`chat.message` hook): Injects relevant memories into conversation context on first user message (or always, configurable). Respects `excludeCurrentSession` and `maxAgeDays`.
6. **Compaction recovery** (`session.compacted` event): Re-injects memories after context compaction to maintain continuity.
7. **User profile learning**: Periodically analyzes user prompts to build preference/pattern/workflow profiles.

### Storage & Search

8. **SQLite sharding**: Databases auto-shard at 50k vectors per shard.
9. **Deduplication**: Configurable similarity-based dedup (default threshold 0.9).
10. **Auto-cleanup**: Deletes memories older than retention period (default 30 days).
11. **Vector backends**: USearch (preferred in-memory) → ExactScan (fallback).

### Web UI

12. **Local web server**: HTTP server at `http://127.0.0.1:4747` for visual memory browsing and management.

## Key Files

| File | Purpose |
|------|---------|
| `src/index.ts` | Main plugin — memory tool, event handlers (idle/compacted), chat injection |
| `src/config.ts` | Full config system — JSONC parsing, defaults, provider settings |
| `src/services/client.ts` | MemoryClient — add/search/delete/list memories |
| `src/services/embedding.ts` | Embedding service (local + remote) |
| `src/services/auto-capture.ts` | AI-powered memory extraction from sessions |
| `src/services/user-profile/user-profile-manager.ts` | User profile CRUD and learning |
| `src/services/sqlite/vector-search.ts` | Vector similarity search on SQLite |
| `src/services/vector-backends/usearch-backend.ts` | USearch vector indexing |
| `package.json` | v2.13.0, dependencies include ai-sdk, usearch, transformers |