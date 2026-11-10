# Etapa 1 — Documentos de exemplo e campos-alvo

**Período:** a partir de 10/11/2026
**Status:** 🟡 Em andamento

## Objetivo

Montar o conjunto de documentos que guia o desenvolvimento e a avaliação do sistema, e fechar a lista de campos extraídos de cada tipo. Sem esse conjunto não há como medir acurácia nem comparar abordagens técnicas.

## Conjunto de teste

O conjunto combina **documentos reais**, que medem o desempenho em condições verdadeiras, e **documentos fictícios**, que podem ser publicados e reproduzidos.

| Tipo | Real (local, não versionado) | Fictício (versionado) | Canal de entrada |
|---|---|---|---|
| NF-e | 1 DANFE em PDF | A gerar | Upload no computador |
| CNH | 1 CNH física | A gerar | Câmera do celular (cross-device) |
| RG | 1 RG | A gerar (RG antigo e CIN) | Câmera do celular (cross-device) |
| Boleto | — | A gerar | Upload no computador |

### Dois canais de entrada

A escolha do canal segue a forma como cada documento chega no mundo real:

- **NF-e e boleto → upload de PDF.** Normalmente chegam por e-mail já em formato digital. O PDF pode conter texto nativo, o que dispensa OCR.
- **RG e CNH → captura pelo celular.** São documentos físicos. O fluxo cross-device é testado exatamente com eles, porque é onde a qualidade da foto (luz, reflexo, ângulo, foco) mais afeta o resultado.

Isso ajusta o requisito de captura da Etapa 0: o celular é o canal principal para documentos físicos, e o upload é o canal principal para documentos digitais. A classificação automática vale para os dois canais.

## Privacidade dos documentos reais

| Regra | Como é garantida |
|---|---|
| Documentos reais nunca vão para o repositório | `data/privado/` ignorado pelo git, e PDFs e imagens bloqueados fora de `data/exemplos/` |
| Gabaritos de documentos reais também são privados | Ficam em `data/privado/gabaritos/`, porque repetem os dados pessoais |
| Prints e exemplos na documentação usam só documentos fictícios | Revisão antes de cada commit |
| Envio de documentos reais a serviços externos (APIs de OCR ou IA) | Decisão registrada em ADR na Etapa 2, considerando LGPD e retenção de dados pelo provedor |

## Gabarito (ground truth)

Cada documento do conjunto tem um arquivo JSON com o valor correto de cada campo. A acurácia é calculada comparando a extração do sistema com esse gabarito, campo a campo.

```json
{
  "arquivo": "cnh/cnh-01.jpg",
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

## Campos-alvo

Versão inicial definida na Etapa 0, a ser confirmada contra os documentos reais.

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

Alguns campos têm regra matemática ou formato fixo. Isso permite ao sistema saber se errou, mesmo sem gabarito, e alimenta o indicador de confiança.

| Campo | Validação |
|---|---|
| CPF / CNPJ | Dígitos verificadores |
| Chave de acesso da NF-e | 44 dígitos com dígito verificador (módulo 11) |
| Linha digitável do boleto | Dígitos verificadores por bloco e dígito geral |
| Datas | Formato válido e coerência (ex.: validade da CNH posterior à emissão) |

## Limitação conhecida

Com um documento real por tipo, a amostra mostra **se o sistema funciona**, mas não permite afirmar uma taxa de acurácia com confiança estatística. Os documentos fictícios ampliam a cobertura de layouts, e as métricas serão reportadas sempre informando o tamanho da amostra.

## Entregáveis da etapa

- [ ] Documentos reais em `data/privado/`, com gabaritos
- [ ] Documentos fictícios de NF-e, boleto, CNH, RG antigo e CIN em `data/exemplos/`, com gabaritos
- [ ] Lista final de campos por tipo
- [ ] Funções de validação (CPF, CNPJ, chave NF-e, linha digitável) especificadas

## Próxima etapa

Etapa 2 — Arquitetura e escolha de stack: definir como funcionam o pareamento por QR code, o processamento em tempo real e o motor de leitura e extração, com os trade-offs registrados em ADRs.
