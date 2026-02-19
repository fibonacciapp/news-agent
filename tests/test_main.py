from unittest.mock import patch, MagicMock
from src.main import run, filter_ai_articles


def test_filter_ai_articles_keeps_only_ai_related():
    articles = [
        {"title": "OpenAI releases GPT-5", "description": "New AI model"},
        {"title": "Best pizza in NYC", "description": "Food review"},
        {"title": "Machine learning breakthrough", "description": "New paper"},
    ]
    keywords = ["ai", "openai", "machine learning", "gpt"]

    result = filter_ai_articles(articles, keywords)

    assert len(result) == 2
    assert result[0]["title"] == "OpenAI releases GPT-5"
    assert result[1]["title"] == "Machine learning breakthrough"


@patch("src.main.send_digest_email")
@patch("src.main.build_email_html")
@patch("src.main.summarize_articles")
@patch("src.main.collect_newsapi_articles")
@patch("src.main.collect_rss_articles")
def test_run_orchestrates_full_pipeline(
    mock_rss, mock_newsapi, mock_summarize, mock_build_html, mock_send
):
    mock_rss.return_value = [
        {"title": "New AI model", "link": "https://a.com", "source": "HN", "description": "AI research"},
    ]
    mock_newsapi.return_value = [
        {"title": "GPT update", "link": "https://b.com", "source": "TC", "description": "OpenAI GPT"},
    ]
    mock_summarize.return_value = {
        "articles": [
            {"title": "New AI model", "link": "https://a.com", "source": "HN", "titulo_pt": "Novo modelo de IA", "resumo_pt": "Desc PT"},
            {"title": "GPT update", "link": "https://b.com", "source": "TC", "titulo_pt": "Atualização GPT", "resumo_pt": "Desc PT"},
        ],
    }
    mock_build_html.return_value = "<html>email</html>"
    mock_send.return_value = {"id": "sent123"}

    run()

    mock_rss.assert_called_once()
    mock_newsapi.assert_called_once()
    mock_summarize.assert_called_once()
    mock_send.assert_called_once()
