# 0010 — Motor de extração em produção

**Data:** 11/11/2026
**Status:** Aceita como desenho de referência · **não implementada no estudo de caso**, que segue os ADRs [0002](0002-motor-de-leitura-e-extracao.md) e [0006](0006-ocr-apple-vision.md)

## Contexto

No estudo, o motor de extração roda no Mac do autor e usa o Apple Vision para ler o texto ([ADR 0006](0006-ocr-apple-vision.md)). O business case da [Etapa 7](../etapas/07-business-case.md) mostrou que esse desenho não se sustenta num produto vendido a escritórios: cada escritório precisaria de um Mac com o motor instalado, além de suporte para instalação e atualização.

## Decisão

Em produção, o motor roda num **servidor próprio na nuvem**:

- **Leitura de texto:** PaddleOCR (código aberto), atrás da mesma interface de OCR trocável do estudo ([ADR 0006](0006-ocr-apple-vision.md)). A troca do Apple Vision pelo PaddleOCR não muda o resto do pipeline.
- **Modelo de linguagem de apoio:** um modelo aberto rodando no mesmo servidor, sem chamadas a provedores de IA de terceiros.
- **Armazenamento:** segue o [ADR 0008](0008-armazenamento-em-producao.md).

Os documentos continuam **sem passar por empresas de IA de terceiros**. O motor é da própria aplicação, e só a infraestrutura é alugada.

## Alternativas consideradas

- **Motor no computador do escritório** — custo de servidor quase zero, mas exige instalação e suporte em cada escritório, e o Apple Vision só funciona em Mac. Contradiz a ideia de começar a usar sem instalar nada. Recusada.
- **API de IA de terceiros** — mais rápida de lançar, mas os documentos passariam por outra empresa, o que o estudo evitou desde o [ADR 0002](0002-motor-de-leitura-e-extracao.md). Recusada.

## Consequências

- **Custo mensal de servidor**, que passa a ser o principal custo variável do produto ([Etapa 7](../etapas/07-business-case.md)).
- **A acurácia medida no estudo, com o Apple Vision, não vale automaticamente para o PaddleOCR.** A troca exige repetir a medição no conjunto fictício antes de qualquer lançamento.
- O servidor passa a ver os documentos durante o processamento, o que já é aceito pelo modelo de segurança de produção ([ADR 0008](0008-armazenamento-em-producao.md)).
