# Etapa 3 — Validação do problema e benchmark

**Período:** a partir de 10/11/2026
**Status:** 🟡 Em andamento: evidência indireta coletada; entrevistas pendentes

## Objetivo

Testar com evidências as hipóteses de problema (H1) e de mercado (H5) e a persona definidas na [Etapa 0](00-concepcao.md), antes de construir.

## Método

| Nível | Fonte | Situação |
|---|---|---|
| Evidência indireta | Pesquisa pública: fóruns de contadores, conteúdos do setor, documentação de fornecedores | ✅ Realizada em 10/11/2026 |
| Evidência direta | Entrevistas com 3 a 5 profissionais de escritórios contábeis | ⚪ Pendente |

Limitação: a maior parte das fontes públicas é material de fornecedores e blogs, com interesse comercial. Elas indicam **práticas existentes**, mas não medem a intensidade da dor.

## Achados

### A1. NF-e recebida já é capturada automaticamente pelos escritórios

Escritórios contábeis usam ferramentas que consultam a SEFAZ periodicamente com o certificado digital do cliente e baixam o **XML** de toda NF-e emitida contra o CNPJ, entregando os dados diretamente ao sistema contábil, sem digitação ([Jettax](https://www.jettax.com.br/blog/baixar-xml-de-nf-e-automaticamente-guia-completo-para-escritorios-contabeis/), [Qive](https://qive.com.br/blog/consulta-nfe-automatica-lucro-escritorio-contabil), [Conta Azul](https://contaazul.com/contadores/buscador-de-notas-fiscais/), [Fiscal.io](https://www.fiscal.io/assets/docs/fiscal-io-monitor-dominio-xmls-direto-no-erp.pdf), [fórum Contábeis](https://www.contabeis.com.br/forum/tecnologia-contabil/260018/procuracao-eletronica-para-baixar-xml-dos-clientes/)).

**Implicação:** o XML é a fonte oficial e exata dos dados da NF-e. Ler o DANFE por OCR é uma solução inferior para o escritório contábil. O valor residual está em casos sem acesso ao XML (cliente sem certificado ou procuração, DANFE em papel entregue pelo cliente).

### A2. Boletos registrados chegam eletronicamente pelo DDA, mas contas de consumo não

O DDA (Débito Direto Autorizado) apresenta eletronicamente todos os boletos registrados contra um CNPJ, e é usado para controle de contas a pagar ([Agilize](https://agilize.com.br/blog/gestao-do-dia-a-dia/o-que-e-dda/), [Qive](https://qive.com.br/blog/boleto-dda), [Senior](https://documentacao.senior.com.br/gestaoempresarialerp/7.0.0/backoffice/financas/dda/debito-direto-autorizado.htm)). Porém, **contas de serviços públicos, internet, celular e tributos ficam fora do DDA** ([Tecnoblog](https://tecnoblog.net/responde/o-que-e-como-funciona-o-dda-debito-direto-autorizado/), [Idec](https://idec.org.br/consultas/dicas-e-direitos/entenda-mais-sobre-o-debito-direto-autorizado-dda)).

**Implicação:** boletos bancários têm canal eletrônico; **faturas de serviço não**. A fatura de serviço, incluída no escopo depois da análise dos documentos de referência, é um dos tipos com lacuna real.

### A3. O cadastro de cliente exige exatamente RG/CNH e comprovante de endereço

Listas de documentos para abertura de empresa convergem em: documento de identidade com foto dos sócios (RG ou CNH), CPF e **comprovante de residência**, geralmente uma conta de consumo recente ([Contabilizei](https://www.contabilizei.com.br/contabilidade-online/documentacao-para-abrir-empresa-saiba-o-que-e-solicitado-durante-o-processo/), [Agilize](https://agilize.com.br/artigos/?p=1276), [Conta Azul](https://contaazul.com/blog/quais-sao-os-documentos-necessarios-para-abrir-uma-empresa/)).

**Implicação:** confirma o momento de cadastro descrito no cenário. Mas é um evento **pouco frequente** por cliente: uma vez na abertura ou na troca de contador.

### A4. Captura de RG/CNH pelo celular com classificação e OCR já é um mercado maduro

Fornecedores de verificação de identidade oferecem captura guiada pelo celular, classificação automática (RG, CNH, CIN, passaporte) e OCR: [Unico](https://developer.unico.io/capabilities/document-capture-and-reuse), [CAF](https://docs.caf.io/caf-api/connect/transactions/services/document-ocr), [Legitimuz](https://legitimuz.com/en/legit-doc/), [idwall](https://www.mobiletime.com.br/?p=734853). São soluções em nuvem, voltadas a empresas de médio e grande porte, com foco em antifraude, e que armazenam documentos para auditoria e reutilização.

**Implicação:** a tecnologia não é diferencial. O espaço possível está em **privacidade por arquitetura** (nada armazenado, processamento local) e em **porte**: escritórios pequenos, para os quais uma plataforma de antifraude é cara e excessiva.

### A5. Não há dado público confiável sobre o tempo gasto com digitação nos escritórios

Estudos acadêmicos citam a automação de lançamentos e conciliações como ganho de eficiência ([RSD Journal](https://rsdjournal.org/rsd/article/download/49014/38538/503297), [Revista Esfera](https://multivix.edu.br/wp-content/uploads/2025/05/REVISTA_ESFERA_TECNOLOGIA_V10_N01_ARTIGO13.pdf)), mas sem medir o tempo gasto com digitação de documentos. Números genéricos sobre digitação manual circulam sem metodologia clara.

**Implicação:** a intensidade da dor só pode ser estimada por entrevistas.

## Situação das hipóteses

| # | Hipótese | Antes | Agora | Evidência |
|---|---|---|---|---|
| H1 | Triagem e digitação de documentos consome tempo significativo em escritórios pequenos | 🧪 | 🟠 **Enfraquecida para NF-e e boleto**; aberta para documentos pessoais e faturas | A1, A2, A5 |
| H5 | Existem lacunas nas soluções atuais para escritório pequeno | 🧪 | 🟡 **Parcialmente sustentada**: mercado maduro em tecnologia; lacuna possível em privacidade e porte | A4 |
| Persona | Assistente contábil que digita documentos misturados | 🧪 | 🟠 **Ajuste necessário**: o grosso do volume fiscal já é automatizado; o cadastro é pouco frequente | A1, A2, A3 |

## Pergunta em aberto para o produto

As evidências apontam que o valor do produto, para esta persona, **não está na NF-e nem no boleto**, que já têm canais eletrônicos, e sim em:

1. **Documentos pessoais no cadastro**, com a garantia de que nada fica armazenado.
2. **Documentos sem canal eletrônico:** faturas de serviço e contas de consumo, além de documentos fiscais entregues em papel.

## Decisão (10/11/2026)

**O escopo de tipos de documento é mantido.** Como estudo de caso, a cobertura de NF-e e boleto demonstra a capacidade de classificação e extração em documentos estruturados, com validações matemáticas ricas.

**A proposta de valor é reposicionada** de acordo com a evidência:

| | Antes | Depois |
|---|---|---|
| Valor principal | Eliminar a digitação de todos os documentos | Capturar com segurança documentos **sem canal eletrônico** (documentos pessoais no cadastro, faturas de consumo, documentos fiscais em papel), sem que nada fique armazenado |
| NF-e e boleto | Casos centrais | Casos de cobertura: úteis quando não há acesso ao XML ou ao DDA |
| Diferencial | Classificação automática | Privacidade por arquitetura e adequação a escritórios pequenos |

A persona permanece como hipótese de trabalho até as entrevistas.

## Segunda rodada: escritórios de advocacia de alto volume (10/11/2026)

A frequência baixa do cadastro no escritório contábil (A3) levou a investigar segmentos que **recebem dados de muitas pessoas todos os dias**.

### B1. Ações de consumidor usam exatamente os seis tipos do escopo

O núcleo documental de uma ação de consumidor é: procuração, documento de identificação (RG e CPF, ou CNH), comprovante de residência e **documentos que provam os fatos**, como contratos, **notas fiscais**, faturas e comprovantes ([Âmbito Jurídico](https://ambitojuridico.com.br/quais-documentos-o-advogado-precisa-para-entrar-com-acao/), [TJGO](https://docs.tjgo.jus.br/institucional/departamentos/atermacao/01_CONSUMIDOR.docx), [Idec](https://idec.org.br/download/file/fid/41117)). A exigência de comprovante de residência em nome próprio é controversa na jurisprudência, mas a prática é coletá-lo ([Migalhas](https://www.migalhas.com.br/depeso/424193/exigencia-indevida-de-documentos-pessoais-e-comprovantes-de-residencia)).

**Implicação:** NF-e, fatura de serviço e boleto deixam de ser casos de cobertura e passam a ser **provas centrais** (compra com defeito, cobrança indevida, serviço não prestado).

### B2. Advocacia de massa tem volume alto e mede tempo de cadastro

A advocacia de massa atua com grande volume de casos, sobretudo em consumidor, previdenciário e trabalhista. Guias de operação tratam a triagem com prazo curto e usam **tempo de cadastro** como indicador, e alertam que, em escala, um erro de triagem se repete dezenas de vezes ([Thomson Reuters: intake jurídico](https://www.thomsonreuters.com.br/pt/juridico/blog/intake-juridico.html), [Thomson Reuters: passivo de massa](https://www.thomsonreuters.com.br/pt/juridico/blog/gestao-passivo-massa-workflow.html), [Projuris](https://www.projuris.com.br/blog/o-que-vale-e-o-que-nao-vale-automatizar-no-seu-escritorio/)).

**Implicação:** confirma a frequência que faltava no cenário contábil e sustenta os dois atributos do produto: **ágil** (tempo de cadastro) e **preciso** (erro multiplicado em escala).

### B3. Ações trabalhistas exigem documentos adicionais

Além de identidade, CPF e comprovante de residência, entram CTPS, contracheques, TRCT e extrato do FGTS ([TRT-3](https://portal.trt3.jus.br/internet/servicos/atermacao-virtual/%40%40trt3-atermacao-info), [TRT-11](https://portal.trt11.jus.br/index.php/sociedades/atermacao/formulario-de-atermacao-rr/instrucoes-para-o-atendimento), [Âmbito Jurídico](https://ambitojuridico.com.br/documentos-necessarios-para-entrar-com-processo-trabalhista/)).

**Implicação:** o trabalhista é um segmento adjacente que exige **novos tipos de documento**. Fica para depois do MVP.

### B4. Softwares jurídicos já oferecem cadastro por foto da CNH

O Projuris ADV lista cadastro via foto da CNH, geração de procuração e coleta de documentos ([Projuris](https://projuris.com.br/adv)); o EasyJur anuncia automação da entrada de dados na captação ([EasyJur](https://easyjur.com/easyjur-os-para-administradores-juridicos/)). Emissão automática de procurações e contratos de honorários a partir do cadastro é tratada como requisito de escolha de sistema ([EasyJur](https://easyjur.com/blog/como-escolher-um-sistema-de-gestao-para-um-escritorio-de-advocacia)).

**Implicação:** o cadastro por foto já existe em suítes jurídicas, o que valida a necessidade. Este projeto **não se posiciona como concorrente**: é um estudo de caso e de pesquisa. As suítes servem de **referência de mercado** para comparar escolhas de produto: amplitude de documentos sem escolher o tipo, captura pelo próprio cliente à distância, precisão verificável e privacidade por arquitetura. A geração de documentos a partir dos dados extraídos é registrada como oportunidade.

### Tensões identificadas

| Tensão | Descrição | Encaminhamento |
|---|---|---|
| **Guarda de documentos** | O escritório **precisa** dos documentos para instruir a petição; "nada salvo" não pode significar que o escritório fica sem os arquivos | Redefinir a promessa: **o sistema não retém nada**; os arquivos e os dados são entregues ao escritório, que guarda no próprio ambiente, sob sua responsabilidade de controlador (LGPD) |
| **Referências de mercado** | Cadastro por foto já existe em suítes jurídicas | O projeto é estudo de caso, não concorrente; as suítes são usadas como referência de comparação |
| **Mudança de persona** | Terceira versão de persona | Registrada como evolução por evidência; a anterior tinha frequência insuficiente |

## Situação das hipóteses (atualizada)

| # | Hipótese | Situação | Evidência |
|---|---|---|---|
| H1 | Cadastro consome tempo relevante no segmento-alvo | 🟡 **Sustentada indiretamente** para advocacia de massa | B2 |
| H5 | Existem lacunas nas soluções atuais | 🟡 **Parcial**: há concorrência no cadastro por foto; lacunas em amplitude, captura remota, precisão e privacidade | A4, B4 |
| Persona | Assistente de cadastro em escritório de advocacia de massa | 🟡 **Sustentada indiretamente**; entrevistas pendentes | B1, B2 |

## Decisão de segmento (10/11/2026)

- **Segmento primário:** escritórios de **direito do consumidor** com alto volume de clientes.
- **Segmento adjacente (pós-MVP):** escritórios **trabalhistas**, que exigem CTPS, contracheques, TRCT e extrato do FGTS.
- **Segmento anterior (escritório contábil):** arquivado por frequência insuficiente de cadastros.
- **Atributos centrais do produto:** **ágil** e **preciso**.

## Próximos passos

- Entrevistas com 3 a 5 profissionais de escritórios de advocacia de consumidor (roteiro em [Personas](../persona.md#perguntas-para-as-entrevistas)).
- Análise de referência do fluxo de cadastro em suítes jurídicas (Projuris ADV, EasyJur), como comparação de escolhas de produto.
- Decisão de reposicionamento (persona e proposta de valor) com base nas entrevistas.
