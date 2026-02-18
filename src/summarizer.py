import json

import anthropic


SYSTEM_PROMPT = """Você é um curador de notícias de tecnologia e IA.
Dado uma lista de notícias (que podem estar em inglês), gere:
1. Um resumo geral do dia em português do Brasil (3-5 frases)
2. Para cada notícia, um título traduzido para português e um resumo de 1-2 frases em português

Responda APENAS com JSON válido neste formato exato:
{
  "resumo_do_dia": "texto do resumo geral aqui",
  "noticias": [
    {
      "titulo_pt": "Título traduzido para português",
      "resumo_pt": "Resumo curto de 1-2 frases em português",
      "indice": 0
    }
  ]
}

O campo "indice" deve corresponder à posição da notícia na lista original (começando em 0).
Seja conciso, informativo e objetivo."""

USER_PROMPT_TEMPLATE = """Resuma e traduza estas notícias de hoje:

{articles_text}"""


def summarize_articles(
    articles: list[dict],
    api_key: str,
    model: str = "claude-haiku-4-5-20251001",
) -> dict:
    """Summarize and translate articles using Claude. Returns dict with 'resumo_do_dia' and enriched 'articles'."""
    if not articles:
        return {
            "resumo_do_dia": "Nenhuma notícia relevante encontrada hoje.",
            "articles": [],
        }

    articles_text = "\n\n".join(
        f"[{i}] {a['title']} ({a['source']})\n    {a.get('description', '')}"
        for i, a in enumerate(articles)
    )

    client = anthropic.Anthropic(api_key=api_key.strip())

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(articles_text=articles_text)}
        ],
    )

    try:
        data = json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError):
        # Fallback: use original data if JSON parsing fails
        return {
            "resumo_do_dia": response.content[0].text,
            "articles": articles,
        }

    # Enrich original articles with Portuguese titles and summaries
    noticias_por_indice = {n["indice"]: n for n in data.get("noticias", [])}
    enriched = []
    for i, article in enumerate(articles):
        noticia = noticias_por_indice.get(i, {})
        enriched.append({
            **article,
            "titulo_pt": noticia.get("titulo_pt", article["title"]),
            "resumo_pt": noticia.get("resumo_pt", article.get("description", "")),
        })

    return {
        "resumo_do_dia": data.get("resumo_do_dia", ""),
        "articles": enriched,
    }
