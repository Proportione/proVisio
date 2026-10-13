# Architecture — Proportione Visio

> Companion document to a research artifact described in a manuscript currently under pre-publication review. The accompanying manuscript discusses the methodology and evaluation; this file describes the **as-built architecture** of the public artifact.

## At a glance

Visio is a multi-tenant Business Intelligence artifact that places business KPIs (sales, NPS, ticketing, captation, donations) and digital signals (web traffic, organic positioning, paid advertising, social) on the same view, quantifies their relationship, and surfaces prioritised recommendations.

It is engineered as a thin Streamlit front-end over a pluggable signal-ingestion + KPI-store backend, with an optional LLM fusion layer that turns raw correlations into narrative recommendations.

## Five-layer stack

```
┌────────────────────────────────────────────────────────────────────┐
│ L5  AuthZ            Google OAuth · email-based tenant routing     │
│                      (production also enforces row-level isolation │
│                       in BigQuery; this public repo simulates it)  │
├────────────────────────────────────────────────────────────────────┤
│ L4  KPI views        Streamlit pages (one per tenant) +            │
│                      Plotly figures + reusable widgets             │
├────────────────────────────────────────────────────────────────────┤
│ L3  LLM fusion       (optional) Vertex AI / Anthropic / local OSS  │
│                      Generates narrative + scoring breakdowns      │
│                      from L2 normalised series                     │
├────────────────────────────────────────────────────────────────────┤
│ L2  Normalise        pandas DataFrames in canonical schema         │
│                      (signal_family × kpi_family per tenant)       │
├────────────────────────────────────────────────────────────────────┤
│ L1  Ingest           Connectors: GA4, Search Console, Google Ads,  │
│                      FinOps GCP, custom (Brevo, BigQuery views)    │
│                      Each tenant declares which connectors apply   │
└────────────────────────────────────────────────────────────────────┘
```

## Component inventory and licensing

| Layer | Component | Licence | OSS share | Notes |
|---|---|---|---|---|
| L1 Ingest | Google APIs (GA4 / Search Console / Ads) | Proprietary | 0% | Swappable for Plausible / Matomo (AGPL) + custom crawler |
| L1 Ingest | Brevo SDK and bespoke adapters | MIT / AGPL | 100% | Each adapter is a thin Python module under `connectors/` |
| L2 Normalise | pandas, PyArrow | BSD-3, Apache-2.0 | 100% | |
| L2 Normalise | google-cloud-bigquery (client) | Apache-2.0 | 100% (client) | Storage layer is swappable: PostgreSQL + TimescaleDB |
| L3 LLM fusion | Vertex AI Gemini | Proprietary cloud | 0% | Swappable for Ollama + Nemotron / Qwen / DeepSeek |
| L4 KPI views | Streamlit | Apache-2.0 | 100% | |
| L4 KPI views | Plotly | MIT | 100% | |
| L5 AuthZ | Google OAuth + custom checks | OAuth standard | ~80% | Production hardens with BigQuery row-level security |
| MCP server | `@modelcontextprotocol/sdk` | MIT | 100% | Used by the production deployment, not required for the demo |

Weighted total: roughly **80–85% open-source** by lines of dependency. Every proprietary cell above is replaceable without changing the artifact's signal-KPI schema.

## The 20-60-20 collaboration model

Visio applies the **20-60-20 framework** previously introduced by the same line of work in two domains (higher education, defence) — see the paper for citations. The name refers to the framework; the figures are not measured proportions of effort. It distinguishes three stages:

- **Human input** — the operator parameterises the tenant, picks a focal KPI and a temporal window.
- **AI generation** — the LLM fusion layer ingests heterogeneous signals, normalises them, performs semantic integration against the KPI schema, and produces narrative explanations with scoring breakdowns.
- **Human judgement** — the decision-maker accepts, modifies, or rejects each recommendation. Every action is written to an immutable audit log.

The public repository ships the L2 / L4 layers with synthetic data so the 20-60-20 model can be exercised without GCP credentials. The L3 LLM layer is a stub that returns deterministic narratives; production code for the LLM step is not part of this public release.

## Replicability path: cloud-first ↔ self-hosted

The artifact is engineered so that a reviewer or an SME with self-hosting preferences can replace each cloud cell with an open-source equivalent without touching the L2 schema or the L4 views. Concretely:

| Layer | Cloud-first (production) | Self-hosted swap | Effort estimate |
|---|---|---|---|
| Storage | BigQuery | PostgreSQL + TimescaleDB | 40–60 h |
| Web analytics | GA4 | Plausible / Matomo (AGPL) | 30–40 h |
| SEO signals | Google Search Console | Custom crawler + Lighthouse OSS | 50–80 h |
| LLM | Vertex AI | Ollama + Nemotron / Qwen 32B | 20–30 h, hardware-dependent |
| Compute | Cloud Run | Docker Compose + Caddy | 10–20 h |
| Auth | Google OAuth | Keycloak (Apache-2.0) | 30–50 h |

These figures are estimates from the production deployment, included here so a reviewer can budget a self-hosted reproduction.

## Deployment status (October 2026)

The production deployment described in this document (v1: Streamlit front-end and Core API on Cloud Run) was retired on 17 September 2026. The case-study instance has since been reimplemented privately (v2) on the company's own infrastructure, keeping the layered design (KPI store, digital signals, LLM-mediated recommendations) with declarative KPI contracts and a local LLM. It is not publicly accessible and its code is not part of this repository. References to "production" below describe v1.

## Multi-tenant isolation — current state and known gap

Production routes tenants by authenticated email; row-level filtering is then performed in BigQuery views per `tenant_id`. The public repo simulates this with synthetic data and a `tenant_id` column on every table.

A documented gap from the production system is that BigQuery row-level security (RLS) policies are not yet enforced at the database level — isolation is currently logical, not physical. The accompanying manuscript acknowledges this gap explicitly in its discussion of responsible-AI design choices.

## Where the LLM layer ends and the BI layer begins

A common confusion when reading code that mixes "AI" and "BI": Visio treats the LLM strictly as a narrative + scoring generator over already-normalised series. The LLM does not see raw API payloads, does not store credentials, and does not call out to data sources directly. Every prompt is a structured payload assembled in L2 from validated DataFrames, with the prompt template and the assembled payload both written to the audit log.

Concretely, the L3 stub in `visio/llm/stub.py` shows the contract that production satisfies:

```python
def fuse(signals: dict[str, pd.DataFrame], kpi: pd.Series) -> Recommendation:
    """Combine normalised signals with a target KPI series and return a
    structured recommendation. Production replaces the body with a Vertex
    AI call; the public stub returns deterministic narratives so the demo
    is reproducible."""
```

## What is **not** in this repository

For honesty and to reduce the surface for accidental disclosure, the following are deliberately excluded:

- OAuth client secrets, BigQuery dataset IDs, GA4 property IDs, Ads customer IDs, Brevo API keys, Anthropic / Vertex tokens.
- Tenant-specific page implementations (each production tenant has its own page; the public release ships a single `tenant_template.py` that any tenant page can be derived from).
- The Core API (a separate Cloud Run service) that mediates between the Streamlit front-end and BigQuery in production.
- Any real customer data; only synthetic series are bundled.

## How the synthetic generator stays honest

The synthetic data generator (`visio/synthetic/`) is engineered to reproduce the *shape* of real signals (seasonality, weekly cycles, noise characteristics) without leaking any real value. It does this by drawing parameters from documented public ranges (for example, "B2B SaaS conversion rate typically 1–3 %"), so the demonstration looks realistic but is non-attributable.

A reviewer running the demo sees realistic-looking dashboards. A reader trying to identify a real customer from the synthetic series will not succeed because none of the parameter draws are tied to any production deployment.
