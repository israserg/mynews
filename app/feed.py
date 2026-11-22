"""Fetch the TLDR AI newsletter feed and turn it into short briefs."""
import html
import os
import re
import time

import feedparser
import httpx

FEED_URL = os.environ.get("MYNEWS_FEED_URL", "https://tldr.tech/api/rss/ai")
TTL_SECONDS = int(os.environ.get("MYNEWS_CACHE_TTL", "900"))  # 15 minutes
MAX_ITEMS = 10

_cache = {"items": None, "fetched_at": 0.0}

_HREF_RE = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
_SRC_RE = re.compile(r"""<img\b[^>]*?\bsrc\s*=\s*["']([^"']+)["']""", re.IGNORECASE)
_LINE_END_RE = re.compile(r"</p>|<br", re.IGNORECASE)


def _safe_url(url: str) -> str:
    url = html.unescape(url).strip()
    return url if url.lower().startswith(("http://", "https://")) else ""


def _extract_together_with(text: str) -> dict | None:
    start = text.find("Together With")
    if start == -1:
        return None
    fragment = text[start:]
    end = _LINE_END_RE.search(fragment)
    if end:
        fragment = fragment[:end.start()]
    link = _HREF_RE.search(fragment)
    logo = _SRC_RE.search(fragment)
    return {
        "logo": _safe_url(logo.group(1)) if logo else "",
        "link": _safe_url(link.group(1)) if link else "",
    }


def _to_item(entry) -> dict:
    title = entry.get("title", "").strip()
    # TLDR headlines look like "Topic A 🚀, Topic B 🌍, Topic C 🔬" - split into topics.
    topics = [t.strip() for t in title.split(", ") if t.strip()]
    source = entry.get("summary", "") or (entry.get("content") or [{}])[0].get("value", "")
    return {
        "title": title,
        "topics": topics,
        "link": entry.get("link", ""),
        "published": entry.get("published", ""),
        "together_with": _extract_together_with(source),
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
