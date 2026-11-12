# Cadastro por documentos

**O cliente fotografa os documentos no celular; o escritório recebe os dados lidos, conferidos e prontos para confirmar.**

Estudo de caso de produto, do problema ao software funcionando: um sistema que identifica sozinho o tipo de documento (RG, CIN, CNH, nota fiscal, boleto ou fatura), extrai os dados e os apresenta para conferência humana, com privacidade desenhada desde a primeira decisão.

<table>
  <tr>
    <td width="24%"><img src="docs/ux/img/telas-v1.2-produto/celular-04-camera.png" alt="Câmera do celular com cantos de enquadramento"></td>
    <td width="76%"><img src="docs/ux/img/telas-v1.2-produto/escritorio-3-revisao.png" alt="Tela de revisão: foto ao lado dos dados extraídos"></td>
  </tr>
  <tr>
    <td align="center"><sub>Celular do cliente</sub></td>
    <td align="center"><sub>Revisão no escritório: foto ao lado dos dados</sub></td>
  </tr>
</table>

> Projeto de estudo e pesquisa, sem fins comerciais. Todos os documentos usados no desenvolvimento são fictícios.

---

## Em 30 segundos

| Tema | Resumo |
|---|---|
| **Problema** | Escritórios de direito do consumidor cadastram dezenas de clientes por dia. Os documentos chegam misturados pelo WhatsApp, são digitados à mão, e um CPF errado chega à procuração e ao processo |
| **Para quem** | A assistente de cadastro (usuária principal), o cliente que envia os documentos e a advogada que recebe o cadastro |
| **Solução** | Link de captura pelo celular, leitura automática (OCR, regras e IA local), validação por dígito verificador e revisão campo a campo com a foto ao lado |
| **Métrica que guia o produto** | Clientes cadastrados por semana **sem nenhuma edição** |
| **Onde está** | Etapas 0 a 11 de 14 concluídas: produto construído e testado no celular. Próximo: sessões com usuários reais |

---

## O problema

**Juliana** é assistente de cadastro numa advocacia de massa. Cada cliente envia RG ou CNH, um comprovante de residência e as provas da cobrança que contesta. Os seis tipos de documento aparecem **no mesmo atendimento**, misturados.

| Dor | Consequência |
|---|---|
| Digitação manual de identificação e provas | O cadastro vira gargalo, e o tempo de cadastro é cobrado como indicador |
| Documento ilegível exige novo pedido ao cliente | O cadastro espera horas ou dias pela resposta |
| Erro de leitura passa adiante | Um CPF errado se repete na procuração e no processo |

O segmento **não foi o ponto de partida**. O projeto começou com escritórios contábeis e mudou de rumo quando a pesquisa mostrou que nota fiscal e boleto já chegam por canais eletrônicos e que o cadastro contábil é pouco frequente ([Etapa 3](docs/etapas/03-validacao-do-problema.md)).

→ [Personas](docs/persona.md) · [Pesquisa e entrevistas simuladas](docs/pesquisa/entrevistas-simuladas.md)

---

## Como o produto foi pensado

Cada fase respondeu a uma pergunta antes de passar à seguinte. Toda decisão relevante ficou registrada com o motivo e as alternativas descartadas.

| Fase | Pergunta | Decisão central | Artefatos |
|---|---|---|---|
| **Descoberta** | O problema existe, e para quem? | Pivô para advocacia de consumidor de alto volume | [Hipóteses](docs/etapas/00-concepcao.md), [pesquisa](docs/etapas/03-validacao-do-problema.md), [personas](docs/persona.md) |
| **Estratégia** | Onde o produto gera valor? | O documento ilegível pode custar mais que a digitação; o cliente corrige na hora, com o documento na mão | [Visão, árvore de oportunidades, PR/FAQ, jornadas](docs/etapas/04-estrategia.md) |
| **Métricas** | Como saber se funciona? | North Star "clientes sem nenhuma edição", com métrica de proteção vinda de fora da revisão | [North Star, árvore de métricas, OKRs](docs/etapas/05-metricas.md) |
| **Priorização** | O que construir primeiro? | RICE, MVP definido, roadmap "captura primeiro" | [Backlog, RICE, DoR/DoD, roadmap](docs/etapas/06-priorizacao.md) |
| **Viabilidade** | Se fosse produto, se sustentaria? | Venda direta não se paga; o caminho é licenciar para softwares jurídicos | [Business case com dados do CNJ e do TST](docs/etapas/07-business-case.md) |
| **Arquitetura** | Como funciona, com que riscos? | Riscos técnicos testados antes de construir; um deles mudou a arquitetura | [C4](docs/arquitetura/c4.md), [provas de conceito](docs/etapas/08-arquitetura-e-poc.md), [11 decisões (ADRs)](docs/decisoes/README.md) |
| **Experiência** | Como o cliente e a assistente usam? | Wireframes aprovados antes do código; mudanças guiadas por testes no celular | [Wireframes](docs/ux/captura-wireframes.md), [guia visual](docs/ux/guia-visual.html), [telas finais](docs/ux/telas-finais.md) |
| **Construção** | O motor generaliza? | Medição honesta antes de ajustar; regras genéricas e IA local com trava contra dado inventado | [Motor de extração](docs/etapas/10-motor.md), [requisitos](docs/requisitos.md) |

---

## Decisões que mudaram o rumo

As decisões revistas ficam lado a lado com as originais. É nelas que o projeto mais aprendeu.

| Antes | Depois | O que provocou a mudança |
|---|---|---|
| Escritório contábil | Advocacia de consumidor de alto volume | Pesquisa: os documentos já chegavam por canal eletrônico, e o cadastro era raro |
| Venda direta a escritórios | Licenciamento para softwares jurídicos | Business case: a venda direta exigiria de 14% a 28% de todo o mercado alcançável |
| As duas páginas na internet | Aplicação do escritório servida pelo computador local | Prova de conceito: o Safari bloqueia a chamada da página ao computador |
| Regras de extração por layout | Regras genéricas e IA local | Teste com layouts novos: as regras cobriam só 27% dos campos |
| Celular recusa foto com reflexo | Celular barra só o óbvio; o motor decide | Primeiro teste no celular: fotos boas eram recusadas |
| Nada fica guardado | Guardado cifrado até as 18h; só a chave no navegador | Atualizar a página perdia o cadastro do dia |

→ [Linha do tempo completa da evolução do produto](docs/evolucao.md)

---

## O produto

**No celular do cliente**, sem instalar nada: abre o link, fotografa ou importa cada documento, recebe orientação de luz e enquadramento e, se a foto não der para ler, um pedido de nova foto na hora.

**No computador do escritório:** os documentos chegam classificados e lidos; a assistente confere cada campo com a foto ao lado, o cliente confere os próprios dados no fim e o escritório baixa um pacote com os arquivos e os dados.

| | | | |
|---|---|---|---|
| <img src="docs/ux/img/telas-v1.2-produto/celular-01-abertura.png" width="170"><br>Abertura | <img src="docs/ux/img/telas-v1.2-produto/celular-03-documento-n-de-m.png" width="170"><br>Documento | <img src="docs/ux/img/telas-v1.2-produto/celular-07b-vamos-tentar-de-novo.png" width="170"><br>Nova foto pedida pelo motor | <img src="docs/ux/img/telas-v1.2-produto/celular-09-tudo-enviado.png" width="170"><br>Envio concluído |

<img src="docs/ux/img/telas-v1.2-produto/escritorio-4-conferencia-do-cliente.png" alt="Conferência do cliente" width="720">

→ [Todas as telas e o que mudou entre as versões](docs/ux/telas-finais.md) · [Fluxo das telas](docs/ux/captura-wireframes.md#fluxo-das-telas) · [Fluxogramas do sistema](docs/arquitetura/fluxogramas.md)

---

## Resultados até aqui

Medidos em **documentos fictícios**. O resultado com pessoas reais é a próxima etapa.

| Medida | Resultado |
|---|---|
| Cobertura do motor em layouts nunca vistos | **27%** com as primeiras regras → **82%** com regras genéricas e IA |
| Campos extraídos corretos (32 documentos) | **95%**, com cobertura de **89%** |
| Classificação do tipo de documento | 31 de 32 |
| Detecção da posição da foto | 8 de 8 rotações |
| Envio de uma foto de 2 MB, cifrada, do celular ao computador | menos de 0,5 s |
| Testes automatizados | 27 na aplicação e 10 no motor |

O primeiro número do motor foi 100%, e ele estava errado: as regras tinham sido escritas olhando os mesmos documentos em que eram medidas. O número honesto veio de documentos com layouts novos, e as melhorias partiram dele ([Etapa 10](docs/etapas/10-motor.md)).

---

## Privacidade por desenho

| Princípio | Como se aplica |
|---|---|
| O servidor não lê os documentos | A captura é cifrada no celular; o que fica guardado é cifrado com uma chave que só o navegador do escritório tem |
| Nada sobrevive ao dia (no estudo) | Remoção às 18h em três camadas independentes: destruição da chave, tarefa agendada no banco e limite de 24h |
| A IA não sai do computador | OCR e IA rodam localmente; nenhum documento vai para provedores de IA |
| A IA não inventa dados | Todo valor sugerido pela IA precisa aparecer no texto lido; o que vem dela é marcado para conferência |
| Registros sem dados pessoais | Medição e auditoria guardam só eventos, códigos e tempos; o banco recusa texto livre |
| Quem revisa não confere | A métrica de proteção vem do cliente, não de quem fez a revisão |

A separação entre o que o estudo constrói e o que um produto real exigiria também está documentada: em produção, os documentos ficariam guardados com chave por escritório, controle de acesso e auditoria ([ADR 0008](docs/decisoes/0008-armazenamento-em-producao.md)).

---

## Próximos passos

1. **Linha de base com fotos de documentos impressos** e metas dos resultados-chave **congeladas antes** das sessões, para a régua não se ajustar ao resultado.
2. **Qualidade:** testes de ponta a ponta e de privacidade automatizados.
3. **Sessões com usuários:** a pessoa fotografa os próprios documentos e confere os dados.
4. **Retrospectiva:** resultados finais e aprendizados.

| # | Etapa | Situação |
|---|---|---|
| 0–8 | Concepção, documentos e campos, requisitos, validação, estratégia, métricas, priorização, business case, arquitetura e provas de conceito | ✅ |
| 9 | Captura pelo celular | ✅ testada |
| 10 | Motor de extração | ✅ |
| 11 | Revisão, conferência, pacote, armazenamento cifrado e auditoria | ✅ testada |
| 12 | Qualidade | ⚪ |
| 13 | Avaliação com usuários | ⚪ |
| 14 | Lançamento e retrospectiva | ⚪ |

---

## Mapa do repositório

| Onde | O quê |
|---|---|
| [`docs/etapas/`](docs/etapas/) | Uma nota por etapa, na ordem em que aconteceu |
| [`docs/decisoes/`](docs/decisoes/) | Decisões de arquitetura e produto (ADRs), com alternativas e consequências |
| [`docs/requisitos.md`](docs/requisitos.md) | Histórias de usuário, requisitos e critérios de aceite |
| [`docs/arquitetura/`](docs/arquitetura/) | C4 e fluxogramas, com imagens |
| [`docs/ux/`](docs/ux/) | Wireframes, guia visual, telas por versão |
| [`docs/evolucao.md`](docs/evolucao.md) | Linha do tempo das decisões e dos números |
| [`docs/competencias.md`](docs/competencias.md) | O que o projeto exercita, papel a papel |
| [`app/`](app/) | Página de captura (celular) e aplicação do escritório: React e TypeScript |
| [`src/`](src/) | Motor local: OCR (Apple Vision), classificação, extração, validação e IA (Ollama) |
| [`supabase/`](supabase/) | Banco: armazenamento cifrado, auditoria e remoção agendada |
| [`scripts/`](scripts/) | Documentos fictícios, avaliação do motor, relatório dos resultados-chave e imagens dos diagramas |
| [`tests/`](tests/), `app/src/**/*.test.ts` | Testes automatizados |

### Como rodar

```bash
scripts/iniciar-motor.sh          # IA local + motor; abra http://localhost:8787
.venv/bin/python scripts/avaliar.py --ia     # avaliação do motor nos documentos fictícios
.venv/bin/python scripts/relatorio.py        # resultados-chave a partir do registro de medição
```

Modo de demonstração, sem celular: `captura.html?demo=camera` e `escritorio.html?demo=revisao`.

---

**Marcos Pantoja** · [github.com/marcosvpantoja](https://github.com/marcosvpantoja)
