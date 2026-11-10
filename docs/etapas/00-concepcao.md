# Etapa 0 — Concepção e discovery

**Data de início:** 10/11/2026
**Status:** 🟡 Em andamento
**Atributo de PM praticado:** Discovery e definição do problema

## Natureza do projeto

Projeto de **estudo**, sem cliente real. O objetivo é praticar, de ponta a ponta, as atribuições de Product Management (discovery, requisitos, priorização, métricas, decisões técnicas, riscos de IA, roadmap e comunicação) enquanto o sistema é construído. Personas e cenários são **hipóteses explícitas**, validadas com pesquisa pública e documentos de exemplo, não com dados de clientes.

> Convenção: tudo marcado com 🧪 é hipótese ainda não validada. Quando for validada (ou descartada), a marca muda para ✅ ou ❌ com a fonte da evidência.

## Cenário de trabalho 🧪

Um **escritório de contabilidade de pequeno porte** que atende dezenas de clientes PME. Todo mês recebe notas fiscais e boletos por e-mail e WhatsApp, em PDF ou foto, e a equipe digita os dados manualmente no sistema contábil.

**Por que esse cenário para um estudo:**
- NF-e (DANFE) e boletos têm layout padronizado, então dá para medir acurácia campo a campo.
- Existem exemplos públicos e é possível gerar documentos fictícios.
- Tem dor clara (trabalho repetitivo e sazonal) e um usuário que revisa o resultado.

## Persona 🧪

**Ana, assistente contábil**
- Recebe os documentos dos clientes por canais misturados (e-mail, WhatsApp, pasta compartilhada).
- Digita CNPJ, número da nota, data, valores e impostos no sistema contábil.
- Picos de trabalho no fechamento do mês.
- **Dor principal:** tempo gasto em digitação e retrabalho causado por erro de digitação.
- **O que ela precisa:** confiar no dado extraído sem ter que conferir tudo.

## Problema em uma frase 🧪

> Assistentes contábeis gastam parte relevante do fechamento mensal digitando dados de notas fiscais e boletos, um trabalho repetitivo e propenso a erro que atrasa as entregas e gera retrabalho.

## Proposta de solução (alto nível)

```
Documento ──► Ingestão ──► Leitura (texto/OCR) ──► Classificação ──► Extração ──► Validação ──► JSON
                                                                                      │
                                                                                      └──► Revisão humana (baixa confiança)
```

## Mapa de hipóteses

| # | Hipótese | Risco se estiver errada | Como validar |
|---|---|---|---|
| H1 🧪 | A digitação de NF/boleto consome tempo significativo no fechamento | Problema pequeno demais para justificar o produto | Pesquisa pública (fóruns de contadores, conteúdos do setor), conversas informais |
| H2 🧪 | Os documentos chegam majoritariamente em PDF digital, não em foto | OCR vira o gargalo e a acurácia cai | Coletar amostra de exemplos e classificar por formato |
| H3 🧪 | O usuário aceita revisar só os campos de baixa confiança | Se precisar revisar tudo, o ganho de tempo some | Protótipo da tela de revisão (Etapa 7) |
| H4 🧪 | Soluções existentes são caras ou complexas demais para escritório pequeno | Mercado já resolvido | Benchmark de concorrentes |

## Fora de escopo (por enquanto)

- Integração direta com sistemas contábeis específicos.
- Documentos manuscritos.
- Lançamento contábil automático (o sistema extrai, não contabiliza).

## Critérios de sucesso (rascunho)

- Acurácia por campo, medida sobre um conjunto rotulado de documentos de exemplo.
- Percentual de documentos aprovados sem nenhuma correção humana.
- Tempo médio de processamento por documento.

As metas numéricas serão definidas na etapa de métricas, depois de medir uma linha de base.

## ✍️ Sua tarefa como PM nesta etapa

1. **Revisar a persona e o problema:** concorda? Mudaria o cenário?
2. **Validar H1 e H4:** pesquisar como contadores falam dessa dor (fóruns, LinkedIn, YouTube) e listar 3 concorrentes ou soluções existentes.
3. **Escolher os campos-alvo do MVP:** quais dados da NF-e e do boleto são indispensáveis?

As respostas fecham a Etapa 0 e abrem a Etapa 1 (documentos e campos-alvo).
