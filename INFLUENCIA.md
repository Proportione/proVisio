# Influence — the focal construct of proVisio Media

> **Status: design, 2026-10-17.** No code in this repository implements this
> chapter. It records how the *Media* variant (see [VERTICALS.md](VERTICALS.md))
> turns "influence" into measurable key results without claiming more than the
> signals allow.

## Why this chapter exists

[VERTICALS.md](VERTICALS.md) gives proVisio Media its focal construct:
*influence — reach into decision-maker audiences rather than raw traffic volume*.
That sentence names a goal. It does not say how to measure it, and the obvious
shortcut is to compute a composite "influence index" from whatever the analytics
stack returns. That shortcut fails in a precise way. Web analytics, search and
email data measure **reach weighted by attention**. None of them says **who** the
reader is. Without an audience-composition signal, an index labelled "influence"
is reach under another name.

This chapter fixes the vocabulary and the rules. Influence stays the
**objective**, and each key result is named after what it actually measures.

## A public instrument: the Digital News Report

The Reuters Institute for the Study of Journalism (University of Oxford)
publishes the *Digital News Report* (DNR) every year. It is an online survey of
national samples in 48 markets (2026 edition), fielded by YouGov, and its
questionnaire is published. The indicators most relevant to influence are:

| DNR item | What it measures |
|---|---|
| Q5B — brands used to access news online in the last week | Weekly brand reach |
| Q5BI — of those, used on 3 days or more | Habitual use / loyalty |
| Q6 — "How trustworthy would you say news from the following brands is?" (0–10, plus "haven't heard of this brand") | Brand trust (and awareness) |
| Q10 — ways of coming across news online | Gateway (direct, search, social, email, aggregators) |
| Q13 — ways of sharing or taking part in news coverage in an average week | Participation and amplification |

Two limits apply to any outlet that uses these items:

1. **Most outlets are not in the report.** Each market asks about trust in
   roughly fifteen brands, and brands below a minimum reach are excluded (3% reach in
   some national editions). A niche or small outlet therefore has **no
   DNR data about itself**. Only the questions are available.
2. **Same wording does not mean the same sample.** Asking the DNR items of an
   outlet's own readers makes the **wording** comparable to the national
   figures. The **sample** stays different: only readers are reached, and they
   select themselves. Readers also cannot answer "haven't heard of this brand",
   so awareness is out of reach.

## How the method measures it

| Layer | What it does for influence |
|---|---|
| L1 Ingest | Existing connectors (web analytics, a first-party cookieless page counter, email service provider events, social referrals). Optionally, an on-site reader survey that uses the DNR wording, stored through the same human-gate store as the rest of the platform's feedback |
| L2 Normalise | Each DNR item is mapped to an existing `signal_family × kpi_family` cell. **No new family is created for this variant.** If one were ever needed, the canonical schema would be at fault (see the invariant in VERTICALS.md) |
| L3 Fusion | A **weekly** reading with the usual numeric validation and deterministic fallback. Two words are banned in its output: causal language, and "influence" attached to a number |
| L4 Views | One card per key result. Each card shows its source and its bias ("analytics · consenting users only", "counter · page views, not people", "survey · respondents only") |
| L5 Presentation | A dedicated tab named after the objective. The 20-60-20 human gate ("Is this useful?") applies to every card |

### Key results

| KR | Behavioural signal (available without a survey) | Declared signal (survey, DNR wording) |
|---|---|---|
| Trust | — | Share of respondents scoring the outlet 6–10 |
| Habitual use | Returning users, daily/28-day stickiness | Q5BI |
| Gateway | Direct, newsletter, search and social share of visits | Q10 |
| Composition | — | Share of respondents in decision-making roles |
| Amplification | Visits from social platforms | Q13 |
| Reach | Weekly page views from the first-party counter | — |

Comparing what readers **say** (survey) with what they **do** (behaviour) is part
of the output, not noise to be reconciled away.

## Rules

1. **"Influence" names the objective, never a figure.** No card, index or L3
   sentence calls a number "influence".
2. **No composite index.** Requesting one raises an error that a test pins.
3. **Missing is not zero.** Trust and composition appear as "no data" until a
   survey exists. They are never drawn as 0 and never hidden.
4. **Baseline before targets.** No key-result target is set before a measured
   baseline exists. Neither pieces nor authors are ranked by "influence", to
   avoid Goodhart effects on editorial choices.
5. **Personal data.** A reader survey needs a privacy notice, consent and
   anonymity. **Political self-placement (the DNR left–right item) is excluded**:
   it is special-category data under GDPR Art. 9.
6. **National benchmarks are context, not targets.** When shown next to the DNR
   brand figures for the same market, the outlet's figures carry the label
   "different sample".

## What this chapter does not claim

It does not claim that the key results above measure influence. They measure
reach, loyalty, gateway, amplification, declared trust and the declared
composition of respondents. Whether and how these combine into influence is an
open research question, and nothing here is offered as evidence for it.

## Reference

Reuters Institute for the Study of Journalism (2026). *Digital News Report 2026*.
University of Oxford. https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026 ·
methodology and questionnaire:
https://reutersinstitute.politics.ox.ac.uk/digital-news-report/2026/methodology
