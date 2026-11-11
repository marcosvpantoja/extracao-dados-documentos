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

---

## 2. Backlog

**Unidade:** histórias de usuário. O RICE pergunta pelo impacto no usuário, e a história é a unidade que tem usuário. Cada história aponta para os requisitos que a compõem, e o esforço é estimado a partir deles.

### Ajustes antes de pontuar

| História | Ajuste | Motivo |
|---|---|---|
| HU-06 | "não fica guardado" passou a "saber quem terá acesso e por quanto tempo" | Em produção os documentos ficam guardados ([ADR 0008](../decisoes/0008-armazenamento-em-producao.md)) |
| HU-08 | "sistema contábil" passou a "software jurídico" | Resto da persona contábil, anterior ao pivô de segmento |
| HU-11 | Absorvida pela HU-13 | Enviar vários documentos numa sessão já é a HU-13 |
| HU-20 a HU-23 | Criadas | Requisitos decididos depois do PRD ficaram sem história (RF-28 a RF-32) |

### Histórias e requisitos

| História | Resumo | Requisitos | Prioridade atual |
|---|---|---|---|
| HU-01 | Importar sem dizer o tipo | RF-01, RF-08 a RF-11 | M |
| HU-02 | Enviar link ou QR ao cliente | RF-02, RF-03, RF-07 | M |
| HU-03 | Dados ao lado da imagem | RF-16 | M |
| HU-04 | Confirmar ou recusar cada campo | RF-17 | M |
| HU-05 | Ver campos de baixa confiança | RF-14 | M |
| HU-06 | Saber quem acessa e por quanto tempo | RF-07, RF-21 | M |
| HU-07 | Orientação de enquadramento e luz | RF-05, RF-06 | S |
| HU-08 | Copiar dados confirmados | RF-20 | S |
| HU-09 | Ver acurácia por campo e tipo | RF-22 a RF-25 | S |
| HU-10 | Aviso de documento não reconhecido | RF-10, RF-15 | M |
| HU-12 | Captura automática | — | W |
| HU-13 | Enviar todos os documentos pelo link | RF-04, RF-06 | M |
| HU-14 | Entender a página sem ajuda | RF-04, RF-05 | M |
| HU-15 | Baixar pacote do cliente | RF-26, RF-27 | M |
| HU-16 | Procuração preenchida | — | W |
| HU-17 | Documentos trabalhistas | — | W |
| HU-18 | Marcar "não tenho agora" | RF-33, RF-34 | A definir |
| HU-19 | Link só para os pendentes | RF-35, RF-36 | A definir |
| HU-20 | Saber na hora se a foto foi lida | RF-31 | A definir |
| HU-21 | Aviso de arquivo ilegível na importação | RF-32 | A definir |
| HU-22 | Saber quem acessou cada documento | RF-28, RF-29 | A definir |
| HU-23 | Marcar dado errado depois da confirmação | RF-30 | A definir |

Requisitos de base, que não pertencem a uma história só (validações RF-12 e RF-13, modo da sessão RF-19, correção no modo desenvolvimento RF-18), entram no esforço das histórias que dependem deles.
