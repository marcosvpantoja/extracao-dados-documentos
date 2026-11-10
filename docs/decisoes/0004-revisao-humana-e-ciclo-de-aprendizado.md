# 0004 — Revisão humana e ciclo de aprendizado

**Data:** 10/11/2026
**Status:** Aceita

## Contexto

O sistema precisa de uma tela onde o usuário vê os dados extraídos e **confirma ou recusa** cada um, e essas respostas devem servir para o sistema melhorar. O requisito esbarra em duas decisões anteriores:

1. **Não salvar dados** ([ADR 0001](0001-transporte-cross-device.md)): aprender com uma correção exige guardar o valor correto, o que é guardar dado pessoal.
2. **Separar desenvolvimento de avaliação** ([Etapa 1](../etapas/01-documentos-e-campos.md)): se o sistema aprender com as sessões de testers, a avaliação vira treino e a medição fica viciada.

## Decisão

### Tela de revisão

Depois da extração, o computador mostra, lado a lado, a imagem do documento e os campos extraídos. Para cada item:

| Item | Ações |
|---|---|
| Tipo detectado | Confirmar / Recusar (e indicar o tipo correto) |
| Cada campo | Confirmar / Recusar |
| Correção do valor | Disponível **só no modo desenvolvimento** |

A confiança de cada campo (validações automáticas + confiança do motor de leitura) aparece junto, para o usuário saber onde olhar primeiro.

### O que é registrado depende do modo

| | Modo desenvolvimento | Modo avaliação / produção |
|---|---|---|
| Documentos | Fictícios | Reais |
| Confirmar / recusar | Registrado | Registrado |
| Valor extraído e valor corrigido | Registrado | **Nunca registrado** |
| Imagem do documento | Já está no repositório | **Nunca registrada** |
| Uso | **Aprendizado** | **Só medição** |

O modo é definido na abertura da sessão e exibido na tela. Documentos reais nunca abrem no modo desenvolvimento.

### O que "aprendizado" significa no MVP

O MVP **não retreina modelos de IA**. O ciclo de aprendizado usa as revisões para:

1. **Medir:** acurácia por campo e por tipo, apontando onde o sistema mais erra.
2. **Calibrar a confiança:** ajustar os limites a partir dos quais um campo é marcado como "conferir".
3. **Corrigir regras e prompts:** cada erro revisado no modo desenvolvimento vira um caso de teste de regressão.
4. **Priorizar:** os campos com mais recusas definem o que melhorar na próxima versão.

Retreinamento ou ajuste fino de modelos fica fora do MVP: exige volume de dados rotulados, hardware e, com documentos reais, consentimento específico para uso em treinamento.

## Alternativas consideradas

- **Aprender também com documentos reais, guardando as correções** — o sistema melhoraria com dados verdadeiros, mas viola o "nada salvo" e contamina a avaliação. Recusada.
- **Tela só de visualização, sem confirmar/recusar** — mais simples, mas perde a medição em produção e o ciclo de melhoria. Recusada.

## Consequências

- A mesma tela serve à revisão do usuário, à avaliação com testers e ao aprendizado no desenvolvimento.
- Em produção, o sistema mede a própria acurácia sem guardar dado pessoal.
- O aprendizado depende do volume e da variedade dos documentos fictícios. Se os erros em produção forem de um tipo que os fictícios não cobrem, novos fictícios precisam ser gerados para reproduzi-los.
