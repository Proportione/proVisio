"""L2 — Normalización. Aislamiento por tag + codec de 3 estados + vectores/razones.

Materializa lo que en el wallboard estaba implícito en `aggregator.compose`:
  - tri_estado: N/A estructural  !=  traza (near-zero medido)  !=  cero.
  - vectores: vector de proporciones (canales GA4, suma 1) y razones acotadas [0,1].
  - compose: contrato de claves del board + normalización de las señales L1.
"""
