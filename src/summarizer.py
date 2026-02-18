import anthropic


SYSTEM_PROMPT = """Você é um curador de notícias de tecnologia e IA.
Dado uma lista de notícias, gere um resumo em português do Brasil.

Formato:
1. Um parágrafo de 3-5 frases com os destaques mais importantes do dia
2. Identifique tendências e conexões entre as notícias

Seja conciso, informativo e objetivo."""

USER_PROMPT_TEMPLATE = """Resuma estas notícias de hoje:

{articles_text}"""


def summarize_articles(
    articles: list[dict],
    api_key: str,
    model: str = "claude-haiku-4-5-20251001",
) -> str:
    """Summarize a list of articles using Claude."""
    if not articles:
        return "Nenhuma notícia relevante encontrada hoje."

    articles_text = "\n\n".join(
        f"- **{a['title']}** ({a['source']})\n  {a.get('description', '')}"
        for a in articles
    )

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(articles_text=articles_text)}
        ],
    )

    return response.content[0].text
