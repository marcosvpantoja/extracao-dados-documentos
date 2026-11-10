#!/usr/bin/env python3
"""
Gera o conjunto de desenvolvimento: documentos FICTÍCIOS + gabaritos.

Para cada tipo gera:
  - <id>.pdf            arquivo para o canal de importação
  - <id>-impressao.pdf  versão para imprimir e fotografar (canal cross-device), quando difere
  - <id>.json           gabarito com o valor correto de cada campo

Todos os dados são inventados. Identificadores (CPF, CNPJ, chave NF-e, linha digitável,
MRZ) têm dígitos verificadores válidos para exercitar as validações automáticas.
Nenhum brasão, logotipo oficial ou elemento de segurança real é reproduzido.

Uso: python3 scripts/gerar_exemplos.py [--n 2] [--seed 29]
Requer: Google Chrome (headless) e Pillow.
"""
import argparse, base64, datetime as dt, html, io, json, random, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "exemplos"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MARCA = "DOCUMENTO FICTÍCIO · SEM VALOR LEGAL"

# ---------------------------------------------------------------- dados fictícios
NOMES_M = ["BRUNO", "DIEGO", "FABIO", "HUGO", "JOAO", "MATEUS", "OTAVIO", "RAFAEL", "TIAGO", "VINICIUS"]
NOMES_F = ["ANA", "CARLA", "ELISA", "GABRIELA", "ISABELA", "LARISSA", "NATALIA", "PRISCILA", "SABRINA", "VALERIA"]
MEIOS_M = ["EDUARDO", "HENRIQUE", "LUIZ", "PAULO", "ROBERTO", "CARLOS"]
MEIOS_F = ["APARECIDA", "CRISTINA", "MARIA", "VITORIA", "HELENA", "BEATRIZ"]
SOBRENOMES = ["ALMEIDA", "BARBOSA", "CARDOSO", "DUARTE", "FERREIRA", "GOMES", "LIMA", "MOREIRA",
              "NASCIMENTO", "OLIVEIRA", "PEREIRA", "RIBEIRO", "SANTOS", "TEIXEIRA", "VIEIRA", "ROCHA"]
CIDADES = [("CAMPINAS", "SP"), ("BELO HORIZONTE", "MG"), ("CURITIBA", "PR"), ("RECIFE", "PE"),
           ("GOIANIA", "GO"), ("MANAUS", "AM"), ("BELEM", "PA"), ("PORTO ALEGRE", "RS"),
           ("SALVADOR", "BA"), ("FLORIANOPOLIS", "SC"), ("NATAL", "RN"), ("CUIABA", "MT")]
UF_COD = {"SP": 35, "MG": 31, "PR": 41, "PE": 26, "GO": 52, "AM": 13, "PA": 15, "RS": 43,
          "BA": 29, "SC": 42, "RN": 24, "MT": 51}
EMPRESAS = ["COMERCIAL HORIZONTE EXEMPLO LTDA", "DISTRIBUIDORA AURORA FICTICIA LTDA",
            "PAPELARIA MODELO DE TESTE ME", "TECNOLOGIA SINTETICA EXEMPLO S.A.",
            "ALIMENTOS DEMONSTRACAO LTDA"]
PRODUTOS = [("PAPEL A4 75G CX 10 RESMAS", 289.90), ("CANETA ESFEROGRAFICA AZUL CX 50", 42.50),
            ("TONER COMPATIVEL PRETO", 159.00), ("CADEIRA ESCRITORIO GIRATORIA", 649.00),
            ("CABO HDMI 2M", 29.90), ("MOUSE OPTICO USB", 39.90), ("GRAMPEADOR METAL 26/6", 54.00)]
BANCOS = [("001", "BANCO DO BRASIL"), ("237", "BRADESCO"), ("341", "ITAU"), ("033", "SANTANDER")]


def nome_pessoa(r, sobrenome_fixo=None, sexo=None):
    sexo = sexo or r.choice("MF")
    nomes, meios = (NOMES_M, MEIOS_M) if sexo == "M" else (NOMES_F, MEIOS_F)
    s2 = sobrenome_fixo or r.choice(SOBRENOMES)
    return f"{r.choice(nomes)} {r.choice(meios)} {r.choice(SOBRENOMES)} {s2}"


def data_aleatoria(r, ini, fim):
    return ini + dt.timedelta(days=r.randint(0, (fim - ini).days))


def br(d):  # dd/mm/aaaa
    return d.strftime("%d/%m/%Y")


def moeda(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------------------------------------------------------------- identificadores válidos
def cpf(r):
    n = [r.randint(0, 9) for _ in range(9)]
    for k in (10, 11):
        s = sum(d * w for d, w in zip(n, range(k, 1, -1)))
        n.append(0 if s % 11 < 2 else 11 - s % 11)
    t = "".join(map(str, n))
    return f"{t[:3]}.{t[3:6]}.{t[6:9]}-{t[9:]}"


def cnpj(r):
    n = [r.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    for pesos in ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]):
        s = sum(d * w for d, w in zip(n, pesos))
        n.append(0 if s % 11 < 2 else 11 - s % 11)
    t = "".join(map(str, n))
    return f"{t[:2]}.{t[2:5]}.{t[5:8]}/{t[8:12]}-{t[12:]}"


def so_digitos(s):
    return "".join(c for c in s if c.isdigit())


def mod11_nfe(base):
    s, p = 0, 2
    for d in reversed(base):
        s += int(d) * p
        p = 2 if p == 9 else p + 1
    dv = 11 - s % 11
    return 0 if dv >= 10 else dv


def chave_nfe(uf, emissao, cnpj_emit, serie, numero, r):
    base = (f"{UF_COD[uf]:02d}{emissao:%y%m}{so_digitos(cnpj_emit)}55{serie:03d}{numero:09d}1"
            f"{r.randint(0, 99999999):08d}")
    return base + str(mod11_nfe(base))


def mod10(num):
    s, peso = 0, 2
    for d in reversed(num):
        p = int(d) * peso
        s += p // 10 + p % 10
        peso = 1 if peso == 2 else 2
    return (10 - s % 10) % 10


def mod11_boleto(num):
    s, p = 0, 2
    for d in reversed(num):
        s += int(d) * p
        p = 2 if p == 9 else p + 1
    dv = 11 - s % 11
    return 1 if dv in (0, 10, 11) else dv


def fator_vencimento(venc):
    # Regra Febraban: o fator reiniciou em 1000 em 22/02/2025.
    return 1000 + (venc - dt.date(2025, 2, 22)).days


def boleto_codigos(banco, venc, valor, r):
    livre = "".join(str(r.randint(0, 9)) for _ in range(25))
    fv = f"{fator_vencimento(venc):04d}{int(round(valor * 100)):010d}"
    sem_dv = f"{banco}9{fv}{livre}"
    dv = mod11_boleto(sem_dv)
    barras = f"{banco}9{dv}{fv}{livre}"
    c1 = f"{banco}9{livre[:5]}"; c1 += str(mod10(c1))
    c2 = livre[5:15]; c2 += str(mod10(c2))
    c3 = livre[15:25]; c3 += str(mod10(c3))
    linha = f"{c1[:5]}.{c1[5:]} {c2[:5]}.{c2[5:]} {c3[:5]}.{c3[5:]} {dv} {fv}"
    return barras, linha


def i2of5_svg(code, altura=60):
    """Código de barras Interleaved 2 of 5 (padrão dos boletos) em SVG."""
    pad = {"0": "nnwwn", "1": "wnnnw", "2": "nwnnw", "3": "wwnnn", "4": "nnwnw",
           "5": "wnwnn", "6": "nwwnn", "7": "nnnww", "8": "wnnwn", "9": "nwnwn"}
    n, w = 1.2, 3.0
    barras = [(True, n), (False, n), (True, n), (False, n)]
    for a, b in zip(code[::2], code[1::2]):
        for x, y in zip(pad[a], pad[b]):
            barras += [(True, w if x == "w" else n), (False, w if y == "w" else n)]
    barras += [(True, w), (False, n), (True, n)]
    x, rects = 0.0, []
    for preto, larg in barras:
        if preto:
            rects.append(f'<rect x="{x:.1f}" y="0" width="{larg:.1f}" height="{altura}"/>')
        x += larg
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{x:.0f}" height="{altura}">{"".join(rects)}</svg>'


def mrz_dv(s):
    val = {**{str(i): i for i in range(10)}, **{chr(65 + i): 10 + i for i in range(26)}, "<": 0}
    return str(sum(val[c] * (7, 3, 1)[i % 3] for i, c in enumerate(s)) % 10)


def mrz_td1(doc, nasc, sexo, validade, nome, opcional=""):
    doc9 = doc[:9].ljust(9, "<")
    l1 = f"I<BRA{doc9}{mrz_dv(doc9)}{opcional[:15].ljust(15, '<')}"
    n, v = nasc.strftime("%y%m%d"), validade.strftime("%y%m%d")
    l2 = f"{n}{mrz_dv(n)}{sexo}{v}{mrz_dv(v)}BRA" + "<" * 11
    comp = l1[5:30] + l2[0:7] + l2[8:15] + l2[18:29]
    l2 = l2[:29] + mrz_dv(comp)
    partes = nome.split()
    l3 = (partes[-1] + "<<" + "<".join(partes[:-1]))[:30].ljust(30, "<")
    return [l1, l2, l3]


# ---------------------------------------------------------------- renderização
CSS_BASE = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,Helvetica,sans-serif;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.marca{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;z-index:99}
.marca span{transform:rotate(-30deg);font-size:34px;font-weight:700;color:rgba(200,0,0,.16);white-space:nowrap;letter-spacing:2px}
"""


def pagina(corpo, css="", tamanho="A4", marca=True):
    m = f'<div class="marca"><span>{MARCA}</span></div>' if marca else ""
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>@page{{size:{tamanho};margin:0}}"
            f"{CSS_BASE}{css}</style></head><body>{m}{corpo}</body></html>")


def chrome_pdf(doc_html, destino):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "doc.html"; f.write_text(doc_html, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={destino}", f.as_uri()], check=True, capture_output=True)


def chrome_png(doc_html, largura, altura):
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "doc.html"; f.write_text(doc_html, encoding="utf-8")
        out = Path(tmp) / "shot.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={largura},{altura}",
                        f"--screenshot={out}", f.as_uri()], check=True, capture_output=True)
        return Image.open(out).convert("RGB")


def img_b64(img, fmt="PNG"):
    b = io.BytesIO(); img.save(b, fmt, quality=88); return base64.b64encode(b.getvalue()).decode()


def foto_placeholder():
    # Silhueta genérica no lugar da foto: nenhum rosto real.
    return ("<svg viewBox='0 0 100 125' xmlns='http://www.w3.org/2000/svg'><rect width='100' height='125' fill='#d9dde3'/>"
            "<circle cx='50' cy='45' r='22' fill='#9aa3ad'/><path d='M12 125c4-30 24-42 38-42s34 12 38 42z' fill='#9aa3ad'/></svg>")


def qr_ilustrativo(r, n=29):
    im = Image.new("1", (n, n), 1); d = ImageDraw.Draw(im)
    for y in range(n):
        for x in range(n):
            if r.random() < 0.45: d.point((x, y), 0)
    for ox, oy in ((0, 0), (n - 7, 0), (0, n - 7)):
        d.rectangle([ox, oy, ox + 6, oy + 6], fill=1); d.rectangle([ox, oy, ox + 6, oy + 6], outline=0)
        d.rectangle([ox + 2, oy + 2, ox + 4, oy + 4], fill=0)
    return im.resize((n * 8, n * 8), Image.NEAREST).convert("RGB")


def esc(s):
    return html.escape(str(s))


def assinatura(nome):
    return f"<span style='font-family:\"Snell Roundhand\",\"Brush Script MT\",cursive;font-size:20px;color:#1b3a8a'>{esc(nome.title().split()[0])} {esc(nome.title().split()[-1])}</span>"


# ---------------------------------------------------------------- CNH (CNH-e + impressão)
CSS_CARTAO = """
.c{width:860px;height:560px;padding:18px 22px;position:relative;overflow:hidden;border-radius:14px}
.lbl{font-size:11px;color:#3a4a3a;text-transform:uppercase;letter-spacing:.3px}
.val{font-size:19px;font-weight:700;font-family:'Courier New',monospace;margin-bottom:9px}
.cx{border:1.5px solid #6c7c6c;border-radius:6px;padding:3px 8px;margin-bottom:8px;background:rgba(255,255,255,.45)}
.cab{text-align:center;font-weight:700;letter-spacing:1px}
"""


def cnh(r, i):
    cidade, uf = r.choice(CIDADES)
    nasc = data_aleatoria(r, dt.date(1960, 1, 1), dt.date(2004, 12, 31))
    primeira = data_aleatoria(r, nasc + dt.timedelta(days=18 * 365 + 5), dt.date(2024, 6, 30))
    emissao = data_aleatoria(r, max(primeira, dt.date(2021, 1, 1)), dt.date(2026, 9, 30))
    validade = emissao.replace(year=emissao.year + r.choice([5, 10]))
    sobrenome = r.choice(SOBRENOMES); sexo = r.choice("MF")
    nome = nome_pessoa(r, sobrenome, sexo)
    pai = nome_pessoa(r, sobrenome, "M"); mae = nome_pessoa(r, sexo="F")
    categoria = r.choice(["B", "AB", "A", "C", "D", "AE"])
    rg_num = str(r.randint(1000000, 99999999)); orgao = f"SSP {uf}"
    registro = "".join(str(r.randint(0, 9)) for _ in range(11))
    c = cpf(r)
    local_em, uf_em = r.choice(CIDADES)
    mrz = mrz_td1(registro[:9], nasc, sexo, validade, nome, so_digitos(c))
    campos = {
        "nome": nome, "data_nascimento": nasc.isoformat(), "local_nascimento": f"{cidade}, {uf}",
        "filiacao_pai": pai, "filiacao_mae": mae, "documento_identidade": f"{rg_num} {orgao}",
        "cpf": c, "numero_registro": registro, "categoria": categoria,
        "primeira_habilitacao": primeira.isoformat(), "data_emissao": emissao.isoformat(),
        "validade": validade.isoformat(), "nacionalidade": "BRASILEIRO(A)",
        "local_emissao": f"{local_em}, {uf_em}", "observacoes": r.choice(["", "EAR", "A"]),
    }
    fundo = "background:linear-gradient(135deg,#e6f2e3,#d4e9d0 60%,#e9f3e6)"
    frente = f"""<div class="c" style="{fundo}">
      <div class="cab" style="font-size:16px">CARTEIRA NACIONAL DE HABILITAÇÃO · MODELO FICTÍCIO</div>
      <div style="display:flex;gap:18px;margin-top:12px">
        <div style="width:200px"><div style="width:200px;height:250px">{foto_placeholder()}</div>
          <div style="margin-top:14px;border-top:1px solid #555;text-align:center">{assinatura(nome)}<div class="lbl">assinatura do portador</div></div></div>
        <div style="flex:1">
          <div class="cx"><div class="lbl">2 e 1 nome e sobrenome</div><div class="val">{esc(nome)}</div></div>
          <div style="display:flex;gap:8px"><div class="cx" style="flex:1"><div class="lbl">3 data, local e UF de nascimento</div><div class="val">{br(nasc)}, {esc(cidade)}, {uf}</div></div>
            <div class="cx"><div class="lbl">1ª habilitação</div><div class="val">{br(primeira)}</div></div></div>
          <div style="display:flex;gap:8px"><div class="cx" style="flex:1"><div class="lbl">4a data emissão</div><div class="val">{br(emissao)}</div></div>
            <div class="cx" style="flex:1"><div class="lbl">4b validade</div><div class="val" style="color:#b00">{br(validade)}</div></div>
            <div class="cx"><div class="lbl">9 cat. hab.</div><div class="val" style="color:#b00">{categoria}</div></div></div>
          <div class="cx"><div class="lbl">4c doc. identidade / órg. emissor / UF</div><div class="val">{rg_num} {orgao}</div></div>
          <div style="display:flex;gap:8px"><div class="cx" style="flex:1"><div class="lbl">4d CPF</div><div class="val">{c}</div></div>
            <div class="cx" style="flex:1"><div class="lbl">5 nº registro</div><div class="val" style="color:#b00">{registro}</div></div></div>
          <div class="cx"><div class="lbl">nacionalidade</div><div class="val">BRASILEIRO(A)</div></div>
          <div class="cx"><div class="lbl">filiação</div><div class="val" style="font-size:16px">{esc(pai)}<br>{esc(mae)}</div></div>
        </div></div></div>"""
    linhas = "".join(f"<tr><td>{k}</td><td>{br(validade) if k in categoria else ''}</td></tr>" for k in ["ACC", "A", "A1", "B", "B1", "C", "C1", "D", "D1", "BE", "CE", "DE"])
    verso = f"""<div class="c" style="{fundo}">
      <div style="display:flex;gap:22px">
        <table style="border-collapse:collapse;font-size:14px;width:330px" border="1" cellpadding="3"><tr><th>cat.</th><th>validade</th></tr>{linhas}</table>
        <div style="flex:1"><div class="cx" style="height:150px"><div class="lbl">12 observações</div><div class="val">{campos['observacoes']}</div></div>
          <div class="cx"><div class="lbl">local</div><div class="val">{esc(local_em)}, {uf_em}</div></div></div></div>
      <div style="margin-top:26px;font-family:'Courier New',monospace;font-size:24px;line-height:1.5;letter-spacing:2px">{'<br>'.join(esc(l) for l in mrz)}</div></div>"""
    img_f = chrome_png(pagina(frente, CSS_CARTAO, marca=False) .replace("<body>", "<body style='width:860px'>"), 860, 560)
    img_v = chrome_png(pagina(verso, CSS_CARTAO, marca=False).replace("<body>", "<body style='width:860px'>"), 860, 560)

    # CNH-e: PDF A4 com a carteira como IMAGEM (igual ao documento real: exige OCR)
    pdf_e = f"""<div style="background:#3d3d3d;color:#fff;padding:14px 28px;font-weight:700">DOCUMENTO DIGITAL DE HABILITAÇÃO · EMISSOR FICTÍCIO</div>
      <div style="display:flex;gap:28px;padding:28px">
        <div style="width:58%"><img src="data:image/jpeg;base64,{img_b64(img_f, 'JPEG')}" style="width:100%">
          <img src="data:image/jpeg;base64,{img_b64(img_v, 'JPEG')}" style="width:100%;margin-top:10px"></div>
        <div style="flex:1;font-size:12px"><b>QR-CODE (ilustrativo)</b><br><img src="data:image/png;base64,{img_b64(qr_ilustrativo(r))}" style="width:100%;margin:8px 0">
          Documento fictício gerado para testes de extração de dados. Não possui assinatura digital nem validade legal.</div></div>"""
    return campos, {"pdf": pagina(pdf_e)}, (img_f, img_v)


# ---------------------------------------------------------------- RG antigo (escaneado) + impressão
def rg_antigo(r, i):
    cidade, uf = r.choice(CIDADES)
    estado_emissor = r.choice(list(UF_COD))
    nasc = data_aleatoria(r, dt.date(1960, 1, 1), dt.date(2008, 12, 31))
    exped = data_aleatoria(r, max(nasc + dt.timedelta(days=3650), dt.date(2000, 1, 1)), dt.date(2025, 12, 31))
    sobrenome = r.choice(SOBRENOMES)
    nome = nome_pessoa(r, sobrenome); pai = nome_pessoa(r, sobrenome, "M"); mae = nome_pessoa(r, sexo="F")
    rg = str(r.randint(1000000, 99999999)); c = cpf(r)
    via = r.choice(["1VIA", "2VIA"])
    matricula = " ".join("".join(str(r.randint(0, 9)) for _ in range(k)) for k in (6, 2, 2, 4, 1, 5, 3, 7, 2))
    campos = {
        "nome": nome, "filiacao_pai": pai, "filiacao_mae": mae, "data_nascimento": nasc.isoformat(),
        "naturalidade": f"{cidade}, {uf}", "orgao_expedidor": f"PC/{estado_emissor}",
        "estado_emissor": estado_emissor, "registro_geral": rg, "via": via,
        "data_expedicao": exped.isoformat(), "cpf": c, "registro_civil": matricula,
    }
    css = """.c{width:860px;height:600px;padding:22px 26px;position:relative;
      background:repeating-linear-gradient(45deg,#cfe3c6 0 6px,#d9eccf 6px 12px);border:14px solid #4f8a46}
      .l{font-size:12px;font-weight:700;color:#222}.v{font-size:20px;font-weight:700;font-family:Arial;margin-bottom:12px}"""
    frente = f"""<div class="c"><div style="text-align:center;font-weight:700;font-size:22px;letter-spacing:3px">ESTADO FICTÍCIO DE {estado_emissor}</div>
      <div style="text-align:center;font-size:12px;margin-bottom:14px">INSTITUTO DE IDENTIFICAÇÃO · MODELO DE TESTE</div>
      <div style="display:flex;gap:20px"><div style="width:190px;height:240px">{foto_placeholder()}</div>
        <div style="flex:1"><div class="l">NOME</div><div class="v">{esc(nome)}</div>
          <div class="l">FILIAÇÃO</div><div class="v" style="font-size:17px">{esc(pai)} /<br>{esc(mae)}</div>
          <div style="display:flex;gap:30px"><div><div class="l">DATA NASCIMENTO</div><div class="v">{br(nasc)}</div></div>
            <div><div class="l">NATURALIDADE</div><div class="v">{esc(cidade)} - {uf}</div></div></div>
          <div style="display:flex;gap:30px"><div><div class="l">ÓRGÃO EXPEDIDOR</div><div class="v">PC/{estado_emissor}</div></div>
            <div><div class="l">OBSERVAÇÃO</div><div class="v">&nbsp;</div></div></div></div></div>
      <div style="margin-top:8px;border-top:1px solid #333;width:420px;text-align:center">{assinatura(nome)}<div class="l">ASSINATURA DO TITULAR</div></div>
      <div style="position:absolute;bottom:4px;left:0;right:0;text-align:center;font-weight:700;letter-spacing:6px;color:#2f5d29">CARTEIRA DE IDENTIDADE</div></div>"""
    verso = f"""<div class="c"><div style="text-align:center;font-weight:700;letter-spacing:2px;margin-bottom:16px">VÁLIDA EM TODO O TERRITÓRIO NACIONAL · MODELO FICTÍCIO</div>
      <div style="display:flex;gap:28px"><div><div class="l">CPF</div><div class="v">{c}</div></div><div><div class="l">REGISTRO GERAL</div><div class="v">{rg}</div></div>
        <div><div class="l">VIA</div><div class="v">{via}</div></div><div><div class="l">DATA DE EXPEDIÇÃO</div><div class="v">{br(exped)}</div></div></div>
      <div class="l">REGISTRO CIVIL · MATRÍCULA ÚNICA</div><div class="v" style="font-size:17px">{matricula}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px 20px;font-size:12px;font-weight:700;margin-top:6px">
        <div>T. ELEITOR</div><div>CTPS</div><div>SÉRIE / UF</div><div>NIS/PIS/PASEP</div><div>IDENTIDADE PROFISSIONAL</div><div></div><div>CERT. MILITAR</div><div>CNH</div><div>CNS</div></div>
      <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:30px">
        <div style="border-top:1px solid #333;width:300px;text-align:center" class="l">ASSINATURA DO DIRETOR</div>
        <div style="width:150px;height:170px;border:1px solid #555;background:#fff;text-align:center;font-size:11px;font-weight:700">POLEGAR DIREITO</div></div></div>"""
    img_f = chrome_png(pagina(frente, css, marca=False), 860, 600)
    img_v = chrome_png(pagina(verso, css, marca=False), 860, 600)

    # Escaneamento simulado: frente e verso lado a lado, girados 90°, levemente borrados e amarelados
    scan = Image.new("RGB", (img_f.width * 2 + 80, img_f.height + 60), (246, 244, 238))
    scan.paste(img_f, (20, 30)); scan.paste(img_v, (img_f.width + 60, 30))
    scan = scan.rotate(90 if i % 2 else -90, expand=True, fillcolor=(246, 244, 238))
    scan = scan.filter(ImageFilter.GaussianBlur(0.8))
    scan = ImageEnhance.Color(scan).enhance(1.25); scan = ImageEnhance.Brightness(scan).enhance(1.06)
    pdf_scan = f"<img src='data:image/jpeg;base64,{img_b64(scan, 'JPEG')}' style='width:100%'>"
    return campos, {"pdf": pagina(pdf_scan, tamanho="210mm 600mm")}, (img_f, img_v)


# ---------------------------------------------------------------- CIN (nova identidade)
def cin(r, i):
    cidade, uf = r.choice(CIDADES)
    nasc = data_aleatoria(r, dt.date(1960, 1, 1), dt.date(2008, 12, 31))
    emissao = data_aleatoria(r, dt.date(2023, 7, 1), dt.date(2026, 9, 30))
    validade = emissao.replace(year=emissao.year + 10)
    sobrenome = r.choice(SOBRENOMES)
    sexo = r.choice("MF")
    nome = nome_pessoa(r, sobrenome, sexo); pai = nome_pessoa(r, sobrenome, "M"); mae = nome_pessoa(r, sexo="F")
    c = cpf(r); orgao = f"SSP/{uf}"
    mrz = mrz_td1(so_digitos(c)[:9], nasc, sexo, validade, nome, so_digitos(c))
    campos = {
        "nome": nome, "sexo": sexo, "nacionalidade": "BRA", "data_nascimento": nasc.isoformat(),
        "naturalidade": f"{cidade}, {uf}", "filiacao_pai": pai, "filiacao_mae": mae,
        "cpf": c, "registro_geral": so_digitos(c), "orgao_expedidor": orgao,
        "local_emissao": f"{cidade}, {uf}", "data_emissao": emissao.isoformat(), "validade": validade.isoformat(),
    }
    css = CSS_CARTAO + ".c{background:linear-gradient(120deg,#e3eef9,#cfe0f2 55%,#eaf2fb)}"
    frente = f"""<div class="c"><div class="cab" style="font-size:16px">CARTEIRA DE IDENTIDADE NACIONAL · MODELO FICTÍCIO</div>
      <div style="display:flex;gap:18px;margin-top:12px"><div style="width:200px;height:250px">{foto_placeholder()}</div>
      <div style="flex:1"><div class="lbl">nome</div><div class="val">{esc(nome)}</div>
        <div style="display:flex;gap:26px"><div><div class="lbl">sexo</div><div class="val">{sexo}</div></div><div><div class="lbl">nacionalidade</div><div class="val">BRA</div></div>
          <div><div class="lbl">data de nascimento</div><div class="val">{br(nasc)}</div></div></div>
        <div class="lbl">CPF / registro geral</div><div class="val">{c}</div>
        <div style="display:flex;gap:26px"><div><div class="lbl">validade</div><div class="val">{br(validade)}</div></div><div><div class="lbl">emissão</div><div class="val">{br(emissao)}</div></div></div>
      </div></div><div style="margin-top:8px;width:400px;border-top:1px solid #444;text-align:center">{assinatura(nome)}<div class="lbl">assinatura do titular</div></div></div>"""
    verso = f"""<div class="c"><div class="lbl">filiação</div><div class="val" style="font-size:17px">{esc(pai)}<br>{esc(mae)}</div>
      <div style="display:flex;gap:26px"><div><div class="lbl">naturalidade</div><div class="val">{esc(cidade)}/{uf}</div></div>
        <div><div class="lbl">órgão expedidor</div><div class="val">{orgao}</div></div><div><div class="lbl">local de emissão</div><div class="val">{esc(cidade)}/{uf}</div></div></div>
      <div style="margin-top:40px;font-family:'Courier New',monospace;font-size:24px;line-height:1.5;letter-spacing:2px">{'<br>'.join(esc(l) for l in mrz)}</div></div>"""
    img_f = chrome_png(pagina(frente, css, marca=False), 860, 560)
    img_v = chrome_png(pagina(verso, css, marca=False), 860, 560)
    corpo = f"""<div style="padding:30px"><div style="font-weight:700;margin-bottom:14px">CIN digital · emissor fictício</div>
      <img src="data:image/jpeg;base64,{img_b64(img_f, 'JPEG')}" style="width:75%"><br>
      <img src="data:image/jpeg;base64,{img_b64(img_v, 'JPEG')}" style="width:75%;margin-top:10px"></div>"""
    return campos, {"pdf": pagina(corpo)}, (img_f, img_v)


# ---------------------------------------------------------------- Fatura de serviço (texto nativo)
def fatura(r, i):
    cidade, uf = r.choice(CIDADES)
    emissora = r.choice(["CONECTA FIBRA EXEMPLO S.A.", "LUZ E FORCA FICTICIA S.A.", "AGUA MODELO SANEAMENTO S.A."])
    cn = cnpj(r); cliente = nome_pessoa(r).title()
    num_cliente = str(r.randint(100000, 9999999)); num_fatura = str(r.randint(10 ** 11, 10 ** 12 - 1))
    mes = data_aleatoria(r, dt.date(2026, 1, 1), dt.date(2026, 10, 1)).replace(day=1)
    venc = (mes + dt.timedelta(days=40)).replace(day=r.choice([5, 10, 15, 20]))
    valor = round(r.uniform(59, 480), 2)
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    ref = f"{meses[mes.month - 1]}/{mes.year}"
    situacao = r.choice(["PAGA", "EM ABERTO"])
    endereco = f"Rua Exemplo das Flores, {r.randint(10, 2999)} - Centro - {cidade.title()} / {uf} - CEP: {r.randint(10, 99)}.{r.randint(100, 999)}-{r.randint(100, 999)}"
    banco, nome_banco = r.choice(BANCOS)
    _, linha = boleto_codigos(banco, venc, valor, r)
    campos = {
        "emissora": emissora, "cnpj_emissora": cn, "cliente": cliente, "numero_cliente": num_cliente,
        "numero_fatura": num_fatura, "referencia": ref, "vencimento": venc.isoformat(),
        "valor_total": f"{valor:.2f}", "endereco": endereco, "situacao": situacao,
        "linha_digitavel": linha if situacao == "EM ABERTO" else "",
    }
    cor = r.choice(["#14365d", "#5a1a1a", "#1d4d3a"])
    css = f""".top{{background:{cor};color:#fff;display:flex;justify-content:space-between;align-items:center;padding:28px 40px}}
      .box{{background:#fff;color:#111;border-radius:10px;padding:12px 18px}} .sec{{padding:18px 40px}}
      .cards{{display:flex;gap:18px}} .card{{flex:1;border:1.5px solid #333;border-radius:10px;padding:12px;text-align:center}}
      .card b{{display:block;color:{cor};margin-bottom:6px}}"""
    boleto_html = (f"<div class='sec'><b>Pague com boleto</b><div style='font-family:Courier New;font-size:16px;margin-top:6px'>{nome_banco} · {linha}</div></div>"
                   if situacao == "EM ABERTO" else "<div class='sec' style='background:#d8f3df'>✔ Fatura paga.</div>")
    corpo = f"""<div class="top"><div style="font-size:30px;font-weight:900">{esc(emissora.split()[0])}</div>
        <div class="box"><b>DEMONSTRATIVO DE COBRANÇA</b><br><small><b>Número da fatura:</b> {num_fatura}<br><b>Referente a:</b> {ref}</small></div>
        <div class="box"><b>VALOR TOTAL</b><br><span style="font-size:22px;font-weight:700">R$ {moeda(valor)}</span></div></div>
      <div class="sec" style="background:#f0f0f0"><b>Endereço:</b><br><small>{esc(endereco)}</small></div>
      <div class="sec"><h3 style="color:{cor}">Olá {esc(cliente)}. Sua fatura chegou!</h3></div>
      <div class="sec cards"><div class="card"><b>Número do Cliente</b>{num_cliente}</div><div class="card"><b>Vencimento</b>{br(venc)}</div><div class="card"><b>Valor total</b>R$ {moeda(valor)}</div></div>
      <div class="sec"><b style="color:{cor}">RESUMO</b><hr><div style="display:flex;justify-content:space-between"><span>Serviços contratados</span><span>R$ {moeda(valor)}</span></div></div>
      {boleto_html}
      <div class="sec" style="font-size:11px;margin-top:120px"><b>BENEFICIÁRIO:</b> {esc(emissora)} - CNPJ: {cn}<br><b>CLIENTE:</b> {esc(cliente)}<br>
        <b>REFERENTE A:</b> {ref} &nbsp; <b>VENCIMENTO:</b> {br(venc)} &nbsp; <b>TOTAL:</b> R$ {moeda(valor)}</div>"""
    return campos, {"pdf": pagina(corpo, css)}, None


# ---------------------------------------------------------------- NF-e / DANFE (texto nativo)
def nfe(r, i):
    cid_e, uf_e = r.choice(CIDADES); cid_d, uf_d = r.choice(CIDADES)
    emit = r.choice(EMPRESAS); cn_e = cnpj(r)
    dest_pj = r.random() < 0.5
    dest = r.choice([e for e in EMPRESAS if e != emit]) if dest_pj else nome_pessoa(r)
    doc_d = cnpj(r) if dest_pj else cpf(r)
    emissao = data_aleatoria(r, dt.date(2026, 1, 1), dt.date(2026, 10, 31))
    serie, numero = 1, r.randint(1000, 999999)
    chave = chave_nfe(uf_e, emissao, cn_e, serie, numero, r)
    itens = []
    for prod, preco in r.sample(PRODUTOS, r.randint(2, 4)):
        q = r.randint(1, 6); itens.append({"descricao": prod, "quantidade": q, "valor_unitario": f"{preco:.2f}", "valor_total": f"{q * preco:.2f}"})
    total = round(sum(float(x["valor_total"]) for x in itens), 2)
    natureza = r.choice(["VENDA DE MERCADORIA", "VENDA DE MERCADORIA ADQUIRIDA DE TERCEIROS"])
    campos = {
        "numero": f"{numero:09d}", "serie": f"{serie:03d}", "chave_acesso": chave, "data_emissao": emissao.isoformat(),
        "emitente_razao_social": emit, "emitente_cnpj": cn_e, "emitente_municipio": f"{cid_e}, {uf_e}",
        "destinatario_nome": dest, "destinatario_documento": doc_d, "destinatario_municipio": f"{cid_d}, {uf_d}",
        "natureza_operacao": natureza, "valor_total": f"{total:.2f}", "itens": itens,
    }
    ch = " ".join(chave[k:k + 4] for k in range(0, 44, 4))
    n = f"{numero:09d}"; nf = f"{n[:3]}.{n[3:6]}.{n[6:]}"
    css = """.d{padding:24px 26px;font-size:11px} table{width:100%;border-collapse:collapse} td,th{border:1px solid #000;padding:3px 5px;vertical-align:top}
      .t{font-size:8px;text-transform:uppercase;color:#333;display:block} .g{font-weight:700;font-size:12px} .h{background:#eee;font-weight:700;font-size:9px;padding:2px 5px;border:1px solid #000;border-bottom:0;margin-top:6px}"""
    linhas = "".join(f"<tr><td>{k + 1:03d}</td><td>{esc(it['descricao'])}</td><td>UN</td><td style='text-align:right'>{it['quantidade']}</td>"
                     f"<td style='text-align:right'>{moeda(float(it['valor_unitario']))}</td><td style='text-align:right'>{moeda(float(it['valor_total']))}</td></tr>" for k, it in enumerate(itens))
    corpo = f"""<div class="d">
      <table><tr><td style="width:75%"><span class="t">Recebemos de {esc(emit)} os produtos constantes da nota fiscal indicada ao lado</span><br><br></td><td><span class="g">NF-e</span><br>Nº {nf}<br>SÉRIE {serie:03d}</td></tr></table>
      <table style="margin-top:6px"><tr><td style="width:40%"><span class="g">{esc(emit)}</span><br>Av. Fictícia, {r.randint(10, 999)} - {esc(cid_e.title())}/{uf_e}</td>
        <td style="width:18%;text-align:center"><span class="g" style="font-size:16px">DANFE</span><br>Documento Auxiliar da Nota Fiscal Eletrônica<br>1 - SAÍDA<br><b>Nº {nf}<br>SÉRIE {serie:03d}</b></td>
        <td><span class="t">Chave de acesso</span><span class="g">{ch}</span><br><br><span class="t">Consulta de autenticidade</span>Documento fictício · sem consulta</td></tr>
        <tr><td colspan="2"><span class="t">Natureza da operação</span>{natureza}</td><td><span class="t">Protocolo de autorização</span>FICTÍCIO {r.randint(10 ** 14, 10 ** 15 - 1)}</td></tr>
        <tr><td><span class="t">Inscrição estadual</span>ISENTO</td><td></td><td><span class="t">CNPJ</span>{cn_e}</td></tr></table>
      <div class="h">DESTINATÁRIO / REMETENTE</div>
      <table><tr><td style="width:55%"><span class="t">Nome / razão social</span>{esc(dest)}</td><td><span class="t">CNPJ / CPF</span>{doc_d}</td><td><span class="t">Data da emissão</span>{br(emissao)}</td></tr>
        <tr><td><span class="t">Endereço</span>Rua Modelo, {r.randint(10, 999)}</td><td><span class="t">Município</span>{esc(cid_d.title())}</td><td><span class="t">UF</span>{uf_d}</td></tr></table>
      <div class="h">CÁLCULO DO IMPOSTO</div>
      <table><tr><td><span class="t">Base de cálculo do ICMS</span>0,00</td><td><span class="t">Valor do ICMS</span>0,00</td><td><span class="t">Valor total dos produtos</span>{moeda(total)}</td><td><span class="t">Valor total da nota</span><span class="g">{moeda(total)}</span></td></tr></table>
      <div class="h">DADOS DOS PRODUTOS / SERVIÇOS</div>
      <table><tr><th>Cód.</th><th>Descrição</th><th>Un.</th><th>Qtd.</th><th>V. unit.</th><th>V. total</th></tr>{linhas}</table>
      <div class="h">DADOS ADICIONAIS</div><table><tr><td style="height:80px">Documento fictício gerado para testes de extração de dados. Sem valor fiscal.</td></tr></table></div>"""
    return campos, {"pdf": pagina(corpo, css)}, None


# ---------------------------------------------------------------- Boleto (texto nativo)
def boleto(r, i):
    banco, nome_banco = r.choice(BANCOS)
    benef = r.choice(EMPRESAS); cn = cnpj(r)
    pagador = nome_pessoa(r); doc_p = cpf(r)
    venc = data_aleatoria(r, dt.date(2026, 11, 15), dt.date(2027, 3, 31))
    valor = round(r.uniform(80, 4800), 2)
    barras, linha = boleto_codigos(banco, venc, valor, r)
    nosso = str(r.randint(10 ** 10, 10 ** 11 - 1))
    campos = {
        "linha_digitavel": linha, "codigo_barras": barras, "banco": f"{banco} - {nome_banco}",
        "beneficiario_nome": benef, "beneficiario_documento": cn, "pagador_nome": pagador,
        "pagador_documento": doc_p, "valor": f"{valor:.2f}", "vencimento": venc.isoformat(),
    }
    css = """.b{padding:30px 34px;font-size:11px} table{width:100%;border-collapse:collapse} td{border:1px solid #000;padding:3px 6px;vertical-align:top}
      .t{font-size:8px;color:#333;display:block} .top{display:flex;align-items:flex-end;border-bottom:2px solid #000;padding-bottom:3px;margin-top:10px}
      .bk{font-weight:700;font-size:16px;padding-right:12px;border-right:2px solid #000} .cd{font-weight:700;font-size:18px;padding:0 12px;border-right:2px solid #000}
      .ln{font-family:'Courier New',monospace;font-weight:700;font-size:15px;padding-left:12px}"""
    def bloco(titulo):
        return f"""<div class="top"><span class="bk">{nome_banco}</span><span class="cd">{banco}-9</span><span class="ln">{linha}</span></div>
          <table><tr><td colspan="4"><span class="t">Local de pagamento</span>PAGÁVEL EM QUALQUER BANCO ATÉ O VENCIMENTO</td><td style="width:22%"><span class="t">Vencimento</span><b>{br(venc)}</b></td></tr>
            <tr><td colspan="4"><span class="t">Beneficiário</span>{esc(benef)} - CNPJ {cn}</td><td><span class="t">Agência / código do beneficiário</span>{r.randint(1000, 9999)} / {r.randint(10000, 99999)}-{r.randint(0, 9)}</td></tr>
            <tr><td><span class="t">Data do documento</span>{br(venc - dt.timedelta(days=20))}</td><td><span class="t">Nº do documento</span>{r.randint(1000, 99999)}</td><td><span class="t">Espécie doc.</span>DM</td><td><span class="t">Aceite</span>N</td><td><span class="t">Nosso número</span>{nosso}</td></tr>
            <tr><td colspan="4" rowspan="2"><span class="t">Instruções</span>Não receber após 30 dias do vencimento.<br>Documento fictício gerado para testes. Sem valor de cobrança.</td><td><span class="t">(=) Valor do documento</span><b>{moeda(valor)}</b></td></tr>
            <tr><td><span class="t">(=) Valor cobrado</span>&nbsp;</td></tr>
            <tr><td colspan="5"><span class="t">Pagador</span>{esc(pagador)} - CPF {doc_p}</td></tr></table>
          <div style="text-align:right;font-size:9px">{titulo}</div>"""
    corpo = f"""<div class="b"><div style="text-align:right;font-size:9px">Recibo do Pagador</div>{bloco('Autenticação mecânica')}
      <div style="border-top:1px dashed #000;margin:40px 0 10px"></div>{bloco('Ficha de Compensação')}
      <div style="margin-top:6px">{i2of5_svg(barras)}</div></div>"""
    return campos, {"pdf": pagina(corpo, css)}, None


# ---------------------------------------------------------------- impressão de cartões
def pdf_impressao_cartao(faces, largura_mm=86):
    imgs = "".join(f"<img src='data:image/jpeg;base64,{img_b64(f, 'JPEG')}' style='width:{largura_mm}mm;margin:0 6mm 6mm 0;border:0.2mm dashed #999'>" for f in faces)
    corpo = (f"<div style='padding:15mm'><p style='font-size:10pt;margin-bottom:6mm'>Imprimir em 100% (sem ajustar à página). "
             f"Recortar e fotografar frente e verso pelo fluxo cross-device.</p>{imgs}</div>")
    return pagina(corpo)


TIPOS = {"cnh": cnh, "rg-antigo": rg_antigo, "cin": cin, "fatura": fatura, "nfe": nfe, "boleto": boleto}
NOME_TIPO = {"cnh": "CNH", "rg-antigo": "RG", "cin": "CIN", "fatura": "FATURA", "nfe": "NFE", "boleto": "BOLETO"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2, help="documentos por tipo")
    ap.add_argument("--seed", type=int, default=29)
    ap.add_argument("--copiar-para", default=str(Path.home() / "Downloads" / "documentos-ficticios"))
    a = ap.parse_args()
    r = random.Random(a.seed)
    for tipo, fn in TIPOS.items():
        pasta = SAIDA / tipo; pasta.mkdir(parents=True, exist_ok=True)
        for i in range(1, a.n + 1):
            ident = f"{tipo}-ficticio-{i:02d}"
            campos, saidas, faces = fn(r, i)
            chrome_pdf(saidas["pdf"], pasta / f"{ident}.pdf")
            if faces:
                chrome_pdf(pdf_impressao_cartao(faces), pasta / f"{ident}-impressao.pdf")
            gabarito = {"arquivo": f"{tipo}/{ident}.pdf", "tipo": NOME_TIPO[tipo], "ficticio": True, "campos": campos}
            (pasta / f"{ident}.json").write_text(json.dumps(gabarito, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("ok", pasta.relative_to(RAIZ) / ident)
    if a.copiar_para:
        destino = Path(a.copiar_para)
        if destino.exists(): shutil.rmtree(destino)
        shutil.copytree(SAIDA, destino, ignore=shutil.ignore_patterns("*.md"))
        print("cópia em", destino)


if __name__ == "__main__":
    main()
