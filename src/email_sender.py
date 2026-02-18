import resend


def build_email_html(summary: str, articles: list[dict], date_str: str) -> str:
    """Build a formatted HTML email with summary and article links."""
    articles_html = ""
    for i, article in enumerate(articles, 1):
        articles_html += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #eee;">
                <strong style="font-size: 15px;">{i}. {article['title']}</strong><br>
                <span style="color: #666; font-size: 13px;">
                    {article.get('description', '')[:150]}
                </span><br>
                <span style="color: #999; font-size: 12px;">{article['source']}</span>
                &nbsp;·&nbsp;
                <a href="{article['link']}" style="color: #0066cc; font-size: 12px;">Ler mais</a>
            </td>
        </tr>"""

    return f"""
    <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, sans-serif; color: #333;">
        <h1 style="font-size: 22px; border-bottom: 3px solid #0066cc; padding-bottom: 8px;">
            Seu Resumo Tech/IA — {date_str}
        </h1>

        <div style="background: #f0f7ff; padding: 16px; border-radius: 8px; margin: 16px 0;">
            <h2 style="font-size: 16px; margin: 0 0 8px 0;">Resumo do Dia</h2>
            <p style="margin: 0; line-height: 1.6; font-size: 14px;">{summary}</p>
        </div>

        <h2 style="font-size: 16px;">Notícias</h2>
        <table style="width: 100%; border-collapse: collapse;">
            {articles_html}
        </table>

        <p style="color: #999; font-size: 11px; margin-top: 24px; text-align: center;">
            Gerado automaticamente pelo News Agent
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
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    })
