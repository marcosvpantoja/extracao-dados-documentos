# Etapa 2 — Arquitetura e requisitos

**Período:** 10/11/2026
**Status:** ✅ Concluída

## Objetivo

Transformar as decisões de produto em requisitos verificáveis e numa arquitetura que cumpra a tese do MVP: acerto alto sem que o documento fique salvo ou seja visto por terceiros.

## Entregáveis

| Entregável | Conteúdo |
|---|---|
| [Documento de requisitos (PRD)](../requisitos.md) | Histórias de usuário priorizadas (MoSCoW), requisitos funcionais e não funcionais com critérios de aceite, métricas, riscos |
| [Fluxogramas](../arquitetura/fluxogramas.md) | Sete visões: componentes, jornada, sequência cross-device, pipeline, estados da sessão, revisão e aprendizado, garantias de privacidade |
| [ADR 0004](../decisoes/0004-revisao-humana-e-ciclo-de-aprendizado.md) | Revisão humana; aprendizado só com documentos fictícios |
| [ADR 0005](../decisoes/0005-infraestrutura-vercel-supabase-realtime.md) | Vercel + Supabase Realtime Broadcast, sem banco nem storage |
| [ADR 0006](../decisoes/0006-ocr-apple-vision.md) | Apple Vision atrás de interface de OCR trocável |

## Arquitetura em uma frase

Páginas servidas pela **Vercel**; imagem cifrada no **celular** e repassada pelo **Supabase Realtime Broadcast**; leitura, classificação, extração e validação num **motor local em Python** no computador; resultado numa **tela de revisão** onde o usuário confirma ou recusa cada campo.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend (revisão e captura) | React + TypeScript |
| Criptografia | Web Crypto API (AES-GCM) |
| Canal de repasse | Supabase Realtime Broadcast |
| Hospedagem do frontend | Vercel |
| Motor local | Python + FastAPI |
| OCR | Apple Vision (via interface trocável) |
| Modelo de linguagem local (fallback) | Via Ollama, modelo a definir na prova de conceito |
| Validações | `src/extracao/validacoes.py` |

## Riscos técnicos a eliminar primeiro

A ordem de construção começa por uma **prova de conceito** dos dois riscos que podem invalidar a arquitetura:

1. Tamanho de mensagem no Supabase Broadcast para uma imagem cifrada em pedaços.
2. Página servida pela Vercel acessando o motor em `localhost`, no Chrome e no Safari.

## Próxima etapa

[Etapa 3 — Validação do problema e benchmark](03-validacao-do-problema.md).
