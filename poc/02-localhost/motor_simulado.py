"""Motor simulado para a prova de conceito 2.

Responde no endereço local do Mac (porta 8787), como o motor real fará,
para testar se uma página hospedada na Vercel (HTTPS) consegue chamá-lo.
Não processa nada: devolve uma resposta fixa e o tamanho do que recebeu.

Uso: python3 motor_simulado.py https://<pagina>.vercel.app
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ORIGEM = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "*"


class Motor(BaseHTTPRequestHandler):
    def _cabecalhos(self, status=200):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", ORIGEM)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        # Chrome: permissão para uma página pública acessar a rede local
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Content-Type", "application/json")
        self.end_headers()

    def do_OPTIONS(self):
        self._cabecalhos(204)

    def do_GET(self):
        if self.path in ("/", "/local.html"):
            # Prova 2b: a aplicação do escritório é servida pelo próprio motor
            corpo = open(__file__.replace("motor_simulado.py", "pagina/local.html"), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(corpo)
            return
        self._cabecalhos()
        self.wfile.write(json.dumps({"motor": "ok"}).encode())

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        self.rfile.read(tamanho)  # descartado: nada é guardado
        self._cabecalhos()
        self.wfile.write(json.dumps({"tipo": "cnh", "recebidos_bytes": tamanho}).encode())

    def log_message(self, formato, *args):
        sys.stderr.write(f"{self.headers.get('Origin', '-')} {formato % args}\n")


if __name__ == "__main__":
    print(f"Motor simulado em http://127.0.0.1:8787 · origem permitida: {ORIGEM}")
    ThreadingHTTPServer(("127.0.0.1", 8787), Motor).serve_forever()
