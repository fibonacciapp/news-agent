# src/collectors/rss.py
import feedparser
from datetime import datetime, timedelta, timezone


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

            # Include article if we can't determine date or if it's recent
            if published and published < cutoff:
                continue

            articles.append({
                "title": entry.title,
                "link": entry.link,
                "source": feed_config["name"],
                "description": entry.get("summary", ""),
                "published": published.isoformat() if published else None,
            })

    return articles
