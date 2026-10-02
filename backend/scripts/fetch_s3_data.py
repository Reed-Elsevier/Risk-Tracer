"""Download the named REPH CSVs from S3 before the API starts."""

from __future__ import annotations

import os
from pathlib import Path

import boto3


# =========================================================
# AWS CLIENTS / CONFIG
# =========================================================

s3 = boto3.client("s3")

BUCKET = os.environ["DATA_BUCKET"].strip()
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))

# S3 key -> path under DATA_DIR (the layout DataStore already expects).
FILES = {
    "invoices": ("finance/invoices.csv", "G_finance/invoices.csv"),
    "suppliers": ("finance/suppliers.csv", "G_finance/suppliers.csv"),
    "purchase_orders": ("finance/purchase_orders.csv", "G_finance/purchase_orders.csv"),
    "payments": ("finance/payments.csv", "G_finance/payments.csv"),
    "invoice_exceptions": ("finance/invoice_exceptions.csv", "G_finance/invoice_exceptions.csv"),
    "business_entities": ("risk/business_entities.csv", "D_risk/business_entities.csv"),
    "ownership_links": ("risk/ownership_links.csv", "D_risk/ownership_links.csv"),
    "watchlists": ("risk/watchlists.csv", "D_risk/watchlists.csv"),
}


# =========================================================
# S3 HELPERS
# =========================================================

def download_object(key, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(BUCKET, key, str(destination))


def main():
    for name, (key, relative_path) in FILES.items():
        target = DATA_DIR / relative_path
        print(f"Downloading {name} from s3://{BUCKET}/{key}")
        download_object(key, target)


if __name__ == "__main__":
    main()
