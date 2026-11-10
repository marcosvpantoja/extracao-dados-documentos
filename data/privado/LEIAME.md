# data/privado

Pasta **local** para documentos reais e seus gabaritos. Todo o conteúdo, exceto este arquivo, é ignorado pelo git.

Estrutura usada:

```
data/privado/
├── nfe/   PDF da nota fiscal (entrada por upload)
├── rg/    fotos do RG capturadas pelo fluxo cross-device
├── cnh/   fotos da CNH capturadas pelo fluxo cross-device
└── gabaritos/   valores corretos de cada campo (JSON), usados para medir acurácia
```

Os gabaritos também contêm dados pessoais, por isso ficam aqui e não em `data/exemplos/`.
