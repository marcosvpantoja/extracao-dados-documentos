# Etapa 6: Priorização e roadmap

**Status:** ✅ Concluída · 11/11/2026
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

---

## 3. RICE

**Nota = (Alcance × Impacto × Confiança) ÷ Esforço.** Quanto maior a nota, maior o valor por dia de trabalho.

### Como cada fator foi definido

| Fator | Escala | Quem definiu |
|---|---|---|
| **Alcance** | % das sessões com testers em que a história acontece, tirado do roteiro da sessão: link, captura e revisão = 100; importação = 50 (só com PDF); documento pendente = 30; não reconhecido = 20 | Derivado do roteiro, conferido pelo PM |
| **Impacto** | Pergunta: "sem essa função, o tester sairia com mais campos corrigidos?" Alto = 2 · Médio = 1 · Baixo = 0,5 | PM |
| **Confiança** | 80% quando há indício público ou de desenho; 50% quando depende só das entrevistas simuladas ou de palpite | PM e desenvolvimento |
| **Esforço** | Dias de trabalho, sem contar o motor de extração, que é a base de todas as histórias | Desenvolvimento |

**Contexto:** a pontuação reflete o **estudo**, e não um escritório real. Por isso as histórias de captura saem na frente, e as do escritório, como o registro de acessos (HU-22), saem atrás. Num produto real, a ordem seria outra.

### Resultado

| # | História | Alcance | Impacto | Confiança | Esforço | **Nota** |
|---|---|---|---|---|---|---|
| 1 | HU-23 Marcar dado errado depois da confirmação | 100 | 2 | 80% | 1,5 | **107** |
| 2 | HU-06 Saber quem acessa e por quanto tempo | 100 | 1 | 50% | 0,5 | **100** |
| 3 | HU-04 Confirmar ou recusar cada campo | 100 | 2 | 80% | 2 | **80** |
| 3 | HU-05 Campos de baixa confiança em destaque | 100 | 1 | 80% | 1 | **80** |
| 3 | HU-14 Entender a página sem ajuda | 100 | 2 | 80% | 2 | **80** |
| 6 | HU-10 Aviso de não reconhecido | 20 | 2 | 80% | 0,5 | **64** |
| 7 | HU-03 Dados ao lado da imagem | 100 | 2 | 80% | 3 | **53** |
| 7 | HU-07 Orientação de enquadramento e luz | 100 | 2 | 80% | 3 | **53** |
| 7 | HU-13 Enviar todos os documentos pelo link | 100 | 2 | 80% | 3 | **53** |
| 7 | HU-20 Saber na hora se a foto foi lida | 100 | 2 | 80% | 3 | **53** |
| 11 | HU-08 Copiar dados confirmados | 100 | 0,5 | 50% | 0,5 | **50** |
| 12 | HU-02 Enviar link ou QR ao cliente | 100 | 2 | 80% | 5 | **32** |
| 13 | HU-15 Baixar pacote do cliente | 100 | 1 | 50% | 2 | **25** |
| 14 | HU-01 Importar sem dizer o tipo | 50 | 1 | 80% | 2 | **20** |
| 15 | HU-21 Aviso de arquivo ilegível na importação | 50 | 1 | 50% | 1,5 | **17** |
| 16 | HU-09 Relatório de acurácia | 100 | 0,5 | 50% | 2 | **13** |
| 16 | HU-22 Registro de acessos | 100 | 0,5 | 50% | 2 | **13** |
| 18 | HU-18 Marcar "não tenho agora" | 30 | 0,5 | 50% | 2 | **4** |
| 18 | HU-19 Link só para os pendentes | 30 | 0,5 | 50% | 2 | **4** |

### Decisões sobre o resultado

| Questão | Decisão | Motivo |
|---|---|---|
| HU-08 e HU-22 tinham impacto alto, mas acontecem depois da revisão | Impacto reduzido para baixo (0,5) | A North Star conta as edições feitas na revisão; o valor delas é real, mas fica fora dessa métrica |
| O RICE não enxerga dependências: a HU-02 é pré-requisito da captura e ficou em 12º | A ordem do RICE é mantida; as dependências são resolvidas na construção | O RICE mede valor por esforço; a ordem de construção respeita o que precisa existir antes (seção 5, roadmap) |
| HU-18 e HU-19 ficaram em último | **HU-18 entra no MVP**; HU-19 fica para depois | O cliente marcar "não tenho agora" resolve o principal do achado N4. Sem a HU-19, a Juliana gera um link comum e monta a lista só com os pendentes (RF-33), o que cobre o caso manualmente |

---

## 4. Escopo do MVP

**Regra de corte:** entram as histórias com nota **20 ou mais**, além das exceções com motivo registrado.

| Situação | Histórias |
|---|---|
| **Entram pela nota** (≥ 20) | HU-23, HU-06, HU-04, HU-05, HU-14, HU-10, HU-03, HU-07, HU-13, HU-20, HU-08, HU-02, HU-15, HU-01 |
| **Entram por exceção** | HU-09: mede os resultados-chave; sem ela os OKRs não são medidos · HU-21: decidida para o MVP como RF-32 na [Etapa 4](04-estrategia.md#2-opportunity-solution-tree) · HU-22: decidida no [ADR 0009](../decisoes/0009-registro-de-auditoria-no-estudo.md) · HU-18: resolve o principal do achado N4 |
| **Ficam para depois** | HU-19 (link complementar, coberto à mão pela RF-33) · HU-12, HU-16 e HU-17 (já eram W) |

**O que o corte revelou:** com as exceções, só a HU-19 ficou de fora. O RICE serviu mais para definir a **ordem** de construção do que o **tamanho** do MVP. As exceções têm motivos válidos (medição, decisões já registradas), mas mostram que boa parte do escopo foi decidida antes da pontuação. Num produto real, a pontuação viria antes das decisões, e não depois.

As prioridades das histórias e dos requisitos novos foram atualizadas no [PRD](../requisitos.md#6-histórias-de-usuário).

---

## 5. Definição de pronto

### Pronta para começar (Definition of Ready)

Uma história só entra em construção quando:

- [ ] **Critérios de aceite:** cada requisito da história tem critério verificável no [PRD](../requisitos.md).
- [ ] **Wireframe aprovado:** histórias com tela têm wireframe e textos (microcopy) definidos.
- [ ] **Dependências prontas:** o que ela precisa (motor, link, tela de revisão) já existe ou está na mesma entrega.
- [ ] **Dados de teste:** os documentos fictícios e os gabaritos necessários já existem.

### Concluída (Definition of Done)

Uma história só é considerada pronta quando:

- [ ] **Testes automatizados:** os critérios de aceite são cobertos por testes, que rodam sem falha.
- [ ] **Privacidade verificada:** `scripts/limpar-e-verificar.sh` e os testes de resíduo retornam ✅ CONFIRMADO.
- [ ] **Acessível e responsivo:** quando houver tela, ela funciona no celular e no computador, com navegação por teclado e contraste AA.
- [ ] **Documentado:** PRD, fluxogramas e ADRs atualizados, se a história mudou alguma decisão.
- [ ] **Aceite do PO:** o PO confere a história contra os critérios de aceite e registra o aceite antes de dá-la como pronta.

---

## 6. Roadmap

**Estratégia: captura primeiro.** O foco do estudo é o cliente capturando os documentos, então a captura pelo celular é construída antes do motor de extração, com um **motor simulado** que devolve respostas prontas, inclusive falhas de leitura para testar o pedido de nova foto (RF-31). O motor real entra depois, começando pelo documento mais fácil.

| Incremento | Etapa | O que entrega | Histórias |
|---|---|---|---|
| **0 · Prova de conceito** | 8 | Os dois riscos técnicos testados antes de construir: envio em pedaços pelo Broadcast e página na nuvem chamando o motor local | — |
| **1 · Captura pelo celular** | 9 | Link, lista de documentos, câmera com orientação, envio cifrado, "não tenho agora" e nova foto pedida na hora, com motor simulado | HU-02, HU-06, HU-07, HU-13, HU-14, HU-18, HU-20 |
| **2 · Motor real com NF-e** | 10 e 11 | Importação, leitura, classificação e extração da NF-e, com a tela de revisão. Vitória rápida: PDF com texto nativo e chave de 44 dígitos | HU-01, HU-03, HU-04, HU-05, HU-10, HU-21 |
| **3 · Documentos pessoais e demais tipos** | 10 | CNH, CIN e RG antigo fotografados, ligando o motor real à captura; boleto e fatura | HU-01, HU-13 (com motor real) |
| **4 · Escritório e medição** | 11 e 12 | Pacote do cliente, cópia dos dados, registro de acessos, marcação de dado errado, relatório de acurácia e remoção das 18h | HU-08, HU-09, HU-15, HU-22, HU-23 |

**Por que essa ordem:**

- **O incremento 0 vem antes de tudo** porque a captura depende dos dois riscos técnicos que ele testa. Se um deles falhar, a arquitetura muda antes de existir código para jogar fora.
- **O motor simulado** permite testar a experiência de captura, que é o foco do estudo, sem esperar o motor real. O risco é a captura ser desenhada para um motor que ainda não existe; o incremento 3 corrige isso ao ligar os dois.
- **A NF-e abre o motor real** por ser o tipo mais fácil, mas chega por importação, e não pelo celular. Os documentos pessoais, que são os capturados, só ganham motor real no incremento 3.
- **O incremento 4 precisa terminar antes da Etapa 13**, porque o relatório de acurácia (HU-09) e a marcação de dado errado (HU-23) são o que mede os resultados-chave.

**Linha de base e metas:** medidas no fim dos incrementos 2 e 3, sobre o conjunto fictício, e congeladas antes da Etapa 13 ([Etapa 5](05-metricas.md#como-as-metas-serão-definidas)).

| Alternativa | Por que não foi escolhida |
|---|---|
| Fatias de ponta a ponta, um tipo por vez | Teria algo funcionando mais cedo, mas adiaria a captura, que é o foco do estudo |
| Por camada (entrada, motor, revisão) | Só funcionaria de ponta a ponta no fim, sem nada para mostrar antes |
