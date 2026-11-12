"""Relatório dos resultados-chave a partir do registro local de medição (Etapa 5).

Lê data/privado/registro-revisao.jsonl (só eventos, contagens e tempos; nenhum dado pessoal)
e calcula, sempre com o tamanho da amostra:

- KR1 · % de documentos sem nenhum campo apontado como errado na conferência do cliente
- KR2 · % de documentos confirmados sem nenhuma edição (apoio da North Star)
- KR3 · tempo de cadastro por cliente (link gerado → última conferência)
- KR4 · % de documentos aceitos com a primeira foto
- Proteção · % de documentos com algum campo apontado como errado depois da confirmação
- North Star (estudo) · sessões em que todos os documentos saíram sem edição

Uso: .venv/bin/python scripts/relatorio.py [arquivo.jsonl]
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PADRAO = RAIZ / "data" / "privado" / "registro-revisao.jsonl"


def pct(a: int, b: int) -> str:
    return f"{a / b:.0%} ({a} de {b})" if b else "sem amostra"


def main(caminho: Path):
    if not caminho.exists():
        print("Nenhum registro ainda. Faça uma sessão completa (captura, revisão e conferência).")
        return
    eventos = [json.loads(l) for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip()]
    sessoes = defaultdict(list)
    for e in eventos:
        if e.get("sessao"):
            sessoes[e["sessao"]].append(e)

    revisoes = [e for e in eventos if e.get("evento") == "revisao_concluida"]
    conferencias = [e for e in eventos if e.get("evento") == "conferencia_concluida"]
    lidos = [e for e in eventos if e.get("evento") == "documento_lido"]

    # KR4: aceito de primeira = uma foto por face e leitura sem pedido de nova foto
    primeira = [e for e in lidos if e.get("status") == "lido" and 0 < e.get("fotos", 0) <= e.get("faces", 1)]
    # KR3: tempo de cadastro por sessão
    tempos = []
    for evs in sessoes.values():
        t0 = next((e["quando"] for e in evs if e.get("evento") == "link_gerado"), None)
        fins = [e["quando"] for e in evs if e.get("evento") in ("conferencia_concluida", "revisao_concluida")]
        if t0 and fins:
            tempos.append((datetime.fromisoformat(max(fins)) - datetime.fromisoformat(t0)).total_seconds() / 60)
    # North Star (estudo): sessões com todos os documentos revisados sem edição
    ns = [s for s, evs in sessoes.items()
          if (rv := [e for e in evs if e.get("evento") == "revisao_concluida"]) and all(e.get("sem_edicao") for e in rv)]

    print(f"Registro: {caminho} · {len(eventos)} eventos · {len(sessoes)} sessões\n")
    print(f"KR1 · documentos sem erro na conferência do cliente: {pct(sum(1 for e in conferencias if e.get('erros', 0) == 0), len(conferencias))}")
    print(f"KR2 · documentos confirmados sem edição:            {pct(sum(1 for e in revisoes if e.get('sem_edicao')), len(revisoes))}")
    if tempos:
        tempos.sort()
        print(f"KR3 · tempo de cadastro por cliente:                mediana {tempos[len(tempos) // 2]:.1f} min (n = {len(tempos)}); comparar com a digitação manual")
    else:
        print("KR3 · tempo de cadastro por cliente:                sem amostra")
    print(f"KR4 · documentos aceitos com a primeira foto:       {pct(len(primeira), len(lidos))}")
    print(f"Proteção · documentos com erro depois da revisão:   {pct(sum(1 for e in conferencias if e.get('erros', 0) > 0), len(conferencias))}")
    print(f"North Star (estudo) · sessões 100% sem edição:      {pct(len(ns), len(sessoes))}")

    erros_campo = defaultdict(lambda: [0, 0])
    for e in eventos:
        if e.get("etapa") == "conferencia":
            erros_campo[(e.get("tipo", "?"), e.get("campo", "?"))][1] += 1
            if e.get("resultado") == "errado":
                erros_campo[(e.get("tipo", "?"), e.get("campo", "?"))][0] += 1
    falhas = [(k, v) for k, v in erros_campo.items() if v[0]]
    if falhas:
        print("\nCampos com erro apontado pelo cliente:")
        for (tipo, campo), (err, tot) in sorted(falhas, key=lambda x: -x[1][0]):
            print(f"  {tipo:8} {campo:22} {err} de {tot}")
    print("\nAmostra pequena: os números indicam direção, não taxas com confiança estatística.")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else PADRAO)
