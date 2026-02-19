import json

import anthropic


SYSTEM_PROMPT = """Você é um curador de notícias especializado em Inteligência Artificial.
Dado uma lista de notícias (que podem estar em inglês), para cada uma gere:
- Um título traduzido para português do Brasil
- Um resumo de 3-4 frases em português explicando o conteúdo e a relevância da notícia

IMPORTANTE:
- Responda SOMENTE com JSON puro. Sem ```json, sem markdown, sem texto antes ou depois.
- Não inclua metadados como "Points:", "Comments:", "Article URL:" nos resumos.
- Foque no CONTEÚDO da notícia e sua importância para o campo da IA.
- Os resumos devem ser informativos e dar contexto suficiente para o leitor entender a notícia sem precisar clicar.

Formato exato:
{"noticias": [{"titulo_pt": "Título em português", "resumo_pt": "Resumo de 3-4 frases em português.", "indice": 0}]}

O campo "indice" corresponde à posição da notícia na lista (começando em 0)."""

USER_PROMPT_TEMPLATE = """Traduza e resuma estas notícias de IA:

{articles_text}"""


def summarize_articles(
    articles: list[dict],
    api_key: str,
    model: str = "claude-haiku-4-5-20251001",
) -> dict:
    """Summarize and translate articles using Claude. Returns dict with enriched 'articles'."""
    if not articles:
        return {"articles": []}

    articles_text = "\n\n".join(
        f"[{i}] {a['title']} ({a['source']})\n    {a.get('description', '')}"
        for i, a in enumerate(articles)
    )

    client = anthropic.Anthropic(api_key=api_key.strip())

    response = client.messages.create(
        model=model,
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(articles_text=articles_text)}
        ],
    )

    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[-1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    raw_text = raw_text.strip()

    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, IndexError):
        return {"articles": articles}

    noticias_por_indice = {n["indice"]: n for n in data.get("noticias", [])}
    enriched = []
    for i, article in enumerate(articles):
        noticia = noticias_por_indice.get(i, {})
        enriched.append({
            **article,
            "titulo_pt": noticia.get("titulo_pt", article["title"]),
            "resumo_pt": noticia.get("resumo_pt", article.get("description", "")),
        })

    return {"articles": enriched}
