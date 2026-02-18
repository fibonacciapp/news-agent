from datetime import datetime, timedelta, timezone
from newsapi import NewsApiClient


def collect_newsapi_articles(
    api_key: str,
    queries: list[str],
    language: str = "en",
    page_size: int = 20,
) -> list[dict]:
    """Collect articles from NewsAPI for given queries, deduplicated by URL."""
    client = NewsApiClient(api_key=api_key)
    seen_urls: set[str] = set()
    articles: list[dict] = []

    yesterday = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%d")

    for query in queries:
        try:
            response = client.get_everything(
                q=query,
                language=language,
                from_param=yesterday,
                sort_by="relevancy",
                page_size=page_size,
            )
        except Exception:
            continue

        for item in response.get("articles", []):
            url = item.get("url", "")
            if url in seen_urls or not url:
                continue
            seen_urls.add(url)

            articles.append({
                "title": item.get("title", ""),
                "link": url,
                "source": item.get("source", {}).get("name", "Unknown"),
                "description": item.get("description", ""),
                "published": item.get("publishedAt"),
            })

    return articles
