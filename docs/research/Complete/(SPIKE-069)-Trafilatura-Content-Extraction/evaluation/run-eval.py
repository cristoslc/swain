#!/usr/bin/env python3
"""
SPIKE-069 evaluation harness.

Fetches a test corpus of 5 URLs once, then runs each candidate extractor
(trafilatura, readability-lxml, newspaper3k) against the cached HTML.
Saves raw HTML, extracted output per library, timing, and metadata.

Run via: uv run --with trafilatura --with readability-lxml --with markdownify \\
                --with newspaper3k --with lxml_html_clean --with requests run-eval.py
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RAW_DIR = HERE / "raw"
OUT_DIR = HERE / "outputs"
RAW_DIR.mkdir(exist_ok=True, parents=True)
OUT_DIR.mkdir(exist_ok=True, parents=True)

CORPUS = [
    {
        "id": "blog-ghuntley-ralph",
        "category": "blog",
        "url": "https://ghuntley.com/ralph/",
    },
    {
        "id": "docs-mdn-websocket",
        "category": "docs",
        "url": "https://developer.mozilla.org/en-US/docs/Web/API/WebSocket",
    },
    {
        "id": "forum-hn-gastown",
        "category": "forum",
        "url": "https://news.ycombinator.com/item?id=46463757",
    },
    {
        "id": "news-theverge-sample",
        "category": "news",
        "url": "https://www.theverge.com/tech",
    },
    {
        "id": "garden-appleton-gastown",
        "category": "digital-garden",
        "url": "https://maggieappleton.com/gastown",
    },
]


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    # best-effort decode
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def run_trafilatura(html: str, url: str) -> dict[str, Any]:
    import trafilatura

    t0 = time.perf_counter()
    result = trafilatura.extract(
        html,
        output_format="markdown",
        with_metadata=True,
        url=url,
        include_comments=False,
        include_tables=True,
        include_links=True,
    )
    elapsed = time.perf_counter() - t0

    meta = trafilatura.extract_metadata(html)
    md_dict = {}
    if meta is not None:
        md_dict = {
            "title": meta.title,
            "author": meta.author,
            "date": meta.date,
            "description": getattr(meta, "description", None),
        }
    return {
        "library": "trafilatura",
        "elapsed_seconds": round(elapsed, 3),
        "output": result or "",
        "output_len": len(result or ""),
        "metadata": md_dict,
    }


def run_readability(html: str, url: str) -> dict[str, Any]:
    from readability import Document
    from markdownify import markdownify

    t0 = time.perf_counter()
    doc = Document(html)
    title = doc.title()
    summary_html = doc.summary()
    md = markdownify(summary_html, heading_style="ATX")
    elapsed = time.perf_counter() - t0
    return {
        "library": "readability-lxml",
        "elapsed_seconds": round(elapsed, 3),
        "output": md,
        "output_len": len(md),
        "metadata": {
            "title": title,
            "author": None,
            "date": None,
            "description": None,
        },
    }


def run_newspaper(html: str, url: str) -> dict[str, Any]:
    from newspaper import Article

    t0 = time.perf_counter()
    article = Article(url)
    article.download(input_html=html)
    article.parse()
    text = article.text or ""
    elapsed = time.perf_counter() - t0
    return {
        "library": "newspaper3k",
        "elapsed_seconds": round(elapsed, 3),
        "output": text,
        "output_len": len(text),
        "metadata": {
            "title": article.title or None,
            "author": ", ".join(article.authors) if article.authors else None,
            "date": str(article.publish_date) if article.publish_date else None,
            "description": article.meta_description or None,
        },
    }


def main() -> None:
    report: list[dict[str, Any]] = []
    for entry in CORPUS:
        print(f"\n=== {entry['id']} ({entry['category']}) ===")
        print(f"URL: {entry['url']}")
        raw_path = RAW_DIR / f"{entry['id']}.html"
        if raw_path.exists():
            html = raw_path.read_text(encoding="utf-8", errors="replace")
            print(f"  cached raw HTML: {len(html)} chars")
        else:
            try:
                html = fetch_html(entry["url"])
                raw_path.write_text(html, encoding="utf-8")
                print(f"  fetched raw HTML: {len(html)} chars")
            except Exception as e:
                print(f"  FETCH FAILED: {e}")
                report.append(
                    {
                        "entry": entry,
                        "fetch_error": str(e),
                        "results": [],
                    }
                )
                continue

        results = []
        for runner, label in [
            (run_trafilatura, "trafilatura"),
            (run_readability, "readability-lxml"),
            (run_newspaper, "newspaper3k"),
        ]:
            try:
                r = runner(html, entry["url"])
            except Exception as e:
                r = {
                    "library": label,
                    "elapsed_seconds": None,
                    "output": "",
                    "output_len": 0,
                    "metadata": {},
                    "error": str(e),
                }
            out_path = OUT_DIR / f"{entry['id']}__{label}.md"
            out_path.write_text(r.get("output") or "", encoding="utf-8")
            results.append({k: v for k, v in r.items() if k != "output"})
            print(
                f"  {label}: len={r['output_len']} "
                f"elapsed={r.get('elapsed_seconds')}s "
                f"meta.title={(r.get('metadata') or {}).get('title')!r}"
            )

        report.append(
            {
                "entry": entry,
                "raw_size": len(html),
                "results": results,
            }
        )

    report_path = HERE / "report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\nReport written: {report_path}")


if __name__ == "__main__":
    main()
