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
    result = summarize_articles(
        articles=top_articles,
        api_key=config.ANTHROPIC_API_KEY,
        model=config.ANTHROPIC_MODEL,
    )

    date_str = datetime.now().strftime("%d de %B de %Y")
    subject = f"Seu Resumo Tech/IA — {date_str}"

    html = build_email_html(
        summary=result["resumo_do_dia"],
        articles=result["articles"],
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
