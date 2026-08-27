"""Orquestador. Porta la semántica del wallboard (cadencia, frescura 3xCADENCE,
último-bueno, degradación por excepción) y la reorganiza para componer el board del
artefacto (signals L1-normalizadas / screens KPI / fusion L3 / alerts / blocks).

`build_board` = una pasada determinista L1->L4 sobre el snapshot (la usa
componente_a y el poll). `Aggregator` = loop vivo con cadencia y bitácora encendida.
"""

import threading
import time
from datetime import datetime, timezone

from ..l1_ingesta import COLECTORES_I1
from ..l2_normalizacion import compose
from ..l3_fusion import fusiones
from ..l4_kpi import k1_acquisition, vistas
from ..gobernanza import audit_trail
from . import alertas


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_stale(last_ok_iso, cadence_seconds, now=None):
    """True si last_ok es más viejo que 3xcadence (o no hay last_ok). VERBATIM."""
    if not last_ok_iso:
        return True
    try:
        t = datetime.strptime(last_ok_iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    now = now or datetime.now(timezone.utc)
    return (now - t).total_seconds() > 3 * cadence_seconds


def _compose(board, results, last_ok, cadence):
    """Mezcla resultados frescos en el board del artefacto + recalcula blocks/stale.
    signals <- s1/s2/s3 ; screens.k1 <- op_crm+fusion ; fusion.fa1 <- L3."""
    board["generatedAt"] = now_iso()

    # blocks + frescura (semántica del wallboard)
    for name in results:
        board["blocks"][name] = {
            "lastOk": last_ok.get(name),
            "stale": is_stale(last_ok.get(name), cadence.get(name, 60)),
        }

    # señales normalizadas (L2)
    s1_raw = results.get("s1_search")
    s2_raw = results.get("s2_web")
    s3 = results.get("s3_paid")
    op_crm_out = results.get("op_crm")
    if s1_raw is not None:
        board["signals"]["s1"] = compose.normaliza_s1(s1_raw)
    if s2_raw is not None:
        board["signals"]["s2"] = compose.normaliza_s2(s2_raw)
    if s3 is not None:
        board["signals"]["s3"] = s3  # N/A estructural (no se normaliza)

    # fusión F-A1 (L3) + vista K1 (L4)
    if s1_raw is not None and s2_raw is not None and op_crm_out is not None:
        fa1 = fusiones.fa1(s1_raw, s2_raw, op_crm_out,
                           tenant=board.get("tenant", "proportione"),
                           brazo_l=board.get("_brazo_l"))
        board["fusion"]["fa1"] = fa1
        board["fusion"]["fa4"] = fusiones.fa4(s3)  # NO ejercido (N/A estructural)
        screens = vistas.vista_vacia()
        screens["k1"] = k1_acquisition.build_k1(op_crm_out, fa1)
        board["screens"] = screens

    board["alerts"] = alertas.derive_alerts(board)
    return board


def build_board(config=None, brazo_l=None, audit=False):
    """Pasada única determinista L1->L4 sobre el snapshot. Reproducible (gate G1).

    `audit=True` emite evidencia de bitácora (log_fusion de F-A1) por esta pasada
    aislada, para que una corrida fuera del loop vivo (p.ej. Componente A) deje
    audit-trail. Off por defecto: build_board sigue siendo función pura sin efectos
    para tests y para el fallback del servidor. El destino honra
    `config["audit_log_path"]` (best-effort; audit_trail nunca lanza)."""
    config = dict(config or {})
    config.setdefault("mode", "snapshot")
    board = compose.build_empty_board(COLECTORES_I1)
    board["_brazo_l"] = brazo_l
    results, last_ok = {}, {}
    cadence = {c.NAME: c.CADENCE_SECONDS for c in COLECTORES_I1}
    for c in COLECTORES_I1:
        try:
            results[c.NAME] = c.collect(config)
            last_ok[c.NAME] = now_iso()
        except Exception:
            results[c.NAME] = None  # conserva stale; el board sigue válido
    _compose(board, results, last_ok, cadence)
    board.pop("_brazo_l", None)
    if audit and board.get("fusion", {}).get("fa1"):
        audit_trail.log_fusion(board["fusion"]["fa1"], now_iso(),
                               config.get("audit_log_path"))
    return board


class Aggregator:
    """Loop vivo: re-sondea por cadencia, conserva último-bueno, bitácora ENCENDIDA."""

    def __init__(self, config, cache, brazo_l=None):
        self.config = dict(config or {})
        self.config.setdefault("mode", "snapshot")
        self.cache = cache
        self.brazo_l = brazo_l
        self._last_ok = {}
        self._board = compose.build_empty_board(COLECTORES_I1)
        self._stop = threading.Event()
        self._next_due = {c.NAME: 0.0 for c in COLECTORES_I1}
        self._cadence = {c.NAME: c.CADENCE_SECONDS for c in COLECTORES_I1}

    def poll_once(self):
        now = time.monotonic()
        results = {}
        for c in COLECTORES_I1:
            if now < self._next_due[c.NAME]:
                continue
            self._next_due[c.NAME] = now + c.CADENCE_SECONDS
            try:
                results[c.NAME] = c.collect(self.config)
                self._last_ok[c.NAME] = now_iso()
            except Exception:
                results[c.NAME] = None
        self._board["_brazo_l"] = self.brazo_l
        prev_alerts = list(self._board.get("alerts", []))
        _compose(self._board, results, self._last_ok, self._cadence)
        self._board.pop("_brazo_l", None)
        # bitácora append-only ENCENDIDA: transiciones de alerta + corpus de fusión
        ts = now_iso()
        audit_trail.append(alertas.alert_transitions(prev_alerts, self._board.get("alerts", []), ts),
                           self.config.get("audit_log_path"))
        if self._board.get("fusion", {}).get("fa1"):
            audit_trail.log_fusion(self._board["fusion"]["fa1"], ts, self.config.get("audit_log_path"))
        self.cache.set_board(self._board)
        return self._board

    def run(self, interval=5):
        while not self._stop.is_set():
            self.poll_once()
            self._stop.wait(interval)

    def stop(self):
        self._stop.set()
