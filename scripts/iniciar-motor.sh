#!/bin/zsh
# Inicia a IA local (Ollama) e o motor de extração, só no endereço local do Mac.
# Depois, abra http://localhost:8787 no Chrome ou no Safari.
cd "$(dirname "$0")/.."
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null; then
  OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 OLLAMA_HOST=127.0.0.1:11434 ollama serve >/dev/null 2>&1 &
  sleep 2
fi
(cd app && npx vite build >/dev/null)
exec .venv/bin/uvicorn src.motor.servidor:app --host 127.0.0.1 --port 8787
