# Evolução do produto

Registro cronológico das decisões e mudanças do estudo de caso: **o que mudou, por quê e com base em quê**. Cada entrada aponta para o documento onde a decisão está detalhada. As medições ruins ficam ao lado das boas, porque a evolução é o que este registro quer mostrar.

O histórico completo de alterações está no [Git](https://github.com/marcosvpantoja/extracao-dados-documentos/commits/main). Este documento é a versão para leitura e apresentação.

---

## Marcos

| Data | Marco | Detalhe |
|---|---|---|
| 10/11/2026 | Concepção: leitor de NF-e, CNH e RG com classificação automática | [Etapa 0](etapas/00-concepcao.md) |
| 10/11/2026 | Separação entre documentos fictícios (desenvolvimento) e reais (avaliação), para evitar vício de dados | [Etapa 1](etapas/01-documentos-e-campos.md) |
| 10/11/2026 | **Pivô de segmento:** de escritório contábil para advocacia de consumidor de alto volume | [Etapa 3](etapas/03-validacao-do-problema.md) |
| 10/11/2026 | Regra de retenção do estudo: tudo cifrado e removido às 18h | [ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md) |
| 10/11/2026 | Estratégia: visão, árvore de oportunidades, PR/FAQ e jornadas | [Etapa 4](etapas/04-estrategia.md) |
| 10–11/11/2026 | Métricas: North Star "clientes cadastrados sem nenhuma edição" e OKRs | [Etapa 5](etapas/05-metricas.md) |
| 11/11/2026 | Priorização por RICE e roadmap "captura primeiro" | [Etapa 6](etapas/06-priorizacao.md) |
| 11/11/2026 | **Business case muda o modelo de negócio:** de venda direta para licenciamento | [Etapa 7](etapas/07-business-case.md) |
| 11/11/2026 | Provas de conceito: uma elimina um risco, a outra o confirma e muda a arquitetura | [Etapa 8](etapas/08-arquitetura-e-poc.md) |
| 11/11/2026 | Wireframes (Figma) e guia visual aprovados | [Wireframes](ux/captura-wireframes.md), [guia visual](ux/guia-visual.html) |
| 11/11/2026 | Primeiro código: captura pelo celular, escritório e motor | [Incremento 1](etapas/06-priorizacao.md#6-roadmap) |
| 11/11/2026 | Motor real: OCR + regras + IA de texto local | [Etapa 10](etapas/10-motor.md) |
| 11/11/2026 | Tela de revisão com a foto ao lado dos dados | [Wireframe da revisão](ux/revisao-wireframe.md) |
| 11/11/2026 | Telas finais em alta resolução (versão 1.1) e modo de demonstração para apresentações | [Telas finais](ux/telas-finais.md) |
| 11/11/2026 | Figma organizado por versão: página "v1.0 · Wireframes" e página "v1.1 · Produto", com nota das mudanças | [Figma](https://www.figma.com/design/SRwA8xYCHp8B8c2QtufKyv) |
| 11/11/2026 | Versão 1.2 das telas (importar dos arquivos e conferência do cliente) no projeto e no Figma, sem apagar as versões anteriores. Corrigido: a imagem da tela 3 da 1.1 tinha sido sobrescrita e foi restaurada do Git | [Telas finais](ux/telas-finais.md) |
| 11/11/2026 | Pacote do cliente (HU-15, RF-26): .zip gerado no navegador com os arquivos originais, dados em JSON e CSV (com a situação de cada campo) e LEIA-ME; nomes de arquivo neutros | [Etapa 6, roadmap](etapas/06-priorizacao.md#6-roadmap) |
| 11/11/2026 | Armazenamento cifrado no Supabase até as 18h (o cadastro sobrevive a uma atualização da página), aviso das 17h, remoção às 18h nas três camadas e auditoria no Supabase | [ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md), [ADR 0009](decisoes/0009-registro-de-auditoria-no-estudo.md) |
| 12/11/2026 | README reorganizado para apresentação: problema, forma de pensar por fase, decisões que mudaram o rumo, produto, resultados honestos e privacidade por desenho | [README](../README.md) |
| 12/11/2026 | README ampliado: como uma sessão funciona, tecnologias e APIs, custo do estudo, segurança estudo × produção e proposta de negócio | [README](../README.md) |
| 12/11/2026 | README: resultados detalhados (evolução do motor, por tipo de documento, desempenho, testes com o produto) e motivos do motor local e da escolha do Qwen 2.5 7B | [README](../README.md) |
| 12/11/2026 | README com 9 diagramas nas seções que explicam; fluxo das telas atualizado com "Importar dos arquivos" | [README](../README.md) |
| 11/11/2026 | Incremento 4, medição: conferência do cliente na tela do escritório, registro de tempos e fotos por documento, relatório dos resultados-chave (`scripts/relatorio.py`) | [Etapa 5](etapas/05-metricas.md) |

---

## Decisões revistas

Decisões que mudaram depois de tomadas. Nenhuma foi apagada: o documento original continua no repositório, com nota apontando para a revisão.

| Decisão original | Revisão | O que motivou | Onde |
|---|---|---|---|
| Público: escritório contábil | Advocacia de consumidor de alto volume | Pesquisa: NF-e e boleto já chegam por canal eletrônico; cadastro contábil é pouco frequente | [Etapa 3](etapas/03-validacao-do-problema.md) |
| Nada é salvo em lugar nenhum | Salvo cifrado e removido às 18h (estudo) | O escritório precisa dos arquivos durante o dia | [ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md) |
| Remoção às 18h como promessa do produto | Regra só do estudo; produção guarda com segurança reforçada | Correção do autor: a regra protege os testers, não descreve o produto | [ADR 0008](decisoes/0008-armazenamento-em-producao.md) |
| Entrevistas com escritórios | Entrevistas simuladas, marcadas como fictícias | Prazo do estudo | [Entrevistas simuladas](pesquisa/entrevistas-simuladas.md) |
| Link de uso único resolve tudo | Lista de documentos, "não tenho agora" e link complementar | Achado N4: o cadastro espera dias pelo último documento | [Etapa 6](etapas/06-priorizacao.md#1-documento-pendente-achado-n4) |
| Venda direta a escritórios | Licenciamento para softwares jurídicos | Business case: venda direta exigiria 14% a 28% do mercado alcançável | [Etapa 7](etapas/07-business-case.md) |
| Motor no Mac também em produção | Servidor próprio na nuvem | Business case: cada escritório precisaria de um Mac | [ADR 0010](decisoes/0010-motor-em-producao.md) |
| As duas páginas na Vercel | Aplicação do escritório servida pelo motor no Mac | Prova de conceito: o Safari bloqueia a página da Vercel chamando o Mac | [ADR 0011](decisoes/0011-aplicacao-do-escritorio-servida-pelo-motor.md) |
| Nada fica no navegador | Só a chave do dia, não exportável, fica no navegador; nenhum conteúdo | Sem a chave, atualizar a página tornaria o cadastro do dia ilegível | [ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md#implementação-11112026) |
| IA de texto só se preciso | IA de texto instalada como complemento das regras | Teste de generalização: regras sozinhas cobriam 27% dos layouts novos | [Etapa 10](etapas/10-motor.md) |

---

## Mudanças motivadas por testes com o produto

| Data | Teste | O que aconteceu | Antes | Depois | Onde |
|---|---|---|---|---|---|
| 11/11 | Prova de conceito 1 | Foto de 2 MB passou cifrada em 0,4 s | Risco de limite de tamanho | Risco eliminado; pedaços de 128 KB | [Etapa 8](etapas/08-arquitetura-e-poc.md) |
| 11/11 | Prova de conceito 2 | Safari bloqueou a chamada ao Mac | Escritório na Vercel | Escritório servido pelo motor | [ADR 0011](decisoes/0011-aplicacao-do-escritorio-servida-pelo-motor.md) |
| 11/11 | 1º teste no celular | Toda foto da tela era recusada | Celular checava escura, tremida e reflexo; só "Tirar outra" | Celular barra só o óbvio; aceita a 3ª tentativa; o motor decide | [Wireframes, tela 5](ux/captura-wireframes.md) |
| 11/11 | 1º teste no celular | Sem leitura real, o teste parava na metade | Motor simulado | Motor real (OCR + regras) | [Etapa 10](etapas/10-motor.md) |
| 11/11 | 2º teste no celular | Chave da NF-e invadia a coluna ao lado | Valores crus | Nomes legíveis, R$, datas brasileiras, chave em grupos | [Commit](https://github.com/marcosvpantoja/extracao-dados-documentos/commits/main) |
| 11/11 | 2º teste no celular | Moldura da câmera pequena | Moldura fechada no meio | Tela cheia com cantos (cartão ou folha) | [Wireframes, tela 4](ux/captura-wireframes.md) |
| 11/11 | Pedido do autor | Fotos escuras | Sem flash | Botão de flash quando o celular oferece | [Captura](../app/src/captura/camera.ts) |
| 11/11 | Teste com RG de modelo novo | Motor não reconheceu o documento | Regras de layout fixo | Regras genéricas + IA local, com checagem contra o OCR | [Etapa 10](etapas/10-motor.md) |
| 11/11 | 3º teste no celular | Conferência dos dados feita "de outra forma" | Lista de campos sem a foto | Tela de revisão com a foto ao lado, ✓/✗ por campo | [Wireframe da revisão](ux/revisao-wireframe.md) |
| 11/11 | Pedido do autor | O cliente pode já ter o documento no celular | Só fotografar ou "não tenho agora" | Também "Importar dos arquivos" (galeria ou PDF); o motor passou a ler PDF | [Wireframes, tela 3](ux/captura-wireframes.md) |
| 11/11 | Teste do autor | Foto enviada de cabeça para baixo aparecia virada na revisão | Foto mostrada como chegou | O motor detecta a posição certa (acertou 8 de 8 rotações nos testes) e a revisão mostra a foto já em pé, com botão "↻ Girar" para ajuste manual | [Wireframe da revisão](ux/revisao-wireframe.md) |
| 11/11 | Reteste do autor | Foto de cabeça para baixo apareceu em pé na revisão | — | Teste bem-sucedido | — |
| 12/11 | Teste do autor | Cadastro voltou ao atualizar a página; "Encerrar sessão" apagou a cópia cifrada | Tudo só na memória da aba | Armazenamento cifrado no Supabase até as 18h: teste bem-sucedido | [ADR 0007](decisoes/0007-retencao-temporaria-e-purga-diaria.md) |

---

## Números ao longo do tempo

### Motor de extração

| Momento | Conjunto | Tipo certo | Campos extraídos certos | Cobertura |
|---|---|---|---|---|
| Regras v1 | 18 documentos conhecidos | 18 de 18 | 100% | — |
| Regras v1 | **14 layouts novos** | **6 de 14** | 82% | **27%** |
| Regras genéricas | 14 layouts novos | 12 de 14 | 95% | 72% |
| Regras genéricas + IA | 14 layouts novos | 13 de 14 | 93% | 82% |
| Regras genéricas + IA | 32 documentos | 31 de 32 | 94% | 87% |
| + detecção da posição da foto | 32 documentos | 31 de 32 | 95% | 89% |

O 100% inicial era **vício de dados**: as regras tinham sido escritas olhando aqueles mesmos documentos. Os layouts novos mostraram o número real, e as melhorias seguintes partiram dele.

### Testes automatizados

| Momento | App | Motor e validadores |
|---|---|---|
| Incremento 1 | 16 | 3 |
| Tela de revisão | 21 | 7 |

---

## Como este registro é mantido

- Toda decisão nova ou revista ganha uma linha aqui, **no mesmo commit** da mudança.
- Decisões revistas mostram **antes, depois e o motivo**, com link para o documento original.
- Medições antigas não são apagadas quando melhoram.
