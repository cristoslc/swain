"""Quick relay: polls Zulip for new operator messages, writes them to a file.
A companion process reads responses from another file and posts them back.

This is a smoke-test tool, not production code.
"""
import json
import os
import time
from pathlib import Path
import zulip

# Load .env file directly
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ[key.strip()] = val.strip()

SITE = os.environ["ZULIP_SITE"]
EMAIL = os.environ["ZULIP_BOT_EMAIL"]
KEY = os.environ["ZULIP_BOT_API_KEY"]
OPERATOR = os.environ["ZULIP_OPERATOR_EMAIL"]
STREAM = "swain"
INBOX = "relay_inbox.jsonl"
OUTBOX = "relay_outbox.jsonl"

client = zulip.Client(email=EMAIL, api_key=KEY, site=f"https://{SITE}")

# Register event queue
reg = client.register(event_types=["message"], narrow=[["is", "stream"]])
queue_id = reg["queue_id"]
last_id = reg["last_event_id"]
print(f"Relay started. Queue: {queue_id}")

# Track what we've already posted to avoid echo loops
posted_ids = set()

# Watch for outbox responses
last_outbox_pos = 0

while True:
    # Poll for new operator messages
    try:
        result = client.get_events(queue_id=queue_id, last_event_id=last_id)
    except Exception as e:
        print(f"Poll error: {e}")
        time.sleep(3)
        continue

    if result.get("result") == "success":
        for ev in result.get("events", []):
            last_id = max(last_id, ev.get("id", last_id))
            if ev.get("type") == "message":
                msg = ev["message"]
                if msg["sender_email"] == EMAIL:
                    continue  # skip bot's own messages
                if msg.get("id") in posted_ids:
                    continue
                entry = {
                    "sender": msg["sender_full_name"],
                    "topic": msg["subject"],
                    "content": msg["content"],
                    "msg_id": msg["id"],
                    "timestamp": msg.get("timestamp", 0),
                }
                with open(INBOX, "a") as f:
                    f.write(json.dumps(entry) + "\n")
                print(f"[IN] {entry['sender']} [{entry['topic']}]: {entry['content'][:80]}")

    # Check for outbox responses to post back
    if os.path.exists(OUTBOX):
        with open(OUTBOX, "r") as f:
            f.seek(last_outbox_pos)
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    resp = json.loads(line)
                    result = client.send_message({
                        "type": "stream",
                        "to": STREAM,
                        "topic": resp.get("topic", "control"),
                        "content": resp["content"],
                    })
                    if result.get("result") == "success":
                        posted_ids.add(result.get("id"))
                        print(f"[OUT] [{resp.get('topic', 'control')}]: {resp['content'][:80]}")
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Outbox parse error: {e}")
            last_outbox_pos = f.tell()

    time.sleep(1)
