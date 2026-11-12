# Instruções para assistentes de IA

Este repositório é um estudo de caso de produto: cadastro por documentos com captura pelo celular, leitura automática e revisão humana. Visão geral no [README](README.md).

## Regras que não podem ser quebradas

- **Nunca leia, envie ou peça documentos reais** (RG, CNH, notas, faturas de pessoas reais). Use só os fictícios de `data/exemplos/`. A pasta `data/privado/` é ignorada pelo Git e não deve ser aberta.
- **Nunca coloque chaves ou senhas em arquivos versionados.** Elas ficam em `.env.local` e `app/.env.*.local`, que o Git ignora.
- **Todo trabalho novo vai numa branch e termina num pull request** com a lista da definição de pronto (`.github/pull_request_template.md`). Não faça commit direto na `main`.
- **Toda decisão ou mudança deixa rastro:** antes, depois e por quê, com uma linha em `docs/evolucao.md` no mesmo commit.
- Textos para o usuário e documentação: **português do Brasil**.

## Instalar e rodar o teste

O motor usa o **Apple Vision** (OCR do macOS): a leitura de documentos **só funciona em macOS**. Em outros sistemas, rode só os testes da aplicação e o modo de demonstração.

### 1. Pré-requisitos

- macOS (para o OCR), [Homebrew](https://brew.sh), Node 22 ou mais novo, Python 3.9 ou mais novo
- Opcional, para a IA local: `brew install ollama` e `ollama pull qwen2.5:7b` (~4,7 GB)

### 2. Dependências

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
(cd app && npm ci)
(cd mcp && npm ci)
```

### 3. Teste rápido, sem Supabase

```bash
.venv/bin/python tests/test_gabaritos.py          # validadores (CPF, CNPJ, chave NF-e, boleto, MRZ)
.venv/bin/python -m pytest -q tests/              # motor (os de OCR rodam só no macOS)
(cd app && npx vitest run)                        # aplicação
.venv/bin/python scripts/avaliar.py               # motor nos 32 documentos fictícios (--ia usa o Ollama)
```

Telas no **modo de demonstração**, com dados fictícios e sem celular:

```bash
(cd app && npx vite build && npx vite preview --port 4173)
# http://localhost:4173/captura.html?demo=camera
# http://localhost:4173/escritorio.html?demo=revisao
```

### 4. Teste completo, com o celular

Exige um projeto Supabase próprio (plano gratuito):

1. `supabase link --project-ref <ref>` e `supabase db push --remote` aplicam `supabase/migrations/` (cadastros cifrados, auditoria e remoção às 18h).
2. Crie `app/.env.development.local` e `app/.env.production.local` com `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` e `VITE_URL_CAPTURA` (endereço da página de captura publicada).
3. Publique a página de captura: `cd app && PAGINA=captura npx vite build`, depois publique a pasta `dist-captura` (por exemplo, na Vercel).
4. `scripts/iniciar-motor.sh` liga a IA local e o motor; abra `http://localhost:8787`, gere o link e leia o QR code com o celular.

Depois de qualquer teste com documentos: `scripts/limpar-e-verificar.sh --verificar` precisa retornar ✅ CONFIRMADO.

## Servidor MCP

O arquivo `.mcp.json` registra o servidor `extracao-documentos` (`mcp/servidor.mjs`). Com o motor rodando, ele oferece:

| Ferramenta | O que faz |
|---|---|
| `estado` | Verifica se o motor e a IA local estão rodando |
| `listar_documentos_ficticios` | Lista os documentos de teste |
| `ler_documento_ficticio` | Lê um documento fictício e devolve tipo e campos; **recusa qualquer arquivo fora de `data/exemplos/`** |
| `avaliar_motor` | Roda a avaliação nos 32 documentos fictícios |
| `resultados_chave` | Calcula os resultados-chave a partir do registro de medição |

## Onde está cada coisa

| Caminho | Conteúdo |
|---|---|
| `docs/etapas/` | Uma nota por etapa do projeto |
| `docs/decisoes/` | Decisões (ADRs) com alternativas e consequências |
| `docs/evolucao.md` | Linha do tempo das decisões e dos números |
| `app/` | Página de captura e aplicação do escritório (React + TypeScript) |
| `src/` | Motor: OCR, classificação, extração, validação e IA |
| `supabase/migrations/` | Banco do estudo |
| `scripts/` | Geração de documentos fictícios, avaliação, relatório e imagens dos diagramas |
