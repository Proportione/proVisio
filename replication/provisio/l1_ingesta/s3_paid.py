"""S3 — Paid media. N/A ESTRUCTURAL en Caso D.

Proportione NO tiene cuenta de Google Ads (`googleAdsCustomerId = null`). S3 es
NULO POR RESTRICCIÓN DURA del tenant, no "cero medido". El colector emite una celda
estructuralmente vacía (l2.tri_estado.NA_ESTRUCTURAL) que NO entra en normalizaciones
ni razones y hace que F-A4 (S3 -> polaridad advertiser) quede NO EJERCIDA (diferida
a Fase 3 / tenant advertiser). Representar S3 como `0` sería un error de tipado que rompe
el claim de frontera de la taxonomía.
"""

from ..l2_normalizacion import tri_estado

NAME = "s3_paid"
CADENCE_SECONDS = 3600
FAMILIA = "S3"


def collect(config):
    """Devuelve ausencia estructural. NUNCA lanza ni devuelve 0: la ausencia ES el dato."""
    return tri_estado.na_estructural(
        "googleAdsCustomerId=null — Proportione no tiene cuenta de Google Ads")
