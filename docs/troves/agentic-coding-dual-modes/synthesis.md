---
trove: agentic-coding-dual-modes
synthesized: 2026-04-07
sources: 13
related-troves:
  - opencode-crush-cli (opencode serve/run; Crush has no server mode)
  - claude-code-remote-interaction (claude -p; remote control; Agent SDK)
---

# Agentic coding environments — headful and headless modes

## Overview of the landscape (14 tools)

| Tool | Headful mode | Headless trigger | Output format | HTTP server? | Skills/extensions |
|---|---|---|---|---|---|
| **Claude Code** | Interactive TUI | `claude -p "prompt"` | text, JSON, stream-JSON | No (Agent SDK) | SKILL.md files in `.claude/skills/` |
| **opencode** | TUI (client/server) | `opencode serve` + `opencode run` | REST API, JSON | **Yes** | No native skills system |
| **Codex CLI** | Interactive TUI | `codex exec "prompt"` | text, JSONL | App Server + MCP Server | No skills; MCP only |
| **Gemini CLI** | Interactive TUI | `gemini -p "prompt"` or non-TTY | text, JSON, stream-JSON (JSONL) | No (ACP mode) | No skills; MCP only |
| **Qwen Code** | Interactive TUI | `qwen -p "prompt"` or non-TTY | text, JSON, stream-JSON | No (TypeScript SDK) | SKILL.md (Claude Code fork) |
| **Aider** | REPL terminal | `aider --message "..." --yes` | stdout text only | No (Python API) | No skills/extensions |
| **Goose** | Interactive TUI or desktop app | `goose run -t "prompt"` | text, JSON, stream-JSON | Yes (goosed server, internal) | Extensions (MCP) + Recipes (YAML) |
| **Amp** | VS Code extension or CLI (TTY) | `amp -x "prompt"` | text (stdout) | No | Toolboxes (shell scripts) + Agent Skills + MCP |
| **Cline** | VS Code extension or CLI (TTY) | `cline -y "task"` | text, JSON (`--json`) | No (ACP) | Skills (SKILL.md, on-demand) + MCP |
| **Plandex** | Terminal REPL | `plandex tell ... --full --apply --skip-menu` | text only | No (internal server) | No skills/extensions; model packs only |
| **Amazon Q / Kiro** | Interactive TUI (`q chat`) | `q chat --no-interactive "prompt"` | text only | No | "Agents" (named configs); AWS-internal only |
| **Continue CLI** | Interactive TUI (`cn`) | `cn -p "prompt"` | text only | No | Rules + Checks + Hub agents + MCP |
| **GitHub Copilot CLI** | Interactive TUI (`copilot`) | `copilot -p "prompt"` | text only | No | No skills; GitHub MCP Server pre-configured |
| **Roo Code CLI** | Interactive TUI | stdin NDJSON stream | stream-JSON or JSON | No | Custom Modes (Code/Architect/Ask + user-defined) |

*Coverage notes: Claude Code and opencode are covered in depth in the related troves
`claude-code-remote-interaction` and `opencode-crush-cli`. This trove covers the remaining 12 tools.*

---

## Theme 1 — The `-p` / `--prompt` flag is the universal headless trigger

Every Claude Code derivative (Claude Code, Gemini CLI, Qwen Code) uses `-p` / `--prompt`
to trigger headless mode. Continue and GitHub Copilot CLI follow the same pattern.
Goose uses `goose run -t`. Aider uses `--message`. Amp uses `-x`. Cline uses `-y`.
Plandex requires combined flags. Amazon Q uses `--no-interactive`. Roo Code is
unique — it has no headless flag at all; it uses a stdin NDJSON stream protocol.

```bash
claude -p "review src/auth.py"           # Claude Code
gemini -p "review src/auth.py"            # Gemini CLI
qwen -p "review src/auth.py"              # Qwen Code
cn -p "review src/auth.py"               # Continue CLI
copilot -p "review src/auth.py"           # GitHub Copilot CLI
codex exec "review src/auth.py"           # Codex CLI
aider --message "review src/auth.py" --yes src/auth.py  # Aider
goose run -t "review src/auth.py"         # Goose
amp -x "review src/auth.py"               # Amp
cline -y "review src/auth.py"             # Cline
q chat --no-interactive "review src/auth.py"  # Amazon Q / Kiro
plandex load src/auth.py && plandex tell "review src/auth.py" --full --apply --skip-menu  # Plandex
# Roo Code: write {"type":"start","task":"review src/auth.py"} to stdin
```

---

## Theme 2 — JSON / stream-JSON output is common but not universal

| Tool | Flag | Format |
|---|---|---|
| Claude Code | `--output-format json` | JSON array of message objects |
| Claude Code | `--output-format stream-json` | JSONL events |
| Gemini CLI | `--output-format json` | Single JSON object |
| Gemini CLI | `--output-format stream-json` | JSONL events |
| Qwen Code | `--output-format json` | JSON array (buffered) |
| Qwen Code | `--output-format stream-json` | JSONL (streaming) |
| Codex CLI | `--json` | JSONL events |
| Goose | `--output-format json/stream-json` | Matches the claude/gemini pattern |
| Roo Code | `stream-json` / `json` (via `JsonEventEmitter`) | NDJSON or buffered JSON |
| Cline | `--json` | JSON output for scripting |
| Aider | none | Plain text only |
| Amp | none documented | Plain text only |
| Plandex | none | Plain text only |
| Amazon Q / Kiro | none documented | Plain text only |
| Continue CLI | none documented | Plain text only |
| GitHub Copilot CLI | none documented | Plain text only |

Six tools lack JSON output (Aider, Amp, Plandex, Amazon Q, Continue, Copilot CLI).
These require shell parsing in machine-driven pipelines.

---

## Theme 3 — Three architectures for server mode

### A. CLI-flag headless (pure subprocess model)
Claude Code, Gemini CLI, Qwen Code, Aider, Amp, Cline, Continue, GitHub Copilot CLI — start
a fresh process per run. No persistent server. State carried via `--continue` / `--resume`.

### B. HTTP server (opencode and Goose)
opencode exposes a full public REST API (`opencode serve`). Goose runs an internal
server (`goosed`) used by the desktop app. Not a public API but exposed via ACP
for external orchestration.

### C. REPL with internal server (Plandex)
Plandex runs an internal server that the CLI connects to. Tasks can run in the
background (`--bg`) and be reattached later (`plandex connect`).

### D. Stdin stream protocol (Roo Code — unique)
Roo Code is the only tool in this set that uses a structured NDJSON stdin protocol
instead of CLI flags. Commands are JSON objects written to stdin:

```json
{"type":"start","task":"Fix TypeScript errors","sessionId":"abc-123"}
{"type":"message","content":"Focus on strict null checks"}
{"type":"cancel"}
{"type":"shutdown"}
```

This design is for embedding in orchestration systems, not shell scripts.
All other tools accept their task as a flag or argument.

---

## Theme 4 — Session continuity in headless runs

| Tool | Session resume | Background tasks |
|---|---|---|
| **opencode** | `opencode run --attach http://localhost:4096` | Server handles persistence |
| **Claude Code** | `claude --continue` / `--resume <id>` | No |
| **Codex CLI** | `codex exec resume --last` / `codex exec resume <id>` | No |
| **Qwen Code** | `qwen --continue` / `--resume <id>` | No |
| **Gemini CLI** | Session management + checkpointing | No |
| **Aider** | No — each `--message` run is independent | No |
| **Goose** | `goose session --resume last` / `--fork` | Scheduled recipes (`goose schedule`) |
| **Amp** | Server-side Threads, accessible from any device | No |
| **Cline** | `--continue` / `--resume <id>` | No |
| **Plandex** | Plans are persistent on the Plandex server | `plandex tell --bg` + `plandex connect` |
| **Amazon Q / Kiro** | `q chat --resume` | No |
| **Continue CLI** | `cn --resume` | No |
| **GitHub Copilot CLI** | `copilot --resume` (selects from recent sessions) | No |
| **Roo Code** | Pass same `sessionId` in `start` command | No |

Amp's server-side thread model is unique — threads accessible across devices and teammates.
Plandex's background streams can survive terminal closure without a full HTTP server.

---

## Theme 5 — Auto-approval and permission models

| Tool | Fine-grained control | Persistent permissions | Auto-approve flag |
|---|---|---|---|
| **Claude Code** | `dangerouslyAllowedCommands` in project config | `.claude/settings.json` | `--dangerously-skip-permissions` |
| **Continue CLI** | `--allow`, `--ask`, `--exclude` with glob patterns | `~/.continue/permissions.yaml` | None |
| **GitHub Copilot CLI** | `--allow-tool <glob>`, `--deny-tool <glob>` | Session only | `--allow-all-tools` |
| **Codex CLI** | `--approval-policy` (full/manual/auto) | None documented | `--full-auto` |
| **Cline** | `-y` bypass approval | Per-project config | `-y` flag |
| **Plandex** | 5-level autonomy system (`--no-auto` to `--full`) | Plan context | `--full` |
| **Goose** | `GOOSE_MODE=auto` env var | None documented | `GOOSE_MODE=auto` |
| **Amazon Q / Kiro** | None documented | None documented | `--trust-all-tools` |
| **Amp** | `amp permissions edit` (configure rules upfront) | Project-level config | `-x` headless mode |
| **Roo Code** | `--require-approval` to *enforce* human review | None documented | None |
| **Aider** | None | None | `--yes-always` |

**Key finding:** Continue CLI is the only tool with *persistent* fine-grained
per-tool permission accumulation across sessions. All others reset on session restart
or offer only session-level whitelisting.

**Roo Code is notable in the opposite direction** — it has a `--require-approval` flag
to enforce human confirmation, but no documented bypass. This makes it the most
conservative option for high-risk automated contexts.

Continue CLI's permission model is the most operator-friendly for team CI setups:
lock down permissions once in `permissions.yaml`, commit it, and every CI run is
constrained to the approved tool surface.

**GitHub Copilot CLI** adds a second unique control: a per-directory trust gate.
The agent cannot read files in an untrusted directory, period. This is the only
hard filesystem boundary in this set.

---

## Theme 6 — The skills/extensions dimension

### Skills (markdown instruction files, on-demand)
- **Claude Code** — SKILL.md files in `.claude/skills/`; on-demand loading via `use_skill` tool.
- **Qwen Code** — Inherits Claude Code's skill mechanism (fork).
- **Cline** — Same SKILL.md convention; `.cline/skills/` or `.claude/skills/` (cross-tool compatible).
- **Amp** — "Agent Skills" (instruction files); `.claude/skills/` as a fallback for compatibility.

All four share the same skill architecture: a markdown file with YAML frontmatter
(`name`, `description`) and a body of instructions. Cline's progressive loading
(metadata always loaded, instructions only when triggered) is the most token-efficient.

### Modes (Roo Code)
Roo Code adds a Mode layer on top of Cline's Plan/Act pattern. Each Mode
has its own system prompt and tool permissions. Built-in: Code, Architect, Ask.
Custom modes are user-defined. Modes persist per-task and are usable in headless operation.

### Extensions (MCP servers / tool plugins)
- **Goose** — Extensions are MCP servers. Built-ins (`developer`, `computer-controller`),
  plus any stdio or HTTP MCP server. Loaded at session start; addable mid-session via `/extension`.
- **Cline** — MCP servers in `cline.mcp.json`. Cline can build new MCP servers on demand.
- **GitHub Copilot CLI** — Ships the GitHub MCP Server pre-configured. Capabilities come from MCP, not hardcoded integrations.
- **Continue CLI** — MCP tools configured in `config.yaml`, shared with IDE extensions.
- **Claude Code**, **Codex CLI**, **Gemini CLI**, **Qwen Code** — MCP via standard config.
- **Plandex**, **Aider**, **Amazon Q / Kiro** — No MCP or extension system.

### Toolboxes (shell scripts, lightweight)
- **Amp only** — Toolboxes are executables in a directory. Each self-describes via
  `TOOLBOX_ACTION=describe` and executes via `TOOLBOX_ACTION=execute`. No server,
  no JSON-RPC, no manifest. Lowest barrier to custom tooling.

### CI agents (Continue Checks)
- **Continue CLI only** — Agents-as-GitHub-PR-status-checks. Markdown files in
  `.continue/checks/` define CI checks that run on every pull request and post a
  green/red status check. The only tool in this set with a native PR-integrated CI story.

### Recipes / workflows (reusable parameterized pipelines)
- **Goose** — Recipes are YAML files with `title`, `prompt`, `instructions`, and `parameters`.
  Can call sub-recipes. Runnable headlessly. Schedulable with cron via `goose schedule`.
- **Others** — No equivalent mechanism.

---

## Theme 7 — Security: prompt injection and the skills attack surface

The arxiv SoK (2601.17548v1) identifies auto-loaded configuration files as the
highest-risk prompt injection vector for agentic coding tools.

**AIShellJack attack:** Malicious `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`,
or skill files placed in a repository are processed as trusted configuration when
the tool opens the directory. The agent executes arbitrary instructions embedded in
those files.

**Tool poisoning (Invariant Labs):** MCP tool descriptions can embed instructions
for the LLM, hidden from the user but processed by the model. No integrity guarantee
exists in the MCP protocol for tool description content.

**Rug-pull attacks:** An MCP server initially presents safe tool definitions, then
updates descriptions after the operator has approved the server. The ETDI proposal
(arXiv:2506.01333) addresses this with cryptographic signing.

**Key risk factors by tool:**
- Tools with auto-loaded config files (CLAUDE.md, .cursorrules) are the highest-risk
  category for indirect prompt injection from repository content.
- Tools with broad MCP server support (Goose, Cline, Claude Code) have wider
  tool poisoning surface.
- Tools with no extension system (Aider, Plandex) have limited injection surface
  but also no mitigation tooling.
- GitHub Copilot CLI's directory trust model is the only per-directory filesystem
  boundary; it reduces attack surface compared to tools that auto-trust the working directory.

**NVIDIA AI Red Team guidance:**
OS-level controls complement per-tool permissions:
- Block network egress to an allowlist.
- Restrict file system writes to the project directory; protect `~/.ssh/`, `~/.aws/`.
- Run agents as minimal-privilege users; avoid root.
- Containerize agentic processes (Docker, Firecracker) for hard host isolation.

These controls remain effective even when agent-level gates are bypassed
(e.g., `--allow-all-tools`, `GOOSE_MODE=auto`).

**Meta's Rule of Two** (cited in arXiv SoK): an agent should satisfy no more than
two of these simultaneously: (A) processing untrusted inputs, (B) accessing sensitive
data, (C) changing state or communicating externally. Headless CI runs that read
arbitrary repository content while having write access to credentials satisfy all three.

---

## Theme 8 — CI/CD authentication maturity varies widely

| Tool | CI auth path | Maturity |
|---|---|---|
| **Claude Code** | `ANTHROPIC_API_KEY` env var | High — standard API key |
| **Codex CLI** | `OPENAI_API_KEY` env var | High — standard API key |
| **Gemini CLI** | `GEMINI_API_KEY` env var | High — standard API key |
| **Qwen Code** | `DASHSCOPE_API_KEY` env var | High |
| **Aider** | Provider API key env vars | High |
| **Continue CLI** | `CONTINUE_API_KEY` env var | High |
| **Goose** | Provider key env vars | Medium — provider-dependent |
| **Amp** | `AMP_API_KEY` env var | High |
| **Cline** | Provider API key env vars | High |
| **GitHub Copilot CLI** | `GH_TOKEN` / `GITHUB_TOKEN` PAT | Medium — org admin config required |
| **Plandex** | `PLANDEX_API_KEY` or self-hosted | High |
| **Amazon Q / Kiro** | OAuth device flow (browser) or IAM role | Low — no API key; CI-blocking |
| **Roo Code** | Provider key env vars | High |

**Amazon Q / Kiro is the outlier** — its CI path requires either browser-based
OAuth (impossible in headless CI) or an AWS IAM role (only available in AWS-managed
compute). This is an explicitly documented gap in GitHub issue #808.

---

## Points of agreement (13-source set)

- All tools work in both interactive and non-interactive modes.
- All tools share the same codebase for both modes — headless is not a separate binary.
- All tools support plain text output as the default headless format.
- All tools require some form of explicit auto-approve configuration for CI use.
- All tools that follow the Claude Code architecture (Qwen Code, Cline, Amp, Roo Code fork of Cline) share compatible SKILL.md conventions.
- MCP is the dominant extension mechanism; every tool that has extensions uses MCP.

---

## Points of disagreement

- **JSON output**: Claude Code, Gemini CLI, Qwen Code, Codex CLI, Goose, Roo Code, and Cline support JSON.
  Aider, Amp, Plandex, Amazon Q, Continue, and GitHub Copilot CLI do not.
- **Headless protocol**: Roo Code uses stdin NDJSON instead of CLI flags — unique in this set.
- **HTTP server**: Only opencode exposes a public REST API.
- **Permission persistence**: Continue CLI is the only tool with cross-session persistent fine-grained permissions.
- **Filesystem boundary**: GitHub Copilot CLI is the only tool with a hard per-directory trust gate.
- **Skills vs. Modes**: Claude Code family uses markdown SKILL.md files. Roo Code uses Modes (system prompt + scoped tool permissions per persona).
- **CI agents**: Continue CLI's GitHub Checks is the only PR-integrated CI story.
- **Model routing**: Plandex is unique in assigning different models to different roles (planner, coder, builder) within a plan.
- **Extension barrier**: Amp's Toolboxes (plain shell scripts) require no MCP server setup. All other extension mechanisms require MCP configuration.
- **CI auth gap**: Amazon Q / Kiro is the only tool where CI authentication is genuinely unsolved.

---

## Gaps (residual after second extension)

- Startup / cold-boot costs (MCP initialization overhead is a known pain point) are not covered by any source.
- Cursor and Windsurf (IDE-embedded) are confirmed absent; different dual-mode story.
- Amp's headless output format remains underdocumented.
- Plandex's scripting story requires multiple flags; a dedicated headless mode is an open issue.
