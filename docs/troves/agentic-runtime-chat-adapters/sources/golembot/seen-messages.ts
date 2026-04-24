import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const GOLEM_DIR = '.golem';
const SEEN_FILE = 'seen-messages.json';

/**
 * Persistent dedup store for message IDs.
 *
 * Both the real-time WebSocket path and the history-fetch polling path
 * write to this store. Before processing any message, both paths check
 * this store to avoid duplicate handling.
 *
 * Entries auto-expire after `ttlMs` (default: 24 hours) to prevent
 * unbounded growth.
 */
export class SeenMessageStore {
  private dir: string;
  private ttlMs: number;
  /** Map of `${channelType}:${messageId}` → timestamp (ms) */
  private entries: Map<string, number> = new Map();
  private dirty = false;
  private saveTimer: ReturnType<typeof setTimeout> | undefined;

  constructor(dir: string, ttlMs = 24 * 60 * 60 * 1000) {
    this.dir = dir;
    this.ttlMs = ttlMs;
  }

  /** Load from disk. Call once on startup. */
  async load(): Promise<void> {
    try {
      const raw = await readFile(join(this.dir, GOLEM_DIR, SEEN_FILE), 'utf-8');
      const parsed: Record<string, number> = JSON.parse(raw);
      const now = Date.now();
      // Only load non-expired entries
      for (const [key, ts] of Object.entries(parsed)) {
        if (now - ts < this.ttlMs) {
          this.entries.set(key, ts);
        }
      }
    } catch {
      // File doesn't exist or is malformed — start fresh
    }
  }

  /** Check if a message has been seen (by messageId or content fingerprint). */
  has(channelType: string, messageId: string): boolean {
    const key = `${channelType}:${messageId}`;
    const ts = this.entries.get(key);
    if (!ts) return false;
    // Expired entries are treated as unseen
    if (Date.now() - ts >= this.ttlMs) {
      this.entries.delete(key);
      return false;
    }
    return true;
  }

  /**
   * Normalize text for content fingerprinting.
   * Strips @_user_N mention placeholders so the same message matches
   * regardless of whether the WebSocket path stripped them or not.
   */
  private static normalizeText(text: string): string {
    return text
      .replace(/@_user_\d+/g, '')
      .trim()
      .slice(0, 100);
  }

  /** Check by content fingerprint (senderId + normalized text). */
  hasContent(channelType: string, senderId: string, text: string): boolean {
    const key = `${channelType}:c:${senderId}:${SeenMessageStore.normalizeText(text)}`;
    const ts = this.entries.get(key);
    if (!ts) return false;
    if (Date.now() - ts >= this.ttlMs) {
      this.entries.delete(key);
      return false;
    }
    return true;
  }

  /** Mark a message as seen. Schedules a debounced save. */
  mark(channelType: string, messageId: string): void {
    this.entries.set(`${channelType}:${messageId}`, Date.now());
    this.dirty = true;
    this.scheduleSave();
  }

  /** Mark by content fingerprint (senderId + normalized text). */
  markContent(channelType: string, senderId: string, text: string): void {
    const key = `${channelType}:c:${senderId}:${SeenMessageStore.normalizeText(text)}`;
    this.entries.set(key, Date.now());
    this.dirty = true;
    this.scheduleSave();
  }

  /** Persist to disk immediately. */
  async save(): Promise<void> {
    if (!this.dirty) return;
    this.dirty = false;

    // Prune expired entries before saving
    const now = Date.now();
    for (const [key, ts] of this.entries) {
      if (now - ts >= this.ttlMs) this.entries.delete(key);
    }

    const obj: Record<string, number> = {};
    for (const [key, ts] of this.entries) {
      obj[key] = ts;
    }

    await mkdir(join(this.dir, GOLEM_DIR), { recursive: true });
    const target = join(this.dir, GOLEM_DIR, SEEN_FILE);
    const tmp = `${target}.tmp`;
    await writeFile(tmp, `${JSON.stringify(obj)}\n`, 'utf-8');
    await rename(tmp, target);
  }

  /** Stop the save timer (call on shutdown). */
  stop(): void {
    if (this.saveTimer) {
      clearTimeout(this.saveTimer);
      this.saveTimer = undefined;
    }
  }

  private scheduleSave(): void {
    if (this.saveTimer) return;
    // Debounce: save at most every 5 seconds
    this.saveTimer = setTimeout(async () => {
      this.saveTimer = undefined;
      await this.save().catch(() => {});
    }, 5000);
    if (this.saveTimer.unref) this.saveTimer.unref();
  }
}
