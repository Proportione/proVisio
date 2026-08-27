"""L3 — Fusión semántica señal -> KPI. CONTRIBUCIÓN CENTRAL (C-2).

El único punto del pipeline donde las señales S se cruzan con los KPIs K, y de forma
DIRIGIDA (F-A1..F-A4). Dos brazos que conviven sobre la misma entrada:
  - reglas.py       brazo R (determinista, 0 alucinación por construcción)
  - llm_narrativa.py brazo L (qwen3:14b local; REDACTA, no produce cifras — FR-11)
fusiones.py fija el mapa señal->KPI y la polaridad por tenant (P1). El control
20-60-20 (gobernanza/) envuelve el brazo L.
"""
