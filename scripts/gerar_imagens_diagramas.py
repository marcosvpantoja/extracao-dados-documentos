"""Gera uma imagem PNG de cada diagrama Mermaid da documentação.

Cada bloco ```mermaid de um arquivo .md vira um PNG em `img/`, na mesma pasta
do documento, com o nome do arquivo e o título da seção. O Mermaid continua
sendo a fonte: rode este script sempre que um diagrama mudar.

Uso:  python3 scripts/gerar_imagens_diagramas.py
Requer o Google Chrome instalado (modo headless) e acesso à internet para
carregar o Mermaid pela CDN.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCUMENTOS = [
    RAIZ / "docs/arquitetura/fluxogramas.md",
    RAIZ / "docs/arquitetura/c4.md",
    RAIZ / "docs/etapas/04-estrategia.md",
    RAIZ / "docs/etapas/05-metricas.md",
    RAIZ / "docs/etapas/07-business-case.md",
]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"
MARGEM = 24
ESCALA = 2  # imagem em alta resolução (2x)

PAGINA = """<!doctype html><html><head><meta charset="utf-8"><title>pendente</title>
<style>html,body{margin:0;background:#fff}#d{padding:%(m)dpx;display:inline-block}</style>
</head><body><div id="d"></div>
<script src="%(js)s"></script>
<script>
mermaid.initialize({startOnLoad:false, theme:'default', fontFamily:'-apple-system, Helvetica, Arial, sans-serif'});
mermaid.render('g', %(codigo)s).then(({svg}) => {
  const d = document.getElementById('d'); d.innerHTML = svg;
  const s = d.querySelector('svg');
  const vb = s.viewBox.baseVal;
  s.setAttribute('width', vb.width); s.setAttribute('height', vb.height);
  s.style.maxWidth = 'none';
  document.title = Math.ceil(vb.width + 2*%(m)d) + 'x' + Math.ceil(vb.height + 2*%(m)d);
}).catch(e => { document.title = 'ERRO ' + e.message; });
</script></body></html>"""


def slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"^\d+\.\s*", "", texto.lower())
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")[:50]


def diagramas(md: Path) -> list[tuple[str, str]]:
    """Retorna (título da seção, código Mermaid) de cada bloco do arquivo."""
    resultado, titulo = [], md.stem
    linhas = md.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(linhas):
        if linhas[i].startswith("## "):
            titulo = linhas[i][3:].strip()
        if linhas[i].strip() == "```mermaid":
            fim = i + 1
            while linhas[fim].strip() != "```":
                fim += 1
            resultado.append((titulo, "\n".join(linhas[i + 1 : fim])))
            i = fim
        i += 1
    return resultado


def chrome(*args: str, tentativas: int = 3) -> str:
    """Roda o Chrome headless num perfil temporário, repetindo se travar."""
    for tentativa in range(1, tentativas + 1):
        with tempfile.TemporaryDirectory() as perfil:
            cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                   "--no-first-run", f"--user-data-dir={perfil}",
                   "--virtual-time-budget=15000", *args]
            try:
                return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
            except subprocess.TimeoutExpired:
                if tentativa == tentativas:
                    raise
    return ""


def renderizar(codigo: str, destino: Path, tmp: Path) -> None:
    html = tmp / "diagrama.html"
    html.write_text(PAGINA % {"m": MARGEM, "js": MERMAID, "codigo": json.dumps(codigo)},
                    encoding="utf-8")
    # 1ª passada: descobre o tamanho natural do diagrama
    dom = chrome("--window-size=4000,4000", "--dump-dom", html.as_uri())
    achado = re.search(r"<title>(.*?)</title>", dom)
    titulo = achado.group(1) if achado else "sem resposta do Chrome"
    if not re.fullmatch(r"\d+x\d+", titulo):
        raise RuntimeError(f"{destino.name}: {titulo}")
    largura, altura = titulo.split("x")
    # 2ª passada: captura a imagem exatamente nesse tamanho
    chrome(f"--window-size={largura},{altura}", f"--force-device-scale-factor={ESCALA}",
           f"--screenshot={destino}", html.as_uri())


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        for md in DOCUMENTOS:
            pasta = md.parent / "img"
            pasta.mkdir(exist_ok=True)
            for n, (titulo, codigo) in enumerate(diagramas(md), start=1):
                destino = pasta / f"{md.stem}-{n:02d}-{slug(titulo)}.png"
                renderizar(codigo, destino, Path(t))
                print(f"✅ {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
