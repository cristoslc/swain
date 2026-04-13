"""Fetch an X/Twitter thread via the fxtwitter API and write transcript + metadata.

Also resolves any cited X/Twitter status URLs inside the thread (one extra API call
each) so cited posts can be rendered inline as blockquote citations.

Usage:
    uv run fetch_x_thread.py <tweet_url_or_id>

Outputs:
    /tmp/media_thread.json            raw fxtwitter thread response
    /tmp/media_clean_transcript.txt   stitched thread with cited posts inline
    stdout                            JSON metadata (author, count, title_guess,
                                      post_urls, cited_posts)
"""
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Optional

TRANSCRIPT_PATH = "/tmp/swain_search_thread_transcript.txt"
RAW_PATH = "/tmp/swain_search_thread.json"
THREAD_API = "https://api.fxtwitter.com/2/thread/{id}"
UA = {"User-Agent": "swain-search/1.0"}

CITED_URL_RE = re.compile(
    r"https?://(?:x|twitter|fxtwitter|fixupx)\.com/\w+/status/(\d+)",
    re.IGNORECASE,
)
MAX_CITATIONS = 25


def extract_tweet_id(s: str) -> str:
    m = re.search(r"/status/(\d+)", s)
    if m:
        return m.group(1)
    if s.isdigit():
        return s
    raise SystemExit(f"error: could not extract tweet id from: {s}")


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fetch_thread(tweet_id: str) -> dict:
    return http_get_json(THREAD_API.format(id=tweet_id))


def _non_x_external_links(post: dict) -> list:
    facets = (post.get("raw_text") or {}).get("facets") or []
    out = []
    for f in facets:
        if f.get("type") != "url":
            continue
        repl = f.get("replacement")
        if not repl or re.match(r"https?://(?:x|twitter|fxtwitter|fixupx)\.com/", repl):
            continue
        out.append({
            "url": repl,
            "display": f.get("display"),
            "source_tweet": post.get("url"),
        })
    return out


def fetch_cited(tweet_id: str) -> Optional[dict]:
    """Fetch a cited tweet + its self-reply chain via /2/thread/.

    Using the thread endpoint instead of /status/ is deliberate: authors commonly
    post a teaser with a preview image, then self-reply with the bare article URL
    (image posts get more engagement; clickers still need a link). /2/thread/
    walks the self-reply chain from any root, so URLs buried in follow-up posts
    by the same author are captured automatically.
    """
    try:
        data = http_get_json(THREAD_API.format(id=tweet_id))
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None
    if data.get("code") != 200:
        return None
    thread = data.get("thread") or []
    target = next((p for p in thread if str(p.get("id")) == str(tweet_id)), None)
    if not target:
        return None

    target_author_id = (target.get("author") or {}).get("id")
    frontier = {str(tweet_id)}
    self_replies = []
    for p in thread:
        pid = str(p.get("id"))
        if pid in frontier:
            continue
        parent = (p.get("replying_to") or {}).get("status")
        author_id = (p.get("author") or {}).get("id")
        if parent in frontier and author_id == target_author_id:
            self_replies.append(p)
            frontier.add(pid)

    external_links = _non_x_external_links(target)
    for r in self_replies:
        external_links.extend(_non_x_external_links(r))

    a = target.get("author") or {}
    article = target.get("article")
    return {
        "id": target.get("id"),
        "url": target.get("url"),
        "text": target.get("text"),
        "created_at": target.get("created_at"),
        "author_name": a.get("name"),
        "author_handle": a.get("screen_name"),
        "author_url": a.get("url"),
        "author_website": (a.get("website") or {}).get("url"),
        "external_links": external_links,
        "photos": [
            ph.get("url")
            for ph in ((target.get("media") or {}).get("photos") or [])
            if ph.get("url")
        ],
        "twitter_card": target.get("twitter_card"),
        "self_replies": [
            {"url": r.get("url"), "text": r.get("text")}
            for r in self_replies
        ],
        "article": _summarize_article(article) if article else None,
    }


def _summarize_article(art: dict) -> dict:
    """Extract a compact representation of an X Article (long-form post).

    Includes title, preview_text, and the first ~6000 chars of body text so the
    model can synopsize without an additional WebFetch. Full article remains
    accessible at the cited tweet's URL on x.com.
    """
    blocks = ((art.get("content") or {}).get("blocks")) or []
    parts, total = [], 0
    for b in blocks:
        text = (b.get("text") or "").strip()
        if not text:
            continue
        parts.append(text)
        total += len(text)
        if total > 6000:
            break
    return {
        "id": art.get("id"),
        "title": art.get("title"),
        "preview_text": art.get("preview_text"),
        "created_at": art.get("created_at"),
        "body_excerpt": "\n\n".join(parts),
        "body_truncated": len(blocks) > len(parts),
    }


def collect_cited_ids(thread: list) -> list[str]:
    """Return unique cited status IDs in thread order, excluding thread's own posts."""
    own = {str(p.get("id")) for p in thread if p.get("id")}
    seen, ordered = set(), []
    for p in thread:
        for tid in CITED_URL_RE.findall(p.get("text", "") or ""):
            if tid in own or tid in seen:
                continue
            seen.add(tid)
            ordered.append(tid)
    return ordered[:MAX_CITATIONS]


def render_transcript(thread: list, cited: dict) -> str:
    """Build the transcript with cited posts as blockquotes under the referencing post."""
    total = len(thread)
    blocks = []
    for i, p in enumerate(thread, 1):
        text = (p.get("text") or "").strip()
        block = f"[{i}/{total}] {text}"
        for tid in CITED_URL_RE.findall(text):
            c = cited.get(tid)
            if not c:
                continue
            quoted = (c.get("text") or "").strip().replace("\n", "\n> ")
            block += (
                f"\n\n> **@{c.get('author_handle', '?')} "
                f"({c.get('created_at', '')}):** {quoted}\n> — {c.get('url', '')}"
            )
            ext = c.get("external_links") or []
            if ext:
                links = ", ".join(e["url"] for e in ext if e.get("url"))
                block += f"\n> external: {links}"
            elif c.get("author_website"):
                block += f"\n> author site: {c['author_website']}"
        blocks.append(block)
    return "\n\n".join(blocks) + "\n"


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: fetch_x_thread.py <tweet_url_or_id>")

    tweet_id = extract_tweet_id(sys.argv[1])
    try:
        data = fetch_thread(tweet_id)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"error: fxtwitter HTTP {e.code} for tweet {tweet_id} ({e.reason})")
    except urllib.error.URLError as e:
        raise SystemExit(f"error: fxtwitter unreachable: {e.reason}")
    if data.get("code") != 200:
        raise SystemExit(f"error: fxtwitter returned {data.get('code')}: {data.get('message')}")

    thread = data.get("thread") or []
    if not thread:
        raise SystemExit("error: empty thread in response")

    root = thread[0]
    root_text = root.get("text", "")
    if len(thread) == 1 and re.search(r"(1/|🧵)", root_text):
        raise SystemExit(
            "error: root post looks like a thread opener but only 1 post returned. "
            "Upstream fxtwitter deployment likely lacks an authenticated account proxy."
        )

    cited_ids = collect_cited_ids(thread)
    cited: dict = {}
    for tid in cited_ids:
        c = fetch_cited(tid)
        if c is not None:
            cited[tid] = c

    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(render_transcript(thread, cited))

    author = root.get("author") or {}
    title_text = re.sub(r"^(@\w+\s+)+", "", root_text).strip()
    title_text = re.sub(r"\s+", " ", title_text)
    if len(title_text) > 80:
        truncated = title_text[:80]
        last_space = truncated.rfind(" ")
        title_text = truncated[:last_space] if last_space > 40 else truncated
    title_guess = title_text or f"Thread by @{author.get('screen_name', 'unknown')}"

    meta = {
        "tweet_id": tweet_id,
        "source_url": root.get("url"),
        "author_name": author.get("name"),
        "author_handle": author.get("screen_name"),
        "author_url": author.get("url"),
        "published_date": root.get("created_at"),
        "tweet_count": len(thread),
        "title_guess": title_guess,
        "post_urls": [p.get("url") for p in thread],
        "cited_posts": {c["url"]: c for c in cited.values() if c.get("url")},
    }
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
