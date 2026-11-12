"""Leitura de texto (OCR) atrás de uma interface trocável (ADR 0006).

No estudo, a implementação é o Apple Vision, do próprio macOS. Em produção, o PaddleOCR
entra no lugar sem mudar o resto do pipeline (ADR 0010).

Nada é gravado em disco: a imagem entra e sai da memória.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class Linha:
    texto: str
    confianca: float  # 0 a 1
    x: float  # caixa normalizada, origem no canto superior esquerdo
    y: float
    largura: float
    altura: float


class LeitorDeTexto(Protocol):
    def ler(self, imagem: bytes) -> List[Linha]: ...


class AppleVision:
    """OCR do macOS (Vision framework), em português, no modo preciso."""

    def ler(self, imagem: bytes) -> List[Linha]:
        return self.ler_com_orientacao(imagem)[0]

    def ler_com_orientacao(self, imagem: bytes) -> tuple:
        """Lê e devolve também a rotação (graus, sentido horário) que deixa o documento em pé."""
        import Quartz
        import Vision
        from Foundation import NSData

        dados = NSData.dataWithBytes_length_(imagem, len(imagem))
        fonte = Quartz.CGImageSourceCreateWithData(dados, None)
        if fonte is None or Quartz.CGImageSourceGetCount(fonte) == 0:
            raise ValueError("imagem ilegível")
        cg = Quartz.CGImageSourceCreateImageAtIndex(fonte, 0, None)

        pedido = Vision.VNRecognizeTextRequest.alloc().init()
        pedido.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
        pedido.setRecognitionLanguages_(["pt-BR", "en-US"])
        pedido.setUsesLanguageCorrection_(False)  # nomes e números não devem ser "corrigidos"

        # Orientação: o Vision lida com rotação de 90°/180° quando informada; tentamos as quatro
        # e ficamos com a que lê mais texto com mais confiança (o RG escaneado vem rotacionado).
        melhor: List[Linha] = []
        rotacao = 0
        graus = {1: 0, 6: 90, 3: 180, 8: 270}
        for orientacao in (1, 6, 3, 8):  # cima, 90° horário, 180°, 90° anti-horário (EXIF)
            tratador = Vision.VNImageRequestHandler.alloc().initWithCGImage_orientation_options_(cg, orientacao, None)
            ok, _ = tratador.performRequests_error_([pedido], None)
            if not ok:
                continue
            linhas = []
            for obs in pedido.results() or []:
                cand = obs.topCandidates_(1)
                if not cand:
                    continue
                c = cand[0]
                caixa = obs.boundingBox()
                linhas.append(Linha(
                    texto=str(c.string()), confianca=float(c.confidence()),
                    x=float(caixa.origin.x), y=float(1 - caixa.origin.y - caixa.size.height),
                    largura=float(caixa.size.width), altura=float(caixa.size.height),
                ))
            if _pontuacao(linhas) > _pontuacao(melhor):
                melhor = linhas
                rotacao = graus[orientacao]
        melhor.sort(key=lambda l: (round(l.y, 2), l.x))
        return melhor, _rotacao_pela_direcao_do_texto(cg)


def _pontuacao(linhas: List[Linha]) -> float:
    return sum(len(l.texto) * l.confianca for l in linhas)


def renderizar_pdf(caminho: str, escala: float = 2.5, pagina: int = 1) -> bytes:
    """Converte uma página de PDF em PNG na memória (para PDFs-imagem e para a avaliação)."""
    import Quartz
    from Foundation import NSURL, NSMutableData

    doc = Quartz.CGPDFDocumentCreateWithURL(NSURL.fileURLWithPath_(caminho))
    pag = Quartz.CGPDFDocumentGetPage(doc, pagina)
    caixa = Quartz.CGPDFPageGetBoxRect(pag, Quartz.kCGPDFMediaBox)
    w, h = int(caixa.size.width * escala), int(caixa.size.height * escala)
    ctx = Quartz.CGBitmapContextCreate(None, w, h, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(),
                                       Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, w, h))
    Quartz.CGContextScaleCTM(ctx, escala, escala)
    Quartz.CGContextDrawPDFPage(ctx, pag)
    img = Quartz.CGBitmapContextCreateImage(ctx)
    saida = NSMutableData.data()
    dest = Quartz.CGImageDestinationCreateWithData(saida, "public.png", 1, None)
    Quartz.CGImageDestinationAddImage(dest, img, None)
    Quartz.CGImageDestinationFinalize(dest)
    return bytes(saida)


def renderizar_pdf_bytes(dados: bytes, escala: float = 2.5) -> bytes:
    """Como renderizar_pdf, mas a partir do PDF na memória (arquivo importado pelo celular)."""
    import Quartz
    from Foundation import NSData, NSMutableData

    prov = Quartz.CGDataProviderCreateWithCFData(NSData.dataWithBytes_length_(dados, len(dados)))
    doc = Quartz.CGPDFDocumentCreateWithProvider(prov)
    if doc is None or Quartz.CGPDFDocumentGetNumberOfPages(doc) == 0:
        raise ValueError("PDF ilegível")
    pag = Quartz.CGPDFDocumentGetPage(doc, 1)
    caixa = Quartz.CGPDFPageGetBoxRect(pag, Quartz.kCGPDFMediaBox)
    w, h = int(caixa.size.width * escala), int(caixa.size.height * escala)
    ctx = Quartz.CGBitmapContextCreate(None, w, h, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(),
                                       Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, w, h))
    Quartz.CGContextScaleCTM(ctx, escala, escala)
    Quartz.CGContextDrawPDFPage(ctx, pag)
    img = Quartz.CGBitmapContextCreateImage(ctx)
    saida = NSMutableData.data()
    dest = Quartz.CGImageDestinationCreateWithData(saida, "public.png", 1, None)
    Quartz.CGImageDestinationAddImage(dest, img, None)
    Quartz.CGImageDestinationFinalize(dest)
    return bytes(saida)


def reduzir(png: bytes, lado: int = 1400) -> bytes:
    """Versão menor da página, só para a prévia na tela de revisão."""
    import io
    from PIL import Image

    im = Image.open(io.BytesIO(png)).convert("RGB")
    im.thumbnail((lado, lado))
    out = io.BytesIO()
    im.save(out, "JPEG", quality=82)
    return out.getvalue()


def _rotacao_pela_direcao_do_texto(cg) -> int:
    """Graus (sentido horário) que deixam o documento em pé.

    No modo preciso, o Vision lê até texto de cabeça para baixo, então "qual orientação lê mais"
    não distingue as posições. No modo rápido, texto virado sai como letras sem sentido. O sinal
    usado é: em qual das quatro orientações o modo rápido encontra mais palavras e números de
    documento de verdade (rótulos comuns, datas, CPF/CNPJ).
    """
    import re
    import Vision

    padrao = re.compile(r"NOME|DATA|CPF|CNPJ|VALIDADE|REGISTRO|CARTEIRA|NASCIMENTO|FILIA|TOTAL|VENCIMENTO|"
                        r"BRASIL|IDENTIDADE|HABILITA|EMISS|VALOR|ENDERE|NOTA|FATURA|\d{2}/\d{2}/\d{4}|"
                        r"\d{3}\.\d{3}\.\d{3}-\d{2}", re.I)
    graus = {1: 0, 6: 90, 3: 180, 8: 270}
    pontos = {}
    for orientacao in (1, 6, 3, 8):
        pedido = Vision.VNRecognizeTextRequest.alloc().init()
        pedido.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelFast)
        pedido.setUsesLanguageCorrection_(False)
        tratador = Vision.VNImageRequestHandler.alloc().initWithCGImage_orientation_options_(cg, orientacao, None)
        ok, _ = tratador.performRequests_error_([pedido], None)
        textos = [str(o.topCandidates_(1)[0].string()) for o in (pedido.results() or []) if ok and o.topCandidates_(1)]
        pontos[graus[orientacao]] = sum(len(padrao.findall(s)) for s in textos)
    melhor = max(pontos, key=pontos.get)
    return melhor if pontos[melhor] > pontos[0] else 0
