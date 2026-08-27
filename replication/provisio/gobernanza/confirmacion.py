"""Control 1 — gate de confirmación (bloqueo antes de superficie de decisión).

En una superficie ambiente read-only (TV) el análogo del "humano confirma" es un
GATE que impide que una afirmación LLM sin respaldo determinista alcance una ruta de
decisión: si el brazo L no puede anclarse a hechos del brazo R, se BLOQUEA (no se
publica su narrativa; la fusión degrada al brazo R). En la evaluación, el revisor
firma el corpus.

También aloja el bloqueo de datos SENSIBLES (M5, fallo duro): ninguna cifra K2
(revenue EUR) ni nombre de cliente puede salir a superficie publicable sin agregación.
"""

import re

from . import citacion

# Marcadores de dato sensible que NO pueden aparecer crudos en superficie publicable.
_EUR = re.compile(r"\d[\d.\s]*\s?(€|eur)", re.IGNORECASE)


def gate_narrativa(fusion, snapshot_keys=None, umbral_citacion=0.90):
    """Decide si la narrativa L de una fusión puede publicarse. Devuelve
    (publicable: bool, motivo). Bloquea si M1(L) < umbral o no hay respaldo R."""
    l = (fusion or {}).get("brazo_L") or {}
    if not l.get("sintesis"):
        return False, "sin narrativa L (degradado a brazo R)"
    if not ((fusion.get("brazo_R") or {}).get("afirmaciones")):
        return False, "narrativa L sin respaldo determinista R"
    m1 = citacion.audita_fusion(fusion, snapshot_keys)["m1_brazo_L"]
    if m1 < umbral_citacion:
        return False, f"citación L insuficiente ({m1:.2f} < {umbral_citacion})"
    return True, "ok"


def bloqueo_sensible(texto):
    """M5 (fallo duro): True si `texto` filtra EUR crudo (revenue). En superficie
    publicable esto debe agregarse/omitirse antes de salir."""
    return bool(texto) and bool(_EUR.search(str(texto)))
