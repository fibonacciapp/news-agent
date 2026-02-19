import resend


def build_email_html(articles: list[dict], date_str: str) -> str:
    """Build a formatted HTML email with article links in titles."""
    articles_html = ""
    for i, article in enumerate(articles, 1):
        titulo = article.get("titulo_pt", article["title"])
        resumo = article.get("resumo_pt", article.get("description", ""))
        articles_html += f"""
        <tr>
            <td style="padding: 14px 0; border-bottom: 1px solid #eee;">
                <a href="{article['link']}" style="color: #0066cc; text-decoration: none; font-size: 16px; font-weight: bold;">
                    {i}. {titulo}
                </a><br>
                <p style="color: #444; font-size: 13px; line-height: 1.6; margin: 6px 0 4px 0;">
                    {resumo}
                </p>
                <span style="color: #999; font-size: 11px;">{article['source']}</span>
            </td>
        </tr>"""

    return f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, sans-serif; color: #333;">
        <h1 style="font-size: 22px; border-bottom: 3px solid #0066cc; padding-bottom: 8px;">
            Novidades de IA no mundo — {date_str}
        </h1>

        <h2 style="font-size: 16px; margin-top: 20px;">Notícias de IA</h2>
        <table style="width: 100%; border-collapse: collapse;">
            {articles_html}
        </table>

        <p style="color: #999; font-size: 11px; margin-top: 24px; text-align: center;">
            Gerado automaticamente pelo Joshua AI News
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
        "from": f"Joshua AI News <{from_email}>",
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    })
