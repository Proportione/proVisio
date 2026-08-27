"""Control 2 — citación-por-afirmación (métrica M1).

Cada afirmación factual del output de fusión debe portar una referencia trazable a
un dato de señal/KPI del snapshot. `tasa_citacion` mide (afirmaciones citadas y
verificables) / (afirmaciones generadas). Objetivo del blueprint: >= 0,90; < 0,80 =
control insuficiente.
"""


def _fuentes_validas(snapshot_keys):
    """Conjunto de ids de fuente citables. Aquí = prefijos de las claves que el brazo
    R expone (s1.*, s2.*, k1.*). En evaluación real se carga del snapshot congelado."""
    return set(snapshot_keys or ("s1", "s2", "s3", "s4", "k1", "k2", "k3", "k4", "k5"))


def afirmacion_citada(afirmacion, fuentes):
    """True si la afirmación tiene >=1 cita y TODAS resuelven a una fuente válida."""
    citas = afirmacion.get("citas") or []
    if not citas:
        return False
    return all(str(c).split(".", 1)[0] in fuentes for c in citas)


def tasa_citacion(afirmaciones, snapshot_keys=None):
    """M1: fracción de afirmaciones citadas y verificables. Sin afirmaciones -> 1.0."""
    fuentes = _fuentes_validas(snapshot_keys)
    afs = list(afirmaciones or [])
    if not afs:
        return 1.0
    ok = sum(1 for a in afs if afirmacion_citada(a, fuentes))
    return ok / len(afs)


def audita_fusion(fusion, snapshot_keys=None):
    """Devuelve el informe de citación de una fusión (brazo R + brazo L)."""
    r = (fusion or {}).get("brazo_R") or {}
    afs = r.get("afirmaciones") or []
    l = (fusion or {}).get("brazo_L") or {}
    # el brazo L hereda las citas de R (redacta sobre ellas): se audita como un bloque
    l_af = [{"texto": l.get("sintesis", ""), "citas": l.get("citas", [])}] if l.get("sintesis") else []
    return {
        "m1_brazo_R": tasa_citacion(afs, snapshot_keys),
        "m1_brazo_L": tasa_citacion(l_af, snapshot_keys),
        "afirmaciones_R": len(afs),
        "afirmaciones_L": len(l_af),
    }
