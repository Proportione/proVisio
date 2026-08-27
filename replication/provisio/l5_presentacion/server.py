"""Servidor HTTP del artefacto (solo stdlib). Deriva de wallboard/server.py.

Rutas:
  GET /api/board  -> JSON del último board (de cache o pasada única sobre snapshot)
  GET /           -> web/index.html
  GET /<estatico> -> ficheros de web/ (css, js)

Bind 0.0.0.0:8080 (LAN/Tailscale, NO WAN). Arranca el aggregator en un hilo de fondo
que refresca la cache desde el snapshot congelado (modo evaluación, determinista).

Uso:  python -m provisio.l5_presentacion.server  ->  http://localhost:8080/
"""

import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ..ciclo_vida.aggregator import Aggregator, build_board
from ..ciclo_vida.cache import Cache

WEB_DIR = Path(__file__).resolve().parent / "web"


def _safe_static(rel):
    """Resuelve `rel` dentro de web/ sin path traversal. None si no existe."""
    rel = rel.lstrip("/")
    candidate = (WEB_DIR / rel).resolve()
    try:
        candidate.relative_to(WEB_DIR)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


class Handler(BaseHTTPRequestHandler):
    cache = None  # inyectado por make_server

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/board":
            board = (self.cache and self.cache.get_board()) or build_board()
            self._send(200, json.dumps(board, ensure_ascii=False).encode("utf-8"))
            return
        if path == "/":
            path = "/index.html"
        static = _safe_static(path)
        if static is None:
            self._send(404, b'{"error":"not_found"}')
            return
        ctype = mimetypes.guess_type(str(static))[0] or "application/octet-stream"
        self._send(200, static.read_bytes(), ctype)

    def log_message(self, *args):
        pass


def make_server(config=None, cache=None, port=8080):
    cache = cache or Cache()
    Handler.cache = cache
    httpd = ThreadingHTTPServer(("0.0.0.0", int(port)), Handler)
    return httpd, cache


def main():
    httpd, cache = make_server()
    agg = Aggregator({"mode": "snapshot"}, cache)
    threading.Thread(target=agg.run, daemon=True).start()
    print("ProVisio L5 en http://localhost:8080/  (Ctrl-C para salir)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        agg.stop()
        httpd.shutdown()


if __name__ == "__main__":
    main()
