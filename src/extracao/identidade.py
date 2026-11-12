"""Extração genérica dos documentos de identificação (RG antigo, CIN e CNH).

Versão 2, depois do teste de generalização (11/11/2026): as regras da versão 1 procuravam
rótulos em posições fixas e falharam em layouts novos (cobertura de 27%). Aqui cada campo tem
uma lista de rótulos sinônimos (inclusive bilíngues) e o valor é procurado em quatro lugares:
na própria linha, ao lado, abaixo e, para o RG antigo, acima do rótulo.
"""

from __future__ import annotations

import re
from typing import Callable, List, Optional

from .validacoes import cpf_valido

# Importados do pipeline em tempo de execução para evitar import circular
Campo = Leitura = Resultado = None  # type: ignore


def _deps():
    from . import pipeline as p
    return p


ROTULOS = {
    "nome": [r"^[\d\s]*(?:\d E \d )?NOME(?: COMPLETO| CIVIL| E SOBRENOME)?\b(?!.*SOCIAL)", r"(?<!SOCIAL )\bNAME\b(?!.*SOCIAL)"],
    "data_nascimento": [r"NASCIMENTO", r"DATE OF BIRTH", r"\bNASC\b"],
    "naturalidade": [r"NATURALIDADE", r"PLACE OF BIRTH"],
    "registro_geral": [r"REGISTRO GERAL(?!\s*[-/]\s*CPF)", r"^\s*R\.?G\.?\b", r"\bRG\s*:"],
    "validade": [r"VALIDADE", r"DATE OF EXPIRY", r"\bVALIDA ATE\b"],
    "data_emissao": [r"EMISSAO", r"DATE OF ISSUE"],
    "data_expedicao": [r"EXPEDICAO"],
    "numero_registro": [r"N\W{0,2}\s*(?:DO )?REGISTRO", r"^[\d\s]*REGISTRO\b"],
    "categoria": [r"CAT\.? HAB", r"\bCATEGORIA\b"],
    "pai": [r"^\s*PAI\b"],
    "mae": [r"^\s*MAE\b"],
    "filiacao": [r"FILIACAO", r"\bPARENTS\b", r"FILHO\(?A?\)? DE", r"FILHA DE"],
}

RE_ORGAO = re.compile(r"\b(SSP|PC|SDS|SESP|SESDEC|DETRAN|IGP|SJS|SEJUSP|PCII|IIRGD|SPTC|DGPC|SEDS)\s*[/-]\s*([A-Z]{2})\b")
RE_RG = re.compile(r"^(?:[A-Z]{2}\s*-\s*)?\d{1,2}\.?\d{3}\.?\d{3}(?:-?[\dX])?$")


def _casa(n: str, rotulos: List[str]) -> Optional[re.Match]:
    for r in rotulos:
        m = re.search(r, n)
        if m:
            return m
    return None


def valor(leitura, campo: str, aceita: Callable[[str], bool]) -> Optional[str]:
    """Procura o valor de um campo pelos rótulos sinônimos: na linha, ao lado, abaixo e acima."""
    p = _deps()
    rotulos = ROTULOS[campo]
    for i, n in enumerate(leitura.norm):
        m = _casa(n, rotulos)
        if not m:
            continue
        rot = leitura.linhas[i]
        texto = rot.texto
        # 1. na própria linha, depois do rótulo (ex.: "Nome: FULANO", "RG: 12.345.678-9")
        resto = texto[m.end():] if len(texto) == len(n) else ""
        resto = re.sub(r"^[\s:.\-]*(/\s*[A-Za-z ]+:?)?[\s:.\-]*", "", resto)  # tira o rótulo em inglês
        if resto and aceita(resto):
            return resto.strip()
        altura = max(rot.altura, 0.004)
        # 2. ao lado, na mesma altura
        lado = sorted((l.x, j) for j, l in enumerate(leitura.linhas)
                      if j != i and abs((l.y + l.altura / 2) - (rot.y + altura / 2)) < altura * 0.8
                      and 0 < l.x - (rot.x + rot.largura) < 0.45)
        for _, j in lado:
            if aceita(leitura.linhas[j].texto):
                return leitura.linhas[j].texto.strip()
            break  # só o vizinho imediato
        # 3. abaixo, na mesma coluna
        # o mais próximo na vertical E alinhado à esquerda com o rótulo (evita a coluna vizinha)
        abaixo = sorted((l.y - rot.y + 2 * abs(l.x - rot.x), j) for j, l in enumerate(leitura.linhas)
                        if j != i and 0 < l.y - rot.y <= 0.07 and abs(l.x - rot.x) < 0.08)
        for _, j in abaixo[:3]:
            if aceita(leitura.linhas[j].texto) and not _casa(leitura.norm[j], sum(ROTULOS.values(), [])):
                return leitura.linhas[j].texto.strip()
        # 4. acima (RG antigo: rótulo embaixo do valor), ou à esquerda se a face estiver girada
        v = p._acima(leitura, re.escape(n[m.start():m.end()]), aceita)
        if v:
            return v
    return None


def eh_data(s: str) -> bool:
    return bool(_deps().data_iso(s))


def eh_nome(s: str) -> bool:
    return _deps()._nome(s)


def eh_cidade_uf(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Z ]+\s*[-/,]\s*[A-Z]{2}", _deps().sem_acento(s).strip()))


def eh_rg(s: str) -> bool:
    t = _deps().sem_acento(s).strip()
    return bool(RE_RG.match(t)) and not cpf_valido(t)


def provavelmente_feminino(nome: str) -> bool:
    primeiro = nome.split()[0] if nome.split() else ""
    return primeiro.endswith("A") and primeiro not in {"LUCA", "JOSHUA", "NIKITA"}


def extrair(leitura, r, tipo: str):
    p = _deps()
    c = r.campos
    mrz = p.ler_mrz(leitura)
    up = lambda s: p.sem_acento(s).strip(" /:")

    # CPF: qualquer número com dígito verificador válido
    if (cpf := p._cpf(leitura)):
        c["cpf"] = cpf

    # Nome do titular
    if (v := valor(leitura, "nome", eh_nome)):
        c["nome"] = p.Campo(up(v), "rótulo")
    if "_nome_mrz" in mrz:
        partes = mrz["_nome_mrz"].valor.split()
        prenome, sobrenome = partes[0], partes[-1]
        if "nome" in c and prenome in c["nome"].valor:
            c["nome"].validado = True
        else:
            alvo = next((l.texto for l in leitura.linhas if eh_nome(l.texto) and prenome in up(l.texto)), None)
            if alvo:
                c["nome"] = p.Campo(up(alvo), "mrz", True)
            else:
                for l in leitura.linhas:
                    n = up(l.texto)
                    if eh_nome(l.texto) and n.endswith(sobrenome) and n.split()[0] in partes[1:-1]:
                        c["nome"] = p.Campo(" ".join(partes[:partes.index(n.split()[0])] + n.split()), "mrz + ocr")
                        break

    # Datas
    if "data_nascimento" in mrz:
        c["data_nascimento"] = mrz["data_nascimento"]
    elif (v := valor(leitura, "data_nascimento", eh_data)):
        c["data_nascimento"] = p.Campo(p.data_iso(v), "rótulo")
    if "sexo" in mrz:
        c["sexo"] = mrz["sexo"]
    for campo in ("validade", "data_emissao", "data_expedicao"):
        if (v := valor(leitura, campo, eh_data)):
            c[campo] = p.Campo(p.data_iso(v), "rótulo")

    # Filiação, em ordem de confiabilidade
    _filiacao(leitura, c, up)

    # Naturalidade e órgão
    if (v := valor(leitura, "naturalidade", eh_cidade_uf)):
        cidade, uf = re.split(r"\s*[-/,]\s*", up(v))[:2]
        c["naturalidade"] = p.Campo(f"{cidade.strip()}, {uf}", "rótulo")
    if (m := RE_ORGAO.search(leitura.texto)):
        c["orgao_expedidor"] = p.Campo(f"{m.group(1)}/{m.group(2)}", "padrão")

    if tipo == "cnh":
        if (v := valor(leitura, "numero_registro", lambda s: bool(re.fullmatch(r"\d{9,11}", s.strip())))):
            c["numero_registro"] = p.Campo(v.strip(), "rótulo")
        if (v := valor(leitura, "categoria", lambda s: bool(re.fullmatch(r"(ACC|[A-E]{1,2})", s.strip())))):
            c["categoria"] = p.Campo(v.strip(), "rótulo")
    elif tipo == "cin":
        if "cpf" in c:
            c["registro_geral"] = p.Campo(p.digitos(c["cpf"].valor), "cpf", True)
    elif tipo == "rg":
        if (v := valor(leitura, "registro_geral", eh_rg)):
            t = up(v)
            c["registro_geral"] = p.Campo(t if "-" in t and not re.match(r"^[A-Z]{2}", t) else p.digitos(t), "rótulo")


def _filiacao(leitura, c, up):
    p = _deps()
    # 1. Rotulada: "Pai:" e "Mãe:"
    pai = valor(leitura, "pai", eh_nome)
    mae = valor(leitura, "mae", eh_nome)
    if pai or mae:
        if pai:
            c["filiacao_pai"] = p.Campo(up(pai), "rótulo")
        if mae:
            c["filiacao_mae"] = p.Campo(up(mae), "rótulo")
        return
    # 2. Numa linha só: "FILHO(A) DE FULANO E BELTRANA"
    for i, n in enumerate(leitura.norm):
        m = re.search(r"FILH[OA]\(?A?\)? DE\s*:?\s*(.+)", n)
        alvo = m.group(1) if m else None
        if not alvo and _casa(n, ROTULOS["filiacao"]):
            prox = [l for l in leitura.linhas if 0 < l.y - leitura.linhas[i].y <= 0.05 and abs(l.x - leitura.linhas[i].x) < 0.12]
            alvo = up(prox[0].texto) if len(prox) == 1 and " E " in up(prox[0].texto) else None
        if alvo and " E " in alvo:
            a, b = [s.strip() for s in alvo.split(" E ", 1)]
            if eh_nome(a) and eh_nome(b):
                c["filiacao_pai"], c["filiacao_mae"] = p.Campo(a, "rótulo"), p.Campo(b, "rótulo")
                return
    # 3. RG antigo: "PAI /" numa linha e a mãe na linha mais próxima
    linhas = [l for l in leitura.linhas if eh_nome(l.texto) and l.confianca >= 0.5]
    i_pai = next((i for i, l in enumerate(linhas) if l.texto.rstrip().endswith("/")), None)
    if i_pai is not None:
        pai = linhas[i_pai]
        c["filiacao_pai"] = p.Campo(up(pai.texto), "posição")
        viz = [l for l in linhas if l is not pai and ((l.x - pai.x) ** 2 + (l.y - pai.y) ** 2) ** 0.5 <= 0.06]
        if viz:
            mae_l = min(viz, key=lambda l: (l.x - pai.x) ** 2 + (l.y - pai.y) ** 2)
            c["filiacao_mae"] = p.Campo(up(mae_l.texto), "posição")
        if "nome" not in c or c["nome"].valor in (c["filiacao_pai"].valor, c.get("filiacao_mae", c["filiacao_pai"]).valor):
            usados = {c[k].valor for k in ("filiacao_pai", "filiacao_mae") if k in c}
            tit = next((l for l in linhas if up(l.texto) not in usados), None)
            if tit:
                c["nome"] = p.Campo(up(tit.texto), "posição")
        return
    # 4. Bloco "FILIAÇÃO" com dois nomes, sem dizer quem é quem: a ordem vem da posição,
    #    corrigida pelo gênero provável do prenome (a mãe costuma ter prenome terminado em A).
    for i, n in enumerate(leitura.norm):
        if not _casa(n, ROTULOS["filiacao"]):
            continue
        base = leitura.linhas[i]
        blocos = sorted((l for l in leitura.linhas if 0 < l.y - base.y <= 0.09 and abs(l.x - base.x) < 0.12
                         and (eh_nome(l.texto) or l.confianca < 0.5)), key=lambda l: l.y)[:2]
        nomes = [up(l.texto) if (l.confianca >= 0.5 and eh_nome(l.texto)) else None for l in blocos]
        if len(nomes) == 2 and all(nomes) and provavelmente_feminino(nomes[0]) and not provavelmente_feminino(nomes[1]):
            nomes.reverse()
        for chave, nome in zip(("filiacao_pai", "filiacao_mae"), nomes):
            if nome:
                c[chave] = p.Campo(nome, "posição")
        return
    # 5. Sem rótulo nenhum (RG antigo de layout desconhecido): titular, pai e mãe pela ordem
    if "nome" not in c and len(linhas) >= 1:
        c["nome"] = p.Campo(up(linhas[0].texto), "posição")


def classificar_identidade(leitura) -> Optional[str]:
    """Decide entre CNH, CIN e RG antigo; None se não parecer documento de identificação."""
    t = leitura.texto
    tem_id = bool(re.search(r"\bNOME\b|\bNAME\b", t)) and bool(
        re.search(r"FILIACAO|PARENTS|FILH[OA]|\bPAI\b|\bMAE\b|NASCIMENTO|DATE OF BIRTH", t))
    if not tem_id and "HABILITACAO" not in t and "IDENTIDADE" not in t:
        return None
    # "CNH" sozinho não basta: o verso do RG antigo tem um campo "CNH" para anotar o número
    if re.search(r"HABILITACAO|CAT\.? HAB|CNH DIGITAL", t) or (re.search(r"\bCATEGORIA\b", t) and re.search(r"REGISTRO", t)):
        return "cnh"
    mrz = bool(re.search(r"I<BRA|IDBRA|ID<BRA", t.replace(" ", "")))
    if re.search(r"IDENTIDADE NACIONAL|NOME SOCIAL|PERSONAL NUMBER|REGISTRO GERAL\s*[-/]\s*CPF", t) or mrz:
        return "cin"
    # RG antigo não tem validade; a CIN tem
    if "IDENTIDADE" in t and re.search(r"VALIDADE|DATE OF EXPIRY", t) and not re.search(r"REGISTRO GERAL|\bRG\b", t):
        return "cin"
    if re.search(r"CARTEIRA DE IDENTIDADE|REGISTRO GERAL|\bRG\b|SEGURANCA PUBLICA|INSTITUTO DE IDENTIFICACAO|IDENTIDADE", t):
        return "rg"
    return None
