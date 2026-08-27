"""S1 — Search interest (Google Search Console, propiedad proportione.com).

Familia de SEÑAL (marketing-scoped), NO KPI. Alimenta F-A1 (con S2 -> K1) y, la
subseñal *brand*, F-A2 (-> K4). Presente-fina: 446 queries, marca floja.

Modo --snapshot: lee `s1-search-console.json` (congelado 2026-07-02, real).
Modo --live (diferido): `mcp bi_search_console` / core-api con doble-auth SA.
"""

from ._snapshot import load

NAME = "s1_search"
CADENCE_SECONDS = 3600  # el interés de búsqueda no cambia por minuto
FAMILIA = "S1"


def collect(config):
    """Sub-árbol crudo de S1. Lanza si el snapshot falta -> bloque stale."""
    if (config or {}).get("mode", "snapshot") != "snapshot":
        raise NotImplementedError(
            "s1_search modo --live diferido: llamaría a bi_search_console (MCP) "
            "con id_token SA. Incremento 1 usa el snapshot congelado.")
    return load("s1-search-console.json", config)
