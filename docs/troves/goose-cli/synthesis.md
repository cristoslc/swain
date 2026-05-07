# Synthesis: Goose CLI

## Key findings

- **Goose** is an AI agent CLI with 17 subcommands spanning interactive chat, programmatic execution, ACP server modes, extensions, scheduling, and gateway management.
- **Run mode** (`goose run`) supports headless execution from instruction files, stdin, or direct text, with recipe-driven agent configuration.
- **Session management** supports named sessions, resume, fork, export, and diagnostics — similar to swain's session concept but with built-in fork capability.
- **ACP (Agent Client Protocol)** is a first-class feature: `goose acp` on stdio, `goose serve` over HTTP/WebSocket on port 3284.
- **Extension system** supports three types: stdio extensions (`--with-extension`), HTTP extensions (`--with-streamable-http-extension`), and builtins (`--with-builtin`). Extensions can run inside containers via `--container`.
- **Recipes** are YAML-based agent configurations with validation, deeplinking, parameters, and sub-recipes.
- **Terminal integration** (`goose term`) provides shell-eval-based per-terminal persistent sessions with `@goose` / `@g` inline aliases.
- **Scheduling** (`goose schedule`) supports cron-based automated agent jobs with session tracking.
- **Gateway** (`goose gateway`) manages external platform integrations with pairing-based auth.
- **Local models** (`goose local-models`) supports searching, downloading, listing, and deleting GGUF models from HuggingFace.
- **Providers** include openai, anthropic, ollama, databricks, gemini-cli, claude-code, and others.

## Points of agreement

- Recipe system is the primary configuration mechanism for custom agent behavior.
- Extensions (skills/tools) are loadable from multiple sources (builtin, stdio, HTTP).

## Points of disagreement

- None — single-source CLI capture.

## Gaps

- No actual recipe file content captured — only CLI help output.
- No extension catalog or list of available builtins.
- No scheduling output format or notification mechanisms.
- No details on gateway pair/pairing protocol.
- Goose is also listed in the `agentic-coding-dual-modes` trove for its headless mode; this trove captures the full CLI surface.

## Related research

- `agentic-coding-dual-modes` — Goose headless mode compared with Codex, Gemini CLI, Aider, Qwen Code, and others.
