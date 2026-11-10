"""Confere que todos os gabaritos do conjunto de desenvolvimento passam nas validações."""
import json, sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from extracao import validacoes as v  # noqa: E402

REGRAS = {
    "cpf": v.cpf_valido, "pagador_documento": v.cpf_valido,
    "cnpj_emissora": v.cnpj_valido, "emitente_cnpj": v.cnpj_valido, "beneficiario_documento": v.cnpj_valido,
    "chave_acesso": v.chave_nfe_valida, "codigo_barras": v.codigo_barras_valido,
    "linha_digitavel": lambda x: x == "" or v.linha_digitavel_valida(x),
    "destinatario_documento": lambda x: v.cpf_valido(x) or v.cnpj_valido(x),
}


def test_todos_os_gabaritos():
    arquivos = sorted((RAIZ / "data" / "exemplos").glob("*/*.json"))
    assert arquivos, "nenhum gabarito encontrado"
    falhas = []
    for f in arquivos:
        g = json.loads(f.read_text())
        for campo, regra in REGRAS.items():
            if campo in g["campos"] and not regra(g["campos"][campo]):
                falhas.append(f"{f.name}: {campo}")
        if g["tipo"] == "BOLETO":
            c = g["campos"]
            assert v.linha_para_codigo_barras(c["linha_digitavel"]) == c["codigo_barras"], f.name
            assert v.boleto_vencimento(c["linha_digitavel"]) == date.fromisoformat(c["vencimento"]), f.name
            assert abs(v.boleto_valor(c["linha_digitavel"]) - float(c["valor"])) < 0.001, f.name
    assert not falhas, falhas


def test_validadores_rejeitam_erros():
    assert not v.cpf_valido("111.111.111-11")
    assert not v.cpf_valido("123.456.789-00")
    assert not v.cnpj_valido("00.000.000/0001-00")
    assert v.cpf_valido("529.982.247-25")          # CPF de exemplo público
    assert v.cnpj_valido("11.222.333/0001-81")     # CNPJ de exemplo público
    assert v.mrz_digito("D23145890") == 7          # exemplo do padrão ICAO 9303


if __name__ == "__main__":
    test_todos_os_gabaritos(); test_validadores_rejeitam_erros(); print("todos os testes passaram")
