# 0009 — Registro de auditoria no estudo de caso

**Data:** 10/11/2026
**Status:** Aceita · implementa no estudo uma das camadas do [ADR 0008](0008-armazenamento-em-producao.md)

## Contexto

O [ADR 0008](0008-armazenamento-em-producao.md) descreve o armazenamento em produção e não é construído no estudo. Uma das camadas dele, a trilha de auditoria, é barata de implementar e mostra na prática uma proteção de produção.

Implementar essa camada não testa as hipóteses centrais do produto (ágil e preciso) e tira tempo do motor de extração. A decisão foi tomada mesmo assim, para que o estudo demonstre uma parte do desenho de produção em funcionamento, e não só no papel.

## Decisão

### 1. Eventos registrados

Só as três ações sobre documentos que importam para a LGPD:

| Evento | Quando acontece |
|---|---|
| `documento_aberto` | Um documento é exibido na tela de revisão |
| `pacote_baixado` | O pacote com arquivos e dados é baixado (RF-26) |
| `documento_excluido` | Alguém descarta um documento manualmente |

A remoção das 18h tem registro próprio ([ADR 0007](0007-retencao-temporaria-e-purga-diaria.md)) e não entra aqui.

### 2. O que cada registro contém

| Campo | Exemplo | Observação |
|---|---|---|
| Identificador do evento | `uuid` | Aleatório |
| Horário | `2026-11-10T14:32:05Z` | UTC |
| Evento | `documento_aberto` | Um dos três da lista |
| Perfil | `assistente` | Simulado (ver item 4) |
| Estação | `uuid` | Gerado uma vez por navegador; não identifica a máquina |
| Documento | `uuid` | Código aleatório, sem relação com o conteúdo |
| Tipo de documento | `cnh` | Um dos seis tipos ou `nao_reconhecido` |

**Nunca registrado:** nome, CPF, qualquer valor extraído, imagem e **nome do arquivo**. O nome do arquivo pode conter dados: o PDF de uma NF-e costuma se chamar pela chave de acesso, que identifica o emitente ([Etapa 1](../etapas/01-documentos-e-campos.md)).

**Privacidade pelo formato:** a tabela não tem nenhuma coluna de texto livre. Todas as colunas são códigos aleatórios, horários ou valores de uma lista fechada. Sem um lugar onde caiba um nome, um dado pessoal não entra nem por engano.

### 3. Onde fica e por quanto tempo

- Tabela `auditoria` no Supabase, **só de inclusão**: as regras de acesso (Row Level Security) permitem inserir, mas não alterar nem apagar.
- **Não é apagada às 18h.** Depois da remoção diária, o código do documento deixa de levar a qualquer conteúdo, e o registro continua útil para auditar dias anteriores. Fica guardada até o fim do estudo.

### 4. Perfil simulado

O estudo não tem login. Um seletor na tela define o perfil ativo (assistente ou advogada), e esse perfil vai para o registro. **Isso não é controle de acesso:** qualquer pessoa pode escolher qualquer perfil. O objetivo é mostrar o formato do registro, e não garantir quem fez a ação. Em produção, o perfil viria do login com segundo fator ([ADR 0008](0008-armazenamento-em-producao.md)).

## Alternativas consideradas

- **Manter o ADR 0008 só como documento** — mais foco no motor de extração. Recusada: o estudo ficaria sem nenhuma camada de produção demonstrada.
- **Registrar o cadastro completo** (confirmações, recusas e sessões de captura) — conta a história inteira, mas dobra o que precisa ser projetado e testado, e se sobrepõe ao registro de revisão do [ADR 0004](0004-revisao-humana-e-ciclo-de-aprendizado.md). Recusada em favor do mínimo.
- **Apagar o registro às 18h** — mais simples, mas só permite auditar o dia corrente. Recusada.
- **Login real (Supabase Auth)** — garantiria quem fez cada ação, mas é um projeto à parte e não testa nada do produto. Recusada no estudo.

## Consequências

- O estudo demonstra uma trilha de auditoria funcionando, e o teste de privacidade ganha uma verificação nova: a tabela `auditoria` não contém dados pessoais.
- O registro mostra "quem" só como perfil simulado. Ele demonstra o formato, não a garantia de autoria.
- Dois registros convivem com propósitos diferentes: o de **revisão** (ADR 0004, local) mede a acurácia, e o de **auditoria** (este ADR, no Supabase) registra quem acessou o quê.

## Implementação (11/11/2026)

Tabela `auditoria` no Supabase ([migração](../../supabase/migrations/20261111220000_armazenamento_cifrado_e_auditoria.sql)), com os três eventos, o perfil simulado e restrições que recusam qualquer valor fora das listas. Verificado: a inclusão funciona, a tentativa de apagar não apaga nada e um texto livre no lugar do evento é recusado pelo banco.

Gatilhos na aplicação do escritório: **documento_aberto** ao abrir a revisão, **pacote_baixado** ao baixar o pacote do cliente e **documento_excluido** ao encerrar a sessão, que também apaga a cópia cifrada no Supabase.
