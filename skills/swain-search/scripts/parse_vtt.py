import re
from collections import deque

with open('/tmp/swain_search_media.en.vtt', 'r') as f:
    content = f.read()

# Parse all cue blocks
cues = []
for block in re.split(r'\n\n+', content):
    lines = [l.strip() for l in block.split('\n') if l.strip()]
    timestamp_line = None
    text_lines = []
    for line in lines:
        if '-->' in line:
            m = re.match(r'(\d{2}:\d{2}:\d{2})', line)
            if m:
                timestamp_line = m.group(1)
        elif not re.match(r'^\d+$', line) and not line.startswith('WEBVTT') \
             and not line.startswith('Kind:') and not line.startswith('Language:'):
            clean = re.sub(r'<[^>]+>', '', line).strip()
            if clean:
                text_lines.append(clean)
    if timestamp_line and text_lines:
        cues.append((timestamp_line, ' '.join(text_lines)))

# Emit only new words per cue, preserving the timestamp of first appearance.
# Keep a sliding window of recent words — caption overlaps are always with
# the immediately preceding cue (typically 5–20 words), so 50 is plenty.
WINDOW = 50
result_lines = []
recent_words = deque(maxlen=WINDOW)

for timestamp, text in cues:
    words = text.split()
    tail = list(recent_words)
    overlap = 0
    for i in range(min(len(words), len(tail)), 0, -1):
        if words[:i] == tail[-i:]:
            overlap = i
            break
    new_words = words[overlap:]
    if new_words:
        result_lines.append(f'[{timestamp}] {" ".join(new_words)}')
        recent_words.extend(new_words)

with open('/tmp/swain_search_media_transcript.txt', 'w') as f:
    f.write('\n'.join(result_lines))
print(f"Saved {len(result_lines)} lines")
