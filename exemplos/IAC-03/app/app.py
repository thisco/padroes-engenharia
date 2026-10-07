"""App mínima da IAC-03: /versao devolve a versão da imagem; /saude depende do build."""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSAO = os.environ.get("VERSAO", "?")
SAUDE = os.environ.get("SAUDE", "ok")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/versao":
            self._responder(200, VERSAO)
        elif self.path == "/saude":
            self._responder(200 if SAUDE == "ok" else 500, SAUDE)
        else:
            self._responder(404, "não encontrado")

    def _responder(self, codigo, texto):
        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(texto.encode())


HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
