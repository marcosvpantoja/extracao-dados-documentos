# Personas

**Versão:** 3.0 · 10/11/2026 · segmento: **escritórios de direito do consumidor com alto volume de clientes**
**Atributos centrais do produto:** **ágil** e **preciso**

Personas construídas a partir da [pesquisa da Etapa 3](etapas/03-validacao-do-problema.md). Cada afirmação indica sua origem:

- **[A1]–[A5], [B1]–[B4]**: achado da pesquisa pública (evidência indireta)
- **🧪**: hipótese ainda não validada, a testar nas entrevistas

---

## Persona primária: Juliana, assistente de cadastro em escritório de advocacia de massa

> "Atendo dezenas de clientes por dia. Cada um manda RG, conta de luz e a fatura que está contestando, tudo por WhatsApp. Se eu erro um CPF na procuração, o erro vai para o processo."

### Perfil

| | |
|---|---|
| Função | Assistente de atendimento e cadastro, no primeiro contato com o cliente 🧪 |
| Escritório | Advocacia de massa em direito do consumidor: grande volume de casos parecidos **[B2]** |
| Atividades | Recebe documentos, cadastra o cliente, organiza as provas e prepara procuração e contrato de honorários para a equipe jurídica **[B1] [B4]** 🧪 |
| Ferramentas | Software de gestão jurídica (ex.: Projuris, EasyJur) **[B4]**; WhatsApp para receber documentos **[B2]** 🧪 |
| Como é avaliada | Tempo de cadastro e ausência de erros que voltem da equipe jurídica **[B2]** |

### O que cada cadastro exige [B1]

| Documento | Para quê | Tipo no sistema |
|---|---|---|
| RG e CPF, ou CNH | Qualificação da parte e procuração | RG antigo, CIN, CNH |
| Comprovante de residência | Endereço da parte (prática comum, embora a exigência seja controversa) | Fatura de serviço |
| Provas do caso: nota fiscal da compra, fatura contestada, boleto cobrado | Fundamentar o pedido | NF-e, fatura de serviço, boleto |

Os seis tipos do escopo aparecem num **único atendimento**, misturados, e o sistema precisa separá-los sozinho.

### Jobs to be done

> **Quando** um novo cliente envia seus documentos, **quero** ter os dados de identificação e das provas cadastrados corretamente em poucos minutos, **para** liberar o caso para a equipe jurídica e atender o próximo cliente.

### Dores

| Dor | Origem |
|---|---|
| Volume alto e cadastro como gargalo: o tempo de cadastro é cobrado como indicador | **[B2]** |
| Em escala, um erro se repete dezenas de vezes; um CPF errado chega à procuração e ao processo | **[B2]** |
| Documentos chegam misturados e em qualidade variável pelo WhatsApp, exigindo novos pedidos | 🧪 |
| Digitação dos dados de identificação e das provas (valores, datas, empresa cobradora) | 🧪 |
| O cadastro por foto da ferramenta atual cobre um documento por vez, sem as provas | **[B4]** 🧪 |
| Cópias de documentos pessoais ficam espalhadas em celulares e conversas | 🧪 |

### O que ela já usa ou tentou

| Alternativa | Limite | Origem |
|---|---|---|
| Cadastro por foto da CNH no software jurídico | Um tipo de documento; não cobre RG antigo, comprovante nem provas | **[B4]** 🧪 |
| Chatbots de triagem que coletam documentos | Coletam o arquivo, mas não extraem nem conferem os dados | **[B2]** 🧪 |
| Plataformas de verificação de identidade | Voltadas a antifraude, caras e armazenam documentos | **[A4]** |

### Critérios de sucesso: ágil e preciso

| Atributo | Para ela significa | Métrica |
|---|---|---|
| **Ágil** | Cadastro completo do cliente numa única interação, sem digitar | Tempo de cadastro por cliente; recapturas por documento |
| **Preciso** | Nenhum dado errado chega à equipe jurídica | Acurácia por campo; % de campos confirmados sem correção; erros devolvidos pela equipe jurídica |

---

## Persona secundária: Roberto, cliente consumidor

> "Me cobraram uma fatura que eu não devia. O escritório pediu foto do RG, da conta de luz e da fatura. Mandei pelo WhatsApp, mas não gosto de deixar meu documento por aí."

| | |
|---|---|
| Papel | Consumidor que contrata o escritório para uma ação |
| Interação com o produto | Fotografa os próprios documentos com o celular, normalmente **à distância** 🧪 |
| Necessidade | Enviar tudo de uma vez, rápido, sem instalar app e sem ter de reenviar 🧪 |
| Preocupação | Para onde vão os documentos e quem tem acesso 🧪 |
| Contexto | Pouca familiaridade com tecnologia é comum; precisa de instruções simples 🧪 |

**Requisitos que ele revela:** a página de captura precisa funcionar sozinha, com linguagem simples, para quem nunca usou o sistema; o link pode chegar pelo WhatsApp, e não só por QR code na tela.

---

## Persona terciária: Dra. Paula, advogada responsável

| | |
|---|---|
| Papel | Recebe o caso cadastrado e redige a petição |
| Necessidade | Dados de qualificação corretos e provas organizadas, com os arquivos disponíveis para anexar ao processo **[B1]** |
| Impacto do produto | Menos devoluções de cadastro e menos retrabalho na petição 🧪 |

**Requisito que ela revela:** o escritório **precisa ficar com os arquivos**. Em produção, o sistema guarda os documentos cifrados, com acesso controlado e pelo prazo que o escritório definir ([ADR 0008](decisoes/0008-armazenamento-em-producao.md)). No estudo de caso, para proteger quem testa, tudo é removido às 18h e o escritório baixa o que precisa ([ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md)).

---

## Anti-persona

**Analista de antifraude de banco ou fintech.** Precisa de biometria, prova de vida e guarda de documentos para auditoria; é atendido pelas plataformas de verificação de identidade **[A4]**.

---

## Perguntas para as entrevistas

Aplicadas em [cinco entrevistas simuladas](pesquisa/entrevistas-simuladas.md) (🧪 fictícias), por causa do prazo do estudo.

1. Quantos clientes novos o escritório cadastra por dia?
2. Quanto tempo leva um cadastro completo, do primeiro contato à liberação para a equipe jurídica?
3. Quais documentos chegam em cada caso, e por qual canal?
4. Quantas vezes por dia é preciso pedir que o cliente reenvie um documento?
5. Com que frequência a equipe jurídica devolve um cadastro por erro? Quais erros são mais comuns?
6. O que o software jurídico atual faz no cadastro? O que falta?
7. Onde os documentos ficam guardados hoje? Algum cliente já questionou isso?

---

## Histórico das personas

| Versão | Persona | Por que mudou |
|---|---|---|
| 1.0 | Assistente contábil que digita documentos misturados | NF-e e boletos já chegam por canais eletrônicos (XML, DDA) **[A1] [A2]** |
| 2.0 | Assistente contábil focada no cadastro de clientes | Cadastro acontece uma vez por cliente: frequência insuficiente **[A3]** |
| 3.0 | Assistente de cadastro em advocacia de massa (consumidor) | Volume alto, tempo de cadastro medido e os seis tipos de documento no mesmo atendimento **[B1] [B2]** |
