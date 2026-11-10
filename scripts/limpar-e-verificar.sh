#!/usr/bin/env bash
# Remove documentos reais usados em testes e verifica que nenhum permaneceu no projeto.
# Uso: ./scripts/limpar-e-verificar.sh              limpa data/privado/entrada e verifica
#      ./scripts/limpar-e-verificar.sh --verificar  só verifica (mantém documentos aguardando teste)
set -uo pipefail
cd "$(dirname "$0")/.."

ENTRADA="data/privado/entrada"
falhas=0

echo "== 1. Limpeza de $ENTRADA"
if [ "${1:-}" = "--verificar" ]; then
  qtd=$(find "$ENTRADA" -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "   modo só verificação: $qtd arquivo(s) aguardando teste, mantidos e ignorados pelo git"
elif [ -d "$ENTRADA" ]; then
  qtd=$(find "$ENTRADA" -type f | wc -l | tr -d ' ')
  find "$ENTRADA" -type f -exec rm -P {} + 2>/dev/null || find "$ENTRADA" -type f -delete
  echo "   $qtd arquivo(s) removido(s)"
else
  mkdir -p "$ENTRADA"; echo "   pasta vazia"
fi

echo "== 2. Busca por documentos (PDF/imagem) fora de data/exemplos/, pelo conteúdo e não só pela extensão"
achados=$(find . -type f \
  -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" \
  -not -path "./data/exemplos/*" -not -path "./docs/*" -not -path "./$ENTRADA/*" \
  -exec file --mime-type {} + 2>/dev/null | grep -E ": (application/pdf|image/)" || true)
if [ -n "$achados" ]; then echo "   ENCONTRADO:"; echo "$achados" | sed 's/^/     /'; falhas=1; else echo "   nenhum"; fi

echo "== 3. Arquivos não rastreados ou modificados que não sejam código/documentação"
pendentes=$(git status --porcelain --ignored --untracked-files=all | grep -vE '\.(md|sh|py|ts|tsx|js|json|css|html|toml|yml|yaml)$|\.gitignore$|data/privado/LEIAME|data/privado/$|data/privado/entrada/$|data/privado/entrada/|data/exemplos/|data/privado/[^/]+\.jsonl$|node_modules|\.venv|__pycache__|\.DS_Store' || true)
if [ -n "$pendentes" ]; then echo "   VERIFICAR:"; echo "$pendentes" | sed 's/^/     /'; falhas=1; else echo "   nenhum"; fi

echo "== 4. Histórico do git: algum PDF/imagem fora de data/exemplos/ e docs/ já foi commitado?"
hist=$(git log --all --diff-filter=A --name-only --pretty=format: 2>/dev/null \
  | grep -iE '\.(pdf|jpe?g|png|heic|webp|tiff?)$' | grep -vE '^(data/exemplos|docs)/' | sort -u || true)
if [ -n "$hist" ]; then echo "   ENCONTRADO NO HISTÓRICO:"; echo "$hist" | sed 's/^/     /'; falhas=1; else echo "   nenhum"; fi

echo "== 5. Registros de avaliação (só métricas anônimas)"
for f in data/privado/*.jsonl; do
  [ -e "$f" ] || { echo "   nenhum registro"; break; }
  if grep -qE '[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}|base64|data:image' "$f"; then
    echo "   POSSÍVEL DADO PESSOAL em $f"; falhas=1
  else echo "   $f: ok"; fi
done

echo
if [ "$falhas" -eq 0 ]; then
  echo "✅ CONFIRMADO: nenhum documento real no projeto, no histórico do git ou nos registros."
else
  echo "❌ ATENÇÃO: itens acima precisam ser revisados antes do próximo teste."
  exit 1
fi
