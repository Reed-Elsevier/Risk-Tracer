"""Review decision persistence in DuckDB."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import duckdb

from app.models import DecisionRequest, Investigation, ReviewDecision


class DecisionRepository:
    def __init__(self, connection: duckdb.DuckDBPyConnection):
        self.connection = connection
        self.connection.execute(
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

    def create(self, invoice_id: str, request: DecisionRequest, investigation: Investigation) -> ReviewDecision:
        if request.priority_override and not request.override_reason:
            raise ValueError("A priority override requires a reason")
        evidence_snapshot = investigation.model_dump(mode="json")
        evidence_snapshot["latest_decision"] = None
        narrative = evidence_snapshot.get("narrative")
        if isinstance(narrative, dict):
            narrative["checklist"] = ""
        decision = ReviewDecision(
            decision_id=str(uuid.uuid4()),
            invoice_id=invoice_id,
            disposition=request.disposition,
            note=request.note,
            priority=request.priority_override or investigation.priority.value,
            priority_override=request.priority_override,
            override_reason=request.override_reason,
            reviewer=request.reviewer,
            created_at=datetime.now(timezone.utc).isoformat(),
            evidence_snapshot=evidence_snapshot,
        )
        created_at = datetime.fromisoformat(decision.created_at)
        self.connection.execute(
            """
            INSERT INTO review_decisions
            (decision_id, invoice_id, disposition, note, priority, priority_override,
             override_reason, reviewer, created_at, evidence_snapshot)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                decision.decision_id,
                decision.invoice_id,
                decision.disposition,
                decision.note,
                decision.priority,
                decision.priority_override,
                decision.override_reason,
                decision.reviewer,
                created_at,
                json.dumps(decision.evidence_snapshot),
            ],
        )
        return decision

    def _to_model(self, row: tuple[Any, ...]) -> ReviewDecision:
        (
            decision_id,
            invoice_id,
            disposition,
            note,
            priority,
            priority_override,
            override_reason,
            reviewer,
            created_at,
            evidence_snapshot,
        ) = row
        if isinstance(evidence_snapshot, str):
            evidence_snapshot = json.loads(evidence_snapshot)
        return ReviewDecision(
            decision_id=decision_id,
            invoice_id=invoice_id,
            disposition=disposition,
            note=note,
            priority=priority,
            priority_override=priority_override,
            override_reason=override_reason,
            reviewer=reviewer,
            created_at=created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
            evidence_snapshot=evidence_snapshot,
        )

    def latest(self, invoice_id: str) -> ReviewDecision | None:
        result = self.connection.execute(
            """
            SELECT decision_id, invoice_id, disposition, note, priority, priority_override,
                   override_reason, reviewer, created_at, evidence_snapshot
            FROM review_decisions
            WHERE invoice_id = ?
            ORDER BY created_at DESC, decision_id DESC
            LIMIT 1
            """,
            [invoice_id],
        ).fetchone()
        return self._to_model(result) if result else None

    def history(self, invoice_id: str) -> list[ReviewDecision]:
        rows = self.connection.execute(
            """
            SELECT decision_id, invoice_id, disposition, note, priority, priority_override,
                   override_reason, reviewer, created_at, evidence_snapshot
            FROM review_decisions
            WHERE invoice_id = ?
            ORDER BY created_at DESC, decision_id DESC
            """,
            [invoice_id],
        ).fetchall()
        return [self._to_model(row) for row in rows]
