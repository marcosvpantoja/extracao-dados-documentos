# Documento de Requisitos do Produto (PRD)

**Produto:** Extração de Dados de Documentos
**Versão do documento:** 1.2 · 10/11/2026 (segmento: advocacia de consumidor de alto volume, após a [Etapa 3](etapas/03-validacao-do-problema.md))
**Status:** Aprovado para o MVP

## 1. Resumo

Sistema que recebe documentos por **importação de arquivo** no computador ou por **captura com o celular** (fluxo cross-device via QR code), identifica automaticamente o tipo, extrai os dados e os exibe numa tela de revisão para o usuário confirmar ou recusar cada campo. No estudo de caso, o que o sistema guarda fica cifrado e é removido às 18h de cada dia ([ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md)); em produção, os documentos seriam guardados cifrados pelo prazo que o escritório definir ([ADR 0008](decisoes/0008-armazenamento-em-producao.md)).

## 2. Problema

Escritórios de advocacia de massa em direito do consumidor cadastram muitos clientes por dia. Cada atendimento traz documentos de identificação (RG, CIN ou CNH), comprovante de residência e provas do caso (notas fiscais, faturas, boletos), que chegam misturados e em qualidade variável, normalmente pelo WhatsApp. A digitação manual torna o cadastro um gargalo medido em tempo, e um erro, como um CPF errado, se repete em procurações e processos. As ferramentas atuais cadastram por foto um documento por vez, sem as provas, e soluções de verificação de identidade são voltadas a antifraude e armazenam documentos.

Evidências em [Etapa 3](etapas/03-validacao-do-problema.md).

## 3. Personas

- **Juliana, assistente de cadastro** (primária): quer cadastrar cada cliente em poucos minutos, sem digitar e sem erros que voltem da equipe jurídica.
- **Roberto, cliente consumidor** (secundária): fotografa os próprios documentos à distância; quer enviar tudo de uma vez, sem instalar nada.
- **Dra. Paula, advogada** (terciária): precisa de dados corretos e dos arquivos para instruir a petição.

Detalhamento, fontes e histórico em [Personas](persona.md).

## 4. Tese do MVP

> É possível cadastrar um cliente, com identificação, comprovante de residência e provas, numa única interação, de forma **ágil** e **precisa**, capturando os documentos pelo celular do próprio cliente ou importando arquivos, com os documentos protegidos do envio ao armazenamento.

**Segurança dos dados, em dois contextos:**

| | Estudo de caso (o que é construído) | Produção (desenho de referência) |
|---|---|---|
| Regra | Nada sobrevive às 18h; nenhum item chega a 24h ([ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md)) | Documentos guardados pelo prazo que o escritório definir ([ADR 0008](decisoes/0008-armazenamento-em-producao.md)) |
| Por quê | Proteger os documentos de quem testa o sistema | O escritório precisa dos documentos durante todo o processo |
| Criptografia | Chave do dia só no navegador do escritório; servidor não lê | Chave por escritório num KMS; servidor lê só sob controle de acesso e auditoria |

Nos dois contextos, a captura pelo celular é cifrada ponta a ponta e o escritório é o controlador dos dados (LGPD).

## 5. Escopo

**Segmento:** escritórios de direito do consumidor com alto volume de clientes.
**Tipos de documento:** NF-e (DANFE), boleto, fatura de serviço, CNH (física e digital), RG antigo (modelos estaduais) e CIN.
**Canais:** importação de arquivo (PDF, JPG, PNG, HEIC) e captura via celular.

**Fora do escopo do MVP:** modo rede local (offline), exibição de campos em streaming, captura automática pela câmera, retreinamento de modelos, histórico de documentos, integração com sistemas contábeis, documentos manuscritos, outros tipos (contratos, NFS-e, comprovantes de pagamento), documentos trabalhistas (CTPS, contracheques, TRCT, extrato do FGTS), geração automática de procuração. Ver [ADR 0003](decisoes/0003-escopo-do-mvp.md).

## 6. Histórias de usuário

Prioridade MoSCoW: **M** = obrigatório, **S** = importante, **C** = desejável, **W** = não agora.

| ID | História | Prioridade |
|---|---|---|
| HU-01 | Como Juliana, quero importar um arquivo sem dizer o que ele é, para não perder tempo classificando | M |
| HU-02 | Como Juliana, quero enviar ao cliente um QR code ou link para ele fotografar os próprios documentos, para não depender de WhatsApp | M |
| HU-03 | Como Juliana, quero ver os dados extraídos ao lado da imagem do documento, para conferir rapidamente | M |
| HU-04 | Como Juliana, quero confirmar ou recusar cada campo, para garantir que só dados corretos sigam adiante | M |
| HU-05 | Como Juliana, quero saber quais campos têm baixa confiança, para conferir só esses | M |
| HU-06 | Como Roberto, quero ter certeza de que meu documento não fica guardado, para confiar no escritório | M |
| HU-13 | Como Roberto, quero abrir pelo WhatsApp o link de captura e fotografar todos os meus documentos de uma vez, para fazer o cadastro sem ir ao escritório | M |
| HU-14 | Como Roberto, quero entender o que fazer na página de captura sem ajuda, para concluir sozinho | M |
| HU-07 | Como Juliana, quero ser orientada pelo celular sobre enquadramento e luz, para a foto sair legível na primeira tentativa | S |
| HU-08 | Como Juliana, quero copiar os dados confirmados, para colá-los no sistema contábil | S |
| HU-09 | Como responsável pelo produto, quero ver a acurácia por campo e por tipo, para priorizar melhorias | S |
| HU-10 | Como Juliana, quero que o sistema avise quando não reconhecer o documento, em vez de inventar dados | M |
| HU-11 | Como Juliana, quero processar vários documentos do mesmo cliente em sequência sem reescanear o QR code | C |
| HU-12 | Como Juliana, quero que a câmera capture sozinha quando a imagem estiver nítida | W |
| HU-15 | Como Juliana, quero baixar os arquivos e os dados confirmados do cliente num pacote organizado, para anexar ao sistema do escritório | M |
| HU-16 | Como Dra. Paula, quero a procuração preenchida com os dados confirmados, para não redigitar a qualificação | W |
| HU-17 | Como Juliana, quero cadastrar clientes de ações trabalhistas (CTPS, contracheques, TRCT, FGTS) | W |

## 7. Requisitos funcionais

### 7.1 Entrada

| ID | Requisito | Critério de aceite | Prior. |
|---|---|---|---|
| RF-01 | Importar arquivo PDF, JPG, PNG ou HEIC no computador | Arquivo de até 20 MB é aceito por arrastar ou selecionar; formato inválido mostra mensagem clara | M |
| RF-02 | Gerar QR code de sessão para captura pelo celular | QR exibido em até 2 s após clicar em "Capturar pelo celular" | M |
| RF-03 | Sessão de uso único e expiração curta | Segundo celular é recusado; sessão não pareada expira em 5 min; QR expirado mostra aviso e opção de gerar outro | M |
| RF-04 | Página de captura abre no navegador do celular, sem app | Funciona no Safari (iOS) e no Chrome (Android) atuais | M |
| RF-05 | Captura pela câmera com orientação de enquadramento | Moldura na tela; aviso de imagem escura ou borrada antes do envio | S |
| RF-06 | Captura de frente e verso para RG, CNH física e CIN | Página pede a segunda face quando aplicável; as duas faces chegam como um documento | S |
| RF-07 | Criptografia ponta a ponta da imagem | Imagem criptografada no celular (AES-GCM); chave só no fragmento da URL do QR; canal de repasse recebe apenas dados cifrados | M |

### 7.2 Processamento

| ID | Requisito | Critério de aceite | Prior. |
|---|---|---|---|
| RF-08 | Pré-processamento da imagem | Corrige rotação de 90°/180°; separa frente e verso na mesma página | M |
| RF-09 | Leitura de texto nativo de PDF e OCR de imagem | PDF com texto usa o texto nativo; PDF-imagem e fotos passam por OCR | M |
| RF-10 | Classificação automática do tipo | Retorna um dos seis tipos ou "Não reconhecido", com confiança | M |
| RF-11 | Extração dos campos do tipo detectado | Campos conforme o [catálogo da Etapa 1](etapas/01-documentos-e-campos.md#campos-alvo) | M |
| RF-12 | Validação automática de identificadores | CPF, CNPJ, chave NF-e, linha digitável, código de barras e MRZ validados por dígito verificador | M |
| RF-13 | Validação cruzada | Valor e vencimento do boleto conferidos contra a linha digitável; dados da CNH/CIN conferidos contra a MRZ | S |
| RF-14 | Confiança por campo | Cada campo recebe nível alto, médio ou baixo, combinando confiança do OCR e validações | M |
| RF-15 | Não inventar dados | Campo não encontrado aparece como "não encontrado", nunca preenchido por suposição | M |

### 7.3 Revisão

| ID | Requisito | Critério de aceite | Prior. |
|---|---|---|---|
| RF-16 | Tela de revisão com imagem e campos lado a lado | Imagem com zoom; campos agrupados; campos de baixa confiança destacados | M |
| RF-17 | Confirmar ou recusar tipo e campos | Cada item tem as duas ações; recusa do tipo pede o tipo correto | M |
| RF-18 | Correção de valor no modo desenvolvimento | Disponível só no modo desenvolvimento; oculta nos demais | S |
| RF-19 | Indicação do modo da sessão | Modo (desenvolvimento, avaliação ou produção) sempre visível; documento real nunca abre em modo desenvolvimento | M |
| RF-20 | Copiar dados confirmados | Botão copia os campos confirmados em texto ou JSON | S |
| RF-27 | Aviso de remoção | A partir das 17h, contagem regressiva e lembrete de baixar os pacotes ainda não baixados | M |
| RF-26 | Entrega ao escritório | Download de pacote com arquivos originais e dados confirmados (JSON/CSV), gerado na memória do navegador e salvo apenas onde o usuário escolher | M |
| RF-21 | Encerrar sessão | Ao encerrar, imagem e dados somem da tela e da memória; canal e chave são descartados | M |

### 7.4 Medição e aprendizado

| ID | Requisito | Critério de aceite | Prior. |
|---|---|---|---|
| RF-22 | Registro de revisão no modo avaliação/produção | Registra só tipo, resultado por campo, tempos, canal e versão; nunca valores nem imagem | M |
| RF-23 | Registro completo no modo desenvolvimento | Registra valores extraídos e corrigidos dos documentos fictícios | S |
| RF-24 | Relatório de acurácia | Acurácia por campo e por tipo, sempre com tamanho da amostra | S |
| RF-28 | Registro de auditoria | Abrir, baixar e excluir documento geram um registro com horário, evento, perfil, estação, código do documento e tipo; a tabela só aceita inclusão ([ADR 0009](decisoes/0009-registro-de-auditoria-no-estudo.md)) | M |
| RF-29 | Perfil simulado | Seletor de perfil (assistente ou advogada) sempre visível; o perfil ativo vai para o registro de auditoria | M |
| RF-30 | Devolver por dado errado | Em um cadastro confirmado, qualquer perfil marca o campo errado; a marcação alimenta a métrica de proteção ([Etapa 5](etapas/05-metricas.md#2-métrica-de-proteção)) | S |
| RF-25 | Erros viram testes | Cada erro revisado no modo desenvolvimento pode ser exportado como caso de teste de regressão | C |

## 8. Requisitos não funcionais

| ID | Categoria | Requisito | Critério de aceite | Prior. |
|---|---|---|---|---|
| RNF-01 | Privacidade (estudo) | Retenção máxima até as 18h do dia, nunca 24h ou mais; nada persiste no celular | Teste automatizado verifica, após as 18h, tabela e Storage vazios, chave do dia inexistente e nenhum item com mais de 24h; celular sem resíduo após a sessão | M |
| RNF-12 | Privacidade | Conteúdo salvo sempre cifrado | Nenhum campo de conteúdo legível no banco ou no Storage; chave do dia nunca enviada ao servidor | M |
| RNF-02 | Privacidade | Documento real não sai do celular e do computador em texto aberto | Só dados cifrados trafegam pelo canal de repasse; motor de leitura é local | M |
| RNF-03 | Privacidade (estudo) | Remoção diária às 18h em três camadas | Destruição da chave, tarefa agendada às 18h e limite de 24h executado de hora em hora, cada uma com registro anônimo ([ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md)) | M |
| RNF-13 | Privacidade | Registro de auditoria sem dados pessoais | Tabela sem colunas de texto livre; teste automatizado procura CPF, nomes de arquivo e base64 e não encontra nada | M |
| RNF-04 | Segurança | Sessão protegida contra uso indevido | Identificador e chave aleatórios de 128 bits ou mais; uso único; expiração | M |
| RNF-05 | Desempenho | Rápido o suficiente | Meta de tempo até o resultado completo definida na etapa de métricas a partir da linha de base | M |
| RNF-06 | Acurácia | Acerto alto por campo | Meta definida a partir da linha de base no conjunto de desenvolvimento | M |
| RNF-07 | Extensibilidade | Novo tipo de documento sem reescrever o pipeline | Novo tipo exige apenas regras de classificação, catálogo de campos e validações próprias | S |
| RNF-08 | Portabilidade | OCR trocável | Pipeline depende só da interface de OCR ([ADR 0006](decisoes/0006-ocr-apple-vision.md)) | S |
| RNF-09 | Compatibilidade | Navegadores suportados | Computador: Chrome e Safari atuais. Celular: Safari iOS e Chrome Android atuais | M |
| RNF-10 | Acessibilidade | Tela de revisão acessível | Navegação por teclado, contraste AA, rótulos para leitores de tela | S |
| RNF-11 | Transparência | Sistema explica o que não sabe | Confiança visível por campo; "não encontrado" explícito | M |

## 9. Métricas de sucesso

| Métrica | Definição | Meta |
|---|---|---|
| Acurácia de classificação | % de documentos com tipo detectado corretamente | A definir na linha de base |
| Acurácia por campo (**preciso**) | % de campos confirmados na revisão, por tipo | A definir na linha de base |
| Tempo até o resultado | Da captura ou importação até os campos na tela | A definir na linha de base |
| Tempo de cadastro por cliente (**ágil**) | Do início da sessão até todos os campos do cliente confirmados | A definir na linha de base |
| Recapturas por documento | Quantas vezes um documento precisou ser fotografado de novo | A definir na linha de base |
| Retenção respeitada (estudo) | % de dias em que nada sobrevive às 18h e nenhum item chega a 24h | 100% |
| Taxa de "não reconhecido" correto | % de documentos fora do escopo marcados como "não reconhecido" | A definir na linha de base |

## 10. Premissas e dependências

- Hardware de referência: Mac com Apple M4 e 16 GB de RAM.
- Celular e computador com acesso à internet no modo cross-device.
- Disponibilidade do Supabase Realtime e da Vercel.
- Documentos fictícios representativos dos layouts reais ([Etapa 1](etapas/01-documentos-e-campos.md)).

## 11. Riscos

| Risco | Impacto | Mitigação |
|---|---|---|
| RG antigo com muitos modelos estaduais | Acurácia baixa nesse tipo | Regras por campo ancoradas em rótulos ("FILIAÇÃO", "NATURALIDADE"); validação de CPF |
| Fotos com reflexo e baixa luz | OCR falha em documentos pessoais | Orientação na captura (RF-05); aviso de qualidade antes do envio |
| Modelo local lento em 16 GB | Meta de tempo não atingida | Regras primeiro, modelo só quando necessário; medir cedo |
| Limite de tamanho no Broadcast | Imagem não chega inteira | Compressão e envio em pedaços |
| Página na nuvem acessando motor em `localhost` | Bloqueio por navegador | Prova de conceito em Chrome e Safari antes de construir o resto |
| Falha da remoção das 18h | Dados além do prazo | Três camadas independentes; destruição da chave torna cópias ilegíveis (RNF-03) |
| Cadastro feito perto das 18h perdido antes do download | Retrabalho | Aviso a partir das 17h (RF-27) |

## 12. Documentos relacionados

- [Personas](persona.md)
- [Fluxogramas do sistema](arquitetura/fluxogramas.md)
- [Registro de decisões (ADRs)](decisoes/README.md)
- [Etapa 0 — Concepção](etapas/00-concepcao.md) · [Etapa 1 — Documentos e campos](etapas/01-documentos-e-campos.md)
