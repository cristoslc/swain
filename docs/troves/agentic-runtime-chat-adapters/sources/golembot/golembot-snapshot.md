# GolemBot Source Snapshot

**Repository**: https://github.com/0xranx/golembot  
**License**: MIT  
**Version**: 0.46.0  

## Project Structure Overview

```
golembot/
├── src/
│   ├── channel.ts            # ChannelAdapter interface, ChannelMessage, session/conv key builders
│   ├── channels/
│   │   ├── feishu.ts          # Feishu/Lark adapter (WebSocket + HTTP API)
│   │   ├── feishu-format.ts  # Markdown → Feishu card format converter
│   │   ├── slack.ts           # Slack adapter (Bolt framework)
│   │   ├── slack-format.ts   # Markdown → Mrkdwn converter
│   │   ├── telegram.ts        # Telegram adapter (grammy framework)
│   │   ├── telegram-format.ts# Markdown → HTML converter
│   │   ├── discord.ts         # Discord adapter (discord.js)
│   │   ├── wecom.ts           # WeCom (企业微信) adapter (aibot-node-sdk WebSocket)
│   │   ├── dingtalk.ts        # DingTalk (钉钉) adapter (dingtalk-stream SDK)
│   │   └── weixin.ts          # WeChat (微信个人) adapter (HTTP long-polling, no SDK)
│   ├── gateway.ts            # Core message routing: adapter → handleMessage → assistant
│   ├── index.ts              # Assistant class: session management, engine dispatch, concurrency, circuit breaker
│   ├── engine.ts             # AgentEngine interface + factory (cursor, claude-code, opencode, codex)
│   ├── engines/
│   │   ├── claude-code.ts    # Claude Code CLI engine
│   │   ├── codex.ts          # OpenAI Codex CLI engine
│   │   ├── cursor.ts         # Cursor Agent engine
│   │   └── opencode.ts       # OpenCode engine
│   ├── session.ts            # File-based session persistence (.golem/sessions.json)
│   ├── inbox.ts              # Persistent JSONL message queue for ordered processing
│   ├── server.ts             # HTTP API server (/chat, /reset, /health, /status)
│   ├── workspace.ts          # Config loading (golem.yaml), type definitions for all channel configs
│   ├── history-fetcher.ts    # Offline message recovery via REST history APIs
│   ├── seen-messages.ts      # Persistent message deduplication store
│   ├── peer-require.ts       # Dynamic import helper for optional peer dependencies
│   ├── fleet.ts              # Multi-bot fleet coordination (file-based service discovery)
│   ├── scheduler.ts          # Cron-based scheduled task execution
│   ├── proactive.ts          # Proactive messaging (bot-initiated conversations)
│   ├── dashboard.ts          # Web dashboard with metrics
│   ├── commands.ts           # Slash command parser (/engine, /model, /reset, /status, etc.)
│   └── ...
├── skills/                   # Built-in skills (escalation, general, im-adapter, etc.)
├── templates/                # Bot templates (code-reviewer, customer-support, etc.)
├── docs/                     # VitePress documentation site
├── examples/                 # E2E test examples
├── golem.yaml                # Bot config file
└── package.json              # MIT licensed, TypeScript/ESM
```

## How the IM Adapters Work

### ChannelAdapter Interface (`src/channel.ts`)

All adapters implement a common `ChannelAdapter` interface:

```typescript
interface ChannelAdapter {
  readonly name: string;                        // e.g. "feishu", "slack"
  readonly maxMessageLength?: number;            // Platform-specific limit override
  start(onMessage: (msg: ChannelMessage) => void): Promise<void>;
  reply(msg: ChannelMessage, text: string, options?: ReplyOptions): Promise<void>;
  stop(): Promise<void>;
  send?(chatId: string, text: string): Promise<void>;      // Proactive push
  typing?(msg: ChannelMessage): Promise<void>;               // "typing..." indicator
  sendStatus?(msg, text): Promise<string>;                  // Status/progress message
  updateStatus?(msg, statusId, text): Promise<void>;        // Update status msg
  clearStatus?(msg, statusId): Promise<void>;               // Clear status msg
  getGroupMembers?(chatId): Promise<Map<string, string>>;    // @mention resolution
  readReceiptHandler?: (receipt: ReadReceipt) => void;      // Read receipt callback
  fetchHistory?(chatId, since, limit): Promise<ChannelMessage[]>; // Message history
  listChats?(): Promise<Array<{chatId, chatType}>>;          // Discover chats
}
```

### ChannelMessage Structure

```typescript
interface ChannelMessage {
  channelType: string;          // "feishu" | "slack" | "telegram" | "discord" | "dingtalk" | "wecom" | "weixin"
  senderId: string;
  senderName?: string;
  chatId: string;
  chatType: 'dm' | 'group';
  text: string;
  messageId?: string;          // Platform-native ID for dedup/reply
  threadId?: string;            // Thread/conversation root ID
  images?: ImageAttachment[];   // Attached images (Buffer + mimeType + fileName)
  files?: FileAttachment[];      // Non-image attachments
  raw: unknown;                 // Platform-native event object
  senderType?: 'user' | 'bot';  // Human vs bot detection
  mentioned?: boolean;           // Bot was @mentioned (set by adapter)
  mentionedOthers?: string[];   // Other users @mentioned (for multi-bot context)
}
```

### Supported Platforms

| Platform | Adapter | SDK Dependency | Connection | Key Features |
|----------|---------|---------------|------------|--------------|
| Feishu/Lark | `feishu.ts` | `@larksuiteoapi/node-sdk` | WebSocket + REST | Read receipts, card format, group members, image/file download, history fetch |
| Slack | `slack.ts` | `@slack/bolt` | Socket Mode | Thread-scoped sessions, markdown→mrkdwn, image download, history fetch |
| Telegram | `telegram.ts` | `grammy` | Long polling | 4096-char messages, inline keyboard markup, image/photo, HTML format |
| Discord | `discord.ts` | `discord.js` | WebSocket Gateway | 2000-char limit, native @mention detection via `<@userId>`, embed replies |
| DingTalk | `dingtalk.ts` | `dingtalk-stream` | WebSocket Stream | Rich text messages, image download, group mention-only (platform constraint) |
| WeCom | `wecom.ts` | `@wecom/aibot-node-sdk` | WebSocket | Enterprise WeChat AI bot API, text/image messages |
| WeChat | `weixin.ts` | None (pure HTTP) | HTTP long-polling | Personal WeChat via iLink Bot API, AES encryption, context tokens |

### Message Routing Flow

```
IM Platform → ChannelAdapter.start(onMessage)
                     ↓
              ChannelMessage created
                     ↓
         startGateway() (gateway.ts ~line 966)
                     ├─ Direct mode: handleMessage() called immediately
                     └─ Inbox mode: enqueue to InboxStore, consumer processes sequentially
                     ↓
              handleMessage() (gateway.ts ~line 345)
                     ├─ Slash command interception (/engine, /model, /reset, /cancel, /status)
                     ├─ DM routing: [System: private 1-on-1] prefix
                     ├─ Group routing:
                     │   ├─ mention-only policy: skip if not @mentioned
                     │   ├─ smart policy: call agent, expect [PASS] sentinel for silence
                     │   └─ always policy: respond to everything
                     ├─ Group history injection (last N messages)
                     ├─ [PASS]/[SKIP] sentinel suppression
                     └─ Streaming or Buffered delivery mode
                     ↓
              Assistant.chat() (index.ts ~line 258)
                     ├─ Per-session mutex (KeyedMutex)
                     ├─ Concurrency limits (maxConcurrent, maxQueuePerSession)
                     ├─ Session loading/saving
                     ├─ Engine creation (claude-code/codex/cursor/opencode)
                     ├─ Image compression + file attachment handling
                     ├─ Circuit breaker for provider failover
                     └─ History append (per-session JSONL)
                     ↓
              AgentEngine.invoke() → spawns CLI process, parses NDJSON stream
                     ↓
              StreamEvent → {type: "text"|"tool_call"|"completion"|"error"|"done"}
                     ↓
              Reply chunks sent back via adapter.reply()
```

### Key Design Patterns

1. **Peer dependency isolation**: Platform SDKs are optional (peerDependencies in package.json, all optional). The `peer-require.ts` helper provides `importPeer()` which gives clear install instructions on failure.

2. **Deduplication**: Every adapter maintains a `seenMsgIds` Set for near-term dedup, plus a persistent `SeenMessageStore` for crash-recovery dedup across restarts.

3. **Session keys**: Built from `channelType:chatId:senderId` (DMs) or `channelType:chatId` (groups), with special Slack thread handling: `slack:chatId:senderId:thread:threadId`.

4. **Group chat**: Three policies — `mention-only` (default, zero cost), `smart` (agent decides via [PASS] sentinel), `always`. Includes history buffer (last N messages), turn counter safety valve, and multi-bot fleet awareness.

5. **Inbox mode**: Persistent JSONL queue for reliable in-order processing. Messages are enqueued with status tracking (`pending → processing → done/failed`) and compaction.

6. **Custom adapters**: Any channel not built-in can be loaded via `_adapter: "./path.mjs"` in golem.yaml config. The factory function in `createChannelAdapter()` dynamically imports it.

## Session Management

Sessions are file-based, stored in `<workspace>/.golem/sessions.json`:

```json
{
  "sessionKey": {
    "engineSessionId": "engine-session-uuid",
    "lastUsed": 1700000000000,
    "engineType": "opencode"
  }
}
```

- **Key structure**: `{channelType}:{chatId}:{senderId}` for DMs, `{channelType}:{chatId}` for groups
- **Engine-aware**: Sessions are invalidated if the engine type changes (e.g., switching from claude-code to opencode)
- **History**: Per-session JSONL files in `.golem/history/{safeKey}.jsonl` with `{ts, sessionKey, role, content, durationMs, costUsd}`
- **Expiration**: `pruneExpiredSessions()` removes entries older than configurable `sessionTtlDays` (default 30)
- **Conversation reset**: Clears session + history files, plus gateway's in-memory group state

## License

**MIT License** — Copyright (c) 2026 GolemBot Contributors. Permissive, allows any use including commercial.

## Key Files for Borrowing the Chat Adapter Layer

### Essential (must understand)
- `src/channel.ts` — The `ChannelAdapter` interface, `ChannelMessage`, session key builders, mention detection
- `src/gateway.ts` — The routing pipeline: `startGateway()`, `handleMessage()`, `createChannelAdapter()`, group chat logic, streaming/buffered delivery
- `src/index.ts` — The `Assistant` class: concurrency, session lifecycle, engine dispatch, circuit breaker

### Adapter implementations (pick what you need)
- `src/channels/telegram.ts` — Cleanest adapter, good reference implementation (~141 lines)
- `src/channels/slack.ts` — Thread-scoped sessions, Bolt framework integration
- `src/channels/discord.ts` — Native @mention detection, 2000-char limit handling
- `src/channels/feishu.ts` — Most feature-complete: read receipts, card format, group members, file download

### Supporting infrastructure
- `src/session.ts` — File-based session persistence
- `src/inbox.ts` — Persistent message queue for ordered processing
- `src/seen-messages.ts` — Cross-restart deduplication
- `src/peer-require.ts` — Dynamic import helper for optional peer deps
- `src/workspace.ts` — Config types (`ChannelsConfig`, `GroupChatConfig`, all channel configs), YAML loader
- `src/history-fetcher.ts` — Offline message recovery after bot restart
- `src/channels/feishu-format.ts` — Markdown → Feishu card conversion
- `src/channels/slack-format.ts` — Markdown → Mrkdwn conversion
- `src/channels/telegram-format.ts` — Markdown → Telegram HTML conversion

### Configuration
- `golem.yaml` — Minimal bot config (name + engine)
- `src/workspace.ts` — Full type definitions for all config options including channel configs