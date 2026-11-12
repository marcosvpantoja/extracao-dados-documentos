# 0007 — Retenção temporária cifrada com remoção diária às 18h

**Data:** 10/11/2026
**Status:** Aceita · **vale só para o estudo de caso**; o armazenamento em produção está no [ADR 0008](0008-armazenamento-em-producao.md) · substitui a regra "nada salvo no servidor" do [ADR 0001](0001-transporte-cross-device.md) e a proibição de banco e Storage do [ADR 0005](0005-infraestrutura-vercel-supabase-realtime.md)

## Contexto

No segmento de advocacia de alto volume ([Etapa 3](../etapas/03-validacao-do-problema.md)), o escritório precisa dos dados e das fotos ao longo do dia: o cadastro pode ser concluído numa estação e consultado depois, e os arquivos precisam ser baixados para instruir a petição. A regra anterior, de nada salvo em lugar nenhum, impedia esse uso.

A regra abaixo é do **estudo de caso**, e não do produto. Ela protege os documentos das pessoas que testam o sistema: o estudo precisa funcionar de ponta a ponta sem acumular dados pessoais. Em produção, o escritório guarda os documentos por todo o processo ([ADR 0008](0008-armazenamento-em-producao.md)).

Regra do estudo:

- Dados extraídos e fotos **podem ser salvos**, inclusive na nuvem.
- **Nada pode ficar disponível ou salvo na nuvem por 24 horas.**
- **Às 18h (horário de Brasília) de cada dia, todos os dados são removidos.**

## Decisão

### 1. Armazenamento sempre cifrado

| O que | Onde | Como |
|---|---|---|
| Fotos e PDFs | Supabase Storage | Cifrados no computador do escritório (AES-GCM) antes do envio |
| Dados extraídos e revisões | Tabela no Supabase | Conteúdo cifrado; só metadados técnicos em aberto (id, horário de criação, tipo de documento) |
| Chave do dia | Navegador do computador do escritório | Gerada no primeiro uso do dia, não exportável (Web Crypto), nunca enviada ao servidor |

O servidor continua **sem enxergar o conteúdo**: guarda apenas dados cifrados.

O fluxo cross-device não muda: o celular cifra com a chave da sessão (QR code), o computador descriptografa, processa localmente e **recifra com a chave do dia** antes de salvar.

### 2. Remoção às 18h com três camadas independentes

| Camada | Mecanismo | Protege contra |
|---|---|---|
| **Destruição da chave** (*crypto-shredding*) | Às 18h o computador apaga a chave do dia | Qualquer cópia remanescente, inclusive backups do provedor, fica ilegível |
| **Remoção no servidor** | Tarefa agendada no banco (pg_cron) às 18h00 de Brasília (21h00 UTC) apaga linhas da tabela e objetos do Storage | Computador desligado ou fechado às 18h |
| **Limite de 24h** | Mesma tarefa, executada de hora em hora, apaga qualquer item com mais de 24h | Falha pontual da execução das 18h |

Cada execução grava um registro **anônimo**: horário, quantidade de itens removidos e resultado.

### 3. Aviso antes da remoção

A partir das 17h, a tela mostra quanto tempo falta para a remoção e lembra de baixar o pacote dos cadastros ainda não baixados. A remoção acontece às 18h sem exceção.

### 4. Pacote baixado é responsabilidade do escritório

O pacote baixado (arquivos e dados confirmados) sai do sistema e fica sob responsabilidade do escritório, como controlador dos dados (LGPD). A regra das 18h vale para tudo o que o **sistema** guarda.

## Alternativas consideradas

- **Nuvem sem criptografia** — mais simples, mas o provedor e os backups enxergariam documentos pessoais, e backups podem durar mais de 24h, violando a regra. Recusada.
- **Só no computador** — nada na nuvem, mas impede consultar o cadastro de outra estação e cria cópias locais difíceis de verificar. Recusada.
- **Remoção por idade (24h corridas por item)** — evita perder um cadastro feito perto das 18h, mas a regra fica mais difícil de explicar e de verificar. Recusada em favor de um horário único com aviso.

## Consequências

- O estudo pode afirmar: **o servidor nunca vê o conteúdo, e nada sobrevive às 18h**, nem em backups, porque a chave deixa de existir.
- Como a chave do dia fica num único navegador, outras estações não leem os dados no estudo de caso. Compartilhar a chave entre estações exige uma decisão futura.
- Um cadastro iniciado perto das 18h pode ser perdido se não for baixado a tempo; o aviso reduz, mas não elimina, esse risco.
- Os testes de privacidade passam a verificar: tabela e Storage vazios após as 18h, nenhum item com mais de 24h e chave do dia inexistente após as 18h.

## Implementação (11/11/2026)

Implementado com dois ajustes, decididos ao construir:

| Previsto | Implementado | Motivo |
|---|---|---|
| Fotos no Supabase Storage | Fotos **dentro da linha cifrada** da tabela `cadastros_cifrados` | O Storage não permite apagar arquivos por SQL; com tudo na tabela, a remoção das 18h e o limite de 24h ficam inteiramente no banco ([migração](../../supabase/migrations/20261111220000_armazenamento_cifrado_e_auditoria.sql)) |
| Chave do dia só no navegador, sem dizer onde | Chave **não exportável guardada no IndexedDB**, apagada às 18h | Sem guardar a chave, uma atualização da página tornaria ilegíveis os dados do dia. Decisão do autor: a regra passa de "nada no navegador" para "**nenhum conteúdo** no navegador" |

Verificado no projeto Supabase: as duas tarefas agendadas existem (`remocao-18h`, às 21h UTC, e `limite-24h`, de hora em hora), e cada execução grava o total removido em `registro_remocao`.
