# Extração de Dados de Documentos

Sistema que lê **notas fiscais (NF-e), boletos, faturas de serviço e documentos pessoais (CNH e RG)**, identifica sozinho o tipo de documento, extrai os dados e mostra tudo na tela. Projeto de **estudo de caso e pesquisa**, sem fins comerciais, documentado passo a passo desde a concepção que exercita os papéis de **PM, Arquitetura, PO, Desenvolvimento, Front-end, UX e QA**, com foco em **cadastro ágil e preciso de clientes em escritórios de advocacia de alto volume**.

> **Status:** 🟡 Etapas 0 a 8 concluídas · próxima: Etapa 9, captura pelo celular

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
- [Personas](docs/persona.md)
- [Competências demonstradas por papel](docs/competencias.md)

## Roteiro

Cada etapa produz artefatos ligados a um ou mais papéis ([mapa de competências](docs/competencias.md)).

| # | Etapa | Entregável principal | Status |
|---|---|---|---|
| 0 | [Concepção e escopo](docs/etapas/00-concepcao.md) | Problema, persona, hipóteses | ✅ Concluída |
| 1 | [Documentos de exemplo e campos-alvo](docs/etapas/01-documentos-e-campos.md) | Conjunto fictício, gabaritos, validadores | 🟡 Fotos dos impressos pendentes |
| 2 | [Arquitetura e requisitos](docs/etapas/02-arquitetura-e-requisitos.md) | PRD, fluxogramas, ADRs 0004–0006 | ✅ Concluída |
| 3 | [Validação do problema e benchmark](docs/etapas/03-validacao-do-problema.md) | Evidências, [personas](docs/persona.md), [entrevistas simuladas](docs/pesquisa/entrevistas-simuladas.md) | ✅ Concluída (entrevistas simuladas) |
| 4 | [Estratégia e mapeamento de oportunidades](docs/etapas/04-estrategia.md) | Visão, Opportunity Solution Tree, PR/FAQ, mapa de jornada | ✅ Concluída |
| 5 | [Métricas](docs/etapas/05-metricas.md) | North Star, métricas de apoio e proteção, árvore de métricas, OKRs | ✅ Concluída |
| 6 | [Priorização e roadmap](docs/etapas/06-priorizacao.md) | Backlog, RICE, escopo do MVP, DoR/DoD, roadmap | ✅ Concluída |
| 7 | [Business case](docs/etapas/07-business-case.md) | Receita, custos, mercado, licenciamento, stakeholders (hipotético) | ✅ Concluída |
| 8 | [Arquitetura detalhada e prova de conceito](docs/etapas/08-arquitetura-e-poc.md) | [C4](docs/arquitetura/c4.md); envio em pedaços ✅; Vercel → `localhost` ❌ no Safari, resolvido pelo [ADR 0011](docs/decisoes/0011-aplicacao-do-escritorio-servida-pelo-motor.md) | ✅ Concluída |
| 9 | Incremento 1: captura pelo celular | Wireframes e microcopy da captura; motor simulado; HU-02, 06, 07, 13, 14, 18, 20 | ⚪ Pendente |
| 10 | Incrementos 2 e 3: motor real | NF-e por importação, depois documentos pessoais e demais tipos; linha de base e metas dos OKRs | ⚪ Pendente |
| 11 | Tela de revisão e funções do escritório | Wireframes; revisão acessível; pacote, registro de acessos, dado errado (incremento 4) | ⚪ Pendente |
| 12 | Qualidade | Plano de testes; privacidade e remoção das 18h (RNF-01 a 04, RNF-12); ponta a ponta | ⚪ Pendente |
| 13 | Avaliação com usuários | Metas congeladas antes da 1ª sessão; teste de usabilidade; relatório de acurácia com amostra | ⚪ Pendente |
| 14 | Lançamento e retrospectiva | Plano de lançamento, resultados, lições aprendidas | ⚪ Pendente |

O roteiro é vivo: etapas podem ser divididas, fundidas ou reordenadas conforme o projeto avança, e cada mudança fica registrada no diário.

## Autor

Marcos Pantoja — [github.com/marcosvpantoja](https://github.com/marcosvpantoja)
