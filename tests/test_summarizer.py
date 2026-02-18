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
