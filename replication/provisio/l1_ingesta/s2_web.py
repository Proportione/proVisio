"""S2 — Web analytics (GA4; property id retirado del paquete público).

Familia de SEÑAL. Presente: 317 sesiones/30d, dominadas por Direct (210).
El reparto por canal se normaliza en L2 como vector de proporciones (suma 1);
las tasas (bounce, newUsers/sesiones) como razones acotadas [0,1].

Modo --snapshot: lee `s2-ga4.json` (congelado 2026-07-02, real).
Modo --live (diferido): `mcp bi_ga4_report` / core-api con doble-auth SA.
"""

from ._snapshot import load

NAME = "s2_web"
CADENCE_SECONDS = 1800
FAMILIA = "S2"


def collect(config):
    """Sub-árbol crudo de S2. Lanza si el snapshot falta -> bloque stale."""
    if (config or {}).get("mode", "snapshot") != "snapshot":
        raise NotImplementedError(
            "s2_web modo --live diferido: llamaría a bi_ga4_report (MCP). "
            "Incremento 1 usa el snapshot congelado.")
    return load("s2-ga4.json", config)
