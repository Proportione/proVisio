"""Vectores de proporción y razones acotadas (blueprint §S2).

- vector_proporciones: reparto por canal (GA4) como vector que suma 1. Excluye
  celdas N/A estructurales para no dividir por señales ausentes.
- razon_acotada: tasa recortada a [0,1] (bounce, CTR, newUsers/sesiones).
"""

from . import tri_estado


def vector_proporciones(counts):
    """dict {clave: conteo} -> {clave: proporción}, suma 1. Ignora celdas N/A
    estructurales y valores no numéricos. {} o total 0 -> {}."""
    limpio = {k: float(v) for k, v in (counts or {}).items()
              if tri_estado.es_computable(v) and isinstance(v, (int, float))}
    total = sum(limpio.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in limpio.items()}


def razon_acotada(numerador, denominador):
    """numerador/denominador recortado a [0,1]. denominador<=0 -> None."""
    try:
        num, den = float(numerador), float(denominador)
    except (TypeError, ValueError):
        return None
    if den <= 0:
        return None
    return max(0.0, min(1.0, num / den))
