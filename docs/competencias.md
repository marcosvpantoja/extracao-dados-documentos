# Competências demonstradas

Este estudo de caso percorre o ciclo completo de um produto digital e exercita, de forma explícita, sete papéis: **Product Manager, Arquiteto de Software, Product Owner, Desenvolvedor, Front-end, UX e Tester (QA)**.

Para PM, a lista de competências foi consolidada a partir de frameworks públicos de carreira ([ProductLed](https://www.productledalliance.com/product-management-skills-framework/), [GitLab](https://handbook.gitlab.com/handbook/product/product-management/product-cdf-competencies/), [Lenny's Newsletter](https://www.lennysnewsletter.com/p/product-management-career-ladders), [Sachin Rekhi](https://www.sachinrekhi.com/product-management-career-ladders-at-8-top-technology-firms)) e de vagas de PM Sênior ([Blip](https://job-boards.greenhouse.io/blip-global/jobs/4050704009), [Zenvia](https://job-boards.greenhouse.io/zenvia/jobs/5687766004), [RD Station](https://job-boards.greenhouse.io/rdstation/jobs/8162455002), [Workable](https://resources.workable.com/pt-br/gernete-de-produto-senior-descricao-do-trabalho/)). O traço que diferencia o nível sênior nessas fontes: definir e defender estratégia, validar antes de construir, medir resultados e influenciar sem autoridade formal.

Legenda: ✅ demonstrado · 🟡 parcial · ⚪ planejado

---

## Product Manager: por que e o quê

| Competência | Evidência | Situação |
|---|---|---|
| Discovery orientado a evidência | [Mapa de hipóteses](etapas/00-concepcao.md#mapa-de-hipóteses), [pesquisa e benchmark](etapas/03-validacao-do-problema.md), [entrevistas simuladas com síntese](pesquisa/entrevistas-simuladas.md) | 🟡 Método demonstrado; sem entrevistas reais |
| Personas baseadas em evidência | [Personas 3.0](persona.md) com fonte de cada afirmação, anti-persona e histórico de versões | ✅ |
| Seleção de segmento por evidência | Pivô de escritório contábil para advocacia de massa, com motivo registrado ([Etapa 3](etapas/03-validacao-do-problema.md#decisão-de-segmento-10112026)) | ✅ |
| Estratégia e posicionamento | Reposicionamento por evidência ([Etapa 3](etapas/03-validacao-do-problema.md#decisão-10112026)); [visão, princípios e PR/FAQ](etapas/04-estrategia.md) | ✅ |
| Mapeamento de oportunidades | [Opportunity Solution Tree](etapas/04-estrategia.md#2-opportunity-solution-tree) com experimentos por solução | 🟡 Oportunidades O2, O4 e O5 a validar nas entrevistas |
| Priorização defensável | Cortes de escopo ([ADR 0003](decisoes/0003-escopo-do-mvp.md)), MoSCoW, [RICE com decisões sobre o resultado](etapas/06-priorizacao.md#3-rice) | ✅ |
| Métricas e resultados | [North Star, proteção, árvore de métricas e OKRs](etapas/05-metricas.md); metas congeladas antes da avaliação | ✅ |
| Visão de negócio | [Business case](etapas/07-business-case.md): preço pelo valor, ponto de equilíbrio, mercado com dados do CNJ e do TST, mudança para licenciamento | ✅ |
| Privacidade, risco e ética de IA | LGPD, consentimento, resíduo zero, metadados | ✅ |
| Gestão de mudança de escopo | Revisões registradas em ADRs e commits | ✅ |
| Comunicação e influência | ADRs com alternativas e consequências; [mapa de stakeholders](etapas/07-business-case.md#5-stakeholders) | 🟡 Status reports pendentes |

## Arquiteto de Software: como o sistema se sustenta

| Competência | Evidência | Situação |
|---|---|---|
| Decisões arquiteturais registradas | ADRs [0001](decisoes/0001-transporte-cross-device.md), [0002](decisoes/0002-motor-de-leitura-e-extracao.md), [0005](decisoes/0005-infraestrutura-vercel-supabase-realtime.md), [0006](decisoes/0006-ocr-apple-vision.md), [0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md), [0008](decisoes/0008-armazenamento-em-producao.md) | ✅ |
| Privacidade pelo formato | Registro de auditoria sem colunas de texto livre ([ADR 0009](decisoes/0009-registro-de-auditoria-no-estudo.md)) | ⚪ Na implementação |
| Separar o que é construído do que a produção exigiria | Estudo remove tudo às 18h ([ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md)); produção guarda com chave por escritório, auditoria e retenção ([ADR 0008](decisoes/0008-armazenamento-em-producao.md)) | ✅ |
| Segurança por arquitetura | Criptografia ponta a ponta com chave no fragmento da URL; servidor cego ao conteúdo | ✅ |
| Diagramas de arquitetura | [Fluxogramas](arquitetura/fluxogramas.md): componentes, sequência, estados | ✅ |
| Desacoplamento e portabilidade | Interface de OCR trocável | 🟡 Na implementação |
| Gestão de riscos técnicos | [Duas provas de conceito](etapas/08-arquitetura-e-poc.md): uma eliminou o risco, a outra o confirmou e mudou a arquitetura ([ADR 0011](decisoes/0011-aplicacao-do-escritorio-servida-pelo-motor.md)) | ✅ |
| Modelo C4 (contexto, contêineres, componentes) | [Contexto e contêineres](arquitetura/c4.md), estudo e produção lado a lado | 🟡 Componentes na construção |

## Product Owner: o que entra em cada entrega

| Competência | Evidência | Situação |
|---|---|---|
| Histórias de usuário com critérios de aceite | [PRD](requisitos.md#6-histórias-de-usuário) | ✅ |
| Backlog refinado e ordenado | [Backlog por histórias](etapas/06-priorizacao.md#2-backlog), ligado aos requisitos e ordenado por RICE | ✅ |
| Definition of Ready e Definition of Done | [DoR e DoD](etapas/06-priorizacao.md#5-definição-de-pronto), com aceite do PO | ✅ |
| Planejamento de incrementos | [Roadmap em cinco incrementos](etapas/06-priorizacao.md#6-roadmap) | ✅ |
| Aceite de entregas | Validação de cada incremento contra critérios de aceite | ⚪ |

## Desenvolvedor: como é construído

| Competência | Evidência | Situação |
|---|---|---|
| Código de domínio testado | [`validacoes.py`](../src/extracao/validacoes.py) com testes | ✅ |
| Automação e ferramentas | [Gerador de dados sintéticos](../scripts/gerar_exemplos.py), [rotina de verificação](../scripts/limpar-e-verificar.sh) | ✅ |
| Motor de extração (OCR, classificação, extração) | — | ⚪ Etapa 10 |
| Integração em tempo real (Supabase Broadcast) | — | ⚪ Etapa 9 |
| Integração contínua (testes a cada commit) | — | ⚪ |

## Front-end: a interface

| Competência | Evidência | Situação |
|---|---|---|
| Aplicação React + TypeScript | — | ⚪ Etapas 9 e 11 |
| Câmera e criptografia no navegador | Web Crypto API, captura via câmera | ⚪ Etapa 9 |
| Responsividade (celular e desktop) | — | ⚪ |
| Acessibilidade (WCAG AA) | Requisito RNF-10 | ⚪ |
| Desempenho percebido | Estados de carregamento, feedback de envio | ⚪ |

## UX: a experiência

| Competência | Evidência | Situação |
|---|---|---|
| Pesquisa e personas | [Personas](persona.md), roteiro e [entrevistas simuladas](pesquisa/entrevistas-simuladas.md) | 🟡 Sem entrevistas reais |
| Jornada do usuário | [Fluxograma de jornada](arquitetura/fluxogramas.md#2-jornada-completa-do-usuário); [mapas de jornada](etapas/04-estrategia.md#4-mapa-de-jornada) de Juliana e Roberto | ✅ Emoções a confirmar nas entrevistas |
| Arquitetura de informação e wireframes | [Wireframes da captura](ux/captura-wireframes.md): 13 telas no Figma, fluxo das telas e [guia visual](ux/guia-visual.html) | 🟡 Tela de revisão no incremento 2 |
| Microcopy e orientação | [Textos das 13 telas](ux/captura-wireframes.md#telas) em tom próximo e simples, para quem nunca usou o sistema (HU-14) | ✅ |
| Teste de usabilidade | Roteiro e sessões com usuários | ⚪ |

## Tester (QA): a garantia

| Competência | Evidência | Situação |
|---|---|---|
| Estratégia de teste e dados de teste | Separação desenvolvimento x avaliação; [conjunto fictício com gabaritos](etapas/01-documentos-e-campos.md) | ✅ |
| Testes automatizados de regras | [`test_gabaritos.py`](../tests/test_gabaritos.py) | ✅ |
| Testes de privacidade | Resíduo zero (RNF-01 a RNF-04) | 🟡 Rotina local pronta, testes do sistema pendentes |
| Plano e casos de teste | Casos derivados dos critérios de aceite | ⚪ |
| Testes ponta a ponta | Fluxo cross-device completo | ⚪ |
| Avaliação de acurácia de IA | Relatório por campo com tamanho de amostra | ⚪ Etapa 13 |

---

## Artefatos planejados por etapa

| Etapa | Artefatos | Papéis |
|---|---|---|
| 3 | Roteiro e síntese de entrevistas | PM, UX |
| 4 | Visão, Opportunity Solution Tree, PR/FAQ, mapa de jornada | PM, UX |
| 5 | North Star, árvore de métricas, OKRs | PM |
| 6 | Backlog com RICE, histórias INVEST, DoR/DoD, roadmap | PM, PO |
| 7 | Business case e mapa de stakeholders | PM |
| 8 | Diagrama C4 e prova de conceito | Arquiteto, Dev |
| 9 | Wireframes e microcopy da captura; entrada e cross-device | UX, Front-end, Dev |
| 10 | Motor de extração | Dev, Arquiteto |
| 11 | Wireframes e tela de revisão acessível | UX, Front-end |
| 12 | Plano de testes, testes de privacidade e ponta a ponta | Tester |
| 13 | Teste de usabilidade e avaliação de acurácia | UX, Tester, PM |
| 14 | Plano de lançamento e retrospectiva | PM, PO |
