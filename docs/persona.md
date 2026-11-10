# Personas

**Versão:** 2.0 · 10/11/2026 · foco em **agilidade no cadastro de cliente**

Personas construídas a partir da [pesquisa da Etapa 3](etapas/03-validacao-do-problema.md). Cada afirmação indica sua origem:

- **[A1]–[A5]**: achado da pesquisa pública (evidência indireta)
- **🧪**: hipótese ainda não validada, a testar nas entrevistas

---

## Persona primária: Ana, assistente contábil

> "Abrir a empresa de um cliente novo começa sempre igual: pedir os documentos, esperar chegar pelo WhatsApp, descobrir que a foto está cortada, pedir de novo e digitar tudo."

### Perfil

| | |
|---|---|
| Função | Assistente contábil, responsável pela área societária e de cadastro em escritório de pequeno porte 🧪 |
| Atividades | Abertura de empresas, alterações contratuais, cadastro de clientes novos e trocas de contador 🧪 |
| Ferramentas | Sistema contábil; captura automática de XML de NF-e pela SEFAZ **[A1]**; DDA para boletos registrados **[A2]**; WhatsApp e e-mail para receber documentos de clientes 🧪 |
| Relação com tecnologia | Usa ferramentas especializadas no fiscal, mas o cadastro continua manual 🧪 |

### Contexto: o que o cadastro exige

Para abrir ou cadastrar uma empresa, o escritório coleta de **cada sócio** **[A3]**:

| Documento | Observação |
|---|---|
| Documento de identidade com foto (RG ou CNH dentro da validade) | RG estadual é o mais comum; CNH é aceita **[A3]** |
| CPF | Muitas vezes já consta no RG ou na CNH **[A3]** |
| Comprovante de residência | Conta de consumo recente, em geral até 90 dias **[A3]** |
| Comprovante do endereço comercial | Pode ser o residencial quando a empresa funciona em casa **[A3]** |

Contas de consumo (luz, água, internet, celular) **não chegam por DDA [A2]**, então o comprovante de residência só existe como PDF, papel ou foto.

### Jobs to be done

> **Quando** um cliente novo chega, **quero** coletar e transcrever os dados dos documentos dos sócios corretamente e de uma só vez, **para** dar entrada no processo sem idas e vindas e sem que cópias dos documentos fiquem espalhadas.

### Dores

| Dor | Origem |
|---|---|
| Documentos chegam por canais dispersos (WhatsApp, e-mail) e em qualidade variável, exigindo novo pedido | 🧪 |
| Digitação manual dos dados de cada sócio: nome, filiação, CPF, RG, naturalidade, endereço | 🧪 |
| Erros de digitação no cadastro geram retrabalho em órgãos de registro | 🧪 |
| Cópias de documentos pessoais ficam guardadas em conversas, caixas de e-mail e pastas, com exposição a vazamentos e às obrigações da LGPD | 🧪 |
| Toda a automação disponível no escritório cobre o fiscal (NF-e, boletos), não o cadastro | **[A1] [A2]** |

### O que ela já tentou

| Alternativa | Por que não resolve | Origem |
|---|---|---|
| Plataformas de verificação de identidade (Unico, CAF, idwall) | Voltadas a antifraude em empresas de médio e grande porte; custo e complexidade excessivos para poucos cadastros por mês; armazenam documentos | **[A4]** |
| Ferramentas de captura fiscal | Resolvem NF-e e boletos, não documentos pessoais nem contas de consumo | **[A1] [A2]** |
| Scanner ou foto pelo WhatsApp | Qualidade irregular, cópias guardadas no celular e na conversa | 🧪 |

### Critérios de sucesso para ela

- Cadastro de um sócio concluído numa única interação com o cliente 🧪
- Nenhum dado digitado à mão 🧪
- Poder dizer ao cliente: "seu documento não ficou guardado em lugar nenhum" 🧪

### Frequência

O cadastro acontece **uma vez por cliente**, na abertura ou na troca de contador **[A3]**. O volume por escritório é desconhecido e é a principal pergunta das entrevistas: ele define se a dor é frequente o bastante para justificar uma ferramenta 🧪.

---

## Persona secundária: Carlos, sócio do cliente

> "Me pediram RG, comprovante de residência e mais um monte de coisa. Mandei foto pelo WhatsApp, mas não gosto de ver meu documento circulando por aí."

| | |
|---|---|
| Papel | Sócio de uma pequena empresa que está abrindo CNPJ ou trocando de contador |
| Interação com o produto | Fotografa os próprios documentos com o celular, presencialmente ou à distância 🧪 |
| Necessidade | Entregar os documentos rápido, uma vez só, sem instalar nada 🧪 |
| Preocupação | Onde seus documentos ficam guardados e quem tem acesso 🧪 |

### Cenário que a persona secundária revela

Num **cadastro à distância**, Ana compartilha a tela numa chamada de vídeo ou envia o link do QR code. Carlos escaneia com **o próprio celular**, fotografa RG e conta de luz, e os dados aparecem direto na tela de Ana, sem passar por WhatsApp ou e-mail e sem deixar cópias. 🧪

Isso muda requisitos de UX: a página de captura precisa ser compreensível para quem **nunca usou o sistema** e pode estar sozinho, sem ninguém para orientar.

---

## Persona descartada (anti-persona)

**Analista de antifraude de banco ou fintech.** Precisa de biometria, prova de vida, consulta a bases oficiais e guarda de documentos para auditoria. É atendido pelas plataformas de verificação de identidade **[A4]**, e os requisitos dele contradizem a premissa de não armazenar nada.

---

## Perguntas para as entrevistas

1. Quantos cadastros de clientes novos o escritório faz por mês?
2. Como os documentos dos sócios chegam hoje, e quantas vezes é preciso pedir de novo?
3. Quanto tempo leva, do pedido dos documentos até os dados estarem no sistema?
4. Onde as cópias dos documentos ficam guardadas depois do cadastro?
5. Algum cliente já demonstrou preocupação com a guarda dos documentos?
6. O cadastro costuma ser presencial ou à distância?
7. Quais documentos ainda chegam sem canal eletrônico, além dos pessoais?
