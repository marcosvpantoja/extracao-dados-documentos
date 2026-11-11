# Fluxogramas do sistema

O mesmo sistema visto em oito arranjos diferentes: componentes, jornada, sequência de mensagens, pipeline de processamento, estados da sessão, revisão e aprendizado, garantias de privacidade e remoção diária.

Base: [requisitos](../requisitos.md) e [ADRs](../decisoes/README.md).

---

## 1. Componentes e fronteiras de confiança

Quem fala com quem, e onde o documento existe em texto aberto.

```mermaid
flowchart LR
  subgraph CEL["📱 Celular · navegador"]
    CAP["Página de captura"]
    CAM["Câmera"]
    CRIP1["Criptografia AES-GCM<br/>(Web Crypto)"]
    CAM --> CAP --> CRIP1
  end

  subgraph NUVEM["☁️ Nuvem · só dados cifrados"]
    VERCEL["Vercel<br/>hospeda as páginas"]
    SUPA["Supabase Realtime Broadcast<br/>canal efêmero por sessão"]
    STORE[("Supabase Storage + tabela<br/>só conteúdo cifrado<br/>removido às 18h")]
  end

  subgraph PC["💻 Computador do usuário"]
    subgraph NAV["Navegador"]
      REV["Tela de revisão"]
      QR["Gerador de QR + chave"]
      CRIP2["Descriptografia"]
      IMP["Importação de arquivo"]
    end
    subgraph MOTOR["Motor local · Python"]
      PRE["Pré-processamento"]
      OCR["Interface de OCR<br/>Apple Vision"]
      CLS["Classificação"]
      EXT["Extração"]
      VAL["Validações"]
      CONF["Confiança"]
      PRE --> OCR --> CLS --> EXT --> VAL --> CONF
    end
    LOG[("Registro local de revisão<br/>só métricas anônimas")]
  end

  VERCEL -. "entrega HTML/JS" .-> CAP
  VERCEL -. "entrega HTML/JS" .-> REV
  QR -- "QR: sessão + chave no #fragmento" --> CAP
  CRIP1 -- "pedaços cifrados" --> SUPA
  SUPA -- "pedaços cifrados" --> CRIP2
  CRIP2 -- "imagem em memória" --> PRE
  IMP -- "arquivo em memória" --> PRE
  CONF -- "tipo + campos + confiança" --> REV
  REV -- "confirmar / recusar" --> LOG
  REV -- "fotos e dados cifrados<br/>com a chave do dia" --> STORE
  KEY["Chave do dia<br/>só neste navegador<br/>destruída às 18h"] --- REV

  classDef nuvem fill:#eef3fb,stroke:#5b7db8
  classDef privado fill:#eefaf0,stroke:#3c8a4f
  class VERCEL,SUPA,STORE nuvem
  class LOG privado
```

🖼️ [Ver como imagem](img/fluxogramas-01-componentes-e-fronteiras-de-confianca.png)

---

## 2. Jornada completa do usuário

Os dois canais de entrada convergem no mesmo pipeline e na mesma tela de revisão.

```mermaid
flowchart TD
  INI([Juliana abre o sistema no computador]) --> MODO{Modo da sessão}
  MODO -->|Desenvolvimento| DEV[Só documentos fictícios]
  MODO -->|Avaliação ou produção| PROD[Documentos reais]
  DEV --> CANAL
  PROD --> CANAL
  CANAL{Como o documento chega?}

  CANAL -->|Arquivo no computador| ARQ[Arrasta ou seleciona PDF/JPG/PNG/HEIC]
  ARQ --> FMT{Formato válido<br/>e até 20 MB?}
  FMT -->|Não| ERRF[Mensagem de formato inválido] --> CANAL
  FMT -->|Sim| PIPE

  CANAL -->|Celular| GQR[Gera sessão, chave e QR code]
  GQR --> ESC{Celular escaneia<br/>em até 5 min?}
  ESC -->|Não| EXP[QR expirado · gerar outro] --> GQR
  ESC -->|Sim| PAR{Primeiro celular<br/>da sessão?}
  PAR -->|Não| RECUSA[Pareamento recusado]
  PAR -->|Sim| PAG[Abre página de captura no navegador]
  PAG --> FOTO[Fotografa com moldura de orientação]
  FOTO --> QUAL{Imagem nítida<br/>e iluminada?}
  QUAL -->|Não| AVISO[Aviso: reposicionar] --> FOTO
  QUAL -->|Sim| FACES{Documento tem verso?<br/>RG, CNH física, CIN}
  FACES -->|Sim, falta o verso| FOTO
  FACES -->|Não ou já capturado| ENV[Criptografa e envia em pedaços]
  ENV --> CHEGA{Todos os pedaços<br/>chegaram íntegros?}
  CHEGA -->|Não| REENV[Pede reenvio da imagem] --> ENV
  CHEGA -->|Sim| LIMPC[Celular apaga a imagem da memória<br/>e mostra 'Enviado']
  LIMPC --> PIPE

  PIPE[[Pipeline de processamento<br/>ver diagrama 4]] --> TIPO{Tipo reconhecido?}
  TIPO -->|Não| NR[Tela: 'Não reconhecido'<br/>sem campos inventados]
  TIPO -->|Sim| TELA[Tela de revisão:<br/>imagem + campos + confiança]
  NR --> REVT[Juliana indica o tipo correto ou descarta]
  TELA --> REVI[[Revisão campo a campo<br/>ver diagrama 6]]
  REVI --> COPIA[Copia dados confirmados]
  REVT --> FIM
  COPIA --> FIM{Outro documento?}
  FIM -->|Sim| CANAL
  FIM -->|Não| ENC[Encerra sessão:<br/>tela, memória, canal e chave descartados]
  ENC --> VERI[Verificação de resíduo zero] --> FIMJ([Fim])
```

🖼️ [Ver como imagem](img/fluxogramas-02-jornada-completa-do-usuario.png)

---

## 3. Sequência de mensagens no cross-device

O que cada parte envia, em ordem, e o que cada uma consegue ler.

```mermaid
sequenceDiagram
  autonumber
  actor Juliana
  participant N as Navegador do computador
  participant M as Motor local
  participant S as Supabase Broadcast
  participant C as Celular

  Juliana->>N: Clica em "Capturar pelo celular"
  N->>N: Gera id de sessão e chave AES-256 aleatórios
  N->>S: Assina o canal "sessao:<id>"
  N-->>Juliana: Mostra QR = https://.../captura?s=<id>#<chave>
  Note over N,S: A chave fica após o #, e o navegador nunca envia o fragmento ao servidor

  C->>C: Escaneia o QR e abre a página de captura
  C->>S: Assina "sessao:<id>" e envia "pareamento"
  S->>N: Repassa "pareamento"
  N->>N: Marca sessão como pareada e recusa novos celulares
  N->>S: "pareado-ok"
  S->>C: Repassa "pareado-ok"

  C->>C: Captura a foto e verifica nitidez e luz
  C->>C: Comprime e criptografa com a chave do fragmento
  loop Para cada pedaço
    C->>S: pedaço cifrado (n de total)
    S->>N: Repassa pedaço cifrado
  end
  Note over S: O Supabase só vê bytes cifrados e não grava nada

  N->>N: Remonta, verifica integridade e descriptografa
  N->>S: "recebido"
  S->>C: Repassa "recebido"
  C->>C: Apaga a imagem da memória e mostra "Enviado"

  N->>M: POST /processar (imagem em memória, localhost)
  M->>M: Pré-processa, OCR, classifica, extrai, valida
  M-->>N: tipo, campos e confiança
  M->>M: Descarta a imagem da memória
  N->>N: Cifra foto e dados com a chave do dia
  N->>S: Salva no Storage e na tabela (só conteúdo cifrado)
  N-->>Juliana: Tela de revisão

  Juliana->>N: Confirma ou recusa cada campo
  N->>M: POST /revisao (só correto/incorreto por campo)
  M->>M: Grava métrica anônima no registro local

  Juliana->>N: Encerra sessão
  N->>S: "encerrar" e sai do canal
  S->>C: Repassa "encerrar"
  C->>C: Fecha a página de captura
  N->>N: Apaga a chave, a imagem e os campos da memória
```

🖼️ [Ver como imagem](img/fluxogramas-03-sequencia-de-mensagens-no-cross-device.png)

---

## 4. Pipeline de processamento

Do arquivo bruto aos campos com confiança. Cada losango é uma decisão automática.

```mermaid
flowchart TD
  IN[/Imagem ou PDF em memória/] --> ISPDF{É PDF?}
  ISPDF -->|Sim| TXT{Tem texto nativo<br/>na área do documento?}
  TXT -->|Sim| NATIVO[Extrai texto nativo com posições]
  TXT -->|Não, PDF-imagem| RASTER[Converte página em imagem]
  ISPDF -->|Não| IMG[Imagem]
  RASTER --> IMG

  IMG --> ROT{Orientação correta?}
  ROT -->|Não| GIRA[Corrige rotação 90°/180°] --> FACESQ
  ROT -->|Sim| FACESQ{Duas faces<br/>na mesma imagem?}
  FACESQ -->|Sim| SEP[Separa frente e verso]
  FACESQ -->|Não| OCR
  SEP --> OCR[OCR via interface<br/>Apple Vision]

  NATIVO --> CLS
  OCR --> QOCR{Confiança média<br/>do OCR suficiente?}
  QOCR -->|Não| BAIXA[Marca documento como<br/>baixa legibilidade] --> CLS
  QOCR -->|Sim| CLS

  CLS{Classificação por regras<br/>palavras-chave, MRZ, linha digitável, layout}
  CLS -->|Decisão clara| TIPO[Tipo definido]
  CLS -->|Ambígua| LLMC[Modelo local classifica<br/>a partir do texto]
  LLMC --> TCONF{Confiança<br/>suficiente?}
  TCONF -->|Sim| TIPO
  TCONF -->|Não| NR[[Não reconhecido]]

  TIPO --> ROUTE{Tipo}
  ROUTE -->|NF-e| E1[Campos da NF-e]
  ROUTE -->|Boleto| E2[Campos do boleto]
  ROUTE -->|Fatura| E3[Campos da fatura]
  ROUTE -->|CNH| E4[Campos da CNH]
  ROUTE -->|RG antigo| E5[Campos do RG]
  ROUTE -->|CIN| E6[Campos da CIN]

  E1 & E2 & E3 & E4 & E5 & E6 --> REGRAS[Extração por regras<br/>ancoradas em rótulos e padrões]
  REGRAS --> FALTA{Algum campo<br/>obrigatório faltando?}
  FALTA -->|Sim| LLME[Modelo local tenta extrair<br/>só os campos faltantes]
  FALTA -->|Não| VALID
  LLME --> VALID

  VALID[Validações por dígito verificador<br/>CPF · CNPJ · chave NF-e · linha digitável · MRZ]
  VALID --> CRUZ[Validação cruzada<br/>boleto: valor e vencimento x linha<br/>CNH/CIN: campos x MRZ]
  CRUZ --> SCORE[Confiança por campo<br/>OCR + validação + origem regra/modelo]
  SCORE --> NAOINV{Campo sem evidência<br/>no texto?}
  NAOINV -->|Sim| NE[Marca 'não encontrado'<br/>nunca preenche por suposição]
  NAOINV -->|Não| OUT
  NE --> OUT[/Tipo + campos + confiança/]
```

🖼️ [Ver como imagem](img/fluxogramas-04-pipeline-de-processamento.png)

---

## 5. Estados da sessão

Ciclo de vida de uma sessão cross-device, incluindo falhas.

```mermaid
stateDiagram-v2
  [*] --> Criada: Juliana pede captura pelo celular
  Criada --> AguardandoPareamento: QR exibido
  AguardandoPareamento --> Expirada: 5 min sem leitura
  AguardandoPareamento --> Pareada: primeiro celular conecta
  Pareada --> Pareada: segundo celular recusado
  Pareada --> Recebendo: celular envia pedaços
  Recebendo --> Recebendo: pedaço n de total
  Recebendo --> FalhaIntegridade: pedaço faltando ou corrompido
  FalhaIntegridade --> Recebendo: reenvio solicitado
  FalhaIntegridade --> Encerrada: excedeu tentativas
  Recebendo --> Processando: imagem completa e descriptografada
  Processando --> EmRevisao: campos exibidos
  Processando --> NaoReconhecido: tipo não identificado
  NaoReconhecido --> EmRevisao: Juliana indica o tipo
  EmRevisao --> Pareada: próximo documento (HU-11)
  EmRevisao --> Encerrada: Juliana encerra
  Pareada --> Encerrada: inatividade
  Expirada --> Encerrada
  Encerrada --> Verificada: verificação de resíduo zero
  Verificada --> [*]

  note right of Encerrada
    Chave, imagem e campos apagados da memória
    Canal Broadcast abandonado nos dois lados
  end note
```

🖼️ [Ver como imagem](img/fluxogramas-05-estados-da-sessao.png)

---

## 6. Revisão humana e ciclo de aprendizado

O que acontece com cada confirmação ou recusa, conforme o modo ([ADR 0004](../decisoes/0004-revisao-humana-e-ciclo-de-aprendizado.md)).

```mermaid
flowchart TD
  T[Tela de revisão] --> TT{Tipo detectado correto?}
  TT -->|Recusa| TC[Juliana indica o tipo correto] --> REX[Reextrai com o tipo indicado] --> CAMPOS
  TT -->|Confirma| CAMPOS[Lista de campos ordenada<br/>baixa confiança primeiro]
  CAMPOS --> C1{Para cada campo}
  C1 -->|Confirma| OK[Campo confirmado]
  C1 -->|Recusa| NOK[Campo recusado]
  NOK --> MD{Modo da sessão?}
  MD -->|Desenvolvimento| CORR[Juliana digita o valor correto]
  MD -->|Avaliação ou produção| SEMV[Registra só 'incorreto']
  OK --> REG
  CORR --> REG
  SEMV --> REG

  REG{O que gravar?}
  REG -->|Desenvolvimento| RD[(Registro completo<br/>valores extraídos e corrigidos<br/>documento fictício)]
  REG -->|Avaliação ou produção| RP[(Registro anônimo<br/>tipo · campo · correto/incorreto<br/>tempos · canal · versão)]

  RD --> APR[Ciclo de aprendizado]
  RP --> MED[Só medição]

  APR --> A1[Erro vira caso de teste de regressão]
  APR --> A2[Ajuste de regras e prompts]
  APR --> A3[Calibração dos limites de confiança]
  MED --> M1[Acurácia por campo e por tipo<br/>com tamanho da amostra]
  M1 --> PRI[Priorização da próxima versão]
  A1 & A2 & A3 --> NV[Nova versão do motor]
  NV --> RODA[Roda o conjunto de desenvolvimento]
  RODA --> CMP{Melhorou sem<br/>piorar outros campos?}
  CMP -->|Sim| PUB[Versão aprovada]
  CMP -->|Não| A2
  PRI --> A2
```

🖼️ [Ver como imagem](img/fluxogramas-06-revisao-humana-e-ciclo-de-aprendizado.png)

---

## 7. Garantias de privacidade: onde o documento existe

Cada lugar por onde o documento passa, por quanto tempo e como isso é verificado.

```mermaid
flowchart LR
  subgraph EXISTE["Documento em texto aberto"]
    direction TB
    X1["Memória da página de captura<br/>até o 'recebido'"]
    X2["Memória do navegador do computador<br/>enquanto a tela estiver aberta"]
    X3["Memória do motor local<br/>só durante o processamento"]
  end
  subgraph CIFRADO["Documento cifrado"]
    direction TB
    Y1["Rede celular → Supabase"]
    Y2["Supabase → computador"]
    Y3["Storage e tabela do Supabase<br/>até as 18h"]
  end
  subgraph NUNCA["Nunca"]
    direction TB
    Z1["Galeria do celular"]
    Z2["Armazenamento local e cache do navegador"]
    Z3["Arquivos temporários no disco"]
    Z4["Conteúdo legível no Supabase<br/>(só existe cifrado)"]
    Z5["Logs do servidor"]
    Z6["Registro de revisão em produção"]
  end
  subgraph PROVA["Verificação automatizada"]
    direction TB
    V1["Teste: localStorage, IndexedDB,<br/>Cache Storage vazios após sessão"]
    V2["Teste: nenhum arquivo novo<br/>em diretórios temporários"]
    V3["Teste: após as 18h, tabela e Storage<br/>vazios e chave do dia inexistente"]
    V4["Teste: registro de produção sem<br/>CPF, nomes ou base64"]
    V5["scripts/limpar-e-verificar.sh"]
  end
  EXISTE --> PROVA
  CIFRADO --> PROVA
  NUNCA --> PROVA
```

🖼️ [Ver como imagem](img/fluxogramas-07-garantias-de-privacidade-onde-o-documento-existe.png)

---

## 8. Remoção diária às 18h

As três camadas independentes de remoção ([ADR 0007](../decisoes/0007-retencao-temporaria-e-purga-diaria.md)).

```mermaid
flowchart TD
  DIA([Início do dia]) --> K1[Primeiro uso: computador gera a chave do dia<br/>não exportável, nunca enviada ao servidor]
  K1 --> USO[Cadastros do dia: fotos e dados<br/>cifrados com a chave e salvos no Supabase]
  USO --> H17{17h00?}
  H17 -->|Sim| AV[Tela mostra contagem regressiva<br/>e lembra de baixar pacotes pendentes]
  AV --> BX{Pacote baixado?}
  BX -->|Sim| ESC[Arquivos sob responsabilidade do escritório]
  BX -->|Não| RISCO[Será perdido às 18h]
  H17 -->|Não| USO
  ESC --> H18
  RISCO --> H18
  H18{{18h00 de Brasília}}

  H18 --> C1[Camada 1 · computador<br/>destrói a chave do dia]
  H18 --> C2[Camada 2 · servidor<br/>pg_cron apaga tabela e Storage]
  C1 --> R1[Cópias remanescentes, inclusive backups,<br/>ficam ilegíveis]
  C2 --> R2[Itens removidos do Supabase]

  HORA[[A cada hora · camada 3]] --> TTL{Algum item com<br/>mais de 24h?}
  TTL -->|Sim| DEL[Apaga o item] --> LOGR
  TTL -->|Não| LOGR

  R1 --> LOGR[(Registro anônimo:<br/>horário · itens removidos · resultado)]
  R2 --> LOGR
  LOGR --> VER{Teste de verificação<br/>às 18h05}
  VER -->|Tabela e Storage vazios<br/>e chave inexistente| OK([✅ Dia encerrado])
  VER -->|Algo restou| ALERTA([❌ Alerta e remoção manual])
```

🖼️ [Ver como imagem](img/fluxogramas-08-remocao-diaria-as-18h.png)
