"""Classificação e extração por regras, a partir das linhas do OCR (ADR 0002: regras primeiro).

O objetivo é o que o cadastro precisa: identificação do cliente e os dados das provas.
Cada campo sai com a origem (rótulo, padrão, MRZ, linha digitável) e se passou por validação
com dígito verificador. Campo não encontrado fica de fora, nunca inventado (RF-15).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Dict, List, Optional

from .ocr import Linha
from .validacoes import (
    boleto_valor, boleto_vencimento, chave_nfe_valida, cnpj_valido, cpf_valido,
    linha_digitavel_valida, mrz_digito,
)

TIPOS = ("cnh", "cin", "rg", "nfe", "boleto", "fatura")


@dataclass
class Campo:
    valor: str
    origem: str  # "rótulo", "padrão", "mrz", "linha digitável"
    validado: bool = False  # passou por dígito verificador ou cruzamento


@dataclass
class Resultado:
    tipo: str  # um de TIPOS ou "nao_reconhecido"
    confianca_tipo: float
    campos: Dict[str, Campo] = field(default_factory=dict)
    legivel: bool = True
    motivo: Optional[str] = None  # por que pedir nova foto


# ---------------------------------------------------------------- utilidades

def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").upper()


def digitos(s: str) -> str:
    return re.sub(r"\D", "", s)


RE_DATA = re.compile(r"\b(\d{2})[/.-](\d{2})[/.-](\d{4})\b")
RE_CPF = re.compile(r"\b\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}\b")
RE_CNPJ = re.compile(r"\b\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-.\s]?\d{2}\b")
RE_VALOR = re.compile(r"R?\$?\s*(\d{1,3}(?:\.\d{3})*,\d{2})\b")


def data_iso(texto: str) -> Optional[str]:
    m = RE_DATA.search(texto)
    if not m:
        return None
    d, mes, a = map(int, m.groups())
    try:
        return date(a, mes, d).isoformat()
    except ValueError:
        return None


def valor_decimal(texto: str) -> Optional[str]:
    m = RE_VALOR.search(texto)
    return m.group(1).replace(".", "").replace(",", ".") if m else None


class Leitura:
    """Acesso às linhas do OCR por rótulo e posição."""

    def __init__(self, linhas: List[Linha]):
        self.linhas = [l for l in linhas if l.texto.strip()]
        self.norm = [sem_acento(l.texto) for l in self.linhas]
        self.texto = "\n".join(self.norm)

    def tem(self, *padroes: str) -> bool:
        return any(re.search(p, self.texto) for p in padroes)

    def abaixo(self, rotulo: str, aceita: Callable[[str], bool] = lambda s: True, distancia: float = 0.07) -> Optional[str]:
        """Primeiro texto aceito logo abaixo (ou à direita) do rótulo, na mesma coluna."""
        for i, n in enumerate(self.norm):
            if not re.search(rotulo, n):
                continue
            r = self.linhas[i]
            # o valor pode estar na própria linha, depois do rótulo
            resto = re.split(rotulo, n, maxsplit=1)[-1].strip(" :.-")
            if resto and aceita(self.linhas[i].texto[-len(resto):]):
                return self.linhas[i].texto[-len(resto):].strip(" :")
            candidatos = [
                (l.y - r.y, j) for j, l in enumerate(self.linhas)
                if j != i and 0 < l.y - r.y <= distancia and abs(l.x - r.x) < 0.12
            ]
            for _, j in sorted(candidatos):
                if aceita(self.linhas[j].texto) and not _parece_rotulo(self.norm[j]):
                    return self.linhas[j].texto.strip()
        return None


ROTULOS_CONHECIDOS = ("NOME", "DATA", "FILIACAO", "CPF", "REGISTRO", "VALIDADE", "EMISSAO", "NACIONALIDADE",
                      "DOC.", "CAT", "LOCAL", "NATURALIDADE", "SEXO", "ORGAO", "OBSERVA")
# Textos impressos no próprio documento que parecem nomes, mas não são.
NAO_NOMES = ("POLEGAR", "ASSINATURA", "IDENTIDADE", "ESTADO", "DIRETOR", "INSTITUTO", "CARTEIRA", "REPUBLICA",
             "VALIDA", "TERRITORIO", "FICTICIO", "MODELO", "DOCUMENTO", "PROFISSIONAL", "SECRETARIA", "SEGURANCA",
             "HABILITACAO", "NACIONAL", "BRASIL", "TITULAR", "PORTADOR", "EMISSOR", "DIGITAL", "VALOR", "LEGAL", "SEM", "FICTIC", "CUMENT", "IDENTIF")


def _parece_rotulo(n: str) -> bool:
    return bool(re.match(r"^\d{0,2}[A-Z]?\s", n)) and any(r in n for r in ROTULOS_CONHECIDOS) and not re.search(r"\d{4}", n)


def _nome(s: str) -> bool:
    if s.strip() != s.strip().upper():
        return False
    n = sem_acento(s).strip(" /")
    return bool(re.fullmatch(r"[A-Z][A-Z' ]{5,}", n)) and len(n.split()) >= 2 and not any(r in n for r in ROTULOS_CONHECIDOS + NAO_NOMES)


# ---------------------------------------------------------------- MRZ (CNH e CIN, padrão ICAO TD1)

def ler_mrz(leitura: Leitura) -> Dict[str, Campo]:
    linhas = [re.sub(r"\s", "", n).replace("«", "<") for n in leitura.norm if n.count("<") >= 3]
    linhas = [l for l in linhas if len(l) >= 25]
    campos: Dict[str, Campo] = {}
    if len(linhas) < 2:
        return campos
    l2 = next((l for l in linhas if re.match(r"^\d{6}\d[MF<]\d{6}\d", l)), None)
    if l2:
        nasc, dv_nasc, sexo = l2[0:6], l2[6], l2[7]
        if dv_nasc.isdigit() and mrz_digito(nasc) == int(dv_nasc):
            aa, mm, dd = int(nasc[:2]), int(nasc[2:4]), int(nasc[4:6])
            seculo = 1900 if aa > date.today().year % 100 else 2000
            try:
                campos["data_nascimento"] = Campo(date(seculo + aa, mm, dd).isoformat(), "mrz", True)
            except ValueError:
                pass
        if sexo in "MF":
            campos["sexo"] = Campo(sexo, "mrz", True)
    l3 = next((l for l in linhas if re.match(r"^[A-Z]+<<[A-Z<]+$", l)), None)
    if l3:
        sobrenome, _, prenomes = l3.partition("<<")
        nome = " ".join(prenomes.replace("<", " ").split() + sobrenome.replace("<", " ").split())
        # A MRZ corta nomes longos (30 caracteres); serve para conferir, não para preencher sozinha.
        campos["_nome_mrz"] = Campo(nome, "mrz", False)
    return campos


# ---------------------------------------------------------------- classificação

def classificar(leitura: Leitura) -> tuple:
    t = leitura.texto
    pontos = {k: 0.0 for k in TIPOS}
    if "HABILITACAO" in t:
        pontos["cnh"] += 3
    if "IDENTIDADE NACIONAL" in t:
        pontos["cin"] += 3
    elif "CARTEIRA DE IDENTIDADE" in t:
        pontos["rg"] += 1
    if re.search(r"(?<!CPF / )REGISTRO GERAL", t) and "IDENTIDADE NACIONAL" not in t:
        pontos["rg"] += 2.5
    if re.search(r"I<BRA|IDBRA|ID<BRA", t.replace(" ", "")) and "HABILITACAO" not in t:
        pontos["cin"] += 2
    if "DANFE" in t or "NOTA FISCAL ELETRONICA" in t:
        pontos["nfe"] += 3
    if re.search(r"\b\d{5}[.\s]?\d{5}\s+\d{5}[.\s]?\d{6}\s+\d{5}[.\s]?\d{6}\s+\d\s+\d{14}\b", t):
        pontos["boleto"] += 2.5
    if "BENEFICIARIO" in t:
        pontos["boleto"] += 0.5
    if re.search(r"\bFATURA\b|DEMONSTRATIVO|CONSUMO|REFERENTE A", t):
        pontos["fatura"] += 3
    if "PAGADOR" in t or "CEDENTE" in t:
        pontos["boleto"] += 1
    melhor = max(pontos, key=pontos.get)
    total = sum(pontos.values())
    if pontos[melhor] < 1.5:
        return "nao_reconhecido", 0.0
    return melhor, round(pontos[melhor] / total, 2)


# ---------------------------------------------------------------- extração por tipo

def _cpf(leitura: Leitura) -> Optional[Campo]:
    for m in RE_CPF.finditer(leitura.texto):
        if cpf_valido(m.group()):
            d = digitos(m.group())
            return Campo(f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}", "padrão", True)
    return None


def _cnpjs(leitura: Leitura) -> List[str]:
    vistos = []
    for m in RE_CNPJ.finditer(leitura.texto):
        d = digitos(m.group())
        if cnpj_valido(d) and d not in vistos:
            vistos.append(d)
    return [f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}" for d in vistos]


def _pessoal(leitura: Leitura, r: Resultado):
    c = r.campos
    mrz = ler_mrz(leitura)
    nome = leitura.abaixo(r"\bNOME", _nome)
    if nome:
        c["nome"] = Campo(sem_acento(nome).strip(" /"), "rótulo")
    if "_nome_mrz" in mrz:
        partes = mrz["_nome_mrz"].valor.split()
        prenome, sobrenome = partes[0], partes[-1]
        if nome and prenome in c["nome"].valor:
            c["nome"].validado = True
        elif not nome:
            # rótulo ilegível: o titular é a linha com o prenome e o sobrenome da MRZ
            alvo = next((l.texto for l in leitura.linhas if _nome(l.texto)
                         and prenome in sem_acento(l.texto) and sem_acento(l.texto).rstrip().endswith(mrz["_nome_mrz"].valor.split()[-1])), None)
            # o último "prenome" da MRZ pode estar truncado; o sobrenome vem antes do <<
            if not alvo:
                alvo = next((l.texto for l in leitura.linhas if _nome(l.texto) and prenome in sem_acento(l.texto)), None)
            if alvo:
                c["nome"] = Campo(sem_acento(alvo).strip(" /"), "mrz", True)
            else:
                # o OCR perdeu o começo do nome: completa com os prenomes da MRZ
                # (ex.: OCR "APARECIDA BARBOSA RIBEIRO" + MRZ "NATALIA APARECIDA ..." )
                prenomes = partes[:-1]
                for l in leitura.linhas:
                    n = sem_acento(l.texto).strip(" /")
                    if _nome(l.texto) and n.endswith(sobrenome) and n.split()[0] in prenomes[1:]:
                        faltam = prenomes[:prenomes.index(n.split()[0])]
                        c["nome"] = Campo(" ".join(faltam + n.split()), "mrz + ocr")
                        break
    if (cpf := _cpf(leitura)):
        c["cpf"] = cpf
    if "data_nascimento" in mrz:
        c["data_nascimento"] = mrz["data_nascimento"]
    else:
        v = leitura.abaixo(r"NASCIMENTO", lambda s: bool(data_iso(s)))
        if v:
            c["data_nascimento"] = Campo(data_iso(v), "rótulo")
    if "sexo" in mrz:
        c["sexo"] = mrz["sexo"]
    # filiação: as duas linhas logo abaixo do rótulo, na ordem pai e mãe. Linha ilegível
    # ocupa o lugar dela e deixa o campo em branco, em vez de empurrar a outra para cima.
    for i, n in enumerate(leitura.norm):
        if "FILIACAO" in n:
            base = leitura.linhas[i]
            abaixo = sorted((l for l in leitura.linhas
                             if 0 < l.y - base.y <= 0.09 and abs(l.x - base.x) < 0.12
                             and (_nome(l.texto) or l.confianca < 0.5)), key=lambda l: l.y)[:2]
            for chave, l in zip(("filiacao_pai", "filiacao_mae"), abaixo):
                if l.confianca >= 0.5 and _nome(l.texto):
                    c[chave] = Campo(sem_acento(l.texto).strip(" /"), "rótulo")
            break


def _cnh(leitura: Leitura, r: Resultado):
    _pessoal(leitura, r)
    if (v := leitura.abaixo(r"REGISTRO", lambda s: bool(re.fullmatch(r"\d{9,11}", s.strip())))):
        r.campos["numero_registro"] = Campo(digitos(v), "rótulo")
    for rot, chave in ((r"VALIDADE", "validade"), (r"EMISSAO", "data_emissao")):
        if (v := leitura.abaixo(rot, lambda s: bool(data_iso(s)))):
            r.campos[chave] = Campo(data_iso(v), "rótulo")
    if (v := leitura.abaixo(r"CAT\.? HAB", lambda s: bool(re.fullmatch(r"[A-E]{1,2}", s.strip())))):
        r.campos["categoria"] = Campo(v.strip(), "rótulo")


def _cin(leitura: Leitura, r: Resultado):
    _pessoal(leitura, r)
    _orgao_e_naturalidade(leitura, r)
    if "cpf" in r.campos:  # na CIN, o registro geral é o próprio CPF
        r.campos["registro_geral"] = Campo(digitos(r.campos["cpf"].valor), "cpf", True)
    if (v := leitura.abaixo(r"VALIDADE", lambda s: bool(data_iso(s)))):
        r.campos["validade"] = Campo(data_iso(v), "rótulo")


def _rg(leitura: Leitura, r: Resultado):
    """No RG antigo, nome e filiação vêm em linhas próprias, com os rótulos longe, embaixo.
    A ordem das linhas em maiúsculas é: titular, pai, mãe."""
    c = r.campos
    linhas = [l for l in leitura.linhas if _nome(l.texto) and l.confianca >= 0.5]
    # A filiação vem como "PAI /" numa linha e "MÃE" na seguinte; o titular é o outro nome.
    i_pai = next((i for i, l in enumerate(linhas) if l.texto.rstrip().endswith("/")), None)
    if i_pai is not None:
        c["filiacao_pai"] = Campo(sem_acento(linhas[i_pai].texto).strip(" /"), "posição")
        pai = linhas[i_pai]
        vizinhas = [l for l in linhas if l is not pai and ((l.x - pai.x) ** 2 + (l.y - pai.y) ** 2) ** 0.5 <= 0.06]
        if vizinhas:  # a mãe é a linha mais próxima do pai (a face pode estar girada)
            mae = min(vizinhas, key=lambda l: (l.x - pai.x) ** 2 + (l.y - pai.y) ** 2)
            c["filiacao_mae"] = Campo(sem_acento(mae.texto).strip(" /"), "posição")
    usados = {c[k].valor for k in ("filiacao_pai", "filiacao_mae") if k in c}
    titular = next((l for l in linhas if sem_acento(l.texto).strip(" /") not in usados), None)
    if titular:
        c["nome"] = Campo(sem_acento(titular.texto).strip(" /"), "posição")
    if (cpf := _cpf(leitura)):
        c["cpf"] = cpf
    if (v := leitura.abaixo(r"NASCIMENTO", lambda s: bool(data_iso(s)))):
        c["data_nascimento"] = Campo(data_iso(v), "rótulo")
    eh_rg = lambda s: bool(re.fullmatch(r"[\d.\-X]{7,12}", s.strip())) and not cpf_valido(s)
    if (v := leitura.abaixo(r"REGISTRO GERAL", eh_rg)) or (v := _acima(leitura, r"REGISTRO GERAL", eh_rg)):
        r.campos["registro_geral"] = Campo(digitos(v), "rótulo")
    _orgao_e_naturalidade(leitura, r)
    if (v := leitura.abaixo(r"EXPEDICAO", lambda s: bool(data_iso(s)))):
        r.campos["data_expedicao"] = Campo(data_iso(v), "rótulo")


def _nfe(leitura: Leitura, r: Resultado):
    # A chave costuma ser impressa em grupos de 4 e quebrar em duas linhas: junta as linhas
    # só de números logo abaixo de "CHAVE DE ACESSO".
    for i, n in enumerate(leitura.norm):
        if "CHAVE DE ACESSO" not in n:
            continue
        base = leitura.linhas[i]
        seguintes = sorted((l for l in leitura.linhas if 0 < l.y - base.y <= 0.04 and abs(l.x - base.x) < 0.1
                            and re.fullmatch(r"[\d\s.]+", l.texto.strip())), key=lambda l: l.y)
        juntos = "".join(digitos(l.texto) for l in seguintes)
        if len(juntos) >= 44 and chave_nfe_valida(juntos[:44]):
            r.campos["chave_acesso"] = Campo(juntos[:44], "rótulo", True)
    if "chave_acesso" not in r.campos:
        t = re.sub(r"(?<=\d)[\s.]+(?=\d)", "", leitura.texto)
        for m in re.finditer(r"\d{44}", t):
            if chave_nfe_valida(m.group()):
                r.campos["chave_acesso"] = Campo(m.group(), "padrão", True)
                break
    cnpjs = _cnpjs(leitura)
    if cnpjs:
        r.campos["emitente_cnpj"] = Campo(cnpjs[0], "padrão", True)
    if (v := leitura.abaixo(r"VALOR TOTAL DA NOTA", lambda s: bool(valor_decimal(s)), 0.05)):
        r.campos["valor_total"] = Campo(valor_decimal(v), "rótulo")
    if (v := leitura.abaixo(r"DATA DA EMISSAO|DATA DE EMISSAO", lambda s: bool(data_iso(s)))):
        r.campos["data_emissao"] = Campo(data_iso(v), "rótulo")


def _boleto(leitura: Leitura, r: Resultado):
    for m in re.finditer(r"\d{5}[.\s]?\d{5}\s+\d{5}[.\s]?\d{6}\s+\d{5}[.\s]?\d{6}\s+\d\s+\d{14}", leitura.texto):
        linha = m.group()
        if linha_digitavel_valida(linha):
            r.campos["linha_digitavel"] = Campo(" ".join(linha.split()), "padrão", True)
            r.campos["valor"] = Campo(f"{boleto_valor(linha):.2f}", "linha digitável", True)
            r.campos["vencimento"] = Campo(boleto_vencimento(linha).isoformat(), "linha digitável", True)
            break
    cnpjs = _cnpjs(leitura)
    if cnpjs:
        r.campos["beneficiario_documento"] = Campo(cnpjs[0], "padrão", True)
    if (cpf := _cpf(leitura)):
        r.campos["pagador_documento"] = cpf


def _fatura(leitura: Leitura, r: Resultado):
    if (m := re.search(r"CLIENTE:\s*([A-Z ]{6,})", leitura.texto)):
        r.campos["cliente"] = Campo(m.group(1).strip(), "rótulo")
    cnpjs = _cnpjs(leitura)
    if cnpjs:
        r.campos["cnpj_emissora"] = Campo(cnpjs[0], "padrão", True)
    if (v := leitura.abaixo(r"VENCIMENTO", lambda s: bool(data_iso(s)))):
        r.campos["vencimento"] = Campo(data_iso(v), "rótulo")
    if (v := leitura.abaixo(r"TOTAL A PAGAR|VALOR TOTAL|TOTAL", lambda s: bool(valor_decimal(s)))):
        r.campos["valor_total"] = Campo(valor_decimal(v), "rótulo")


RE_ORGAO = re.compile(r"\b(SSP|PC|SDS|SESP|SESDEC|DETRAN|IGP|SJS|SEJUSP|PCII|IIRGD)\s*[/-]\s*([A-Z]{2})\b")


def _orgao_e_naturalidade(leitura: Leitura, r: Resultado):
    if (m := RE_ORGAO.search(leitura.texto)):
        r.campos["orgao_expedidor"] = Campo(f"{m.group(1)}/{m.group(2)}", "padrão")
    cidade_uf = lambda s: bool(re.fullmatch(r"[A-Z][A-Z ]+\s*[-/,]\s*[A-Z]{2}", sem_acento(s).strip()))
    if (v := leitura.abaixo(r"NATURALIDADE", cidade_uf)) or (v := _acima(leitura, r"NATURALIDADE", cidade_uf)):
        cidade, uf = re.split(r"\s*[-/,]\s*", sem_acento(v).strip())[:2]
        r.campos["naturalidade"] = Campo(f"{cidade.strip()}, {uf}", "rótulo")


def _acima(leitura: Leitura, rotulo: str, aceita, distancia: float = 0.04) -> Optional[str]:
    """No RG antigo, o rótulo fica embaixo do valor."""
    for i, n in enumerate(leitura.norm):
        if re.search(rotulo, n):
            r = leitura.linhas[i]
            cands = sorted((r.y - l.y, l.texto) for l in leitura.linhas if 0 < r.y - l.y <= distancia and abs(l.x - r.x) < 0.12)
            # face girada 90°: o "acima" vira "à esquerda, na mesma altura"
            cands += sorted((r.x - l.x, l.texto) for l in leitura.linhas if abs(l.y - r.y) < 0.015 and 0 < r.x - l.x <= distancia)
            for _, texto in cands:
                if aceita(texto):
                    return texto
    return None


EXTRATORES = {"cnh": _cnh, "cin": _cin, "rg": _rg, "nfe": _nfe, "boleto": _boleto, "fatura": _fatura}

# Campos sem os quais o documento não serve ao cadastro: se faltarem, o motor pede nova foto (RF-31).
ESSENCIAIS = {
    "cnh": ("cpf", "nome"), "cin": ("cpf", "nome"), "rg": ("nome", "registro_geral"),
    "nfe": ("chave_acesso",), "boleto": ("linha_digitavel",), "fatura": ("valor_total", "vencimento"),
}

NOMES_CAMPOS = {"cpf": "o CPF", "nome": "o nome", "registro_geral": "o número do RG", "chave_acesso": "a chave da nota",
                "linha_digitavel": "o código de barras", "valor_total": "o valor", "vencimento": "o vencimento"}


def processar(linhas: List[Linha]) -> Resultado:
    leitura = Leitura(linhas)
    if len("".join(leitura.norm)) < 40:
        return Resultado("nao_reconhecido", 0.0, legivel=False, motivo="Não conseguimos ler o documento")
    tipo, conf = classificar(leitura)
    r = Resultado(tipo, conf)
    if tipo == "nao_reconhecido":
        return r
    EXTRATORES[tipo](leitura, r)
    faltando = [c for c in ESSENCIAIS[tipo] if c not in r.campos]
    if faltando:
        r.legivel = False
        r.motivo = f"Não conseguimos ler {NOMES_CAMPOS.get(faltando[0], 'um dado importante')} do documento"
    return r
