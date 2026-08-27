"""Cache del último board bueno. VENDORIZADO verbatim de
nodo-aveiro/tools/wallboard/wallboard/cache.py.

El server sirve siempre de cache (nunca bloquea sobre el polling). El aggregator
escribe aquí tras cada ciclo. En modo evaluación, la cache se sustituye por el
snapshot congelado datado (no cache viva) para reproducibilidad.
"""

import json
import threading
from pathlib import Path

DEFAULT_PATH = Path.home() / ".provisio" / "cache.json"


class Cache:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._board = None
        self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                self._board = json.load(f)
        except (OSError, ValueError):
            self._board = None

    def get_board(self):
        with self._lock:
            return self._board

    def set_board(self, board):
        with self._lock:
            self._board = board
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".json.tmp")
            with open(tmp, "w") as f:
                json.dump(board, f, ensure_ascii=False)
            tmp.replace(self.path)
        except OSError:
            pass
