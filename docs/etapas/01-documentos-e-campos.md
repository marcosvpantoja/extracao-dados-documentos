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

| Tipo | Formato | Canal de entrada |
|---|---|---|
| NF-e | DANFE em PDF | Upload no computador |
| Boleto | PDF | Upload no computador |
| CNH | Impressão fotografada em condições variadas (luz, ângulo, reflexo) | Câmera do celular (cross-device) |
| RG antigo e CIN | Impressão fotografada em condições variadas | Câmera do celular (cross-device) |

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

## Conjunto de avaliação: sessões com testers

Cada tester usa **os próprios documentos**, ao vivo, pelo mesmo fluxo do usuário final:

1. Abre o sistema no computador.
2. NF-e: faz upload do PDF. RG e CNH: escaneia o QR code e fotografa com o celular.
3. O sistema classifica e extrai em tempo real.
4. O tester marca cada campo exibido como **correto** ou **incorreto**.

O tester conhece os próprios dados, então ele é o gabarito. Não é preciso guardar o documento nem digitar os valores corretos.

### O que é registrado

| Registrado (localmente) | Nunca registrado |
|---|---|
| Tipo detectado e se a detecção estava certa | Imagem ou PDF do documento |
| Por campo: correto / incorreto / não extraído | Valor de qualquer campo |
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
| Nenhum dado é salvo em base de dados online | Documentos e dados extraídos existem só durante a sessão; os registros de avaliação ficam em arquivo local |
| Documentos reais nunca vão para o repositório | `data/privado/` ignorado pelo git, e PDFs e imagens bloqueados fora de `data/exemplos/` |
| Prints na documentação usam só documentos fictícios | Revisão antes de cada commit |
| Trânsito por serviços externos (APIs de OCR ou IA) | Não salvar não é o mesmo que não transmitir. Se a leitura usar um serviço na nuvem, a imagem trafega por ele. Decisão registrada em ADR na Etapa 2, considerando LGPD e política de retenção do provedor |

## Campos-alvo

| Nota Fiscal (NF-e) | Boleto | CNH | RG |
|---|---|---|---|
| Número e série | Linha digitável | Nome | Nome |
| Chave de acesso | Código de barras | CPF | Número do RG |
| Data de emissão | Banco emissor | Número de registro | Órgão emissor / UF |
| Emitente (razão social, CNPJ) | Beneficiário (nome, CNPJ/CPF) | Data de nascimento | Data de expedição |
| Destinatário (nome, CPF/CNPJ) | Pagador (nome, CPF/CNPJ) | Categoria | Data de nascimento |
| Valor total | Valor | Validade | Filiação |
| Itens (descrição, qtd., valor) | Data de vencimento | Primeira habilitação | CPF (quando presente) |

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
- **Avaliação não reproduzível:** cada sessão ao vivo tem condições diferentes. Comparações entre versões são feitas no conjunto de desenvolvimento; as sessões validam o resultado no mundo real.
- **Confirmação pelo tester:** depende da atenção do tester ao conferir cada campo.

## Entregáveis da etapa

- [ ] Documentos fictícios de NF-e, boleto, CNH, RG antigo e CIN em `data/exemplos/`, com gabaritos
- [ ] Fotos dos documentos fictícios impressos, em condições variadas
- [ ] Formato do registro de avaliação definido
- [ ] Lista final de campos por tipo
- [ ] Funções de validação (CPF, CNPJ, chave NF-e, linha digitável) especificadas

## Próxima etapa

Etapa 2 — Arquitetura e escolha de stack: definir como funcionam o pareamento por QR code, o processamento em tempo real e o motor de leitura e extração, com os trade-offs registrados em ADRs.
