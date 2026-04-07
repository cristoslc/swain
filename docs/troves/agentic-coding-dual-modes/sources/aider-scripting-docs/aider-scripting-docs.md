---
source-id: "aider-scripting-docs"
title: "Scripting aider | aider documentation"
type: web
url: "https://aider.chat/docs/scripting.html"
fetched: 2026-04-07T02:08:17Z
hash: "798dc631577b374436726a8fd88886357a8113eba6555a72c5eea4c57eab8e44"
---

# Scripting aider

Aider can be scripted via the command line or Python. It has no separate "server mode" or HTTP API — all scripting is CLI-flag or Python-API based.

## Command line

Use `--message` to give aider a single instruction. It applies edits and exits:

```bash
aider --message "make a script that prints hello" hello.js
```

Apply the same instruction across many files:

```bash
for FILE in *.py ; do
    aider --message "add descriptive docstrings to all the functions" $FILE
done
```

### Key flags for scripting

| Flag | Description |
|---|---|
| `--message COMMAND` / `-m` | Single message; process reply then exit (disables chat mode) |
| `--message-file FILE` / `-f` | Read message from file; process reply then exit |
| `--yes` | Always say yes to every confirmation |
| `--no-stream` | Disable streaming responses |
| `--auto-commits` / `--no-auto-commits` | Enable/disable auto-commit of changes (default: enabled) |
| `--dry-run` | Perform a dry run without modifying files |
| `--commit` | Commit all pending changes with a suitable commit message, then exit |

## Python API

```python
from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput

fnames = ["greeting.py"]
model = Model("gpt-4-turbo")

# Auto-accept confirmations
io = InputOutput(yes=True)

coder = Coder.create(main_model=model, fnames=fnames, io=io)

# Execute one instruction and return
coder.run("make a script that prints hello world")
coder.run("make it say goodbye")

# In-chat commands work too
coder.run("/tokens")
```

Note: The Python API is not officially supported or documented and may change without backwards compatibility.

## Architecture notes

Aider is a **pure CLI tool** — the interactive mode IS the primary mode, and scripting is done by suppressing the interactive prompts. There is no HTTP server, no TUI in the Bubble Tea / Ink sense, and no separate headless process. The "headless" pattern in aider is: pass `--message` and `--yes` to fully automate a single run.

Aider builds a **repository map** of the codebase, which it uses to give the LLM context. This runs in both interactive and scripted modes.

Aider's interactive mode is a REPL-style terminal session (not a rich TUI with panels/windows). It reads stdin and writes to stdout with ANSI formatting.
