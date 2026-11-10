# Extração de Dados de Documentos

Sistema que lê **notas fiscais (NF-e), boletos, faturas de serviço e documentos pessoais (CNH e RG)**, identifica sozinho o tipo de documento, extrai os dados e mostra tudo na tela. Documentado passo a passo desde a concepção, como estudo de caso de Product Management.

> **Status:** 🟡 Etapa 3 — Validação do problema

## Objetivo

O usuário **importa um arquivo no computador** ou escaneia um QR code e **fotografa o documento com o celular**. Sem dizer o que ele é, recebe os dados na tela do computador, e o documento não fica salvo em lugar nenhum. O sistema:

1. Detecta o tipo: NF-e, boleto, fatura de serviço, CNH ou RG.
2. Lê o conteúdo (texto nativo ou OCR).
3. Extrai os campos daquele tipo.
4. Mostra os dados na tela, com indicação de confiança por campo, para o usuário confirmar ou recusar cada um.

## Como este repositório está organizado

| Pasta | Conteúdo |
|---|---|
| [`docs/etapas/`](docs/etapas/) | Diário do projeto: uma nota por etapa, na ordem em que aconteceu |
| [`docs/decisoes/`](docs/decisoes/) | Registro de decisões técnicas (ADRs): o que foi escolhido, alternativas e porquê |
| [`data/exemplos/`](data/exemplos/) | Documentos fictícios e gabaritos (conjunto de desenvolvimento) |
| [`src/extracao/`](src/extracao/) | Código-fonte do sistema |
| [`scripts/`](scripts/) | Gerador de documentos fictícios e rotina de limpeza e verificação |
| [`tests/`](tests/) | Testes automatizados |

## Documentos principais

- [Documento de requisitos (PRD)](docs/requisitos.md)
- [Fluxogramas do sistema](docs/arquitetura/fluxogramas.md)
- [Registro de decisões (ADRs)](docs/decisoes/README.md)

## Roteiro

| # | Etapa | Entregável principal | Status |
|---|---|---|---|
| 0 | [Concepção e escopo](docs/etapas/00-concepcao.md) | Problema, persona, hipóteses | ✅ Concluída |
| 1 | [Documentos de exemplo e campos-alvo](docs/etapas/01-documentos-e-campos.md) | Conjunto fictício, gabaritos, validadores | 🟡 Fotos dos impressos pendentes |
| 2 | [Arquitetura e requisitos](docs/etapas/02-arquitetura-e-requisitos.md) | PRD, fluxogramas, ADRs 0004–0006 | ✅ Concluída |
| 3 | Validação do problema e benchmark de concorrentes | Evidências para H1 e H5, mapa de concorrentes | ⚪ Pendente |
| 4 | Métricas: linha de base e metas | Metas de acurácia e tempo | ⚪ Pendente |
| 5 | Backlog priorizado e roadmap | Backlog com RICE, marcos | ⚪ Pendente |
| 6 | Prova de conceito técnica | Broadcast em pedaços; Vercel → `localhost` | ⚪ Pendente |
| 7 | Entrada: importação e cross-device | RF-01 a RF-07 | ⚪ Pendente |
| 8 | Pipeline: OCR, classificação, extração, validação | RF-08 a RF-15 | ⚪ Pendente |
| 9 | Tela de revisão | RF-16 a RF-21 | ⚪ Pendente |
| 10 | Testes de privacidade (resíduo zero) | RNF-01 a RNF-04 automatizados | ⚪ Pendente |
| 11 | Avaliação com testers | Relatório de acurácia com amostra | ⚪ Pendente |
| 12 | Retrospectiva e próximos passos | Lições aprendidas, roadmap pós-MVP | ⚪ Pendente |

O roteiro é vivo: etapas podem ser divididas, fundidas ou reordenadas conforme o projeto avança, e cada mudança fica registrada no diário.

## Autor

Marcos Pantoja — [github.com/marcosvpantoja](https://github.com/marcosvpantoja)
