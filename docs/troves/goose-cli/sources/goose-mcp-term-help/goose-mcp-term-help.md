---
source-id: "goose-mcp-term-help"
title: "goose mcp/term --help"
type: cli-subcommand-help
tool-name: "goose"
command: "mcp, term"
depth: 1
fetched: 2026-05-05T02:45:00Z
---

# goose mcp --help

```
Run one of the mcp servers bundled with goose

Usage: goose mcp <SERVER>

Arguments:
  <SERVER>  

Options:
  -h, --help  Print help
```

# goose term --help

```
Runs a goose session tied to your terminal window.
Each terminal maintains its own persistent session that resumes automatically.

Setup:
  eval "$(goose term init zsh)"  # Add to ~/.zshrc

Usage:
  goose term run "list files in this directory"
  @goose "create a python script"  # using alias
  @g "quick question"  # short alias

Usage: goose term <COMMAND>

Commands:
  init  Print shell initialization script
  run   Run a prompt in the terminal session
  info  Print session info for prompt integration
  help  Print this message or the help of the given subcommand(s)

Options:
  -h, --help
          Print help (see a summary with '-h')
```
