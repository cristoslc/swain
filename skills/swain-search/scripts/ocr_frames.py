"""OCR text from extracted video frames using EasyOCR.

Usage: uv run --with "easyocr,opencv-python-headless" scripts/ocr_frames.py

Reads /tmp/swain_search_frame_*.png, deduplicates text across frames,
and writes unique lines to /tmp/swain_search_media_transcript.txt.
"""
import glob
import easyocr

reader = easyocr.Reader(["en"], gpu=False)
frames = sorted(glob.glob("/tmp/swain_search_frame_*.png"))

all_text = []
seen = set()
for f in frames:
    results = reader.readtext(f, detail=0)
    for line in results:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            all_text.append(line)

with open("/tmp/swain_search_media_transcript.txt", "w") as out:
    out.write("\n".join(all_text))
print(f"Extracted {len(all_text)} unique text lines from {len(frames)} frames")
