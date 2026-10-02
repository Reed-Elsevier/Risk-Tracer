"""Optional narrative generation over cited investigation evidence."""

from __future__ import annotations

import json
import re
from typing import Any

from app.models import ExplainResponse, Investigation


SOURCE_ID_PATTERN = re.compile(r"\b(?:INV|PAY|OWN|WL|IEX|PO|SUP|ENT)\d+\b")


def _evidence_payload(investigation: Investigation) -> dict[str, Any]:
    return {
        "invoice": investigation.invoice.model_dump(mode="json"),
        "supplier": investigation.supplier.model_dump(mode="json"),
        "entity": investigation.entity.model_dump(mode="json"),
        "signals": investigation.signals.model_dump(mode="json"),
        "evidence_brief": investigation.evidence_brief.model_dump(mode="json"),
    }


def explain_investigation(
    investigation: Investigation,
    *,
    api_key: str,
    model: str,
) -> ExplainResponse:
    """Ask the configured OpenAI model for a cited narrative, never a priority."""

    from openai import OpenAI

    payload = _evidence_payload(investigation)
    prompt = (
        "Explain the evidence in this RiskTracer investigation for a human reviewer. "
        "Cite source IDs exactly as provided. Do not assign, recommend, or restate a review "
        "priority, do not conclude fraud, and do not use the phrases 'fraud score', "
        "'duplicate payment', or 'beneficial owner'. Return a short factual narrative.\n\n"
        f"Evidence JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    client = OpenAI(api_key=api_key)
    response = client.responses.create(model=model, input=prompt)
    narrative = getattr(response, "output_text", "") or ""
    allowed_ids = {
        source_id
        for sentence in investigation.evidence_brief.sentences
        for source_id in sentence.source_ids
    }
    cited_ids = [source_id for source_id in SOURCE_ID_PATTERN.findall(narrative) if source_id in allowed_ids]
    return ExplainResponse(narrative=narrative.strip(), source_ids=list(dict.fromkeys(cited_ids)))
