---
source-id: "claude-code-channels-reference"
title: "Channels reference — Claude Code Docs"
type: web
url: "https://code.claude.com/docs/en/channels-reference"
fetched: 2026-03-20T00:00:00Z
hash: "9193748e6cee8347800c6c9e6d1b89602520230173bbd5356f6d6f6c5e5ef7bb"
---

# Channels reference

Build an MCP server that pushes webhooks, alerts, and chat messages into a Claude Code session. Reference for the channel contract: capability declaration, notification events, reply tools, and sender gating.

> Channels are in research preview and require Claude Code v2.1.80 or later. They require claude.ai login. Console and API key authentication is not supported. Team and Enterprise organizations must explicitly enable them.

A channel is an MCP server that pushes events into a Claude Code session so Claude can react to things happening outside the terminal.

You can build a one-way or two-way channel. One-way channels forward alerts, webhooks, or monitoring events for Claude to act on. Two-way channels like chat bridges also expose a reply tool so Claude can send messages back.

## Overview

A channel is an MCP server that runs on the same machine as Claude Code. Claude Code spawns it as a subprocess and communicates over stdio. Your channel server is the bridge between external systems and the Claude Code session:

- **Chat platforms** (Telegram, Discord): your plugin runs locally and polls the platform's API for new messages. When someone DMs your bot, the plugin receives the message and forwards it to Claude. No URL to expose.
- **Webhooks** (CI, monitoring): your server listens on a local HTTP port. External systems POST to that port, and your server pushes the payload to Claude.

## What you need

The only hard requirement is the `@modelcontextprotocol/sdk` package and a Node.js-compatible runtime. Bun, Node, and Deno all work. The pre-built plugins in the research preview use Bun, but your channel doesn't have to.

Your server needs to:

1. Declare the `claude/channel` capability so Claude Code registers a notification listener
2. Emit `notifications/claude/channel` events when something happens
3. Connect over stdio transport (Claude Code spawns your server as a subprocess)

During the research preview, custom channels aren't on the approved allowlist. Use `--dangerously-load-development-channels` to test locally.

## Example: build a webhook receiver

This walkthrough builds a single-file server that listens for HTTP requests and forwards them into your Claude Code session.

### 1. Create the project

```bash
mkdir webhook-channel && cd webhook-channel
bun add @modelcontextprotocol/sdk
```

### 2. Write the channel server

Create `webhook.ts`:

```typescript
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

// Create the MCP server and declare it as a channel
const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    // this key is what makes it a channel
    capabilities: { experimental: { 'claude/channel': {} } },
    // added to Claude's system prompt
    instructions: 'Events from the webhook channel arrive as <channel source="webhook" ...>. They are one-way: read them and act, no reply expected.',
  },
)

// Connect to Claude Code over stdio
await mcp.connect(new StdioServerTransport())

// Start an HTTP server that forwards every POST to Claude
Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  async fetch(req) {
    const body = await req.text()
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,
        meta: { path: new URL(req.url).pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

The file does three things:

- **Server configuration**: creates the MCP server with `claude/channel` in capabilities, telling Claude Code this is a channel. The `instructions` string goes into Claude's system prompt.
- **Stdio connection**: connects to Claude Code over stdin/stdout. Standard for any MCP server.
- **HTTP listener**: starts a local web server on port 8788. Every POST body gets forwarded as a channel event via `mcp.notification()`.

### 3. Register your server with Claude Code

Add to `.mcp.json`:

```json
{
  "mcpServers": {
    "webhook": { "command": "bun", "args": ["./webhook.ts"] }
  }
}
```

### 4. Test it

```bash
claude --dangerously-load-development-channels server:webhook
```

Then in a separate terminal:

```bash
curl -X POST localhost:8788 -d "build failed on main: https://ci.example.com/run/1234"
```

The payload arrives as:

```xml
<channel source="webhook" path="/" method="POST">build failed on main: https://ci.example.com/run/1234</channel>
```

## Test during the research preview

During the research preview, every channel must be on the approved allowlist to register. The development flag bypasses the allowlist for specific entries after a confirmation prompt:

```bash
# Testing a plugin you're developing
claude --dangerously-load-development-channels plugin:yourplugin@yourmarketplace

# Testing a bare .mcp.json server (no plugin wrapper yet)
claude --dangerously-load-development-channels server:webhook
```

The bypass is per-entry. Combining this flag with `--channels` doesn't extend the bypass to the `--channels` entries. The `channelsEnabled` organization policy still applies.

## Server options

A channel sets these options in the `Server` constructor:

| Field | Type | Description |
|-------|------|-------------|
| `capabilities.experimental['claude/channel']` | `object` | Required. Always `{}`. Presence registers the notification listener. |
| `capabilities.tools` | `object` | Two-way only. Always `{}`. Standard MCP tool capability. |
| `instructions` | `string` | Recommended. Added to Claude's system prompt. Tell Claude what events to expect, whether to reply, and which tool to use. |

Example two-way setup:

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js'

const mcp = new Server(
  { name: 'your-channel', version: '0.0.1' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},  // omit for one-way channels
    },
    instructions: 'Messages arrive as <channel source="your-channel" ...>. Reply with the reply tool.',
  },
)
```

## Notification format

Your server emits `notifications/claude/channel` with two params:

| Field | Type | Description |
|-------|------|-------------|
| `content` | `string` | The event body. Delivered as the body of the `<channel>` tag. |
| `meta` | `Record<string, string>` | Optional. Each entry becomes an attribute on the `<channel>` tag. Keys must be identifiers: letters, digits, underscores only. Keys with hyphens or other characters are silently dropped. |

Example:

```typescript
await mcp.notification({
  method: 'notifications/claude/channel',
  params: {
    content: 'build failed on main: https://ci.example.com/run/1234',
    meta: { severity: 'high', run_id: '1234' },
  },
})
```

Arrives as:

```xml
<channel source="your-channel" severity="high" run_id="1234">
build failed on main: https://ci.example.com/run/1234
</channel>
```

## Expose a reply tool

For two-way channels, expose a standard MCP tool that Claude can call to send messages back. Three components:

1. A `tools: {}` entry in capabilities
2. Tool handlers defining the schema and send logic
3. An `instructions` string telling Claude when and how to call the tool

### Register the reply tool

```typescript
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'

// Claude queries this at startup to discover tools
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

// Claude calls this when it wants to invoke the tool
mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    await yourPlatform.send(chat_id, text)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})
```

### Full webhook.ts with reply tool

```typescript
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js'

const mcp = new Server(
  { name: 'webhook', version: '0.0.1' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},
    },
    instructions: 'Messages arrive as <channel source="webhook" chat_id="...">. Reply with the reply tool, passing the chat_id from the tag.',
  },
)

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a message back over this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'The conversation to reply in' },
        text: { type: 'string', description: 'The message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

mcp.setRequestHandler(CallToolRequestSchema, async req => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    console.error(`Reply to ${chat_id}: ${text}`)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})

await mcp.connect(new StdioServerTransport())

let nextId = 1
Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  async fetch(req) {
    const body = await req.text()
    const chat_id = String(nextId++)
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: {
        content: body,
        meta: { chat_id, path: new URL(req.url).pathname, method: req.method },
      },
    })
    return new Response('ok')
  },
})
```

## Gate inbound messages

An ungated channel is a prompt injection vector. Anyone who can reach your endpoint can put text in front of Claude. Check the sender against an allowlist before calling `mcp.notification()`:

```typescript
const allowed = new Set(loadAllowlist())

// inside your message handler, before emitting:
if (!allowed.has(message.from.id)) {  // sender, not room
  return  // drop silently
}
await mcp.notification({ ... })
```

Gate on the **sender's identity**, not the chat or room identity: `message.from.id`, not `message.chat.id`. In group chats these differ, and gating on the room would let anyone in an allowlisted group inject messages.

The Telegram and Discord channels gate on a sender allowlist the same way. They bootstrap the list by pairing: the user DMs the bot, the bot replies with a pairing code, the user approves it in their Claude Code session, and their platform ID is added.

## Package as a plugin

To make your channel installable and shareable, wrap it in a plugin and publish it to a marketplace. Users install it with `/plugin install`, then enable it per session with `--channels plugin:<name>@<marketplace>`.

A channel published to your own marketplace still needs `--dangerously-load-development-channels` to run, since it isn't on the approved allowlist. To get it added, submit it to the official marketplace. Channel plugins go through security review before being approved.

## See also

- Channels — install and use Telegram, Discord, or the fakechat demo
- Working channel implementations — complete server code with pairing flows, reply tools, and file attachments
- MCP — the underlying protocol that channel servers implement
- Plugins — package your channel so users can install it with `/plugin install`
