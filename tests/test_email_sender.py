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
