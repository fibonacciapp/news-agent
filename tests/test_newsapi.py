from unittest.mock import patch, MagicMock
from src.collectors.newsapi import collect_newsapi_articles


@patch("src.collectors.newsapi.NewsApiClient")
def test_collect_newsapi_returns_articles(mock_client_class):
    mock_client = MagicMock()
    mock_client.get_everything.return_value = {
        "status": "ok",
        "articles": [
            {
                "title": "GPT-5 Released",
                "url": "https://example.com/gpt5",
                "source": {"name": "TechNews"},
                "description": "OpenAI releases GPT-5",
                "publishedAt": "2026-02-18T06:00:00Z",
            }
        ],
    }
    mock_client_class.return_value = mock_client

    articles = collect_newsapi_articles(
        api_key="fake-key",
        queries=["AI"],
        language="en",
        page_size=10,
    )

    assert len(articles) == 1
    assert articles[0]["title"] == "GPT-5 Released"
    assert articles[0]["source"] == "TechNews"


@patch("src.collectors.newsapi.NewsApiClient")
def test_collect_newsapi_deduplicates_across_queries(mock_client_class):
    mock_client = MagicMock()
    article = {
        "title": "Same Article",
        "url": "https://example.com/same",
        "source": {"name": "Source"},
        "description": "Desc",
        "publishedAt": "2026-02-18T06:00:00Z",
    }
    mock_client.get_everything.return_value = {
        "status": "ok",
        "articles": [article],
    }
    mock_client_class.return_value = mock_client

    articles = collect_newsapi_articles(
        api_key="fake-key",
        queries=["AI", "machine learning"],
        language="en",
        page_size=10,
    )

    assert len(articles) == 1  # Deduplicated by URL
