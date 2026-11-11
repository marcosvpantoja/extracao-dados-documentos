# 0005 — Infraestrutura: Vercel para o frontend e Supabase Realtime Broadcast como canal de repasse

**Data:** 10/11/2026
**Status:** Aceita (no estudo, a aplicação do escritório passou a ser servida pelo motor local, e a Vercel hospeda só a página de captura: [ADR 0011](0011-aplicacao-do-escritorio-servida-pelo-motor.md); a proibição de banco e Storage foi substituída pelo [ADR 0007](0007-retencao-temporaria-e-purga-diaria.md): permitidos somente com conteúdo cifrado e remoção diária)

## Contexto

O [ADR 0001](0001-transporte-cross-device.md) definiu um servidor de repasse com criptografia ponta a ponta entre celular e computador. Faltava decidir onde ele roda. A Vercel hospeda bem o frontend, mas não mantém conexões WebSocket persistentes.

## Decisão

| Peça | Onde roda |
|---|---|
| Frontend: tela de revisão (computador) e página de captura (celular) | Vercel |
| Canal de repasse celular → computador | Supabase **Realtime Broadcast** |
| Motor de leitura e extração | Computador do usuário (motor local, [ADR 0002](0002-motor-de-leitura-e-extracao.md)) |

Fluxo: o celular criptografa a imagem → publica os pedaços no canal Broadcast da sessão → o navegador do computador recebe, remonta e descriptografa → envia ao motor local → exibe o resultado na tela de revisão.

### Regras de uso do Supabase

O Supabase é usado **exclusivamente** como canal de mensagens efêmeras:

- **Proibido** usar banco de dados (tabelas), Storage, Edge Functions que persistam dados ou Realtime com persistência.
- Canal nomeado por um identificador aleatório de sessão, descartado ao fim.
- Mensagens trafegam já criptografadas; o Supabase nunca recebe a chave.
- Um teste automatizado verifica que o projeto Supabase não tem tabelas nem buckets criados por este sistema.

## Alternativas consideradas

- **Servidor de repasse próprio** (WebSocket em Fly.io, Render ou Cloudflare) — controle total, mas é mais um serviço para construir, hospedar e manter. Recusada para o MVP.
- **Repasse junto ao frontend na Vercel** — inviável sem conexões persistentes.

## Riscos a validar cedo

- **Tamanho de mensagem:** o Broadcast tem limite de tamanho por mensagem; a imagem precisa ser comprimida e enviada em pedaços. Limite exato a confirmar antes da implementação.
- **Frontend na nuvem falando com o motor local:** a página servida pela Vercel (HTTPS) precisa chamar o motor em `localhost`. Navegadores tratam `localhost` de forma diferente; testar Chrome e Safari na primeira prova de conceito.
- **Dependência de terceiro:** indisponibilidade do Supabase interrompe o cross-device. A importação de arquivo continua funcionando.

## Consequências

- Nenhum servidor próprio para construir ou manter no MVP.
- A garantia "o servidor não vê o documento" continua válida, porque o conteúdo é criptografado ponta a ponta.
- A disciplina de uso do Supabase passa a ser uma regra verificada por teste, não uma convenção.
