"""Testes do motor.

Os testes marcados com `precisa_mac` usam o Apple Vision (OCR do macOS) e são pulados em
outros sistemas, como na integração contínua no Linux.
"""

import sys

import pytest

precisa_mac = pytest.mark.skipif(sys.platform != "darwin", reason="usa o Apple Vision, disponível só no macOS")

from fastapi.testclient import TestClient

from src.motor import servidor

servidor.ESPERA_SIMULADA_S = 0
cliente = TestClient(servidor.app)


def _enviar(doc, simular=None, faces=("frente",)):
    arquivos = {f: (f"{f}.jpg", b"\xff\xd8 imagem ficticia", "image/jpeg") for f in faces}
    url = f"/processar?doc={doc}" + (f"&simular={simular}" if simular else "")
    return cliente.post(url, files=arquivos).json()


@precisa_mac
def test_cnh_ficticia_e_lida_com_cpf_validado():
    from src.extracao.ocr import renderizar_pdf
    img = renderizar_pdf("data/exemplos/cnh/cnh-ficticio-01.pdf")
    r = cliente.post("/processar?doc=identidade", files={"frente": ("frente.png", img, "image/png")}).json()
    assert r["status"] == "lido"
    assert r["tipo"] == "cnh"
    assert r["campos"]["cpf"] == {"valor": "644.836.782-99", "origem": "padrão", "validado": True}


@precisa_mac
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


def test_registro_de_revisao_descarta_valores(tmp_path, monkeypatch):
    destino = tmp_path / "registro.jsonl"
    monkeypatch.setattr(servidor, "REGISTRO_REVISAO", destino)
    r = cliente.post("/revisao", json=[
        {"tipo": "cnh", "campo": "cpf", "origem": "padrão", "validado": True, "resultado": "confirmado", "valor": "644.836.782-99"},
        {"tipo": "cnh", "campo": "nome", "resultado": "talvez"},
    ]).json()
    assert r == {"gravados": 1}
    conteudo = destino.read_text()
    assert "644.836" not in conteudo and '"campo": "cpf"' in conteudo


def test_relatorio_calcula_krs_a_partir_do_registro(tmp_path, capsys):
    import importlib.util, json as _json
    reg = tmp_path / "r.jsonl"
    linhas = [
        {"etapa": "sessao", "sessao": "s1", "evento": "link_gerado", "quando": "2026-11-11T10:00:00+00:00"},
        {"etapa": "captura", "sessao": "s1", "evento": "documento_lido", "fotos": 1, "faces": 1, "status": "lido", "quando": "2026-11-11T10:01:00+00:00"},
        {"etapa": "captura", "sessao": "s1", "evento": "documento_lido", "fotos": 3, "faces": 2, "status": "lido", "quando": "2026-11-11T10:02:00+00:00"},
        {"etapa": "sessao", "sessao": "s1", "evento": "revisao_concluida", "sem_edicao": True, "quando": "2026-11-11T10:03:00+00:00"},
        {"etapa": "sessao", "sessao": "s1", "evento": "conferencia_concluida", "erros": 1, "quando": "2026-11-11T10:04:00+00:00"},
    ]
    reg.write_text("\n".join(_json.dumps(l) for l in linhas))
    spec = importlib.util.spec_from_file_location("relatorio", "scripts/relatorio.py")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    mod.main(reg)
    saida = capsys.readouterr().out
    assert "KR4 · documentos aceitos com a primeira foto:       50% (1 de 2)" in saida
    assert "mediana 4.0 min" in saida
    assert "Proteção · documentos com erro depois da revisão:   100% (1 de 1)" in saida


@precisa_mac
def test_pdf_importado_e_lido_e_devolve_previa():
    pdf = open("data/exemplos/nfe/nfe-ficticio-01.pdf", "rb").read()
    r = cliente.post("/processar?doc=nota", files={"frente": ("nota.pdf", pdf, "application/pdf")}).json()
    assert r["status"] == "lido" and r["tipo"] == "nfe"
    assert r["previa"].startswith("data:image/jpeg;base64,")


@precisa_mac
def test_foto_de_cabeca_para_baixo_e_lida_e_informa_a_rotacao():
    import io
    from PIL import Image
    from src.extracao.ocr import renderizar_pdf
    img = Image.open(io.BytesIO(renderizar_pdf("data/exemplos/cnh/cnh-ficticio-01.pdf"))).rotate(180)
    buf = io.BytesIO(); img.save(buf, "PNG")
    r = cliente.post("/processar?doc=identidade", files={"frente": ("f.png", buf.getvalue(), "image/png")}).json()
    assert r["tipo"] == "cnh"
    assert r["rotacao"]["frente"] == 180
