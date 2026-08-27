"""Esquema de pantallas KPI por familia (deriva de aggregator._empty_screens).

Cada familia K tiene una vista con claves estables. Incremento 1 puebla K1; K2-K5
declaran su esquema vacío (contrato presente, datos en incrementos posteriores)."""


def vista_vacia():
    return {
        "k1": {},  # Acquisition (Incr. 1)
        "k2": {"estado": "diferido_incr3", "nota": "Revenue: gate de anonimización (M5)"},
        "k3": {"estado": "diferido_incr3", "nota": "Retention: SLA/tickets (proxy CSAT)"},
        "k4": {"estado": "diferido_incr3", "nota": "Awareness: F-A2 (fino/no accionable)"},
        "k5": {"estado": "diferido_incr2", "nota": "Efficiency: FinOps al céntimo (F-A3)"},
    }
