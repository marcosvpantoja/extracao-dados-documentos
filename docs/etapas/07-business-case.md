# Etapa 7: Business case

**Status:** 🟡 Em andamento · 11/11/2026
**Papéis:** PM

> **Hipotético.** Este projeto é um estudo de caso, não um produto comercial, e não pretende concorrer com softwares de gestão jurídica. O business case responde a uma pergunta de exercício: **se este estudo virasse produto, ele se sustentaria?** Todos os números são suposições declaradas.

---

## 1. Modelo de receita

**Faixas mensais por volume de cadastros.** O escritório escolhe um plano com limite de cadastros concluídos por mês.

| Alternativa | Por que não foi escolhida |
|---|---|
| Por cadastro concluído | Acompanha o valor, mas a receita do escritório e a do produto oscilam todo mês |
| Assinatura por assento (por assistente) | Previsível, mas o escritório que usa pouco paga o mesmo que o de massa |

### Preço pelo valor gerado

O preço parte do que o escritório **poupa**, e não do custo do produto.

| Suposição | Valor | Origem |
|---|---|---|
| Tempo poupado por cadastro | ~8 min | Hipótese; será medida pelo resultado-chave de tempo de cadastro (KR3) |
| Custo da hora de uma assistente, com encargos | ~R$ 30 | Suposição |
| **Economia por cadastro** | **~R$ 4** | 8 min × R$ 30/h |
| Parcela cobrada | ~30% | O escritório fica com cerca de 70% do ganho |
| **Preço de referência por cadastro** | **~R$ 1,20** | |

### Faixas

Volumes baseados nas [entrevistas simuladas](../pesquisa/entrevistas-simuladas.md): de 4 a mais de 50 clientes novos por dia, ou cerca de 100 a 1.100 por mês.

| Plano | Cadastros por mês | Preço mensal | Preço por cadastro | Perfil |
|---|---|---|---|---|
| Entrada | até 100 | R$ 149 | R$ 1,49 | Escritório pequeno |
| Escritório | até 300 | R$ 390 | R$ 1,30 | Escritório médio |
| Profissional | até 1.000 | R$ 1.190 | R$ 1,19 | Escritório de alto volume |
| Massa | até 3.000 | R$ 2.990 | R$ 1,00 | Advocacia de massa |

O preço por cadastro cai com o volume, mas fica sempre bem abaixo da economia estimada (~R$ 4).

**Risco do modelo:** se o tempo poupado medido no estudo for menor que 8 minutos, a economia cai e os preços deixam de se justificar. O preço depende diretamente do resultado-chave de tempo de cadastro (KR3).
