# Sector variants — from methodology to product line

> **Status: design, 2026-08-14.** No code has been written for any variant. This
> file records a scoping decision so that the boundary between the *method* and
> the *products derived from it* is explicit in the repository from the start.

## Why this file exists

What this repository implements is a **method**: place business KPIs and digital
signals on one canonical schema, quantify their relationship, and surface
prioritised recommendations through the L3 fusion layer
(see [ARQUITECTURA.md](ARQUITECTURA.md)).

A method is not something an SME buys. What an SME buys is a system that already
knows which KPIs matter in *its* sector, which signals plausibly move them, and
what a recommendation is allowed to say. That sector knowledge is exactly what
the canonical schema deliberately leaves out in order to stay sector-agnostic.

The consequence is a product line: **one shared core, three sector variants.**

## The invariant / variant boundary

| Layer | Invariant (single implementation) | Varies per sector variant |
|---|---|---|
| L1 Ingest | Connector contract, column contract | Which connectors a tenant declares; sector-specific systems of record (S5, design stage) |
| L2 Normalise | Canonical `signal_family × kpi_family` schema | Nothing. **This is the load-bearing invariant.** |
| L3 LLM fusion | `fuse()` contract, audit log, prompt assembly | KPI taxonomy, benchmark ranges, narrative vocabulary, admissible recommendation types |
| L4 KPI views | Widgets, Plotly figures, page template | Default KPI cards and their ordering |
| L5 AuthZ | Tenant routing, isolation | Nothing |

**A variant is a configuration pack, not a fork.** Concretely: a KPI taxonomy, a
set of benchmark ranges, an L3 prompt vocabulary, and a default page layout — all
of it data loaded by the same code. If a variant ever requires a change below L3,
that is a signal the canonical schema is wrong and must be fixed in the core,
not routed around with a sector branch. Three codebases would invalidate the
central design claim that the layers are swappable and the schema is
sector-agnostic.

## The three variants

Names are **not decided**; the labels below are descriptive placeholders.
See the naming issue in this repository.

### 1. News and media publishing

- **Focal construct**: influence — reach into decision-maker audiences rather
  than raw traffic volume.
- **KPI families**: share of decision-maker audience, tier-1 outlet pickup rate,
  executive newsletter engagement, elite social amplification.
- **Signal families**: web analytics, organic positioning, email service provider
  segmentation, social listening over a curated list.
- **Why it is a variant and not a tenant**: the KPI vocabulary is not a
  reweighting of a generic funnel — the denominator changes from "audience" to
  "audience that decides".

### 2. Education and training

- **Focal construct**: formation — enrolment, completion, and the loop by which
  a learner becomes an advocate or a trainer.
- **KPI families**: enrolments per course unit and cohort, completion rate,
  learner-to-trainer loop, referral, content reach.
- **Signal families**: academic system of record (student information / LMS),
  web analytics, video platform metrics, email service provider.
- **Note**: this variant has the strongest dependence on a system of record
  outside the digital-marketing surface, and therefore the strongest dependence
  on the S5 signal family, which is still at design stage.

### 3. Retail and direct-to-consumer commerce

- **Focal construct**: brand engagement — digital brand equity, not
  last-click attribution.
- **KPI families**: repeat purchase rate, cohort retention, user-generated
  content mentions, engaged sessions on brand content.
- **Signal families**: web analytics, e-commerce platform, paid social.
- **Note**: the only variant where the KPI store has a transactional source of
  truth, which makes it the cheapest to validate quantitatively and the most
  exposed to attribution disputes.

## Relationship to the research artifact

This file describes a **product** decision, not a research claim. The manuscript
under pre-publication review introduces the artifact and its method; it makes no
claim about sector variants, and nothing here is offered as evidence for it. The
variants are relevant to the research line only in that the empirical case
studies announced in [README](README.md#status) are drawn from these three
sectors, which is what made the boundary visible in the first place.

No variant currently exists as running code.
