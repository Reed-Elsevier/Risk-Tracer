# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

A reviewer who already has an invoice to investigate, and someone being shown the product. Both land on Home. Home must let them find an invoice, and the verified demo case must be one click away.

## Product Purpose

RiskTracer helps a human reviewer investigate supplier payment risk for one invoice. The reviewer sees deterministic signals and their source records, follows a bounded ownership path, and records a review decision. Success is a review grounded in named source records, not a conclusion that fraud occurred.

## Positioning

The initial review priority is calculated only by explicit evidence rules. An optional narrative explains the investigation from the evidence brief and supplier history. That narrative never sets review priority and never concludes fraud.

## Operating Context

The reviewer opens an investigation for an invoice, or reaches one from a supplier profile. Home is the entry: find an invoice by id, number, or supplier, read a short orientation of how a review works, and open the verified demo investigation `INV0021439`.

Locally the web app runs at `http://localhost:3000` against the API at `http://localhost:8000`. Review decisions are stored in `var/risktracer.duckdb`. Source CSVs stay immutable.

## Capabilities and Constraints

Confirmed routes and API:

- `GET /invoices?q=&limit=` searches invoices. There is no investigation queue.
- `POST /investigate` loads one investigation.
- `GET /suppliers/{supplier_id}` loads a supplier profile.
- `POST /investigations/{invoice_id}/decisions` and `GET /investigations/{invoice_id}/decisions` record and list review decisions.
- `POST /investigate/explain` writes the investigation narrative when configured. Without `ANTHROPIC_API_KEY` the deterministic investigation still works and that endpoint returns `503`.

Terminology follows `GLOSSARY.md`. In particular: review priority is not a fraud score; possible duplicate submission is not a duplicate payment; indirect watchlist exposure is not a beneficial-owner match; the evidence brief is not the investigation narrative.

A review decision is a human disposition (escalate or clear, with a note and the evidence considered). It is not a payment action.

Undecided: whether a future queue of investigations should exist. Do not invent one from search.

## Brand Commitments

The product name is RiskTracer. Voice stays evidence-led: state recorded facts, name source records, and avoid conclusions the evidence does not support.

## Evidence on Hand

The verified demo investigation is `INV0021439`. README records the expected evidence: high priority from possible duplicate submission plus indirect watchlist exposure; possible duplicate `INV0046758` with payment `PAY0041819`; ownership path `OWN0009353` → `OWN0003041` → `WL003070`; no PO integrity signal for `PO0009457`; exception context `IEX0004557`.

Do not fabricate customers, testimonials, benchmarks, or fraud findings.

## Product Principles

- A human records the review decision. The product does not conclude fraud.
- Review priority comes only from explicit evidence rules.
- What the reviewer reads names the source records it came from.
- Home is an entry: find an invoice, see how a review works, and open the verified demo in one click.
- Use glossary terms. Do not substitute the avoided phrases.
