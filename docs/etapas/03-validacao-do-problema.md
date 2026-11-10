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

## Próximos passos

- Roteiro de entrevistas focado em: frequência de cadastros, documentos que ainda chegam sem canal eletrônico, preocupação dos clientes com a guarda de documentos e ferramentas usadas hoje.
- Entrevistas com 3 a 5 profissionais.
- Decisão de reposicionamento (persona e proposta de valor) com base nas entrevistas.
