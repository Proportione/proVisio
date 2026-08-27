# Provisio

[![Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/streamlit-1.40+-FF4B4B.svg)](https://streamlit.io)
[![Status](https://img.shields.io/badge/status-research%20artifact-orange.svg)](#status)

A multi-tenant Business Intelligence artifact that puts SME business KPIs and digital signals on the same view, quantifies their relationship, and surfaces prioritised recommendations through an optional LLM-mediated fusion layer.

This repository is the public reference implementation of a research artifact described in a paper accepted at CAPSI 2026 (26th Conference of the Portuguese Association for Information Systems, Coimbra, 8–10 October 2026; proceedings in the AIS eLibrary). See [CITATION.cff](CITATION.cff). The corresponding production deployment runs at the URL declared on the repository's homepage.

## What you can do here

- **Run the demo locally with synthetic data**, no Google Cloud credentials needed.
- **Read the architecture** of a production multi-tenant BI artifact: see [ARQUITECTURA.md](ARQUITECTURA.md).
- **Cite the artifact** in your own work: see [CITATION.cff](CITATION.cff).
- **Replicate the paper's evaluation** offline, with no credentials and no cloud: see [`replication/`](replication/) — a runnable evaluation harness over frozen, provenance-documented data snapshots (`python3 -m pytest replication/tests -q`).
- **Adapt one of the connectors** to a different SaaS source by following the contract in `visio/connectors/`.

## Quick start (synthetic, ~2 min)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run visio/app.py
```

The demo opens in your browser, lists three synthetic tenants, and renders the methodological page template (`visio/pages/tenant_template.py`) for any of them. No external API is contacted.

## Quick start (real Google data, ~30 min one-off setup)

1. Install the cloud extras: `pip install -r requirements-cloud.txt`.
2. Provide credentials (one of):
    - `GOOGLE_APPLICATION_CREDENTIALS` pointing at a service-account JSON, or
    - `gcloud auth application-default login` if you prefer ADC.
3. Edit `visio/tenants/tenants.example.toml` to declare your real GA4 property ID, Search Console site, Ads customer ID, and BigQuery dataset.
4. `streamlit run visio/app.py` again.

The same pages now read live data instead of synthetic series. The L3 LLM layer remains a stub; bring your own model by replacing `visio/llm/stub.py`.

## Repository layout

```
visio-public/
├── ARQUITECTURA.md                  Architecture, OSS shares, replicability table
├── CITATION.cff                     Cite the artifact / paper
├── LICENSE                          Apache-2.0
├── README.md                        This file
├── VERTICALS.md                     Sector variants: invariant core vs per-sector config
├── requirements.txt                 Demo dependencies (synthetic only)
├── requirements-cloud.txt           Optional Google Cloud connectors
└── visio/
    ├── app.py                       Streamlit entry point
    ├── auth.py                      Email-based tenant routing (no secrets)
    ├── widgets/                     Reusable, sector-agnostic widgets
    │   ├── ga4.py
    │   ├── search_console.py
    │   ├── google_ads.py
    │   ├── finops.py
    │   └── kpi_card.py
    ├── connectors/                  Source readers (each one swappable)
    │   ├── ga4.py
    │   ├── search_console.py
    │   ├── google_ads.py
    │   └── bigquery.py
    ├── llm/
    │   └── stub.py                  Deterministic L3 stub
    ├── synthetic/
    │   └── generator.py             Realistic, non-attributable mock series
    ├── tenants/
    │   └── tenants.example.toml     Tenant declaration shape
    └── pages/
        └── tenant_template.py       The single sanitised page template
```

The production deployment uses the same `visio/widgets/` and `visio/connectors/` packages, and adds one private page per tenant. Tenant pages and the Core API are not part of this public release.

## Status

Research artifact. The accompanying manuscript introduces the artifact methodologically; this repository is the reference implementation cited in that manuscript. The research line continues with empirical case studies on Iberian SMEs.

The 20-60-20 collaboration framework that organises the artifact's human-AI split has prior validations in two adjacent domains; see [ARQUITECTURA.md](ARQUITECTURA.md) §"The 20-60-20 collaboration model" for the cite chain.

What this repository ships is the sector-agnostic method. The products derived from it are sector variants — **proVisio Media** (news and media), **proVisio Educatio** (education and training) and **proVisio Commercio** (retail and D2C) — configuration packs over this same core, not forks of it. The boundary is recorded in [VERTICALS.md](VERTICALS.md); none of the variants exists as running code.

## Responsible AI

The artifact is classified as **limited risk** under the EU AI Act (Reg. UE 2024/1689). Its design follows the seven principles of the EU AI HLEG (2019), the controls of ISO/IEC 42001:2023 are scoped as the management framework, and every recommendation produced by the LLM layer is logged with the assembled prompt, the model identifier, and the operator who acted on it. See [ARQUITECTURA.md](ARQUITECTURA.md) for the mapping.

## Contributing

Issue reports, replication studies, and connector contributions are welcome. The artifact is research code: it values clarity over generality, and connector implementations are deliberately minimal so that a reviewer can audit each one in a single sitting.

## Acknowledgements

Full acknowledgements will be published upon manuscript acceptance.

## Citation

A citation block (BibTeX / CFF) will be added here upon manuscript acceptance. The machine-readable [CITATION.cff](CITATION.cff) is the source of truth meanwhile.

## License

Apache License 2.0. See [LICENSE](LICENSE).
