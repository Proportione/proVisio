"""ProVisio — artefacto DSR de la tesis (Caso D: auto-monitorización de Proportione).

Instanciación situada (Gregor & Hevner 2013, nivel 1-2) del pipeline de 5 capas
del paper CAPSI, obtenida REORGANIZANDO Y ETIQUETANDO el wallboard TV operativo de
Aveiro (nodo-aveiro/tools/wallboard) — la única instalación donde L3 ejecuta un LLM
real (qwen3:14b local, €0) sobre ground-truth real, con la regla dura FR-11
(los hechos NO pasan por el LLM).

Capas:  l1_ingesta → l2_normalizacion → l3_fusion → l4_kpi → l5_presentacion
Envolturas transversales:  gobernanza (control 20-60-20) · ciclo_vida (orquestador)

Sin dependencias externas salvo `google-auth` (lazy, solo en modo --live). €0, stdlib.
Ver TRAZABILIDAD.md para el mapeo paper ↔ código.
"""
