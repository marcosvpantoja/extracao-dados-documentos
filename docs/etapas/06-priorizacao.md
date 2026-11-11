# Etapa 6: Priorização e roadmap

**Status:** 🟡 Em andamento · 11/11/2026
**Papéis:** PM, PO
**Entradas:** [PRD](../requisitos.md), [Etapa 4](04-estrategia.md), [Etapa 5](05-metricas.md), [entrevistas simuladas](../pesquisa/entrevistas-simuladas.md)

A etapa tem quatro partes: o backlog, a pontuação RICE, a definição de pronto (DoR e DoD) e o roadmap. Antes delas, uma decisão de escopo precisava ser tomada, porque mudava o que entra no backlog.

---

## 1. Documento pendente (achado N4)

**Problema:** as [entrevistas simuladas](../pesquisa/entrevistas-simuladas.md) indicam que o cadastro muitas vezes espera dias pelo último documento. O link de captura é de uso único e expira (RF-03), então o Roberto não consegue voltar depois para enviar o que faltou.

**Decisão:**

1. Ao gerar o link, **a Juliana monta a lista** de documentos esperados daquele cliente (RF-33).
2. Na página de captura, o Roberto marca **"não tenho agora"** no que não tiver em mãos e envia o restante (RF-34).
3. A Juliana vê a pendência e, quando o Roberto avisar que tem o documento, envia **um novo link só com o que falta** (RF-35).
4. **No estudo**, se o envio complementar acontecer em outro dia, ele gera um **pacote complementar**, porque o envio anterior foi removido às 18h (RF-36, [ADR 0007](../decisoes/0007-retencao-temporaria-e-purga-diaria.md)). A Juliana junta os dois pacotes no software jurídico. Em produção, os documentos ficam guardados e o cadastro é completado no mesmo lugar ([ADR 0008](../decisoes/0008-armazenamento-em-producao.md)).

**Por que essa solução:** a segurança não muda. Cada link continua de uso único, e nenhum link fica válido por dias. Ela também segue o princípio "corrigir na origem": o Roberto diz na hora o que não tem, em vez de a Juliana descobrir depois.

| Alternativa | Por que não foi escolhida |
|---|---|
| Link válido por vários dias | Abre uma janela longa para uso indevido do link |
| Lista padrão igual para todos, editável | Poupa tempo, mas a lista montada a cada cliente foi preferida para refletir cada caso |
| Sem lista: o cliente envia o que tiver e escreve o que faltou | Perde o controle do que está pendente |
| No estudo, exigir que o tester traga todos os documentos | Deixaria o fluxo de pendência sem teste |

**Custo conhecido:** montar a lista a cada cliente toma tempo da Juliana em todo atendimento, e esse tempo entra no tempo de cadastro medido pelo KR3.

**Impacto na North Star:** um cliente com documento pendente só conta como "cadastrado sem edição" quando o último documento chegar e for confirmado.
