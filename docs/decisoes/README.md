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
| [0001](0001-transporte-cross-device.md) | Transporte cross-device: repasse com criptografia ponta a ponta + rede local como guardrail | Aceita (rede local adiada; persistência revista pelo 0007) |
| [0002](0002-motor-de-leitura-e-extracao.md) | Motor de leitura e extração: local, com comparação contra nuvem só em documentos fictícios | Aceita |
| [0003](0003-escopo-do-mvp.md) | Escopo do MVP: tese central, seis tipos, dois canais, sem rede local e sem streaming | Aceita |
| [0004](0004-revisao-humana-e-ciclo-de-aprendizado.md) | Revisão humana: confirmar/recusar por campo; aprendizado só com fictícios, medição com reais | Aceita |
| [0005](0005-infraestrutura-vercel-supabase-realtime.md) | Infraestrutura: Vercel (frontend) + Supabase Realtime Broadcast (repasse) | Aceita (banco e Storage liberados pelo 0007) |
| [0006](0006-ocr-apple-vision.md) | OCR: Apple Vision atrás de interface trocável | Aceita |
| [0007](0007-retencao-temporaria-e-purga-diaria.md) | Retenção temporária cifrada; remoção diária às 18h; nada na nuvem por 24h | Aceita (só no estudo de caso) |
| [0008](0008-armazenamento-em-producao.md) | Armazenamento em produção: criptografia com chave por escritório, controle de acesso, auditoria e retenção definida pelo escritório | Aceita como referência (não implementada) |
| [0009](0009-registro-de-auditoria-no-estudo.md) | Registro de auditoria no estudo: abrir, baixar e excluir documento, sem dados pessoais, com perfil simulado | Aceita |
