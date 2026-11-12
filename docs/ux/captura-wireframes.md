# Wireframes e textos da página de captura

**Versão:** 1.0 · aprovada em 11/11/2026
**Etapa:** [9, captura pelo celular](../../README.md#roteiro) · **Papéis:** UX, Front-end
**Base:** [jornada do Roberto com o produto](../etapas/04-estrategia.md#roberto-com-o-produto-passo-a-passo)
**Figma:** [Extração de documentos · Wireframes da captura](https://www.figma.com/design/SRwA8xYCHp8B8c2QtufKyv), com as 13 telas em formato de celular (360 × 720) e os componentes reutilizáveis (botões, rodapé de privacidade, espaço para imagem)
**Guia visual:** [cores, tipografia, espaçamentos e componentes](guia-visual.html) (abra o arquivo no navegador)

## Decisões de base

| Decisão | Escolha | Motivo |
|---|---|---|
| Estrutura | **Passo a passo:** um documento por tela, com indicador "2 de 3" | Menos escolhas para quem tem pouca familiaridade com tecnologia |
| Câmera | **Dentro da página**, com moldura e dica de luz ao vivo | Orienta a foto antes de ela ser tirada (RF-05) |
| Tom | **Próximo e simples:** "você", frases curtas, sem termos jurídicos ou técnicos | O Roberto não conhece o sistema e está sozinho (HU-14) |

**Risco da câmera dentro da página:** ela depende da permissão de câmera do navegador. Se o Roberto negar, a página não tem outra forma de fotografar. A tela 2b explica como liberar a permissão.

## Fluxo das telas

```mermaid
%%{init: {"theme": "base", "themeVariables": {"lineColor": "#8a8a8a", "primaryTextColor": "#111111", "edgeLabelBackground": "#f3f4f6", "fontSize": "15px"}}}%%
flowchart TD
    LINK([Roberto toca no link<br/>recebido pelo WhatsApp]) --> VAL{Link válido?}
    VAL -->|Não| E1["E1 · Este link não vale mais"]
    VAL -->|Sim| T1["1 · Abertura<br/>lista de documentos, tempo<br/>e quem vê os documentos"]
    T1 --> T2["2 · Precisamos usar sua câmera"]
    T2 --> PERM{Permitiu a câmera?}
    PERM -->|Não| T2B["2b · Como liberar a câmera"]
    T2B -->|Tentar de novo| PERM
    PERM -->|Sim| T3["3 · Documento N de M"]

    T3 -->|Não tenho agora| PEND["Item marcado como pendente"]
    T3 -->|Fotografar| T4["4 · Câmera com moldura<br/>e dica de luz ao vivo"]
    T4 --> QUAL{Foto boa?<br/>luz, nitidez, enquadramento}
    QUAL -->|Não| T5["5 · Aviso de qualidade<br/>só Tirar outra"]
    T5 --> T4
    QUAL -->|Sim| VER{Documento tem verso<br/>e falta fotografá-lo?}
    VER -->|Sim| T6["6 · Agora o verso"]
    T6 --> T4
    VER -->|Não| T7["7 · Lendo seu documento…<br/>até 30 s"]

    T7 --> LEU{Resultado da leitura}
    LEU -->|Não deu para ler| T7B["7b · Vamos tentar de novo<br/>com o motivo"]
    T7B --> T4
    LEU -->|Leu| T8["8 · Enviado"]
    LEU -->|Passou de 30 s| E2["E2 · Recebemos sua foto<br/>o escritório avisa se precisar"]

    T8 --> MAIS{Falta algum documento?}
    E2 --> MAIS
    PEND --> MAIS
    MAIS -->|Sim| T3
    MAIS -->|Não| T9(["9 · Tudo enviado<br/>com os pendentes listados"])

    classDef tela fill:#bfdbfe,stroke:#1d4ed8,color:#111
    classDef excecao fill:#fee2e2,stroke:#b91c1c,color:#111
    classDef decisao fill:#fde68a,stroke:#b45309,color:#111
    class T1,T2,T3,T4,T5,T6,T7,T7B,T8 tela
    class E1,E2,T2B excecao
    class VAL,PERM,QUAL,VER,LEU,MAIS decisao
    classDef borda fill:#e5e7eb,stroke:#6b7280,color:#111
    class LINK,PEND,T9 borda
```

🖼️ [Ver como imagem](img/captura-wireframes-01-fluxo-das-telas.png)

**Legenda:** 🟦 tela · 🟥 exceção · 🟨 decisão do sistema · ⬜ início, fim e pendência

---

## Telas

Visão geral, na ordem da jornada. Os detalhes de cada tela estão nas seções abaixo.

| | | | |
|---|---|---|---|
| <img src="img/telas/01-abertura.png" alt="1 · Abertura" width="160"><br>**1 · Abertura** | <img src="img/telas/02-permissao-da-camera.png" alt="2 · Permissão da câmera" width="160"><br>**2 · Permissão da câmera** | <img src="img/telas/02b-camera-bloqueada.png" alt="2b · Câmera negada" width="160"><br>**2b · Câmera negada** | <img src="img/telas/03-documento-n-de-m.png" alt="3 · Documento N de M" width="160"><br>**3 · Documento N de M** |
| <img src="img/telas/04-camera.png" alt="4 · Câmera" width="160"><br>**4 · Câmera** | <img src="img/telas/05-aviso-de-qualidade.png" alt="5 · Aviso de qualidade" width="160"><br>**5 · Aviso de qualidade** | <img src="img/telas/06-verso.png" alt="6 · Verso" width="160"><br>**6 · Verso** | <img src="img/telas/07-lendo-seu-documento.png" alt="7 · Lendo seu documento" width="160"><br>**7 · Lendo seu documento** |
| <img src="img/telas/07b-vamos-tentar-de-novo.png" alt="7b · Vamos tentar de novo" width="160"><br>**7b · Vamos tentar de novo** | <img src="img/telas/08-enviado.png" alt="8 · Enviado" width="160"><br>**8 · Enviado** | <img src="img/telas/09-tudo-enviado.png" alt="9 · Tudo enviado" width="160"><br>**9 · Tudo enviado** | <img src="img/telas/e1-link-expirado.png" alt="E1 · Link expirado ou já usado" width="160"><br>**E1 · Link expirado ou já usado** |
| <img src="img/telas/e2-leitura-demorada.png" alt="E2 · Tempo de leitura esgotado" width="160"><br>**E2 · Tempo de leitura esgotado** |  |  |  |

### 1 · Abertura

<img src="img/telas/01-abertura.png" alt="Tela 1 · Abertura" width="280">

- A lista vem da que a assistente montou ao gerar o link (RF-33).
- **"Leva uns 3 minutos" é uma promessa** e precisa ser conferida nas sessões com testers (tempo de captura por sessão). Se o tempo medido for maior, o texto muda.
- "Saiba mais" abre um texto curto sobre quem acessa e por quanto tempo (HU-06).

### 2 · Permissão da câmera

<img src="img/telas/02-permissao-da-camera.png" alt="Tela 2 · Permissão da câmera" width="280">

- Explica **antes** do aviso do navegador, para o Roberto não negar por susto.

### 2b · Câmera negada

<img src="img/telas/02b-camera-bloqueada.png" alt="Tela 2b · Câmera negada" width="280">

### 3 · Documento N de M

<img src="img/telas/03-documento-n-de-m.png" alt="Tela 3 · Documento N de M" width="280">

- "Não tenho agora" marca o item como pendente e passa ao próximo (RF-34).

### 4 · Câmera

<img src="img/telas/04-camera.png" alt="Tela 4 · Câmera" width="280">

- Dicas ao vivo, uma por vez: "Procure mais luz" · "Aproxime o documento" · "Segure firme" · "Pronto, pode fotografar".

### 5 · Aviso de qualidade

<img src="img/telas/05-aviso-de-qualidade.png" alt="Tela 5 · Aviso de qualidade" width="280">

- Motivos possíveis: escura · tremida · cortada · com reflexo.
- Quando a foto está boa, a tela é pulada.
- **Limite de 3 tentativas** (revisto no primeiro teste no celular, 11/11/2026): na terceira foto recusada seguida, a última segue para o motor, que ainda pode pedir outra (tela 7b). Antes, só existia "Tirar outra", e o teste mostrou o risco de o cliente ficar preso.
- **O celular barra só o óbvio:** foto muito escura ou muito tremida. O reflexo deixou de bloquear, porque a regra recusava papel branco bem iluminado e fotos de tela. Quem decide se dá para ler é o motor (RF-31).

### 6 · Verso

<img src="img/telas/06-verso.png" alt="Tela 6 · Verso" width="280">

- Só para RG, CNH física e CIN (RF-06).

### 7 · Lendo seu documento

<img src="img/telas/07-lendo-seu-documento.png" alt="Tela 7 · Lendo seu documento" width="280">

- Espera de até 30 s (RF-31). "Mantenha o documento por perto" prepara para uma possível nova foto.

### 7b · Vamos tentar de novo

<img src="img/telas/07b-vamos-tentar-de-novo.png" alt="Tela 7b · Vamos tentar de novo" width="280">

- O motivo vem do motor, sem nenhum dado do documento: só o que faltou ler e a causa provável.

### 8 · Enviado

<img src="img/telas/08-enviado.png" alt="Tela 8 · Enviado" width="280">

### 9 · Tudo enviado

<img src="img/telas/09-tudo-enviado.png" alt="Tela 9 · Tudo enviado" width="280">

### E1 · Link expirado ou já usado

<img src="img/telas/e1-link-expirado.png" alt="Tela E1 · Link expirado ou já usado" width="280">

### E2 · Tempo de leitura esgotado

<img src="img/telas/e2-leitura-demorada.png" alt="Tela E2 · Tempo de leitura esgotado" width="280">

---

## Acessibilidade e responsividade

- Botões de pelo menos 48 px de altura, ocupando a largura da tela.
- Contraste AA em todos os textos; as dicas da câmera ficam sobre uma faixa escura, e não direto sobre a imagem.
- Toda mudança de estado ("Lendo…", "Enviado") é anunciada aos leitores de tela.
- Funciona com uma mão: as ações principais ficam na metade de baixo da tela.
