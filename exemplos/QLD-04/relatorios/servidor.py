"""Serviço de exemplo da QLD-04: um relatório por GET, com um cache opcional em memória."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# CACHE_MB > 0 carrega o "histórico inteiro" na memória ao subir (o defeito do Antes).
CACHE = bytearray(int(os.environ.get("CACHE_MB", "0")) * 1024 * 1024)
for i in range(0, len(CACHE), 4096):
    CACHE[i] = 1  # toca cada página, para a memória ser de fato usada


class Relatorio(BaseHTTPRequestHandler):
    def do_GET(self):
        corpo = json.dumps({"rota": self.path, "linhas": 120}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args):
        pass


ThreadingHTTPServer(("0.0.0.0", 8000), Relatorio).serve_forever()
