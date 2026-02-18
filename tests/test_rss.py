# tests/test_rss.py
from unittest.mock import patch, MagicMock
from src.collectors.rss import collect_rss_articles


def _fake_feed(titles):
    feed = MagicMock()
    feed.entries = []
    for title in titles:
        entry = MagicMock()
        entry.title = title
        entry.link = f"https://example.com/{title.lower().replace(' ', '-')}"
        entry.get.return_value = "Test source description"
        entry.published_parsed = (2026, 2, 18, 8, 0, 0, 2, 49, 0)
        feed.entries.append(entry)
    return feed


@patch("src.collectors.rss.feedparser.parse")
def test_collect_rss_returns_articles(mock_parse):
    mock_parse.return_value = _fake_feed(["AI Breakthrough", "New Chip Released"])

    feeds = [{"name": "TestFeed", "url": "https://example.com/rss"}]
    articles = collect_rss_articles(feeds)

    assert len(articles) == 2
    assert articles[0]["title"] == "AI Breakthrough"
    assert articles[0]["source"] == "TestFeed"
    assert "link" in articles[0]


@patch("src.collectors.rss.feedparser.parse")
def test_collect_rss_handles_empty_feed(mock_parse):
    mock_parse.return_value = _fake_feed([])

    feeds = [{"name": "Empty", "url": "https://example.com/rss"}]
    articles = collect_rss_articles(feeds)

    assert articles == []
