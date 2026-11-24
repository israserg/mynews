"""Fetch the TLDR AI newsletter feed and turn it into short briefs."""
import html
import os
import re
import time
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

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


def _is_tldr_issue_url(url: str) -> bool:
    parts = urlparse(url)
    return parts.scheme == "https" and parts.hostname == "tldr.tech"


def _fetch_together_with(issue_url: str) -> dict | None:
    """Fetch the issue HTML page and extract its "Together With" block; None on any failure."""
    if not _is_tldr_issue_url(issue_url):
        return None
    try:
        resp = httpx.get(issue_url, timeout=15, follow_redirects=True)
        resp.raise_for_status()
        return _extract_together_with(resp.text)
    except Exception:
        return None


def _to_item(entry) -> dict:
    title = entry.get("title", "").strip()
    # TLDR headlines look like "Topic A 🚀, Topic B 🌍, Topic C 🔬" - split into topics.
    topics = [t.strip() for t in title.split(", ") if t.strip()]
    published = entry.get("published", "")
    try:
        weekday = parsedate_to_datetime(published).strftime("%A")
    except Exception:
        weekday = ""
    return {
        "title": title,
        "topics": topics,
        "link": entry.get("link", ""),
        "published": published,
        "weekday": weekday,
        "together_with": None,
    }


def fetch_news() -> list[dict]:
    resp = httpx.get(FEED_URL, timeout=15, follow_redirects=True)
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    items = [_to_item(e) for e in parsed.entries[:MAX_ITEMS]]
    for item in items:
        item["together_with"] = _fetch_together_with(item["link"])
    return items


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
