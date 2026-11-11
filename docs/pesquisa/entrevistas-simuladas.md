# Entrevistas simuladas

> **🧪 SIMULADO.** As cinco entrevistas abaixo são **fictícias**. Escritórios, pessoas, falas e números foram criados para este estudo de caso e **não são evidência**. Elas foram escritas para serem coerentes com a pesquisa pública da [Etapa 3](../etapas/03-validacao-do-problema.md) e servem para demonstrar o método: roteiro, condução, síntese e decisão. Nenhuma hipótese é considerada validada por elas.

**Por que simular:** o prazo do estudo não comporta o recrutamento de profissionais de escritórios. A alternativa seria pular a etapa. Simular mantém o método visível e deixa claro o que precisaria ser confirmado com pessoas reais.

**Como foram construídas:**
- O perfil de cada entrevistado varia em porte do escritório, cargo e região, para cobrir o segmento e um caso fora dele.
- As respostas partem dos achados públicos **[B1]–[B4]** e incluem **divergências**, porque entrevistados reais não concordam em tudo.
- Os números são plausíveis, mas inventados. Eles servem para mostrar como a síntese seria feita, não para dimensionar o problema.

**Roteiro:** as sete perguntas de [Personas](../persona.md#perguntas-para-as-entrevistas).

---

## Perfis

| # | Pessoa (fictícia) | Cargo | Escritório (fictício) | Porte | Clientes novos por dia |
|---|---|---|---|---|---|
| E1 | Camila | Assistente de cadastro | Escritório A, São Paulo (SP) | 40 pessoas | 25 a 35 |
| E2 | Renata | Coordenadora de atendimento | Escritório B, Belo Horizonte (MG) | 15 pessoas | 10 a 15 |
| E3 | Dra. Helena | Advogada sócia | Escritório C, interior de SP | 5 pessoas | 4 a 6 |
| E4 | Diego | Assistente de cadastro | Escritório D, Recife (PE) | 80 pessoas | 50 ou mais |
| E5 | Lucas | Assistente jurídico | Escritório E, Curitiba (PR) | 12 pessoas | 8 a 12 |

E3 foi incluída de propósito **fora do perfil de alto volume**, para testar se o problema existe em escritórios pequenos.

---

## E1 · Camila, assistente de cadastro, Escritório A

**1. Clientes por dia:** "Entre 25 e 35 novos. Em semana de campanha nas redes sociais passa de 50."

**2. Tempo de cadastro:** "Uns 15 minutos, quando o cliente manda tudo certo. Mas o cadastro só termina quando chega o último documento, e isso pode levar dois dias."

**3. Documentos e canal:** "RG ou CNH, comprovante de residência e as provas: fatura, print da cobrança, nota fiscal. Tudo pelo WhatsApp. Às vezes vem um print de tela em vez da foto do documento."

**4. Pedidos de reenvio:** "Peço para uns 3 de cada 10 clientes mandarem algo de novo. O RG plastificado é o pior: reflexo bem em cima do número."

**5. Devoluções do jurídico:** "Duas ou três por semana. Quase sempre CPF com dois números trocados ou nome da mãe abreviado."

**6. Software atual:** "A gente usa um sistema jurídico. Ele lê CNH por foto, mas RG antigo não, e comprovante também não. Eu digito tudo e copio para a procuração."

**7. Guarda dos documentos:** "Fica no WhatsApp do celular do escritório e numa pasta da rede. Já teve cliente perguntando se o RG dele ia ficar 'rodando por aí'."

## E2 · Renata, coordenadora de atendimento, Escritório B

**1. Clientes por dia:** "De 10 a 15, mas o volume varia muito com o mês."

**2. Tempo de cadastro:** "Medimos: a média é 22 minutos de trabalho por cliente, sem contar a espera pelos documentos."

**3. Documentos e canal:** "Um chatbot pede os documentos no WhatsApp e salva os arquivos. Depois alguém da equipe abre um por um e digita."

**4. Pedidos de reenvio:** "Um em cada quatro clientes. O chatbot aceita qualquer arquivo, até foto desfocada."

**5. Devoluções do jurídico:** "Poucas, umas duas por semana, porque eu confiro tudo antes. Mas a conferência é justamente o que toma tempo."

**6. Software atual:** "O chatbot coleta, mas não lê nada. Eu queria que ele já dissesse que a foto não serve na hora que o cliente manda."

**7. Guarda dos documentos:** "No servidor do chatbot e no nosso sistema. Nunca pensamos muito em por quanto tempo."

## E3 · Dra. Helena, advogada sócia, Escritório C

**1. Clientes por dia:** "Quatro, cinco, num dia bom."

**2. Tempo de cadastro:** "Eu mesma faço, junto com a primeira conversa. Leva uns 10 minutos e nunca foi problema."

**3. Documentos e canal:** "O cliente traz os documentos aqui, em papel. Eu tiro cópia."

**4. Pedidos de reenvio:** "Raramente. Como ele está na minha frente, se falta algo eu peço na hora."

**5. Devoluções do jurídico:** "Não se aplica, sou eu que faço tudo."

**6. Software atual:** "Uma planilha e o sistema do tribunal. Não sinto falta de ferramenta para cadastro."

**7. Guarda dos documentos:** "Pasta física e digitalização no computador."

## E4 · Diego, assistente de cadastro, Escritório D

**1. Clientes por dia:** "Mais de 50. São seis pessoas só no cadastro."

**2. Tempo de cadastro:** "A meta é 12 minutos por cliente, e a gente é cobrado por ela. Quando dá problema de documento, estoura fácil."

**3. Documentos e canal:** "WhatsApp e e-mail. Muita CNH digital em PDF, que o cliente baixa do aplicativo. E comprovante de residência no nome da mãe ou do marido, o que gera uma declaração extra."

**4. Pedidos de reenvio:** "Uns 40%. E cada reenvio pode atrasar o cadastro em um dia, porque o cliente demora a responder."

**5. Devoluções do jurídico:** "Umas cinco por semana. Já aconteceu de um CPF errado ir parar na petição e ter que emendar."

**6. Software atual:** "O sistema lê a CNH, mas lê uma por vez, e eu ainda confiro campo a campo. Não confio cem por cento."

**7. Guarda dos documentos:** "No sistema jurídico. A política de LGPD do escritório diz cinco anos depois do fim do processo."

## E5 · Lucas, assistente jurídico, Escritório E

**1. Clientes por dia:** "Entre 8 e 12."

**2. Tempo de cadastro:** "Uns 20 minutos, porque eu também separo as provas por tipo para a advogada."

**3. Documentos e canal:** "Metade por WhatsApp, metade por e-mail, tudo misturado: o cliente manda RG, fatura e boleto num PDF só, escaneado pelo celular."

**4. Pedidos de reenvio:** "Uns 2 em cada 10."

**5. Devoluções do jurídico:** "Uma por semana, mais ou menos. Normalmente valor ou data da fatura digitados errado."

**6. Software atual:** "Nada lê documento aqui. Eu digito e renomeio cada arquivo."

**7. Guarda dos documentos:** "Numa pasta compartilhada na nuvem. Um cliente já pediu para apagarmos tudo dele depois que o processo acabou, e foi trabalhoso achar os arquivos."

---

## Síntese

### Padrões

| Padrão | Quantos citaram | Entrevistas |
|---|---|---|
| WhatsApp é o canal principal de documentos | 4 de 5 | E1, E2, E4, E5 |
| Pedir reenvio é frequente (20% a 40% dos clientes) | 4 de 5 | E1, E2, E4, E5 |
| O reenvio atrasa o cadastro em dias, não em minutos | 2 de 5 | E1, E4 |
| Erros que voltam do jurídico: CPF, nome da mãe, valores e datas | 4 de 5 | E1, E2, E4, E5 |
| O cadastro por foto atual cobre só a CNH, um documento por vez | 2 de 5 | E1, E4 |
| A conferência manual consome o tempo que a ferramenta deveria poupar | 2 de 5 | E2, E4 |
| Documentos misturados num único arquivo ou mensagem | 2 de 5 | E1, E5 |
| Escritório pequeno, com cliente presencial, não sente o problema | 1 de 5 | E3 |

### O que a simulação ilustra sobre as hipóteses

As hipóteses **continuam 🧪**. A tabela mostra como cada uma seria avaliada se as entrevistas fossem reais.

| Hipótese | O que as entrevistas simuladas mostram | Se fosse real |
|---|---|---|
| H1 · O cadastro consome tempo relevante | 15 a 22 min por cliente, com meta cobrada em E4 | Sustentaria, só para alto volume (E3 diverge) |
| O2 · Documentos ilegíveis exigem novo pedido | Reenvio em 20% a 40% dos clientes, com atraso de dias | Confirmaria O2 como a oportunidade mais cara, acima de O3 |
| O3 · Documentos misturados | Citado por 2 de 5 | Relevante, mas secundário |
| H4 · Confiança no resultado | E4 confere campo a campo por não confiar | Reforçaria a revisão orientada por confiança (RF-14) |
| O5 · Desconfiança do cliente | Citada por 1 de 5 (E1) | Fraca como motivação; LGPD aparece mais como dor do escritório (E5) |
| Segmento | E3 não tem o problema | Confirmaria o recorte em alto volume |

### Achados novos

Pontos que **não estavam** em nenhum documento do projeto e que viram candidatos para a priorização da [Etapa 6](../../README.md#roteiro):

| # | Achado | De onde | Possível consequência |
|---|---|---|---|
| N1 | **Comprovante em nome de outra pessoa** (mãe, cônjuge) | E4 | O sistema extrai o titular do comprovante e sinaliza quando ele difere do cliente |
| N2 | **Vários documentos num único PDF** | E5 | Separar páginas antes de classificar |
| N3 | **Print de tela** no lugar da foto do documento | E1 | Tratar como imagem comum e verificar resolução |
| N4 | **O cadastro dura dias**, esperando o último documento | E1, E4 | A sessão de captura precisa poder ser retomada; o link não pode valer só para uma vez |
| N5 | **Exclusão a pedido do titular** é trabalhosa hoje | E5 | Reforça a retenção do [ADR 0008](../decisoes/0008-armazenamento-em-producao.md) |

### Limites

- **Nada aqui é evidência.** Os padrões refletem as escolhas de quem escreveu as simulações, e não o mercado.
- **Viés de confirmação:** simulações escritas por quem desenhou o produto tendem a confirmar o produto. A entrevista E3 e as divergências foram incluídas para reduzir esse efeito, mas não o eliminam.
- **Antes de qualquer uso real**, as sete perguntas precisam ser feitas a profissionais de verdade, e a síntese refeita.
