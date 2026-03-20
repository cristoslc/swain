---
source-id: "claude-code-channels-docs"
title: "Push events into a running session with channels — Claude Code Docs"
type: web
url: "https://code.claude.com/docs/en/channels"
fetched: 2026-03-20T00:00:00Z
hash: "760eeff0b102d978105e25c23a03bb1dba8f1ee66fe332ce44ddf2623103421d"
---

# Push events into a running session with channels

Use channels to push messages, alerts, and webhooks into your Claude Code session from an MCP server. Forward CI results, chat messages, and monitoring events so Claude can react while you're away.

> Channels are in research preview and require Claude Code v2.1.80 or later. They require claude.ai login. Console and API key authentication is not supported. Team and Enterprise organizations must explicitly enable them.

A channel is an MCP server that pushes events into your running Claude Code session, so Claude can react to things that happen while you're not at the terminal. Channels can be two-way: Claude reads the event and replies back through the same channel, like a chat bridge. Events only arrive while the session is open, so for an always-on setup you run Claude in a background process or persistent terminal.

You install a channel as a plugin and configure it with your own credentials. Telegram and Discord are included in the research preview.

When Claude replies through a channel, you see the inbound message in your terminal but not the reply text. The terminal shows the tool call and a confirmation (like "sent"), and the actual reply appears on the other platform.

## Supported channels

Each supported channel is a plugin that requires [Bun](https://bun.sh). For a hands-on demo of the plugin flow before connecting a real platform, try the fakechat quickstart.

### Telegram

View the full [Telegram plugin source](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/telegram).

1. **Create a Telegram bot** — Open BotFather in Telegram and send `/newbot`. Give it a display name and a unique username ending in `bot`. Copy the token BotFather returns.

2. **Install the plugin** — In Claude Code, run:

   ```
   /plugin install telegram@claude-plugins-official
   ```

3. **Configure your token** — Run the configure command with the token from BotFather:

   ```
   /telegram:configure <token>
   ```

   This saves it to `.claude/channels/telegram/.env` in your project. You can also set `TELEGRAM_BOT_TOKEN` in your shell environment before launching Claude Code.

4. **Restart with channels enabled** — Exit Claude Code and restart with the channel flag:

   ```
   claude --channels plugin:telegram@claude-plugins-official
   ```

5. **Pair your account** — Open Telegram and send any message to your bot. The bot replies with a pairing code. Back in Claude Code, run:

   ```
   /telegram:access pair <code>
   ```

   Then lock down access:

   ```
   /telegram:access policy allowlist
   ```

### Discord

View the full [Discord plugin source](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/discord).

1. **Create a Discord bot** — Go to the Discord Developer Portal, click New Application, and name it. In the Bot section, create a username, then click Reset Token and copy the token.

2. **Enable Message Content Intent** — In your bot's settings, scroll to Privileged Gateway Intents and enable Message Content Intent.

3. **Invite the bot to your server** — Go to OAuth2 > URL Generator. Select the `bot` scope and enable these permissions:
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Read Message History
   - Attach Files
   - Add Reactions

   Open the generated URL to add the bot to your server.

4. **Install the plugin** — In Claude Code, run:

   ```
   /plugin install discord@claude-plugins-official
   ```

5. **Configure your token** — Run the configure command with the bot token you copied:

   ```
   /discord:configure <token>
   ```

   This saves it to `.claude/channels/discord/.env` in your project. You can also set `DISCORD_BOT_TOKEN` in your shell environment before launching Claude Code.

6. **Restart with channels enabled**:

   ```
   claude --channels plugin:discord@claude-plugins-official
   ```

7. **Pair your account** — DM your bot on Discord. The bot replies with a pairing code. Back in Claude Code, run:

   ```
   /discord:access pair <code>
   ```

   Then lock down access:

   ```
   /discord:access policy allowlist
   ```

You can also build your own channel for systems that don't have a plugin yet.

## Quickstart

Fakechat is an officially supported demo channel that runs a chat UI on localhost, with nothing to authenticate and no external service to configure.

Once you install and enable fakechat, you can type in the browser and the message arrives in your Claude Code session. Claude replies, and the reply shows up back in the browser.

### Prerequisites

- Claude Code installed and authenticated with a claude.ai account
- Bun installed (`bun --version`; if that fails, install Bun)
- **Team/Enterprise users**: your organization admin must enable channels in managed settings

### Steps

1. **Install the fakechat channel plugin** — Start a Claude Code session and run:

   ```
   /plugin install fakechat@claude-plugins-official
   ```

   Fakechat is in the `claude-plugins-official` marketplace, which is added automatically for most setups. If you don't have it, run `/plugin marketplace add anthropics/claude-plugins-official` first.

2. **Restart with the channel enabled** — Exit Claude Code, then restart:

   ```
   claude --channels plugin:fakechat@claude-plugins-official
   ```

   The fakechat server starts automatically. You can pass several plugins to `--channels`, space-separated.

3. **Push a message in** — Open the fakechat UI at `http://localhost:8787` and type a message:

   ```
   hey, what's in my working directory?
   ```

   The message arrives in your Claude Code session as a `<channel source="fakechat">` event. Claude reads it, does the work, and calls fakechat's `reply` tool. The answer shows up in the chat UI.

> If Claude hits a permission prompt while you're away from the terminal, the session pauses until you approve locally. For unattended use, `--dangerously-skip-permissions` bypasses prompts, but only use it in environments you trust.

## Security

Every approved channel plugin maintains a sender allowlist: only IDs you've added can push messages, and everyone else is silently dropped.

Telegram and Discord bootstrap the list by pairing:

1. Find your bot in Telegram or Discord and send it any message
2. The bot replies with a pairing code
3. In your Claude Code session, approve the code when prompted
4. Your sender ID is added to the allowlist

On top of that, you control which servers are enabled each session with `--channels`, and on Team and Enterprise plans your organization controls availability with `channelsEnabled`.

Being in `.mcp.json` isn't enough to push messages: a server also has to be named in `--channels`.

## Enterprise controls

Channels are controlled by the `channelsEnabled` setting in managed settings.

| Plan type | Default behavior |
|-----------|-----------------|
| Pro / Max, no organization | Channels available; users opt in per session with `--channels` |
| Team / Enterprise | Channels disabled until an admin explicitly enables them |

### Enable channels for your organization

Admins can enable channels from **claude.ai > Admin settings > Claude Code > Channels**, or by setting `channelsEnabled` to `true` in managed settings.

Once enabled, users in your organization can use `--channels` to opt channel servers into individual sessions. If the setting is disabled or unset, the MCP server still connects and its tools work, but channel messages won't arrive. A startup warning tells the user to have an admin enable the setting.

## Research preview

Channels are a research preview feature. Availability is rolling out gradually, and the `--channels` flag syntax and protocol contract may change based on feedback.

During the preview, `--channels` only accepts plugins from an Anthropic-maintained allowlist. The channel plugins in [claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins) are the approved set. If you pass something that isn't, Claude Code starts normally but the channel doesn't register, and the startup notice tells you why.

To test a channel you're building, use `--dangerously-load-development-channels`. See the channels reference for information about testing custom channels.

## Next steps

- Build your own channel for systems that don't have plugins yet
- Remote Control to drive a local session from your phone instead of forwarding events into it
- Scheduled tasks to poll on a timer instead of reacting to pushed events
