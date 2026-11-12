"""Testes do motor simulado (incremento 1)."""

from fastapi.testclient import TestClient

from src.motor import servidor

servidor.ESPERA_SIMULADA_S = 0
cliente = TestClient(servidor.app)


def _enviar(doc, simular=None, faces=("frente",)):
    arquivos = {f: (f"{f}.jpg", b"\xff\xd8 imagem ficticia", "image/jpeg") for f in faces}
    url = f"/processar?doc={doc}" + (f"&simular={simular}" if simular else "")
    return cliente.post(url, files=arquivos).json()


def test_cnh_ficticia_e_lida_com_cpf_validado():
    from src.extracao.ocr import renderizar_pdf
    img = renderizar_pdf("data/exemplos/cnh/cnh-ficticio-01.pdf")
    r = cliente.post("/processar?doc=identidade", files={"frente": ("frente.png", img, "image/png")}).json()
    assert r["status"] == "lido"
    assert r["tipo"] == "cnh"
    assert r["campos"]["cpf"] == {"valor": "644.836.782-99", "origem": "padrão", "validado": True}


def test_imagem_que_nao_abre_pede_nova_foto():
    r = _enviar("identidade")
    assert r["status"] == "nova-foto"


def test_falha_simulada_pede_nova_foto_com_motivo():
    r = _enviar("comprovante", simular="falha")
    assert r["status"] == "nova-foto"
    assert "ler" in r["motivo"]


def test_resposta_nao_devolve_conteudo_da_imagem():
    r = _enviar("fatura")
    assert "ficticia" not in str(r)
