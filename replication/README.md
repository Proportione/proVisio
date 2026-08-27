> **English summary.** This folder is the replication package accompanying the CAPSI 2026 paper *"From digital signals to sector-specific KPIs: an LLM-mediated BI artifact for SMEs"* (Cuervo & Marques). It is a runnable, offline evaluation harness (Apache-2.0, no credentials, no cloud) over frozen first-party data snapshots with per-file provenance (`evaluacion/snapshot/PROVENANCE.md`). `SCHEMA.md` mirrors the paper's Table 1; `TRAZABILIDAD.md` maps every paper claim to code. Run `python3 -m pytest tests -q` (17 tests). Full documentation below is in Spanish.

# ProVisio — artefacto DSR de la tesis (Caso D)

Instanciación opensource **evaluable** del pipeline de 5 capas del paper CAPSI 2026
(paper 17, "From digital signals to sector-specific KPIs"), obtenida
**reorganizando y etiquetando** el wallboard TV operativo interno (repo privado).
Caso D = **auto-monitorización de Proportione** (la propia PYME que opera el nodo
se monitoriza a sí misma). Licencia: este paquete se publica dentro del repo
`Proportione/proVisio` bajo **Apache-2.0**. El esquema señal-KPI (Table 1 del paper)
está documentado en `SCHEMA.md`.

> **No es un fork que reemplace producción.** El wallboard sigue vivo en la TV de
> Aveiro sin cambios. Este artefacto es una **copia reorganizada y datada** (snapshot
> reproducible) que hace legible, para la defensa DSR, la instanciación que ya corre.

## Qué es (y qué no)

- **Es** la instanciación situada (Gregor & Hevner 2013, nivel 1-2) donde **L3 fusiona
  señal→KPI** de forma explícita, con dos brazos (R determinista, L mediado por LLM
  local) y el control de gobernanza 20-60-20 instrumentado.
- **No** reclama efecto de negocio, estadística, ni la fusión completa de las 4 familias
  de señal. Ver el techo de claims en `TRAZABILIDAD.md`.

## Principios duros

€0 · **Python stdlib** (`http.server`, `urllib`, `threading`) + vanilla frontend · sin
FastAPI/React/build. Única dependencia externa (lazy, solo en modo `--live`): `google-auth`
para el id_token de la SA — la misma credencial que ya usa el wallboard, sin secretos nuevos.
**FR-11: los hechos NO pasan por el LLM** (toda cifra la calcula código determinista).

## Arquitectura (5 capas + 2 envolturas)

```
provisio/
  l1_ingesta/        L1  colectores de señal (s1_search, s2_web, s3_paid, op_crm, ...)
  l2_normalizacion/  L2  codec 3-estados + vectores de proporción + normalización
  l3_fusion/         L3  fusión señal→KPI (fusiones) · brazo R (reglas) · brazo L (llm_narrativa)
  l4_kpi/            L4  vistas KPI por tenant (k1_acquisition, vistas)
  l5_presentacion/   L5  wallboard TV kiosk (server http.server + web/ vanilla)
  gobernanza/        control 20-60-20 (confirmacion · citacion · audit_trail ENCENDIDO)
  ciclo_vida/        orquestador (aggregator stale/último-bueno · alertas · cache)
evaluacion/          protocolo FEDS (componente_a_capacidad + snapshot congelado G1)
```

Mapeo completo concepto↔módulo↔origen en **`TRAZABILIDAD.md`**.

## Estado: Incremento 1 — F-A1 (S1 + S2 → K1) end-to-end

Ejercido el carril **F-A1**: interés de búsqueda (S1, Search Console) + analítica web
(S2, GA4) → **K1 Acquisition** (funnel CRM), sobre el **snapshot congelado** (gate G1).
El colector K1 reusa **`build_leads` (+ sus 7 helpers) de `wallboard/sources/leads.py`
con cuerpo y comentarios verbatim** (lógica real de producción, no reimplementada); solo
se adaptan los docstrings de módulo/función y `collect()` para leer el snapshot congelado
en vez de llamar a core-api con la doble-auth. S3 se emite como **N/A estructural** (no `0`),
así que F-A4 queda **no ejercido** (frontera de taxonomía, diferido a Fase 3).

## Reproducir (offline, €0, sin credenciales)

Requiere solo Python 3.9+ (stdlib). Desde este directorio:

```bash
# 1) Batería de tests (invariantes del blueprint + E2E)
python3 -m unittest discover -s tests -v

# 2) Componente A — demostración de CAPACIDAD (checklist L1→L5 + fidelidad + determinismo)
python3 -m evaluacion.componente_a_capacidad --fusion fa1 --snapshot

# 3) L5 vivo — wallboard en el navegador
python3 -m provisio.l5_presentacion.server     # -> http://localhost:8080/
```

Salida esperada de (2): **5/5 verde**, fidelidad censo K1 **al conteo** (500 contactos,
216 deals, 11 follow-ups vencidos = cifras reales del snapshot), **reproducible**, y
citación-por-afirmación **M1 = 1,00 del brazo R (determinista)**.

> **Alcance exacto del M1 = 1,00 (no sobreclamar).** Offline, `build_board` corre **solo
> el brazo R** (sin LLM: por eso es determinista y reproducible), así que Componente A
> mide y reporta únicamente `m1_brazo_R`. **El brazo L (LLM, `llm_narrativa.py`) no se
> ejerce offline** — su columna `m1_brazo_L` existe en `citacion.audita_fusion` pero
> queda sin ejercitar en este snapshot. Por tanto el titular correcto del Incremento 1 es:
> **demuestra la CAPACIDAD de instrumentar la fusión F-A1 E2E, NO todavía la EFICACIA DEL
> CONTROL de gobernanza 20-60-20** (medir el reparto real R/L y la calidad de citación del
> brazo L es Componente B, **diferido** — ver roadmap punto 4 y `TRAZABILIDAD.md`).

## Modo `--snapshot` vs `--live`

- **`--snapshot`** (por defecto, reproducible): los colectores L1 leen
  `evaluacion/snapshot/*.json` (ground-truth congelado 2026-07-02, gate G1).
- **`--live`** (diferido): acuñarían id_token de la SA y llamarían a core-api / BI MCP
  con la doble-auth existente. Los colectores lanzan `NotImplementedError` explícito
  documentando la ruta live; el Incremento 1 no la necesita.

## Snapshot congelado (autocontenido)

`evaluacion/snapshot/` (ver su `PROVENANCE.md`) es autocontenido: el artefacto se re-corre
solo con los ficheros de ese directorio. La evidencia naturalista interna de los casos
(`evaluation-data/`) **no forma parte de este paquete y no se distribuye**: no está
versionada en el repositorio. Este README no la ofrece como material consultable.
El `census` de K1 son cifras reales; la lista `deals` es una shape-fixture del test-suite
de producción para ejercer `build_leads` — los 216 registros reales no se redistribuyen
(RGPD). No se inventan datos donde la instrumentación es fina.

## Roadmap por incrementos

1. ✅ **F-A1 (S1+S2→K1) E2E** + scaffolding L1-L5 + gobernanza + Componente A.
2. Carril FinOps→K5 (F-A3, BQ billing al céntimo, el mejor instrumentado).
3. Familias restantes + estados de borde (S3 N/A, S4 traza, K2 con gate de anonimización).
4. Micro-evaluación del control (Componente B, M1-M5).
5. Baseline determinista (Componente C, R vs L) + congelado G1 + techo (Componente D).

## Relación con `Proportione/proVisio` (OSS público)

El artefacto de la tesis es la instanciación **Caso D con L3 real (qwen local) sobre
ground-truth**, complementaria al stub determinista/sintético del repo público. Cierra
la deuda de honestidad del gate G3 (expediente interno de la tesis).

### Relación con los claims del paper (léase antes de comparar)

El paper (§4.4) declara: *"We do not claim that the pipeline has run end-to-end on
this case"* — y este paquete titula "ejercido el carril F-A1 end-to-end". **No es una
contradicción: son dos sustratos distintos.** (1) La *línea de producción* del Case D
del paper (core-api + Vertex AI) tiene evidenciado exactamente un tick autónomo
(18-may-2026, cero filas emitidas): el paper reporta instrumentación, no operación.
(2) Lo que este paquete ejercita end-to-end es una **demo de capacidad offline,
posterior a la sumisión**, en modo snapshot y con el brazo determinista (el brazo LLM
es opcional y degradable, regla FR-11). El paper no reclama nada de este ejercicio
como resultado operativo.
