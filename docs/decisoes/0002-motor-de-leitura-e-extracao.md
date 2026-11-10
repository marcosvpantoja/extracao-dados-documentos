# 0002 — Motor de leitura e extração: processamento local, com comparação contra IA na nuvem só em documentos fictícios

**Data:** 10/11/2026
**Status:** Aceita

## Contexto

O transporte é protegido por criptografia ponta a ponta ([ADR 0001](0001-transporte-cross-device.md)), mas isso não resolve onde o documento é **lido**. Se a extração usar um serviço na nuvem, o documento sai dos dois aparelhos. As duas prioridades do produto são segurança dos dados e acerto nos campos extraídos.

## Decisão

1. **Processamento no computador** (OCR e/ou modelo de visão rodando localmente) é o caminho principal. Nenhum documento real sai dos dois aparelhos.
2. **IA de visão na nuvem é avaliada apenas no conjunto de desenvolvimento** (documentos fictícios), em comparação direta com o processamento local.
3. A comparação mede, por tipo de documento: acurácia por campo, tempo até o resultado e custo por documento.
4. A nuvem só passa a ser usada com documentos reais se a diferença de acurácia justificar, com nova ADR registrando o motivo e a política de retenção do provedor.

## Custo: desenvolvimento x operação

| | Local | IA de visão na nuvem |
|---|---|---|
| **Custo de desenvolvimento** | Maior: instalar e configurar modelos, ajustar OCR e regras por layout, lidar com a variedade do RG antigo | Menor: um prompt e um esquema de campos por tipo; incluir novo tipo de documento é rápido |
| **Custo de operação** | Sem custo por documento; depende do hardware do computador | Cobrança por uso (por imagem processada) |
| **Latência** | Depende do hardware; modelos de visão locais podem ser lentos sem GPU | Depende da rede e do provedor |
| **Privacidade** | Documento não sai dos aparelhos | Documento trafega até o provedor |

Ou seja, a nuvem tende a ser **mais barata e rápida de desenvolver** e **mais cara de operar** em volume. O processamento local inverte essa relação e é o único que cumpre plenamente a prioridade de segurança. Os custos reais de operação serão medidos no benchmark, não estimados.

## Alternativas consideradas

- **Leitura no celular** — máxima privacidade; acurácia limitada pela capacidade do aparelho e por modelos que rodam no navegador. Pode ser revisitada para etapas de pré-processamento (detecção de borda e nitidez para a captura automática).
- **Nuvem como caminho principal** — menor esforço de desenvolvimento e provável maior acurácia; contraria a prioridade de que nenhum dado saia dos aparelhos.

## Consequências

- O produto pode afirmar que documentos reais nunca saem do celular e do computador.
- Maior esforço de desenvolvimento no motor local.
- A decisão sobre a nuvem passa a ser baseada em dados medidos, sem expor dados reais.
- O requisito de tempo real depende do desempenho do hardware local, a ser medido.
