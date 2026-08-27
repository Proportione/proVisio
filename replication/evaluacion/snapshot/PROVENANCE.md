# Snapshot congelado datado — Caso D (gate G1)

Snapshot reproducible y offline del ground-truth de Proportione, ventana **jun-2026**
(Search Console, FinOps) + **últimos 30 d** (GA4, CRM), congelado el **2026-07-02**.
Cumple la regla de ground-truth del blueprint (gate **G1**): el artefacto re-corre sobre
estos ficheros y produce **output idéntico** (determinismo del pipeline salvo la etapa LLM).

| Fichero | Señal / KPI | Fuente real | Naturaleza |
|---|---|---|---|
| `s1-search-console.json` | **S1** Search interest | Google Search Console (proportione.com) | Cifras reales (446 queries) |
| `s2-ga4.json` | **S2** Web analytics | GA4 de proportione.com (property id retirado del paquete público) | Cifras reales (317 sesiones) |
| `crm.json` | **K1** Acquisition | crm.proportione.com (core-api) | `census` real (500 contactos, 216 deals, 11 follow-ups vencidos); `deals[]` = shape-fixture 100% sintética (nombres, empresas e importes inventados) que reproduce la variedad de etapas del test-suite de producción para ejercer `build_leads` (su cuerpo y comentarios son verbatim de `wallboard/sources/leads.py`; solo `collect()` se adapta para leer este snapshot en vez de core-api live) |

## Alcance de este snapshot

Este snapshot es autocontenido: lo componen los tres ficheros de la tabla anterior y este
`PROVENANCE.md`, y nada más. La evidencia naturalista interna de los casos
(`evaluation-data/`) **no forma parte del paquete publicable** y no se distribuye: no está
versionada en el repositorio. En particular, **el audit-log de Caso D no se publica**. Ver
`TRAZABILIDAD.md` para el mapeo de lo que sí contiene este paquete.

## Frontera honesta (techo de claims)

- **S3 Paid media = N/A estructural** (`googleAdsCustomerId = null`): no hay fichero de snapshot
  porque no hay señal; el colector `s3_paid.py` emite ausencia estructural, no un `0`.
- **S4 Comms/social = traza** (4 sesiones social): diferido a Incremento 3.
- El `census` de K1 es real; el desglose de pipeline se ejerce sobre la shape-fixture. La cifra
  publicable de K1 sale del `census`. No se inventan datos donde la instrumentación es fina.
