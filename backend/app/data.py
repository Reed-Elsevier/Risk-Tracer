"""CSV loading, Parquet caching, and indexed dataset access."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


DATASET_PATHS = {
    "invoices": Path("G_finance/invoices.csv"),
    "suppliers": Path("G_finance/suppliers.csv"),
    "purchase_orders": Path("G_finance/purchase_orders.csv"),
    "payments": Path("G_finance/payments.csv"),
    "invoice_exceptions": Path("G_finance/invoice_exceptions.csv"),
    "business_entities": Path("D_risk/business_entities.csv"),
    "ownership_links": Path("D_risk/ownership_links.csv"),
    "watchlists": Path("D_risk/watchlists.csv"),
}


def _clean_record(row: pd.Series) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in row.to_dict().items():
        if pd.isna(value) or value == "":
            record[key] = None if key not in {"invoice_id", "supplier_id", "entity_id"} else ""
        else:
            record[key] = value
    return record


class DataStore:
    """Own the read-only source frames and fast lookup indexes."""

    def __init__(self, data_dir: str | Path, db_path: str | Path):
        self.data_dir = Path(data_dir)
        self.db_path = Path(db_path)
        self.cache_dir = self.db_path.parent / "parquet"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.frames = {
            name: self._load_frame(name, relative_path)
            for name, relative_path in DATASET_PATHS.items()
        }
        self._index_frames()
        self.connection = self._open_database()

    def _load_frame(self, name: str, relative_path: Path) -> pd.DataFrame:
        csv_path = self.data_dir / relative_path
        parquet_path = self.cache_dir / f"{name}.parquet"
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {csv_path}")
        if parquet_path.exists() and parquet_path.stat().st_mtime >= csv_path.stat().st_mtime:
            return pd.read_parquet(parquet_path)
        frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_filter=False)
        frame.to_parquet(parquet_path, index=False)
        return frame

    def _index_frames(self) -> None:
        self.invoice_index = self.frames["invoices"].set_index("invoice_id", drop=False)
        self.supplier_index = self.frames["suppliers"].set_index("supplier_id", drop=False)
        self.entity_index = self.frames["business_entities"].set_index("entity_id", drop=False)
        self.po_index = self.frames["purchase_orders"].set_index("po_id", drop=False)
        self.payment_index = self.frames["payments"].set_index("invoice_id", drop=False)

    def _open_database(self) -> duckdb.DuckDBPyConnection:
        if str(self.db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = duckdb.connect(str(self.db_path))
        for name, frame in self.frames.items():
            connection.register(f"{name}_frame", frame)
            connection.execute(
                f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM {name}_frame"
            )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS review_decisions (
                decision_id VARCHAR PRIMARY KEY,
                invoice_id VARCHAR NOT NULL,
                disposition VARCHAR NOT NULL,
                note VARCHAR NOT NULL,
                priority VARCHAR NOT NULL,
                priority_override VARCHAR,
                override_reason VARCHAR,
                reviewer VARCHAR NOT NULL,
                created_at TIMESTAMP NOT NULL,
                evidence_snapshot JSON NOT NULL
            )
            """
        )
        return connection

    def close(self) -> None:
        self.connection.close()

    def _one(self, frame_name: str, key: str, value: str) -> dict[str, Any] | None:
        frame = self.frames[frame_name]
        if key not in frame.columns:
            return None
        matches = frame[frame[key].astype(str) == str(value)]
        return _clean_record(matches.iloc[0]) if not matches.empty else None

    def invoice(self, invoice_id: str) -> dict[str, Any] | None:
        return self._one("invoices", "invoice_id", invoice_id)

    def supplier(self, supplier_id: str) -> dict[str, Any] | None:
        return self._one("suppliers", "supplier_id", supplier_id)

    def entity(self, entity_id: str) -> dict[str, Any] | None:
        return self._one("business_entities", "entity_id", entity_id)

    def purchase_order(self, po_id: str | None) -> dict[str, Any] | None:
        return self._one("purchase_orders", "po_id", po_id) if po_id else None

    def payment(self, invoice_id: str) -> dict[str, Any] | None:
        if self.frames["payments"].empty:
            return None
        matches = self.frames["payments"][
            self.frames["payments"]["invoice_id"].astype(str) == str(invoice_id)
        ]
        return _clean_record(matches.iloc[0]) if not matches.empty else None

    def exceptions(self, invoice_id: str) -> list[dict[str, Any]]:
        frame = self.frames["invoice_exceptions"]
        matches = frame[frame["invoice_id"].astype(str) == str(invoice_id)]
        return [_clean_record(row) for _, row in matches.iterrows()]

    def search_invoices(self, query: str = "", limit: int = 20) -> list[dict[str, Any]]:
        invoices = self.frames["invoices"]
        suppliers = self.frames["suppliers"][["supplier_id", "supplier_name"]]
        joined = invoices.merge(suppliers, on="supplier_id", how="left")
        query = query.strip().lower()
        if query:
            mask = (
                joined["invoice_id"].str.lower().str.contains(query, regex=False)
                | joined["invoice_number"].str.lower().str.contains(query, regex=False)
                | joined["supplier_name"].str.lower().str.contains(query, regex=False)
            )
            joined = joined[mask]
        return [_clean_record(row) for _, row in joined.head(limit).iterrows()]

    def supplier_invoices(self, supplier_id: str) -> list[dict[str, Any]]:
        frame = self.frames["invoices"]
        matches = frame[frame["supplier_id"].astype(str) == str(supplier_id)]
        return [_clean_record(row) for _, row in matches.iterrows()]
