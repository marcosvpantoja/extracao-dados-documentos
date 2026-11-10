# Extração de Dados de Documentos

Sistema que lê **notas fiscais (NF-e), boletos e documentos pessoais (CNH e RG)**, identifica sozinho o tipo de documento, extrai os dados e mostra tudo na tela. Documentado passo a passo desde a concepção, como estudo prático de Product Management.

> **Status:** 🟡 Etapa 0 — Concepção

## Objetivo

O usuário envia um documento (PDF ou foto) **sem dizer o que ele é**. O sistema:

1. Detecta o tipo: NF-e, boleto, CNH ou RG.
2. Lê o conteúdo (texto nativo ou OCR).
3. Extrai os campos daquele tipo.
4. Mostra os dados na tela, com indicação de confiança por campo.

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
| 1 | Documentos de exemplo e campos-alvo (NF-e, boleto, CNH, RG) | ⚪ Pendente |
| 2 | Arquitetura e escolha de stack | ⚪ Pendente |
| 3 | Ingestão e pré-processamento (PDF/imagem) | ⚪ Pendente |
| 4 | Leitura: texto nativo + OCR | ⚪ Pendente |
| 5 | Classificação automática do tipo de documento | ⚪ Pendente |
| 6 | Extração de campos estruturados | ⚪ Pendente |
| 7 | Validação, confiança e revisão humana | ⚪ Pendente |
| 8 | Tela de resultado | ⚪ Pendente |
| 9 | Avaliação (métricas de acurácia) | ⚪ Pendente |
| 10 | Deploy e monitoramento | ⚪ Pendente |

O roteiro é vivo: etapas podem ser divididas, fundidas ou reordenadas conforme o projeto avança, e cada mudança fica registrada no diário.

## Autor

Marcos Pantoja — [github.com/marcosvpantoja](https://github.com/marcosvpantoja)
