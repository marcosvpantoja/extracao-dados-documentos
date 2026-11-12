"""Motor local de extração (estudo de caso).

Incremento 2: leitura real por regras (ADR 0002). O Apple Vision lê o texto, as regras
classificam e extraem os campos, e os validadores conferem CPF, CNPJ, chave da NF-e,
linha digitável e MRZ. Sem IA de texto por enquanto. Se faltar um campo essencial,
o motor pede nova foto (RF-31). Nada é gravado: as imagens vivem só durante a requisição.

`simular=falha` continua disponível para testar o pedido de nova foto.

Também serve a aplicação do escritório em http://localhost:8787 (ADR 0011).

Uso:  .venv/bin/uvicorn src.motor.servidor:app --port 8787
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

RAIZ = Path(__file__).resolve().parents[2]
DIST = RAIZ / "app" / "dist"
ESPERA_SIMULADA_S = 1.5

from src.extracao.ocr import AppleVision, Linha  # noqa: E402
from src.extracao.pipeline import processar as extrair  # noqa: E402

ocr = AppleVision()

app = FastAPI(title="Motor local de extração", docs_url=None, redoc_url=None)

# Em desenvolvimento, a aplicação do escritório roda no Vite (localhost:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST"],  # /processar e /revisao
    allow_headers=["*"],
)


@app.post("/processar")
async def processar(request: Request, doc: str, simular: Optional[str] = None) -> dict:
    formulario = await request.form()
    faces = [k for k in ("frente", "verso") if k in formulario]
    # As imagens ficam só na memória desta requisição e são descartadas ao fim dela.
    imagens = {f: await formulario[f].read() for f in faces}
    await formulario.close()
    if simular == "falha":
        await asyncio.sleep(ESPERA_SIMULADA_S)
        return {"status": "nova-foto", "motivo": "Não conseguimos ler o número do documento"}

    t0 = time.perf_counter()
    linhas: list = []
    try:
        for i, f in enumerate(faces):
            # o verso vem "embaixo" da frente, para as regras de posição não misturarem as faces
            for l in await asyncio.to_thread(ocr.ler, imagens[f]):
                linhas.append(Linha(l.texto, l.confianca, l.x, l.y + i * 1.5, l.largura, l.altura))
    except ValueError:
        return {"status": "nova-foto", "motivo": "Não conseguimos abrir a foto"}
    finally:
        imagens.clear()

    r = extrair(linhas)
    resposta = {
        "tipo": r.tipo,
        "confianca_tipo": r.confianca_tipo,
        "campos": {k: asdict(v) for k, v in r.campos.items() if not k.startswith("_")},
        "tempo_ms": round((time.perf_counter() - t0) * 1000),
    }
    if not r.legivel or r.tipo == "nao_reconhecido":
        return {**resposta, "status": "nova-foto", "motivo": r.motivo or "Não reconhecemos este documento"}
    return {**resposta, "status": "lido"}


REGISTRO_REVISAO = RAIZ / "data" / "privado" / "registro-revisao.jsonl"
# Só estas chaves entram no registro: eventos, contagens e tempos. Nunca valores nem imagens.
CHAVES_REVISAO = {"etapa", "sessao", "evento", "tipo", "campo", "origem", "validado", "resultado",
                  "doc", "docs", "fotos", "faces", "status", "ms", "sem_edicao", "erros"}
RESULTADOS = {"confirmado", "recusado", "certo", "errado"}


@app.post("/revisao")
async def revisao(eventos: list = Body(...)) -> dict:
    """Registro local de revisão (RF-22, ADR 0004): só tipo, campo, origem e resultado.
    Qualquer outra chave é descartada, para nenhum valor do documento entrar no registro."""
    import json
    from datetime import datetime, timezone
    REGISTRO_REVISAO.parent.mkdir(parents=True, exist_ok=True)
    gravados = 0
    with REGISTRO_REVISAO.open("a", encoding="utf-8") as f:
        for e in eventos[:100]:
            if not isinstance(e, dict) or ("resultado" in e and e["resultado"] not in RESULTADOS):
                continue
            if "resultado" not in e and "evento" not in e:
                continue
            limpo = {k: e[k] for k in CHAVES_REVISAO
                     if k in e and isinstance(e[k], (str, bool, int)) and (not isinstance(e[k], str) or len(e[k]) <= 60)}
            limpo["quando"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            f.write(json.dumps(limpo, ensure_ascii=False) + "\n")
            gravados += 1
    return {"gravados": gravados}


@app.get("/")
def raiz():
    return RedirectResponse("/escritorio.html")


if DIST.exists():
    @app.get("/escritorio.html")
    def escritorio():
        return FileResponse(DIST / "escritorio.html")

    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")
