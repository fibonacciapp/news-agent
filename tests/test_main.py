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
