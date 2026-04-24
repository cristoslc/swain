import type { ChannelAdapter, ChannelMessage, ReplyOptions } from '../channel.js';
import { importPeer } from '../peer-require.js';
import type { WecomChannelConfig } from '../workspace.js';

export class WecomAdapter implements ChannelAdapter {
  readonly name = 'wecom';
  readonly maxMessageLength = 2048;
  private config: WecomChannelConfig;
  private wsClient: any = null;
  private seenMsgIds = new Set<string>();
  private static readonly MAX_SEEN = 500;

  constructor(config: WecomChannelConfig) {
    this.config = config;
  }

  async start(onMessage: (msg: ChannelMessage) => void): Promise<void> {
    let AiBot: any;
    try {
      AiBot = await importPeer('@wecom/aibot-node-sdk');
    } catch {
      throw new Error('WeCom adapter requires @wecom/aibot-node-sdk. Install it: npm install @wecom/aibot-node-sdk');
    }

    // Support both default and named exports
    const WSClient = AiBot.WSClient || AiBot.default?.WSClient || AiBot.default;
    if (!WSClient) {
      throw new Error('Invalid @wecom/aibot-node-sdk: WSClient not found');
    }

    const wsOpts: Record<string, unknown> = {
      botId: this.config.botId,
      secret: this.config.secret,
    };
    if (this.config.websocketUrl) wsOpts.url = this.config.websocketUrl;

    this.wsClient = new WSClient(wsOpts);

    this.wsClient.on('message.text', (frame: any) => {
      this.handleFrame(frame, onMessage);
    });

    this.wsClient.on('message.image', (frame: any) => {
      this.handleFrame(frame, onMessage, '(image)');
    });

    await this.wsClient.connect();
    console.log('[wecom] WebSocket connection established');
  }

  private handleFrame(frame: any, onMessage: (msg: ChannelMessage) => void, fallbackText?: string): void {
    const body = frame?.body ?? frame;
    const msgId: string | undefined = body.msgid || body.msgId || body.message_id;
    if (msgId) {
      if (this.seenMsgIds.has(msgId)) return;
      this.seenMsgIds.add(msgId);
      if (this.seenMsgIds.size > WecomAdapter.MAX_SEEN) {
        const entries = [...this.seenMsgIds];
        this.seenMsgIds = new Set(entries.slice(entries.length >> 1));
      }
    }

    const text =
      body.text?.content ||
      body.content?.text ||
      (typeof body.text === 'string' ? body.text : undefined) ||
      fallbackText ||
      '';
    if (!text) return;

    const senderId = body.from?.userid || body.userId || (typeof body.from === 'string' ? body.from : '') || '';
    const chatType = body.chattype || body.chatType || body.chat_type;
    const isGroup = chatType === 'group';
    const chatId = body.chatid || body.chatId || body.conversation_id || (!isGroup ? senderId : '');

    const channelMsg: ChannelMessage = {
      channelType: 'wecom',
      senderId,
      senderName: body.userName || body.from_name,
      chatId,
      chatType: isGroup ? 'group' : 'dm',
      text,
      messageId: msgId,
      mentioned: body.mentioned,
      raw: frame,
    };

    onMessage(channelMsg);
  }

  async reply(msg: ChannelMessage, text: string, _options?: ReplyOptions): Promise<void> {
    if (!this.wsClient) return;
    const frame = msg.raw;
    const streamId = `reply-${Date.now()}`;
    await this.wsClient.replyStream(frame, streamId, text, true);
  }

  async send(chatId: string, text: string): Promise<void> {
    if (!this.wsClient) return;
    await this.wsClient.sendMessage(chatId, { msgtype: 'text', text: { content: text } });
  }

  async stop(): Promise<void> {
    if (this.wsClient) {
      await this.wsClient.disconnect?.();
      this.wsClient = null;
    }
  }
}
