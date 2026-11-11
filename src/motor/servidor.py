"""Motor local de extração (estudo de caso).

Incremento 1: a leitura é SIMULADA. O motor recebe as fotos, não guarda nada e responde
como o motor real responderá, para a captura pelo celular ser testada de ponta a ponta.
O motor real (OCR, classificação, extração) entra nos incrementos 2 e 3.

Também serve a aplicação do escritório em http://localhost:8787 (ADR 0011).

Uso:  .venv/bin/uvicorn src.motor.servidor:app --port 8787
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

RAIZ = Path(__file__).resolve().parents[2]
DIST = RAIZ / "app" / "dist"
ESPERA_SIMULADA_S = 1.5

TIPOS = {"identidade": "cnh", "comprovante": "fatura", "fatura": "fatura", "boleto": "boleto", "nota": "nfe"}

app = FastAPI(title="Motor local de extração", docs_url=None, redoc_url=None)

# Em desenvolvimento, a aplicação do escritório roda no Vite (localhost:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.post("/processar")
async def processar(request: Request, doc: str, simular: Optional[str] = None) -> dict:
    formulario = await request.form()
    faces = [k for k in ("frente", "verso") if k in formulario]
    # As imagens ficam só na memória desta requisição e são descartadas ao fim dela.
    tamanhos = {f: len(await formulario[f].read()) for f in faces}
    await formulario.close()
    await asyncio.sleep(ESPERA_SIMULADA_S)
    if simular == "falha":
        return {"status": "nova-foto", "motivo": "Não conseguimos ler o número do documento", "faces": tamanhos}
    return {"status": "lido", "tipo": TIPOS.get(doc, "nao_reconhecido"), "faces": tamanhos}


@app.get("/")
def raiz():
    return RedirectResponse("/escritorio.html")


if DIST.exists():
    @app.get("/escritorio.html")
    def escritorio():
        return FileResponse(DIST / "escritorio.html")

    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")
