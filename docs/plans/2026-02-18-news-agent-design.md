# News Agent — Design Document

**Data:** 2026-02-18
**Objetivo:** Agente automatizado que coleta notícias diárias de Tech/IA, resume com IA e envia por email.

## Arquitetura

```
GitHub Actions (cron 5h BRT) → Coleta (NewsAPI + RSS) → Resumo (Claude Haiku) → Email (Resend)
```

## Decisões

- **Canal:** Email
- **Tema:** Tecnologia e Inteligência Artificial
- **Formato:** Resumo gerado por IA + links originais
- **Infra:** GitHub Actions (zero servidor, grátis)
- **Horário:** 5h00 BRT (08:00 UTC), email chega ~5h03

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Linguagem | Python 3.12 |
| Scheduler | GitHub Actions cron |
| Notícias (API) | NewsAPI (grátis, 100 req/dia) |
| Notícias (RSS) | feedparser — Hacker News, TechCrunch, The Verge |
| Resumo IA | Claude API (Haiku) via anthropic SDK |
| Email | Resend API |

## Estrutura do Projeto

```
news-agent/
├── .github/
│   └── workflows/
│       └── daily-news.yml
├── src/
│   ├── collectors/
│   │   ├── newsapi.py
│   │   └── rss.py
│   ├── summarizer.py
│   ├── email_sender.py
│   └── main.py
├── config.py
├── requirements.txt
└── README.md
```

## Fontes de Notícias

| Fonte | Tipo | Conteúdo |
|-------|------|----------|
| NewsAPI | API REST | Keywords: "AI", "artificial intelligence", "tech" |
| Hacker News | RSS | Top stories tecnologia |
| TechCrunch | RSS | Startups e IA |
| The Verge | RSS | Tech mainstream |

## Formato do Email

- Título: "Seu Resumo Tech/IA — {data}"
- Seção 1: Resumo geral do dia (parágrafo IA)
- Seção 2: Lista de 10-15 notícias com título, resumo de 1-2 linhas, fonte e link
- Footer: "Gerado automaticamente pelo News Agent"

## Secrets (GitHub Secrets)

| Secret | Serviço |
|--------|---------|
| `NEWSAPI_KEY` | newsapi.org |
| `ANTHROPIC_API_KEY` | Claude API |
| `RESEND_API_KEY` | resend.com |
| `EMAIL_TO` | Email de destino |

## Custo Mensal Estimado

| Serviço | Custo |
|---------|-------|
| GitHub Actions | $0 |
| NewsAPI | $0 |
| Claude Haiku | ~$0.30-1.50 |
| Resend | $0 |
| **Total** | **~$0.30-1.50/mês** |
