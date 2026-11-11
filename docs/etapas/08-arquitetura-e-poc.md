# Etapa 8: Arquitetura detalhada e prova de conceito

**Status:** 🟡 Em andamento · 11/11/2026
**Papéis:** Arquiteto, Dev

A etapa tem duas partes:
- a **arquitetura em C4**, que é o desenho do sistema em níveis de zoom ([docs/arquitetura/c4.md](../arquitetura/c4.md));
- as **provas de conceito**, testes pequenos e descartáveis dos dois maiores riscos técnicos, feitos antes de construir o produto.

O código das provas fica em [`poc/`](../../poc/) e não é reaproveitado no produto.

---

## Prova de conceito 1: uma foto cifrada passa inteira pelo Supabase?

**Risco:** a documentação do Supabase limita cada mensagem do canal em tempo real (Broadcast) a **256 KB** no plano gratuito ([Realtime Limits](https://supabase.com/docs/guides/realtime/limits), [Realtime Quotas](https://supabase.com/docs/guides/realtime/quotas)). Uma foto de documento comprimida tem de 300 KB a 2 MB, então o desenho prevê dividir a foto em pedaços ([ADR 0001](../decisoes/0001-transporte-cross-device.md)).

**Como foi testado** ([`poc/01-broadcast/poc.mjs`](../../poc/01-broadcast/poc.mjs)):
- Dois clientes Supabase separados simulam o celular e o computador, num projeto gratuito na região de São Paulo.
- O conteúdo é **aleatório**: nenhum documento, real ou fictício, foi usado.
- O conteúdo é cifrado com AES-256-GCM, dividido em pedaços, convertido em texto (base64, que aumenta o tamanho em cerca de 33%) e enviado com confirmação de recebimento.
- O computador remonta os pedaços, decifra e compara a impressão digital (SHA-256) com a original.

### Resultado: envio em pedaços (11/11/2026)

| Foto | Pedaço | Tamanho de cada mensagem | Mensagens | Chegou inteira? | Tempo total |
|---|---|---|---|---|---|
| 300 KB | 64 KB | ~85 KB | 5 | ✅ | 124 ms |
| 300 KB | 128 KB | ~171 KB | 3 | ✅ | 95 ms |
| 300 KB | 180 KB | ~240 KB | 2 | ✅ | 106 ms |
| 1 MB | 64 KB | ~85 KB | 17 | ✅ | 323 ms |
| 1 MB | 128 KB | ~171 KB | 9 | ✅ | 176 ms |
| 1 MB | 180 KB | ~240 KB | 6 | ✅ | 183 ms |
| 2 MB | 64 KB | ~85 KB | 33 | ✅ | 604 ms |
| 2 MB | 128 KB | ~171 KB | 17 | ✅ | 371 ms |
| 2 MB | 180 KB | ~240 KB | 12 | ✅ | 316 ms |

Nenhum envio foi recusado, e todas as fotos chegaram idênticas à original depois de decifradas.

### Resultado: mensagem única, sem pedaços (controle)

| Tamanho da mensagem | Envio aceito? | Chegou ao outro lado? |
|---|---|---|
| 200 KB | ✅ | ✅ |
| 253 KB | ✅ | ✅ |
| 333 KB | ✅ | ✅ |
| 533 KB | ✅ | ✅ |
| 1.333 KB | ✅ | ✅ |

**Surpresa:** mensagens acima do limite documentado de 256 KB também chegaram, inclusive uma de 1,3 MB. Na prática, o limite não estava sendo aplicado neste projeto na data do teste.

### Conclusão

- **O risco foi eliminado:** uma foto de até 2 MB atravessa o canal cifrada, inteira, em menos de meio segundo.
- **A divisão em pedaços continua no desenho,** mesmo sem o limite aplicado hoje. O limite está documentado e pode passar a valer a qualquer momento, e dividir custa pouco: no pior caso, cerca de 0,3 segundo a mais numa foto de 2 MB.
- **O tempo do canal é pequeno** perto da espera de até 30 segundos pela leitura (RF-31). O gargalo do fluxo será o motor de extração, e não o envio.

### Decisão: pedaços de 128 KB

Cada pedaço tem 128 KB de conteúdo cifrado, o que dá cerca de 171 KB por mensagem depois da conversão para texto.

| Critério | Por que 128 KB |
|---|---|
| Folga até o limite documentado de 256 KB | Cerca de 85 KB, contra 16 KB do pedaço de 180 KB |
| Velocidade | Foto de 2 MB em ~0,4 s, contra ~0,3 s do pedaço maior; diferença imperceptível |
| Volume de sessões simultâneas | O plano gratuito aceita 100 mensagens por segundo por projeto. Uma foto de 2 MB gera 17 mensagens, então cerca de 5 fotos podem ser enviadas no mesmo segundo. É suficiente para as sessões do estudo; pedaços menores consumiriam essa cota mais rápido |
