---
title: "Model Selection Mechanisms Across Agent Runtimes"
artifact: SPIKE-013
track: container
status: Complete
author: cristos
created: 2026-03-13
last-updated: 2026-03-13
research-date: 2026-03-13
question: "How does each target agent runtime (Claude Code, Codex, OpenCode, Cursor, Copilot, Gemini CLI) expose model selection and reasoning effort control — and what is the correct instruction format for each?"
gate: Pre-EPIC-007-specs
risks-addressed:
  - Runtime-specific annotations may conflict or cause errors in runtimes that don't understand them
  - Some runtimes may have no model selection mechanism — fallback must be a safe no-op
  - Reasoning effort APIs (extended-thinking, budget tokens) differ across providers and may not map cleanly
linked-artifacts:
  - EPIC-007
trove: ""
---

# Model Selection Mechanisms Across Agent Runtimes

## Question

How does each target agent runtime (Claude Code, Codex, OpenCode, Cursor, Copilot, Gemini CLI) expose model selection and reasoning effort control — and what is the correct instruction format for each?

## Go / No-Go Criteria

**Go:** For each runtime, produce: (a) the mechanism for steering model selection (config key, prompt annotation, environment variable, none), (b) the mechanism for reasoning effort / extended thinking, (c) a safe fallback instruction that is a no-op if the runtime ignores it, and (d) the instruction format to embed in SKILL.md files.

**No-Go:** No runtime-agnostic instruction format exists that is safe across all targets. In that case, produce a conditional block format (runtime-keyed sections) and flag runtimes that require separate skill file variants.

## Pivot Recommendation

If no-go: design a runtime-keyed annotation block (e.g., `<!-- runtime: claude-code -->` fenced sections) so each runtime reads only its relevant instructions. skill-creator handles the block insertion.

## Findings

### Summary Table

| Runtime | Model Selection Mechanism | Reasoning Effort Mechanism | Instruction File | Can Embed Model Hints in Instructions? |
|---------|--------------------------|---------------------------|-----------------|---------------------------------------|
| **Claude Code** | `model` in settings.json, `--model` flag, `ANTHROPIC_MODEL` env var | `effortLevel` in settings.json, `CLAUDE_CODE_EFFORT_LEVEL` env var (low/medium/high) | `CLAUDE.md` | No -- model selection is out-of-band (settings/env/CLI flag), not in instruction text |
| **Codex (OpenAI)** | `model` in `~/.codex/config.toml`, `--model`/`-m` flag | `model_reasoning_effort` in config.toml (minimal/low/medium/high/xhigh) | `AGENTS.md` | No -- model and reasoning are config-file settings, not instruction-file directives |
| **OpenCode** | `model` in `opencode.json` (`provider/model-id`), per-agent `model` override | Provider-specific: `reasoningEffort` (OpenAI), `thinking.budgetTokens` (Anthropic) in provider config | `AGENTS.md` | No -- model config is in opencode.json, AGENTS.md is for behavioral instructions |
| **Cursor** | UI model picker, per-request model switching | Thinking toggle (brain icon), effort levels (low/medium/high/max) via UI | `.cursor/rules/*.mdc` | No -- MDC rules only support `description`, `globs`, `alwaysApply` frontmatter; no model fields |
| **GitHub Copilot** | `--model` flag, `/model` command, Auto mode | `--reasoning-effort` flag, Ctrl+T reasoning toggle | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` | No -- instructions are behavioral; model is selected via CLI flag or UI |
| **Gemini CLI** | `-m` flag, `/model` command | `thinkingConfig.thinkingBudget` in `~/.gemini/settings.json` (0-24576) | `GEMINI.md` | No -- GEMINI.md is context/instructions only; model config is in settings.json |
| **Aider** | `--model` flag, `AIDER_MODEL` env var | `--reasoning-effort` (low/medium/high), `--thinking-tokens` (e.g., "8k", "0") | `.aider.model.settings.yml` | Partially -- `.aider.model.settings.yml` configures per-model reasoning settings, but this is model config, not instruction text |

### Key Finding: No Runtime Accepts Model Hints in Instruction Files

**Every runtime separates model configuration (which model, how much reasoning) from behavioral instructions (what to do, how to behave).** No runtime allows embedding model selection directives inside its instruction/context file (CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, copilot-instructions.md). Model routing is always an out-of-band concern handled through settings files, environment variables, or CLI flags.

This means SKILL.md files **cannot directly steer model selection**. Instead, model steering must be expressed as:
1. **Advisory natural-language hints** that an agent can interpret if it has access to model-switching APIs
2. **Separate configuration overlays** that live alongside skill files

---

### Runtime Details

#### 1. Claude Code (Anthropic)

**Model selection:**
- `settings.json` (user: `~/.claude/settings.json`, project: `.claude/settings.json`): `"model": "opus"` or full model name
- CLI: `claude --model opus`
- Environment: `ANTHROPIC_MODEL=opus`
- In-session: `/model sonnet`
- Model aliases: `default`, `sonnet`, `opus`, `haiku`, `sonnet[1m]`, `opusplan`
- Subagent override: `CLAUDE_CODE_SUBAGENT_MODEL` env var

**Reasoning effort:**
- `settings.json`: `"effortLevel": "high"` (values: `low`, `medium`, `high`)
- Environment: `CLAUDE_CODE_EFFORT_LEVEL=low|medium|high`
- In-session: `/model` then arrow keys to adjust effort slider
- Supported on Opus 4.6 and Sonnet 4.6
- To disable adaptive reasoning: `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=1` (reverts to fixed `MAX_THINKING_TOKENS` budget)

**Instruction file:** `CLAUDE.md` at project root or `~/.claude/CLAUDE.md` globally. Plain markdown, no frontmatter. Content is prepended to system context.

**Safe fallback instruction for SKILL.md:**
```
Recommended model tier: heavy-reasoning (e.g., Opus-class).
If your runtime supports reasoning effort controls, use high effort for this task.
```
This is a natural-language hint. Claude Code will not parse it as a directive, but an agent reading a SKILL.md may act on it if instructed to do so in AGENTS.md.

**What happens with unknown annotations:** Treated as plain text in the instruction context. No error, no special behavior -- simply ignored as prose.

#### 2. Codex (OpenAI)

**Model selection:**
- Config: `~/.codex/config.toml` with `model = "gpt-5-codex"`
- CLI: `codex --model gpt-5-codex` or `codex -m gpt-5-codex`
- In-session: `/model`
- Profile-scoped: `[profiles.<name>] model = "..."` in config.toml

**Reasoning effort:**
- Config: `model_reasoning_effort = "minimal|low|medium|high|xhigh"` in config.toml
- Plan-mode override: `plan_mode_reasoning_effort` in config.toml
- Reasoning summary: `model_reasoning_summary = "auto|concise|detailed|none"`
- No CLI flag for reasoning effort (config-only)

**Instruction file:** `AGENTS.md` at project root. Plain markdown. Discovery: `AGENTS.override.md` > `AGENTS.md` > fallback names. Files concatenated from project root down to CWD. Max 32 KiB combined (configurable via `project_doc_max_bytes`). Fallback filenames configurable in config.toml: `project_doc_fallback_filenames = ["TEAM_GUIDE.md"]`.

**Safe fallback instruction for SKILL.md:**
```
This task benefits from high reasoning effort. If your runtime supports
reasoning effort configuration, consider using high or xhigh.
```

**What happens with unknown annotations:** Treated as instruction text. No error -- Codex reads AGENTS.md as plain markdown and sends it to the model as context.

#### 3. OpenCode

**Model selection:**
- Config: `opencode.json` with `"model": "anthropic/claude-sonnet-4-20250514"`
- Per-agent override: `"agent": { "plan": { "model": "anthropic/claude-haiku-4-20250514" } }`
- Model ID format: `provider_id/model_id`
- In-session: model switching available via UI

**Reasoning effort:**
- OpenAI models: `"options": { "reasoningEffort": "high" }` in provider model config
- Anthropic models: `"options": { "thinking": { "type": "enabled", "budgetTokens": 16000 } }`
- Variants: define named config variants per model (e.g., `"high"`, `"fast"`)
- Variant switching: `variant_cycle` keybind during session

**Instruction file:** `AGENTS.md` at project root or `~/.config/opencode/AGENTS.md` globally. Also reads `CLAUDE.md`. Can reference remote URLs for instructions. Plain markdown.

**Safe fallback instruction for SKILL.md:**
```
This task requires deep reasoning. If your runtime supports model variants
or reasoning effort settings, use the highest available tier.
```

**What happens with unknown annotations:** Treated as context text. OpenCode passes instruction file content to the model as system context.

#### 4. Cursor

**Model selection:**
- UI-only: model picker in IDE (Settings > Models)
- Per-request: users can switch models between turns
- Agent mode supports parallel agent execution with different models
- No file-based or env-based model configuration

**Reasoning effort:**
- Thinking toggle (brain icon) in UI: switches to thinking-capable model variants
- Effort levels: low, medium, high, max (max is Opus 4.6 only)
- "Ultrathink" convenience toggle: sets effort to high for one turn
- No config-file or env-var control

**Instruction file:** `.cursor/rules/*.mdc` files with frontmatter:
```markdown
---
description: "Rule description"
globs: ["src/**/*.ts"]
alwaysApply: false
---
Rule content here...
```
Four rule types: Always, Auto Attached (glob-based), Agent Requested (description-matched), Manual (@mention). Legacy `.cursorrules` still works.

**Safe fallback instruction for SKILL.md:**
```
This task involves complex reasoning. Consider using a thinking-capable model
with high effort if your editor supports it.
```

**What happens with unknown annotations:** MDC frontmatter only supports `description`, `globs`, `alwaysApply`. Unknown fields in frontmatter are silently ignored. Rule body content is plain markdown passed as context.

#### 5. GitHub Copilot (CLI and IDE)

**Model selection:**
- CLI: `copilot --model gpt-5.3-codex`
- In-session: `/model`
- Auto mode: automatically selects best available model
- Available: Claude Opus 4.6, Claude Sonnet 4.6, GPT-5.x-Codex variants, Gemini 3 Pro

**Reasoning effort:**
- CLI: `--reasoning-effort` flag (for GPT models with extended thinking)
- In-session: Ctrl+T toggles reasoning visibility
- No config-file persistence for reasoning effort

**Instruction file:** `.github/copilot-instructions.md` (repo-wide), `.github/instructions/*.instructions.md` (path-specific with `applyTo` frontmatter). Also reads `AGENTS.md`. Path-specific format:
```markdown
---
applyTo: "**/*.ts,**/*.tsx"
excludeAgent: "code-review"
---
Instructions here...
```

**Safe fallback instruction for SKILL.md:**
```
This task benefits from deep reasoning. If your runtime supports a
reasoning effort setting, use a higher level.
```

**What happens with unknown annotations:** Instructions are plain markdown. Unknown frontmatter fields in `.instructions.md` files are ignored. Body text is passed as context.

#### 6. Gemini CLI (Google)

**Model selection:**
- CLI flag: `gemini -m gemini-2.5-pro`
- In-session: `/model`
- Config: model aliases in `~/.gemini/settings.json` via `modelConfigs.customAliases`
- Available: Gemini 2.5 Pro/Flash, Gemini 3 Pro/Flash

**Reasoning effort:**
- Settings: `thinkingConfig.thinkingBudget` in `~/.gemini/settings.json` (0-24576 tokens)
- Per-agent override via `modelConfigs.overrides` with scope matching
- `thinkingBudget: -1` enables dynamic thinking (model adjusts based on complexity)
- `thinkingBudget: 0` disables thinking
- Gemini 3 models use `thinkingLevel: "HIGH"` instead of numeric budget

Example settings.json:
```json
{
  "modelConfigs": {
    "overrides": [{
      "match": { "overrideScope": "codebaseInvestigator" },
      "modelConfig": {
        "generateContentConfig": {
          "thinkingConfig": { "thinkingBudget": 4096 }
        }
      }
    }]
  }
}
```

**Instruction file:** `GEMINI.md` at project root, `~/.gemini/GEMINI.md` globally. Supports `@./path/file.md` imports. All found files concatenated. Configurable filename: `context.fileName` in settings.json can include `["AGENTS.md", "GEMINI.md"]`.

**Safe fallback instruction for SKILL.md:**
```
This task requires deep analysis. If your runtime supports thinking budget
or reasoning effort controls, use a high setting.
```

**What happens with unknown annotations:** GEMINI.md is plain markdown context. All content is concatenated and sent as system context. No parsing of directives -- unknown text is treated as instructions.

#### 7. Aider

**Model selection:**
- CLI: `aider --model claude-sonnet-4-20250514`
- Environment: `AIDER_MODEL=...`
- Config: `.aider.conf.yml` with `model: claude-sonnet-4-20250514`
- Separate models for different roles: `--weak-model` (commits/summaries), `--editor-model`
- Legacy shortcuts: `--opus`, `--sonnet`, `--haiku`, `--4o`

**Reasoning effort:**
- CLI: `--reasoning-effort low|medium|high` (env: `AIDER_REASONING_EFFORT`)
- CLI: `--thinking-tokens 8k` (env: `AIDER_THINKING_TOKENS`) -- values like "1024", "1k", "8k", "0.01M", "0" to disable
- In-chat: `/reasoning-effort low`, `/thinking-tokens 4k`
- Model settings YAML (`.aider.model.settings.yml`): `accepts_settings: ["reasoning_effort"]` or `accepts_settings: ["thinking_tokens"]`
- `reasoning_tag` for models that wrap thinking in XML tags (e.g., DeepSeek R1 uses `<think>`)

**Instruction file:** No dedicated project instruction file like AGENTS.md. Aider uses `.aider.conf.yml` for configuration and `.aider.model.settings.yml` for per-model behavior tuning. No equivalent of CLAUDE.md/AGENTS.md for free-form project instructions.

**Safe fallback instruction for SKILL.md:**
```
This task benefits from extended reasoning. If using Aider, consider
--reasoning-effort high or --thinking-tokens 8k.
```

**What happens with unknown annotations:** Not applicable -- Aider does not read project instruction files. Model settings YAML validates known fields; unknown fields are ignored without error.

---

### Cross-Runtime Analysis

#### Instruction file compatibility matrix

| File | Claude Code | Codex | OpenCode | Cursor | Copilot | Gemini CLI | Aider |
|------|-------------|-------|----------|--------|---------|------------|-------|
| `CLAUDE.md` | Native | -- | Read | -- | -- | -- | -- |
| `AGENTS.md` | Native | Native | Native | -- | Read | Configurable | -- |
| `GEMINI.md` | -- | -- | -- | -- | -- | Native | -- |
| `.cursor/rules/*.mdc` | -- | -- | -- | Native | -- | -- | -- |
| `.github/copilot-instructions.md` | -- | -- | -- | -- | Native | -- | -- |
| `.cursorrules` | -- | -- | -- | Legacy | -- | -- | -- |

"Native" = primary instruction file. "Read" = the runtime discovers and reads this file. "Configurable" = can be configured to read via settings. "--" = not read.

**Key observation:** `AGENTS.md` has the broadest native reach (Claude Code, Codex, OpenCode, Copilot). Gemini CLI can be configured to read it. Cursor and Aider do not read it.

#### Model selection mechanism categories

1. **Config-file + CLI flag + env var** (full out-of-band control): Claude Code, Codex, Aider
2. **Config-file + CLI flag** (no env var for model): OpenCode, Gemini CLI, Copilot CLI
3. **UI-only** (no file/env control): Cursor

#### Reasoning effort mechanism categories

1. **Config-file + env var**: Claude Code (`effortLevel` + `CLAUDE_CODE_EFFORT_LEVEL`)
2. **Config-file only**: Codex (`model_reasoning_effort`), OpenCode (provider options), Gemini CLI (`thinkingConfig`)
3. **CLI flag only**: Aider (`--reasoning-effort`, `--thinking-tokens`), Copilot CLI (`--reasoning-effort`)
4. **UI-only**: Cursor (thinking toggle, effort slider)

---

### Verdict: GO (Conditional)

A **single natural-language advisory block** is safe across all runtimes. No runtime errors on unknown text in instruction files -- all treat instruction content as plain markdown context passed to the model. However, no runtime parses model-steering directives from instruction text.

**Recommended approach for SKILL.md model steering:**

1. **Advisory prose block** -- a natural-language section in each SKILL.md describing the recommended model tier and reasoning effort. This is always safe (plain text, ignored by runtimes that don't parse it, potentially useful to agents that read it).

2. **Runtime-keyed configuration overlays** -- alongside each SKILL.md, provide optional configuration snippets for each runtime (e.g., settings.json fragment for Claude Code, config.toml fragment for Codex). These are documentation, not auto-applied config.

3. **AGENTS.md-level routing logic** -- the project's AGENTS.md (read by Claude Code, Codex, OpenCode, Copilot) can include model-routing rules that reference skill cognitive tiers. Example:

```markdown
## Model Routing

When executing skills marked as "heavy-reasoning" tier:
- Prefer the most capable available model (Opus-class, GPT-5-Codex, Gemini Pro)
- Enable high reasoning effort if your runtime supports it

When executing skills marked as "lightweight" tier:
- Prefer a fast model (Haiku-class, Flash, mini)
- Use low reasoning effort
```

This pattern works because AGENTS.md is read by the broadest set of runtimes, and the routing rules are expressed as natural language that any LLM can interpret.

**Runtime-keyed conditional blocks are NOT needed** because all runtimes safely ignore unknown prose. The advisory approach is simpler and sufficient.

---

### Sources

- [Claude Code Model Configuration](https://code.claude.com/docs/en/model-config)
- [Codex CLI Configuration Reference](https://developers.openai.com/codex/config-reference/)
- [Codex CLI Command Line Reference](https://developers.openai.com/codex/cli/reference)
- [Codex AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md/)
- [OpenCode Models Documentation](https://opencode.ai/docs/models/)
- [OpenCode Agents Documentation](https://opencode.ai/docs/agents/)
- [Cursor Rules Documentation](https://cursor.com/docs/context/rules)
- [GitHub Copilot Model Comparison](https://docs.github.com/en/copilot/reference/ai-models/model-comparison)
- [GitHub Copilot Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [GitHub Copilot CLI Custom Instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)
- [Gemini CLI GitHub Repository](https://github.com/google-gemini/gemini-cli)
- [Gemini CLI Generation Settings](https://geminicli.com/docs/cli/generation-settings/)
- [Gemini CLI GEMINI.md Documentation](https://geminicli.com/docs/cli/gemini-md/)
- [Aider Reasoning Models](https://aider.chat/docs/config/reasoning.html)
- [Aider Options Reference](https://aider.chat/docs/config/options.html)

## Lifecycle

| Phase | Date | Commit | Notes |
|-------|------|--------|-------|
| Planned | 2026-03-13 | -- | Initial creation |
| Active | 2026-03-13 | -- | Research conducted across all 7 runtimes |
| Complete | 2026-03-13 | 2eae5a0 | GO: advisory prose blocks safe across all runtimes |
