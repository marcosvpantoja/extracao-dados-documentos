# Extração de Dados de Documentos

Sistema que lê **notas fiscais (NF-e), boletos, faturas de serviço e documentos pessoais (CNH e RG)**, identifica sozinho o tipo de documento, extrai os dados e mostra tudo na tela. Documentado passo a passo desde a concepção, como estudo de caso de Product Management.

> **Status:** 🟡 Etapa 1 — Documentos de exemplo e campos-alvo

## Objetivo

O usuário **importa um arquivo no computador** ou escaneia um QR code e **fotografa o documento com o celular**. Sem dizer o que ele é, recebe os dados na tela do computador, e o documento não fica salvo em lugar nenhum. O sistema:

1. Detecta o tipo: NF-e, boleto, fatura de serviço, CNH ou RG.
2. Lê o conteúdo (texto nativo ou OCR).
3. Extrai os campos daquele tipo.
4. Mostra os dados na tela, com indicação de confiança por campo.

## Como este repositório está organizado

| Pasta | Conteúdo |
|---|---|
| [`docs/etapas/`](docs/etapas/) | Diário do projeto: uma nota por etapa, na ordem em que aconteceu |
| [`docs/decisoes/`](docs/decisoes/) | Registro de decisões técnicas (ADRs): o que foi escolhido, alternativas e porquê |
| [`data/exemplos/`](data/exemplos/) | Documentos fictícios e gabaritos (conjunto de desenvolvimento) |
| [`src/extracao/`](src/extracao/) | Código-fonte do sistema |
| [`scripts/`](scripts/) | Gerador de documentos fictícios e rotina de limpeza e verificação |
| [`tests/`](tests/) | Testes automatizados |

## Roteiro

| # | Etapa | Status |
|---|---|---|
| 0 | [Concepção e escopo](docs/etapas/00-concepcao.md) | ✅ Concluída |
| 1 | Documentos de exemplo, campos-alvo e validação do problema | 🟡 Em andamento |
| 2 | Arquitetura e escolha de stack | ⚪ Pendente |
| 3 | Entrada: importação e captura pelo celular via QR code | ⚪ Pendente |
| 4 | Leitura: texto nativo + OCR | ⚪ Pendente |
| 5 | Classificação automática do tipo de documento | ⚪ Pendente |
| 6 | Extração de campos estruturados | ⚪ Pendente |
| 7 | Validação, confiança e verificação de resíduo zero | ⚪ Pendente |
| 8 | Tela de resultado | ⚪ Pendente |
| 9 | Avaliação (métricas de acurácia) | ⚪ Pendente |
| 10 | Deploy e monitoramento | ⚪ Pendente |

O roteiro é vivo: etapas podem ser divididas, fundidas ou reordenadas conforme o projeto avança, e cada mudança fica registrada no diário.

## Autor

Marcos Pantoja — [github.com/marcosvpantoja](https://github.com/marcosvpantoja)
