"""L1 — Ingesta. Colectores de señal.

Contrato de colector (heredado verbatim del wallboard de producción):
  NAME: str
  CADENCE_SECONDS: int
  FAMILIA: str | tuple[str, ...]      # familia S/K declarada (etiquetado del paper)
  def collect(config: dict) -> dict   # sub-árbol; lanza excepción si falla (-> stale)

Novedad del artefacto frente al wallboard: cada colector DECLARA su familia
(S1-S4 = señales marketing-scoped; K1-K5 = KPIs de negocio; op = carril operativo).
El invariante del blueprint es que las S no se mezclan con las K salvo en L3 (fusión).

Incremento 1 ejerce el carril F-A1 (S1 + S2 -> K1). COLECTORES_I1 es el registro
mínimo end-to-end; el registro completo (op_finops, s4_comms, op_soporte, ...) se
puebla en los incrementos 2-3 (ver TRAZABILIDAD.md).
"""

from . import s1_search, s2_web, s3_paid, op_crm

# Registro Incremento 1: el aggregator itera sobre estos para componer el board.
COLECTORES_I1 = (s1_search, s2_web, s3_paid, op_crm)

__all__ = ["s1_search", "s2_web", "s3_paid", "op_crm", "COLECTORES_I1"]
