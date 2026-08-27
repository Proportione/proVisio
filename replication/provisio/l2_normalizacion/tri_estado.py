"""Codec de 3 estados (invariante del blueprint).

Distingue tres cosas que un `0` colapsaría y que romperían el claim de frontera:

  NA_ESTRUCTURAL  — ausencia por restricción dura del tenant (S3: googleAdsCustomerId
                    = null). NO entra en normalizaciones ni razones (no divide el
                    vector de señales). La ausencia ES el dato.
  TRAZA           — magnitud medida cerca de cero pero presente (S4: 4 sesiones social).
                    Cuenta como señal, marcada como no-accionable.
  VALOR           — magnitud medida ordinaria.
"""

NA_ESTRUCTURAL = "na_estructural"
TRAZA = "traza"
VALOR = "valor"


def na_estructural(razon):
    """Celda estructuralmente vacía. `valor=None` a propósito: no es 0."""
    return {"estado": NA_ESTRUCTURAL, "razon": razon, "valor": None}


def traza(valor, umbral):
    """Magnitud presente pero por debajo de `umbral` -> traza (no-accionable)."""
    estado = TRAZA if (valor is not None and valor <= umbral) else VALOR
    return {"estado": estado, "valor": valor, "umbral": umbral}


def es_na(x):
    return isinstance(x, dict) and x.get("estado") == NA_ESTRUCTURAL


def es_computable(x):
    """True si el estado puede entrar en normalizaciones/razones (no es N/A estructural)."""
    return not es_na(x)
