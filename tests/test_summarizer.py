import json
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

MOCK_JSON_RESPONSE = json.dumps({
    "resumo_do_dia": "Hoje os destaques foram o GPT-5 da OpenAI e o novo chip de IA da Apple.",
    "noticias": [
        {"titulo_pt": "OpenAI lança GPT-5", "resumo_pt": "Novo modelo com raciocínio aprimorado.", "indice": 0},
        {"titulo_pt": "Apple anuncia chip de IA", "resumo_pt": "Chip M5 com motor neural.", "indice": 1},
    ],
})


@patch("src.summarizer.anthropic.Anthropic")
def test_summarize_returns_structured_data(mock_anthropic_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=MOCK_JSON_RESPONSE)]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = summarize_articles(
        articles=SAMPLE_ARTICLES,
        api_key="fake-key",
        model="claude-haiku-4-5-20251001",
    )

    assert "resumo_do_dia" in result
    assert "GPT-5" in result["resumo_do_dia"]
    assert len(result["articles"]) == 2
    assert result["articles"][0]["titulo_pt"] == "OpenAI lança GPT-5"
    assert result["articles"][0]["resumo_pt"] == "Novo modelo com raciocínio aprimorado."
    assert result["articles"][0]["link"] == "https://example.com/1"


@patch("src.summarizer.anthropic.Anthropic")
def test_summarize_empty_articles(mock_anthropic_class):
    result = summarize_articles(
        articles=[],
        api_key="fake-key",
        model="claude-haiku-4-5-20251001",
    )

    assert result["resumo_do_dia"] == "Nenhuma notícia relevante encontrada hoje."
    assert result["articles"] == []


@patch("src.summarizer.anthropic.Anthropic")
def test_summarize_fallback_on_invalid_json(mock_anthropic_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Texto livre, não é JSON")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = summarize_articles(
        articles=SAMPLE_ARTICLES,
        api_key="fake-key",
        model="claude-haiku-4-5-20251001",
    )

    assert result["resumo_do_dia"] == "Texto livre, não é JSON"
    assert len(result["articles"]) == 2
