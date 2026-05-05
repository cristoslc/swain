---
source-id: "goose-run-help"
title: "goose run --help"
type: cli-subcommand-help
tool-name: "goose"
command: "run"
depth: 1
fetched: 2026-05-05T02:45:00Z
---

# goose run --help

```
Execute commands from an instruction file or stdin

Usage: goose run [OPTIONS]

Options:
  -i, --instructions <FILE>
          Path to instruction file containing commands. Use - for stdin.

  -t, --text <TEXT>
          Input text containing commands for goose. Use this in lieu of the instructions argument.

      --recipe <RECIPE_NAME or FULL_PATH_TO_RECIPE_FILE>
          Recipe name to get recipe file or the full path of the recipe file that defines a custom agent configuration. Use --explain to see the recipe's title, description, and parameters.

      --system <TEXT>
          Provide additional system instructions to customize the agent's behavior

      --params <KEY=VALUE>
          Key-value parameters to pass to the recipe file. Can be specified multiple times.

      --sub-recipe <RECIPE>
          Specify sub-recipes to include alongside the main recipe. Can be:
            - Recipe names from GitHub (if GOOSE_RECIPE_GITHUB_REPO is configured)
            - Local file paths to YAML files
          Can be specified multiple times to include multiple sub-recipes.

      --explain
          Show the recipe title, description, and parameters

      --render-recipe
          Print the rendered recipe instead of running it.

  -n, --name <NAME>
          Specify a name for your chat session. When used with --resume, will resume this specific session if it exists.

      --session-id <SESSION_ID>
          Specify a session ID directly. When used with --resume, will resume this specific session if it exists.

      --path <PATH>
          Legacy parameter for backward compatibility. Extracts session ID from the file path.

  -s, --interactive
          Continue in interactive mode after processing initial input

      --no-session
          Execute commands without creating or using a session file. Useful for automated runs.

  -r, --resume
          Continue from a previous run, maintaining the execution state and context.

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

  -q, --quiet
          Quiet mode. Suppress non-response output, printing only the model response to stdout

      --output-format <FORMAT>
          Output format (text, json, stream-json)

          [default: text]
          [possible values: text, json, stream-json]

      --provider <PROVIDER>
          Override the GOOSE_PROVIDER environment variable for this run. Available providers include openai, anthropic, ollama, databricks, gemini-cli, claude-code, and others.

      --model <MODEL>
          Override the GOOSE_MODEL environment variable for this run. The model must be supported by the specified provider.

  -h, --help
          Print help (see a summary with '-h')
```
