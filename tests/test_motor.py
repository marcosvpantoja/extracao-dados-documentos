"""Testes do motor simulado (incremento 1)."""

from fastapi.testclient import TestClient

from src.motor import servidor

servidor.ESPERA_SIMULADA_S = 0
cliente = TestClient(servidor.app)


def _enviar(doc, simular=None, faces=("frente",)):
    arquivos = {f: (f"{f}.jpg", b"\xff\xd8 imagem ficticia", "image/jpeg") for f in faces}
    url = f"/processar?doc={doc}" + (f"&simular={simular}" if simular else "")
    return cliente.post(url, files=arquivos).json()


def test_leitura_simulada_devolve_o_tipo():
    r = _enviar("identidade", faces=("frente", "verso"))
    assert r["status"] == "lido"
    assert r["tipo"] == "cnh"
    assert set(r["faces"]) == {"frente", "verso"}


def test_falha_simulada_pede_nova_foto_com_motivo():
    r = _enviar("comprovante", simular="falha")
    assert r["status"] == "nova-foto"
    assert "ler" in r["motivo"]


def test_resposta_nao_devolve_conteudo_da_imagem():
    r = _enviar("fatura")
    assert "ficticia" not in str(r)
