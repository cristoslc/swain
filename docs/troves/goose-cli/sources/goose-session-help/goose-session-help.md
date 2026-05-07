---
source-id: "goose-session-help"
title: "goose session --help"
type: cli-subcommand-help
tool-name: "goose"
command: "session"
depth: 1
fetched: 2026-05-05T02:45:00Z
---

# goose session --help

```
Start or resume interactive chat sessions

Usage: goose session [OPTIONS] [COMMAND]

Commands:
  list         List all available sessions
  remove       Remove sessions. Runs interactively if no ID, name, or regex is provided.
  export       Export a session
  diagnostics  
  help         Print this message or the help of the given subcommand(s)

Options:
  -n, --name <NAME>
          Specify a name for your chat session. When used with --resume, will resume this specific session if it exists.

      --session-id <SESSION_ID>
          Specify a session ID directly. When used with --resume, will resume this specific session if it exists.

      --path <PATH>
          Legacy parameter for backward compatibility. Extracts session ID from the file path.

  -r, --resume
          Continue from a previous session. If --name or --session-id is provided, resumes that specific session. Otherwise, resumes the most recently used session.

      --fork
          Create a new session by copying all messages from a previous session. Must be used with --resume. If --name or --session-id is provided, forks that specific session. Otherwise, forks the most recently used session.

      --history
          Show previous messages when resuming a session

      --debug
          When enabled, shows complete tool responses without truncation and full paths.

      --max-tool-repetitions <NUMBER>
          Set a limit on how many times the same tool can be called consecutively with identical parameters. Helps prevent infinite loops.

      --max-turns <NUMBER>
          Set a limit on how many turns (iterations) the agent can take without asking for user input to continue.

      --container <CONTAINER_ID>
          Run extensions (stdio and built-in) inside the specified container. The extension must exist in the container. For built-in extensions, goose must be installed inside the container.

      --with-extension <COMMAND>
          Add stdio extensions from full commands with environment variables. Can be specified multiple times. Format: 'ENV1=val1 ENV2=val2 command args...'

      --with-streamable-http-extension <URL>
          Add streamable HTTP extensions from a URL. Can be specified multiple times. Format: 'url...' or 'url... timeout=100' to set up timeout other than default

      --with-builtin <NAME>
          Add one or more builtin extensions that are bundled with goose by specifying their names, comma-separated

      --no-profile
          Don't load your default extensions, only use CLI-specified extensions

  -h, --help
          Print help (see a summary with '-h')
```
