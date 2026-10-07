"""API mínima da IAC-01: /versao devolve a versão da imagem e /saude confere o banco."""

import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

VERSAO = "v1"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/versao":
            self._responder(200, VERSAO)
        elif self.path == "/saude":
            try:
                socket.create_connection(("db", 5432), timeout=2).close()
                self._responder(200, "ok")
            except OSError:
                self._responder(503, "banco indisponível")
        else:
            self._responder(404, "não encontrado")

    def _responder(self, codigo, texto):
        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(texto.encode())


HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
