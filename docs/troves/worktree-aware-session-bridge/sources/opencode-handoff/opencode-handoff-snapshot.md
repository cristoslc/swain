# opencode-handoff Snapshot

**Repository**: https://github.com/joshuadavidthomas/opencode-handoff
**License**: MIT (Copyright 2025 Josh Thomas)
**Author**: joshuadavidthomas
**Inspired by**: Amp's handoff command (https://ampcode.com/news/handoff)

## Project Structure

```
opencode-handoff/
  src/
    plugin.ts       # Main plugin — registers /handoff command, chat.message hook, session cleanup
    tools.ts         # Tool definitions — HandoffSession (create new session) and ReadSession (read transcript)
    files.ts         # File reference parsing — extracts @file refs from prompts, builds synthetic parts
    vendor.ts        # Vendored code from OpenCode — isBinaryFile(), formatFileContent()
  package.json
  tsconfig.json
  CHANGELOG.md
  README.md
```

## How Handoff Works

### The /handoff Command

1. **Command registration**: Plugin registers a `/handoff` command via `config.command` hook, with a detailed template that instructs the AI to:
   - Analyze the current conversation
   - Identify 8-20 relevant files to carry forward
   - Draft context and goals preserving decisions/constraints/preferences
   - Exclude conversation back-and-forth and dead ends

2. **Agent generates handoff**: After analyzing, the AI calls `handoff_session(prompt, files)` which:
   - Creates a continuation prompt with: session reference line, @file references, and the generated context
   - Opens a new OpenCode session via `client.tui.executeCommand({ command: "session_new" })`
   - Appends the full prompt to the new session's input via `client.tui.appendPrompt()`
   - Shows a toast: "Handoff Ready — Review and edit the draft, then send"

3. **File injection on continuation**: The `chat.message` hook detects sessions starting with "Continuing work from session" text:
   - Parses `@file` references from the prompt text
   - Reads each referenced file, skips binary files
   - Builds synthetic text parts matching OpenCode's Read tool output format (with line numbers in `<file>` tags)
   - Injects them via `client.session.prompt()` with `noReply: true` to silently load file context

4. **Session cleanup**: `event` hook listens for `session.deleted` to remove processed session IDs from the tracking set.

### read_session Tool

5. **Previous session access**: The `read_session` tool lets the new session retrieve full conversation transcripts from the source session:
   - Uses `client.session.messages()` to fetch up to 500 messages
   - Formats as markdown transcript (## User / ## Assistant sections)
   - Provides escape hatch when handoff summary lacks detail

### Vendored Code

6. **OpenCode ReadTool compatibility**: `vendor.ts` contains code extracted from OpenCode's `packages/opencode/src/tool/read.ts` to ensure synthetic file parts match the Read tool output format exactly (line numbers, `<file>` tags, truncation markers).

## Key Files

| File | Purpose |
|------|---------|
| `src/plugin.ts` | Main plugin — /handoff command, chat.message hook for file injection, session cleanup |
| `src/tools.ts` | HandoffSession tool (new session + prompt) and ReadSession tool (transcript retrieval) |
| `src/files.ts` | @file reference parsing and synthetic TextPart construction |
| `src/vendor.ts` | Vendored OpenCode ReadTool code — isBinaryFile(), formatFileContent() |