# Signal-KPI schema (Table 1 del paper CAPSI 2026, paper 17)

Esquema sector-agnóstico de ProVisio: las fuentes ingeridas colapsan en **cuatro
familias de señal (S1–S4)** y las métricas sector-específicas de cada tenant son
instancias de **cinco familias de KPI (K1–K5)**. Este fichero espeja la Table 1
del paper; la implementación vive en `provisio/l1_ingesta/` (S1–S3),
`provisio/l2_normalizacion/` (vectores y tri-estado) y `provisio/l4_kpi/` (K1).

## Familias de señal

| Código | Familia y fuentes de ejemplo |
|---|---|
| S1 | Search interest: Google Trends, Search Console queries |
| S2 | Web analytics: GA4, Firebase, custom pageview trackers |
| S3 | Paid media: Google Ads, Ad Manager |
| S4 | Comms engagement: newsletter, social, press mentions |

## Familias de KPI

| Código | Familia y ejemplos |
|---|---|
| K1 | Acquisition: enrolments, leads, donor first-touch |
| K2 | Revenue: sales, advertising revenue, donations, subscriptions |
| K3 | Retention: repeat visits, churn, NPS, completion |
| K4 | Awareness: brand search, share of voice, reach |
| K5 | Efficiency: CPA, FinOps cost, SLA, cost-per-engaged-reader |

## Estado de ejercicio en este paquete

Este paquete ejercita el carril **F-A1 (S1+S2 → K1)** end-to-end en modo snapshot
(ver `TRAZABILIDAD.md`). S3 se representa como N/A estructural (no como 0) y S4/K2–K5
están definidos en el esquema pero no ejercidos aquí — coherente con lo que el paper
declara en §5.2 (demostración temprana, un carril).
