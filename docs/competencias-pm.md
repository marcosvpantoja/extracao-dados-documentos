# Competências de Product Management demonstradas

Este estudo de caso é estruturado para evidenciar as competências esperadas de um **Product Manager Sênior**. A lista foi consolidada a partir de frameworks públicos de carreira em produto ([ProductLed](https://www.productledalliance.com/product-management-skills-framework/), [GitLab](https://handbook.gitlab.com/handbook/product/product-management/product-cdf-competencies/), [Lenny's Newsletter](https://www.lennysnewsletter.com/p/product-management-career-ladders), [Sachin Rekhi](https://www.sachinrekhi.com/product-management-career-ladders-at-8-top-technology-firms)) e de vagas de PM Sênior no Brasil e no exterior ([Blip](https://job-boards.greenhouse.io/blip-global/jobs/4050704009), [Zenvia](https://job-boards.greenhouse.io/zenvia/jobs/5687766004), [RD Station](https://job-boards.greenhouse.io/rdstation/jobs/8162455002), [Workable](https://resources.workable.com/pt-br/gernete-de-produto-senior-descricao-do-trabalho/)).

O que diferencia o nível sênior nessas fontes: **definir e defender estratégia**, em vez de apenas executar entregas; **validar antes de construir**; **medir resultados**, não funcionalidades entregues; e **influenciar** pessoas de diferentes áreas sem autoridade formal.

## Matriz de competências

| # | Competência | O que se espera no nível sênior | Evidência neste projeto | Situação |
|---|---|---|---|---|
| 1 | **Discovery orientado a evidência** | Validar problema e oportunidade com pesquisa, entrevistas e benchmark antes de comprometer o time | [Mapa de hipóteses](etapas/00-concepcao.md#mapa-de-hipóteses), [validação indireta e benchmark](etapas/03-validacao-do-problema.md) | 🟡 Entrevistas pendentes |
| 2 | **Estratégia e visão de produto** | Visão clara, posicionamento frente a concorrentes, apostas explícitas | Tese do MVP ([ADR 0003](decisoes/0003-escopo-do-mvp.md)); posicionamento por privacidade e porte ([Etapa 3](etapas/03-validacao-do-problema.md)) | 🟡 Visão e PR/FAQ pendentes |
| 3 | **Mapeamento de oportunidades e ideias** | Ligar resultados desejados a oportunidades e soluções, comparando alternativas | Opportunity Solution Tree | ⚪ Pendente |
| 4 | **Priorização defensável** | Escolher e cortar com critérios explícitos; defender a prioridade para stakeholders | Cortes de escopo ([ADR 0003](decisoes/0003-escopo-do-mvp.md)), MoSCoW no [PRD](requisitos.md) | 🟡 Backlog com RICE pendente |
| 5 | **Métricas e resultados** | North Star, KPIs e OKRs com linha de base e metas; medir resultado, não entrega | Métricas definidas no [PRD](requisitos.md#9-métricas-de-sucesso); desenho de avaliação sem vício ([Etapa 1](etapas/01-documentos-e-campos.md)) | 🟡 Metas e OKRs pendentes |
| 6 | **Requisitos e execução** | Requisitos claros, critérios de aceite, riscos mapeados, entrega incremental | [PRD](requisitos.md), [fluxogramas](arquitetura/fluxogramas.md), ordem de construção | ✅ |
| 7 | **Profundidade técnica e IA** | Entender trade-offs técnicos o suficiente para decidir com engenharia; avaliar sistemas de IA com rigor | ADRs [0001](decisoes/0001-transporte-cross-device.md), [0002](decisoes/0002-motor-de-leitura-e-extracao.md), [0005](decisoes/0005-infraestrutura-vercel-supabase-realtime.md), [0006](decisoes/0006-ocr-apple-vision.md); separação desenvolvimento x avaliação; validadores | ✅ |
| 8 | **Privacidade, risco e ética** | Antecipar riscos regulatórios e de confiança e transformá-los em requisito | LGPD, consentimento de testers, resíduo zero verificável, metadados no nome de arquivo | ✅ |
| 9 | **Visão de negócio** | Custo, modelo de receita, tamanho de mercado, go-to-market | Custo de desenvolvimento x operação ([ADR 0002](decisoes/0002-motor-de-leitura-e-extracao.md)) | ⚪ Business case pendente |
| 10 | **Comunicação e influência** | Narrativa escrita clara; alinhar do C-level ao time técnico; comunicar decisões e progresso | ADRs com alternativas e consequências; documentação por etapa | 🟡 Mapa de stakeholders e status reports pendentes |
| 11 | **Gestão de mudança de escopo** | Absorver novas informações e requisitos sem perder a tese | Histórico de revisões de escopo registrado em commits e ADRs | ✅ |
| 12 | **Aprendizado contínuo e retrospectiva** | Fechar ciclos: medir, aprender, ajustar | Ciclo de aprendizado ([ADR 0004](decisoes/0004-revisao-humana-e-ciclo-de-aprendizado.md)) | ⚪ Retrospectiva pendente |

## Artefatos planejados para fechar as lacunas

| Competência | Artefato | Etapa |
|---|---|---|
| 1 | Roteiro e síntese de entrevistas | 3 |
| 2, 3 | Visão de produto, Opportunity Solution Tree e PR/FAQ (press release do futuro + perguntas frequentes) | 4 |
| 5 | North Star, árvore de métricas e OKRs | 5 |
| 4 | Backlog priorizado com RICE e roadmap de resultados (Agora / Próximo / Depois) | 6 |
| 9 | Business case: custos, modelo de receita hipotético, mercado endereçável, go-to-market | 7 |
| 10 | Mapa de stakeholders e status report ao fim de cada etapa | Contínuo |
| 12 | Plano de lançamento, resultados da avaliação e retrospectiva | 13–14 |
