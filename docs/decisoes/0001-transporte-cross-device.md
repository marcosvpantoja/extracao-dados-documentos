# 0001 — Transporte cross-device: servidor de repasse com criptografia ponta a ponta e rede local como guardrail

**Data:** 10/11/2026
**Status:** Aceita (modo rede local adiado para depois do MVP pelo [ADR 0003](0003-escopo-do-mvp.md))

## Contexto

RG e CNH são capturados pela câmera do celular e os dados aparecem no computador (fluxo cross-device). A prioridade do produto é a segurança desse trajeto: **nenhum terceiro pode enxergar o documento** e **nada pode ficar salvo** em servidor, celular ou computador.

## Decisão

**Modo principal: servidor de repasse com criptografia ponta a ponta.**

1. O computador abre uma sessão e gera uma chave de criptografia aleatória.
2. O QR code contém o identificador da sessão e a chave. A chave vai no fragmento da URL (`#...`), parte que o navegador nunca envia ao servidor.
3. O celular captura a imagem, criptografa no próprio aparelho e envia ao servidor.
4. O servidor apenas repassa os bytes criptografados ao computador, em memória, sem gravar nada. Ele não tem a chave, então não consegue ler o conteúdo.
5. O computador descriptografa e processa.

**Guardrail (fora do MVP): modo rede local.** Celular e computador no mesmo Wi-Fi, sem internet: o computador atua como servidor e o QR code aponta para o endereço dele na rede. Usado:
- quando não há internet ou o servidor de repasse está indisponível;
- nos testes com documentos reais, eliminando qualquer trânsito externo.

A mesma criptografia ponta a ponta é aplicada nos dois modos.

## Alternativas consideradas

- **Só rede local** — nenhum trânsito externo; mas exige HTTPS com certificado próprio para liberar a câmera no navegador do celular e falha em redes que isolam aparelhos (Wi-Fi corporativo ou público). Mantida como guardrail.
- **Conexão direta via WebRTC** — mesma garantia de que o servidor não vê o documento; mais complexa e, em algumas redes, depende de um intermediário. Descartada por complexidade sem ganho de segurança sobre a decisão.
- **Servidor de repasse sem criptografia ponta a ponta** — mais simples, mas o servidor teria acesso ao documento. Descartada.

## Regras de sessão e de não persistência

| Regra | Aplicação |
|---|---|
| QR code de uso único | A sessão aceita um único celular e é invalidada após o pareamento |
| Expiração curta | Sessão não pareada expira em poucos minutos |
| Encerramento nos dois lados | Ao fim da extração, a conexão é fechada e a chave descartada |
| Celular sem resíduo | Captura via câmera no navegador (não vai para a galeria); imagem só em memória; sem armazenamento local do navegador |
| Computador sem resíduo | Imagem só em memória, sem arquivo temporário, descartada ao fim da sessão |
| Servidor sem resíduo | Repasse em memória, sem banco de dados e sem log de conteúdo |
| Sem cache | Respostas com `Cache-Control: no-store` |

Cada regra vira um teste automatizado e um item verificado por `scripts/limpar-e-verificar.sh`.

## Consequências

- Dá para afirmar que **o servidor nunca vê o documento**, mesmo estando na nuvem.
- O modo principal funciona em qualquer rede, inclusive dados móveis.
- Dois modos de conexão a manter e testar.
- O modo rede local exige gerar e instalar um certificado local para HTTPS.
