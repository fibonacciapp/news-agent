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
