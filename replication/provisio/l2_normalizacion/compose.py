"""Normalización de señales L1 -> forma L2 + contrato de claves del board.

Deriva de `aggregator.compose` / `build_empty_board` del wallboard, separando la
NORMALIZACIÓN (aquí, L2) del esquema de PANTALLAS por familia K (l4_kpi/vistas.py).
"""

from . import tri_estado, vectores


def normaliza_s1(raw):
    """S1 crudo (Search Console) -> vector normalizado. CTR branded como razón [0,1]."""
    br = (raw or {}).get("branded") or {}
    impr = br.get("impressions")
    clicks = br.get("clicks")
    return {
        "queries_total": (raw or {}).get("queries_total", 0),
        "branded": {
            "query": br.get("query"),
            "impressions": impr, "clicks": clicks, "position": br.get("position"),
            "ctr": vectores.razon_acotada(clicks, impr),
        },
        "top_nonbranded": (raw or {}).get("top_nonbranded", []),
    }


def normaliza_s2(raw):
    """S2 crudo (GA4) -> vector de proporciones por canal (suma 1) + razones acotadas."""
    raw = raw or {}
    canales = raw.get("channels") or {}
    sesiones = raw.get("sessions", 0)
    return {
        "sessions": sesiones,
        "channel_mix": vectores.vector_proporciones(canales),
        "newuser_ratio": vectores.razon_acotada(raw.get("newUsers"), sesiones),
        "pageviews_per_session": (raw.get("pageviews") / sesiones) if sesiones else None,
        "bounce_direct": raw.get("bounce_direct"),
    }


def build_empty_board(colectores):
    """Board vacío VÁLIDO contra el contrato (todos los bloques stale)."""
    from ..ciclo_vida.aggregator import now_iso
    return {
        "generatedAt": now_iso(),
        "tenant": "proportione",  # Caso D: auto-monitorización
        "alerts": [],
        "blocks": {c.NAME: {"lastOk": None, "stale": True} for c in colectores},
        "signals": {},
        "screens": {},
        "fusion": {},
    }
