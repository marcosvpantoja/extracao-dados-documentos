# 0003 — Escopo do MVP

**Data:** 10/11/2026
**Status:** Aceita

## Contexto

Ao longo da concepção o escopo cresceu: cinco tipos de documento, dois modelos de RG, dois modos de conexão (repasse na nuvem e rede local), campos exibidos em streaming, captura automática pela câmera e processamento local. Uma revisão crítica apontou quatro problemas:

1. **Inchaço do MVP:** muitas frentes para validar uma tese central.
2. **Tempo real como solução, não como problema:** não havia evidência de que o usuário precisa ver campos surgindo um a um, e o requisito conflita com o processamento local, mais lento.
3. **Modo rede local sem demanda:** nenhum usuário pediu operação offline; manter dois modos dobra a superfície de construção e teste.
4. **Discovery pulado:** todas as hipóteses seguiam sem validação.

## Decisão

**Tese que o MVP precisa provar:**

> É possível capturar documentos pelo celular ou importá-los no computador e receber os dados extraídos com acerto alto, sem que o documento fique salvo em nenhum dispositivo ou servidor, nem seja visto por terceiros.

| Item | Decisão |
|---|---|
| Tipos de documento | **Mantidos:** NF-e, boleto, fatura de serviço, CNH, RG antigo e CIN |
| Canais de entrada | **Ambos para qualquer tipo:** importação de arquivo no computador e captura via cross-device |
| Transporte cross-device | Só repasse com criptografia ponta a ponta ([ADR 0001](0001-transporte-cross-device.md)). **Modo rede local sai do MVP** |
| Tempo real | Substituído por **"rápido o suficiente"**, com meta de tempo até o resultado completo. Streaming de campos e captura automática saem do MVP |
| Discovery | Hipóteses de problema e mercado (H1, H5) validadas com pesquisa pública antes da implementação |

**Ordem de construção:** CNH e RG primeiro, por serem os documentos que exercitam o cross-device e a privacidade; depois fatura, boleto e NF-e, aproveitando o mesmo pipeline.

## Alternativas consideradas

- **MVP só com CNH e RG via cross-device** — menor esforço e foco total na tese de segurança. Recusada: o produto perde a classificação automática entre documentos pessoais e financeiros, que é parte da proposta de valor.
- **Manter o escopo integral** — recusada pelos problemas descritos no contexto.

## Consequências

- Classificação automática continua sendo testada em seis tipos, o que mantém o MVP grande; a ordem de construção mitiga o risco entregando valor por partes.
- Um único pipeline atende os dois canais: o canal só muda a origem do arquivo.
- Persona reposicionada para o momento em que todos os tipos aparecem juntos (ver Etapa 0).
- Requisitos retirados ficam no backlog, não descartados.
