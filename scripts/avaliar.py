"""Avaliação do motor no conjunto fictício (linha de base da Etapa 10).

Para cada documento fictício: renderiza o PDF, lê com o OCR, classifica, extrai e compara
cada campo com o gabarito. Só usa documentos fictícios (data/exemplos), nunca documentos reais.

Uso: .venv/bin/python scripts/avaliar.py [--detalhe]
"""

from __future__ import annotations

import glob
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.extracao.ocr import AppleVision, renderizar_pdf  # noqa: E402
from src.extracao.pipeline import processar, sem_acento  # noqa: E402

TIPO_GABARITO = {"CNH": "cnh", "CIN": "cin", "RG": "rg", "NFE": "nfe", "BOLETO": "boleto", "FATURA": "fatura"}


def norm(v) -> str:
    return re.sub(r"[^A-Z0-9]", "", sem_acento(str(v)))


def main(detalhe: bool):
    ocr = AppleVision()
    por_campo = defaultdict(lambda: [0, 0, 0])  # acertos, errados, ausentes
    classificacao = [0, 0]
    tempos = []
    for gab_path in sorted(glob.glob(str(RAIZ / "data/exemplos/*/*.json"))):
        gab = json.load(open(gab_path))
        esperado = TIPO_GABARITO[gab["tipo"]]
        pdfs = [RAIZ / "data/exemplos" / gab["arquivo"]]
        impressao = Path(str(pdfs[0]).replace(".pdf", "-impressao.pdf"))
        if impressao.exists():
            pdfs.append(impressao)
        for pdf in pdfs:
            t0 = time.perf_counter()
            r = processar(ocr.ler(renderizar_pdf(str(pdf))))
            tempos.append(time.perf_counter() - t0)
            classificacao[0 if r.tipo == esperado else 1] += 1
            linha = [f"{pdf.name:34} tipo={r.tipo:15} {'✓' if r.tipo == esperado else '✗ esperado ' + esperado}"]
            for campo, valor in r.campos.items():
                if campo.startswith("_") or campo not in gab["campos"]:
                    continue
                ok = norm(valor.valor) == norm(gab["campos"][campo])
                por_campo[(esperado, campo)][0 if ok else 1] += 1
                if detalhe and not ok:
                    linha.append(f"    ✗ {campo}: lido={valor.valor!r} esperado={gab['campos'][campo]!r}")
            if not r.legivel:
                linha.append(f"    → pediria nova foto: {r.motivo}")
            print("\n".join(linha))

    print(f"\nClassificação: {classificacao[0]}/{sum(classificacao)} corretas")
    print(f"Tempo por documento: média {sum(tempos)/len(tempos):.2f} s · máximo {max(tempos):.2f} s\n")
    print(f"{'tipo':8} {'campo':24} {'certos':>6} {'errados':>7}")
    for (tipo, campo), (ok, err, _) in sorted(por_campo.items()):
        print(f"{tipo:8} {campo:24} {ok:>6} {err:>7}")
    tot_ok = sum(v[0] for v in por_campo.values())
    tot_err = sum(v[1] for v in por_campo.values())
    print(f"\nCampos extraídos: {tot_ok + tot_err} · certos: {tot_ok} ({tot_ok / max(1, tot_ok + tot_err):.0%})")


if __name__ == "__main__":
    main("--detalhe" in sys.argv)
