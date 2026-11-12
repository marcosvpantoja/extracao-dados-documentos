# Wireframe da tela de revisão

**Versão:** 1.0 · aprovada em 11/11/2026
**Histórias:** ver os dados ao lado da imagem (HU-03), confirmar ou recusar cada campo (HU-04), ver primeiro o que pede atenção (HU-05)
**Origem:** no teste do celular, a conferência dos dados precisou ser feita "de outra forma", sem a foto ao lado, o que é lento e sujeito a erro.

```
┌──────────────────────────────────────────────────────────────┐
│ CNH · Roberto                                       Fechar   │
├──────────────────────────────┬───────────────────────────────┤
│                              │ Mãe        IA · conferir ✓ ✗  │
│                              │ CARLA VITORIA RIBEIRO          │
│      [ foto do documento ]   │ Nome                     ✓ ✗  │
│                              │ NATALIA APARECIDA RIBEIRO      │
│                              │ CPF ✓ conferido          ✓ ✗  │
│                              │ 644.836.782-99                 │
│ [frente] [verso]   －  100% ＋│ …                              │
│                              │ [ Confirmar os demais (5) ]    │
└──────────────────────────────┴───────────────────────────────┘
```

## Decisões

| Decisão | Escolha | Alternativas descartadas |
|---|---|---|
| Layout | **Foto à esquerda, dados à direita**: o olho vai e volta na mesma altura | Foto em cima e dados embaixo (menos espaço para a foto) |
| Confirmação | **Um a um, com "Confirmar os demais"** para fechar o que não foi marcado | Só um a um (mais lento); confirmar tudo e recusar exceções (maior risco de passar erro) |
| Ordem dos campos | **Primeiro os que vieram da IA, depois os sem conferência automática, por último os conferidos** por dígito verificador ou MRZ | Ordem fixa do documento |

## Regras

- A foto tem **zoom** (100% a 400%) e abas **frente / verso** quando houver duas faces.
- **Rotação (revisto em 11/11/2026, teste do autor com foto de cabeça para baixo):** a foto aparece **já em pé**, porque o motor detecta a posição pela leitura do texto nas quatro orientações; o botão **"↻ Girar"** gira 90° para ajustes manuais.
- "Confirmar os demais" **não altera** o que já foi recusado.
- Cada decisão vai para o **registro de revisão** local (RF-22), só com tipo, campo, origem e resultado. Nenhum valor do documento entra no registro ([ADR 0004](../decisoes/0004-revisao-humana-e-ciclo-de-aprendizado.md)).
- Em telas estreitas, a foto fica em cima e os campos embaixo.
