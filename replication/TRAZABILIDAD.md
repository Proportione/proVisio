# Trazabilidad paper ↔ código — Artefacto ProVisio (Caso D)

Condición DSR de *instanciación* (Gregor & Hevner 2013, nivel 1-2): cada concepto del
artefacto del paper CAPSI está anclado a un módulo concreto, y cada módulo declara su
origen en el wallboard de producción del que se reorganiza. El artefacto **no inventa
capacidad**: hace legible y reproducible la que ya corre en Aveiro.

## Origen (encuadre honesto, gate G3)

La dashboard viva de Caso D en `bi.proportione.com` es display de widgets (sustrato
L1/L2/L4/L5 **sin L3**). El repo público `Proportione/proVisio` es un stub determinista
sobre datos sintéticos. **El wallboard TV interno** (repo privado)
es el único sitio donde **L3 ejecuta un LLM real** (`sources/insight.py`, qwen3:14b local,
€0) sobre ground-truth real, con la regla dura FR-11 (*los hechos NO pasan por el LLM*).
Este artefacto **explicita** esa instanciación. Complementa (no duplica) el stub público.

## Tabla de trazabilidad

| Concepto del artefacto (paper/blueprint) | Módulo del artefacto | Origen en el wallboard de producción | Incr. |
|---|---|---|---|
| **L1 Ingesta** (contrato NAME/CADENCE/collect) | `provisio/l1_ingesta/*` | `sources/*.py` | 1 |
| **L2 Normalización** | `provisio/l2_normalizacion/{tri_estado,vectores,compose}.py` | `aggregator.compose`, `build_empty_board` | 1 |
| **L3 Fusión semántica (C-2)** | `provisio/l3_fusion/fusiones.py` (+ `reglas.py`, `llm_narrativa.py`) | `sources/insight.py` (implícito) | 1 |
| **L4 Vistas KPI por tenant** | `provisio/l4_kpi/{k1_acquisition,vistas}.py` | `aggregator._empty_screens` | 1 |
| **L5 Presentación** | `provisio/l5_presentacion/{server.py,web/}` | `server.py` + `web/` (whitepaper 040) | 1 |
| **S1 Search interest** (fina) | `l1_ingesta/s1_search.py` | — (nuevo; hoy en `bi.proportione.com`) | 1 |
| **S2 Web analytics** (presente) | `l1_ingesta/s2_web.py` | — (nuevo) | 1 |
| **S3 Paid media** (N/A estructural) | `l1_ingesta/s3_paid.py` + `l2/tri_estado.NA_ESTRUCTURAL` | — (nuevo; `googleAdsCustomerId=null`) | 1 |
| **S4 Comms/social** (traza) | `l1_ingesta/s4_comms.py` *(diferido)* | — | 3 |
| **K1 Acquisition** | `l4_kpi/k1_acquisition.py` ← `op_crm.py` | `sources/leads.py` (`build_leads` + 7 helpers: **cuerpo y comentarios verbatim**; solo docstrings de módulo/función y `collect()` adaptados —snapshot vs core-api live) | 1 |
| **K2 Revenue** (sensible) | `l4_kpi` + gate anonimización *(diferido)* | `sources/leads.py` | 3 |
| **K3 Retention** | `op_soporte.py` *(diferido)* | `sources/tickets.py` | 3 |
| **K4 Awareness** (fina) | `l4_kpi/k4` *(diferido)* | — (deriva de S1∩brand + S4) | 3 |
| **K5 Efficiency** (al céntimo) | `op_finops.py` + `op_salud.py` *(diferido)* | `sources/health.py`; FinOps nuevo (BQ) | 2 |
| **Carril operativo FinOps (Salida B)** | `l1_ingesta/op_finops.py` *(diferido)* | `sources/arquitectura.py` (solo estimado) → sustituido | 2 |
| **F-A1 S1+S2→K1** (ejercido) | `l3_fusion/fusiones.py::fa1` | — (nuevo) | **1** |
| **F-A2 S1∩brand+S4→K4** (fino) | `fusiones.py::fa2` *(diferido)* | — | 3 |
| **F-A3 FinOps→K5** (carril) | `fusiones.py::fa3` *(diferido)* | — | 2 |
| **F-A4 S3→advertiser** (NO ejercido) | `fusiones.py::fa4` → `N/A` estructural | — (diferido Fase 3 / tenant advertiser) | 1 |
| **Control 20-60-20 (C-4, P2)** | `provisio/gobernanza/{confirmacion,citacion,audit_trail}.py` | `insight.py` (confinamiento) + `aggregator._log_evidence` | 1 |
| **Brazo R (baseline determinista)** | `l3_fusion/reglas.py` + `ciclo_vida/alertas.py` | `sources/success.py` + `derive_alerts` | 1 |
| **Brazo L (LLM+control)** | `l3_fusion/llm_narrativa.py` | `sources/insight.py` | 1 |
| **Ciclo de vida / stale / último-bueno** | `ciclo_vida/aggregator.py` (`is_stale`, `poll_once`, `run`) | `aggregator` (verbatim) | 1 |
| **Audit-log append-only a nivel de aplicación (FEDS C4/C2; C5 NO reclamado)** | `gobernanza/audit_trail.py` (**ENCENDIDO**) — emitido por `poll_once` (loop vivo) **y** por `build_board(audit=True)` (Componente A) | `aggregator._log_evidence` (OFF por defecto) | 1 |
| **Componente A capacidad (E1)** | `evaluacion/componente_a_capacidad.py` (deja audit-trail: `build_board(audit=True)`) | — | 1 |
| **Componente B control M1–M5 (E2)** | `evaluacion/componente_b_control.py` *(diferido)* | — | 4 |
| **Componente C baseline C1–C5** | `evaluacion/componente_c_baseline.py` *(diferido)* | R vs L ya conviven | 5 |
| **Componente D techo/anonimización** | `evaluacion/componente_d_techo.py` *(diferido)* | — | 5 |
| **Snapshot congelado datado (G1)** | `evaluacion/snapshot/` | — (evidencia interna de casos, no distribuida) | 1 |
| **P1 señal=parámetro por tenant** | `l3_fusion/fusiones.py` (`POLARIDAD`) | — | 1 |
| **P2 LLM en fusión exige control** | `provisio/gobernanza/*` | — | 1 |

## Invariantes de diseño verificados por tests (Incr. 1)

| Invariante (blueprint) | Módulo | Test |
|---|---|---|
| Las S no se mezclan con las K salvo en L3 | `l3_fusion/fusiones.py` | `test_fusion_ejercida` |
| FinOps = carril operativo, NO S5 | `TRAZABILIDAD` + `vistas.k5` nota | (documental) |
| Codec 3 estados: N/A ≠ traza ≠ cero | `l2/tri_estado.py` | `test_na_no_es_cero`, `test_traza_vs_valor` |
| N/A estructural no divide el vector | `l2/vectores.py` | `test_na_no_divide_el_vector` |
| FR-11: los hechos no pasan por el LLM | `l3_fusion/` (brazo R autoritativo) | `test_fr11_las_cifras_no_las_pone_el_llm` |
| Citación-por-afirmación **brazo R** (M1_R ≥ 0,90; offline = 1,00) | `gobernanza/citacion.py` | `test_citacion_por_afirmacion` |
| F-A4 no ejercido (S3 N/A) | `fusiones.py::fa4` | `test_fa4_no_ejercida` |
| Reproducibilidad del snapshot (G1) | `ciclo_vida/aggregator.build_board` | `componente_a.run["reproducible"]` |
| Fidelidad cifra-panel = cifra-fuente | `evaluacion/componente_a` | `test_capacidad_verde_y_fiel` |
| Audit-trail emitido por Componente A / `build_board(audit=True)` | `gobernanza/audit_trail.py`, `aggregator.build_board` | `test_componente_a_deja_audit_trail`, `test_audit_on_emite_log_fusion`, `test_audit_off_por_defecto_no_escribe` |

## Titular del Incremento 1: CAPACIDAD, no eficacia del control

El Incremento 1 demuestra la **CAPACIDAD** de instrumentar la fusión F-A1 (S1+S2→K1) de
extremo a extremo sobre ground-truth congelado. **NO** demuestra todavía la **EFICACIA DEL
CONTROL** de gobernanza 20-60-20. Razón concreta y verificable: offline, `build_board`
ejecuta **solo el brazo R (determinista, sin LLM)**, y por eso Componente A obtiene y reporta
únicamente `m1_brazo_R = 1,00`. **El brazo L (LLM, `llm_narrativa.py`) no se ejerce offline**
—`citacion.audita_fusion` deja `m1_brazo_L` disponible pero sin ejercitar en el snapshot—, de
modo que el reparto real R/L del control 20-60-20 y la calidad de citación del brazo L **no
están medidos aquí**. Esa micro-evaluación es **Componente B (E2, diferido, Incr. 4)**. En
resumen: `M1 = 1,00` es una propiedad del **baseline R**, no una medida de que el control
sobre el LLM funcione.

## Techo de claims (no negociable)

**Permitido:** capacidad/viabilidad de instrumentación E2E · eficacia formativa del control ·
decisión de diseño razonada (Salida B: FinOps carril, no S5) · frontera de taxonomía (S3 N/A).
**PROHIBIDO:** efecto de negocio · estadística (n pequeño) · polaridad advertiser (F-A4) ·
fusión completa de las 4 familias · generalización multi-tenant · **eficacia del control
20-60-20 a partir de `M1 = 1,00`** (eso es solo el brazo R; el brazo L no se ejerce offline).
