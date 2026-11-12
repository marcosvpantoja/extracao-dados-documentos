"""Avaliação do motor no conjunto fictício (linha de base da Etapa 10).

Para cada documento fictício: renderiza o PDF, lê com o OCR, classifica, extrai e compara
cada campo com o gabarito. Só usa documentos fictícios (data/exemplos), nunca documentos reais.

Uso: .venv/bin/python scripts/avaliar.py [--detalhe] [--variantes]
   --variantes avalia só os layouts novos (gerar_variantes.py), que as regras não viram ao serem escritas.
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

# Campos que o motor se propõe a extrair hoje, por tipo (para medir os não encontrados)
CAMPOS_AVALIADOS = {
    "cnh": ("nome", "cpf", "data_nascimento", "filiacao_pai", "filiacao_mae", "numero_registro", "validade"),
    "cin": ("nome", "cpf", "data_nascimento", "filiacao_pai", "filiacao_mae", "naturalidade", "orgao_expedidor"),
    "rg": ("nome", "registro_geral", "data_nascimento", "filiacao_pai", "filiacao_mae", "naturalidade", "orgao_expedidor"),
    "nfe": ("chave_acesso", "emitente_cnpj", "valor_total", "data_emissao"),
    "boleto": ("linha_digitavel", "valor", "vencimento"),
    "fatura": ("valor_total", "vencimento", "cnpj_emissora"),
}

TIPO_GABARITO = {"CNH": "cnh", "CIN": "cin", "RG": "rg", "NFE": "nfe", "BOLETO": "boleto", "FATURA": "fatura"}


def norm(v) -> str:
    return re.sub(r"[^A-Z0-9]", "", sem_acento(str(v)))


def main(detalhe: bool, so_variantes: bool = False):
    ocr = AppleVision()
    por_campo = defaultdict(lambda: [0, 0, 0])  # acertos, errados, ausentes
    classificacao = [0, 0]
    tempos = []
    for gab_path in sorted(glob.glob(str(RAIZ / "data/exemplos/*/*.json"))):
        gab = json.load(open(gab_path))
        if so_variantes and "variante" not in gab:
            continue
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
            for campo in gab["campos"]:
                if campo in CAMPOS_AVALIADOS.get(esperado, ()) and campo not in r.campos:
                    por_campo[(esperado, campo)][2] += 1
                    if detalhe:
                        linha.append(f"    · {campo}: não encontrado")
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
    print(f"{'tipo':8} {'campo':24} {'certos':>6} {'errados':>7} {'não achou':>9}")
    for (tipo, campo), (ok, err, aus) in sorted(por_campo.items()):
        print(f"{tipo:8} {campo:24} {ok:>6} {err:>7} {aus:>9}")
    tot_ok = sum(v[0] for v in por_campo.values())
    tot_err = sum(v[1] for v in por_campo.values())
    tot_aus = sum(v[2] for v in por_campo.values())
    print(f"\nCampos extraídos: {tot_ok + tot_err} · certos: {tot_ok} ({tot_ok / max(1, tot_ok + tot_err):.0%})")
    print(f"Cobertura (campos esperados encontrados e certos): {tot_ok}/{tot_ok + tot_err + tot_aus} "
          f"({tot_ok / max(1, tot_ok + tot_err + tot_aus):.0%})")


if __name__ == "__main__":
    main("--detalhe" in sys.argv, "--variantes" in sys.argv)
