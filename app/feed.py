"""Fetch the TLDR AI newsletter feed and turn it into short briefs."""
import os
import time

import feedparser
import httpx

FEED_URL = os.environ.get("MYNEWS_FEED_URL", "https://tldr.tech/api/rss/ai")
TTL_SECONDS = int(os.environ.get("MYNEWS_CACHE_TTL", "900"))  # 15 minutes
MAX_ITEMS = 10

_cache = {"items": None, "fetched_at": 0.0}


def _to_item(entry) -> dict:
    title = entry.get("title", "").strip()
    # TLDR headlines look like "Topic A 🚀, Topic B 🌍, Topic C 🔬" - split into topics.
    topics = [t.strip() for t in title.split(", ") if t.strip()]
    return {
        "title": title,
        "topics": topics,
        "link": entry.get("link", ""),
        "published": entry.get("published", ""),
    }


def fetch_news() -> list[dict]:
    resp = httpx.get(FEED_URL, timeout=15, follow_redirects=True)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    return [_to_item(e) for e in parsed.entries[:MAX_ITEMS]]


def get_news() -> list[dict]:
    """Return cached news; refresh when older than TTL. Serve stale data if refresh fails."""
    now = time.time()
    fresh = _cache["items"] is not None and now - _cache["fetched_at"] < TTL_SECONDS
    if fresh:
        return _cache["items"]
    try:
        _cache["items"] = fetch_news()
        _cache["fetched_at"] = now
    except Exception:
        if _cache["items"] is None:
            raise
    return _cache["items"]
