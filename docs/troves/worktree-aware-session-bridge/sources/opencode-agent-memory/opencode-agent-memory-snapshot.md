# opencode-agent-memory Snapshot

**Repository**: https://github.com/joshuadavidthomas/opencode-agent-memory
**License**: MIT (Copyright 2025 Josh Thomas)
**Author**: joshuadavidthomas

## Project Structure

```
opencode-agent-memory/
  src/
    plugin.ts              # Main plugin entry — registers tools, system prompt injection, chat.message hook
    memory.ts              # Memory store — CRUD for memory blocks stored as markdown files with YAML frontmatter
    prompt.ts              # System prompt renderer — XML-formatted memory blocks with metadata
    tools.ts               # Tool definitions — memory_list, memory_set, memory_replace, journal_write/read/search
    journal.ts             # Journal store — append-only entries with semantic search
    embeddings.ts          # Local embedding generation (all-MiniLM-L6-v2)
    frontmatter.ts         # YAML frontmatter parsing/serialization for memory blocks
    letta.ts               # Letta-inspired default descriptions and memory instructions
    memory.test.ts
    journal.test.ts
    prompt.test.ts
  package.json
  tsconfig.json
  CHANGELOG.md
  README.md
```

## How Memory Works

### Memory Blocks (Letta-inspired)

1. **Architecture**: Adapted from Letta's shared memory blocks pattern. Memory is stored as markdown files with YAML frontmatter, providing persistent, self-editable memory across sessions.
2. **Scopes**: Two scopes — `global` (`~/.config/opencode/memory/*.md`) and `project` (`.opencode/memory/*.md`, auto-gitignored).
3. **Default blocks**: Three seeded on first run:
   - `persona` (global) — how the agent should behave
   - `human` (global) — user preferences/habits
   - `project` (project) — codebase-specific knowledge
4. **System prompt injection**: Memory blocks are injected into the system prompt via `experimental.chat.system.transform` — inserted at position 1 (after provider header) for salience, with XML formatting including descriptions, metadata (chars/limit/read_only/scope), and line-numbered values.
5. **Tools**: Three memory tools (`memory_list`, `memory_set`, `memory_replace`) for the agent to read and modify its own memory. Blocks support `read_only` flag, `limit` (char cap), and `description` fields.
6. **Stable ordering**: Blocks sorted in deterministic order (persona → human → project → alphabetical) to support prompt caching.

### Journal

7. **Opt-in journal**: Enabled via `~/.config/opencode/agent-memory.json` with `{"journal": {"enabled": true}}`.
8. **Journal entries**: Append-only markdown files with YAML frontmatter in `~/.config/opencode/journal/`. Captures project, model, provider, agent, session metadata.
9. **Semantic search**: Uses local embeddings (all-MiniLM-L6-v2 via `@huggingface/transformers`) for similarity search across journal entries.
10. **Journal tools**: `journal_write`, `journal_read`, `journal_search` with tag support and pagination.

## Key Files

| File | Purpose |
|------|---------|
| `src/plugin.ts` | Main plugin — registers tools, injects memory into system prompt, captures chat metadata |
| `src/memory.ts` | MemoryStore — CRUD operations on frontmatter markdown files, seeding, validation |
| `src/prompt.ts` | Renders memory blocks as XML for system prompt injection |
| `src/tools.ts` | All tool definitions (memory_list/set/replace, journal_write/read/search) |
| `src/journal.ts` | Journal store — write entries, semantic search, tag filtering |
| `src/embeddings.ts` | Local embedding generation using HuggingFace transformers |
| `src/frontmatter.ts` | YAML frontmatter parse/serialize with atomic file writes |
| `src/letta.ts` | Default descriptions and memory instructions (Letta-inspired) |