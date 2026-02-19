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
    "noticias": [
        {"titulo_pt": "OpenAI lança GPT-5", "resumo_pt": "Novo modelo com raciocínio aprimorado. O GPT-5 representa um salto em capacidade de análise. A OpenAI promete melhorias significativas.", "indice": 0},
        {"titulo_pt": "Apple anuncia chip de IA", "resumo_pt": "Chip M5 com motor neural dedicado. O novo processador promete acelerar tarefas de IA. Apple investe pesado em inteligência artificial.", "indice": 1},
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

    assert len(result["articles"]) == 2
    assert result["articles"][0]["titulo_pt"] == "OpenAI lança GPT-5"
    assert "raciocínio" in result["articles"][0]["resumo_pt"]
    assert result["articles"][0]["link"] == "https://example.com/1"


@patch("src.summarizer.anthropic.Anthropic")
def test_summarize_empty_articles(mock_anthropic_class):
    result = summarize_articles(
        articles=[],
        api_key="fake-key",
        model="claude-haiku-4-5-20251001",
    )

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

    assert len(result["articles"]) == 2
