"""Gera documentos fictícios com LAYOUTS DIFERENTES dos de gerar_exemplos.py.

Motivo (teste no celular, 11/11/2026): um RG de modelo novo não foi reconhecido, porque as
regras do motor tinham sido ajustadas em um único layout por tipo. Estas variantes imitam a
variedade real (rótulos ao lado, rótulos bilíngues, modelo antigo sem MRZ, formato de app)
e servem primeiro para MEDIR a generalização, antes de qualquer ajuste nas regras.

Gera: rg-antigo 03 a 05, cin 03 e 04, cnh 03 e 04 (com gabarito JSON e versão de impressão).
Uso: .venv/bin/python scripts/gerar_variantes.py
"""

from __future__ import annotations

import datetime as dt
import json
import random
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_exemplos as g  # noqa: E402

CSS = """
.c{width:860px;height:560px;padding:20px 24px;position:relative;overflow:hidden;border-radius:14px;font-family:Arial,Helvetica,sans-serif}
.lb{font-size:11px;color:#333;text-transform:uppercase}
.vl{font-size:19px;font-weight:700;margin-bottom:8px}
.ln{display:flex;gap:8px;align-items:baseline;margin-bottom:9px}.ln .lb{min-width:120px}
"""


def png(html, w=860, h=560):
    return g.chrome_png(g.pagina(html, CSS, marca=False), w, h)


def pessoa(r, sexo=None):
    cidade, uf = r.choice(g.CIDADES)
    sobrenome = r.choice(g.SOBRENOMES)
    sexo = sexo or r.choice("MF")
    return dict(
        cidade=cidade, uf=uf, sexo=sexo, nome=g.nome_pessoa(r, sobrenome, sexo),
        pai=g.nome_pessoa(r, sobrenome, "M"), mae=g.nome_pessoa(r, sexo="F"),
        nasc=g.data_aleatoria(r, dt.date(1960, 1, 1), dt.date(2005, 12, 31)), cpf=g.cpf(r),
    )


def rg_formatado(r):
    n = str(r.randint(10000000, 49999999))
    return n, f"{n[:2]}.{n[2:5]}.{n[5:]}-{r.randint(0, 9)}"


# ---------------------------------------------------------------- RG antigo: 3 layouts novos

def rg_v_rotulos_ao_lado(r, i):
    """Rótulos à esquerda do valor, com dois-pontos; número com pontos; PAI e MÃE separados."""
    p = pessoa(r); uf = p["uf"]; num, num_fmt = rg_formatado(r)
    exped = g.data_aleatoria(r, dt.date(2006, 1, 1), dt.date(2024, 12, 31))
    campos = {"nome": p["nome"], "filiacao_pai": p["pai"], "filiacao_mae": p["mae"], "data_nascimento": p["nasc"].isoformat(),
              "naturalidade": f"{p['cidade']}, {uf}", "orgao_expedidor": f"SSP/{uf}", "registro_geral": num_fmt,
              "data_expedicao": exped.isoformat(), "cpf": p["cpf"]}
    fundo = "background:repeating-linear-gradient(0deg,#f3eadb 0 3px,#efe3cf 3px 6px);border:10px solid #8a6d3b"
    frente = f"""<div class="c" style="{fundo}">
      <div style="text-align:center;font-weight:700;font-size:18px">SECRETARIA DA SEGURANÇA PÚBLICA · ESTADO FICTÍCIO</div>
      <div style="text-align:right;font-size:20px;font-weight:700;margin:6px 0 12px">RG: {num_fmt}</div>
      <div class="ln"><span class="lb">Nome:</span><span class="vl">{g.esc(p['nome'])}</span></div>
      <div class="ln"><span class="lb">Pai:</span><span class="vl">{g.esc(p['pai'])}</span></div>
      <div class="ln"><span class="lb">Mãe:</span><span class="vl">{g.esc(p['mae'])}</span></div>
      <div class="ln"><span class="lb">Naturalidade:</span><span class="vl">{g.esc(p['cidade'])}/{uf}</span></div>
      <div class="ln"><span class="lb">Nascimento:</span><span class="vl">{g.br(p['nasc'])}</span></div>
      <div class="ln"><span class="lb">CPF:</span><span class="vl">{p['cpf']}</span></div>
      <div class="ln"><span class="lb">Expedição:</span><span class="vl">{g.br(exped)}</span><span class="lb" style="min-width:0;margin-left:30px">Órgão:</span><span class="vl">SSP/{uf}</span></div>
      <div style="position:absolute;bottom:10px;left:0;right:0;text-align:center;font-weight:700;letter-spacing:5px">CARTEIRA DE IDENTIDADE</div></div>"""
    return campos, [png(frente)]


def rg_v_verso_unico(r, i):
    """Uma face só, rótulo acima do valor, registro com sigla da UF ("MG-12.345.678")."""
    p = pessoa(r); uf = p["uf"]; num, _ = rg_formatado(r)
    exped = g.data_aleatoria(r, dt.date(2006, 1, 1), dt.date(2024, 12, 31))
    campos = {"nome": p["nome"], "filiacao_pai": p["pai"], "filiacao_mae": p["mae"], "data_nascimento": p["nasc"].isoformat(),
              "naturalidade": f"{p['cidade']}, {uf}", "orgao_expedidor": f"SSP/{uf}", "registro_geral": num,
              "data_expedicao": exped.isoformat()}
    reg = f"{uf}-{num[:2]}.{num[2:5]}.{num[5:]}"
    corpo = f"""<div class="c" style="background:linear-gradient(160deg,#e9f0e4,#dbe8d3)">
      <div style="display:flex;justify-content:space-between"><div><div class="lb">Registro geral</div><div class="vl">{reg}</div></div>
        <div><div class="lb">Data de expedição</div><div class="vl">{g.br(exped)}</div></div></div>
      <div class="lb">Nome</div><div class="vl">{g.esc(p['nome'])}</div>
      <div class="lb">Filiação</div><div class="vl" style="font-size:17px">{g.esc(p['pai'])}<br>{g.esc(p['mae'])}</div>
      <div style="display:flex;gap:40px"><div><div class="lb">Naturalidade</div><div class="vl">{g.esc(p['cidade'])} - {uf}</div></div>
        <div><div class="lb">Data de nascimento</div><div class="vl">{g.br(p['nasc'])}</div></div></div>
      <div class="lb">Doc. origem</div><div class="vl" style="font-size:15px">CERT. NASC. LIVRO {r.randint(10,99)} FOLHA {r.randint(10,299)}</div>
      <div style="position:absolute;bottom:14px;right:24px;font-size:13px;font-weight:700">SSP/{uf} · INSTITUTO DE IDENTIFICAÇÃO FICTÍCIO</div></div>"""
    return campos, [png(corpo)]


def rg_v_ordem_invertida(r, i):
    """Data e naturalidade antes do nome; filiação numa linha só, separada por "e"."""
    p = pessoa(r); uf = p["uf"]; num, num_fmt = rg_formatado(r)
    exped = g.data_aleatoria(r, dt.date(2006, 1, 1), dt.date(2024, 12, 31))
    campos = {"nome": p["nome"], "filiacao_pai": p["pai"], "filiacao_mae": p["mae"], "data_nascimento": p["nasc"].isoformat(),
              "naturalidade": f"{p['cidade']}, {uf}", "orgao_expedidor": f"SSP/{uf}", "registro_geral": num_fmt,
              "data_expedicao": exped.isoformat(), "cpf": p["cpf"]}
    corpo = f"""<div class="c" style="background:#eef3f7;border:8px double #4a6a8a">
      <div style="text-align:center;font-weight:700;letter-spacing:3px;margin-bottom:10px">REPÚBLICA FEDERATIVA DO BRASIL · MODELO FICTÍCIO</div>
      <div style="display:flex;gap:40px"><div><div class="lb">Registro geral</div><div class="vl">{num_fmt}</div></div>
        <div><div class="lb">Expedição</div><div class="vl">{g.br(exped)}</div></div><div><div class="lb">CPF</div><div class="vl">{p['cpf']}</div></div></div>
      <div style="display:flex;gap:40px"><div><div class="lb">Nascimento</div><div class="vl">{g.br(p['nasc'])}</div></div>
        <div><div class="lb">Naturalidade</div><div class="vl">{g.esc(p['cidade'])}, {uf}</div></div></div>
      <div class="lb">Nome</div><div class="vl">{g.esc(p['nome'])}</div>
      <div class="lb">Filho(a) de</div><div class="vl" style="font-size:16px">{g.esc(p['pai'])} e {g.esc(p['mae'])}</div>
      <div style="position:absolute;bottom:12px;left:24px;font-size:13px;font-weight:700">Expedida por SSP/{uf}</div></div>"""
    return campos, [png(corpo)]


# ---------------------------------------------------------------- CIN: rótulos bilíngues e formato de app

def cin_bilingue(r, i):
    p = pessoa(r); uf = p["uf"]
    emissao = g.data_aleatoria(r, dt.date(2023, 7, 1), dt.date(2026, 9, 30)); validade = emissao.replace(year=emissao.year + 10)
    mrz = g.mrz_td1(g.so_digitos(p["cpf"])[:9], p["nasc"], p["sexo"], validade, p["nome"], g.so_digitos(p["cpf"]))
    campos = {"nome": p["nome"], "sexo": p["sexo"], "data_nascimento": p["nasc"].isoformat(), "naturalidade": f"{p['cidade']}, {uf}",
              "filiacao_pai": p["pai"], "filiacao_mae": p["mae"], "cpf": p["cpf"], "registro_geral": g.so_digitos(p["cpf"]),
              "orgao_expedidor": f"SSP/{uf}", "data_emissao": emissao.isoformat(), "validade": validade.isoformat()}
    fundo = "background:linear-gradient(110deg,#e8f4ec,#d6ebe0 50%,#eef7f1)"
    frente = f"""<div class="c" style="{fundo}">
      <div style="font-weight:700;font-size:15px">REPÚBLICA FEDERATIVA DO BRASIL</div>
      <div style="font-size:12px;margin-bottom:12px">CARTEIRA DE IDENTIDADE · MODELO FICTÍCIO</div>
      <div style="display:flex;gap:20px"><div style="width:190px;height:240px">{g.foto_placeholder()}</div><div style="flex:1">
        <div class="lb">Nome / Name</div><div class="vl">{g.esc(p['nome'])}</div>
        <div class="lb">Nome social / Social name</div><div class="vl">&nbsp;</div>
        <div style="display:flex;gap:24px"><div><div class="lb">Sexo / Sex</div><div class="vl">{p['sexo']}</div></div>
          <div><div class="lb">Nacionalidade / Nationality</div><div class="vl">BRA</div></div></div>
        <div class="lb">Data de nascimento / Date of birth</div><div class="vl">{g.br(p['nasc'])}</div>
        <div class="lb">Registro geral - CPF / Personal number</div><div class="vl">{p['cpf']}</div>
        <div class="lb">Data de validade / Date of expiry</div><div class="vl">{g.br(validade)}</div></div></div></div>"""
    verso = f"""<div class="c" style="{fundo}">
      <div class="lb">Filiação / Parents</div><div class="vl" style="font-size:17px">{g.esc(p['mae'])}<br>{g.esc(p['pai'])}</div>
      <div style="display:flex;gap:26px"><div><div class="lb">Naturalidade / Place of birth</div><div class="vl">{g.esc(p['cidade'])}/{uf}</div></div>
        <div><div class="lb">Órgão expedidor / Issuing authority</div><div class="vl">SSP/{uf}</div></div></div>
      <div class="lb">Data de emissão / Date of issue</div><div class="vl">{g.br(emissao)}</div>
      <div style="margin-top:24px;font-family:'Courier New',monospace;font-size:24px;line-height:1.5;letter-spacing:2px">{'<br>'.join(g.esc(l) for l in mrz)}</div></div>"""
    return campos, [png(frente), png(verso)]


def cin_app(r, i):
    """Formato de app no celular: tela vertical, um campo por linha, sem MRZ visível."""
    p = pessoa(r); uf = p["uf"]
    emissao = g.data_aleatoria(r, dt.date(2023, 7, 1), dt.date(2026, 9, 30)); validade = emissao.replace(year=emissao.year + 10)
    campos = {"nome": p["nome"], "sexo": p["sexo"], "data_nascimento": p["nasc"].isoformat(), "naturalidade": f"{p['cidade']}, {uf}",
              "filiacao_pai": p["pai"], "filiacao_mae": p["mae"], "cpf": p["cpf"], "registro_geral": g.so_digitos(p["cpf"]),
              "orgao_expedidor": f"SSP/{uf}", "validade": validade.isoformat()}
    item = lambda l, v: f"<div style='padding:10px 0;border-bottom:1px solid #ddd'><div class='lb'>{l}</div><div class='vl' style='margin:0'>{v}</div></div>"
    tela = f"""<div class="c" style="width:420px;height:860px;background:#fff;border-radius:28px;border:10px solid #111">
      <div style="background:#1351b4;color:#fff;margin:-20px -24px 14px;padding:22px 24px;font-weight:700">Carteira de Identidade · app fictício</div>
      {item('Nome', g.esc(p['nome']))}{item('CPF', p['cpf'])}{item('Data de nascimento', g.br(p['nasc']))}{item('Sexo', p['sexo'])}
      {item('Mãe', g.esc(p['mae']))}{item('Pai', g.esc(p['pai']))}{item('Naturalidade', f"{g.esc(p['cidade'])}/{uf}")}
      {item('Órgão expedidor', f'SSP/{uf}')}{item('Validade', g.br(validade))}</div>"""
    return campos, [png(tela, 420, 860)]


# ---------------------------------------------------------------- CNH: modelo antigo sem MRZ e formato de app

def cnh_antiga(r, i):
    p = pessoa(r); uf = p["uf"]
    primeira = g.data_aleatoria(r, p["nasc"] + dt.timedelta(days=18 * 366), dt.date(2015, 12, 31))
    validade = g.data_aleatoria(r, dt.date(2026, 1, 1), dt.date(2030, 12, 31))
    registro = "".join(str(r.randint(0, 9)) for _ in range(11)); categoria = r.choice(["B", "AB"])
    rg = str(r.randint(1000000, 99999999))
    campos = {"nome": p["nome"], "data_nascimento": p["nasc"].isoformat(), "filiacao_pai": p["pai"], "filiacao_mae": p["mae"],
              "cpf": p["cpf"], "numero_registro": registro, "categoria": categoria, "validade": validade.isoformat(),
              "primeira_habilitacao": primeira.isoformat(), "documento_identidade": f"{rg} SSP {uf}"}
    corpo = f"""<div class="c" style="background:linear-gradient(180deg,#d9ead0,#c6dfb9);border:2px solid #5d7d4f">
      <div style="text-align:center;font-weight:700;font-size:15px;margin-bottom:10px">REPÚBLICA FEDERATIVA DO BRASIL · DEPARTAMENTO FICTÍCIO DE TRÂNSITO<br>CARTEIRA NACIONAL DE HABILITAÇÃO</div>
      <div style="display:flex;gap:18px"><div style="width:170px;height:220px">{g.foto_placeholder()}</div><div style="flex:1">
        <div class="lb">Nome</div><div class="vl">{g.esc(p['nome'])}</div>
        <div class="lb">Doc. identidade / Órg. emissor / UF</div><div class="vl">{rg} SSP {uf}</div>
        <div style="display:flex;gap:24px"><div><div class="lb">CPF</div><div class="vl">{p['cpf']}</div></div>
          <div><div class="lb">Data nascimento</div><div class="vl">{g.br(p['nasc'])}</div></div></div>
        <div class="lb">Filiação</div><div class="vl" style="font-size:16px">{g.esc(p['pai'])}<br>{g.esc(p['mae'])}</div>
        <div style="display:flex;gap:20px"><div><div class="lb">Permissão</div><div class="vl">&nbsp;</div></div><div><div class="lb">ACC</div><div class="vl">&nbsp;</div></div>
          <div><div class="lb">Cat. hab.</div><div class="vl">{categoria}</div></div></div>
        <div style="display:flex;gap:20px"><div><div class="lb">Nº registro</div><div class="vl">{registro}</div></div>
          <div><div class="lb">Validade</div><div class="vl">{g.br(validade)}</div></div><div><div class="lb">1ª habilitação</div><div class="vl">{g.br(primeira)}</div></div></div>
      </div></div></div>"""
    return campos, [png(corpo)]


def cnh_app(r, i):
    p = pessoa(r); uf = p["uf"]
    emissao = g.data_aleatoria(r, dt.date(2021, 1, 1), dt.date(2026, 9, 30)); validade = emissao.replace(year=emissao.year + 10)
    registro = "".join(str(r.randint(0, 9)) for _ in range(11)); categoria = r.choice(["B", "AB", "D"])
    campos = {"nome": p["nome"], "data_nascimento": p["nasc"].isoformat(), "filiacao_pai": p["pai"], "filiacao_mae": p["mae"],
              "cpf": p["cpf"], "numero_registro": registro, "categoria": categoria, "validade": validade.isoformat(),
              "data_emissao": emissao.isoformat()}
    item = lambda l, v: f"<div style='padding:9px 0;border-bottom:1px solid #ddd'><div class='lb'>{l}</div><div class='vl' style='margin:0'>{v}</div></div>"
    tela = f"""<div class="c" style="width:420px;height:860px;background:#fff;border-radius:28px;border:10px solid #111">
      <div style="background:#0c7a43;color:#fff;margin:-20px -24px 14px;padding:22px 24px;font-weight:700">CNH digital · app fictício</div>
      {item('Nome completo', g.esc(p['nome']))}{item('CPF', p['cpf'])}{item('Data de nascimento', g.br(p['nasc']))}
      {item('Nº do registro', registro)}{item('Categoria', categoria)}{item('Emissão', g.br(emissao))}{item('Validade', g.br(validade))}
      {item('Filiação', g.esc(p['pai']) + '<br>' + g.esc(p['mae']))}</div>"""
    return campos, [png(tela, 420, 860)]


VARIANTES = [
    ("rg-antigo", "RG", [rg_v_rotulos_ao_lado, rg_v_verso_unico, rg_v_ordem_invertida], 3),
    ("cin", "CIN", [cin_bilingue, cin_app], 3),
    ("cnh", "CNH", [cnh_antiga, cnh_app], 3),
]


def main():
    r = random.Random(1129)
    for tipo, nome_tipo, funcoes, primeiro in VARIANTES:
        pasta = g.SAIDA / tipo
        for k, fn in enumerate(funcoes):
            ident = f"{tipo}-ficticio-{primeiro + k:02d}"
            campos, faces = fn(r, k)
            imgs = "".join(f"<img src='data:image/jpeg;base64,{g.img_b64(f, 'JPEG')}' style='width:70%;margin-bottom:10px'><br>" for f in faces)
            g.chrome_pdf(g.pagina(f"<div style='padding:30px'>{imgs}</div>"), pasta / f"{ident}.pdf")
            g.chrome_pdf(g.pdf_impressao_cartao(faces), pasta / f"{ident}-impressao.pdf")
            gab = {"arquivo": f"{tipo}/{ident}.pdf", "tipo": nome_tipo, "ficticio": True, "variante": fn.__name__, "campos": campos}
            (pasta / f"{ident}.json").write_text(json.dumps(gab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("ok", ident, fn.__name__)
    destino = Path.home() / "Downloads" / "documentos-ficticios"
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(g.SAIDA, destino, ignore=shutil.ignore_patterns("*.md"))
    print("cópia em", destino)


if __name__ == "__main__":
    main()
