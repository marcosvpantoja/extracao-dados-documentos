# Registro de decisões (ADRs)

Cada decisão técnica relevante ganha um arquivo `NNNN-titulo-curto.md` neste diretório, seguindo o modelo abaixo.

```markdown
# NNNN — Título da decisão

**Data:** DD/MM/AAAA
**Status:** Proposta | Aceita | Substituída por NNNN

## Contexto
Qual problema ou restrição levou a essa decisão.

## Decisão
O que foi escolhido.

## Alternativas consideradas
- Opção A — prós / contras
- Opção B — prós / contras

## Consequências
O que muda, o que fica mais fácil e o que fica mais difícil.
```

## Índice

| ADR | Decisão | Status |
|---|---|---|
| [0001](0001-transporte-cross-device.md) | Transporte cross-device: repasse com criptografia ponta a ponta + rede local como guardrail | Aceita |
| [0002](0002-motor-de-leitura-e-extracao.md) | Motor de leitura e extração: local, com comparação contra nuvem só em documentos fictícios | Aceita |
