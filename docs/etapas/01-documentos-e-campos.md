# Etapa 1 — Documentos de exemplo e campos-alvo

**Período:** a partir de 10/11/2026
**Status:** 🟡 Em andamento

## Objetivo

Definir com quais documentos o sistema é desenvolvido e com quais ele é avaliado, e fechar a lista de campos extraídos de cada tipo.

## Princípio: separar desenvolvimento de avaliação

Se os mesmos documentos usados para ajustar o sistema forem usados para medi-lo, o resultado fica inflado: o sistema aprende aqueles arquivos, não o tipo de documento. Esse vício é conhecido como **vazamento de dados** (*data leakage*) e leva a **overfitting**.

Por isso o projeto usa dois conjuntos que nunca se misturam:

| | Conjunto de desenvolvimento | Conjunto de avaliação |
|---|---|---|
| **Documentos** | Fictícios | Reais, dos próprios testers |
| **Quem vê** | Equipe do projeto, livremente | Ninguém antes do teste |
| **Armazenamento** | Versionados em `data/exemplos/` | Não são armazenados |
| **Gabarito** | JSON escrito junto com o documento | O próprio tester confirma cada campo na tela |
| **Uso** | Construir, ajustar e comparar versões (testes de regressão) | Medir o desempenho em condições reais |

## Conjunto de desenvolvimento

Documentos fictícios, com dados inventados e formato válido, que podem ser publicados.

Qualquer tipo pode entrar pelos dois canais ([ADR 0003](../decisoes/0003-escopo-do-mvp.md)), então o conjunto cobre as duas formas:

| Tipo | Arquivo para importação | Foto para cross-device |
|---|---|---|
| CNH | CNH-e em PDF | Impressão fotografada em condições variadas (luz, ângulo, reflexo) |
| RG antigo e CIN | PDF escaneado | Impressão fotografada em condições variadas |
| Fatura de serviço | PDF | Impressão fotografada |
| NF-e | DANFE em PDF | Impressão fotografada |
| Boleto | PDF | Impressão fotografada |

As fotos ficam salvas e são sempre as mesmas. Isso permite rodar duas versões do sistema sobre a mesma entrada e saber se uma mudança melhorou ou piorou a extração.

### Gabarito (ground truth)

Cada documento fictício tem um JSON com o valor correto de cada campo:

```json
{
  "arquivo": "cnh/cnh-ficticia-01.jpg",
  "tipo": "CNH",
  "campos": {
    "nome": "FULANO DE TAL",
    "cpf": "000.000.000-00",
    "numero_registro": "00000000000",
    "data_nascimento": "1990-01-01",
    "categoria": "AB",
    "validade": "2030-01-01",
    "primeira_habilitacao": "2010-01-01"
  }
}
```

### Como o conjunto foi gerado

`scripts/gerar_exemplos.py` cria dois exemplares de cada tipo (semente fixa, reproduzível):

| Tipo | Arquivo de importação | Reproduz do documento real | Versão de impressão |
|---|---|---|---|
| CNH | PDF A4 com a carteira **como imagem** | Dados só legíveis por OCR; MRZ com dígitos válidos | Frente e verso em tamanho de cartão |
| RG antigo | PDF de escaneamento, **frente e verso girados 90°**, leve desfoque | Rotação, duas faces na mesma página, sem texto | Frente e verso em tamanho de cartão |
| CIN | PDF com o cartão como imagem | CPF como número de registro; MRZ | Frente e verso em tamanho de cartão |
| Fatura | PDF com texto nativo | Layout de demonstrativo; em aberto traz linha digitável | O próprio PDF |
| NF-e | DANFE com texto nativo | Blocos do layout padrão; chave de acesso válida | O próprio PDF |
| Boleto | PDF com texto nativo | Linha digitável e código de barras I2of5 coerentes com valor e vencimento | O próprio PDF |

Todos levam a marca d'água "DOCUMENTO FICTÍCIO · SEM VALOR LEGAL". Nenhum brasão, logotipo oficial, foto real ou elemento de segurança é reproduzido; o rosto é uma silhueta genérica.

## Conjunto de avaliação: sessões com testers

Cada tester usa **os próprios documentos**, ao vivo, pelo mesmo fluxo do usuário final. Como são dados pessoais de terceiros, valem três condições:

- **O tester é o titular do documento e está presente.** Ninguém testa com documento de outra pessoa.
- **Consentimento antes da sessão:** o tester é informado do que é processado, de que o facilitador verá os documentos e os dados na tela, de que tudo é removido às 18h do mesmo dia ([ADR 0007](../decisoes/0007-retencao-temporaria-e-purga-diaria.md)) e de que só o resultado anônimo por campo é registrado.
- **Nenhum documento de tester é enviado para fora dos dois aparelhos**, inclusive para assistentes de IA usados no desenvolvimento.

Papéis na sessão:

| Pessoa | Papel em produção | O que faz |
|---|---|---|
| **Tester** | Roberto, o cliente | Captura os próprios documentos pelo celular e, no fim, confere os dados |
| **Facilitador** (autor do estudo) | Juliana, a assistente | Cria e envia o link, importa arquivos e revisa os campos |

O foco principal de observação é **o tester capturando os documentos**: a experiência do cliente na ponta final.

Fluxo da sessão:

1. O facilitador abre o sistema no computador e envia o link de captura ao tester.
2. RG, CNH e CIN: o tester fotografa pelo celular. NF-e, fatura e boleto em PDF: o facilitador importa o arquivo.
3. O sistema classifica e extrai os dados.
4. **Revisão:** o facilitador confirma ou corrige cada campo, como a Juliana faria.
5. **Conferência:** o tester vê os dados já confirmados e marca o que estiver errado. É o papel do jurídico que devolve um cadastro ([Etapa 5](05-metricas.md#3-métricas-no-estudo-de-caso)).

Documentos pessoais também existem em versão digital (CNH-e, identidade digital em PDF). Por isso RG e CNH são avaliados nos dois canais: **foto do documento físico** pelo celular e **PDF digital** por upload.

O tester conhece os próprios dados, então ele é o gabarito. Não é preciso guardar o documento nem digitar os valores corretos.

### O que é registrado

| Registrado (localmente) | Nunca registrado |
|---|---|
| Tipo detectado e se a detecção estava certa | Imagem ou PDF do documento |
| Por campo, na revisão: confirmado / corrigido / não extraído | Valor de qualquer campo |
| Por campo, na conferência: correto / apontado como errado | |
| Tempo até o primeiro campo e até o resultado completo | Nome ou identificação do tester |
| Canal de entrada e versão do sistema | |

Exemplo de registro:

```json
{ "sessao": "s-007", "versao": "0.3.0", "canal": "celular", "tipo_real": "CNH", "tipo_detectado": "CNH",
  "campos": { "nome": "correto", "cpf": "correto", "validade": "incorreto" },
  "ms_primeiro_campo": 1800, "ms_resultado_completo": 4200 }
```

## Privacidade

| Regra | Como é garantida |
|---|---|
| Retenção mínima na nuvem (estudo) | Dados e fotos salvos só cifrados e removidos às 18h de cada dia, nunca por 24h ([ADR 0007](../decisoes/0007-retencao-temporaria-e-purga-diaria.md)); registros de avaliação ficam em arquivo local, sem valores |
| Documentos reais nunca vão para o repositório | `data/privado/` ignorado pelo git, e PDFs e imagens bloqueados fora de `data/exemplos/` |
| Prints na documentação usam só documentos fictícios | Revisão antes de cada commit |
| Nome do arquivo não pode entregar a resposta | Arquivos reais são renomeados para nomes neutros na importação (ex.: `nfe-01.pdf`). O nome padrão de download de uma NF-e é a própria chave de acesso, o que vazaria um campo avaliado e dados do emitente |
| Nenhum documento real permanece após um teste | `scripts/limpar-e-verificar.sh`, executado ao fim de cada sessão (ver abaixo) |
| Trânsito por serviços externos (APIs de OCR ou IA) | Não salvar não é o mesmo que não transmitir. Se a leitura usar um serviço na nuvem, a imagem trafega por ele. Decisão registrada em ADR na Etapa 2, considerando LGPD e política de retenção do provedor |

### Limpeza e verificação após cada teste

Documentos reais importados para teste entram apenas em `data/privado/entrada/`. Ao fim de cada sessão, `scripts/limpar-e-verificar.sh`:

1. Apaga todos os arquivos de `data/privado/entrada/`.
2. Procura PDFs e imagens em qualquer outro lugar do projeto, identificando pelo conteúdo do arquivo e não só pela extensão.
3. Lista arquivos não rastreados ou ignorados que não sejam código ou documentação.
4. Verifica se algum PDF ou imagem fora de `data/exemplos/` e `docs/` já entrou no histórico do git.
5. Confere se os registros de avaliação contêm padrões de dado pessoal (CPF, imagem em base64).

A sessão só é considerada encerrada quando o script retorna **✅ CONFIRMADO**. Os documentos reais também não são abertos nem consultados durante o desenvolvimento, o que evita o vazamento de dados descrito acima.

## Achados dos documentos de referência

Três documentos reais foram analisados **apenas quanto a estrutura e campos** (nenhum valor registrado). Eles mudaram premissas do projeto:

| Documento | Formato real | Achado |
|---|---|---|
| CNH digital (CNH-e) | PDF A4 emitido pelo Senatran | O PDF tem texto nativo só no aviso de assinatura; **os dados da carteira estão dentro de uma imagem**. Mesmo sendo PDF, exige OCR. Traz uma **zona de leitura mecânica (MRZ)** com dígitos verificadores e um QR code assinado |
| RG antigo (modelo estadual) | Escaneamento do iPhone, só imagem, sem texto | **Frente e verso na mesma página, girados 90°**. Exige correção de rotação, separação das faces e OCR. Brilho e textura de segurança atrapalham a leitura |
| Fatura de serviço (internet) | PDF com texto nativo | **Não é NF-e nem boleto.** É um demonstrativo de cobrança. Revelou um tipo não previsto no escopo |

Consequências:

- **"Documento digital" não significa "texto pronto".** A classificação precisa olhar o conteúdo, não o formato do arquivo.
- **Correção de rotação e separação de frente e verso** entram no pré-processamento (Etapa 3).
- **MRZ da CNH** vira fonte de validação cruzada: nome, número do documento e datas lidos no corpo do documento podem ser conferidos contra a MRZ.
- **Fatura de serviço** entra no escopo como quinto tipo, por ser comum no mesmo cenário (contas de consumo e serviços chegam ao escritório junto com boletos e notas).

## Campos-alvo

Os modelos de extração procuram, em cada tipo, os campos abaixo. Campos marcados com * podem não existir em todos os modelos.

### CNH (física e CNH-e)

| Campo | Observação |
|---|---|
| Nome completo | |
| Data de nascimento | |
| Local e UF de nascimento (cidade) | |
| Filiação: nome do pai e nome da mãe | Dois nomes no mesmo bloco |
| Documento de identidade, órgão emissor e UF | |
| CPF | Validação por dígito verificador |
| Número de registro | |
| Categoria de habilitação | |
| Data da primeira habilitação | |
| Data de emissão | |
| Validade | |
| Nacionalidade | |
| Local de emissão (cidade, UF) | |
| Observações* | Ex.: exerce atividade remunerada |
| Validade por categoria* | Tabela do verso |
| MRZ* | Usada só para validação cruzada |

### RG antigo (modelos estaduais) e CIN

| Campo | Face | Observação |
|---|---|---|
| Nome completo | Frente | |
| Filiação: nome do pai e nome da mãe | Frente | Separados por barra ou em linhas distintas |
| Data de nascimento | Frente | |
| Naturalidade (cidade e UF) | Frente | |
| Órgão expedidor e UF | Frente | |
| Estado emissor | Frente | Cabeçalho ("Estado de ...") |
| Fator RH* | Frente | |
| Registro geral (número do RG) | Verso | |
| Via* | Verso | Ex.: 2ª via |
| Data de expedição | Verso | |
| CPF* | Verso | Validação por dígito verificador |
| Registro civil / matrícula da certidão* | Verso | |
| Outros números* | Verso | Título de eleitor, NIS/PIS, CNH, CNS, CTPS, certificado militar |

### Fatura de serviço

| Campo | Observação |
|---|---|
| Empresa emissora (beneficiário) e CNPJ | Validação por dígito verificador |
| Nome do cliente | |
| Número do cliente / contrato | |
| Número da fatura | |
| Período de referência | Ex.: mês/ano do serviço |
| Data de vencimento | |
| Valor total | |
| Endereço do cliente (cidade, UF, CEP)* | |
| Situação* | Ex.: paga, em aberto |
| Linha digitável* | Quando o boleto vem anexo |

### NF-e (DANFE)

| Campo | Observação |
|---|---|
| Número e série | |
| Chave de acesso | 44 dígitos, validação por módulo 11 |
| Data de emissão | |
| Emitente: razão social, CNPJ, cidade/UF | |
| Destinatário: nome, CPF/CNPJ, cidade/UF | |
| Natureza da operação | |
| Valor total da nota | |
| Itens: descrição, quantidade, valor | |

### Boleto

| Campo | Observação |
|---|---|
| Linha digitável | Validação por dígitos verificadores |
| Banco emissor | Três primeiros dígitos da linha digitável |
| Beneficiário: nome e CNPJ/CPF | |
| Pagador: nome e CPF/CNPJ | |
| Valor | Também contido na linha digitável |
| Data de vencimento | Também contida na linha digitável (fator de vencimento) |

### Campos com validação automática

Alguns campos têm regra matemática ou formato fixo. O sistema consegue detectar o próprio erro nesses campos, mesmo sem gabarito, e isso alimenta o indicador de confiança.

| Campo | Validação |
|---|---|
| CPF / CNPJ | Dígitos verificadores |
| Chave de acesso da NF-e | 44 dígitos com dígito verificador (módulo 11) |
| Linha digitável do boleto | Dígitos verificadores por bloco e dígito geral |
| Datas | Formato válido e coerência (ex.: validade da CNH posterior à emissão) |

## Limitações conhecidas

- **Amostra pequena:** com poucos testers, as sessões mostram se o sistema funciona em documentos reais, mas não sustentam uma taxa de acurácia com confiança estatística. Toda métrica é reportada com o tamanho da amostra.
- **Vazamento de layout:** os três documentos de referência foram usados para definir estrutura e campos. Avaliar o sistema **nesses mesmos documentos** tende a superestimar o resultado. A avaliação válida é feita com documentos de outros testers, e os resultados nos documentos de referência são reportados à parte.
- **Sem NF-e e boleto reais na referência:** esses dois tipos dependem de layouts públicos e do conjunto fictício até que um tester traga exemplares.
- **Avaliação não reproduzível:** cada sessão ao vivo tem condições diferentes. Comparações entre versões são feitas no conjunto de desenvolvimento; as sessões validam o resultado no mundo real.
- **Confirmação pelo tester:** depende da atenção do tester ao conferir cada campo.

## Entregáveis da etapa

- [x] Documentos fictícios dos seis tipos em `data/exemplos/`, com gabaritos (`scripts/gerar_exemplos.py`)
- [ ] Fotos dos documentos fictícios impressos (`*-impressao.pdf`), em condições variadas
- [ ] Formato do registro de avaliação definido
- [x] Lista final de campos por tipo
- [x] Funções de validação (CPF, CNPJ, chave NF-e, linha digitável, código de barras, MRZ) em `src/extracao/validacoes.py`, testadas contra os gabaritos

## Próxima etapa

[Etapa 2 — Arquitetura e requisitos](02-arquitetura-e-requisitos.md).
