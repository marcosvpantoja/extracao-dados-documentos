# Extração de Dados de Documentos

Sistema de leitura e extração de dados estruturados a partir de documentos (PDFs, imagens digitalizadas, fotos de documentos), documentado passo a passo desde a concepção.

> **Status:** 🟡 Etapa 0 — Concepção

## Objetivo

Receber um documento, identificar o tipo, ler o conteúdo (texto nativo ou OCR) e devolver os campos relevantes em formato estruturado (JSON), com indicação de confiança e possibilidade de revisão humana.

## Como este repositório está organizado

| Pasta | Conteúdo |
|---|---|
| [`docs/etapas/`](docs/etapas/) | Diário do projeto: uma nota por etapa, na ordem em que aconteceu |
| [`docs/decisoes/`](docs/decisoes/) | Registro de decisões técnicas (ADRs): o que foi escolhido, alternativas e porquê |
| `src/` | Código-fonte (a partir da etapa de implementação) |

## Roteiro

| # | Etapa | Status |
|---|---|---|
| 0 | [Concepção e escopo](docs/etapas/00-concepcao.md) | 🟡 Em andamento |
| 1 | Levantamento de documentos e campos-alvo | ⚪ Pendente |
| 2 | Arquitetura e escolha de stack | ⚪ Pendente |
| 3 | Ingestão e pré-processamento (PDF/imagem) | ⚪ Pendente |
| 4 | Leitura: texto nativo + OCR | ⚪ Pendente |
| 5 | Classificação do tipo de documento | ⚪ Pendente |
| 6 | Extração de campos estruturados | ⚪ Pendente |
| 7 | Validação, confiança e revisão humana | ⚪ Pendente |
| 8 | API / interface | ⚪ Pendente |
| 9 | Avaliação (métricas de acurácia) | ⚪ Pendente |
| 10 | Deploy e monitoramento | ⚪ Pendente |

O roteiro é vivo: etapas podem ser divididas, fundidas ou reordenadas conforme o projeto avança, e cada mudança fica registrada no diário.

## Autor

Marcos Pantoja — [github.com/marcosvpantoja](https://github.com/marcosvpantoja)
