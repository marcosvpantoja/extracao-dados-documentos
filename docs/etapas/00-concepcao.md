# Etapa 0 — Concepção e discovery

**Período:** 10/11/2026
**Status:** ✅ Concluída (escopo revisado em 10/11/2026, ver [ADR 0003](../decisoes/0003-escopo-do-mvp.md))

## Natureza do projeto

Estudo de caso, sem cliente real, que documenta a construção do produto de ponta a ponta sob a ótica de Product Management: discovery, requisitos, priorização, métricas, decisões técnicas, riscos de IA e roadmap. Personas e cenários são **hipóteses explícitas**, validadas com pesquisa pública e documentos de exemplo, não com dados de clientes.

> Convenção: tudo marcado com 🧪 é hipótese ainda não validada. Quando for validada (ou descartada), a marca muda para ✅ ou ❌ com a fonte da evidência.

## Definição do produto ✅

> **O usuário importa um arquivo no computador ou fotografa o documento pelo celular, sem informar o tipo. O sistema identifica sozinho o tipo, extrai os dados e mostra os campos na tela, sem guardar o documento em lugar nenhum.**

Requisitos centrais:

1. **Tipos suportados no MVP:** Nota Fiscal (NF-e / DANFE), boleto bancário, fatura de serviço e documentos pessoais (CNH, RG antigo e CIN).
2. **Classificação automática:** o usuário não escolhe o tipo; o sistema detecta.
3. **Saída em tela:** os dados extraídos aparecem organizados para o usuário ler e conferir.
4. **Dois canais de entrada, para qualquer tipo:** importação de arquivo no computador ou captura pelo celular (fluxo cross-device: o computador mostra um QR code, o celular fotografa e os dados voltam para a tela do computador).
5. **Extensível:** a arquitetura deve permitir incluir novos tipos de documento sem reescrever o sistema.
6. **Rápido o suficiente:** o resultado completo aparece na tela do computador sem fila, dentro de uma meta de tempo definida na etapa de métricas.
7. **Sem resíduo:** nenhum documento ou dado extraído fica salvo no celular, no computador ou no servidor ([ADR 0001](../decisoes/0001-transporte-cross-device.md)).
8. **Revisão humana:** uma tela mostra os dados extraídos para o usuário confirmar ou recusar cada campo; as respostas medem a acurácia e alimentam a melhoria do sistema ([ADR 0004](../decisoes/0004-revisao-humana-e-ciclo-de-aprendizado.md)).

Decisão complementar:
- **RG:** suportar **ambos**, o RG antigo (modelos estaduais) e a nova Carteira de Identidade Nacional (CIN).

## Cenário de trabalho 🧪

Um **escritório de contabilidade de pequeno porte**, no momento em que todos os tipos de documento aparecem juntos: o **cadastro de um cliente novo** (abertura de empresa ou troca de contador). O cliente vai ao escritório, ou faz uma chamada de vídeo, e entrega de uma vez:

- RG ou CNH dos sócios, fotografados na hora;
- comprovante de endereço (fatura de serviço);
- as últimas notas fiscais e boletos em aberto, recebidos em PDF.

Depois do cadastro, o fluxo mensal continua com documentos misturados chegando pelos mesmos canais (e-mail, WhatsApp, pasta compartilhada):

- **Documentos fiscais e financeiros:** notas fiscais de compra e venda e boletos a pagar dos clientes, que precisam ser lançados no fechamento.
- **Documentos pessoais:** RG e CNH de sócios e responsáveis, usados em cadastros, abertura de empresa e alterações contratuais.

Hoje alguém abre cada arquivo, descobre o que é e digita os dados à mão.

## Persona 🧪 (versão 1)

> **Substituída** pela [persona 2.0](../persona.md), construída com a pesquisa da [Etapa 3](03-validacao-do-problema.md) e com foco em agilidade no cadastro de cliente. Mantida aqui como registro da evolução.


**Ana, assistente contábil**
- Faz o cadastro de clientes novos e o lançamento mensal de documentos.
- Recebe arquivos de tipos diferentes, misturados, sem padrão de nome; documentos pessoais muitas vezes só existem em papel, na mão do cliente.
- Precisa primeiro **entender o que é cada documento** e depois **transcrever os campos**.
- **Dor principal:** tempo gasto em triagem e digitação, e retrabalho causado por erro de digitação.
- **O que ela precisa:** fotografar ou soltar o arquivo, ver os dados prontos e confiar neles sem conferir campo por campo, e garantir ao cliente que o documento dele não ficou guardado em lugar nenhum.

## Problema em uma frase 🧪 (versão 1)

> **Revisado** no [PRD](../requisitos.md#2-problema) após a Etapa 3.


> Escritórios que lidam com notas fiscais, boletos e documentos pessoais misturados perdem tempo identificando cada arquivo e digitando seus dados à mão, num processo lento e propenso a erro.

## Fluxo do usuário (cross-device)

```
COMPUTADOR                                   CELULAR
1. Abre o sistema e clica em "Novo documento"
2. Tela mostra um QR code (sessão única) ──► 3. Escaneia o QR com a câmera
                                             4. Abre página web de captura (sem instalar app)
                                             5. Fotografa o documento
                                             6. Envia a imagem
7. Computador recebe a imagem na hora ◄──────┘
8. Sistema detecta o tipo  ──►  "NF-e" | "Boleto" | "Fatura" | "CNH" | "RG" | "Não reconhecido"
9. Sistema extrai os campos daquele tipo
10. Tela do computador mostra: tipo detectado + campos extraídos + confiança
```

O nome técnico desse padrão é **fluxo cross-device** (ou *mobile handoff*): o mesmo mecanismo de pareamento por QR code do WhatsApp Web, aplicado à captura de documentos, como fazem plataformas de verificação de identidade (KYC).

A importação de arquivo no computador segue os passos 8 a 10 diretamente. Qualquer tipo pode entrar por qualquer canal: o canal só muda a origem do arquivo.

## Campos-alvo

Catálogo completo por tipo na [Etapa 1](01-documentos-e-campos.md#campos-alvo).

## Mapa de hipóteses

| # | Hipótese | Risco se estiver errada | Como validar |
|---|---|---|---|
| H1 🧪 | Triagem + digitação de documentos consome tempo significativo em escritórios pequenos | Problema pequeno demais para justificar o produto | Pesquisa pública (fóruns de contadores, conteúdos do setor) |
| H2 🧪 | É possível distinguir NF-e, boleto, CNH e RG automaticamente com alta acurácia | Usuário teria que escolher o tipo, quebrando o requisito central | Teste com conjunto de exemplos na etapa de classificação |
| H3 🧪 | Fotos de celular (RG/CNH) são lidas com qualidade suficiente | Extração falha justamente nos documentos pessoais | Testar com fotos em condições variadas (luz, ângulo, desfoque) |
| H6 🧪 | O usuário prefere fotografar pelo celular a usar scanner ou upload | Esforço no fluxo cross-device não se paga | Teste de usabilidade com o protótipo |
| H7 🧪 | O processamento local é rápido o suficiente para uso no atendimento | Usuário espera demais com o cliente à frente | Medir tempo até o resultado no hardware de referência |
| H4 🧪 | O usuário confia no resultado se a tela indicar a confiança por campo | Se precisar conferir tudo, o ganho de tempo some | Protótipo da tela de resultado |
| H5 🧪 | Existem lacunas nas soluções atuais para escritório pequeno | Mercado já resolvido | Benchmark de concorrentes |

## Riscos e restrições

- **LGPD:** RG e CNH contêm dados pessoais. Nenhum documento ou dado extraído é salvo em base de dados online; tudo existe só durante a sessão, e apenas métricas anônimas de avaliação ficam em arquivo local (ver Etapa 1).
- **Repositório público:** nenhum documento real entra no repositório. Testes usam apenas documentos fictícios ou modelos públicos.
- **RG tem vários modelos:** o RG antigo varia por estado e há a nova CIN. Decidido suportar ambos, o que aumenta o esforço de classificação e extração; será o tipo mais trabalhoso do MVP.
- **Segurança do pareamento:** o QR code deve gerar uma sessão única, de curta duração e de uso único, para que ninguém envie documentos para a sessão de outra pessoa.
- **Velocidade x privacidade:** processamento local protege os dados, mas tende a ser mais lento que IA na nuvem ([ADR 0002](../decisoes/0002-motor-de-leitura-e-extracao.md)).
- **Qualidade da foto:** a página de captura no celular deve orientar enquadramento, luz e foco, porque a qualidade da imagem limita a acurácia.
- **CNH física x CNH digital (PDF):** layouts diferentes; ambos podem chegar.
- **Boleto tem validação matemática:** a linha digitável tem dígitos verificadores, o que permite checar automaticamente se a extração está correta. Pode servir de referência de confiança.

## Fora de escopo (MVP)

- Seleção manual do tipo de documento (contraria o requisito central).
- Outros documentos (contratos, comprovantes de pagamento, NFS-e).
- Modo rede local (offline), campos exibidos em streaming e captura automática pela câmera: no backlog ([ADR 0003](../decisoes/0003-escopo-do-mvp.md)).
- Integração com sistemas contábeis e exportação automática.
- Armazenamento de histórico de documentos.
- Documentos manuscritos.

## Critérios de sucesso

- **Acurácia da classificação:** % de documentos com tipo detectado corretamente.
- **Acurácia por campo:** % de campos extraídos corretamente, por tipo de documento.
- **Tempo até o resultado completo**, medido desde a captura ou importação.
- **Resíduo zero:** nenhum documento ou dado encontrado nos dispositivos e no servidor após cada sessão (verificação automatizada).

As metas numéricas serão definidas na etapa de métricas, depois de medir uma linha de base.

## Próxima etapa

[Etapa 1 — Documentos de exemplo e campos-alvo](01-documentos-e-campos.md): montar o conjunto de documentos fictícios e fechar a lista de campos de cada tipo.
