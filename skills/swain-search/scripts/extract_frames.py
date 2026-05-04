"""Extract frames from a video using scene-change detection.

Usage: uv run --with opencv-python-headless scripts/extract_frames.py <video_path> [threshold]

Compares consecutive frames using histogram correlation. When the
similarity drops below the threshold, a scene change is detected and
the frame is captured. Also captures the first and last frames.

Saves frames as /tmp/swain_search_frame_000.png, /tmp/swain_search_frame_001.png, etc.
Default threshold: 0.85 (lower = fewer captures, higher = more sensitive).
A minimum gap of 0.3s between captures prevents duplicates from minor jitter.
"""
import sys
import cv2

video_path = sys.argv[1]
threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.85

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"ERROR: Cannot open {video_path}", file=sys.stderr)
    sys.exit(1)

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30.0
min_gap = int(fps * 0.3)  # minimum frames between captures


def frame_hist(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
    cv2.normalize(hist, hist)
    return hist


saved = []
prev_hist = None
frame_id = 0
last_saved_id = -min_gap  # allow first frame to save immediately

while True:
    ret, frame = cap.read()
    if not ret:
        break

    curr_hist = frame_hist(frame)
    save = False

    if prev_hist is None:
        save = True  # first frame
    elif frame_id - last_saved_id >= min_gap:
        similarity = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)
        if similarity < threshold:
            save = True

    if save:
        path = f"/tmp/swain_search_frame_{len(saved):03d}.png"
        cv2.imwrite(path, frame)
        saved.append(path)
        last_saved_id = frame_id

    prev_hist = curr_hist
    frame_id += 1

# Always capture the last frame if it wasn't already saved
if frame_id - 1 != last_saved_id and frame_id > 0:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id - 1)
    ret, frame = cap.read()
    if ret:
        path = f"/tmp/swain_search_frame_{len(saved):03d}.png"
        cv2.imwrite(path, frame)
        saved.append(path)

cap.release()

for p in saved:
    print(p)
print(f"Saved {len(saved)} frames")
