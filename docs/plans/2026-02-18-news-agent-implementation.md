# News Agent — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a daily automated news agent that collects Tech/AI news, summarizes them with Claude Haiku, and sends an email digest before 6am BRT.

**Architecture:** Python script orchestrated by GitHub Actions cron (5h BRT / 8h UTC). Collectors fetch from NewsAPI + RSS feeds, a summarizer uses Claude Haiku to generate a Portuguese digest, and Resend delivers the formatted HTML email.

**Tech Stack:** Python 3.12, newsapi-python, feedparser, anthropic SDK, resend SDK, GitHub Actions

---

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `src/__init__.py`
- Create: `src/collectors/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create requirements.txt**

```txt
newsapi-python==0.2.7
feedparser==6.0.11
anthropic>=0.42.0
resend>=2.0.0
python-dotenv==1.0.1
pytest==8.3.4
```

**Step 2: Create config.py**

```python
import os

# Schedule
TIMEZONE = "America/Sao_Paulo"

# NewsAPI
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
NEWSAPI_QUERIES = ["artificial intelligence", "AI technology", "machine learning"]
NEWSAPI_LANGUAGE = "en"
NEWSAPI_PAGE_SIZE = 20

# RSS Feeds
RSS_FEEDS = [
    {"name": "Hacker News", "url": "https://hnrss.org/newest?points=50"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
]

# Claude API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
MAX_ARTICLES_TO_SUMMARIZE = 15

# Email
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "news@resend.dev")
EMAIL_TO = os.environ.get("EMAIL_TO", "")
```

**Step 3: Create empty __init__.py files**

Create empty files at `src/__init__.py`, `src/collectors/__init__.py`, and `tests/__init__.py`.

**Step 4: Commit**

```bash
git add requirements.txt config.py src/__init__.py src/collectors/__init__.py tests/__init__.py
git commit -m "feat: project setup with dependencies and config"
```

---

### Task 2: RSS Feed Collector

**Files:**
- Create: `tests/test_rss.py`
- Create: `src/collectors/rss.py`

**Step 1: Write the failing test**

```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_rss.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.collectors.rss'`

**Step 3: Write minimal implementation**

```python
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
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_rss.py -v`
Expected: PASS — 2 tests passed

**Step 5: Commit**

```bash
git add src/collectors/rss.py tests/test_rss.py
git commit -m "feat: add RSS feed collector with tests"
```

---

### Task 3: NewsAPI Collector

**Files:**
- Create: `tests/test_newsapi.py`
- Create: `src/collectors/newsapi.py`

**Step 1: Write the failing test**

```python
# tests/test_newsapi.py
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
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_newsapi.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/collectors/newsapi.py
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
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_newsapi.py -v`
Expected: PASS — 2 tests passed

**Step 5: Commit**

```bash
git add src/collectors/newsapi.py tests/test_newsapi.py
git commit -m "feat: add NewsAPI collector with deduplication"
```

---

### Task 4: AI Summarizer with Claude Haiku

**Files:**
- Create: `tests/test_summarizer.py`
- Create: `src/summarizer.py`

**Step 1: Write the failing test**

```python
# tests/test_summarizer.py
from unittest.mock import patch, MagicMock
from src.summarizer import summarize_articles


SAMPLE_ARTICLES = [
    {
        "title": "OpenAI releases GPT-5",
        "description": "New model with improved reasoning",
        "source": "TechCrunch",
        "link": "https://example.com/1",
    },
    {
        "title": "Apple announces AI chip",
        "description": "M5 chip with neural engine",
        "source": "The Verge",
        "link": "https://example.com/2",
    },
]


@patch("src.summarizer.anthropic.Anthropic")
def test_summarize_returns_text(mock_anthropic_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hoje os destaques foram GPT-5 e o novo chip da Apple.")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = summarize_articles(
        articles=SAMPLE_ARTICLES,
        api_key="fake-key",
        model="claude-haiku-4-5-20251001",
    )

    assert "GPT-5" in result or "Apple" in result
    assert len(result) > 10


@patch("src.summarizer.anthropic.Anthropic")
def test_summarize_empty_articles(mock_anthropic_class):
    result = summarize_articles(
        articles=[],
        api_key="fake-key",
        model="claude-haiku-4-5-20251001",
    )

    assert result == "Nenhuma notícia relevante encontrada hoje."
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_summarizer.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/summarizer.py
import anthropic


SYSTEM_PROMPT = """Você é um curador de notícias de tecnologia e IA.
Dado uma lista de notícias, gere um resumo em português do Brasil.

Formato:
1. Um parágrafo de 3-5 frases com os destaques mais importantes do dia
2. Identifique tendências e conexões entre as notícias

Seja conciso, informativo e objetivo."""

USER_PROMPT_TEMPLATE = """Resuma estas notícias de hoje:

{articles_text}"""


def summarize_articles(
    articles: list[dict],
    api_key: str,
    model: str = "claude-haiku-4-5-20251001",
) -> str:
    """Summarize a list of articles using Claude."""
    if not articles:
        return "Nenhuma notícia relevante encontrada hoje."

    articles_text = "\n\n".join(
        f"- **{a['title']}** ({a['source']})\n  {a.get('description', '')}"
        for a in articles
    )

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(articles_text=articles_text)}
        ],
    )

    return response.content[0].text
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_summarizer.py -v`
Expected: PASS — 2 tests passed

**Step 5: Commit**

```bash
git add src/summarizer.py tests/test_summarizer.py
git commit -m "feat: add Claude Haiku summarizer"
```

---

### Task 5: Email Sender with Resend

**Files:**
- Create: `tests/test_email_sender.py`
- Create: `src/email_sender.py`

**Step 1: Write the failing test**

```python
# tests/test_email_sender.py
from unittest.mock import patch
from src.email_sender import build_email_html, send_digest_email


SAMPLE_ARTICLES = [
    {
        "title": "GPT-5 Released",
        "source": "TechCrunch",
        "link": "https://example.com/1",
        "description": "New model",
    },
]


def test_build_email_html_contains_summary_and_articles():
    html = build_email_html(
        summary="Resumo do dia com destaques.",
        articles=SAMPLE_ARTICLES,
        date_str="18 de Fevereiro de 2026",
    )

    assert "Resumo do dia" in html
    assert "GPT-5 Released" in html
    assert "https://example.com/1" in html
    assert "18 de Fevereiro" in html


@patch("src.email_sender.resend.Emails.send")
def test_send_digest_email_calls_resend(mock_send):
    mock_send.return_value = {"id": "abc123"}

    result = send_digest_email(
        api_key="fake-key",
        from_email="test@resend.dev",
        to_email="user@example.com",
        subject="Test",
        html_body="<p>Hello</p>",
    )

    mock_send.assert_called_once()
    assert result == {"id": "abc123"}
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_email_sender.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/email_sender.py
import resend


def build_email_html(summary: str, articles: list[dict], date_str: str) -> str:
    """Build a formatted HTML email with summary and article links."""
    articles_html = ""
    for i, article in enumerate(articles, 1):
        articles_html += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
                <strong style="font-size: 15px;">{i}. {article['title']}</strong><br>
                <span style="color: #666; font-size: 13px;">
                    {article.get('description', '')[:150]}
                </span><br>
                <span style="color: #999; font-size: 12px;">{article['source']}</span>
                &nbsp;·&nbsp;
                <a href="{article['link']}" style="color: #0066cc; font-size: 12px;">Ler mais</a>
            </td>
        </tr>"""

    return f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, sans-serif; color: #333;">
        <h1 style="font-size: 22px; border-bottom: 3px solid #0066cc; padding-bottom: 8px;">
            Seu Resumo Tech/IA — {date_str}
        </h1>

        <div style="background: #f0f7ff; padding: 16px; border-radius: 8px; margin: 16px 0;">
            <h2 style="font-size: 16px; margin: 0 0 8px 0;">Resumo do Dia</h2>
            <p style="margin: 0; line-height: 1.6; font-size: 14px;">{summary}</p>
        </div>

        <h2 style="font-size: 16px;">Notícias</h2>
        <table style="width: 100%; border-collapse: collapse;">
            {articles_html}
        </table>

        <p style="color: #999; font-size: 11px; margin-top: 24px; text-align: center;">
            Gerado automaticamente pelo News Agent
        </p>
    </div>
    """


def send_digest_email(
    api_key: str,
    from_email: str,
    to_email: str,
    subject: str,
    html_body: str,
) -> dict:
    """Send the digest email via Resend."""
    resend.api_key = api_key

    return resend.Emails.send({
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    })
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_email_sender.py -v`
Expected: PASS — 2 tests passed

**Step 5: Commit**

```bash
git add src/email_sender.py tests/test_email_sender.py
git commit -m "feat: add email sender with HTML template"
```

---

### Task 6: Main Orchestrator

**Files:**
- Create: `tests/test_main.py`
- Create: `src/main.py`

**Step 1: Write the failing test**

```python
# tests/test_main.py
from unittest.mock import patch, MagicMock
from src.main import run


@patch("src.main.send_digest_email")
@patch("src.main.build_email_html")
@patch("src.main.summarize_articles")
@patch("src.main.collect_newsapi_articles")
@patch("src.main.collect_rss_articles")
def test_run_orchestrates_full_pipeline(
    mock_rss, mock_newsapi, mock_summarize, mock_build_html, mock_send
):
    mock_rss.return_value = [
        {"title": "RSS Article", "link": "https://a.com", "source": "HN", "description": "Desc"},
    ]
    mock_newsapi.return_value = [
        {"title": "API Article", "link": "https://b.com", "source": "TC", "description": "Desc"},
    ]
    mock_summarize.return_value = "Resumo do dia."
    mock_build_html.return_value = "<html>email</html>"
    mock_send.return_value = {"id": "sent123"}

    run()

    mock_rss.assert_called_once()
    mock_newsapi.assert_called_once()
    mock_summarize.assert_called_once()
    assert len(mock_summarize.call_args[1]["articles"]) == 2  # RSS + API combined
    mock_send.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_main.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/main.py
from datetime import datetime

import config
from src.collectors.rss import collect_rss_articles
from src.collectors.newsapi import collect_newsapi_articles
from src.summarizer import summarize_articles
from src.email_sender import build_email_html, send_digest_email


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    """Remove duplicate articles by URL."""
    seen: set[str] = set()
    unique: list[dict] = []
    for article in articles:
        url = article.get("link", "")
        if url not in seen:
            seen.add(url)
            unique.append(article)
    return unique


def run():
    """Main pipeline: collect → deduplicate → summarize → email."""
    print("Collecting RSS articles...")
    rss_articles = collect_rss_articles(config.RSS_FEEDS)
    print(f"  Found {len(rss_articles)} RSS articles")

    print("Collecting NewsAPI articles...")
    newsapi_articles = collect_newsapi_articles(
        api_key=config.NEWSAPI_KEY,
        queries=config.NEWSAPI_QUERIES,
        language=config.NEWSAPI_LANGUAGE,
        page_size=config.NEWSAPI_PAGE_SIZE,
    )
    print(f"  Found {len(newsapi_articles)} NewsAPI articles")

    all_articles = deduplicate_articles(rss_articles + newsapi_articles)
    top_articles = all_articles[: config.MAX_ARTICLES_TO_SUMMARIZE]
    print(f"  Total unique: {len(all_articles)}, sending top {len(top_articles)}")

    print("Summarizing with Claude...")
    summary = summarize_articles(
        articles=top_articles,
        api_key=config.ANTHROPIC_API_KEY,
        model=config.ANTHROPIC_MODEL,
    )

    date_str = datetime.now().strftime("%d de %B de %Y")
    subject = f"Seu Resumo Tech/IA — {date_str}"

    html = build_email_html(
        summary=summary,
        articles=top_articles,
        date_str=date_str,
    )

    print(f"Sending email to {config.EMAIL_TO}...")
    result = send_digest_email(
        api_key=config.RESEND_API_KEY,
        from_email=config.EMAIL_FROM,
        to_email=config.EMAIL_TO,
        subject=subject,
        html_body=html,
    )
    print(f"  Email sent! ID: {result.get('id', 'unknown')}")


if __name__ == "__main__":
    run()
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/test_main.py -v`
Expected: PASS — 1 test passed

**Step 5: Commit**

```bash
git add src/main.py tests/test_main.py
git commit -m "feat: add main orchestrator pipeline"
```

---

### Task 7: GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/daily-news.yml`

**Step 1: Create the workflow file**

```yaml
# .github/workflows/daily-news.yml
name: Daily News Digest

on:
  schedule:
    # 08:00 UTC = 05:00 BRT (before 6am)
    - cron: '0 8 * * *'
  workflow_dispatch:  # Manual trigger for testing

jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run news agent
        env:
          NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
        run: python -m src.main
```

**Step 2: Commit**

```bash
git add .github/workflows/daily-news.yml
git commit -m "feat: add GitHub Actions daily cron workflow"
```

---

### Task 8: Run All Tests and Final Commit

**Step 1: Run full test suite**

Run: `cd /Users/claudiovalverde/news-agent && python -m pytest tests/ -v`
Expected: PASS — all 7 tests pass

**Step 2: Final commit if any adjustments needed**

```bash
git add -A
git commit -m "chore: final adjustments after full test run"
```

---

### Task 9: Push to GitHub and Configure Secrets

**Step 1: Create GitHub repo**

```bash
gh repo create news-agent --private --source=. --push
```

**Step 2: Add secrets to the repository**

```bash
gh secret set NEWSAPI_KEY
gh secret set ANTHROPIC_API_KEY
gh secret set RESEND_API_KEY
gh secret set EMAIL_FROM
gh secret set EMAIL_TO
```

**Step 3: Test manually via workflow_dispatch**

```bash
gh workflow run daily-news.yml
gh run watch
```

Expected: Workflow completes, email received.

---

## Setup Guide (one-time)

1. **NewsAPI:** Create free account at https://newsapi.org → copy API key
2. **Anthropic:** Get API key at https://console.anthropic.com → add credits ($5 lasts months)
3. **Resend:** Create free account at https://resend.com → verify domain or use `onboarding@resend.dev` for testing
4. **GitHub:** Push repo, add all secrets via `gh secret set`
