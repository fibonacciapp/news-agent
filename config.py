import os

# Schedule
TIMEZONE = "America/Sao_Paulo"

# NewsAPI
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
NEWSAPI_QUERIES = ["artificial intelligence", "AI technology", "machine learning"]
NEWSAPI_LANGUAGE = "en"
NEWSAPI_PAGE_SIZE = 20

# RSS Feeds (AI-focused only)
RSS_FEEDS = [
    {"name": "Hacker News AI", "url": "https://hnrss.org/newest?points=30&q=AI+OR+LLM+OR+GPT+OR+artificial+intelligence+OR+machine+learning"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
]

# Keywords to filter articles — must match at least one
AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "llm", "gpt", "claude", "gemini", "neural network", "openai",
    "anthropic", "chatbot", "generative", "transformer", "diffusion",
    "copilot", "inteligência artificial", "aprendizado de máquina",
]

# Claude API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
MAX_ARTICLES_TO_SUMMARIZE = 15

# Email
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "news@resend.dev")
EMAIL_TO = os.environ.get("EMAIL_TO", "")
