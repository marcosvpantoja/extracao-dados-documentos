# 0011 — Aplicação do escritório servida pelo motor local

**Data:** 11/11/2026
**Status:** Aceita · vale só para o estudo de caso · altera parte do [ADR 0005](0005-infraestrutura-vercel-supabase-realtime.md)

## Contexto

Pelo desenho original ([ADR 0005](0005-infraestrutura-vercel-supabase-realtime.md)), a Vercel hospedaria as duas páginas: a de captura, usada no celular, e a aplicação do escritório, usada no computador. A aplicação do escritório chamaria o motor de extração no Mac pelo endereço `localhost`.

A prova de conceito 2 ([Etapa 8](../etapas/08-arquitetura-e-poc.md#prova-de-conceito-2-a-página-na-internet-consegue-falar-com-o-motor-no-mac)) testou essa chamada:

| Navegador | Página na Vercel chamando o motor no Mac |
|---|---|
| Chrome 156 | ✅ Funciona, depois que o usuário autoriza o acesso à rede local num aviso do navegador |
| Safari 26 | ❌ Bloqueia sempre, sem aviso: uma página segura (`https`) não pode chamar um endereço não seguro (`http`) |

O requisito de compatibilidade (RNF-09) exige Chrome e Safari no computador.

## Decisão

No estudo, **a aplicação do escritório é servida pelo próprio motor**, em `http://localhost`. A página e o motor ficam no mesmo endereço, e não há chamada entre um site da internet e o computador.

| Página | Onde fica |
|---|---|
| Página de captura (celular) | Vercel, como antes |
| Aplicação do escritório (computador) | Servida pelo motor, no Mac |

A prova de conceito 2b confirmou, no Chrome e no Safari:
- o navegador considera `localhost` um endereço seguro, então a criptografia do navegador (Web Crypto, AES-GCM) funciona;
- a aplicação envia a imagem ao motor sem bloqueio;
- a aplicação se conecta a serviços na internet por WebSocket, como o Supabase.

## Alternativas consideradas

- **Certificado local para o motor responder com conexão segura** — manteria as duas páginas na Vercel, mas exige instalar um certificado nas configurações de segurança do Mac. Recusada pela complexidade de instalação.
- **Usar só o Chrome no estudo** — mais simples, mas descumpre o requisito de compatibilidade (RNF-09) e depende de o usuário aceitar o aviso de rede local. Recusada.

## Consequências

- **O aviso de rede local do Chrome deixa de aparecer**, porque a aplicação não é mais um site da internet chamando o computador.
- **A aplicação do escritório só abre no Mac onde o motor roda.** Para o estudo isso não muda nada, já que o motor era local de qualquer forma.
- **Em produção o problema não existe:** o motor fica num servidor na nuvem, com conexão segura ([ADR 0010](0010-motor-em-producao.md)).
