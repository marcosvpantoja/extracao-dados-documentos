"""
Validações automáticas de campos extraídos.

Usadas para calcular a confiança da extração: se um identificador não passa na
validação, o campo é marcado como suspeito mesmo sem gabarito.
Implementação independente do gerador de exemplos (scripts/gerar_exemplos.py).
"""
import re
from datetime import date


def _digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


def cpf_valido(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for pos in (9, 10):
        soma = sum(int(d[i]) * (pos + 1 - i) for i in range(pos))
        dv = (soma * 10) % 11 % 10
        if dv != int(d[pos]):
            return False
    return True


def cnpj_valido(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 14 or d == d[0] * 14:
        return False
    for pos in (12, 13):
        pesos = list(range(pos - 7, 1, -1)) + list(range(9, 1, -1))
        soma = sum(int(x) * p for x, p in zip(d[:pos], pesos))
        dv = 0 if soma % 11 < 2 else 11 - soma % 11
        if dv != int(d[pos]):
            return False
    return True


def chave_nfe_valida(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 44 or d[20:22] != "55":
        return False
    pesos = [2, 3, 4, 5, 6, 7, 8, 9] * 6
    soma = sum(int(x) * p for x, p in zip(reversed(d[:43]), pesos))
    resto = soma % 11
    dv = 0 if resto < 2 else 11 - resto
    return dv == int(d[43]) and cnpj_valido(d[6:20])


def _mod10(num: str) -> int:
    total = 0
    for i, c in enumerate(reversed(num)):
        p = int(c) * (2 if i % 2 == 0 else 1)
        total += p - 9 if p > 9 else p
    return (10 - total % 10) % 10


def linha_digitavel_valida(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 47:
        return False
    campos = [(d[0:9], d[9]), (d[10:20], d[20]), (d[21:31], d[31])]
    if any(_mod10(c) != int(dv) for c, dv in campos):
        return False
    return codigo_barras_valido(linha_para_codigo_barras(d))


def linha_para_codigo_barras(linha: str) -> str:
    d = _digitos(linha)
    return d[0:4] + d[32] + d[33:47] + d[4:9] + d[10:20] + d[21:31]


def codigo_barras_valido(valor: str) -> bool:
    d = _digitos(valor)
    if len(d) != 44:
        return False
    base = d[:4] + d[5:]
    pesos = [2, 3, 4, 5, 6, 7, 8, 9] * 6
    soma = sum(int(x) * p for x, p in zip(reversed(base), pesos))
    dv = 11 - soma % 11
    dv = 1 if dv in (0, 10, 11) else dv
    return dv == int(d[4])


def boleto_vencimento(linha: str) -> date:
    """Data de vencimento embutida na linha digitável (fator reiniciado em 22/02/2025)."""
    from datetime import timedelta
    fator = int(_digitos(linha)[33:37])
    return date(2025, 2, 22) + timedelta(days=fator - 1000)


def boleto_valor(linha: str) -> float:
    return int(_digitos(linha)[37:47]) / 100


def mrz_digito(trecho: str) -> int:
    def v(c):
        if c.isdigit():
            return int(c)
        if c == "<":
            return 0
        return ord(c) - 55
    return sum(v(c) * (7, 3, 1)[i % 3] for i, c in enumerate(trecho)) % 10


def mrz_td1_valida(linhas) -> bool:
    l1, l2 = linhas[0], linhas[1]
    if len(l1) != 30 or len(l2) != 30:
        return False
    checks = [(l1[5:14], l1[14]), (l2[0:6], l2[6]), (l2[8:14], l2[14])]
    if any(mrz_digito(t) != int(dv) for t, dv in checks):
        return False
    composto = l1[5:30] + l2[0:7] + l2[8:15] + l2[18:29]
    return mrz_digito(composto) == int(l2[29])
