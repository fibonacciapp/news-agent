# src/collectors/rss.py
import re

import feedparser
from datetime import datetime, timedelta, timezone


def _clean_description(text: str) -> str:
    """Remove aggregator metadata (Points, Comments, URLs) from description."""
    lines = text.split("\n")
    clean = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^(Article URL:|Comments URL:|Points:|# Comments:)", stripped):
            continue
        if stripped:
            clean.append(stripped)
    return " ".join(clean)[:300]


def collect_rss_articles(feeds: list[dict]) -> list[dict]:
    """Collect articles from RSS feeds published in the last 24 hours."""
    articles = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    for feed_config in feeds:
        feed = feedparser.parse(feed_config["url"])

        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if published and published < cutoff:
                continue

            raw_desc = entry.get("summary", "")
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "source": feed_config["name"],
                "description": _clean_description(raw_desc),
                "published": published.isoformat() if published else None,
            })

    return articles
