"""Mapa señal -> KPI EXPLÍCITO (F-A1..F-A4). El módulo que el wallboard no tenía:
insight.py NARRABA pantallas, no FUSIONABA S->K. Aquí la fusión es un objeto de
primera clase, con la señal tratada como PARÁMETRO interpretado por tenant (P1,
polaridad), no como magnitud fija.

Incremento 1 ejerce F-A1. F-A2/F-A3 se ejercen en Incr. 2-3; F-A4 devuelve N/A
estructural (S3 ausente, diferido a Fase 3).
"""

from ..l2_normalizacion import compose, tri_estado
from . import reglas


# Polaridad de la señal por tenant (P1): cómo se interpreta la demanda. Proportione
# = adquisición por marca/relación (no advertiser, no publisher). El parámetro existe
# para que la MISMA fusión sirva a un advertiser (S3+) o un publisher sin
# ramificar código — la contribución del patrón, aunque su instancia advertiser (F-A4)
# NO se ejerce en Caso D.
POLARIDAD = {
    "proportione": "demanda-marca",   # Caso D
    "advertiser": "retorno-inversion",
    "publisher": "audiencia-monetizable",
}


def fa1(s1_raw, s2_raw, k1_crm, tenant="proportione", brazo_l=None):
    """F-A1: S1 (Search interest) + S2 (Web analytics) -> K1 Acquisition.

    Determinista salvo `brazo_l` (callable opcional que redacta NL sobre los MISMOS
    hechos; si es None o falla, la fusión sigue con solo el brazo R). Devuelve el
    registro de fusión con inputs normalizados, lectura R y (si hay) narrativa L."""
    s1 = compose.normaliza_s1(s1_raw)
    s2 = compose.normaliza_s2(s2_raw)
    r = reglas.lectura_fa1(s1, s2, k1_crm)

    fusion = {
        "id": "F-A1",
        "entrada": ["S1", "S2"],
        "kpi": "K1",
        "estado_carril": "ejercido",
        "polaridad": POLARIDAD.get(tenant, "demanda-marca"),
        "inputs_normalizados": {"s1": s1, "s2": s2},
        "brazo_R": r,
        "brazo_L": None,
    }
    if brazo_l is not None:
        try:
            fusion["brazo_L"] = brazo_l(s1, s2, k1_crm, r)
        except Exception as e:  # el LLM nunca tumba la fusión (degrada al brazo R)
            fusion["brazo_L"] = {"error": type(e).__name__}
    return fusion


def fa4(s3_raw):
    """F-A4: S3 (paid) -> polaridad advertiser. NO EJERCIDO: S3 es N/A estructural."""
    return {
        "id": "F-A4",
        "entrada": ["S3"],
        "kpi": "advertiser-return",
        "estado_carril": "no_ejercido",
        "motivo": tri_estado.na_estructural(
            "S3 ausente (googleAdsCustomerId=null) — diferido a Fase 3 / tenant advertiser"),
    }
