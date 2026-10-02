# RiskTracer

RiskTracer is an evidence-led invoice investigation MVP. A reviewer opens an investigation for an invoice, sees deterministic signals and their source records, follows a bounded ownership graph, and records a human review decision.

The initial review priority is calculated only by explicit rules from [ADR-0002](docs/adr/0002-assign-review-priority-from-evidence-rules.md). When `ANTHROPIC_API_KEY` is set, each investigation includes an investigation narrative and a checklist for the review note. The narrative can describe supplier history, and it never sets priority or concludes fraud. See [ADR-0003](docs/adr/0003-let-the-narrative-use-supplier-history-without-changing-priority.md).

## Local run

Requirements: Python 3.12+ and Node.js 20+.

Start the API:

```powershell
cd backend
python -m pip install -e ".[test]"
uvicorn app.main:app --reload --port 8000
```

In another terminal, start the web app:

```powershell
cd frontend
npm install
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
npm run dev
```

Open <http://localhost:3000>. The default route opens `INV0021439`, the verified demo case.

The first API run reads the CSV files and writes a Parquet cache under `var/parquet/`. Review decisions are stored in `var/risktracer.duckdb`; both are generated files and are ignored by git.

## API

```text
GET  /health
GET  /invoices?q=INV0021439&limit=20
GET  /suppliers/{supplier_id}
POST /investigate                         {"invoice_id":"INV0021439"}
POST /investigate/explain                 {"invoice_id":"INV0021439"}
POST /investigations/{invoice_id}/decisions
GET  /investigations/{invoice_id}/decisions
```

The demo investigation is expected to show:

- High priority from possible duplicate submission plus indirect watchlist exposure.
- Possible duplicate `INV0046758`, with payment `PAY0041819`.
- The recorded upstream path `OWN0009353` → `OWN0003041` → `WL003070`.
- No PO integrity signal for `PO0009457`.
- Exception context `IEX0004557`.

Malformed request bodies return `422`; unknown invoice IDs return `404`. Without `ANTHROPIC_API_KEY`, the investigation still works, its narrative status is `unavailable`, and the explanation endpoint returns `503`.

## Verification

```powershell
cd backend
python -m pytest

cd ..\frontend
npm run typecheck
npm run build
```

## Docker Compose

Copy the environment template and start both services:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The API is available at <http://localhost:8000> and the web app at <http://localhost:3000>. Mounting `center_data` read-only keeps source data immutable; `var/` holds the cache and DuckDB file.

## EC2 outline

1. Launch an Ubuntu instance with a security group allowing TCP `22` for administration and TCP `3000` for the web app. Keep `8000` private when possible.
2. Install Docker Engine and the Compose plugin.
3. Clone this repository and create `.env` from `.env.example`; set `CORS_ORIGINS` to the web origin and optionally set `ANTHROPIC_API_KEY`.
4. Run `docker compose up --build -d`.
5. Put a TLS reverse proxy in front of port `3000` for a shared deployment. Persist the `var/` directory and back up the DuckDB file if review history matters.
