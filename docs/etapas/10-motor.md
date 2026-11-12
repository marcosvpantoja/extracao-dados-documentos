# Etapa 10: Motor de extração

**Status:** 🟡 Em andamento · 11/11/2026
**Papéis:** Dev, Arquiteto
**Decisões:** [ADR 0002](../decisoes/0002-motor-de-leitura-e-extracao.md) (regras primeiro), [ADR 0006](../decisoes/0006-ocr-apple-vision.md) (Apple Vision)

## Como o motor funciona

1. **Leitura de texto (OCR):** o Apple Vision lê a foto em português ([`src/extracao/ocr.py`](../../src/extracao/ocr.py)). A imagem é girada nas quatro orientações, e fica a leitura com mais texto e mais confiança.
2. **Classificação por regras:** títulos ("CARTEIRA NACIONAL DE HABILITAÇÃO", "IDENTIDADE NACIONAL", "DANFE"), MRZ, linha digitável e palavras como "FATURA" somam pontos para cada tipo ([`src/extracao/pipeline.py`](../../src/extracao/pipeline.py)).
3. **Extração por regras:** cada campo do catálogo da [Etapa 1](01-documentos-e-campos.md) é procurado pelo rótulo ("NOME", "FILIAÇÃO") e pelo formato (data, CPF, sigla do órgão).
4. **Validação:** CPF, CNPJ, chave da NF-e, linha digitável e MRZ são conferidos por dígito verificador ([`src/extracao/validacoes.py`](../../src/extracao/validacoes.py)). O nome da CNH e da CIN é conferido contra a MRZ.
5. **Pedido de nova foto:** se faltar um campo essencial ao cadastro (por exemplo, o CPF ou o nome), o motor responde "nova foto" com o motivo, e o celular pede outra na hora (RF-31).

**IA de texto:** ainda não instalada, por decisão de 11/11/2026. As regras vêm primeiro, como previa o ADR 0002, e a IA entra se as regras não derem conta nas fotos reais.

## Problemas encontrados e regras ajustadas

| Problema | Causa | Ajuste |
|---|---|---|
| Chave da NF-e não encontrada | Impressa em duas linhas | Junta as linhas de números abaixo de "CHAVE DE ACESSO" |
| Fatura classificada como boleto | A fatura também tem "BENEFICIÁRIO" | "FATURA" e "DEMONSTRATIVO" pesam mais |
| CIN classificada como RG | Rótulo "CPF / REGISTRO GERAL" | "IDENTIDADE NACIONAL" e MRZ pesam mais |
| Nome não encontrado | A marca d'água embaralha o rótulo "NOME" | O nome é localizado e conferido pela MRZ; prenomes perdidos pelo OCR são completados por ela |
| Filiação trocada | Linha do pai ilegível "empurrava" a mãe para o lugar dele | Cada linha ocupa sua posição; ilegível fica em branco |
| RG antigo | Rótulos ficam abaixo dos valores, e uma face vem girada | Regras próprias: filiação pela barra "PAI /" e vizinhança, rótulo "acima" ou "à esquerda" |
| Textos impressos lidos como nomes | "POLEGAR DIREITO", "ESTADO FICTÍCIO DE PR", pedaços da marca d'água | Lista de palavras que não são nomes |

## Linha de base no conjunto fictício (11/11/2026)

18 documentos: 12 PDFs digitais e 6 cartões em versão de impressão, renderizados pelo [`scripts/avaliar.py`](../../scripts/avaliar.py).

| Medida | Resultado |
|---|---|
| Classificação correta | 18 de 18 |
| Campos extraídos corretos | 109 de 109 (100%) |
| Documentos com todos os campos essenciais | 18 de 18 (nenhum pedido de nova foto) |
| Tempo por documento (OCR + regras) | 0,24 s em média, 0,46 s no máximo |

### Por que esse número não vale como resultado

- **Vício de dados:** as regras foram ajustadas olhando esses mesmos 18 documentos. É o risco descrito na [Etapa 1](01-documentos-e-campos.md#limitações): o número mostra que o motor funciona nos layouts que conhece, não que generaliza.
- **Imagens perfeitas:** são PDFs renderizados, sem foto, luz, reflexo ou ângulo. As fotos do celular são o teste de verdade.
- **Cobertura parcial:** o motor extrai os campos essenciais e parte do catálogo. Campos como local de emissão, categoria da CNH em todos os casos e os itens da NF-e ainda não são extraídos.

O número que vale para as metas dos resultados-chave sai das **fotos dos documentos fictícios impressos** (documentos que as regras não viram como foto) e, depois, das sessões com testers ([Etapa 5](05-metricas.md#como-as-metas-serão-definidas)).

## Teste de generalização: layouts novos (11/11/2026)

**Origem:** no teste no celular, um RG de modelo novo não foi reconhecido. Para medir o problema sem vício, foram gerados 7 documentos fictícios com **layouts que as regras nunca viram** ([`scripts/gerar_variantes.py`](../../scripts/gerar_variantes.py)): 3 RG antigos (rótulos ao lado do valor, face única com sigla da UF, ordem invertida), 2 CIN (rótulos bilíngues e formato de app) e 2 CNH (modelo antigo sem MRZ e formato de app). A medição foi feita **antes** de qualquer ajuste nas regras.

| Medida | Layouts conhecidos | **Layouts novos** |
|---|---|---|
| Classificação correta | 18 de 18 | **6 de 14** |
| Campos extraídos corretos | 100% | **82%** |
| Cobertura: campos esperados encontrados e certos | — | **27%** (28 de 105) |

**Conclusão:** as regras atuais **não generalizam**. Elas funcionam nos layouts para os quais foram escritas e falham em layouts diferentes, inclusive nas versões de impressão, em que o texto fica pequeno. Esta é a medida honesta do motor por regras, e confirma o risco de vício registrado na Etapa 1.

## Regras genéricas e IA de texto (11/11/2026)

**Decisão:** tornar as regras genéricas e usar a IA de texto local (Ollama, modelo Qwen 2.5 7B, ~4,7 GB, só no Mac) para o que as regras não acharem, como o ADR 0002 previa.

**Regras genéricas** ([`src/extracao/identidade.py`](../../src/extracao/identidade.py)): cada campo tem rótulos sinônimos, inclusive bilíngues ("Nome / Name", "Filho(a) de", "Pai:"), e o valor é procurado na própria linha, ao lado, abaixo ou acima do rótulo. A classificação passou a usar sinais mais robustos (por exemplo, o RG antigo não tem validade; a CIN tem).

**IA de texto** ([`src/extracao/ia.py`](../../src/extracao/ia.py)): recebe o texto do OCR, não a imagem, e só preenche os campos em branco. Três proteções contra dado inventado:
1. o valor precisa **aparecer no texto do OCR**;
2. passa pelas **mesmas validações de formato** das regras (CPF com dígito verificador, número de registro com 9 a 11 dígitos, RG que não seja um CPF);
3. não pode repetir um nome já usado em outro campo de pessoa.

Na tela do escritório, o campo que veio da IA aparece marcado **"IA · conferir"**.

| Conjunto | Tipo certo | Campos extraídos certos | Cobertura |
|---|---|---|---|
| Layouts novos, regras v1 | 6 de 14 | 82% | 27% |
| Layouts novos, regras genéricas | 12 de 14 | 95% | 72% |
| Layouts novos, regras genéricas + IA | 13 de 14 | 93% | 82% |
| Todos os 32 documentos, regras genéricas + IA | 31 de 32 | 94% | 87% |

**Custo:** o tempo médio passa de 0,6 s para cerca de 2,6 s por documento, com picos de 8 s quando a IA entra. Cabe nos 30 s de espera do celular (RF-31).

**Limites que continuam:** as variantes também foram usadas para ajustar as regras genéricas, então deixaram de ser um conjunto "nunca visto". A medição de generalização daqui para frente depende de documentos novos: as fotos dos impressos e as sessões com testers.

## Detecção da posição da foto (11/11/2026)

**Origem:** no teste, uma foto chegou de cabeça para baixo e apareceu assim na revisão.

**Primeira tentativa, que falhou:** escolher a orientação em que o OCR lê mais texto. Não funciona, porque no modo preciso o Apple Vision lê até texto de cabeça para baixo, com resultado quase igual nas quatro posições.

**Solução:** no modo rápido, texto virado sai como letras sem sentido. O motor lê a foto nas quatro orientações no modo rápido e escolhe aquela com mais palavras e números de documento de verdade (rótulos como NOME e CPF, datas, CPF e CNPJ formatados). Nos testes, acertou **8 de 8** combinações (CNH e fatura, cada uma em 0°, 90°, 180° e 270°), com custo de cerca de 0,5 s a mais por foto.
