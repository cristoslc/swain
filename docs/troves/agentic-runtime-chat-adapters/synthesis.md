# Synthesis: Agentic Runtime Chat Adapters

Projects that bridge agentic coding runtimes to web and chat UIs have matured fast in early 2026. This synthesis covers the build-vs-buy landscape for VISION-006 (Untethered Operator), with focus on Python-native paths to ACP.

## Key findings

### Three architectural tiers have emerged

The landscape splits into three tiers, each addressing a different layer of the adapter problem:

1. **Protocol layer (ACP/ACPX).** The Agent Client Protocol provides structured, typed communication with 16+ coding agents. ACPX wraps this as a CLI client with session lifecycle, event normalization, and permission controls. The Vercel AI SDK ACP provider exposes these agents as standard LanguageModel instances for web apps. (`acpx-agent-client-protocol`, `acp-vercel-ai-sdk-provider`, `casys-acpx-orchestration-guide`)

2. **Web UI layer.** CloudCLI (9.5k stars) leads the pack with support for Claude Code, Cursor CLI, Codex, and Gemini CLI in a single responsive web interface. AgentOS takes a mobile-first approach with 6 runtimes. AionUi offers a cross-platform desktop app with 8+ runtimes. Claudeck is a minimal WebSocket bridge for Claude Code only. (`cloudcli-claude-code-ui`, `agent-os-mobile-web-ui`, `aionui-multi-agent-desktop`, `claudeck-browser-ui`)

3. **Messaging bridge layer.** OpenClaw (247k stars) is the dominant messaging router with 15+ platform adapters, but it is a general-purpose assistant, not a coding agent adapter. Claude Code Telegram Bot provides a dedicated Claude-to-Telegram bridge. Secure OpenClaw demonstrates approval-over-chat for coding runtimes. Claude Code's official channel plugins handle Telegram and Discord natively. (`openclaw-ai-assistant`, `claude-code-telegram-bot`, `secure-openclaw-composio`)

### ACP is the emerging standard for runtime abstraction

The Agent Client Protocol (ACP), stewarded by Zed, has gained rapid adoption as the wire protocol between coding agents and their clients. Most major runtimes now support ACP natively or through community adapters:

- Native ACP: Gemini CLI, Cursor CLI, GitHub Copilot CLI, Kimi CLI, Kiro CLI, Qwen Code, Trae CLI, Factory Droid, iFlow.
- Community adapters: Claude Code (claude-agent-acp), Codex (codex-acp), Pi (pi-acp), OpenCode, Kilocode.

This means any project building on ACP gets multi-runtime support as a side effect of the protocol. (`acpx-agent-client-protocol`, `casys-acpx-orchestration-guide`)

### ACP has first-class Python support — Node.js is not required

The ACP organization ships official SDKs in five languages: TypeScript, Python, Rust, Kotlin, and Java. The Python SDK (`agent-client-protocol` on PyPI, v0.9.0) provides async base classes, stdio JSON-RPC transport, Pydantic schema models, and helper builders. It matches the TypeScript SDK in scope and supports both client and agent roles. (`acp-python-sdk`, `acp-protocol-org`, `acp-python-sdk-blog`)

The Python SDK is not a wrapper or shim. It began as a community project by Chojan Shang, was adopted by production users (Moonshot), and officially joined the `agentclientprotocol` organization in November 2025. Migration guides exist for version upgrades (0.7, 0.8). (`acp-python-sdk-blog`)

The `claude-code-acp` package (v0.5.1) wraps the Claude CLI as a subprocess and exposes four components: `ClaudeAcpAgent` (ACP server for editors), `ClaudeClient` (event-driven Python API), `AcpClient` (general ACP client), and `AcpProxyServer` (Copilot bridge). It needs Python 3.10+ and no API key — it reuses the Claude CLI subscription. (`claude-code-acp-pypi`)

### ACPX is a Node.js convenience layer, not a protocol requirement

ACPX is written in TypeScript (95%) and distributed as an npm package (`acpx`). It requires Node.js and is installed via `npm install -g acpx@latest` or `npx acpx@latest`. It provides session lifecycle management, named sessions, prompt queueing, and structured NDJSON output (`--format json`). (`acpx-agent-client-protocol`)

However, ACPX is **not required** to use ACP. The protocol is stdio JSON-RPC, and any language that can spawn a subprocess and read/write stdio can join. The official Python SDK provides the same client features. For Python-first projects, the stack is: (`acp-protocol-org`, `acp-python-sdk`)

- **`agent-client-protocol`** (Python SDK) for ACP client/agent plumbing.
- **`claude-code-acp`** for Claude Code-specific integration with a clean async API.
- ACPX only if its session management features (named sessions, prompt queueing, crash reconnect) are needed and worth the Node.js dependency.

ACPX does expose structured JSON output (`--format json`, `--json-strict`) that makes it usable as a subprocess from Python if needed. This is a viable fallback path — Python spawns `npx acpx` and reads NDJSON events from stdout. (`acpx-agent-client-protocol`)

### Session lifecycle is solved at the protocol level

ACPX handles session lifecycle comprehensively: create, ensure (idempotent), close (soft), crash reconnect, prompt queueing, cooperative cancel, and turn history. Sessions scope to git root directories with optional named parallel streams. This is the exact lifecycle model that Untethered Operator needs. (`acpx-agent-client-protocol`)

The Python SDK provides the transport and schema layers but does not include ACPX's session persistence (multi-turn conversations that survive across invocations). A Python-native project would need to build session persistence on top of the SDK, or call ACPX as a subprocess for that feature. (`acp-python-sdk`, `acpx-agent-client-protocol`)

### Approval flows are the hardest unsolved problem

Every project handles permissions differently, and none handle them well for asynchronous remote operation:

- **CloudCLI:** all tools disabled by default, selective enablement via UI (requires browser).
- **Claude Code Telegram Bot:** tool allowlist in config, but no interactive approval during sessions.
- **Secure OpenClaw:** "Reply Y to allow, N to deny" over messaging — the closest to async approval, but with a 2-minute timeout.
- **ACPX:** `--approve-all`, `--approve-reads`, `--deny-all` flags set at session start, not per-tool.
- **OpenClaw:** durable trust model (`allow-always`), but focused on OpenClaw's own exec, not coding runtime tools.
- **claude-code-acp:** exposes file operation interception and terminal execution control, providing hooks where an approval layer could be inserted.

No project provides a general-purpose "route this approval request to a chat surface and wait for a response" mechanism. (`secure-openclaw-composio`, `cloudcli-claude-code-ui`, `claude-code-telegram-bot`, `acpx-agent-client-protocol`, `claude-code-acp-pypi`)

### The composable path is clearer than the monolithic path

Rather than adopting one complete product, the landscape suggests composing from three layers:

1. **ACP Python SDK + claude-code-acp** for runtime adaptation (session lifecycle, event normalization, Claude Code integration) — entirely Python-native.
2. **Custom adapter or OpenClaw** for messaging platform routing (Telegram, Discord, etc.).
3. **ACPX** as an optional subprocess for features not yet in the Python SDK (named sessions, prompt queueing, crash reconnect), if the Node.js dependency is acceptable.

This stack keeps the primary runtime Python-native while allowing selective use of Node.js tools as subprocesses when needed. (`acp-python-sdk`, `claude-code-acp-pypi`, `acpx-agent-client-protocol`, `openclaw-ai-assistant`)

## Points of agreement

- Local execution is the core value proposition; files and tools stay on the operator's machine.
- All projects need a running terminal/process; no persistent daemon mode is standard yet.
- The community wants more messaging platforms (Slack, WhatsApp, iMessage) beyond Telegram and Discord.
- Multi-runtime support is the expected baseline for new projects in 2026.
- AGPL and GPL licenses appear in the web UI projects, which may constrain integration options.
- ACP's stdio JSON-RPC transport makes the protocol language-agnostic by design.

## Points of disagreement

- **CloudCLI vs. Claude Code Remote Control:** CloudCLI claims to be strictly better (all sessions, more runtimes, full UI). Anthropic positions Remote Control as complementary, not competing.
- **ACP maturity:** ACPX self-reports as alpha. Zed's ACP spec is expanding. The casys.ai guide treats it as production-ready. The Python SDK is at v0.9.0, approaching 1.0. Real-world stability varies by SDK.
- **OpenClaw security posture:** OpenClaw had a critical RCE (CVE-2026-25253). Claude Code's outbound-only model is architecturally safer. Some dismiss OpenClaw's security concerns; others (including OpenClaw's own maintainers) flag danger for non-technical users.
- **Python SDK vs. ACPX features:** The Python SDK covers transport and schema. ACPX adds session persistence, named sessions, and prompt queueing. Whether the Python SDK alone is enough depends on which ACPX features a project needs.

## Gaps

- **Async approval routing.** No project bridges runtime permission prompts to chat surfaces with proper timeout, escalation, and audit logging. This is the primary unsolved problem.
- **Python-native session persistence.** The Python ACP SDK provides transport but not ACPX-style durable session management. A Python-first project needs to build this or shell out to ACPX.
- **Event normalization across all three tiers.** ACP normalizes events between the protocol client and coding agents, but there is no standard for normalizing these events into chat messages. Each messaging bridge formats output differently.
- **Persistent daemon mode.** All projects require an open terminal or container. systemd/launchd integration is mentioned by Claude Code Telegram Bot but not standardized.
- **Audit trails for unattended sessions.** Enterprise security concern. No project provides comprehensive audit logging for what happened during remote/unattended agent sessions.
- **Testing and CI integration.** No project addresses how to test chat-to-runtime adapters automatically. All testing is manual.

## Cross-references

- Related trove: `claude-code-remote-interaction` covers Claude Code's native channels, remote control, and headless modes.
- This trove focuses on third-party projects that wrap or extend those native capabilities.
