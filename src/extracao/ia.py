"""IA de texto local (Ollama + Qwen 2.5 7B), usada só para o que as regras não acharam (ADR 0002).

Roda inteiramente no Mac: o texto do documento nunca sai do computador. A IA recebe o texto
do OCR, não a imagem, e só preenche campos que as regras deixaram em branco.

Proteção contra dado inventado (RF-15): todo valor devolvido pela IA precisa aparecer no
próprio texto do OCR. Se não aparecer, é descartado. CPF ainda passa pelo dígito verificador.
"""

from __future__ import annotations

import json
import re
import urllib.request
from typing import Dict, List, Optional

URL = "http://127.0.0.1:11434/api/chat"
MODELO = "qwen2.5:7b"
TEMPO_LIMITE_S = 20

DESCRICOES = {
    "nome": "nome completo do titular do documento (não o nome social, não o pai nem a mãe)",
    "cpf": "CPF do titular, formato 000.000.000-00",
    "data_nascimento": "data de nascimento do titular, formato DD/MM/AAAA",
    "filiacao_pai": "nome completo do pai",
    "filiacao_mae": "nome completo da mãe",
    "naturalidade": "cidade e UF de nascimento, formato CIDADE/UF",
    "orgao_expedidor": "órgão expedidor e UF, formato SSP/UF",
    "registro_geral": "número do RG (registro geral), como impresso",
    "numero_registro": "número de registro da CNH (11 dígitos)",
    "categoria": "categoria da habilitação (ex.: B, AB, D)",
    "validade": "data de validade, formato DD/MM/AAAA",
    "data_emissao": "data de emissão, formato DD/MM/AAAA",
    "data_expedicao": "data de expedição, formato DD/MM/AAAA",
    "valor_total": "valor total em reais, formato 0000,00",
    "vencimento": "data de vencimento, formato DD/MM/AAAA",
    "cliente": "nome do cliente",
}

TIPOS_DESCRICAO = {
    "cnh": "Carteira Nacional de Habilitação", "cin": "Carteira de Identidade Nacional (RG novo, número = CPF)",
    "rg": "RG antigo (carteira de identidade estadual)", "nfe": "Nota fiscal eletrônica (DANFE)",
    "boleto": "Boleto bancário", "fatura": "Fatura de serviço (luz, água, telefone, internet)",
}


def disponivel() -> bool:
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1)
        return True
    except Exception:
        return False


def _perguntar(sistema: str, usuario: str, esquema: dict) -> Optional[dict]:
    corpo = json.dumps({
        "model": MODELO, "stream": False, "format": esquema,
        "options": {"temperature": 0, "num_ctx": 4096},
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
    }).encode()
    req = urllib.request.Request(URL, data=corpo, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TEMPO_LIMITE_S) as r:
            return json.loads(json.load(r)["message"]["content"])
    except Exception:
        return None


SISTEMA = ("Você extrai dados de documentos brasileiros a partir do texto lido por OCR. "
           "Responda somente com o JSON pedido. Copie os valores exatamente como aparecem no texto. "
           "Se um campo não estiver no texto, use null. Nunca invente nem complete dados.")


def classificar(texto: str) -> Optional[str]:
    esquema = {"type": "object", "properties": {"tipo": {"type": "string", "enum": list(TIPOS_DESCRICAO) + ["outro"]}},
               "required": ["tipo"]}
    lista = "\n".join(f"- {k}: {v}" for k, v in TIPOS_DESCRICAO.items())
    r = _perguntar(SISTEMA, f"Qual é o tipo deste documento?\n{lista}\n- outro: nenhum dos anteriores\n\nTEXTO:\n{texto[:3000]}", esquema)
    tipo = (r or {}).get("tipo")
    return tipo if tipo in TIPOS_DESCRICAO else None


def completar(texto: str, tipo: str, faltando: List[str]) -> Dict[str, str]:
    """Pede à IA só os campos que faltam e devolve os que passam na checagem contra o texto."""
    campos = [c for c in faltando if c in DESCRICOES]
    if not campos:
        return {}
    esquema = {"type": "object", "properties": {c: {"type": ["string", "null"]} for c in campos}, "required": campos}
    pedido = "\n".join(f"- {c}: {DESCRICOES[c]}" for c in campos)
    r = _perguntar(SISTEMA, f"Documento: {TIPOS_DESCRICAO.get(tipo, tipo)}.\nExtraia:\n{pedido}\n\nTEXTO:\n{texto[:3500]}", esquema) or {}
    return {c: str(v).strip() for c, v in r.items() if c in campos and v and _aparece_no_texto(str(v), texto)}


def _norm(s: str) -> str:
    from .pipeline import sem_acento
    return re.sub(r"[^A-Z0-9]", "", sem_acento(s))


def _aparece_no_texto(valor: str, texto: str) -> bool:
    """O valor precisa estar no texto do OCR (ignorando acentos, espaços e pontuação)."""
    v = _norm(valor)
    if len(v) < 2:
        return False
    if v in _norm(texto):
        return True
    # datas: aceita DD/MM/AAAA presente no texto em outro separador
    m = re.fullmatch(r"(\d{2})\D?(\d{2})\D?(\d{4})", valor.strip())
    return bool(m) and "".join(m.groups()) in re.sub(r"\D", "", texto)
